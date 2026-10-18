import csv
import statistics
from collections import defaultdict

INPUT_FILE = "benchmark_results.csv"
OUTPUT_FILE = "/home/amcgin/kmerCounting/source/etc/benchmark_table.tex"

results = defaultdict(lambda: {"total": [], "count": [], "memory": []})

with open(INPUT_FILE, newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        k = int(row["k"])

        results[k]["total"].append(float(row["total_time_seconds"]))
        results[k]["count"].append(float(row["count_time_seconds"]))
        results[k]["memory"].append(int(row["max_memory_kb"]))

summary = []

for k in sorted(results):
    total = results[k]["total"]
    count = results[k]["count"]
    memory = results[k]["memory"]

    summary.append({
        "k": k,
        "trials": len(total),
        "total_mean": statistics.mean(total) * 1000,
        "count_mean": statistics.mean(count) * 1000,
        "count_std": statistics.stdev(count) * 1000 if len(count) > 1 else 0,
        "peak_memory": max(memory) / 1024
    })

# Print results to terminal
print(f"{'k':<5} {'Total (ms)':<15} {'Count (ms)':<15} "
      f"{'Std Dev (ms)':<15} {'Peak RAM (MiB)':<15}")

for row in summary:
    print(f"{row['k']:<5} {row['total_mean']:<15.3f} "
          f"{row['count_mean']:<15.3f} {row['count_std']:<15.3f} "
          f"{row['peak_memory']:<15.2f}")

# Generate LaTeX table
with open(OUTPUT_FILE, "w") as file:
    file.write("\\begin{table}[ht]\n")
    file.write("    \\centering\n")
    file.write("    \\caption{Sequential k-mer counting benchmark results}\n")
    file.write("    \\begin{tabular}{ccccc}\n")
    file.write("        \\toprule\n")
    file.write("        $k$ & Total (ms) & Count (ms) & Std. Dev. (ms) & Peak RAM (MiB) \\\\\n")
    file.write("        \\midrule\n")

    for row in summary:
        file.write(
            f"        {row['k']} & {row['total_mean']:.3f} & "
            f"{row['count_mean']:.3f} & {row['count_std']:.3f} & "
            f"{row['peak_memory']:.2f} \\\\\n"
        )

    file.write("        \\bottomrule\n")
    file.write("    \\end{tabular}\n")
    file.write("    \\label{tab:sequential_results}\n")
    file.write("\\end{table}\n")

print(f"\nLaTeX table saved to {OUTPUT_FILE}")
