# 🔬 Mathematical Foundations of NeuroKey

NeuroKey approaches the keyboard layout problem as a **Discrete Combinatorial Optimization** task within a high-dimensional state space. This document details the rigorous mathematical frameworks used to resolve this space.

---

## 1. The State Space ($S$)

The keyboard is modeled as a set of positions $P = \{1, 2, \dots, 30\}$ and a set of characters $C = \{c_1, c_2, \dots, c_{30}\}$. A layout $L$ is a **bijection** (one-to-one mapping) between $C$ and $P$.
The size of the state space $S$ is the factorial of the number of keys:
$$|S| = 30! \approx 2.652 \times 10^{32}$$
Navigating this space via brute force is computationally impossible; thus, we employ stochastic search methods.

---

## 2. The Objective Function ($f: S \rightarrow \mathbb{R}^+$)

We define a cost function (Energy) that the system seeks to minimize. This is a weighted linear combination of four ergonomic sub-metrics:
$$E(L) = \omega_1 E_{effort} + \omega_2 E_{sfb} - \omega_3 E_{roll} + \omega_4 E_{balance}$$

### 2.1 Static Effort ($E_{effort}$)
Let $f_i$ be the frequency of character $c_i$ in the corpus, and $d_j$ be the static penalty (distance/effort) of position $j$.
$$E_{effort}(L) = \sum_{i=1}^{30} f_i \cdot d_{L(c_i)}$$

### 2.2 Same-Finger Bigrams ($E_{sfb}$)
Let $B$ be the set of character bigrams and $Freq(b)$ their frequency. Let $\mathbb{1}_{finger}(p_1, p_2)$ be an indicator function that returns 1 if positions $p_1$ and $p_2$ are mapped to the same finger.
$$E_{sfb}(L) = \sum_{(c_1, c_2) \in B} Freq(c_1, c_2) \cdot \mathbb{1}_{finger}(L(c_1), L(c_2))$$

---

## 3. Simulated Annealing & Markov Chains

NeuroKey uses a **Markov Chain Monte Carlo (MCMC)** process. The transition from layout $s$ to $s'$ is governed by the **Acceptance Probability** $A(s, s', T)$:

### 3.1 Metropolis-Hastings Criterion
For a proposed move from $s$ to $s'$, where $\Delta E = E(s') - E(s)$:
$$A(s, s', T) = \begin{cases} 1 & \text{if } \Delta E < 0 \\ \exp\left(-\frac{\Delta E}{k_B T}\right) & \text{if } \Delta E \geq 0 \end{cases}$$
Where $T$ is the temperature and $k_B$ is a scaling constant (analogous to the Boltzmann constant).

### 3.2 Convergence Analysis
To guarantee convergence to a **Global Optimum**, the cooling schedule must satisfy the Geman-Geman condition:
$$T_k \geq \frac{C}{\ln(k + 1)}$$
Where $C$ is a constant proportional to the depth of the deepest local minimum. In practice, we use faster schedules (Exponential/Cosine) for computational efficiency, accepting a near-optimal "quasi-equilibrium" state.

---

## 4. Cooling Schedule Mathematics

### 4.1 Exponential Decay
$$T_{k} = T_0 \cdot \alpha^k, \quad \alpha \in (0.8, 0.999)$$
This provides a geometric contraction of the search space.

### 4.2 Cosine Annealing
Derived from Stochastic Gradient Descent (SGD) restarts:
$$T_t = T_{min} + \frac{1}{2}(T_{max} - T_{min})(1 + \cos(\frac{t_{curr}}{t_{total}}\pi))$$
This allows the engine to escape deep local minima by periodically "re-heating" the system.

---

## 5. Genetic Recombination (GPU Engine)

The GPU engine treats layouts as **Genotypes**. Evolution is modeled as a directed search in the fitness landscape.

### 5.1 Permutation Crossover (PMX)
Since layouts are permutations, standard crossover would produce duplicates. We use **Partially Mapped Crossover**:
1.  Select a random swath from Parent 1.
2.  Map those elements into the Child.
3.  Fill remaining slots from Parent 2, using a mapping table to resolve collisions.

### 5.2 Fitness Selection
The population $P_t$ evolves to $P_{t+1}$ via a selection operator $\mathcal{S}$:
$$\mathcal{S}(P_t) = \{ L \in P_t \mid Rank(E(L)) < k \}$$
Only layouts in the $k$-th percentile survive, ensuring the population's mean energy $\bar{E}$ decreases monotonically over generations.

---

> [!IMPORTANT]
> The combination of MCMC for local refinement and Genetic Evolution for global exploration ensures that NeuroKey finds layouts that are mathematically superior to any human-designed configuration.
