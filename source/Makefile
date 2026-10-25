
CXX = g++
CXXFLAGS = -std=c++17 -O2

SEQ_SRC = sequential/kmerMain.cpp sequential/KmerCounter.cpp
SEQ_TARGET = sequential/out

OMP_SRC = openmp/kmerMainOMP.cpp openmp/KmerCounterOMP.cpp
OMP_TARGET = openmp/out
OMPFLAGS = -fopenmp


.PHONY: all sequential openmp clean

all: sequential

sequential: $(SEQ_TARGET)

openmp: $(OMP_TARGET)

$(SEQ_TARGET): $(SEQ_SRC) sequential/KmerCounter.h
	$(CXX) $(CXXFLAGS) $(SEQ_SRC) -o $(SEQ_TARGET)

$(OMP_TARGET): $(OMP_SRC) openmp/KmerCounterOMP.h
	$(CXX) $(CXXFLAGS) $(OMPFLAGS) $(OMP_SRC) -o $(OMP_TARGET)

clean:
	rm -f $(SEQ_TARGET) $(OMP_TARGET)
