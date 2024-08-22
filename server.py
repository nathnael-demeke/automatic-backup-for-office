import socket 
import json 
import os
import base64
import time
import shutil
import pathlib
from concurrent.futures import ThreadPoolExecutor

clients = [
    "192.168.8.120"
]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 19))
server.listen(2)

backup_finished = False
print("server Started")
server_name = "Nathnael Demeke"
server_selected_directories = [
    {"directory_path": r"C:\\Users\\Hp\\Desktop\\websites\\nodejs", "directory_name": "trials"}
]
def move_all_server_folders():
    for folder in server_selected_directories:
        directory_path = folder["directory_path"]
        directory_name = folder["directory_name"]
        current_dir = pathlib.Path.cwd()
        upload_to_directory = f"./{directory_name} (${server_name})"
        try:
            shutil.rmtree(upload_to_directory)
        except Exception as error:
           pass
        try:
            shutil.copytree(directory_path,f"{current_dir}\\{upload_to_directory}",symlinks=False,ignore=None)
        except Exception as error: 
            print(error)
            

def get_message_from_client(cli):
    full_data = ""
    while True: 
        chunk = cli.recv(1024)
        full_data += chunk.decode("utf-8")
        if (len(chunk) == 0):
            break  
    return full_data
def create_folder(folder_path):
    try:
        os.makedirs(folder_path)
    except OSError as error:
        pass


def download_sub_directory_data(main_directory,directory_data):
        sub_directory_folder_name = list(directory_data.keys())[0]
        files = directory_data[sub_directory_folder_name]["files"]
        folders = directory_data[sub_directory_folder_name]["folders"]
        create_folder(f"{main_directory}\\{sub_directory_folder_name}")
        index = 0
        for folder in folders: 
            download_sub_directory_data(f"{main_directory}\\{sub_directory_folder_name}", directory_data[sub_directory_folder_name]["folders"][index])
            index += 1
        for file in files:
            file_name = list(file.keys())[0]
            file_base64 = file[file_name]
            file_bytes = base64.urlsafe_b64decode(file_base64)
            with open(f"{main_directory}\\{sub_directory_folder_name}\\{file_name}", "wb") as f:
                f.write(file_bytes)


def download_directory_data(main_directory,directory_data, client_name):
    main_directory = list(directory_data.keys())[0]
    main_directory_path = fr"{main_directory} (${client_name})"
    create_folder(main_directory_path)
    files = directory_data[main_directory]["files"]
    folders = directory_data[main_directory]["folders"]
    index = 0
    for folder in folders:
            try:
                 folder_name = list(folder.keys())[0]  
                 download_sub_directory_data(os.path.abspath(f"./{main_directory_path}"),directory_data[main_directory]["folders"][index])
            except: 
                pass
        
            index += 1
    for file in files:
        file_name = list(file.keys())[0]
        file_base64 = file[file_name]
        file_bytes = base64.urlsafe_b64decode(file_base64)
        with open(f"{main_directory_path}\\{file_name}", "wb") as f:
                f.write(file_bytes)
def upload_sub_folder_json(main_directory,sub_folder): 
        try: 
            sub_folder_name = list(sub_folder.keys())[0]
            directory = f"{main_directory}\\{sub_folder_name}"
            files = os.listdir(directory)
            formatted_message = {sub_folder_name: {
                "folders": [],
                "files": []
            }}
            for file in files:
                if file.find(".") == -1:
                    formatted_message[sub_folder_name]["folders"].append({file: {
                        "folders": [],
                        "files": []
                    }})
                else:
                    with open(f"{directory}\\{file}", "rb") as f:
                        file_bytes = f.read()
                        file_base64 = base64.urlsafe_b64encode(file_bytes)
                        file_formmated_message = {file: file_base64.decode("utf-8")}
                        formatted_message[sub_folder_name]["files"].append(file_formmated_message)    
            index = 0
            for folder in formatted_message[sub_folder_name]["folders"]:
                formatted_response = upload_sub_folder_json(directory,folder)
                formatted_message[sub_folder_name]["folders"][index] = formatted_response
                index += 1
            return formatted_message
        except Exception as error:
            print(error)

       
            
def upload_selected_folder_json(directory_path, directory_name):
    files = os.listdir(directory_path)
    formatted_message = {directory_name: {
        "folders": [],
        "files": [],
    }}
    #getting bytes of each file in the directory
    for file in files:
        if file.find(".") == -1:
            try: 
               formatted_message[directory_name]["folders"].append({file: {}})
            except:
                pass
        else:
            try:
                with open(f"{directory_path}\\{file}", "rb") as f:
                    file_bytes = f.read()
                    file_base64 = base64.urlsafe_b64encode(file_bytes)
                    file_formmated_message = {file: file_base64.decode("utf-8")}
                    formatted_message[directory_name]["files"].append(file_formmated_message)
            except:
                pass
    index = 0
    for folder in formatted_message[directory_name]["folders"]:
        sub_folder_data = upload_sub_folder_json(directory_path,folder)
        formatted_message[directory_name]["folders"][index] = sub_folder_data
        index += 1

    return formatted_message
        

    

def serve_user(client):
    full_message = json.loads(get_message_from_client(client))
    client_name = full_message["ClientName"]
    message_type = full_message["MessageType"]
   
    if (message_type == "updateFoldersData"):
        then = time.time()
        print("working on folders data...")
        directories_data = full_message["DirectoriesData"]
        for directory_data in directories_data:
            print(client_name)
            download_directory_data(list(directory_data.keys())[0],directory_data,client_name)
        move_all_server_folders()
        now = time.time()
        print(now - then)

    
    elif message_type == "getUpdatedBackup":
        print("data")
    client.close()


pool = ThreadPoolExecutor(4)

while True: 
    cli, addr = server.accept()
    pool.submit(serve_user,cli)
   
        
        
