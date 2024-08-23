from flask import Flask, jsonify, request, render_template
from flask_assets import Environment, Bundle
import socket
import torch
import numpy as np
import logging
from webassets.cache import FilesystemCache
import os

# Set up caching for assets
cache_dir = '/tmp/.webassets-cache'
os.makedirs(cache_dir, exist_ok=True)

# Initialize Flask and Flask-Assets
app = Flask(__name__)
env = Environment(app)
env.directory = 'static'
env.url = '/static'
env.cache = FilesystemCache(cache_dir)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize and register SCSS assets
scss = Bundle('scss/style.scss', filters='libsass', output='gen/style.css')
env.register('scss_all', scss)
scss.build(force=True)

def request_service(host, port, message, expect_binary=False):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        logging.debug(f"Connected to {host}:{port}")
        if isinstance(message, str):
            client_socket.sendall(message.encode('utf-8'))
        else:
            client_socket.sendall(message)

        if expect_binary:
            response = b""
            while True:
                part = client_socket.recv(4096)
                response += part
                if len(part) < 4096:
                    break
        else:
            response = client_socket.recv(1024).decode('utf-8')

        client_socket.close()
        logging.debug(f"Received response from {host}:{port}")
        return response

    except socket.gaierror as e:
        logging.error(f"Address-related error connecting to server: {e}")
    except socket.error as e:
        logging.error(f"Connection error: {e}")
    return None

@app.route('/')
def home():
    return render_template('about.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/hello/<name>')
def hello(name):
    return f"Hello, {name}!"

@app.route('/json')
def json_example():
    return jsonify(message="Hello, World!", status="success")

@app.route('/post-example', methods=['POST'])
def post_example():
    data = request.json
    return jsonify(received=data)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/ready', methods=['GET'])
def readiness_check():
    return jsonify({"status": "ready"}), 200

@app.route('/button-click', methods=['POST'])
def button_click():
    try:
        data = request.json
        message = data.get("message", "")
        logging.debug(f"Received message: {message}")

        # Preprocess the input
        logging.debug("Calling clean_text service")
        clean = request_service('clean-text', 5002, f'clean:{message}')
        if clean is None:
            logging.error("Error in clean_text service")
            return jsonify({'error': 'Error in clean_text service'}), 500

        logging.debug(f"CLEANED: {clean}")
        embd = request_service('embedding-service', 5003, f'embed:{clean}', expect_binary=True)
        if embd is None:
            logging.error("Error in embedding service")
            return jsonify({'error': 'Error in embedding service'}), 500

        logging.debug("EMBEDDED")
        # Convert bytes back to tensor
        embd_np = np.frombuffer(embd, dtype=np.float32).reshape(200, 256)
        embd_np_copy = np.copy(embd_np)  # Create a writable copy
        embd_tensor = torch.from_numpy(embd_np_copy)

        # Send tensor to prediction service
        label = request_service('model-service', 5004, embd_tensor.numpy().tobytes(), expect_binary=False)
        if label is None:
            logging.error("Error in model service")
            return jsonify({'error': 'Error in model service'}), 500

        logging.debug(f"PREDICTED: {label}")

        # Modify the message based on the prediction (for demonstration purposes)
        modified_message = f"Processed message: {message} - Sentiment: {label}"
        logging.debug(modified_message)

        return jsonify(status="success", message=modified_message)
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,)
