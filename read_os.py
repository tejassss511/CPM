
import tkinter as tk
from tkinter import ttk
import psutil
import platform
import socket
import speedtest
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import deque
import threading
import time

# ---------------- WINDOW SETUP ---------------- #
root = tk.Tk()
root.title("Advanced System Monitor")
root.geometry("1200x800")
root.configure(bg="#0f172a")

# ---------------- STYLE ---------------- #
style = ttk.Style()
style.theme_use("clam")

# ---------------- TITLE ---------------- #
header = tk.Label(
    root,
    text="ADVANCED SYSTEM MONITOR DASHBOARD",
    font=("Arial", 22, "bold"),
    fg="cyan",
    bg="#0f172a"
)
header.pack(pady=10)

# ---------------- MAIN FRAME ---------------- #
main_frame = tk.Frame(root, bg="#0f172a")
main_frame.pack(fill="both", expand=True)

# ---------------- LEFT PANEL ---------------- #
left_panel = tk.Frame(main_frame, bg="#111827", width=350)
left_panel.pack(side="left", fill="y", padx=10, pady=10)

# ---------------- RIGHT PANEL ---------------- #
right_panel = tk.Frame(main_frame, bg="#111827")
right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# ---------------- SYSTEM INFO LABELS ---------------- #
info_title = tk.Label(
    left_panel,
    text="SYSTEM INFORMATION",
    font=("Arial", 16, "bold"),
    fg="cyan",
    bg="#111827"
)
info_title.pack(pady=10)

info_text = tk.Text(
    left_panel,
    height=35,
    width=45,
    bg="#1e293b",
    fg="white",
    font=("Consolas", 10),
    relief="flat"
)
info_text.pack(padx=10, pady=10)

# ---------------- GRAPH SETUP ---------------- #
fig = Figure(figsize=(8, 6), dpi=100)
fig.patch.set_facecolor('#111827')

cpu_ax = fig.add_subplot(311)
ram_ax = fig.add_subplot(312)
net_ax = fig.add_subplot(313)

canvas = FigureCanvasTkAgg(fig, master=right_panel)
canvas.get_tk_widget().pack(fill="both", expand=True)

# ---------------- DATA STORAGE ---------------- #
cpu_data = deque([0]*50, maxlen=50)
ram_data = deque([0]*50, maxlen=50)
download_data = deque([0]*50, maxlen=50)
upload_data = deque([0]*50, maxlen=50)

# ---------------- NETWORK TRACKING ---------------- #
last_recv = psutil.net_io_counters().bytes_recv
last_sent = psutil.net_io_counters().bytes_sent

# ---------------- SYSTEM INFO FUNCTION ---------------- #
def get_system_info():
    info_text.delete(1.0, tk.END)

    uname = platform.uname()

    info = f"""
SYSTEM        : {uname.system}
NODE NAME     : {uname.node}
RELEASE       : {uname.release}
VERSION       : {uname.version}
MACHINE       : {uname.machine}
PROCESSOR     : {uname.processor}

---------------- CPU ----------------
Physical Cores : {psutil.cpu_count(logical=False)}
Total Cores    : {psutil.cpu_count(logical=True)}
CPU Usage      : {psutil.cpu_percent()}%

---------------- RAM ----------------
Total RAM      : {psutil.virtual_memory().total / (1024**3):.2f} GB
Available RAM  : {psutil.virtual_memory().available / (1024**3):.2f} GB
Used RAM       : {psutil.virtual_memory().used / (1024**3):.2f} GB
RAM Usage      : {psutil.virtual_memory().percent}%

---------------- STORAGE ----------------
"""

    partitions = psutil.disk_partitions()

    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)

            info += f"""
Drive           : {partition.device}
File System     : {partition.fstype}
Total Size      : {usage.total / (1024**3):.2f} GB
Used            : {usage.used / (1024**3):.2f} GB
Free            : {usage.free / (1024**3):.2f} GB
Usage           : {usage.percent}%
"""

        except:
            pass

    battery = psutil.sensors_battery()

    info += "\n---------------- BATTERY ----------------\n"

    if battery:
        info += f"Battery Percentage : {battery.percent}%\n"
        info += f"Charging           : {battery.power_plugged}\n"
    else:
        info += "No Battery Detected\n"

    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)

    info += f"\n---------------- NETWORK ----------------\n"
    info += f"Hostname : {hostname}\n"
    info += f"IP Addr  : {ip}\n"

    info_text.insert(tk.END, info)

# ---------------- SPEED TEST FUNCTION ---------------- #
def run_speed_test():
    speed_label.config(text="Running Internet Speed Test...")

    def test():
        try:
            st = speedtest.Speedtest()

            download_speed = st.download() / 1_000_000
            upload_speed = st.upload() / 1_000_000
            ping = st.results.ping

            result = f"Download: {download_speed:.2f} Mbps | Upload: {upload_speed:.2f} Mbps | Ping: {ping:.2f} ms"

            speed_label.config(text=result)

        except Exception as e:
            speed_label.config(text=f"Error: {e}")

    threading.Thread(target=test).start()

# ---------------- LIVE GRAPH UPDATE ---------------- #
def update_graphs():
    global last_recv, last_sent

    # CPU and RAM
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent

    cpu_data.append(cpu)
    ram_data.append(ram)

    # Network Speed Monitoring
    current = psutil.net_io_counters()

    download_speed = (current.bytes_recv - last_recv) / 1024
    upload_speed = (current.bytes_sent - last_sent) / 1024

    last_recv = current.bytes_recv
    last_sent = current.bytes_sent

    download_data.append(download_speed)
    upload_data.append(upload_speed)

    # Clear Graphs
    cpu_ax.clear()
    ram_ax.clear()
    net_ax.clear()

    # Styling
    for ax in [cpu_ax, ram_ax, net_ax]:
        ax.set_facecolor('#1e293b')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')

    # CPU Graph
    cpu_ax.plot(cpu_data)
    cpu_ax.set_title('CPU Usage (%)', color='cyan')
    cpu_ax.set_ylim(0, 100)

    # RAM Graph
    ram_ax.plot(ram_data)
    ram_ax.set_title('RAM Usage (%)', color='cyan')
    ram_ax.set_ylim(0, 100)

    # Network Graph
    net_ax.plot(download_data, label='Download KB/s')
    net_ax.plot(upload_data, label='Upload KB/s')
    net_ax.set_title('Internet Speed Monitor', color='cyan')
    net_ax.legend()

    canvas.draw()

    get_system_info()

    root.after(1000, update_graphs)

# ---------------- SPEED TEST BUTTON ---------------- #
speed_frame = tk.Frame(left_panel, bg="#111827")
speed_frame.pack(pady=10)

speed_button = tk.Button(
    speed_frame,
    text="Run Internet Speed Test",
    command=run_speed_test,
    bg="cyan",
    fg="black",
    font=("Arial", 11, "bold"),
    padx=10,
    pady=5
)

speed_button.pack()

speed_label = tk.Label(
    left_panel,
    text="",
    fg="white",
    bg="#111827",
    font=("Arial", 10)
)

speed_label.pack(pady=10)

# ---------------- START ---------------- #
update_graphs()

root.mainloop()


