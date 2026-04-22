# 🏗️ Development Architecture

NeuroKey is a hybrid desktop application designed for maximum computational throughput and a modern user experience.

## 🌉 The Tauri-React Bridge

The application uses an **Asynchronous IPC (Inter-Process Communication)** bridge to handle heavy computations without freezing the UI.

### 1. Command Invocation
Frontend calls to the backend are handled via `invoke`:
```typescript
const result = await invoke("run_optimization", { weights, steps });
```

### 2. Real-Time Telemetry (Events)
The Rust engine emits state updates during the annealing process:
```rust
handle.emit("best_layout_found", payload);
```
The React frontend listens for these events to update the Convergence Graph and the Keyboard Layout live:
```typescript
listen<BestLayoutPayload>("best_layout_found", (event) => {
  setLayout(event.payload.layout);
});
```

---

## 📂 Project Structure

| Directory | Purpose |
| :--- | :--- |
| **`src-tauri/`** | Core Rust optimization logic and IPC commands. |
| **`ui/`** | React frontend, styles, and dashboard logic. |
| **`python_engine/`** | GPU sidecar, data scripts, and n-gram caches. |
| **`.github/`** | CI/CD automation for Fedora. |

---

## 🧪 Testing & Verification

### Rust Backend
```bash
cargo test --manifest-path src-tauri/Cargo.toml
```

### Frontend
```bash
npm run build
```

---

## 🛠️ Performance Optimization

*   **Release Builds**: Use `npm run tauri build` for production-grade speed.
*   **Zero-Cost Abstractions**: Rust ensures the scoring logic runs at near-hardware speeds.
