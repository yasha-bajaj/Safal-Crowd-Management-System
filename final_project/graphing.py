import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import threading
import time
import requests
from datetime import datetime
import math
import random

class Speedometer(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.width = 300
        self.height = 300
        self.center_x = self.width / 2
        self.center_y = self.height / 2
        self.radius = min(self.width, self.height) * 0.4
        self.speed = 0
        self.max_speed = 100  # Maximum density value to display

        # Create canvas for speedometer
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg="black")
        self.canvas.pack()

        # Draw the speedometer
        self.create_speedometer()

    def create_speedometer(self):
        # Draw the outer circle
        self.canvas.create_oval(
            self.center_x - self.radius,
            self.center_y - self.radius,
            self.center_x + self.radius,
            self.center_y + self.radius,
            outline="white",
            width=2
        )

        # Draw speed labels
        for i in range(0, self.max_speed + 1, 20):
            angle = 180 + (i / self.max_speed) * 180
            x1 = self.center_x + (self.radius - 20) * math.cos(math.radians(angle))
            y1 = self.center_y + (self.radius - 20) * math.sin(math.radians(angle))
            x2 = self.center_x + self.radius * math.cos(math.radians(angle))
            y2 = self.center_y + self.radius * math.sin(math.radians(angle))
            self.canvas.create_line(x1, y1, x2, y2, fill="white", width=2)
            self.canvas.create_text(
                x1 - 10 * math.cos(math.radians(angle)),
                y1 - 10 * math.sin(math.radians(angle)),
                text=str(i),
                fill="white",
                font=("Arial", 10)
            )

        # Draw the needle
        self.needle = self.canvas.create_line(
            self.center_x,
            self.center_y,
            self.center_x + self.radius * math.cos(math.radians(180)),
            self.center_y + self.radius * math.sin(math.radians(180)),
            fill="red",
            width=3
        )

    def update_speed(self, speed):
        self.speed = speed
        angle = 180 + (self.speed / self.max_speed) * 180
        x = self.center_x + self.radius * math.cos(math.radians(angle))
        y = self.center_y + self.radius * math.sin(math.radians(angle))
        self.canvas.coords(self.needle, self.center_x, self.center_y, x, y)

class StatsDisplay:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Model Statistics")
        self.root.geometry("1200x800")
        
        # Store historical data
        self.occupancy_history = {
            'times': [],
            'occupancy': {}
        }
        
        self.setup_gui()
        self.done_sts = []
        # Start update threads
        threading.Thread(target=self.update_alerts, daemon=True).start()
        threading.Thread(target=self.update_stats, daemon=True).start()
        threading.Thread(target=self.update_console, daemon=True).start()
        threading.Thread(target=self.update_speedometer, daemon=True).start()

    def setup_gui(self):
        # Create main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for room stats
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel, weight=1)
        
        # Right panel for alerts, graph, and console
        right_panel = ttk.PanedWindow(main_container, orient=tk.VERTICAL)
        main_container.add(right_panel, weight=1)
        
        # Room Stats Section
        self.setup_room_stats(left_panel)
        
        # Upper right section (alerts and graph)
        upper_right = ttk.Frame(right_panel)
        right_panel.add(upper_right, weight=2)
        
        # Alerts Section
        self.setup_alerts(upper_right)
        
        # Occupancy Graph
        self.setup_occupancy_graph(upper_right)
        
        # Speedometer Section
        # self.setup_speedometer(left_panel)
        
        # Console Section
        self.setup_console(right_panel)

    def setup_speedometer(self, parent):
        # Speedometer Frame
        speedometer_frame = ttk.LabelFrame(parent, text="Density Speedometer")
        speedometer_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Create speedometer
        self.speedometer = Speedometer(speedometer_frame)
        self.speedometer.pack(pady=10, padx=10)

    def update_speedometer(self):
        while True:
            try:
                response = requests.get('http://localhost:9000/density')
                if response.ok:
                    density = float(response.text)
                    self.root.after(0, self.speedometer.update_speed, density)
            except Exception as e:
                print(f"Error fetching density data: {e}")
            time.sleep(1)

    def setup_console(self, parent):
        # Console Frame
        console_frame = ttk.LabelFrame(parent, text="Console Output")
        parent.add(console_frame, weight=1)
        
        # Console Text Widget
        self.console_text = tk.Text(console_frame, height=10, width=50, bg='black', fg='green')
        scrollbar = ttk.Scrollbar(console_frame, orient="vertical", command=self.console_text.yview)
        self.console_text.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        scrollbar.pack(side="right", fill="y")
        self.console_text.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

    def update_console(self):
        while True:
            try:
                response = requests.get('http://localhost:9000/console')
                if response.ok and response.text:
                    self.root.after(0, self.add_console_message, response.text)
            except Exception as e:
                print(f"Error fetching console data: {e}")
            time.sleep(1)

    def add_console_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console_text.insert('end', f"[{timestamp}] {message}\n")
        self.console_text.see('end')
        
        # Keep only the last 1000 lines
        line_count = int(self.console_text.index('end-1c').split('.')[0])
        if line_count > 1000:
            self.console_text.delete('1.0', '2.0')

    def setup_room_stats(self, parent):
        # Room Stats Header
        ttk.Label(parent, text="Room Statistics", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Create scrollable frame for room stats
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self.rooms_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Create window in canvas
        canvas.create_window((0, 0), window=self.rooms_frame, anchor="nw")
        
        # Configure scroll region when frame size changes
        self.rooms_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Store room frames
        self.room_frames = {}

    def setup_alerts(self, parent):
        # Alerts Header
        ttk.Label(parent, text="Recent Alerts", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Alerts Text Widget
        self.alerts_text = tk.Text(parent, height=10, width=50)
        self.alerts_text.pack(pady=10, padx=10, fill=tk.X)

    def setup_occupancy_graph(self, parent):
        # Graph Header
        ttk.Label(parent, text="Occupancy Trends", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def update_room_stats(self, room_data):
        # Clear existing room frames
        for widget in self.rooms_frame.winfo_children():
            widget.destroy()
        
        # Create new frames for each room
        for room_name, stats in room_data.items():
            # Room frame setup
            frame = ttk.LabelFrame(self.rooms_frame, text=f"Room {room_name}")
            frame.pack(pady=5, padx=10, fill=tk.X)
            
            # Occupancy info
            occupancy_frame = ttk.Frame(frame)
            occupancy_frame.pack(fill=tk.X, padx=5, pady=5)
            
            ttk.Label(occupancy_frame, text="Occupancy:").pack(side=tk.LEFT)
            occupancy_bar = ttk.Progressbar(
                occupancy_frame, 
                length=200,
                maximum=stats['capacity']
            )
            occupancy_bar['value'] = stats['current_occupancy']
            occupancy_bar.pack(side=tk.LEFT, padx=5)
            
            ttk.Label(
                occupancy_frame, 
                text=f"{stats['current_occupancy']}/{stats['capacity']}"
            ).pack(side=tk.LEFT)
            
            # Evacuation path
            if not room_name.startswith("Gate from"):
                ttk.Label(frame, text=f"Evacuation Path: {stats['evacuation_path']}").pack(
                    pady=2, padx=5, anchor='w'
                )
            
            # Safety status
            status_text = "⚠️ SMOKE DETECTED" if stats['smoke_detected'] else "✅ Clear"
            status_color = 'red' if stats['smoke_detected'] else 'green'
            
            status_label = ttk.Label(
                frame,
                text=f"Status: {status_text}",
                foreground=status_color
            )
            status_label.pack(pady=2, padx=5, anchor='w')

    def update_alerts(self):
        while True:
            try:
                response = requests.get('https://internal-smoothly-jaybird.ngrok-free.app/alert')
                if response.ok and response.text:
                    message, st = response.text.split("<--->")
                    if st in self.done_sts:
                        time.sleep(5)
                        continue
                    self.done_sts.append(st)
                    self.root.after(0, self.add_alert, message)
            except Exception as e:
                print(f"Error fetching alerts: {e}")
            time.sleep(5)

    def add_alert(self, alert_text):    
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.alerts_text.insert('1.0', f"[{timestamp}] {alert_text}\n")
        self.alerts_text.see('1.0')

    def draw_graph(self):
        self.ax.clear()
        
        for room_name, occupancy_data in self.occupancy_history['occupancy'].items():
            self.ax.plot(
                self.occupancy_history['times'],
                occupancy_data,
                label=f"Room {room_name}",
                marker='o'
            )
        
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Occupancy')
        self.ax.set_title('Recent Room Occupancy Trends')
        self.ax.legend()
        self.ax.tick_params(axis='x', rotation=45)
        self.fig.tight_layout()
        
        self.canvas.draw()
    
    def get_room_data(self):
        resp = requests.get('http://localhost:9000/rooms_data')
        return resp.json()

    def update_stats(self):
        while True:
            try:
                room_data = self.get_room_data()
                
                # Update room stats
                self.root.after(0, self.update_room_stats, room_data)
                
                # Update occupancy history
                for room_name, stats in room_data.items():
                    if room_name not in self.occupancy_history['occupancy']:
                        if len(list(self.occupancy_history['occupancy'].keys())) != 0:
                            self.occupancy_history['occupancy'][room_name] = [0]*(len(self.occupancy_history["occupancy"][next(i for i in self.occupancy_history["occupancy"])])-1)
                        else:
                            self.occupancy_history['occupancy'][room_name] = []
                    self.occupancy_history['occupancy'][room_name].append(stats['current_occupancy'])
                
                # Get current time
                current_time = datetime.now().strftime("%H:%M:%S")
                self.occupancy_history['times'].append(current_time)
                
                # Keep only last 10 data points
                if len(self.occupancy_history['times']) > 10:
                    self.occupancy_history['times'].pop(0)
                    for room in self.occupancy_history['occupancy'].values():
                        room.pop(0)
                
                # Update graph
                self.root.after(0, self.draw_graph)
                
                time.sleep(1)
            except:
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = StatsDisplay(root)
    root.mainloop()