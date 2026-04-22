# OptiKey: AI-Powered Keyboard Layout Optimizer

OptiKey is an advanced, AI-powered keyboard layout optimizer designed to find the **mathematically optimal keyboard layout for programming and general typing**. 

Unlike other layout generators that optimize only for English prose, OptiKey uses a multi-language programming corpus (Python, JavaScript, Rust, C++, Go, Java, TypeScript, C, Ruby, Shell, and Markdown docs) to build an N-gram frequency model of how developers *actually* type.

It uses **Simulated Annealing (SA)**, a powerful stochastic optimization algorithm from the machine learning family, running in parallel to search through the `30!` (2.65×10³²) possible layout permutations.

---

## 🌟 Features

* **Beautiful Web GUI**: Comes with a sleek, real-time dashboard to monitor the optimization process, visualize the current best layout, and view live metrics.
* **Programming-First Corpus**: Optimized for real code, not just novels. Includes syntax frequencies for 10+ major languages.
* **10 Ergonomic Metrics**: Evaluates Effort, Same-Finger Bigrams (SFB), Same-Finger Skipgrams (SFS), Inward/Outward Rolls, Lateral Stretches, Hand Balance, Finger Overload, and Redirects.
* **Parallel Optimization**: Spawns multiple independent Simulated Annealing workers to utilize all CPU cores effectively.
* **Distributable**: Volunteers and contributors can easily clone the repo, fetch the data, and run the optimizer to help find the global optimum.

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have Python 3 installed. Then, install the dependencies:

```bash
pip install -r requirements.txt
pip install flask
```

### 2. Fetch the Training Corpus
OptiKey requires real code to learn from. Run the fast data fetch script to automatically clone popular open-source repositories and extract their code into the training corpus.

```bash
bash get_fast_data.sh
```
*(This script fetches Python, Rust, C, C++, JS, Go, Java, TS, Ruby, Shell, and Markdown. It then automatically rebuilds the N-gram frequency cache.)*

### 3. Launch the GUI
Start the beautiful web dashboard to control and monitor the optimization process:

```bash
python gui.py
```
Open your browser to `http://localhost:5000`. From the dashboard, you can click **Start Optimization** and watch the AI discover better layouts in real-time.

---

## 🧠 How it Works

1. **Corpus Generation**: The tool scans millions of lines of code to build unigram, bigram, and trigram frequency tables.
2. **Scoring Function (`scorer.py`)**: A fitness function assigns a penalty score to any given layout. A lower score means a more ergonomic layout.
3. **Simulated Annealing (`optimizer.py`)**: 
   - The AI starts with a random layout (or a known layout like QWERTY) at a high "temperature".
   - It randomly swaps two keys. If the new layout is better (lower score), it keeps it.
   - If it's worse, it *might* still keep it depending on the temperature. This helps the AI escape local minima.
   - Over millions of steps, the temperature "cools" down, and the AI fine-tunes the layout into a highly optimized state.

---

## 🛠️ CLI Usage (Headless Mode)

If you prefer the terminal or want to run this on a headless server:

```bash
# Start or resume the optimizer
python main.py optimize

# View the best layout found so far
python main.py show-best

# Compare known layouts (QWERTY, Colemak-DH, Graphite, etc.) against your corpus
python main.py compare

# Analyze a specific layout string
python main.py analyze qwerty
```

---

## ⚖️ Tuning the Algorithm

OptiKey is highly customizable. Edit `config.py` to change:

* **Language Weights (`CORPUS_WEIGHTS`)**: If you write more JavaScript than Rust, increase the JS weight.
* **Ergonomic Penalties (`WEIGHTS`)**: Want to completely eliminate Same-Finger Bigrams? Increase the `sfb` weight from `10.0` to `20.0`.
* **Simulated Annealing Parameters (`SA`)**: Adjust the cooling schedule, starting temperature, and number of parallel workers.

> Note: If you change `CORPUS_WEIGHTS`, you must rebuild the cache by running `python main.py rebuild-corpus`.

---

## 🤝 Contributing

We welcome volunteers to run the optimizer on their machines! Finding the absolute best layout out of `2.65×10³²` possibilities requires massive compute. 

1. Clone the repository.
2. Let the optimizer run for a few days.
3. Share your `results/best_layout.pkl` or the flat string output!

### Hardware Acceleration (Future Work)
Currently, OptiKey utilizes 100% of your CPU via parallel multiprocessing. Future updates may introduce GPU acceleration (via CUDA/JAX) to evaluate millions of layout permutations concurrently.
