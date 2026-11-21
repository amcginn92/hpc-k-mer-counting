#!/bin/bash

set -euo pipefail

PROJECT="/home/amcgin/kmerCounting/source"
FASTA="$PROJECT/datasets/ecoli.fasta"
EXEC="$PROJECT/openMP/out"
PYTHON_VERIFY="$PROJECT/scripts/countVerify.py"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/verification"

mkdir -p "$OUTPUT_DIR"

REPEATS=3

for k in 3 6 9 12; do
    for threads in 1 2 4 8 16; do
        for ((run=1; run<=REPEATS; run++)); do

            echo "======================================"
            echo "Verifying k=$k, threads=$threads, run=$run"

            OUTPUT="$OUTPUT_DIR/counts_k${k}_t${threads}.csv"

            "$EXEC" "$k" "$FASTA" "$threads" "$OUTPUT"

            python3 "$PYTHON_VERIFY" "$k" "$FASTA" "$OUTPUT"

            # Remove successful verification output
            rm -f "$OUTPUT"

            echo
        done
    done
done

echo "All 60 OpenMP verification tests passed."