#!/bin/bash

FASTA="/home/amcgin/kmerCounting/source/datasets/ecoli.fasta"
EXEC="/home/amcgin/kmerCounting/source/out"
RESULTS="benchmark_results.csv"

echo "k,run,total_time_seconds,count_time_seconds,max_memory_kb" > "$RESULTS"

for k in 3 6 9 12; do
    echo "Benchmarking k=$k"

    for run in {1..10}; do

        /usr/bin/time -f "%M" -o /tmp/kmer_memory.txt \
            "$EXEC" "$k" "$FASTA" > /tmp/kmer_output.txt

        total_time=$(awk '/Total processing time:/ {print $4}' /tmp/kmer_output.txt)
        count_time=$(awk '/Count time:/ {print $3}' /tmp/kmer_output.txt)
        memory=$(cat /tmp/kmer_memory.txt)

        echo "$k,$run,$total_time,$count_time,$memory" >> "$RESULTS"

        echo "Run $run: Total=$total_time s, Count=$count_time s, Memory=$memory KiB"

    done

    echo
done

echo "Results saved to $RESULTS"