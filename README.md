# 🧠 NEUROKEY
### The Next Generation of Keyboard Layout Optimization

![NeuroKey Banner](https://img.shields.io/badge/Engine-Rust%20%7C%20PyTorch-blueviolet?style=for-the-badge)
![UI-Tauri](https://img.shields.io/badge/UI-Tauri%20%7C%20React-blue?style=for-the-badge)

NeuroKey is a high-performance desktop application designed to evolve the "perfect" keyboard layout using Simulated Annealing and Neural Population Dynamics.

---

## 🛠️ Prerequisites & Installation

To build and run NeuroKey, you must install the following development toolchains and system-level libraries for your specific Linux distribution.

### 1. Development Toolchains (All Platforms)
*   **Rust**: [rustup.rs](https://rustup.rs/) (Stable 1.75+)
*   **Node.js**: v18 or later ([nvm](https://github.com/nvm-sh/nvm) recommended)
*   **Python**: 3.10+ (For GPU acceleration)

### 2. System Dependencies (Distro-Specific)

You must install these libraries to support the Tauri GUI and the Rust compilation process.

#### **🟦 Fedora / RHEL**
```bash
sudo dnf install webkit2gtk4.1-devel libappindicator-gtk3-devel librsvg2-devel openssl-devel gcc-c++ make pkgconf-pkg-config
```

#### **🟧 Ubuntu / Debian / Mint**
```bash
sudo apt update
sudo apt install libwebkit2gtk-4.1-dev libappindicator3-dev librsvg2-dev build-essential curl wget libssl-dev libgtk-3-dev
```

#### **⬜ Arch Linux / Manjaro**
```bash
sudo pacman -Syu --needed base-devel webkit2gtk-4.1 libappindicator-gtk3 librsvg openssl
```

#### **🟩 openSUSE**
```bash
sudo zypper install -t pattern devel_basis
sudo zypper install webkit2gtk3-devel libappindicator3-devel librsvg-devel libopenssl-devel
```

### 3. Neural Engine Setup
The GPU-accelerated sidecar requires specific Python packages. Navigate to the project root and run:
```bash
pip install -r python_engine/requirements.txt
```

---

## 🎮 Getting Started

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/Effectforward/NeuroKey.git
    cd NeuroKey
    ```
2.  **Install Frontend**:
    ```bash
    npm install
    ```
3.  **Fetch Training Data**:
    ```bash
    bash python_engine/get_data.sh
    ```
4.  **Run Development Mode**:
    ```bash
    npm run tauri dev
    ```

---

## ✨ Key Features

*   **🚀 Dual-Engine Optimization**: Switch between Rust (CPU) for precision and PyTorch (GPU) for broad exploration.
*   **🌡️ Real-Time Convergence**: Live telemetry and convergence graphs.
*   **🧬 Biometric Weighting**: Tune SFB penalties, rolls, and hand balance.
*   **📥 Presets**: Compare against QWERTY, Dvorak, and Colemak out of the box.

---

## 🏗️ Project Architecture

*   **`src-tauri/`**: High-performance Rust backend & IPC bridge.
*   **`ui/`**: React-based dashboard with Recharts visualization.
*   **`python_engine/`**: Neural sidecar logic and `requirements.txt`.
*   **`.github/workflows/`**: Fedora-based CI/CD pipeline.

---

**Crafted with ❤️ by the NeuroKey Team. Finding the future of typing, one swap at a time.**
