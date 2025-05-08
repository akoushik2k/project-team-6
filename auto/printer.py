import sys
import time
import threading
from colorama import Fore

spinner_running = False

def print_progress_bar(iteration, total, prefix='', length=40):
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{Fore.CYAN}{prefix} |{bar}| {percent}%')
    sys.stdout.flush()
    if iteration == total:
        sys.stdout.write('\n')

def show_loading_bar(message="Uploading...", duration=3):
    total = 50
    print(message)
    for i in range(total + 1):
        print_progress_bar(i, total, prefix="Upload")
        time.sleep(duration / total)

def spinner_start(message="Generating tests..."):
    def spin():
        cycle = ['|', '/', '-', '\\']
        idx = 0
        while spinner_running:
            sys.stdout.write(f"\r{Fore.CYAN}{message} {cycle[idx % len(cycle)]}")
            sys.stdout.flush()
            time.sleep(0.1)
            idx += 1
        sys.stdout.write(f"\r" + " " * (len(message) + 2) + "\r")

    global spinner_running, spinner_thread
    spinner_running = True
    spinner_thread = threading.Thread(target=spin)
    spinner_thread.start()

def spinner_stop():
    global spinner_running
    spinner_running = False
    spinner_thread.join()