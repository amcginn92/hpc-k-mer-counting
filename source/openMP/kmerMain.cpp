#include <iostream>
#include <chrono>
#include <stdexcept>
#include <fstream>

#include "KmerCounter.h"

const int maxK = 12;

bool verifyInput(int argc, char** argv, uint64_t& k, int& numThreads);

using namespace std;

int main(int argc, char** argv){

    ull k = 0;
    int numThreads = 0;

    if (!verifyInput(argc, argv, k, numThreads)) {
        return 1;
    }
    auto startFull = std::chrono::steady_clock::now();

    KmerCounter counter(k);
    
    counter.loadFasta(argv[2]);

    auto start = std::chrono::steady_clock::now();

    counter.countParallel(numThreads);

    auto end = std::chrono::steady_clock::now();

    std::chrono::duration<double> elapsedCount = end - start;

    std::chrono::duration<double> elapsedFull = end - startFull;


    std::cout << "Total processing time: "
            << elapsedFull.count()
            << " seconds\n";

    std::cout << "Count time: "
            << elapsedCount.count()
            << " seconds\n";


    if(argc == 5){
        std::ofstream output(argv[4]);

        if(!output.is_open()){
            std::cerr << "Cannot open output file: " << argv[3] << "\n";
            return 1;
        }

        counter.writeCounts(output);

        if(!output){
            std::cerr << "Error writing counts file\n";
            return 1;
        }
    }

    return 0;
}

bool verifyInput(int argc, char** argv, uint64_t& k, int& numThreads) {

    if (argc != 4 && argc != 5) {
        std::cerr << "Usage: " << argv[0]
                  << " <k> <fasta-file> <thread-count> [counts-output.csv]\n";
        return false;
    }

    try {
        uint64_t kVal = std::stoull(argv[1]);
        numThreads = std::stoi(argv[3]);

        if (kVal == 0 || kVal > maxK) {
            std::cerr << "k must be between 1 and " << maxK << "\n";
            return false;
        }

        if (numThreads < 1) {
            std::cerr << "Thread count must be greater than 0\n";
            return false;
        }

        k = kVal;

    } catch (const std::exception& e) {
        std::cerr << "Invalid argument: " << e.what() << "\n";
        return false;
    }

    return true;
}