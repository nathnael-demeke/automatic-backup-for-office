import socket 
import json 
import os
import base64

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
                        file_formmated_message = {file: file_base64}
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
            formatted_message[directory_name]["folders"].append({file: {}})
        else:
            with open(f"{directory}\\{file}", "rb") as f:
                file_bytes = f.read()
                file_base64 = base64.urlsafe_b64encode(file_bytes)
                file_formmated_message = {file: file_base64}
                formatted_message[directory]["files"].append(file_formmated_message)
    index = 0
    for folder in formatted_message[directory_name]["folders"]:
        sub_folder_data = upload_sub_folder_json(directory_path,folder)
        formatted_message[directory_name]["folders"][index] = sub_folder_data
        index += 1

    return formatted_message
        

    
client_name = "Muluwork Adugna"
selected_directories = [
    {"directory_path": r"C:\\Users\\Hp\\Desktop\\Projects\\automatic-backup-for-office\\adugna", "directory_name": "adugna"}
]
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

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(("127.0.0.1", 19))
server.send(bytes(str(message_to_backup_server), "utf-8"))




