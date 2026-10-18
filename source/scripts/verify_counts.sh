#!/bin/bash

set -euo pipefail

PROJECT="/home/amcgin/kmerCounting/source"
FASTA="$PROJECT/datasets/ecoli.fasta"
EXEC="$PROJECT/out"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$SCRIPT_DIR/verification"

for k in 3 6 9 12; do
    echo "================================="
    echo "Verifying k=$k"

    OUTPUT="$SCRIPT_DIR/verification/counts_k${k}.csv"

    "$EXEC" "$k" "$FASTA" "$OUTPUT"

    python3 "$SCRIPT_DIR/kmerCountVerify.py" \
        "$k" "$FASTA" "$OUTPUT"

    echo
done

echo "All verification tests passed."
