#include <iostream>
#include <fstream>
#include <chrono>

#include "KmerCounter.h"

bool verifyInput(int argc, char** argv, uint64_t& k);
bool processFasta(const std::string& filename, KmerCounter& counter);

using namespace std;

int main(int argc, char** argv){

    ull k = 0;
    if(!verifyInput(argc, argv, k)){
        return 1;
    }

    KmerCounter counter(k);

    auto start = std::chrono::steady_clock::now();

    if (!processFasta(argv[2], counter)) {
        return 1;
    }

    auto end = std::chrono::steady_clock::now();

    std::chrono::duration<double> elapsed = end - start;

    std::cout << "Processing time: "
            << elapsed.count()
            << " seconds\n";

    // counter.countSequence("ACGTACGT");
    // counter.countSequence("ACGNTACG");
    
    // std::cout << "ACG: " << counter.getCount(6) << std::endl;
    // std::cout << "CGT: " << counter.getCount(27) << std::endl;
    // std::cout << "GTA: " << counter.getCount(44) << std::endl;
    // std::cout << "TAC: " << counter.getCount(49) << std::endl;

    return 0;
}

bool processFasta(const std::string& filename, KmerCounter& counter)
{
    std::ifstream file(filename);

    if (!file.is_open()) {
        std::cerr << "Unable to open file: " << filename << '\n';
        return false;
    }

    std::string line;
    std::string sequence;

    while (std::getline(file, line)) {

        if (!line.empty() && line[0] == '>') {

            if (!sequence.empty()) {
                counter.countSequence(sequence);
                sequence.clear();
            }

        } else {
            sequence += line;
        }
    }

    // Process the final sequence
    if (!sequence.empty()) {
        counter.countSequence(sequence);
    }

    if (file.bad()) {
        std::cerr << "Error reading FASTA file\n";
        return false;
    }

    return true;
}

bool verifyInput(int argc, char** argv, uint64_t& k){

    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <k> <fasta-file>\n";
        return false;
    }else{
        ull kVal = std::stoull(argv[1]);
        if(kVal > 0 && kVal <= 64){
            k = static_cast<uint64_t>(kVal);
        }else{
            std::cerr << "k-val must be less than greater than 0 and less than 64" << std::endl;
            return false;
        }
    }

    return true;
}