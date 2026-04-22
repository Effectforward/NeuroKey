# NeuroKey Development Guide

Welcome to the NeuroKey contributor community! We are actively transitioning from a Python Flask application into a native desktop application powered by **Rust** and **Tauri**.

## Architecture Overview
The new architecture is a **Sidecar Pattern**:
1. **Frontend (Tauri + React):** A sleek, premium desktop UI that runs offline without needing a browser.
2. **Backend 1 (Rust Engine):** The CPU-based Simulated Annealing algorithm is being rewritten in Rust for maximum performance (10-50x speedup over Python).
3. **Backend 2 (PyTorch Sidecar):** The GPU-accelerated tensor layout generation runs in Python via PyTorch and is spawned as a sidecar process by the Tauri backend.

## Setting Up Your Development Environment

### 1. Install Rust
Install the Rust toolchain via [rustup.rs](https://rustup.rs/).

### 2. Install Tauri Prerequisites
Depending on your OS, install the necessary native dependencies. See the [Tauri Getting Started Guide](https://tauri.app/v1/guides/getting-started/prerequisites).

### 3. Install Node.js
Install Node v18+ to run the React frontend build tools.

### 4. Install Python Dependencies
For the PyTorch sidecar, you need a local Python environment.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running Tests
We use `pytest` for the Python backend. Run the test suite before submitting any Pull Requests:
```bash
python3 -m pytest test_neurokey.py -v
```

## Code of Conduct
Please read our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing to ensure a welcoming environment for everyone.
