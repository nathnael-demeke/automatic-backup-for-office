import socket 
import json 
import os
clients = [
    "192.168.8.120"
]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 19))
server.listen(2)
def get_message_from_client():
    full_data = ""
    cli, addr = server.accept()
    while True: 
        chunk = cli.recv(1024)
        if (len(chunk) == 0):
            break
        full_data += chunk.decode("utf-8")
    return full_data

full_message = json.loads(f"{get_message_from_client()}")

client_name = full_message["ClientName"]
message_type = full_message["MessageType"]
created_folders = 0
def create_folder(folder_path):
    global created_folders
    created_folders += 1
    try:
        os.makedirs(folder_path)
    except OSError as error:
        pass
def download_sub_directory_data(main_directory,directory_data):
        sub_directory_folder_name = list(directory_data.keys())[0]
        files = directory_data[sub_directory_folder_name]["files"]
        folders = directory_data[sub_directory_folder_name]["folders"]
        create_folder(f"{main_directory}\\{sub_directory_folder_name}")
        print(f"{main_directory}\\{sub_directory_folder_name}")
        index = 0
        for folder in folders: 
            download_sub_directory_data(f"{main_directory}\\{sub_directory_folder_name}", directory_data[sub_directory_folder_name]["folders"][index])
            index += 1
            
    

def download_directory_data(main_directory,directory_data):
    main_directory = list(directory_data.keys())[0]
    main_directory_path = fr"{main_directory} (${client_name})"
    create_folder(main_directory_path)
    files = directory_data[main_directory]["files"]
    folders = directory_data[main_directory]["folders"]
    index = 0
    for folder in folders:
            folder_name = list(folder.keys())[0]  
            download_sub_directory_data(os.path.abspath(f"./{main_directory_path}"),directory_data[main_directory]["folders"][index])
            index += 1
            
    print(created_folders)
        
        
if (message_type == "updateFoldersData"):
    directories_data = full_message["DirectoriesData"]
    for directory_data in directories_data:
        download_directory_data(list(directory_data.keys())[0],directory_data)
        
        
