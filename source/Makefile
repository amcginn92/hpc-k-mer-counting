CXX = g++
CXXFLAGS = -std=c++17 -O2

TARGET = out

SRC = kmerMain.cpp KmerCounter.cpp

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) -o $(TARGET)

clean:
	rm -f $(TARGET)