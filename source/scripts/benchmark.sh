#!/bin/bash

FASTA="/home/amcgin/kmerCounting/source/datasets/ecoli.fasta"

for k in 3 6 8 10; do
    echo "Benchmarking k=$k"

    for run in {1..10}; do
        /home/amcgin/kmerCounting/source/out "$k" "$FASTA" | grep "Processing time"
    done

    echo
done