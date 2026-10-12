#pragma once

#include <cstdint>
#include <vector>
#include <string>

typedef uint64_t ull;

class KmerCounter{

public:
    //================================== Constructor/Destructor
    KmerCounter(uint64_t k);
    ~KmerCounter() = default;

    //==================================Public Functions
    void countSequence(const std::string& sequence);
    void countSequences();
    uint64_t getCount(uint64_t encoded) const;
    void loadFasta(const std::string& filename);
    
    //==================================Public Variables
    

private: 

    //==================================Private Functions
    uint8_t encodeBase(char base);


    //==================================Private Variables
    uint64_t k_;
    std::vector<uint64_t> counts_;
    std::vector<std::string> sequences_;



};