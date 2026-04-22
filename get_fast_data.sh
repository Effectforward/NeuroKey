#!/bin/bash
set -e




mkdir -p data/corpus/{python,rust,c,cpp,javascript,go,java,typescript,ruby,shell,english}

# Function to clone and extract
fetch_repo() {
    lang=$1
    ext=$2
    repo=$3
    echo "Fetching $lang from $repo..."
    dir="/tmp/repo_$lang"
    rm -rf "$dir"
    git clone --depth=1 "$repo" "$dir" 2>/dev/null
    find "$dir" -name "*.$ext" -exec cat {} + > "data/corpus/$lang/data.txt" 2>/dev/null || true
    rm -rf "$dir"
    
    # Print lines downloaded
    lines=$(wc -l < "data/corpus/$lang/data.txt")
    echo "  -> Saved $lines lines of $lang code."
}

fetch_repo python py https://github.com/django/django.git
fetch_repo rust rs https://github.com/rust-lang/cargo.git
fetch_repo c c https://github.com/redis/redis.git
fetch_repo cpp cpp https://github.com/bitcoin/bitcoin.git
fetch_repo javascript js https://github.com/facebook/react.git
fetch_repo go go https://github.com/moby/moby.git
fetch_repo java java https://github.com/elastic/elasticsearch.git
fetch_repo typescript ts https://github.com/microsoft/vscode.git
fetch_repo ruby rb https://github.com/discourse/discourse.git
fetch_repo shell sh https://github.com/ohmyzsh/ohmyzsh.git

echo "Fetching English prose..."
curl -sL https://www.gutenberg.org/cache/epub/100/pg100.txt > data/corpus/english/shakespeare.txt
lines=$(wc -l < data/corpus/english/shakespeare.txt)
echo "  -> Saved $lines lines of English prose."

echo "Fast data fetch complete!"
