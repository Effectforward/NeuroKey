# 🧠 NEUROKEY
### The Next Generation of Keyboard Layout Optimization

![NeuroKey Banner](https://img.shields.io/badge/Engine-Rust%20%7C%20PyTorch-blueviolet?style=for-the-badge)
![UI-Tauri](https://img.shields.io/badge/UI-Tauri%20%7C%20React-blue?style=for-the-badge)
![Build](https://img.shields.io/badge/CI-Fedora%20Actions-brightgreen?style=for-the-badge)

NeuroKey is a high-performance desktop application designed to evolve the "perfect" keyboard layout using **Simulated Annealing** and **Neural Population Dynamics**. By simulating millions of interactions per second, NeuroKey identifies configurations that minimize finger travel and maximize typing comfort.

---

## ✨ Features at a Glance

*   **🚀 Real-Time Convergence**: Watch your layout evolve live with high-fidelity telemetry.
*   **🌡️ Advanced Cooling**: Choose between Exponential, Linear, and Cosine annealing models.
*   **🧬 Biometric Tuning**: Customize penalties for Same-Finger Bigrams (SFBs), outward rolls, and hand usage.
*   **🐧 Native Performance**: Built with **Rust** and **Tauri** for a lightweight, native experience on Fedora and beyond.
*   **📚 Deep Documentation**: Comprehensive guides for installation, development, and mathematical theory.

---

## 🚀 Quick Start

1.  **Install Dependencies**:
    See our [Detailed Installation Guide](INSTALLATION.md) for Fedora, Ubuntu, Arch, and more.
2.  **Clone & Setup**:
    ```bash
    git clone https://github.com/Effectforward/NeuroKey.git
    cd NeuroKey
    npm install
    ```
3.  **Fetch Data**:
    ```bash
    bash python_engine/get_data.sh
    ```
4.  **Run**:
    ```bash
    npm run tauri dev
    ```

---

## 📖 Documentation Suite

We maintain a complete documentation ecosystem to help you get the most out of NeuroKey:

*   **[🛠️ Installation Guide](INSTALLATION.md)**: System dependencies, toolchain setup, and OS-specific troubleshooting.
*   **[🏗️ Development Architecture](DEVELOPMENT.md)**: Project structure, Tauri-React IPC bridge, and contribution guidelines.
*   **[🔬 Algorithm Science](ALGORITHMS.md)**: Deep dive into the Simulated Annealing math and Ergonomic Cost Functions.
*   **[📝 Roadmap](development.md)**: Our future plans for GPU acceleration and mobile support.

---

## 🧬 The Core Logic

NeuroKey doesn't just swap keys randomly. It calculates an **Ergonomic Score** based on real-world typing frequencies. It then uses a probabilistic "acceptance criterion" to escape local bad spots and find a global optimum for your specific typing style.

> [!TIP]
> Use the **Help Icons (`?`)** in the application dashboard to learn more about each parameter while you optimize!

---

## 🤝 Contributing

We welcome contributions from ergonomics experts, Rustaceans, and UI designers! 

1.  Fork the repository.
2.  Follow the [Development Guide](DEVELOPMENT.md) to set up your environment.
3.  Open a Pull Request with a clear description of your changes.

---

**Crafted with ❤️ by the NeuroKey Team. Finding the future of typing, one swap at a time.**
