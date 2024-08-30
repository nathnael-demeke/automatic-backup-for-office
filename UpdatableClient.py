import socket 
import json 
import os
import base64
import time

current_dir_path = os.path.dirname(__file__).replace("\\", "\\\\")
server_address = "localhost"
def create_folder(folder_path):
    try:
        os.makedirs(folder_path)
    except OSError as error:
        pass
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


def download_directory_data(directory_data):
    main_directory = current_dir_path + "\\adugna"
    main_directory = list(directory_data.keys())[0]
    main_directory_path = fr"{main_directory}"
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

    
client_name = "Muluwork Adugna"
selected_directories = [ {"directory_path": r"C:\\Users\\Hp\\Desktop\\softwares\\automatic-backup-for-office\\adugna", "directory_name": "adugna"} ]
message_to_backup_server = {
    "MessageType": "updateFoldersData",
    "ClientName": client_name,
    "DirectoriesData": [],
}
for data in selected_directories:
    directory_name = data["directory_name"]
    directory_path = data["directory_path"]
    full_message = upload_selected_folder_json(directory_path=directory_path, directory_name=directory_name)
    message_to_backup_server["DirectoriesData"].append(full_message)

while True:
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect(("127.0.0.1", 19))
        server.send(bytes(json.dumps(message_to_backup_server),"utf-8"))
        server.close()
        break
    except Exception as error: 
        pass
get_backup_message = {"MessageType": "getUpdatedBackup", "ClientName": client_name}
time.sleep(5)
while True: 
        second_request_server = socket.socket()
        second_request_server.connect(("localhost", 19))
        second_request_server.send(bytes(json.dumps(get_backup_message), "utf-8"))
        time.sleep(1)
        second_request_server.send(bytes("break", "utf-8"))
        full_message = ""
        while True:
            chunk = second_request_server.recv(1024).decode("utf-8")
            if len(chunk) == 0:
                break
            full_message += chunk
        response = json.loads(full_message)
        if response["MessageType"] == "notFinished":
            print("not finished")
        elif response["MessageType"] == "downloadBackup":
            download_directory_data(response["Message"])
            break
        
        second_request_server.close()
        time.sleep(3)
   


   






