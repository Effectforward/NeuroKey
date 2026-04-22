#!/bin/bash

# Function to clone and extract
fetch_repo() {
    lang=$1
    ext=$2
    repo=$3
    echo "Fetching $lang from $repo..."
    dir="/tmp/repo_$lang"
    rm -rf "$dir"
    git clone --depth=1 "$repo" "$dir" 2>/dev/null || echo "Clone failed for $repo"
    find "$dir" -name "*.$ext" -exec sh -c 'cat "$@" > "data/corpus/'$lang'/data.txt"' _ {} + 2>/dev/null || true
    rm -rf "$dir"
    if [ -f "data/corpus/$lang/data.txt" ]; then
        lines=$(wc -l < "data/corpus/$lang/data.txt")
        echo "  -> Saved $lines lines of $lang code."
    fi
}

fetch_repo java java https://github.com/spring-projects/spring-petclinic.git
fetch_repo typescript ts https://github.com/vuejs/vue.git
fetch_repo ruby rb https://github.com/heartcombo/devise.git
fetch_repo shell sh https://github.com/koalaman/shellcheck.git

echo "Fetching English prose (Markdown)..."
git clone --depth=1 https://github.com/freeCodeCamp/freeCodeCamp.git /tmp/repo_markdown 2>/dev/null
find /tmp/repo_markdown -name "*.md" -exec sh -c 'cat "$@" > "data/corpus/english/markdown.txt"' _ {} + 2>/dev/null || true
rm -rf /tmp/repo_markdown
if [ -f "data/corpus/english/markdown.txt" ]; then
    lines=$(wc -l < "data/corpus/english/markdown.txt")
    echo "  -> Saved $lines lines of Markdown."
fi

echo "Rebuilding n-gram cache..."
python3 main.py rebuild-corpus
