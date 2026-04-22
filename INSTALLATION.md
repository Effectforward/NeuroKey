# 🛠️ Installation Guide

This document provides detailed instructions for setting up the NeuroKey development environment on various operating systems.

## 1. Toolchain Requirements

Regardless of your OS, you will need the following core toolchains:

### **Rust**
NeuroKey requires the Rust stable toolchain (2021 edition or later).
*   **Install**: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
*   **Verify**: `rustc --version`

### **Node.js & NPM**
Requires Node.js v18+. We recommend using [nvm](https://github.com/nvm-sh/nvm).
*   **Install**: `nvm install 20`
*   **Verify**: `node -v`

### **Python**
Required for the GPU-accelerated sidecar and data processing scripts.
*   **Version**: Python 3.10 or newer.
*   **Packages**: `pip install -r python_engine/requirements.txt`

---

## 2. System Dependencies (Linux)

You must install the following development headers to support the Tauri GUI and the Rust compiler.

### **Fedora / RHEL / CentOS**
```bash
sudo dnf install \
    webkit2gtk4.1-devel \
    libappindicator-gtk3-devel \
    librsvg2-devel \
    openssl-devel \
    gcc-c++ \
    make \
    pkgconf-pkg-config \
    gtk3-devel \
    libsoup3-devel
```

### **Ubuntu / Debian / Linux Mint**
```bash
sudo apt update
sudo apt install \
    libwebkit2gtk-4.1-dev \
    libappindicator3-dev \
    librsvg2-dev \
    build-essential \
    curl \
    wget \
    libssl-dev \
    libgtk-3-dev \
    libsoup-3.0-dev
```

### **Arch Linux / Manjaro**
```bash
sudo pacman -Syu --needed \
    base-devel \
    webkit2gtk-4.1 \
    libappindicator-gtk3 \
    librsvg \
    openssl \
    libsoup3
```

### **openSUSE**
```bash
sudo zypper install -t pattern devel_basis
sudo zypper install \
    webkit2gtk3-devel \
    libappindicator3-devel \
    librsvg-devel \
    libopenssl-devel \
    libsoup3-devel
```

---

## 3. Post-Installation Check

Once the dependencies are installed, run the following to verify your environment:

```bash
# Clone the repository
git clone https://github.com/Effectforward/NeuroKey.git
cd NeuroKey

# Check if Tauri can build
npm install
npm run tauri build -- --debug
```

If the build succeeds, you are ready to start optimizing!
