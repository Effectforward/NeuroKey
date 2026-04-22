# 🏗️ Development Architecture

NeuroKey is built as a hybrid desktop application, leveraging the safety of Rust and the flexibility of React.

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
listen("best_layout_found", (event) => {
  setLayout(event.payload.layout);
});
```

---

## 📂 Project Structure

*   **`src-tauri/src/optimizer.rs`**: The core Simulated Annealing logic.
*   **`src-tauri/src/scorer.rs`**: The ergonomic scoring engine (SFBs, Rolls, Effort).
*   **`ui/App.tsx`**: The main dashboard component and state manager.
*   **`python_engine/`**: The PyTorch-based sidecar for GA (Genetic Algorithm) exploration.

---

## 🧪 Testing & Verification

### Rust Backend
Run unit tests for the scoring logic:
```bash
cargo test --manifest-path src-tauri/Cargo.toml
```

### Frontend
Verify the build and run TypeScript checks:
```bash
npm run build
```

---

## 🛠️ Performance Optimization

*   **Release Builds**: Always use `npm run tauri build` for performance testing, as the Rust optimizer is significantly faster with `--release` flags.
*   **Multi-threading**: The SA engine is currently single-threaded for precision, but the Scorer is designed for thread-safe parallelization.
