#!/usr/bin/env python3
"""Plot combined sequential / OpenMP benchmark CSV."""
import csv
import statistics as stats
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / 'results' / 'benchmark_results.csv'
FIGURES = ROOT / 'results' / 'figures'
FIGURES.mkdir(parents=True, exist_ok=True)

# key = (implementation, k, threads)
records = defaultdict(list)
with CSV.open(newline='') as stream:
    for row in csv.DictReader(stream):
        key = (row['implementation'], int(row['k']), int(row['threads']))
        records[key].append(row)

if not records:
    raise SystemExit(f'No benchmark records in {CSV}')

ks = sorted({k for _, k, _ in records})
threads = sorted({t for impl, _, t in records if impl == 'openmp'})

def values(impl, k, t, column, multiplier=1):
    return [float(row[column]) * multiplier for row in records.get((impl, k, t), []) if row[column].strip()]

def mean(impl, k, t, column, multiplier=1):
    v = values(impl, k, t, column, multiplier)
    return stats.mean(v) if v else float('nan')

def save(name):
    plt.tight_layout()
    path = FIGURES / name
    plt.savefig(path, dpi=300, bbox_inches='tight')
    print(f'Saved {path}')

# 1. Overall counting-function time (allocation + merge included)
plt.figure(figsize=(9, 5))
plt.plot(ks, [mean('sequential', k, 1, 'count_time_seconds', 1000) for k in ks], 'o-', label='Sequential')
for t in threads:
    plt.plot(ks, [mean('openmp', k, t, 'count_time_seconds', 1000) for k in ks], 'o-', label=f'OpenMP {t} threads')
plt.xlabel('k-mer length (k)')
plt.ylabel('Counting-function time (ms)')
plt.title('Sequential vs OpenMP: End-to-end counting-function time')
plt.xticks(ks)
plt.grid(alpha=0.3)
plt.legend()
save('count_time_comparison.png')

# 2. Speedup = mean sequential count time / mean OpenMP count time
plt.figure(figsize=(9, 5))
for k in ks:
    baseline = mean('sequential', k, 1, 'count_time_seconds')
    plt.plot(threads, [baseline / mean('openmp', k, t, 'count_time_seconds') for t in threads], 'o-', label=f'k = {k}')
plt.axhline(1.0, linestyle='--', linewidth=1, label='No speedup')
plt.xlabel('OpenMP threads')
plt.ylabel('Speedup (sequential / OpenMP)')
plt.title('End-to-end counting speedup')
plt.xticks(threads)
plt.grid(alpha=0.3)
plt.legend()
save('speedup.png')

# 3. Peak resident memory
plt.figure(figsize=(9, 5))
for k in ks:
    plt.plot(threads, [mean('openmp', k, t, 'max_memory_kb') / 1024 for t in threads], 'o-', label=f'OpenMP k = {k}')
plt.xlabel('OpenMP threads')
plt.ylabel('Mean peak resident memory (MiB)')
plt.title('OpenMP peak memory usage')
plt.xticks(threads)
plt.grid(alpha=0.3)
plt.legend()
save('memory.png')

# 4. Phase breakdown for each k (one plot per k)
for k in ks:
    columns = [('allocation_time_seconds', 'Allocation'), ('parallel_counting_time_seconds', 'Counting'), ('merge_time_seconds', 'Merge')]
    bottoms = [0.0] * len(threads)
    plt.figure(figsize=(9, 5))
    for col, label in columns:
        heights = [mean('openmp', k, t, col, 1000) for t in threads]
        plt.bar([str(t) for t in threads], heights, bottom=bottoms, label=label)
        bottoms = [x + y for x, y in zip(bottoms, heights)]
    plt.xlabel('OpenMP threads')
    plt.ylabel('Time (ms)')
    plt.title(f'OpenMP phase breakdown: k = {k}')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    save(f'phase_breakdown_k{k}.png')

# Preserve an interactive window when an interactive Matplotlib backend is active.
plt.show()
