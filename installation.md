# NeuroKey Installation Guide

Welcome to NeuroKey! This project is transitioning to a high-performance **Rust + Tauri** architecture with a **PyTorch GPU Backend**. 

## Prerequisites
To run or develop NeuroKey, you need the following dependencies installed on your system:

### 1. Python & Machine Learning
NeuroKey uses Python 3 for data scraping and PyTorch for GPU-accelerated layout evaluation.
*   **Python 3.10+**
*   **PyTorch**: Follow the official guide at [pytorch.org](https://pytorch.org/get-started/locally/) to install the correct version for your GPU.

### 2. Rust & Tauri
The core CPU engine and the Desktop GUI are built with Rust and Tauri.
*   **Rust**: Install via `rustup` ([rustup.rs](https://rustup.rs/))
*   **Node.js**: Version 18+ ([nodejs.org](https://nodejs.org/))
*   **Tauri Prerequisites**: Depending on your OS (Linux/Windows/macOS), you must install the OS-specific Tauri dependencies. See the [Tauri Prerequisites Guide](https://tauri.app/v1/guides/getting-started/prerequisites).

---

## Installation Steps

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/neurokey.git
cd neurokey
```

### Step 2: Set up Python Virtual Environment (Optional but Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
# If you haven't installed PyTorch globally, install it here.
# Example for CUDA 12.1:
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Step 4: Download Corpus Data
Before running any optimizations, you need to download the corpus data which will be used to generate the n-gram frequencies.
```bash
bash get_data.sh
```
*Note: This script will download gigabytes of code from various GitHub repositories to build a mathematically accurate model of modern programming languages. It may take some time.*

### Step 5: Start the Web UI (Legacy Python Mode)
Currently, NeuroKey runs via a Flask web interface.
```bash
python3 gui.py
```
Open `http://localhost:5000` in your web browser. From here, you can select between the **Simulated Annealing (CPU)** engine or the **PyTorch Tensor Batching (GPU)** engine.

---

## Future Release: Tauri Native App
We are actively working on `NeuroKey v2.0` which bundles everything into a single desktop application.

### Key GUI Features
*   **Advanced Ergonomic Weights**: Fine-tune SFB penalties, Roll bonuses, and Effort weights directly from the UI.
*   **Live Convergence Charts**: Monitor optimization progress with real-time score tracking.
*   **Layout Presets**: Instantly switch between QWERTY, Dvorak, and Colemak.
*   **System Telemetry**: Real-time monitoring of CPU/GPU load and optimization logs.

---
*Note: If you are a developer, ensure you run `npm install` to fetch the new `recharts` and `lucide-react` dependencies.*
