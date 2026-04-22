# 🔬 The Science of NeuroKey

NeuroKey uses advanced probabilistic and evolutionary algorithms to solve the discrete optimization problem of keyboard layout design.

## 1. Simulated Annealing (SA)

The core Rust engine implements **Simulated Annealing**, a metaheuristic inspired by the metallurgical process of heating and controlled cooling.

### How it Works:
1.  **State**: A permutation of 30 characters on a 3x10 grid.
2.  **Move**: Randomly swapping two characters.
3.  **Cost Function**: The "Ergonomic Score" calculated by `scorer.rs`.
4.  **Acceptance Criterion**: If a swap improves the score, it is always accepted. If it worsens the score, it is accepted with a probability $P = e^{-\Delta / T}$, where $\Delta$ is the score increase and $T$ is the current temperature.

### Cooling Schedules:
*   **Exponential**: $T_{next} = T_{curr} \times \alpha$. Best for general exploration.
*   **Linear**: $T_{next} = T_{curr} - \text{constant}$. Provides steady refinement.
*   **Cosine**: $T_{next} = \cos(\text{step})$. Cycles between "shaking" the layout and "freezing" it.

---

## 2. Ergonomic Scoring Model

The score is a weighted sum of four critical biometric factors:

| Metric | Description | Formula Logic |
| :--- | :--- | :--- |
| **Effort** | Distance from home row. | $\sum \text{Freq}(c) \times \text{Dist}(\text{pos}(c))$ |
| **SFB** | Same-Finger Bigrams. | Penalizes consecutive keys on the same finger. |
| **Rolls** | Fluid inward motion. | Bonuses for Pinky $\rightarrow$ Ring $\rightarrow$ Middle $\rightarrow$ Index. |
| **Balance** | Hand usage ratio. | Minimizes $|\text{Left Usage} - \text{Target Balance}|$. |

---

## 3. Genetic Algorithm (GPU Sidecar)

The Python sidecar uses **Population Dynamics** to evolve layouts:
1.  **Crossover**: Combining parts of two "parent" layouts.
2.  **Mutation**: Randomly shuffling keys in a child layout.
3.  **Selection**: Only the top 5% of layouts survive to the next generation.

By running these on a GPU, NeuroKey can evaluate thousands of generations in seconds.
