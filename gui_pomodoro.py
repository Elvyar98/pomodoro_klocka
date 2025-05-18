import tkinter as tk
from tkinter import messagebox
import subprocess
import time
import threading

WORK_MINUTES = 25
SHORT_BREAK = 5
LONG_BREAK = 15
POMODOROS_BEFORE_LONG_BREAK = 4

class PomodoroApp:
    def __init__(self, root):
        self.current_theme= "light"
        self.root = root
        self.root.title("Pomodoro Klocka")
        self.root.geometry("320x240")
        self.running=False
        self.is_break=False
        self.pomodoro_count=0
        self.is_work_period=True
        self.break_type=None


        self.theme_button = tk.Button(self.root, text="Dark Mode", command=self.toggle_theme)
        self.theme_button.pack(pady=5)

        self.label = tk.Label(root, text="25:00", font=("Helvetica", 48))
        self.label.pack(pady=10)

        self.status_label = tk.Label(root, text="Status: Klar", font=("Helvetica", 14))
        self.status_label.pack()

        self.start_button = tk.Button(root, text="Start", command=self.start_timer)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_timer, state=tk.DISABLED)
        self.stop_button.pack()

        self.seconds_left = WORK_MINUTES * 60
        self.running = False
        self.pomodoro_count = 0
        self.is_break = False

    def toggle_theme(self):
     if self.current_theme == "light":
        self.root.config(bg="#2e2e2e")
        self.label.config(bg="#2e2e2e", fg="white")
        self.start_button.config(bg="#444", fg="white", activebackground="#666")
        self.theme_button.config(text="Light Mode", bg="#444", fg="white", activebackground="#666")
        self.current_theme = "dark"
     else:
        self.root.config(bg="white")
        self.label.config(bg="white", fg="black")
        self.start_button.config(bg="SystemButtonFace", fg="black", activebackground="SystemButtonFace")
        self.theme_button.config(text="Dark Mode", bg="SystemButtonFace", fg="black", activebackground="SystemButtonFace")
        self.current_theme = "light"
   
    def activate_dnd(self):
        subprocess.run(["shortcuts", "run", "Enable DND"])

    def deactivate_dnd(self):
        subprocess.run(["shortcuts", "run", "Disable DND"])

    def play_sound(self, sound_type):
        if sound_type == "start":
            subprocess.run(["say", "Fokus"])
        elif sound_type == "short_break":
            subprocess.run(["say", "Paus"])
        elif sound_type == "long_break":
            subprocess.run(["say", "Vila"])

    def start_timer(self):
        if not self.running:
            self.running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            if not self.is_break:
                self.activate_dnd()
                self.status_label.config(text="Status: Arbete")
                self.label.config(text="Fokusera")
                self.play_sound("start")
                self.seconds_left = WORK_MINUTES * 60
            else:
                self.status_label.config(text="Status: Paus")
                self.label.config(text="Lång paus")
                if self.pomodoro_count % POMODOROS_BEFORE_LONG_BREAK == 0:
                    self.play_sound("long_break")
                    self.seconds_left = LONG_BREAK * 60
                else:
                    self.play_sound("short_break")
                    self.status_label.config(text="Status: Paus")
                    self.label.config(text="Kort paus!")
                    self.seconds_left = SHORT_BREAK * 60

            threading.Thread(target=self.countdown).start()

    def stop_timer(self):
        self.running = False
        self.deactivate_dnd()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.label.config(text="25:00")
        self.status_label.config(text="Status: Stoppad")
        self.seconds_left = WORK_MINUTES * 60
        self.is_break = False
        self.pomodoro_count = 0

    def countdown(self):
        while self.seconds_left > 0 and self.running:
            mins, secs = divmod(self.seconds_left, 60)
            time_str = f"{mins:02d}:{secs:02d}"
            self.label.config(text=time_str)
            time.sleep(1)
            self.seconds_left -= 1

        if self.running and self.remaining_time == 0:
            self.running = False
            self.stop_button.config(state=tk.DISABLED)
            self.start_button.config(state=tk.NORMAL)

            if not self.is_break:
                self.pomodoro_count += 1
                self.is_break = True
                self.status_label.config(text="Status: Klar med arbete")
                self.deactivate_dnd()
                self.start_button.config(state=tk.NORMAL)
                self.label.config(text="Paus!")

            if self.pomodoro_count % 4 == 0:
               self.break_type = "long"
               self.remaining_time = 15 * 60  # 15 minuter
               self.status_label.config(text="Status: Lång paus!")
               self.label.config(text="Lång paus!")
            else:
               self.break_type = "short"
               self.remaining_time = 5 * 60  # 5 minuter
               self.status_label.config(text="Status: Paus")
               self.label.config(text="Kort paus!")

        else:
            self.is_break = False
            self.status_label.config(text="Status: Klar med paus")
            self.label.config(text="Redo")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    

root = tk.Tk() 
app = PomodoroApp(root)
root.mainloop()