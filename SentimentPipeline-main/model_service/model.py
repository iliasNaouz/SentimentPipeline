import socket
import numpy as np
import tensorflow as tf
import torch
import os
import requests

def download_model(url, local_path, auth):
    response = requests.get(url, auth=auth)
    response.raise_for_status()  # Ensure we raise an error for bad responses (4xx and 5xx)
    with open(local_path, 'wb') as file:
        file.write(response.content)
    print(f"Model downloaded to {local_path}")

def build_model(input_shape=(200, 256), dense_units=256, dropout_rate=0.1, output_units=1, activ='relu'):
    initializer = tf.keras.initializers.GlorotUniform()
    model = tf.keras.Sequential([
        tf.keras.layers.Conv1D(32, 2, activation=activ, input_shape=input_shape, kernel_initializer=initializer),
        tf.keras.layers.Conv1D(64, 2, activation=activ, kernel_initializer=initializer),
        tf.keras.layers.MaxPooling1D(),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(dense_units, activation=activ, kernel_initializer=initializer),
        tf.keras.layers.Dropout(dropout_rate),
        tf.keras.layers.Dense(output_units, activation='sigmoid', kernel_initializer=initializer)
    ])
    return model

model_url = "https://audensiel123.jfrog.io/artifactory/model-generic-local/model.h5"
model_path = "my_model.h5"
auth = ('ilyassjoker2@gmail.com', 'cmVmdGtuOjAxOjE3NTM5NTI4OTY6MDJiVEVyM3FZSXBobVpKM1M3OUk1RHZVdE54')  # Replace with your email and API key or password

if not os.path.exists(model_path):
    download_model(model_url, model_path, auth)
else:
    print(f"Model file already exists at {model_path}")

# Check if the file is correctly downloaded and not corrupted
try:
    with open(model_path, 'rb') as file:
        file.read(4)
    print("Model file is valid")
except Exception as e:
    print(f"Model file is invalid: {e}")
    download_model(model_url, model_path, auth)

# Build and load the model
try:
    model = tf.keras.models.load_model(model_path)
    print("Model loaded successfully using load_model")
except:
    model = build_model()
    model.load_weights(model_path)
    print("Model weights loaded successfully using load_weights")

def predict(embeddings):
    embeddings_np = np.frombuffer(embeddings, dtype=np.float32).reshape(1, 200, 256)
    embeddings_tensor = torch.tensor(embeddings_np)
    embeddings_np = embeddings_tensor.numpy()
    prediction = model.predict(embeddings_np)
    label = "Positive" if prediction[0][0] < 0.5 else "Negative"
    return label

def handle_client(client_socket):
    print("Handling client")
    data = b""
    expected_size = 1 * 200 * 256 * 4  
    client_socket.settimeout(20)  
    try:
        while len(data) < expected_size:
            part = client_socket.recv(4096)
            if not part:
                break
            data += part
            print(f"Received data length: {len(data)}")
        if len(data) == expected_size:
            label = predict(data)
            client_socket.sendall(label.encode('utf-8'))
            print("Response sent to client")
        else:
            print("Received incomplete data")
    except socket.timeout:
        print("Socket timed out, closing connection")
    finally:
        client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 5004))
    server_socket.listen(5)
    print("Model service listening on port 5004")
    
    while True:
        client_socket, _ = server_socket.accept()
        handle_client(client_socket)

if __name__ == '__main__':
    main()
