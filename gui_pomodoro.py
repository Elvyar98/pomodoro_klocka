import tkinter as tk
from tkinter import messagebox
import subprocess
import time
import threading
import json
from datetime import date
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import timedelta

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

        self.stats_header = tk.Label(self.window, text="Statistik", font=("Helvetica", 12, "bold"))
        self.stats_header.pack()

        self.stats_label = tk.Label(self.window, text="Inga data ännu", font=("Helvetica", 10))
        self.stats_label.pack(pady=5)

        self.show_statistics()

        self.weekly_button = tk.Button(self.window, text="Visa veckostatistik", command=self.show_weekly_stats)
        self.weekly_button.pack(pady=5)

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
                self.update_statistics()
                self.show_statistics()
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
   
    def update_statistics(self):
        today = str(date.today())
        stats_file = "stats.json"

        if os.path.exists(stats_file):
            with open(stats_file, "r") as f:
                stats=json.load(f)
        else:
            stats={}
        if today not in stats:
            stats[today]={"pomodoros": 0, "minutes": 0}

        stats[today]["pomodoros"] +=1
        stats[today]["minutes"] +=25

        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2)      
    
    def show_statistics(self):
        stats_file="stats.json"

        if not os.path.exists(stats_file):
            self.stats_label.config(text="Ingen statistik tillgänglig ännu.")
            return
        with open(stats_file, "r") as f:
            stats=json.load(f)

        today = str(date.today())
        today_stats = stats.get(today, {})
        today_poms = today_stats.get("pomodoros", 0)
        today_minutes = today_stats.get("minutes", 0)

        total_poms = sum(day.get("pomodoros", 0) for day in stats.values())
        total_minutes = sum(day.get("minutes", 0) for day in stats.values())

        text = (
            f"Idag: {today_poms} pomodoros ({today_minutes} min)\n"
            f"Totalt: {total_poms} pomodoros ({total_minutes} min)"
         )
        self.stats_label.config(text=text)    
    
    def show_stats_over_time(self, days_back=28, show_minutes=False):
      stats_file = "stats.json"
      if not os.path.exists(stats_file):
        return

      with open(stats_file, "r") as f:
        stats = json.load(f)

      today = date.today()
      days = [(today - timedelta(days=i)).isoformat() for i in range(days_back - 1, -1, -1)]

      values = [stats.get(day, {}).get("minutes" if show_minutes else "pomodoros", 0) for day in days]

      def average_for_group(group_days):
        group_values = [stats.get(day, {}).get("pomodoros", 0) for day in group_days]
        return sum(group_values) / len(group_values) if group_values else 0

      avg_week = average_for_group(days[-7:]) if len(days) >= 7 else 0
      avg_month = average_for_group(days[-30:]) if len(days) >= 30 else 0
      avg_year = average_for_group(days[-365:]) if len(days) >= 365 else 0

      chart_window = tk.Toplevel(self.window)
      chart_window.title("Statistik över tid")

      fig, ax = plt.subplots(figsize=(10, 5))
      x = range(len(days))
      ax.bar(x, values, color="#FF5733", label="Pomodoros per dag")

      ax.axhline(y=avg_week, color="blue", linestyle="--", label=f"Snitt (7d): {avg_week:.1f}")
      ax.axhline(y=avg_month, color="green", linestyle="--", label=f"Snitt (30d): {avg_month:.1f}")
      ax.axhline(y=avg_year, color="gray", linestyle="--", label=f"Snitt (365d): {avg_year:.1f}")

      ax.set_title("Pomodoros per dag")
      ax.set_ylabel("Antal")
      ax.set_xticks(x[::max(1, len(x)//10)])
      ax.set_xticklabels([days[i][5:] for i in x][::max(1, len(x)//10)], rotation=45)
      ax.legend()
      fig.tight_layout()

      canvas = FigureCanvasTkAgg(fig, master=chart_window)
      canvas.draw()
      canvas.get_tk_widget().pack()


 
root = tk.Tk() 
app = PomodoroApp(root)
root.mainloop()

