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
server.bind(("0.0.0.0", 80))
server.listen(2)


backup_finished = False
clients_quantity = 1
clients_backuped = 0
backuped_data_json = None
server_name = "Nathnael Demeke"
server_selected_directories = [
    {"directory_path": r"C:\\Users\\Hp\\Desktop\\websites\\nodejs", "directory_name": "trials"}
]
current_dir_path = os.path.dirname(__file__).replace("\\", "\\\\")
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
        chunk = cli.recv(1024).decode("utf-8")
        if chunk == "break" or (len(chunk) == 0):
            break  
        full_data += chunk
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
    print(f"{main_directory_path} file downloaded")
def upload_sub_folder_json(main_directory,sub_folder): 
        global backuped_data_json
        try: 
            sub_folder_name = list(sub_folder.keys())[0]
            directory = f"{main_directory}\\{sub_folder_name}"
            files = os.listdir(directory)
            formatted_message = {sub_folder_name: {
                "folders": [],
                "files": []
            }}
            for file in files:
                if os.path.isdir(f"{main_directory}\\{sub_folder_name}\\{file}"):
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
 
def upload_backup_folder_json():
    global backuped_data_json
    directory_path = current_dir_path
    directory_name = "backup folder"
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
            pass
    index = 0
    for folder in formatted_message[directory_name]["folders"]:
        sub_folder_data = upload_sub_folder_json(directory_path,folder)
        formatted_message[directory_name]["folders"][index] = sub_folder_data
        index += 1

    backuped_data_json = formatted_message

def serve_user(client):
    global clients_backuped
    now = time.time()
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
        clients_backuped += 1
    elif message_type == "getUpdatedBackup":
        print("message got")
        if backuped_data_json:
            response = {"MessageType": "downloadBackup", "Message": backuped_data_json}
            client.send(bytes(json.dumps(response), "utf-8"))
            print("client backuped")
        else:
            not_finished_message = {"MessageType": "notFinished"}
            client.send(bytes(json.dumps(not_finished_message), "utf-8"))
    else:
        print("unkown request")
    client.close()


pool = ThreadPoolExecutor(clients_quantity * 2)
backup_worker = ThreadPoolExecutor(1)

def upload_backup_to_ram():
    global backup_finished
    move_all_server_folders()
    upload_backup_folder_json()
    backup_finished = True
    print("backup finished")

while True: 
    if (clients_quantity == clients_backuped) and (backup_finished == False):
        backup_worker.submit(upload_backup_to_ram)
    cli, addr = server.accept()
    worker = pool.submit(serve_user,cli)
    print("result " + str(worker.result()))