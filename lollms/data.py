import base64
import hashlib
import json
from typing import Any, Dict, List
import socketio

class SocketIOFile:
    def __init__(self) -> None:
        """
        Initialize the SocketIOFile instance.
        """
        self.sio = socketio.Client()
        self.files_to_send = []
        self.files_received = []

        @self.sio.event
        def connect() -> None:
            print('Connected to server')

        @self.sio.event
        def disconnect() -> None:
            print('Disconnected from server')

        @self.sio.on('file_transfer')
        def receive_file(json_data: str) -> None:
            """
            Receive and save the file from the Socket.IO server.

            Args:
                json_data (str): The JSON data containing the metadata and file.
            """
            data = json.loads(json_data)
            metadata = data['metadata']
            base64_data = data['file']
            received_filename = metadata['filename']
            self.save_file(received_filename, base64_data)
            print('File received and saved:', received_filename)
            self.files_received.append(received_filename)

    def convert_to_base64(self, file_path: str) -> str:
        """
        Convert the file to Base64-encoded data.

        Args:
            file_path (str): The path to the file.

        Returns:
            str: The Base64-encoded data.
        """
        with open(file_path, 'rb') as file:
            binary_data = file.read()
            base64_data = base64.b64encode(binary_data).decode('utf-8')
        return base64_data

    def calculate_sha256(self, file_path: str) -> str:
        """
        Calculate the SHA256 hash of the file.

        Args:
            file_path (str): The path to the file.

        Returns:
            str: The SHA256 hash value.
        """
        with open(file_path, 'rb') as file:
            binary_data = file.read()
            sha256_hash = hashlib.sha256(binary_data).hexdigest()
        return sha256_hash

    def send_file(self, file_path: str, metadata: Dict[str, Any]) -> None:
        """
        Send a file via Socket.IO connection.

        Args:
            file_path (str): The path to the file to be sent.
            metadata (dict): Additional metadata to be included in the JSON object.
        """
        base64_data = self.convert_to_base64(file_path)
        metadata['sha256'] = self.calculate_sha256(file_path)
        metadata['filename'] = file_path.split('/')[-1]  # Extract filename from the file path
        data = {
            'metadata': metadata,
            'file': base64_data
        }
        json_data = json.dumps(data)
        self.sio.emit('file_transfer', json_data)
        self.files_to_send.append(file_path)

    def save_file(self, file_path: str, base64_data: str) -> None:
        """
        Save the file locally from the Base64-encoded data.

        Args:
            file_path (str): The path to save the file.
            base64_data (str): The Base64-encoded data to be saved.
        """
        binary_data = base64.b64decode(base64_data)
        with open(file_path, 'wb') as file:
            file.write(binary_data)

    def connect(self, url: str) -> None:
        """
        Connect to the Socket.IO server.

        Args:
            url (str): The URL of the Socket.IO server.
        """
        self.sio.connect(url)

    def disconnect(self) -> None:
        """
        Disconnect from the Socket.IO server.
        """
        self.sio.disconnect()

if __name__ == "__main__":
    sio_file = SocketIOFile()
    sio_file.connect('http://your-socketio-server-url')

    # Example metadata for the files
    metadata1 = {'file_size': 1024, 'description': 'File 1'}
    metadata2 = {'file_size': 2048, 'description': 'File 2'}

    # Example file paths
    file_path1 = 'path/to/your/file1.bin'
    file_path2 = 'path/to/your/file2.bin'

    # Send files
    sio_file.send_file(file_path1, metadata1)
    sio_file.send_file(file_path2, metadata2)

    # Wait for files to be sent
    while sio_file.files_to_send:
        pass

    # Wait for files to be received
    while sio_file.files_received != [file_path1.split('/')[-1], file_path2.split('/')[-1]]:
        pass

    sio_file.disconnect()
