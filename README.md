# 🧠 NEUROKEY
### The Next Generation of Keyboard Layout Optimization

![NeuroKey Banner](https://img.shields.io/badge/Engine-Rust%20%7C%20PyTorch-blueviolet?style=for-the-badge)
![UI-Tauri](https://img.shields.io/badge/UI-Tauri%20%7C%20React-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

NeuroKey is a high-performance, cross-platform desktop application designed to evolve the "perfect" keyboard layout using **Simulated Annealing** and **Neural Population Dynamics**.

---

## 🛠️ Prerequisites & Installation

Before running NeuroKey, you need to install the core development toolchains and system dependencies.

### 1. Core Toolchains
*   **Rust**: Install via [rustup.rs](https://rustup.rs/)
    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    ```
*   **Node.js**: Install v18 or later (Recommended via [nvm](https://github.com/nvm-sh/nvm))
    ```bash
    nvm install 20
    ```
*   **Python 3.10+**: Required for the GPU-accelerated sidecar.

### 2. System Dependencies (OS Specific)

#### **Fedora (Recommended)**
```bash
sudo dnf install webkit2gtk4.1-devel libappindicator-gtk3-devel librsvg2-devel openssl-devel gcc-c++ make
```

#### **Ubuntu / Debian**
```bash
sudo apt-get update
sudo apt-get install libwebkit2gtk-4.1-dev libayatana-appindicator3-dev librsvg2-dev build-essential curl wget libssl-dev
```

### 3. Python Environment (Sidecar)
The neural engine dependencies are located in the `python_engine` directory.
```bash
pip install -r python_engine/requirements.txt
```

---

## 🎮 Getting Started

1.  **Clone & Install Frontend**:
    ```bash
    git clone https://github.com/Effectforward/NeuroKey.git
    cd NeuroKey
    npm install
    ```
2.  **Fetch Training Data**:
    To train the engine on real-world code and prose:
    ```bash
    bash python_engine/get_data.sh
    ```
3.  **Launch the Dashboard**:
    ```bash
    npm run tauri dev
    ```

---

## ✨ Key Features

*   **🚀 Dual-Engine Optimization**:
    *   **Rust (CPU)**: Ultra-stable, single-threaded simulated annealing for precision refinement.
    *   **PyTorch (GPU)**: Genetic algorithms for broad-spectrum layout exploration (requires Python sidecar).
*   **🌡️ Real-Time Convergence**: Watch your layout evolve live with glassmorphic UI telemetry.
*   **🧬 Biometric Weighting**: Tune SFB penalties, inward roll bonuses, and effort weights to your anatomy.
*   **📊 Convergence Tracking**: High-resolution graphs showing the mathematical descent towards ergonomics.

---

## 🏗️ Developer Notes

### CI/CD Workflow
NeuroKey uses a **Fedora-based GitHub Actions** workflow to ensure build stability. If you are contributing, your PRs will be automatically tested against the latest Fedora environment.

### Project Structure
*   `/src-tauri`: Core Rust logic, IPC commands, and the Annealing engine.
*   `/ui`: React frontend built with Vite and Lucide.
*   `/python_engine`: PyTorch sidecar, data retrieval scripts, and n-gram caches.

---

## 🤝 Contributing

We welcome contributions! Please see [development.md](development.md) for architecture details.

1.  Fork the repo and create your feature branch.
2.  Ensure your code passes `cargo check` and `npm run build`.
3.  Open a Pull Request.

---

**Crafted with ❤️ by the NeuroKey Team. Finding the future of typing, one swap at a time.**
