python3 - <<'PY'
from collections import Counter

counts = Counter()
sequence = ""

def count_record(seq):
    for i in range(len(seq) - 2):
        mer = seq[i:i+3].upper()
        if all(c in "ACGT" for c in mer):
            counts[mer] += 1

with open("datasets/ecoli.fasta") as f:
    for line in f:
        line = line.strip()
        if line.startswith(">"):
            count_record(sequence)
            sequence = ""
        else:
            sequence += line

count_record(sequence)

for mer in ["ACG", "CGT", "GTA", "TAC"]:
    print(f"{mer}: {counts[mer]}")
PY