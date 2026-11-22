import csv
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent

CSV = ROOT / "results/midterm/benchmark_results.csv"
OUTPUT = ROOT / "results/midterm/figures/sequential_performance.png"

# Collect sequential E. coli results by k
results = defaultdict(lambda: {"total": [], "count": []})

with CSV.open(newline="") as file:
    for row in csv.DictReader(file):
        if row["dataset"] != "ecoli.fasta":
            continue

        if row["implementation"] != "sequential":
            continue

        k = int(row["k"])

        results[k]["total"].append(
            float(row["total_time_seconds"]) * 1000
        )

        results[k]["count"].append(
            float(row["count_time_seconds"]) * 1000
        )

# Calculate averages and standard deviations
ks = sorted(results)

total_mean = [statistics.mean(results[k]["total"]) for k in ks]
count_mean = [statistics.mean(results[k]["count"]) for k in ks]

total_std = [statistics.stdev(results[k]["total"]) for k in ks]
count_std = [statistics.stdev(results[k]["count"]) for k in ks]

# Generate the figure
plt.figure(figsize=(9, 5))

plt.errorbar(
    ks, total_mean, yerr=total_std,
    fmt="o-", capsize=4, label="Total processing time"
)

plt.errorbar(
    ks, count_mean, yerr=count_std,
    fmt="s-", capsize=4, label="K-mer counting time"
)

plt.xlabel("K-mer length (k)")
plt.ylabel("Execution time (ms)")
plt.title("Sequential K-mer Counting Performance")
plt.xticks(ks)
plt.grid(alpha=0.3)
plt.legend()

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
plt.tight_layout()
plt.savefig(OUTPUT, dpi=300)
plt.close()

print(f"Saved {OUTPUT}")