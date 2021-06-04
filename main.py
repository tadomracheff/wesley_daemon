from db.firestore import listen
import time
import socket

listen()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 5000))
server_socket.listen(1)

while True:
    (client_socket, address) = server_socket.accept()
    data = client_socket.recv(1)
    time.sleep(1)
    if not data:
        break
    response = '1:1 2:2;'
    client_socket.send(str.encode(response))

client_socket.close()
