#!/bin/bash
#
find . -type f -name "sanskrit.txt" | while read -r sk_file; do
    dir=$(dirname "$sk_file")
    for aligned in "$dir"/*.txt; do
        if [ "$aligned" != "$sk_file" ] && [ -f "$aligned" ]; then
            echo "Processing: $aligned with $sk_file"
            python patch_ll.py "$aligned" "$sk_file"
        fi
    done
done
