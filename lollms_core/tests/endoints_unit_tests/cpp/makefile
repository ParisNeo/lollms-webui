CXX = g++
CXXFLAGS = -std=c++11 -Wall
LIBS = -L/path/to/sio_client_library -lsio_client

# Adjust the path above to the directory where you have the sio_client library

SRC = main.cpp

all: executable

executable: $(SRC)
	$(CXX) $(CXXFLAGS) $(LIBS) $(SRC) -o executable

clean:
	del executable
