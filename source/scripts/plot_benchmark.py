
import csv
import statistics
import matplotlib.pyplot as plt
from collections import defaultdict

INPUT_FILE = "benchmark_results.csv"
OUTPUT_FILE = "/home/amcgin/kmerCounting/source/etc/benchmark_plot.png"

results = defaultdict(lambda: {"total": [], "count": []})

with open(INPUT_FILE, newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        k = int(row["k"])

        results[k]["total"].append(float(row["total_time_seconds"]) * 1000)
        results[k]["count"].append(float(row["count_time_seconds"]) * 1000)

k_values = sorted(results)

total_means = []
count_means = []
total_stds = []
count_stds = []

for k in k_values:
    total = results[k]["total"]
    count = results[k]["count"]

    total_means.append(statistics.mean(total))
    count_means.append(statistics.mean(count))

    total_stds.append(statistics.stdev(total) if len(total) > 1 else 0)
    count_stds.append(statistics.stdev(count) if len(count) > 1 else 0)

# Plot benchmark results
plt.figure(figsize=(9, 5))

plt.errorbar(
    k_values, total_means,
    yerr=total_stds,
    marker="o",
    capsize=4,
    label="Total Processing Time"
)

plt.errorbar(
    k_values, count_means,
    yerr=count_stds,
    marker="s",
    capsize=4,
    label="K-mer Counting Time"
)

plt.title("Sequential K-mer Counting Performance")
plt.xlabel("K-mer Length (k)")
plt.ylabel("Execution Time (ms)")

plt.xticks(k_values)
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
plt.show()

print(f"Graph saved to {OUTPUT_FILE}")
