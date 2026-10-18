#include <iostream>
#include <chrono>
#include <stdexcept>
#include <fstream>

#include "KmerCounter.h"

const int maxK = 12;

bool verifyInput(int argc, char** argv, uint64_t& k);

using namespace std;

int main(int argc, char** argv){

    ull k = 0;
    if(!verifyInput(argc, argv, k)){
        return 1;
    }

    auto startFull = std::chrono::steady_clock::now();

    KmerCounter counter(k);
    
    counter.loadFasta(argv[2]);

    auto start = std::chrono::steady_clock::now();

    counter.countSequences();

    auto end = std::chrono::steady_clock::now();

    std::chrono::duration<double> elapsedCount = end - start;

    std::chrono::duration<double> elapsedFull = end - startFull;


    std::cout << "Total processing time: "
            << elapsedFull.count()
            << " seconds\n";

    std::cout << "Count time: "
            << elapsedCount.count()
            << " seconds\n";

    // std::cout << "ACG: " << counter.getCount(6) << std::endl;
    // std::cout << "CGT: " << counter.getCount(27) << std::endl;
    // std::cout << "GTA: " << counter.getCount(44) << std::endl;
    // std::cout << "TAC: " << counter.getCount(49) << std::endl;

    return 0;
}

bool verifyInput(int argc, char** argv, uint64_t& k){

    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <k> <fasta-file>\n";
        return false;
    }else{
        ull kVal = std::stoull(argv[1]);
        if(kVal > 0 && kVal <= maxK){
            k = static_cast<uint64_t>(kVal);
        }else{
            std::cerr << "k-val must be less than greater than 0 and less than" << maxK << std::endl;
            return false;
        }
    }

    return true;
}