print("Pomodoro Clock starting...")
import time
import subprocess
def activate_dnd():
    subprocess.run(["shortcuts", "run", "Enable DND"])
def deactivate_dnd():
    subprocess.run(["shortcuts", "run", "Disable DND"])
def start_pomodoro():
    print("Pomodoro Clock starting... 25 minuter fokus!")
    activate_dnd()
    time.sleep(1500)
    print("Dags för paus! Deactivating DND.")
    deactivate_dnd()
start_pomodoro()