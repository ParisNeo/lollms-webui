#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <thread>
#include <chrono>

// Don't forget to download these libraries
// git clone https://github.com/socketio/socket.io-client-cpp.git
#include <cxxopts.hpp>
#include <sio_client.h>

// Connect to the Socket.IO server
sio::client socket_client;

// Event handler for receiving generated text
void text_generated(const sio::event& event) {
    std::cout << "Generated text: " << event.get_message()->get_string() << std::endl;
}

void test_generate_text(const std::string& host, int port, const std::string& text_file) {
    // Read the text file and split by multiple newlines
    std::cout << "Loading file" << std::endl;
    std::ifstream file(text_file);
    std::string prompt;
    std::vector<std::string> prompts;
    while (std::getline(file, prompt, '\n')) {
        if (!prompt.empty())
            prompts.push_back(prompt);
    }

    bool is_ready = false;

    // Event handler for successful connection
    socket_client.set_open_listener([&]() {
        std::cout << "Connected to Socket.IO server" << std::endl;
        for (const auto& prompt : prompts) {
            if (!prompt.empty()) {
                // Trigger the 'generate_text' event with the prompt
                is_ready = false;
                std::cout << "Sending prompt: " << prompt << std::endl;
                socket_client.socket()->emit("generate_text", sio::object_message::create_object({ 
                    { "prompt", prompt },
                    { "personality", -1 },
                    { "n_predicts", 1024 }
                }));
                while (!is_ready)
                    std::this_thread::sleep_for(std::chrono::milliseconds(100));
            }
        }
    });

    socket_client.socket()->on("text_chunk", [&](sio::event& event) {
        std::cout << event.get_message()->get_map()["chunk"]->get_string();
    });

    socket_client.socket()->on("text_generated", [&](sio::event& event) {
        std::cout << "text_generated_ok" << std::endl;
        std::cout << event.get_message()->get_map()["text"]->get_string() << std::endl;
        is_ready = true;
    });

    std::cout << "Connecting to http://" << host << ":" << port << std::endl;
    // Connect to the Socket.IO server
    socket_client.connect(host + ":" + std::to_string(port));

    // Start the event loop
    socket_client.socket()->io_service()->poll();
}

int main(int argc, char** argv) {
    cxxopts::Options options("Socket.IO endpoint test", "Usage: ./executable [options]");
    options.add_options()
        ("h,host", "Socket.IO server host", cxxopts::value<std::string>()->default_value("localhost"))
        ("p,port", "Socket.IO server port", cxxopts::value<int>()->default_value("9600"))
        ("t,text-file", "Path to the text file", cxxopts::value<std::string>());

    auto parsed_args = options.parse(argc, argv);

    std::string host = parsed_args["host"].as<std::string>();
    int port = parsed_args["port"].as<int>();
    std::string text_file = parsed_args["text-file"].as<std::string>();

    // Verify if the text file exists
    std::ifstream file_stream(text_file);
    if (!file_stream) {
        std::cerr << "Error: The provided text file '" << text_file << "' does not exist." << std::endl;
        return 1;
    }

    // Run the test with provided arguments
    test_generate_text(host, port, text_file);

    return 0;
}
