import socket 
import json 
import os
import base64

def upload_selected_catagory_json(directory):
    files = os.listdir(dir)
    formatted_message = {directory: {
        "folders": [],
        "files": [],
    }}
    for file in files:
        
        if file.find(".") == -1:
            formatted_message[directory]["folders"].append(file)
        else:
            with open(f"{directory}\\{file}", "rb") as f:
                file_bytes = f.read()
                file_base64 = base64.urlsafe_b64encode(file_bytes)
                file_formmated_message = {file: file_base64}
                formatted_message[directory]["files"].append(file_formmated_message)
    file_base64_data = formatted_message[directory]["files"][2]["4_5845732226825720001.PDF"]
    return formatted_message
        

    

selected_directories = [
    r"C:\\Users\\Hp\\Documents"
]

for dir in selected_directories:
   upload_selected_catagory_json(dir)




