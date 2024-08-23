import re
import string
import socket

def clean_text(text):
    text = str(text)
    text = text.lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>+', '', text)
    text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub(r'\n', '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    return text

def handle_client(client_socket):
    data = client_socket.recv(1024).decode('utf-8')
    if data.startswith('clean:'):
        response = clean_text(data[6:])
        client_socket.sendall(response.encode('utf-8'))
    else:
        client_socket.sendall("Invalid request".encode('utf-8'))
    client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 5002))
    server_socket.listen(5)
    print("Clean-text service listening on port 5002")
    
    while True:
        client_socket, _ = server_socket.accept()
        handle_client(client_socket)

if __name__ == '__main__':
    main()
