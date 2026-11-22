#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="$(cd "$SCRIPT_DIR/.." && pwd)"
SEQ_EXEC="$PROJECT/sequential/out"
OMP_EXEC="$PROJECT/openMP/out"
CUDA_EXEC="$PROJECT/cuda/out"
RESULTS="$PROJECT/results/benchmark_results.csv"

DATASETS=(
    "$PROJECT/datasets/ecoli.fasta"
    "$PROJECT/datasets/chr18.fa"
)

K_VALUES=(3 6 9 12)
THREAD_COUNTS=(1 2 4 8 16)
RUNS=10

mkdir -p "$(dirname "$RESULTS")"
for file in "${DATASETS[@]}" "$SEQ_EXEC" "$OMP_EXEC" "$CUDA_EXEC"; do
    if [[ ! -f "$file" ]]; then
        echo "Missing file: $file" >&2
        exit 1
    fi
done

output_file=$(mktemp)
memory_file=$(mktemp)
trap 'rm -f "$output_file" "$memory_file"' EXIT

printf 'dataset,implementation,k,threads,run,total_time_seconds,count_time_seconds,allocation_time_seconds,parallel_counting_time_seconds,merge_time_seconds,max_memory_kb,cuda_initialization_time_seconds,cuda_allocation_time_seconds,cuda_kernel_time_seconds,warm_count_time_seconds\n' > "$RESULTS"

run_one() {
    local implementation="$1" k="$2" threads="$3" run="$4"
    local fasta="$5"
    local total count allocation parallel_count merge memory
    local cuda_init cuda_alloc cuda_kernel cuda_warm
    local -a cmd

    if [[ "$implementation" == "sequential" ]]; then
        cmd=("$SEQ_EXEC" "$k" "$fasta")

    elif [[ "$implementation" == "openmp" ]]; then
        cmd=("$OMP_EXEC" "$k" "$fasta" "$threads")

    elif [[ "$implementation" == "cuda" ]]; then
        cmd=("$CUDA_EXEC" "$k" "$fasta")

    else
        echo "Unknown implementation: $implementation" >&2
        exit 1
    fi

    /usr/bin/time -f '%M' -o "$memory_file" "${cmd[@]}" > "$output_file"

    total=$(awk '/^Total processing time:/ {print $4}' "$output_file")
    count=$(awk '/^Count time:/ {print $3}' "$output_file")
    allocation=$(awk '/^Allocation time:/ {print $3}' "$output_file")
    parallel_count=$(awk '/^Parallel counting time:/ {print $4}' "$output_file")
    merge=$(awk '/^Merge time:/ {print $3}' "$output_file")
    memory=$(<"$memory_file")

    cuda_init=$(awk '/^CUDA initialization time:/ {print $4}' "$output_file")
    cuda_alloc=$(awk '/^CUDA allocation time:/ {print $4}' "$output_file")
    cuda_kernel=$(awk '/^CUDA kernel time:/ {print $4}' "$output_file")
    cuda_warm=$(awk '/^Warm count time:/ {print $4}' "$output_file")

    if [[ -z "$total" || -z "$count" || -z "$memory" ]]; then
        echo "Missing benchmark output for $implementation k=$k threads=$threads run=$run" >&2
        cat "$output_file" >&2
        exit 1
    fi
    if [[ "$implementation" == "openmp" && ( -z "$allocation" || -z "$parallel_count" || -z "$merge" ) ]]; then
        echo "Missing OpenMP phase timers. Rebuild openMP/out with the timing prints." >&2
        cat "$output_file" >&2
        exit 1
    fi

    if [[ "$implementation" == "cuda" && ( -z "$cuda_init" || -z "$cuda_alloc" || -z "$cuda_kernel" || -z "$cuda_warm" ) ]]; then
        echo "Missing CUDA timing measurements" >&2
        cat "$output_file" >&2
        exit 1
    fi

    dataset=$(basename "$fasta")

    printf '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
        "$dataset" "$implementation" "$k" "$threads" "$run" "$total" "$count" \
        "$allocation" "$parallel_count" "$merge" "$memory" \
        "$cuda_init" "$cuda_alloc" "$cuda_kernel" "$cuda_warm" >> "$RESULTS"

    printf '%-10s k=%-2s threads=%-2s run=%-2s count=%s s\n' \
        "$implementation" "$k" "$threads" "$run" "$count"
}
for fasta in "${DATASETS[@]}";do
    for k in "${K_VALUES[@]}"; do
        for ((run=1; run<=RUNS; run++)); do
            run_one sequential "$k" 1 "$run" "$fasta"
        done
        for threads in "${THREAD_COUNTS[@]}"; do
            for ((run=1; run<=RUNS; run++)); do
                run_one openmp "$k" "$threads" "$run" "$fasta"
            done
        done
        for ((run=1; run<=RUNS; run++)); do
            run_one cuda "$k" 0 "$run" "$fasta"
        done
    done
done
echo "Results saved to $RESULTS"
