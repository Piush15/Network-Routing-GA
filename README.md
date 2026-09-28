# Network Routing Optimization using Genetic Algorithm

## Soft Computing Project — Group G3

A Genetic Algorithm based approach for optimizing network routes using multiple routing metrics: distance, delay, congestion, and hop count.

---

## 📌 Project Overview

Traditional shortest-path routing generally focuses on a single metric such as distance.

In this project, we formulate network routing as a multi-metric optimization problem where a route is evaluated using:

- Distance
- Network delay
- Congestion
- Number of hops

A Genetic Algorithm (GA) is implemented in Python to search for a low-cost route between a source node and a destination node.

The project uses a simulated network topology with nodes A–H.

---

## 🎯 Objectives

The main objectives of this project are:

1. Model network routing as an optimization problem.
2. Represent candidate routes as chromosomes.
3. Apply Genetic Algorithm operators to search for good routes.
4. Optimize distance, delay and congestion simultaneously.
5. Validate the GA using multiple random seeds.
6. Compare the GA solution with Dijkstra-based baselines.
7. Analyze convergence and the effect of GA parameters.

---

## 🧠 Genetic Algorithm Approach

Each possible route from the source to destination is represented as a chromosome.

Example:

`[A, C, E, G, H]`

A population contains multiple candidate routes.

The algorithm follows:

Initial Population  
↓  
Evaluate Route Cost  
↓  
Tournament Selection  
↓  
Crossover  
↓  
Mutation  
↓  
Elitism  
↓  
New Population  
↓  
Repeat for multiple generations  
↓  
Best Route

---

## 📐 Objective Function

The route cost used in this project is:

**Cost = 0.40 × D_norm + 0.30 × Delay_norm + 0.30 × Congestion + 0.01 × Hops**

Lower cost represents a better route.

### Weighting

| Metric | Weight |
|---|---:|
| Distance | 0.40 |
| Delay | 0.30 |
| Congestion | 0.30 |
| Hop penalty | 0.01 per hop |

The weights are experimental design choices used for this project and are not universal network-routing weights.

---

## 🔧 Genetic Algorithm Components

### Chromosome

A chromosome represents one complete candidate route.

Example:

`[A, C, E, G, H]`

### Population

A collection of candidate routes.

### Selection

Tournament selection is used to select parents.

### Crossover

Two valid parent routes are combined at a shared intermediate node to create a new candidate route.

### Mutation

Mutation changes part of an existing route to maintain population diversity.

### Route Validation

Routes produced during genetic operations are checked for validity.

The implementation ensures that candidate routes:

- Start at the source node.
- End at the destination node.
- Do not contain duplicate nodes.
- Use valid graph edges.

### Elitism

The best route from the current population is directly carried into the next generation so that it is not lost through crossover or mutation.

---

## 🗺️ Network

The project uses a small simulated network containing nodes A–H.

Each network edge contains:

- Distance in kilometres
- Delay in milliseconds
- Congestion value between 0 and 1

The dataset was created specifically for this project to provide a controlled environment for demonstrating and evaluating the Genetic Algorithm.

It is not a Kaggle or real-world dataset.

---

## 📊 Final Result

The final GA configuration was:

| Parameter | Value |
|---|---:|
| Population size | 16 |
| Generations | 100 |
| Crossover rate | 0.85 |
| Mutation rate | 0.10 |

### Final Route

`A → C → E → G → H`

### Route Metrics

| Metric | Result |
|---|---:|
| Distance | 26 km |
| Delay | 53 ms |
| Congestion | 0.48 |
| Objective Cost | 1.572889 |

---

## 🔬 Multiple Seed Evaluation

Genetic Algorithms are stochastic because they involve random operations.

To evaluate consistency, the algorithm was executed using 10 different random seeds:

`11, 22, 33, 44, 55, 66, 77, 88, 99, 111`

All 10 runs converged to:

`A → C → E → G → H`

The mean runtime across the complete GA runs was approximately:

`31.73 ms`

---

## 📈 Convergence Analysis

For representative seed 66:

- Initial best cost = 1.758094
- Final best cost = 1.572889
- Improvement ≈ 10.53%

The convergence graph shows how the best route cost improves over generations.

---

## ⚖️ Baseline Comparison

The GA was compared with two Dijkstra-based approaches.

### Distance-only Dijkstra

- Route: A → C → F → H
- Distance: 25 km
- Delay: 51 ms
- Congestion: 1.30
- Cost: 1.755897

### Weighted Dijkstra

Using the same weighted objective function as the GA:

- Route: A → C → E → G → H
- Cost: 1.572889

### Genetic Algorithm

- Route: A → C → E → G → H
- Cost: 1.572889

The GA matches the weighted Dijkstra solution for this static network and objective function.

This serves as a validation of the GA implementation rather than evidence that GA outperforms Dijkstra.

---

## 📊 Parameter Analysis

The project also evaluates the effect of:

- Population size
- Mutation rate
- Number of generations

The corresponding experimental results and graphs are available in the `results/` and `visualizations/` directories.

---

## 📚 Literature Review

### Q1 — Fuzzy/Fuzzy-Hybrid Routing

Fahad, T. O. & Ali, A. A. (2018).

**Multiobjective Optimized Routing Protocol for VANETs**

*Advances in Fuzzy Systems.*

The paper uses fuzzy controllers with ABC optimization for multi-factor routing decisions in VANETs.

### Q2 — Genetic Algorithm Routing

Bhardwaj, A. & El-Ocla, M. (2020).

**Multipath Routing Protocol Using Genetic Algorithm in Mobile Ad Hoc Networks**

*IEEE Access, 8, 177534–177548.*

Li et al. (2013).

**A Genetic Algorithm for Finding a Path Subject to Two Constraints**

*Applied Soft Computing, 13(2), 891–898.*

The Li et al. approach uses Gene Structure (GS) and a Gene Structure Algorithm (GSA) to generate loop-free paths through the chromosome representation and genetic operations.

Our implementation does not use GS/GSA. Instead, we use feasible path generation and route validation after genetic operations.

---

## 🛠️ Technologies Used

- Python
- NetworkX
- Pandas
- NumPy
- Matplotlib

---

## ⚠️ Limitations

The current implementation has several limitations:

- Small simulated network topology.
- Static network conditions.
- Manually selected objective weights.
- Genetic Algorithm is stochastic.
- Weighted Dijkstra can solve this particular static additive objective exactly.

---

## 🔮 Future Scope

Possible extensions include:

- Dynamic congestion
- Real-world network datasets
- Real-time route re-optimization
- Pareto-based multi-objective Genetic Algorithms
- Fuzzy + Genetic Algorithm hybrid routing
- GA combined with local search
- Larger and more complex network topologies

---

## 📜 License

This project is intended for academic and educational purposes.
