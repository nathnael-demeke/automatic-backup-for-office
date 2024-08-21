import socket 
import json 

clients = [
    "192.168.8.120"
]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 19))
server.listen(2)
full_data = ""
cli, addr = server.accept()
while True: 
    chunk = cli.recv(1024)
    if (len(chunk) == 0):
        break
    full_data += chunk.decode("utf-8")

print(full_data)