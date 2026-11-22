import csv
import statistics
from collections import defaultdict

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = ROOT / "results" / "benchmark_results.csv"
OUTPUT_FILE = ROOT / "results" / "benchmark_comparison.tex"
CUDA_OUTPUT_FILE = ROOT / "results" / "cuda_timing_table.tex"

results = defaultdict(lambda: {
    "total": [],
    "count": [],
    "memory": [],
    "warm": [],
    "init": [],
    "kernel": []
})

with open(INPUT_FILE, newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        dataset = row["dataset"]
        implementation = row["implementation"]
        k = int(row["k"])
        threads = int(row["threads"])

        key = (dataset, implementation, k, threads)

        results[key]["total"].append(float(row["total_time_seconds"]))
        results[key]["count"].append(float(row["count_time_seconds"]))
        results[key]["memory"].append(int(row["max_memory_kb"]))

        if implementation == "cuda":
            results[key]["warm"].append(float(row["warm_count_time_seconds"]))
            results[key]["init"].append(float(row["cuda_initialization_time_seconds"]))
            results[key]["kernel"].append(float(row["cuda_kernel_time_seconds"]))

summary = []

for key in sorted(results):
    dataset, implementation, k, threads = key

    total = results[key]["total"]
    count = results[key]["count"]
    memory = results[key]["memory"]

    warm = results[key]["warm"]
    init = results[key]["init"]
    kernel = results[key]["kernel"]

    summary.append({
        "dataset": dataset,
        "implementation": implementation,
        "k": k,
        "threads": threads,
        "trials": len(total),

        "total_mean": statistics.mean(total) * 1000,
        "count_mean": statistics.mean(count) * 1000,
        "count_std": statistics.stdev(count) * 1000 if len(count) > 1 else 0,
        "peak_memory": max(memory) / 1024,

        "warm_mean": statistics.mean(warm) * 1000 if warm else None,
        "init_mean": statistics.mean(init) * 1000 if init else None,
        "kernel_mean": statistics.mean(kernel) * 1000 if kernel else None
    })

print(
    f"{'Dataset':<12} {'Impl':<12} {'k':<4} {'Threads':<8} "
    f"{'Count (ms)':<14} {'Std Dev (ms)':<14} {'Peak RAM (MiB)':<16}"
)

for row in summary:
    print(
        f"{row['dataset']:<12} "
        f"{row['implementation']:<12} "
        f"{row['k']:<4} "
        f"{row['threads']:<8} "
        f"{row['count_mean']:<14.3f} "
        f"{row['count_std']:<14.3f} "
        f"{row['peak_memory']:<16.2f}"
    )

# Look up a summary row by dataset, implementation, k, and threads
summary_lookup = {
    (row["dataset"], row["implementation"], row["k"], row["threads"]): row
    for row in summary
}

# Generate performance comparison LaTeX table
datasets = sorted({row["dataset"] for row in summary})
ks = sorted({row["k"] for row in summary})

with open(OUTPUT_FILE, "w") as file:
    file.write("\\begin{table}[ht]\n")
    file.write("    \\centering\n")
    file.write("    \\caption{Mean k-mer counting time across ten trials (ms)}\n")
    file.write("    \\begin{tabular}{lrrrrr}\n")
    file.write("        \\toprule\n")
    file.write("        Dataset & $k$ & Sequential & OpenMP & CUDA Cold & CUDA Warm \\\\\n")
    file.write("        \\midrule\n")

    for dataset in datasets:
        for k in ks:
            seq = summary_lookup[(dataset, "sequential", k, 1)]
            cuda = summary_lookup[(dataset, "cuda", k, 0)]

            # Find the OpenMP configuration with the lowest mean count time
            omp_rows = [
                row for row in summary
                if row["dataset"] == dataset
                and row["implementation"] == "openmp"
                and row["k"] == k
            ]

            best_omp = min(omp_rows, key=lambda row: row["count_mean"])

            file.write(
                f"        {dataset} & {k} & "
                f"{seq['count_mean']:.2f} & "
                f"{best_omp['count_mean']:.2f} "
                f"({best_omp['threads']} threads) & "
                f"{cuda['count_mean']:.2f} & "
                f"{cuda['warm_mean']:.2f} \\\\\n"
            )

    file.write("        \\bottomrule\n")
    file.write("    \\end{tabular}\n")
    file.write("    \\label{tab:benchmark_comparison}\n")
    file.write("\\end{table}\n")

print(f"\nLaTeX table saved to {OUTPUT_FILE}")

# Generate CUDA timing breakdown table
with open(CUDA_OUTPUT_FILE, "w") as file:
    file.write("\\begin{table}[ht]\n")
    file.write("    \\centering\n")
    file.write("    \\caption{Mean CUDA execution times across ten trials (ms)}\n")
    file.write("    \\begin{tabular}{lrrrrr}\n")
    file.write("        \\toprule\n")
    file.write("        Dataset & $k$ & Initialization & Kernel & Warm Count & Cold Count \\\\\n")
    file.write("        \\midrule\n")

    for dataset in datasets:
        for k in ks:
            cuda = summary_lookup[(dataset, "cuda", k, 0)]

            file.write(
                f"        {dataset} & {k} & "
                f"{cuda['init_mean']:.2f} & "
                f"{cuda['kernel_mean']:.2f} & "
                f"{cuda['warm_mean']:.2f} & "
                f"{cuda['count_mean']:.2f} \\\\\n"
            )

    file.write("        \\bottomrule\n")
    file.write("    \\end{tabular}\n")
    file.write("    \\label{tab:cuda_timing}\n")
    file.write("\\end{table}\n")

print(f"LaTeX table saved to {CUDA_OUTPUT_FILE}")