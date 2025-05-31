import csv
import psutil
import subprocess
import threading
import time
import os
from tkinter import messagebox, filedialog
from PIL import Image, ImageDraw
from pystray import Icon as TrayIcon, MenuItem as item
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class TaskManager(tb.Window):
    def __init__(self):
        self.current_theme = "darkly"
        super().__init__(themename=self.current_theme)
        self.title("Python Task Manager")
        self.geometry("1000x700")
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        self.gui_apps = {"explorer.exe", "chrome.exe", "Spotify.exe", "Code.exe", "Taskmgr.exe"}

        self.system_label = tb.Label(self, text="CPU: 0% | Memory: 0%", font=("Helvetica", 12))
        self.system_label.pack(anchor=W, padx=10, pady=(10, 0))

        self.theme_button = tb.Button(self, text="☀️", command=self.toggle_theme, bootstyle=(LINK, OUTLINE))
        self.theme_button.pack(anchor=E, padx=10, pady=(0, 5))

        search_frame = tb.Frame(self)
        search_frame.pack(fill=X, padx=10)

        self.search_var = tb.StringVar()
        tb.Label(search_frame, text="Search:").pack(side=LEFT)
        tb.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=LEFT, padx=5)
        tb.Button(search_frame, text="Refresh", command=self.update_processes, bootstyle=INFO).pack(side=LEFT)

        self.apps_label = tb.Label(self, text="Apps (0)", font=("Helvetica", 11, "bold"))
        self.apps_label.pack(anchor=W, padx=10)
        self.apps_tree = self.create_treeview()

        self.bg_label = tb.Label(self, text="Background processes (0)", font=("Helvetica", 11, "bold"))
        self.bg_label.pack(anchor=W, padx=10)
        self.bg_tree = self.create_treeview()

        tb.Label(self, text="Process Details", font=("Helvetica", 11, "bold")).pack(anchor=W, padx=10)
        self.detail_text = tb.Text(self, height=7, font=("Courier", 10), relief="flat")
        self.detail_text.pack(fill=X, padx=10)
        self.update_text_widget_theme()

        action_frame = tb.Labelframe(self, text="Actions", padding=10)
        action_frame.pack(fill=X, padx=10, pady=5)

        self.pid_var = tb.StringVar()
        tb.Label(action_frame, text="Kill PID:").pack(side=LEFT)
        tb.Entry(action_frame, textvariable=self.pid_var, width=10).pack(side=LEFT)
        tb.Button(action_frame, text="Kill", command=self.kill_process, bootstyle=DANGER).pack(side=LEFT, padx=5)
        tb.Button(action_frame, text="Export CSV", command=self.export_to_csv, bootstyle=SUCCESS).pack(side=LEFT, padx=5)

        launch_frame = tb.Labelframe(self, text="Launch New Process", padding=10)
        launch_frame.pack(fill=X, padx=10, pady=5)

        self.cmd_var = tb.StringVar()
        tb.Label(launch_frame, text="Command:").pack(side=LEFT)
        tb.Entry(launch_frame, textvariable=self.cmd_var, width=40).pack(side=LEFT)
        tb.Button(launch_frame, text="Start", command=self.launch_process, bootstyle=SECONDARY).pack(side=LEFT, padx=5)

        self.tray_icon = None
        self.icon_image = self.create_image()

        self.init_cpu_counters()
        self.after(1000, self.update_processes)
        self.after(3000, self.update_system_stats)
        self.after(5000, self.auto_refresh)

    def create_treeview(self):
        tree = tb.Treeview(self, columns=("PID", "Name", "Status", "CPU %", "Memory %", "Disk Read MB"), show='headings', height=7, bootstyle=PRIMARY)
        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor='center')
        tree.pack(fill=BOTH, padx=10, pady=2)
        tree.bind("<<TreeviewSelect>>", self.show_process_details)
        return tree

    def toggle_theme(self, *_):
        self.current_theme = "flatly" if self.current_theme == "darkly" else "darkly"
        self.style.theme_use(self.current_theme)
        self.theme_button.config(text="🌙" if self.current_theme == "flatly" else "☀️")
        self.update_text_widget_theme()

    def update_text_widget_theme(self):
        dark = self.current_theme == "darkly"
        self.detail_text.config(bg="#2b2b2b" if dark else "white", fg="white" if dark else "black")

    def update_system_stats(self):
        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory().percent
        self.system_label.config(text=f"CPU: {cpu}% | Memory: {memory}%")
        self.after(3000, self.update_system_stats)

    def init_cpu_counters(self):
        for proc in psutil.process_iter():
            try:
                proc.cpu_percent(interval=None)
            except Exception:
                pass

    def update_processes(self):
        def fetch():
            search = self.search_var.get().lower()
            apps, bg = [], []

            for proc in psutil.process_iter(['pid', 'name', 'status']):
                try:
                    name = proc.info['name']
                    if not name or name.lower() == "system idle process":
                        continue
                    if search and search not in name.lower():
                        continue
                    cpu = proc.cpu_percent(interval=None)
                    mem = round(proc.memory_percent(), 1)
                    try:
                        disk = proc.io_counters().read_bytes / (1024 ** 2)
                    except Exception:
                        disk = 0.0
                    row = (proc.pid, name, proc.info['status'], round(cpu, 1), mem, f"{disk:.2f}")
                    (apps if name in self.gui_apps else bg).append(row)
                except Exception:
                    continue

            def update_tree(tree, data, label, label_widget):
                tree.delete(*tree.get_children())
                for item in data:
                    tree.insert('', 'end', values=item)
                label_widget.config(text=f"{label} ({len(data)})")

            self.after(0, lambda: update_tree(self.apps_tree, apps, "Apps", self.apps_label))
            self.after(0, lambda: update_tree(self.bg_tree, bg, "Background processes", self.bg_label))

        threading.Thread(target=fetch, daemon=True).start()

    def auto_refresh(self):
        self.update_processes()
        self.after(5000, self.auto_refresh)

    def kill_process(self):
        try:
            pid = int(self.pid_var.get())
            proc = psutil.Process(pid)
            proc.terminate()
            proc.wait(timeout=2)
            messagebox.showinfo("Success", f"Terminated PID {pid}")
            self.update_processes()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_to_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path:
            return
        try:
            with open(path, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["PID", "Name", "Status", "CPU %", "Memory %", "Disk Read MB"])
                for tree in (self.apps_tree, self.bg_tree):
                    for item in tree.get_children():
                        writer.writerow(tree.item(item)["values"])
            messagebox.showinfo("Exported", f"Saved to {path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def launch_process(self):
        cmd = self.cmd_var.get()
        if not cmd:
            return messagebox.showwarning("Warning", "Enter a command.")
        try:
            subprocess.Popen(cmd.split())
            messagebox.showinfo("Launched", f"Started: {cmd}")
            self.update_processes()
        except Exception as e:
            messagebox.showerror("Launch Error", str(e))

    def show_process_details(self, event):
        tree = event.widget
        selected = tree.selection()
        if not selected:
            return
        pid = int(tree.item(selected[0], "values")[0])
        try:
            proc = psutil.Process(pid)
            info = f"""
PID: {proc.pid}
Name: {proc.name()}
Status: {proc.status()}
Threads: {proc.num_threads()}
Parent PID: {proc.ppid()}
Executable: {proc.exe()}
Memory RSS: {proc.memory_info().rss // (1024 * 1024)} MB
Start Time: {time.ctime(proc.create_time())}
Disk Read: {proc.io_counters().read_bytes / (1024 ** 2):.2f} MB
""".strip()
            self.detail_text.delete("1.0", "end")
            self.detail_text.insert("end", info)
        except Exception as e:
            self.detail_text.delete("1.0", "end")
            self.detail_text.insert("end", str(e))

    def minimize_to_tray(self):
        self.withdraw()
        if not self.tray_icon:
            menu = (item('Restore', self.restore_from_tray), item('Exit', self.exit_app))
            self.tray_icon = TrayIcon("TaskManager", self.icon_image, "Task Manager", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def restore_from_tray(self, *_):
        self.deiconify()
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

    def exit_app(self, *_):
        self.destroy()
        if self.tray_icon:
            self.tray_icon.stop()

    def create_image(self):
        img = Image.new('RGB', (64, 64), "black")
        d = ImageDraw.Draw(img)
        d.rectangle([16, 16, 48, 48], fill="blue", outline="white")
        return img

if __name__ == "__main__":
    app = TaskManager()
    app.mainloop()
