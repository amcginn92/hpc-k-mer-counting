#include "KmerCounter.h"
#include <fstream>
#include <omp.h>
#include <algorithm>
#include <cstdint>
#include <stdexcept>
#include <vector>
#include <chrono>
#include <iostream>

KmerCounter::KmerCounter(uint64_t k) 
    : k_(k), 
      counts_(1ULL << (2 * k), 0)
{
}

void KmerCounter::countParallel(int numThreads){

    if(numThreads <= 0){
        throw std::invalid_argument("Invalid thread count");
    }

    const size_t arraySize = counts_.size();
    const size_t blockSize = 65536;

    struct Block{
        size_t sequenceIndex;
        size_t begin;
        size_t end;
    };

    std::vector<Block> blocks;

    for (size_t s=0; s < sequences_.size(); s++){
        const auto& sequence = sequences_[s];

        // Only count sequences_ that are long enough to be a kmer for our selected kmer length
        if(sequence.size() < k_){
            continue;
        }

        const size_t numWindows = sequence.size() - k_ + 1;

        for (size_t start = 0; start < numWindows; start += blockSize) {
            blocks.push_back({
                s,
                start,
                std::min(start + blockSize, numWindows)
            });
        }
    }

    // Each thread gets 4^k counter
    std::vector<std::vector<uint64_t>> localCounts(
        numThreads,
        std::vector<uint64_t>(arraySize, 0)
    );

    // Mask used for sliding window to remove entries no longer needed
    const uint64_t mask = (1ULL << (2 * k_)) - 1;

    #pragma omp parallel num_threads(numThreads)
    {
        const int threadId = omp_get_thread_num();
        // Retrieve this threads local frequency array
        auto& local = localCounts[threadId];

        #pragma omp for schedule(static)
        for (size_t b = 0; b < blocks.size(); ++b) {
            const Block& block = blocks[b];
            const auto& sequence = sequences_[block.sequenceIndex];

            uint64_t encoded = 0;
            size_t validBases = 0;

            // Read k-1 extra bases beyond the last starting
            // position, without counting duplicate windows.
            const size_t readEnd = block.end + k_ - 1;

            for (size_t i = block.begin; i < readEnd; ++i) {
                uint64_t base;

                switch (sequence[i]) {
                    case 'A': case 'a': base = 0; break;
                    case 'C': case 'c': base = 1; break;
                    case 'G': case 'g': base = 2; break;
                    case 'T': case 't': base = 3; break;

                    default:
                        encoded = 0;
                        validBases = 0;
                        continue;
                }

                // Encoded kmer, removing entries no longer needed with mask
                encoded = ((encoded << 2) | base) & mask;
                ++validBases;

                // Only count once length of chosen k
                if (validBases >= k_) {
                    ++local[encoded];
                }
            }
        }
    }

    // Merge counters into the final array
    #pragma omp parallel for num_threads(numThreads) schedule(static)
    for (size_t i = 0; i < arraySize; ++i) {
        uint64_t total = 0;

        // For every threads counts increment the total
        for (int t = 0; t < numThreads; ++t) {
            total += localCounts[t][i];
        }

        counts_[i] = total;
    }
}

void KmerCounter::loadFasta(const std::string& filename)
{
    std::ifstream file(filename);

    if (!file.is_open()) {
        throw std::runtime_error("Cannot open FASTA file: " + filename);
    }

    std::vector<std::string> sequences;
    std::string line;
    std::string sequence;
    bool inRecord = false;

    while (std::getline(file, line)) {

        // If this is the beginning of a sample (header)
        if (!line.empty() && line[0] == '>') {
            // This is the start of a new sample, save the prior sequence
            if (inRecord && !sequence.empty()) {
                sequences.push_back(std::move(sequence));
                sequence.clear();
            }

            // Mark that we've begun recording
            inRecord = true;
        }
        else if (inRecord) {
            //Continue Reading the current sequence
            sequence += line;
        }
    }

    // The last sequence never encounters another header
    if (!sequence.empty()) {
        sequences.push_back(std::move(sequence));
    }

    if (file.bad()) {
        throw std::runtime_error("Error reading FASTA file");
    }

    sequences_ = std::move(sequences);
}


uint64_t KmerCounter::getCount(uint64_t encoded) const
{
    return counts_.at(encoded);
}

void KmerCounter::countSequences()
{
    // For every FASTA header we've encountered, count the sequence
    for (const auto& sequence : sequences_) {
        countSequence(sequence);
    }
}

//  Counts the given sequence, if valid
void KmerCounter::countSequence(const std::string& sequence)
{
    uint64_t encoded = 0;
    uint64_t validBases = 0;

    // We use bitwise & to discard additional values 
    uint64_t mask = (1ULL << (2 * k_)) - 1;

    for (char base : sequence) {
        uint8_t value = encodeBase(base);

        if (value == 4) {
            encoded = 0;
            validBases = 0;
            continue;
        }

        // Shift the current bits left and add the new value, discarding additional values.
        encoded = ((encoded << 2) | value) & mask;

        validBases++;

        // Only count complete sequences
        if (validBases >= k_) {
            counts_[encoded]++;
        }
    }
}

//   Convert each nucleotide into a 2-bit int
//   0 - A, 1 - C, 2 - G, 3 - T, 4 - Unk (N)
//   **Currently only uses the lowest 2 bits - room for optimization?**
uint8_t KmerCounter::encodeBase(char base){

    switch(base){
        case 'A':
        case 'a':
            return 0;
        case 'C':
        case 'c':
            return 1;
        case 'G':
        case 'g':
            return 2;
        case 'T':
        case 't':
            return 3;
        default:
            return 4;
    }
}

void KmerCounter::writeCounts(std::ostream& output) const
{
    output << "encoded,count\n";

    for (uint64_t i = 0; i < counts_.size(); i++) {
        if (counts_[i] != 0) {
            output << i << "," << counts_[i] << "\n";
        }
    }
}

