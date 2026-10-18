#!/usr/bin/env python3

import csv
import sys
from collections import Counter

BASES = {"A": 0, "C": 1, "G": 2, "T": 3}


def encode_kmer(kmer):
    encoded = 0

    for base in kmer:
        encoded = (encoded << 2) | BASES[base]

    return encoded


def count_record(sequence, k, counts):
    sequence = sequence.upper()

    for i in range(len(sequence) - k + 1):
        kmer = sequence[i:i + k]

        if all(base in BASES for base in kmer):
            counts[kmer] += 1


def count_fasta(filename, k):
    counts = Counter()
    sequence = ""
    in_record = False

    with open(filename) as file:
        for line in file:
            line = line.strip()

            if line.startswith(">"):
                if in_record:
                    count_record(sequence, k, counts)

                sequence = ""
                in_record = True

            elif in_record:
                sequence += line

        if in_record:
            count_record(sequence, k, counts)

    return {
        encode_kmer(kmer): frequency
        for kmer, frequency in counts.items()
    }


def load_cpp_counts(filename, k):
    counts = {}

    with open(filename, newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != ["encoded", "count"]:
            raise ValueError("Unexpected C++ CSV header")

        for row in reader:
            encoded = int(row["encoded"])
            frequency = int(row["count"])

            if not 0 <= encoded < (1 << (2 * k)):
                raise ValueError(f"Invalid encoded index: {encoded}")

            if frequency <= 0:
                raise ValueError(f"Invalid count at index {encoded}")

            if encoded in counts:
                raise ValueError(f"Duplicate encoded index: {encoded}")

            counts[encoded] = frequency

    return counts


def verify(k, fasta, cpp_file):
    print(f"Verifying k={k}")

    python_counts = count_fasta(fasta, k)
    cpp_counts = load_cpp_counts(cpp_file, k)

    mismatches = []

    for encoded in python_counts.keys() | cpp_counts.keys():
        expected = python_counts.get(encoded, 0)
        actual = cpp_counts.get(encoded, 0)

        if expected != actual:
            mismatches.append((encoded, expected, actual))

    print(f"Python total k-mers: {sum(python_counts.values())}")
    print(f"C++ total k-mers:    {sum(cpp_counts.values())}")
    print(f"Unique k-mers:       {len(python_counts)}")
    print(f"Mismatches:          {len(mismatches)}")

    if not mismatches:
        print("PASS: All k-mer frequencies match.")
        return True

    for encoded, expected, actual in mismatches[:10]:
        print(f"Mismatch at {encoded}: Python={expected}, C++={actual}")

    print("FAIL: Frequency distributions differ.")
    return False


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 kmerCountVerify.py <k> <fasta> <cpp-csv>")
        sys.exit(1)

    k = int(sys.argv[1])
    fasta = sys.argv[2]
    cpp_file = sys.argv[3]

    if k < 1:
        sys.exit("k must be positive")

    sys.exit(0 if verify(k, fasta, cpp_file) else 1)
