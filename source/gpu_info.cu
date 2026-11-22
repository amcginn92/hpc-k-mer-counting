#include <cuda_runtime.h>
#include <iostream>

int main() {
    cudaDeviceProp prop{};

    cudaError_t err = cudaGetDeviceProperties(&prop, 0);
    if (err != cudaSuccess) {
        std::cerr << cudaGetErrorString(err) << "\n";
        return 1;
    }

    std::cout << "GPU: " << prop.name << "\n";
    std::cout << "SM count: " << prop.multiProcessorCount << "\n";
    std::cout << "Global memory: "
              << prop.totalGlobalMem / (1024 * 1024)
              << " MiB\n";
    std::cout << "Max threads per block: "
              << prop.maxThreadsPerBlock << "\n";
}