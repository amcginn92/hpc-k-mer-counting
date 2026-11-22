#include "KmerCounter.h"
#include <fstream>
#include <cstdint>
#include <cuda_runtime.h>
#include <stdexcept>
#include <iostream>
#include <chrono>

__global__ void countKmersKernel(    const char* sequence, size_t sequenceLength, uint64_t k, unsigned long long* counts);

KmerCounter::KmerCounter(uint64_t k) 
    : k_(k), 
      counts_(1ULL << (2 * k), 0)
{
}



void KmerCounter::countCuda()
{
    char* d_sequence = nullptr;
    unsigned long long* d_counts = nullptr;

    const size_t arraySize = counts_.size();
    const size_t countsBytes =
        arraySize * sizeof(unsigned long long);

    // Check CUDA operations for errors
    auto checkCuda = [](cudaError_t error) {
        if (error != cudaSuccess) {
            throw std::runtime_error(cudaGetErrorString(error));
        }
    };

    try {

        auto allocStart = std::chrono::steady_clock::now();

        // Allocate GPU frequency array
        checkCuda(cudaMalloc(
            reinterpret_cast<void**>(&d_counts),
            countsBytes
        ));

        // Initialize all counters to zero
        checkCuda(cudaMemset(d_counts, 0, countsBytes));

        // Ensure GPU finishes initializing before recording allocation time end
        checkCuda(cudaDeviceSynchronize());
        auto allocEnd = std::chrono::steady_clock::now();

        cudaEvent_t kernelStart, kernelStop;

        checkCuda(cudaEventCreate(&kernelStart));
        checkCuda(cudaEventCreate(&kernelStop));

        float totalKernelMs = 0.0f;

        // Process each FASTA sequence
        for (const auto& sequence : sequences_) {

            const size_t sequenceLength = sequence.size();

            if (sequenceLength < k_) {
                continue;
            }

            // Allocate GPU memory for the DNA sequence
            checkCuda(cudaMalloc(
                reinterpret_cast<void**>(&d_sequence),
                sequenceLength
            ));

            // Copy data from RAM to GPU memory
            checkCuda(cudaMemcpy(
                d_sequence,
                sequence.data(),
                sequenceLength,
                cudaMemcpyHostToDevice
            ));

            // Calculate kernel launch configuration
            constexpr int threadsPerBlock = 256;

            const size_t numWindows = sequenceLength - k_ + 1;

            const size_t numBlocks = (numWindows + threadsPerBlock - 1) / threadsPerBlock;

            checkCuda(cudaEventRecord(kernelStart));

            // Launch the GPU kernel
            countKmersKernel<<<numBlocks, threadsPerBlock>>>(
                d_sequence,
                sequenceLength,
                k_,
                d_counts
            );

            // Check launch and execution errors
            checkCuda(cudaGetLastError());
            checkCuda(cudaDeviceSynchronize());

            // Record when the kernel finishes
            checkCuda(cudaEventRecord(kernelStop));

            // Wait for the GPU to reach this event
            checkCuda(cudaEventSynchronize(kernelStop));

            float kernelMs = 0.0f;

            checkCuda(cudaEventElapsedTime(
                &kernelMs,
                kernelStart,
                kernelStop
            ));

            totalKernelMs += kernelMs;

            // Free this sequence's GPU memory
            checkCuda(cudaFree(d_sequence));
            d_sequence = nullptr;
        }

        // Copy frequency array back to CPU
        checkCuda(cudaMemcpy(
            counts_.data(),
            d_counts,
            countsBytes,
            cudaMemcpyDeviceToHost
        ));

        std::cout << "CUDA kernel time: "
          << totalKernelMs / 1000.0f
          << " seconds\n";

        std::chrono::duration<double> allocTime = allocEnd - allocStart;

        std::cout << "CUDA allocation time: "
            << allocTime.count()
            << " seconds\n";

        checkCuda(cudaEventDestroy(kernelStart));
        checkCuda(cudaEventDestroy(kernelStop));

    } catch (...) {
        // Clean up GPU memory if an error occurs
        cudaFree(d_sequence);
        cudaFree(d_counts);
        throw;
    }



    // Release GPU memory
    checkCuda(cudaFree(d_counts));
}

// Runs on the GPU
__global__ void countKmersKernel(
    const char* sequence,
    size_t sequenceLength,
    uint64_t k,
    unsigned long long* counts)
{
    // Unique starting position assigned to this GPU thread
    size_t i = blockIdx.x * blockDim.x + threadIdx.x;

    // Make sure a complete k-mer fits in the sequence
    if (i >= sequenceLength ||
        k > sequenceLength - i) {
        return;
    }

    uint64_t encoded = 0;

    // Encode the k-mer starting at position i
    for (uint64_t j = 0; j < k; ++j) {
        uint64_t base;

        switch (sequence[i + j]) {
            case 'A': case 'a': base = 0; break;
            case 'C': case 'c': base = 1; break;
            case 'G': case 'g': base = 2; break;
            case 'T': case 't': base = 3; break;

            default:
                return; // Skip invalid k-mers
        }

        // Starts at 0 and encodes exactly k nucleotides, doesn't require mask
        encoded = (encoded << 2) | base;
    }

    // Safely increment the shared GPU frequency array
    atomicAdd(&counts[encoded], 1ULL);
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

