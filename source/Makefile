
CXX = g++
CXXFLAGS = -std=c++17 -O2

NVCC = /usr/local/cuda/bin/nvcc
NVCCFLAGS = -std=c++17 -O2 -gencode arch=compute_120,code=sm_120

SEQ_SRC = sequential/kmerMain.cpp sequential/KmerCounter.cpp
SEQ_TARGET = sequential/out

OMP_SRC = openMP/kmerMain.cpp openMP/KmerCounter.cpp
OMP_TARGET = openMP/out
OMPFLAGS = -fopenmp

CUDA_SRC = cuda/kmerMain.cpp cuda/KmerCounter.cu
CUDA_TARGET = cuda/out

.PHONY: all sequential openmp cuda clean

all: sequential openmp cuda

sequential: $(SEQ_TARGET)

openmp: $(OMP_TARGET)

cuda: $(CUDA_TARGET)

$(SEQ_TARGET): $(SEQ_SRC) sequential/KmerCounter.h
	$(CXX) $(CXXFLAGS) $(SEQ_SRC) -o $(SEQ_TARGET)

$(OMP_TARGET): $(OMP_SRC) openMP/KmerCounter.h
	$(CXX) $(CXXFLAGS) $(OMPFLAGS) $(OMP_SRC) -o $(OMP_TARGET)

$(CUDA_TARGET): $(CUDA_SRC) cuda/KmerCounter.h
	$(NVCC) $(NVCCFLAGS) $(CUDA_SRC) -o $(CUDA_TARGET)

clean:
	rm -f $(SEQ_TARGET) $(OMP_TARGET) $(CUDA_TARGET)
