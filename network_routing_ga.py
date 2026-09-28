import random
import time
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

SEED = 42
random.seed(SEED)

SOURCE = "A"
TARGET = "H"

# Simulated communication network loaded from the reproducible CSV dataset.
# Each edge contains distance, delay and congestion.
EDGES = [
    tuple(row)
    for row in pd.read_csv("network_edges.csv").itertuples(index=False, name=None)
]

G = nx.Graph()
for u, v, distance, delay, congestion in EDGES:
    G.add_edge(
        str(u), str(v),
        distance_km=float(distance),
        delay_ms=float(delay),
        congestion=float(congestion)
    )

# -------------------------------------------------------------------
# 2. Objective function
# We normalize the three edge-level metrics before combining them.
# Lower total cost = better route.
# -------------------------------------------------------------------
MAX_DISTANCE = max(d["distance_km"] for _, _, d in G.edges(data=True))
MAX_DELAY = max(d["delay_ms"] for _, _, d in G.edges(data=True))
MAX_CONGESTION = 1.0

WEIGHTS = {
    "distance": 0.40,
    "delay": 0.30,
    "congestion": 0.30,
}

def route_metrics(route):
    distance = 0.0
    delay = 0.0
    congestion = 0.0

    for u, v in zip(route[:-1], route[1:]):
        edge = G[u][v]
        distance += edge["distance_km"]
        delay += edge["delay_ms"]
        congestion += edge["congestion"]

    return distance, delay, congestion

def route_cost(route):
    """Additive multi-metric route objective.
    Lower is better. Each edge contributes normalized distance, delay,
    and congestion using the same weights for GA and Dijkstra.
    """
    total = 0.0
    for u, v in zip(route[:-1], route[1:]):
        edge = G[u][v]
        total += (
            WEIGHTS["distance"] * (edge["distance_km"] / MAX_DISTANCE)
            + WEIGHTS["delay"] * (edge["delay_ms"] / MAX_DELAY)
            + WEIGHTS["congestion"] * edge["congestion"]
            + 0.01
        )
    return total

def fitness(route):
    return 1.0 / (1.0 + route_cost(route))

# -------------------------------------------------------------------
# 3. Feasible route generation
# -------------------------------------------------------------------
def random_simple_path(source, target, max_attempts=100):
    for _ in range(max_attempts):
        route = [source]
        visited = {source}
        current = source

        while current != target and len(route) <= len(G.nodes):
            candidates = [n for n in G.neighbors(current) if n not in visited]

            if not candidates:
                break

            # Prefer neighbors that are closer to the target, but retain
            # randomness so the population remains diverse.
            candidates.sort(key=lambda n: nx.shortest_path_length(G, n, target))
            if len(candidates) > 1 and random.random() < 0.55:
                next_node = random.choice(candidates[:min(3, len(candidates))])
            else:
                next_node = random.choice(candidates)

            route.append(next_node)
            visited.add(next_node)
            current = next_node

        if current == target:
            return route

    # Guaranteed fallback for a connected graph.
    return nx.shortest_path(G, source, target)

def initial_population(size):
    population = []
    seen = set()

    while len(population) < size:
        route = random_simple_path(SOURCE, TARGET)
        key = tuple(route)
        if key not in seen:
            population.append(route)
            seen.add(key)

    return population

# -------------------------------------------------------------------
# 4. GA operators
# -------------------------------------------------------------------
def selection(population, tournament_size=3):
    contestants = random.sample(population, tournament_size)
    return min(contestants, key=route_cost)

def crossover(parent1, parent2):
    # Route-aware crossover: find a common intermediate node and combine
    # the prefix of one parent with the suffix of the other.
    common = list(set(parent1[1:-1]).intersection(parent2[1:-1]))

    if not common:
        return parent1[:] if random.random() < 0.5 else parent2[:]

    pivot = random.choice(common)
    i = parent1.index(pivot)
    j = parent2.index(pivot)

    child = parent1[:i] + parent2[j:]

    # Validate that every consecutive pair is a real edge and that
    # the chromosome is a simple path.
    if (
        child[0] == SOURCE
        and child[-1] == TARGET
        and len(child) == len(set(child))
        and all(G.has_edge(u, v) for u, v in zip(child[:-1], child[1:]))
    ):
        return child

    return parent1[:] if route_cost(parent1) <= route_cost(parent2) else parent2[:]

def mutation(route, mutation_rate=0.15):
    if random.random() >= mutation_rate or len(route) <= 2:
        return route[:]

    # Replace the suffix after a randomly chosen internal node with a
    # newly generated feasible path to the destination.
    pivot_index = random.randint(0, len(route) - 2)
    pivot = route[pivot_index]

    try:
        suffix = random_simple_path(pivot, TARGET)
        candidate = route[:pivot_index] + suffix

        if (
            candidate[0] == SOURCE
            and candidate[-1] == TARGET
            and len(candidate) == len(set(candidate))
            and all(G.has_edge(u, v) for u, v in zip(candidate[:-1], candidate[1:]))
        ):
            return candidate
    except Exception:
        pass

    return route[:]

def genetic_algorithm(
    population_size=40,
    generations=100,
    crossover_rate=0.85,
    mutation_rate=0.15
):
    population = initial_population(population_size)
    best_route = min(population, key=route_cost)
    best_cost = route_cost(best_route)

    history = []

    for _ in range(generations):
        population = sorted(population, key=route_cost)

        if route_cost(population[0]) < best_cost:
            best_route = population[0][:]
            best_cost = route_cost(best_route)

        history.append(best_cost)

        new_population = [population[0][:]]  # elitism

        while len(new_population) < population_size:
            parent1 = selection(population)
            parent2 = selection(population)

            if random.random() < crossover_rate:
                child = crossover(parent1, parent2)
            else:
                child = parent1[:]

            child = mutation(child, mutation_rate)
            new_population.append(child)

        population = new_population

    return best_route, best_cost, history

def edge_cost(u, v):
    edge = G[u][v]
    return (
        WEIGHTS["distance"] * (edge["distance_km"] / MAX_DISTANCE)
        + WEIGHTS["delay"] * (edge["delay_ms"] / MAX_DELAY)
        + WEIGHTS["congestion"] * edge["congestion"]
        + 0.01
    )

# -------------------------------------------------------------------
# 5. Baselines
# -------------------------------------------------------------------
# Baseline 1: conventional shortest-distance routing.
distance_route = nx.shortest_path(G, SOURCE, TARGET, weight="distance_km")

# Baseline 2: Dijkstra with the SAME combined multi-metric objective as GA.
# This is a useful validation baseline on a static graph because it solves
# the additive weighted shortest-path formulation exactly.
G_cost = G.copy()
for u, v in G_cost.edges():
    G_cost[u][v]["combined_cost"] = edge_cost(u, v)

def dijkstra_weighted_baseline():
    return nx.shortest_path(
        G_cost, SOURCE, TARGET, weight="combined_cost"
    )

# -------------------------------------------------------------------
# 6. Run experiment
# -------------------------------------------------------------------
if __name__ == "__main__":
    start = time.perf_counter()
    ga_route, ga_cost, history = genetic_algorithm(
        population_size=8,
        generations=100,
        crossover_rate=0.85,
        mutation_rate=0.15
    )
    ga_time_ms = (time.perf_counter() - start) * 1000

    distance_route = nx.shortest_path(G, SOURCE, TARGET, weight="distance_km")
    weighted_route = dijkstra_weighted_baseline()

    print("=== G3 NETWORK ROUTING OPTIMIZATION ===")
    print(f"Source: {SOURCE}")
    print(f"Destination: {TARGET}")
    print()
    print("GA route:", " -> ".join(ga_route))
    print("GA objective cost:", round(ga_cost, 6))
    print("GA metrics (distance km, delay ms, congestion):",
          tuple(round(x, 3) for x in route_metrics(ga_route)))
    print(f"GA execution time: {ga_time_ms:.3f} ms")
    print()
    print("Dijkstra distance-only route:", " -> ".join(distance_route))
    print("Dijkstra distance-only metrics:",
          tuple(round(x, 3) for x in route_metrics(distance_route)))
    print("Distance-only objective cost:", round(route_cost(distance_route), 6))
    print()
    print("Dijkstra weighted multi-metric route:", " -> ".join(weighted_route))
    print("Dijkstra weighted metrics:",
          tuple(round(x, 3) for x in route_metrics(weighted_route)))
    print("Dijkstra weighted objective cost:",
          round(route_cost(weighted_route), 6))
    print()
    print("GA initial objective:", round(history[0], 6))
    print("GA final objective:", round(history[-1], 6))
    print("GA convergence improvement (%):",
          round((history[0] - history[-1]) / history[0] * 100, 2))

    # Convergence plot
    plt.figure(figsize=(8, 5))
    plt.plot(range(1, len(history) + 1), history)
    plt.xlabel("Generation")
    plt.ylabel("Best Route Cost (lower is better)")
    plt.title("GA Convergence for Network Routing")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig("ga_convergence.png", dpi=180)
    plt.close()

    # Network plot
    pos = nx.spring_layout(G, seed=7)
    plt.figure(figsize=(8, 6))
    nx.draw_networkx_nodes(G, pos, node_size=800)
    nx.draw_networkx_labels(G, pos, font_weight="bold")
    nx.draw_networkx_edges(G, pos, width=1.5)

    ga_edges = list(zip(ga_route[:-1], ga_route[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=ga_edges, width=4)

    plt.title("Network and GA-Selected Route")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig("ga_route.png", dpi=180)
    plt.close()

