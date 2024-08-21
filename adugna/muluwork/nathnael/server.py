import socket 
import json 

clients = [
    "192.168.8.120"
]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
full_data = None
server.bind(("localhost", 19))
server.listen(1)
cli, addr = server.accept()
while True: 
    chunk = cli.recv(1024)
    print(chunk)
    full_data += chunk

print(full_data)