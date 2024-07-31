from flask import Flask, jsonify, request, render_template
from flask_assets import Environment, Bundle
import socket
import torch
import numpy as np
from pymongo import MongoClient

app = Flask(__name__)

# Initialize Flask-Assets
assets = Environment(app)
scss = Bundle('style.scss', filters='libsass', output='gen/style.css')
assets.register('scss_all', scss)
scss.build()

# MongoDB setup
client = MongoClient("mongodb+srv://pronaouzilias:h97Hu1bu7ogH2jb3@audensiel.kc7tr5z.mongodb.net/")
db = client['Comments']
collection = db['Comment']

def request_service(host, port, message, expect_binary=False):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
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
        return response
    except socket.gaierror as e:
        print(f"Address-related error connecting to server: {e}")
    except socket.error as e:
        print(f"Connection error: {e}")
    return None

@app.route('/')
def home():
    return "Welcome to the Flask App!"

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

@app.route('/button-click', methods=['POST'])
def button_click():
    data = request.json
    message = data.get("message", "")
    
    # Preprocess the input similarly to the /predict endpoint
    print("Calling clean_text service")
    clean = request_service('localhost', 5002, f'clean:{message}')
    if clean is None:
        return jsonify({'error': 'Error in clean_text service'}), 500

    print(f"CLEANED: {clean}")
    embd = request_service('localhost', 5003, f'embed:{clean}', expect_binary=True)
    if embd is None:
        return jsonify({'error': 'Error in embedding service'}), 500

    print("EMBEDDED")
    # Convert bytes back to tensor
    embd_np = np.frombuffer(embd, dtype=np.float32).reshape(200, 256)
    embd_np_copy = np.copy(embd_np)  # Create a writable copy
    embd_tensor = torch.from_numpy(embd_np_copy)

    # Send tensor to prediction service
    label = request_service('localhost', 5004, embd_tensor.numpy().tobytes(), expect_binary=False)
    if label is None:
        return jsonify({'error': 'Error in model service'}), 500

    print(f"PREDICTED: {label}")

    # Store the comment, cleaned text, and prediction in MongoDB
    comment_data = {
        "comment": message,
        "cleaned": clean,
        "prediction": label
    }
    collection.insert_one(comment_data)

    # Modify the message based on the prediction (for demonstration purposes)
    modified_message = f"Processed message: {message} - Sentiment: {label}"
    print(modified_message)

    return jsonify(status="success", message=modified_message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
