import socket
import torch
from transformers import ElectraTokenizer, ElectraModel
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)

tokenizer = ElectraTokenizer.from_pretrained('dbmdz/electra-base-french-europeana-cased-generator')
model = ElectraModel.from_pretrained('dbmdz/electra-base-french-europeana-cased-generator')

def embedding(text):
    tokens = tokenizer.encode_plus(text, add_special_tokens=True, truncation=True,
                                   max_length=200, padding='max_length',
                                   return_tensors='pt')
    input_ids = tokens['input_ids']
    attention_mask = tokens['attention_mask']

    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
    embeddings = outputs.last_hidden_state
    embeddings = embeddings.squeeze(0)
    return embeddings

def handle_client(client_socket):
    try:
        message = client_socket.recv(1024).decode('utf-8')
        logging.debug(f"Received message: {message}")
        if message.startswith('embed:'):
            phrase = message[len('embed:'):]
            logging.debug(f"Processing phrase: {phrase}")
            embedding_tensor = embedding(phrase)
            response = embedding_tensor.numpy().tobytes()
            client_socket.sendall(response)
            logging.debug(f"Sent embedding response")
        else:
            client_socket.sendall(b"Invalid command")
            logging.debug("Invalid command received")
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        client_socket.close()

def main():
    host = '0.0.0.0'
    port = 5003

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    logging.info(f"Embedding service listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        logging.info(f"Connection from {addr}")
        handle_client(client_socket)

if __name__ == '__main__':
    main()
