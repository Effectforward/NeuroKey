#!/usr/bin/env bash
# get_data.sh — Download corpus data for keyboard layout optimization
#
# This script downloads source code in 10+ programming languages
# plus English prose. Total data: ~30-100GB depending on selections.
#
# REQUIREMENTS:
#   - git, wget, curl, python3, pip
#   - huggingface_hub: pip install huggingface_hub datasets
#   - ~200GB free disk space for raw data (processed n-grams are ~500MB)
#
# WHAT WE DOWNLOAD:
#   1. The Stack (HuggingFace) — 6TB of code, we sample subsets per language
#   2. CodeSearchNet — Python, Java, JS, PHP, Ruby, Go
#   3. BigCode The Stack Dedup — deduplicated, higher quality
#   4. Linux kernel source (C) — canonical C code
#   5. CPython source (Python)
#   6. Rust standard library + top crates
#   7. Wikipedia dump (English prose for comments/docstrings)
#
# RUNTIME: Expect 4-12 hours depending on your connection
# STORAGE:  ~50GB raw, ~500MB processed n-gram cache

set -e

DATA_DIR="data/corpus"
mkdir -p "$DATA_DIR"

echo "============================================================"
echo "  Keyboard Optimizer — Corpus Downloader"
echo "  Target: 20M+ lines of code in 10 languages"
echo "============================================================"
echo ""

# ─────────────────────────────────────────────────────────────
# PYTHON — via HuggingFace The Stack
# ─────────────────────────────────────────────────────────────
echo "[1/10] Python corpus..."
mkdir -p "$DATA_DIR/python"
python3 - <<'PYEOF'
from datasets import load_dataset
import os

# Download 5GB sample of Python from The Stack (deduplicated)
# The Stack requires accepting the license at:
# https://huggingface.co/datasets/bigcode/the-stack-dedup
# After accepting, run: huggingface-cli login

ds = load_dataset(
    "bigcode/the-stack-dedup",
    data_dir="data/python",
    split="train",
    streaming=True,
    trust_remote_code=True,
)

out_dir = "data/corpus/python"
os.makedirs(out_dir, exist_ok=True)

max_bytes = 3 * 1024**3  # 3GB
written = 0
file_idx = 0
current_file = None

for sample in ds:
    code = sample.get('content', '')
    if not code:
        continue
    encoded = code.encode('utf-8', errors='ignore')
    
    if written == 0 or written % (100 * 1024**2) == 0:
        if current_file:
            current_file.close()
        fname = os.path.join(out_dir, f"python_{file_idx:04d}.txt")
        current_file = open(fname, 'wb')
        file_idx += 1
    
    current_file.write(encoded + b'\n')
    written += len(encoded)
    
    if written >= max_bytes:
        break

if current_file:
    current_file.close()

print(f"Python: wrote {written/1e9:.2f} GB")
PYEOF
echo "  Python done."


# ─────────────────────────────────────────────────────────────
# RUST — via HuggingFace The Stack
# ─────────────────────────────────────────────────────────────
echo "[2/10] Rust corpus..."
mkdir -p "$DATA_DIR/rust"
python3 - <<'PYEOF'
from datasets import load_dataset
import os

ds = load_dataset(
    "bigcode/the-stack-dedup",
    data_dir="data/rust",
    split="train",
    streaming=True,
    trust_remote_code=True,
)

out_dir = "data/corpus/rust"
os.makedirs(out_dir, exist_ok=True)
max_bytes = 2 * 1024**3
written = 0
file_idx = 0
current_file = None

for sample in ds:
    code = sample.get('content', '')
    if not code: continue
    encoded = code.encode('utf-8', errors='ignore')
    if written == 0 or written % (100 * 1024**2) == 0:
        if current_file: current_file.close()
        current_file = open(os.path.join(out_dir, f"rust_{file_idx:04d}.txt"), 'wb')
        file_idx += 1
    current_file.write(encoded + b'\n')
    written += len(encoded)
    if written >= max_bytes: break

if current_file: current_file.close()
print(f"Rust: wrote {written/1e9:.2f} GB")
PYEOF
echo "  Rust done."


# ─────────────────────────────────────────────────────────────
# C — Linux kernel source (canonical C, very large)
# ─────────────────────────────────────────────────────────────
echo "[3/10] C corpus (Linux kernel)..."
mkdir -p "$DATA_DIR/c"
if [ ! -d "/tmp/linux_kernel" ]; then
    echo "  Cloning Linux kernel (shallow, ~1GB)..."
    git clone --depth=1 https://github.com/torvalds/linux.git /tmp/linux_kernel
fi
echo "  Extracting .c files..."
find /tmp/linux_kernel -name "*.c" -exec cat {} \; > "$DATA_DIR/c/linux_kernel.txt"
echo "  Linux kernel done: $(wc -l < $DATA_DIR/c/linux_kernel.txt) lines"

# Also get sqlite (excellent C)
if [ ! -f "$DATA_DIR/c/sqlite3.c" ]; then
    wget -q "https://www.sqlite.org/src/raw/sqlite3.c" -O "$DATA_DIR/c/sqlite3.c" || true
fi


# ─────────────────────────────────────────────────────────────
# C++ — LLVM/Clang source
# ─────────────────────────────────────────────────────────────
echo "[4/10] C++ corpus (LLVM)..."
mkdir -p "$DATA_DIR/cpp"
if [ ! -d "/tmp/llvm_project" ]; then
    echo "  Cloning LLVM (shallow, ~2GB)..."
    git clone --depth=1 https://github.com/llvm/llvm-project.git /tmp/llvm_project
fi
find /tmp/llvm_project -name "*.cpp" | head -5000 | xargs cat > "$DATA_DIR/cpp/llvm.txt" 2>/dev/null || true
echo "  LLVM C++ done."


# ─────────────────────────────────────────────────────────────
# JAVASCRIPT — via CodeSearchNet
# ─────────────────────────────────────────────────────────────
echo "[5/10] JavaScript corpus (CodeSearchNet)..."
mkdir -p "$DATA_DIR/javascript"
python3 - <<'PYEOF'
from datasets import load_dataset
import os

ds = load_dataset("code_search_net", "javascript", split="train", trust_remote_code=True)
out_path = "data/corpus/javascript/codesearchnet_js.txt"
os.makedirs(os.path.dirname(out_path), exist_ok=True)

with open(out_path, 'w', encoding='utf-8', errors='ignore') as f:
    for sample in ds:
        f.write(sample.get('whole_func_string', '') + '\n\n')

print(f"JavaScript: {len(ds):,} functions")
PYEOF

# Also The Stack for more JS
python3 - <<'PYEOF'
from datasets import load_dataset
import os

ds = load_dataset("bigcode/the-stack-dedup", data_dir="data/javascript",
                  split="train", streaming=True, trust_remote_code=True)
out_dir = "data/corpus/javascript"
max_bytes = 1 * 1024**3
written = 0; file_idx = 0; current_file = None

for sample in ds:
    code = sample.get('content', '')
    if not code: continue
    encoded = code.encode('utf-8', errors='ignore')
    if written == 0 or written % (100*1024**2) == 0:
        if current_file: current_file.close()
        current_file = open(os.path.join(out_dir, f"stack_js_{file_idx:04d}.txt"), 'wb')
        file_idx += 1
    current_file.write(encoded + b'\n'); written += len(encoded)
    if written >= max_bytes: break
if current_file: current_file.close()
print(f"JS Stack: wrote {written/1e9:.2f} GB")
PYEOF
echo "  JavaScript done."


# ─────────────────────────────────────────────────────────────
# GO
# ─────────────────────────────────────────────────────────────
echo "[6/10] Go corpus..."
mkdir -p "$DATA_DIR/go"
python3 - <<'PYEOF'
from datasets import load_dataset
import os

ds = load_dataset("code_search_net", "go", split="train", trust_remote_code=True)
with open("data/corpus/go/codesearchnet_go.txt", 'w', encoding='utf-8', errors='ignore') as f:
    for sample in ds:
        f.write(sample.get('whole_func_string', '') + '\n\n')
print(f"Go: {len(ds):,} functions")
PYEOF
echo "  Go done."


# ─────────────────────────────────────────────────────────────
# JAVA — GitHub Java Corpus (same as adumb video!)
# ─────────────────────────────────────────────────────────────
echo "[7/10] Java corpus (GitHub Java Corpus)..."
mkdir -p "$DATA_DIR/java"
python3 - <<'PYEOF'
from datasets import load_dataset
import os

# CodeSearchNet Java
ds = load_dataset("code_search_net", "java", split="train", trust_remote_code=True)
with open("data/corpus/java/codesearchnet_java.txt", 'w', encoding='utf-8', errors='ignore') as f:
    for sample in ds:
        f.write(sample.get('whole_func_string', '') + '\n\n')
print(f"Java CSN: {len(ds):,} functions")

# Also The Stack Java
ds2 = load_dataset("bigcode/the-stack-dedup", data_dir="data/java",
                   split="train", streaming=True, trust_remote_code=True)
out = "data/corpus/java"
max_bytes = 1*1024**3; written = 0; file_idx = 0; f2 = None
for sample in ds2:
    code = sample.get('content', '')
    if not code: continue
    enc = code.encode('utf-8', errors='ignore')
    if written == 0 or written % (100*1024**2) == 0:
        if f2: f2.close()
        f2 = open(os.path.join(out, f'stack_java_{file_idx:04d}.txt'), 'wb'); file_idx += 1
    f2.write(enc + b'\n'); written += len(enc)
    if written >= max_bytes: break
if f2: f2.close()
print(f"Java Stack: {written/1e9:.2f} GB")
PYEOF
echo "  Java done."


# ─────────────────────────────────────────────────────────────
# TYPESCRIPT
# ─────────────────────────────────────────────────────────────
echo "[8/10] TypeScript corpus..."
mkdir -p "$DATA_DIR/typescript"
python3 - <<'PYEOF'
from datasets import load_dataset
import os

ds = load_dataset("bigcode/the-stack-dedup", data_dir="data/typescript",
                  split="train", streaming=True, trust_remote_code=True)
out = "data/corpus/typescript"
max_bytes = 1*1024**3; written = 0; file_idx = 0; f = None
for sample in ds:
    code = sample.get('content', '')
    if not code: continue
    enc = code.encode('utf-8', errors='ignore')
    if written == 0 or written % (100*1024**2) == 0:
        if f: f.close()
        f = open(os.path.join(out, f'ts_{file_idx:04d}.txt'), 'wb'); file_idx += 1
    f.write(enc + b'\n'); written += len(enc)
    if written >= max_bytes: break
if f: f.close()
print(f"TypeScript: {written/1e9:.2f} GB")
PYEOF
echo "  TypeScript done."


# ─────────────────────────────────────────────────────────────
# RUBY
# ─────────────────────────────────────────────────────────────
echo "[9/10] Ruby corpus..."
mkdir -p "$DATA_DIR/ruby"
python3 - <<'PYEOF'
from datasets import load_dataset
import os

ds = load_dataset("code_search_net", "ruby", split="train", trust_remote_code=True)
with open("data/corpus/ruby/codesearchnet_ruby.txt", 'w', encoding='utf-8', errors='ignore') as f:
    for sample in ds:
        f.write(sample.get('whole_func_string', '') + '\n\n')
print(f"Ruby: {len(ds):,} functions")
PYEOF
echo "  Ruby done."


# ─────────────────────────────────────────────────────────────
# SHELL / BASH
# ─────────────────────────────────────────────────────────────
echo "[10/10] Shell corpus..."
mkdir -p "$DATA_DIR/shell"
python3 - <<'PYEOF'
from datasets import load_dataset
import os

ds = load_dataset("bigcode/the-stack-dedup", data_dir="data/shell",
                  split="train", streaming=True, trust_remote_code=True)
out = "data/corpus/shell"
max_bytes = 300*1024**2; written = 0; f = None
for sample in ds:
    code = sample.get('content', '')
    if not code: continue
    enc = code.encode('utf-8', errors='ignore')
    if written == 0:
        f = open(os.path.join(out, 'shell.txt'), 'wb')
    f.write(enc + b'\n'); written += len(enc)
    if written >= max_bytes: break
if f: f.close()
print(f"Shell: {written/1e6:.0f} MB")
PYEOF
echo "  Shell done."


# ─────────────────────────────────────────────────────────────
# ENGLISH PROSE — Wikipedia (for comments, docs, README text)
# ─────────────────────────────────────────────────────────────
echo "[+] English prose (Wikipedia subset)..."
mkdir -p "$DATA_DIR/english"
python3 - <<'PYEOF'
from datasets import load_dataset
import os

# Small Wikipedia subset is enough for prose
ds = load_dataset("wikipedia", "20220301.en", split="train",
                  streaming=True, trust_remote_code=True)
out = "data/corpus/english/wikipedia.txt"
max_bytes = 500*1024**2; written = 0
with open(out, 'w', encoding='utf-8', errors='ignore') as f:
    for sample in ds:
        text = sample.get('text', '')
        enc = text.encode('utf-8', errors='ignore')
        f.write(text + '\n\n'); written += len(enc)
        if written >= max_bytes: break
print(f"English: {written/1e6:.0f} MB")
PYEOF
echo "  English done."


# ─────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "  Download complete!"
echo "============================================================"
echo ""
echo "Corpus sizes:"
du -sh data/corpus/*/  2>/dev/null || true
echo ""
total_lines=$(find data/corpus -name "*.txt" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
echo "Total lines: ~${total_lines}"
echo ""
echo "Next step: python main.py test"
echo "Then:       python main.py optimize"
echo ""
echo "NOTE: First run will take 1-4 hours to build n-gram cache."
echo "After that, subsequent runs load from cache in seconds."


# ─────────────────────────────────────────────────────────────
# ALTERNATIVE: Direct download without HuggingFace
# ─────────────────────────────────────────────────────────────
# If you don't want to use HuggingFace, these are direct sources:
#
# Python:     https://huggingface.co/datasets/codeparrot/github-code
# GitHub Code (all langs): https://huggingface.co/datasets/codeparrot/github-code
# arXiv papers (like adumb's video): https://www.kaggle.com/datasets/Cornell-University/arxiv
# GitHub Java Corpus (like adumb): https://groups.inf.ed.ac.uk/cup/javaGithub/
# Stack Overflow dump:  https://archive.org/details/stackexchange
#   (excellent for real-world code snippets with prose explanations)
#
# For offline/manual download, create data/corpus/<lang>/ directories
# and put .txt files with source code in them. The corpus loader
# reads any .txt files recursively from these directories.
