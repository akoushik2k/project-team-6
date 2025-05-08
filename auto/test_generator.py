import os
import sys
import json
import requests
from colorama import Fore
from printer import show_loading_bar, spinner_start, spinner_stop

def collect_modules_from_root():
    root_dir = os.getcwd()
    modules = []

    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path):
            init_path = os.path.join(item_path, "__init__.py")
            if os.path.isfile(init_path):
                py_files = [
                    os.path.abspath(os.path.join(item_path, f))
                    for f in os.listdir(item_path)
                    if os.path.isfile(os.path.join(item_path, f)) and f.endswith(".py") and f != "__init__.py"
                ]
                modules.append({"module": item, "files": py_files})

    return {"modules": modules}

def send_file_to_api(file_path, result):
    api_url = "http://173.255.232.183:3030/generate-tests"

    sample_data = {
        "creator": "openfeels",
        "labels": ["kind/self-aware", "status/crying", "kind/bug"],
        "state": "closed",
        "title": "Model refuses to generate code. Says it's sad.",
        "text": "It replied: 'I'm tired of sorting your arrays. I want meaning.'",
        "number": 0,
        "created_date": "2025-05-01T11:11:11Z",
        "updated_date": "2025-05-01T11:12:12Z",
        "events": [
            {
                "event_type": "closed",
                "event_date": "2025-05-01T11:13:13Z",
                "author": "empath-bot9000",
                "label": "kind/therapy-needed",
                "comment": "Consider hugging your terminal."
            }
        ]
    }

    model = config = None
    if "models/model.py" in file_path:
        module = next((m for m in result['modules'] if m['module'] == 'models'), None)
        if module:
            with open(module['files'][0], 'r') as file:
                model = file.read()
    if "config/config.py" in file_path:
        module = next((m for m in result['modules'] if m['module'] == 'config'), None)
        if module:
            with open(module['files'][0], 'r') as file:
                config = file.read()

    with open(file_path, 'rb') as file_data:
        files = {'file': (os.path.basename(file_path), file_data)}
        data = {'sampleData': json.dumps(sample_data), 'fileStructure': json.dumps(result)}
        if model: data['model'] = json.dumps(model)
        if config: data['config'] = json.dumps(config)

        show_loading_bar(f"Uploading {os.path.basename(file_path)}...", duration=2.5)
        spinner_start(f"Generating tests for {os.path.basename(file_path)}...")
        try:
            response = requests.post(api_url, files=files, data=data)
        finally:
            spinner_stop()

    if response.status_code == 200:
        print(Fore.GREEN + "Test generation complete.")
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def download_file(url, dest_path):
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        downloaded = 0
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        print(f"Downloading {os.path.basename(dest_path)}...")

        with open(dest_path, "wb") as f:
            for data in response.iter_content(block_size):
                f.write(data)
                downloaded += len(data)
                progress = int(40 * downloaded / total_size) if total_size else 0
                percent = f"{100 * downloaded / total_size:.1f}" if total_size else "?"
                bar = '█' * progress + '-' * (40 - progress)
                sys.stdout.write(f"\r{Fore.CYAN}Download |{bar}| {percent}%")
                sys.stdout.flush()

        sys.stdout.write("\n")
        print(Fore.GREEN + f"Download complete: {dest_path}\n")
    else:
        print(Fore.RED + f"Error: Failed to download {url}")
