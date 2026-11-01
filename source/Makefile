
CXX = g++
CXXFLAGS = -std=c++17 -O2

SEQ_SRC = sequential/kmerMain.cpp sequential/KmerCounter.cpp
SEQ_TARGET = sequential/out

OMP_SRC = openMP/kmerMain.cpp openMP/KmerCounter.cpp
OMP_TARGET = openMP/out
OMPFLAGS = -fopenmp


.PHONY: all sequential openmp clean

all: sequential openmp

sequential: $(SEQ_TARGET)

openmp: $(OMP_TARGET)

$(SEQ_TARGET): $(SEQ_SRC) sequential/KmerCounter.h
	$(CXX) $(CXXFLAGS) $(SEQ_SRC) -o $(SEQ_TARGET)

$(OMP_TARGET): $(OMP_SRC) openMP/KmerCounter.h
	$(CXX) $(CXXFLAGS) $(OMPFLAGS) $(OMP_SRC) -o $(OMP_TARGET)

clean:
	rm -f $(SEQ_TARGET) $(OMP_TARGET)
