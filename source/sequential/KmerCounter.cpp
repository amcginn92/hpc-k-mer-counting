#include "KmerCounter.h"
#include <fstream>


KmerCounter::KmerCounter(uint64_t k) 
    : k_(k), 
      counts_(1ULL << (2 * k), 0)
{
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

        if (!line.empty() && line[0] == '>') {
            if (inRecord && !sequence.empty()) {
                sequences.push_back(std::move(sequence));
                sequence.clear();
            }

            inRecord = true;
        }
        else if (inRecord) {
            sequence += line;
        }
    }

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

