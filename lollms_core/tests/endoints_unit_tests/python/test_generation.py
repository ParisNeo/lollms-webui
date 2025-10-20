import argparse
import socketio
from pathlib import Path
from lollms import MSG_TYPE
import time 
import sys
# Connect to the Socket.IO server
sio = socketio.Client()


# Event handler for receiving generated text
@sio.event
def text_generated(data):
    print('Generated text:', data)

def test_generate_text(host, port, text_file):
    # Read the text file and split by multiple newlines
    print("Loading file")
    with open(text_file, 'r') as file:
        prompts = file.read().split('\n\n')

    is_ready=[False]
    # Event handler for successful connection
    @sio.event
    def connect():
        print('Connected to Socket.IO server')
        for prompt in prompts:
            if prompt:
                # Trigger the 'generate_text' event with the prompt
                is_ready[0]=False
                print(f"Sending prompt:{prompt}")
                sio.emit('generate_text', {'prompt': prompt, 'personality':-1, "n_predicts":1024})
                while is_ready[0]==False:
                    time.sleep(0.1)

    @sio.event
    def text_chunk(data):
        print(data["chunk"],end="")
        sys.stdout = sys.__stdout__
        sys.stdout.flush()


    @sio.event
    def text_generated(data):
        print("text_generated_ok")
        print(data["text"])
        is_ready[0]=True

    print(f"Connecting to http://{host}:{port}")
    # Connect to the Socket.IO server
    sio.connect(f'http://{host}:{port}')

    # Start the event loop
    sio.wait()

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Socket.IO endpoint test')
    parser.add_argument('--host', type=str, default='localhost', help='Socket.IO server host')
    parser.add_argument('--port', type=int, default=9600, help='Socket.IO server port')
    parser.add_argument('--text-file', type=str, default=str(Path(__file__).parent/"example_text_gen.txt"),help='Path to the text file')
    args = parser.parse_args()

    # Verify if the text file exists
    text_file_path = Path(args.text_file)
    if not text_file_path.is_file():
        print(f"Error: The provided text file '{args.text_file}' does not exist.")
    else:
        # Run the test with provided arguments
        test_generate_text(args.host, args.port, args.text_file)
