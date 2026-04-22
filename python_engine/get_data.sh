#!/bin/bash
set -e

echo "============================================================"
echo "  OptiKey — Fast Corpus Downloader"
echo "  Target: Real-world source code across 10 languages"
echo "============================================================"
echo ""

echo "Cleaning up old data..."
rm -rf data/corpus/*
rm -f data/ngrams_cache.pkl
rm -rf checkpoints/*
rm -rf results/*

mkdir -p data/corpus/{python,rust,c,cpp,javascript,go,java,typescript,ruby,shell,english}

# Function to clone and extract
fetch_repo() {
    lang=$1
    ext=$2
    repo=$3
    target_file="data/corpus/$lang/data.txt"

    if [ -s "$target_file" ]; then
        lines=$(wc -l < "$target_file")
        echo "  -> Data for $lang already exists ($lines lines). Skipping download."
        echo ""
        return
    fi

    echo "Fetching $lang from $repo..."
    dir="/tmp/repo_$lang"
    rm -rf "$dir"
    
    # Clone shallow copy, suppress output
    git clone --depth=1 "$repo" "$dir" 2>/dev/null || echo "  [!] Clone failed for $repo"
    
    # Find files of specific extension and concatenate them into our corpus
    find "$dir" -name "*.$ext" -exec sh -c 'cat "$@" > "'$target_file'"' _ {} + 2>/dev/null || true
    
    rm -rf "$dir"
    
    if [ -s "$target_file" ]; then
        lines=$(wc -l < "$target_file")
        echo "  -> Saved $lines lines of $lang code."
    else
        echo "  -> No $lang code found or saved."
    fi
    echo ""
}

# General Programming Languages
fetch_repo python py https://github.com/django/django.git
fetch_repo rust rs https://github.com/rust-lang/cargo.git
fetch_repo c c https://github.com/redis/redis.git
fetch_repo cpp cpp https://github.com/bitcoin/bitcoin.git
fetch_repo javascript js https://github.com/facebook/react.git
fetch_repo go go https://github.com/moby/moby.git
fetch_repo java java https://github.com/spring-projects/spring-petclinic.git
fetch_repo typescript ts https://github.com/vuejs/vue.git
fetch_repo ruby rb https://github.com/heartcombo/devise.git
fetch_repo shell sh https://github.com/koalaman/shellcheck.git

# English prose via Markdown files
echo "Fetching English prose (Markdown)..."
git clone --depth=1 https://github.com/freeCodeCamp/freeCodeCamp.git /tmp/repo_markdown 2>/dev/null
find /tmp/repo_markdown -name "*.md" -exec sh -c 'cat "$@" > "data/corpus/english/markdown.txt"' _ {} + 2>/dev/null || true
rm -rf /tmp/repo_markdown
if [ -f "data/corpus/english/markdown.txt" ]; then
    lines=$(wc -l < "data/corpus/english/markdown.txt")
    echo "  -> Saved $lines lines of Markdown."
fi
echo ""

echo "============================================================"
echo "  Download complete! Rebuilding n-gram cache..."
echo "============================================================"
python3 main.py rebuild-corpus

echo "Corpus is ready! You can now start the NeuroKey Dashboard:"
echo "  npm run tauri dev"
