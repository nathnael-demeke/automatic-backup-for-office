import socket 
import json 

clients = [
    "192.168.8.120"
]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
full_data = None
while True: 
    chunk = server.recv(1024)
    full_data += chunk

print(full_data)