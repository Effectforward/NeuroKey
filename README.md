# 🧠 NEUROKEY
### The Next Generation of Keyboard Layout Optimization

![NeuroKey Banner](https://img.shields.io/badge/Engine-Rust%20%7C%20PyTorch-blueviolet?style=for-the-badge)
![UI-Tauri](https://img.shields.io/badge/UI-Tauri%20%7C%20React-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

NeuroKey is a high-performance, cross-platform desktop application designed to evolve the "perfect" keyboard layout using **Simulated Annealing** and **Neural Population Dynamics**. By simulating millions of typing interactions per second, NeuroKey identifies layout configurations that minimize finger travel, reduce same-finger bigrams (SFBs), and maximize comfortable rolls.

---

## ✨ Key Features

*   **🚀 Dual-Engine Optimization**:
    *   **Rust (CPU)**: Ultra-stable, single-threaded simulated annealing for precision refinement.
    *   **PyTorch (GPU)**: Massively parallel genetic algorithms for broad-spectrum layout exploration.
*   **🌡️ Real-Time Convergence**: Watch your layout evolve live! Our glassmorphic UI streams engine telemetry and convergence graphs in real-time.
*   **🧬 Biometric Weighting**: Customize your ergonomic priorities—tune SFB penalties, inward roll bonuses, outward penalties, and hand balance to your exact finger anatomy.
*   **⚡ Modern Stack**: Built with **Rust**, **Tauri**, and **React** for a native feel with zero bloat.
*   **📊 Comprehensive Telemetry**: High-resolution logs and system load indicators keep you informed of the engine's health.

---

## 🎮 Getting Started (User Guide)

1.  **Launch the Dashboard**:
    ```bash
    npm install
    npm run tauri dev
    ```
2.  **Initialize the Engine**: Click **Start Engine**. Watch the ergonomic score drop as the AI finds better key placements.
3.  **Refine Your Style**: 
    *   Click the `?` icons next to any parameter for a deep dive into the ergonomic science.
    *   Use **Presets** to quickly compare against industry standards like Colemak or Dvorak.
4.  **Stop & Export**: Once the convergence graph flattens, you've hit an optimum. Save your layout and flash it to your keyboard!

---

## 🏗️ Developer Documentation

### Prerequisites
*   **Rust**: Stable toolchain (2021 edition+)
*   **Node.js**: v18+
*   **Python 3.10+**: (Only required for GPU engine)

### Setup & Data Retrieval
To train the engine on your own language or code corpus:
```bash
bash python_engine/get_data.sh
```
This script clones high-quality source code from 10+ languages and prose to build a representative n-gram frequency map.

### CI/CD Integration
NeuroKey includes a robust **GitHub Actions** workflow that verifies:
- ✅ Frontend build integrity
- ✅ Rust compilation and safety
- ✅ Unit testing for scoring logic

---

## 🔬 The Science of NeuroKey

NeuroKey doesn't just swap keys randomly. It uses a **thermal cooling schedule** (Exponential, Linear, or Cosine) to determine the probability of accepting a "worse" layout. This allows the AI to escape local optima (bad spots that look good) to find the true global maximum of typing efficiency.

---

## 🤝 Contributing

We welcome contributions! Whether you're an ergonomics expert, a Rustacean, or a UI designer, your input helps us build the future of typing.

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---

**Crafted with ❤️ by the NeuroKey Team. Finding the future of typing, one swap at a time.**
