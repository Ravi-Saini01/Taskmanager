# Taskmanager
A modern and responsive Task Manager GUI built with Tkinter, ttkbootstrap, and psutil, mimicking the Windows Task Manager experience with advanced features like CPU monitoring, disk usage, theme switching, process control, CSV export, and system tray minimization.

✨ Features
🎛️ Live Process View

Separate views for foreground apps and background processes.

Displays PID, name, CPU %, memory %, status, and disk read usage.

🌡️ System Usage Monitor

Real-time display of CPU and memory usage.

🌓 Light/Dark Theme Toggle

Seamless switch between light (flatly) and dark (darkly) modes.

🔍 Search Filter

Quickly locate specific processes by name.

⚙️ Process Management

Launch new processes via command.

Kill running processes by entering their PID.

📋 Process Details Panel

Displays memory, parent PID, threads, executable path, and disk read data.

📂 Export to CSV

Save current process data to a .csv file.

🧲 System Tray Integration

Minimize to tray with icon and menu options to restore or exit.

📦 Dependencies
Ensure you have the following Python packages installed:

pip install psutil pystray pillow ttkbootstrap
▶️ How to Run

python task_manager.py
🧰 Technologies Used
Python 3

tkinter + ttkbootstrap – GUI Framework

psutil – System and process monitoring

pystray – System tray icon

PIL (Pillow) – Tray icon image rendering


🚀 Future Enhancements
CPU/memory graphs

Sorting by column

Thread view per process

Process priority changer

📄 License
MIT License. Feel free to use and modify this project.

🙌 Credits
Created by [Ravi Saini]. Inspired by the Windows Task Manager.
