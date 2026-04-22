# 🧠 NEUROKEY
### The Next Generation of Keyboard Layout Optimization

![NeuroKey Banner](https://img.shields.io/badge/Engine-Rust%20%7C%20PyTorch-blueviolet?style=for-the-badge&logo=rust)
![UI-Tauri](https://img.shields.io/badge/UI-Tauri%20%7C%20React-blue?style=for-the-badge&logo=react)
![Build](https://img.shields.io/badge/CI-Fedora%20Actions-brightgreen?style=for-the-badge&logo=fedora)

NeuroKey is a high-performance desktop application designed to evolve the "perfect" keyboard layout using **Simulated Annealing** and **Neural Population Dynamics**.

---

## ✨ Features at a Glance

*   **🚀 Real-Time Convergence**: Live telemetry and convergence graphs.
*   **🌡️ Advanced Cooling**: Exponential, Linear, and Cosine annealing models.
*   **🧬 Biometric Tuning**: Penalties for SFBs, outward rolls, and hand balance.
*   **🐧 Native Performance**: Optimized for Fedora and other major Linux distros.
*   **📚 Deep Documentation**: Comprehensive guides for all user levels.

---

## 🚦 System Workflow

1.  **📥 Data Ingestion**: Load language/code corpora to build frequency maps.
2.  **⚙️ Weight Tuning**: Set your ergonomic priorities in the dashboard.
3.  **🔥 Ignition**: Start the engine and watch the layout evolve in real-time.
4.  **💾 Export**: Save your optimized layout for use in your favorite keyboard firmware.

---

## 🚀 Quick Start

1.  **Install Dependencies**: See our [Detailed Installation Guide](INSTALLATION.md).
2.  **Setup & Run**:
    ```bash
    git clone https://github.com/Effectforward/NeuroKey.git
    npm install
    bash python_engine/get_data.sh
    npm run tauri dev
    ```

---

## 📖 Documentation Suite

*   **[🛠️ Installation Guide](INSTALLATION.md)**: System dependencies and OS-specific setup.
*   **[🏗️ Development Architecture](DEVELOPMENT.md)**: Project structure and IPC bridge.
*   **[🔬 Algorithm Science](ALGORITHMS.md)**: Deep dive into the math and scoring.

---

## 🔬 The Science

NeuroKey utilizes a probabilistic cooling schedule to explore trillions of possible keyboard configurations. It avoids local bad spots to find the global optimum for your typing style.

> [!TIP]
> Use the **Help Icons (`?`)** in the application dashboard to learn more about each parameter while you optimize!

---

**Crafted with ❤️ by the NeuroKey Team. Finding the future of typing, one swap at a time.**
