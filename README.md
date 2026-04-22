# 🧠 NEUROKEY: The Ultimate Keyboard Layout Optimizer

```text
███╗   ██╗███████╗██╗   ██╗██████╗  ██████╗ ██╗  ██╗███████╗██╗   ██╗
████╗  ██║██╔════╝██║   ██║██╔══██╗██╔═══██╗██║ ██╔╝██╔════╝╚██╗ ██╔╝
██╔██╗ ██║█████╗  ██║   ██║██████╔╝██║   ██║█████╔╝ █████╗   ╚████╔╝ 
██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔═██╗ ██╔══╝    ╚██╔╝  
██║ ╚████║███████╗╚██████╔╝██║  ██║╚██████╔╝██║  ██╗███████╗   ██║   
╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝   ╚═╝   
             HIGH-PERFORMANCE NEURAL KEYBOARD EVOLUTION
```

---

## 🚀 Quick Start Tutorial: Finding Your Perfect Layout

If you're new to layout optimization, follow these steps to find a layout that outperforms QWERTY by 40%+.

1.  **Select Your Engine**: 
    *   **CPU (Rust)**: Best for quick, 1-minute runs. Very stable.
    *   **GPU (PyTorch)**: Best for deep, 10-minute sessions. Uses massive parallelism to explore more of the "layout space."
2.  **Pick a Cooling Strategy**:
    *   **Exponential**: The gold standard. Starts random and slowly settles.
    *   **Linear**: A steady, predictable cooldown. Good for small tweaks.
    *   **Cosine**: High exploration at the start, very sharp settling at the end.
3.  **Set Your Priorities**:
    *   Want to type faster? Increase **SFB Penalty**.
    *   Want more comfort? Increase **Roll Bonus**.
    *   Want less fatigue? Increase **Effort Weight**.
4.  **Press 'Start Engine'**: Watch the Convergence Graph. When the line flattens out, you've found a local optimum!
5.  **Stop & Export**: Use the result in your favorite keyboard firmware (QMK, ZMK, etc.).

---

## 🏗️ Technical Architecture

NeuroKey utilizes a sophisticated **Hybrid Multi-Engine Architecture**.

### 1. The CPU Engine (Simulated Annealing)
Written in **Pure Rust**, this engine is optimized for single-core throughput. It is the most reliable engine for standard laptops and systems without a dedicated GPU.

### 2. The GPU Engine (PyTorch Tensor Batching)
For massive population-based searches, NeuroKey spawns a **Python Sidecar**. It evaluates 50,000+ layouts in a single GPU pass. **Note**: Requires NVIDIA/CUDA or Apple Silicon for best results.

---

## 🎮 GUI Control Reference

### 🌡️ Annealing Strategy
*   **Steps**: Total iterations. Recommended: `1,000,000` for quick runs, `10,000,000` for final results.
*   **Cooling Model**: 
    *   **Exponential**: `T = T_start * (T_end / T_start) ^ (step / total)`. Best all-rounder.
    *   **Linear**: `T = T_start - (T_start - T_end) * (step / total)`. Good for simple refinements.
    *   **Cosine**: Uses a cosine wave to cool down. High early exploration.
*   **Start/End Temp**: Higher start temp = more random exploration. Lower end temp = finer adjustments at the end.

### 📊 Visualization & Metrics
*   **Live Layout Updates**: The keyboard display updates in real-time as the engine discovers more ergonomic arrangements.
*   **Convergence Graph**: Tracks the "Efficiency Score" in real-time. A downward curve indicates the engine is successfully finding better layouts.
*   **Neural Load**: Monitors CPU/GPU utilization. Higher load means faster evaluations per second.
*   **Engine Telemetry**: A live log of system events, hardware acceleration status, and optimization milestones.

### 🧬 Biometric Weights
*   **SFB Penalty**: Penalizes same-finger bigrams (e.g., `ED`). High values eliminate SFBs entirely.
*   **Roll Bonus**: Rewards inward motions (Pinky -> Index). Makes typing feel "fluid."
*   **Outward Penalty**: Penalizes outward motions. Reduces finger "tripping."
*   **Effort Weight**: Penalizes far keys. High values force more common letters to the home row.
*   **Hand Balance**: Target work split. `0.5` = perfect 50/50 balance.

---

## 🛠️ Developer Setup

### Prerequisites
*   **Rust**: `rustup` for the core engine.
*   **Node.js**: `npm` for the React/Vite frontend.
*   **Python 3.10+**: For the PyTorch sidecar.

### Quick Start
```bash
npm install
npm run tauri dev
```

---

## 📊 Which Engine Should I Use?

| Feature | CPU Engine (Rust) | GPU Engine (PyTorch) |
| :--- | :--- | :--- |
| **Speed** | 10M+ evals/sec | 500M+ evals/sec |
| **Stability** | Rock Solid | Dependent on Drivers |
| **Search Depth** | Deep (Simulated Annealing) | Broad (Genetic Algorithm) |
| **Best For** | Daily Tweaking | Discovering New Layouts |

---

## 🛠️ Troubleshooting & FAQ

### 1. "Execution error: invalid args..."
This usually happens if the frontend sends `snake_case` keys to a Tauri command. NeuroKey uses `camelCase` in the frontend and `snake_case` in the Rust backend for optimal interoperability. Ensure your `invoke` calls match the documentation.

### 2. How to read Engine Telemetry?
The telemetry log provides high-resolution timing and status updates:
*   `[CORE]`: Messages from the Rust SA engine.
*   `[GPU]`: Messages from the PyTorch sidecar.
*   `[IPC]`: Communication events between the GUI and the backend.

### 3. Which cooling strategy is "best"?
For most users, **Exponential** is the most effective. If you have a layout that is already 90% perfect and you just want to swap a few keys, use **Linear** with a very low **Start Temp**.

---

## 🤝 Contributing New Engines

NeuroKey is designed to be extensible. You can add new optimization algorithms (like Particle Swarm or Ant Colony) by:
1.  Implementing the `Engine` trait in Rust.
2.  Adding the engine toggle to `App.tsx`.
3.  Registering the command in `lib.rs`.

---
