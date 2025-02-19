import customtkinter as tk
import tkinter as stk
import os
import sys
import subprocess
import flask
import time
import numpy as np
import requests
from tkinter import ttk, messagebox, filedialog
import cv2
from PIL import Image, ImageTk
import threading
import traceback
from ultralytics import YOLO
from collections import deque, defaultdict
from typing import List, Set, Dict, Optional, Tuple

class Node:
    def __init__(self, name: str, capacity: int, is_outer = False):
        self.name = name
        self.near_nodes: List[Node] = []
        self.is_outer = is_outer
        self.capacity = capacity
        self.current_occupancy = 0
    
    def add_connection(self, node: 'Node') -> None:
        """Add a bidirectional connection between nodes"""
        if node not in self.near_nodes:
            self.near_nodes.append(node)
            node.near_nodes.append(self)
    
    def get_occupancy_rate(self) -> float:
        """Return the current occupancy rate as a percentage"""
        return (self.current_occupancy / self.capacity * 100) if self.capacity > 0 else 100
    
    def is_viable_route(self) -> bool:
        """Check if the node is viable for emergency routing"""
        return self.get_occupancy_rate() <= 70
    
    def __repr__(self) -> str:
        return f"Node({self.name}, {self.current_occupancy}/{self.capacity})"
    

def find_best_paths(start_node: Node, outer_nodes: Set[Node]) -> Dict[Node, Tuple[List[Node], bool]]:
    """
    Find the shortest paths from start_node to all outer nodes using BFS.
    Returns a dictionary mapping each outer node to (path, is_high_occupancy_path).
    """
    queue = deque([(start_node, [start_node])])
    visited = {start_node}
    paths: Dict[Node, Tuple[List[Node], bool]] = {}
    high_occupancy_paths: Dict[Node, List[Node]] = {}
    
    while queue and (len(paths) + len(high_occupancy_paths)) < len(outer_nodes):
        current_node, current_path = queue.popleft()
        
        # If we found an outer node
        if current_node in outer_nodes:
            path_has_high_occupancy = any(
                not node.is_viable_route() 
                for node in current_path[1:-1]  # Exclude start and end nodes
            )
            
            if path_has_high_occupancy:
                if current_node not in paths:  # Only store if we don't have a better path
                    high_occupancy_paths[current_node] = current_path
            else:
                paths[current_node] = (current_path, False)
                if current_node in high_occupancy_paths:
                    del high_occupancy_paths[current_node]
            continue
        
        # Explore neighbors
        for neighbor in current_node.near_nodes:
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = current_path + [neighbor]
                queue.append((neighbor, new_path))
    
    # If we have no viable paths, use high occupancy paths
    if not paths and high_occupancy_paths:
        return {node: (path, True) for node, path in high_occupancy_paths.items()}
    
    return paths

def get_optimal_path(start_node: Node, outer_nodes: Set[Node]) -> Tuple[Optional[List[Node]], bool]:
    """
    Find the shortest viable path to any outer node.
    Returns (path, is_high_occupancy_path). Returns (None, False) if no path found.
    """
    paths = find_best_paths(start_node, outer_nodes)
    if not paths:
        return None, False
    
    # First try to find the shortest path among viable routes
    viable_paths = [(path, high_occ) for path, high_occ in paths.values() if not high_occ]
    if viable_paths:
        return min(viable_paths, key=lambda x: len(x[0]))
    
    # If no viable paths exist, use the shortest high-occupancy path
    return min(paths.values(), key=lambda x: len(x[0]))

class DraggableRectangle:
    def __init__(self, canvas: stk.Canvas, text, *args, **kwargs):
        self.canvas = canvas
        self.rect = self.canvas.create_rectangle(*args, **kwargs)
        
        # Bind mouse events
        self.canvas.tag_bind(self.rect, '<ButtonPress-1>', self.on_button_press)
        self.canvas.tag_bind(self.rect, '<B1-Motion>', self.on_mouse_drag)
        self.canvas.tag_bind(self.rect, '<ButtonRelease-1>', self.on_button_release)

        coords = self.canvas.coords(self.rect)
        self.start_x = (coords[0] + coords[2])/2
        self.start_y = (coords[1] + coords[3])/2
        self.text = self.canvas.create_text(self.start_x, self.start_y, text=text, fill="white", font=("Arial", 12))

    def on_button_press(self, event):
        # Store the starting position
        self.start_x = event.x
        self.start_y = event.y

    def on_mouse_drag(self, event):
        # Calculate the distance moved
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        
        # Move the rectangle and the text
        self.canvas.move(self.rect, dx, dy)
        self.canvas.move(self.text, dx, dy)
        
        # Update the starting position
        self.start_x = event.x
        self.start_y = event.y

    def on_button_release(self, event):
        # Optionally handle button release if needed
        pass
class _Point:
    x = 0
    y = 0
    def __init__(self, x, y):
        self.x = x
        self.y = y
class Line:
    def __init__(self, canvas: stk.Canvas, circle1: _Point, circle2: _Point):
        self.canvas = canvas
        self.circle1 = circle1
        self.circle2 = circle2
        self.line = self.canvas.create_line(circle1.x, circle1.y, circle2.x, circle2.y, fill="white")
    def update(self, *new_values):
        self.canvas.coords(self.line, *new_values)
class NodeGraph:
    def __init__(self):
        self.nodes: List[Node] = []
        self.lock = threading.Lock()  # Lock for thread-safe operations

    def add_node(self, node: Node):
        with self.lock:
            self.nodes.append(node)

    def add_connection(self, node1: Node, node2: Node):
        with self.lock:
            node1.add_connection(node2)

    
    def find_optimal_path(self, start_node):
        return get_optimal_path(start_node, [node for node in self.nodes if node.is_outer])

class CrowdManagementApp:
    def __init__(self, root: tk.CTk):

        self.root = root
        self.root.title("Crowd Management System")
        self.rooms = {}
        self.app = flask.Flask(__name__)

        self.CONSOLE_ALERTS = ""

        # self.last_active_smoke_warn = False

        @self.app.route("/frame", methods=["POST"])
        def frame():
            req = dict(flask.request.json)
            _, buffer = cv2.imencode(".jpeg", self.current_frame[req["room"]])
            response = requests.post(
                "https://internal-smoothly-jaybird.ngrok-free.app/flAccess",
                files={'files': buffer.tobytes()},
                data={"prompt": req["prompt"]},
            )
            
            print(response.text)
            return response.text

        @self.app.route("/rooms_data")
        def rooms_data():
            import json
            return json.dumps({room: {"current_occupancy": self.rooms[room]["current_occupency"], "capacity": self.rooms[room]["capacity"], "evacuation_path": self.rooms[room]["evacuation_path"], "smoke_detected": False} for room in self.rooms}), 200

        @self.app.route("/console")
        def console():
            con = self.CONSOLE_ALERTS
            self.CONSOLE_ALERTS = ""
            return con, 200
        
        threading.Thread(target=lambda: self.app.run(port=9000), daemon=True).start()
        self.processes: List[subprocess.Popen] = []
        self.processes.append(subprocess.Popen(sys.executable+" "+os.path.join(os.path.dirname(__file__), "chatgui.py")))
        self.processes.append(subprocess.Popen(sys.executable+" "+os.path.join(os.path.dirname(__file__), "graphing.py")))
        self.gates_look = []
        self.gradient = {}
        self.node_graph = NodeGraph()
        self.new_gradient = True
        threading.Thread(target=self.calc_evacuation_route, daemon=True).start()
        self.current_frame = {}
        self.connections = []
        self.room_frames = defaultdict(lambda: {})
        self.video_streams = {}  # Dictionary to store video streams for each room
        self.root.wm_attributes("-topmost", True)
        self.root.after(2000, lambda: self.root.wm_attributes("-topmost", False))
        self.running = True
        self.scripts = {
            "Heatmap": None,
            "People Count": None,
            "Aggression Map": None,
            "Evacuation Map": None
        }
        self.analysis_running = {}  # Track which analyses are running
        self.model = None  # YOLO model instance

        ttk.Style().configure("TNotebook", background="#202120", foreground='#202120')

        # Tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Layout tab
        self.layout_tab = tk.CTkFrame(self.notebook)
        self.notebook.add(self.layout_tab, text="Layout")
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)

        # Create frames for layout tab
        self.setup_layout_tab()

        self.current_stream = "layout" # default stream is layout which should be none.

        # Initialize other tabs
        self.tabs = {}
        self.video_labels = {}
        self.create_analysis_tabs()
        threading.Thread(target=self.collect_info, daemon=True).start()

        self.__add_test_room("A", True)

    
    def collect_info(self):
        DELIMTER = '<--->'

        INFO_PROMPTS = [
            "is there fire.",
            'is there a stampeed.',
            'how many people.',
            'is there danger.',
            'is there a gun.',
            'is there a knife'
        ]
        while True:
            try:
                for room_name in self.rooms:
                    if not room_name in self.current_frame:
                        continue
                    _, buffer = cv2.imencode(".jpeg", self.current_frame[room_name])
                    prompt = DELIMTER.join(INFO_PROMPTS)
                    response = requests.post(
                        "https://internal-smoothly-jaybird.ngrok-free.app/flAccess",
                        files={'files': buffer.tobytes()},
                        data={"prompt": prompt},
                    )
        
                    for i, res in enumerate(response.text.split(DELIMTER)):
                        if (i == 0):
                            if ('yes' == res.upper()):
                                print(f"SMOKE DETECTED IN ROOM: {room_name}")
                                requests.post("https://internal-smoothly-jaybird.ngrok-free.app/add_alert", json={"message": "Fire is suspected in Room: " + room_name})
                        if i == 2:
                            try:
                                self.rooms[room_name]["current_occupency"] = int(res)
                            except:
                                pass
                            if self.rooms[room_name]["current_occupency"] >= (0.7*self.rooms[room_name]["capacity"]):
                                requests.post("https://internal-smoothly-jaybird.ngrok-free.app/add_alert", json={"message": "High Density in Room: " + room_name})
                        self.CONSOLE_ALERTS += f"{room_name} {INFO_PROMPTS[i]}: {res}\n"
            except RuntimeError:
                print(traceback.format_exc())
            time.sleep(0.1)
    
    def __add_test_room(self, name, is_outer):
        name = name
        width = 100
        length = 100
        self.rooms[name] = {
            "width": width,
            "length": length,
            "area": width * length,
            "capacity": 100,
            "current_occupency": 0,
            "evacuation_path": ""
        }

        # Create a rectangle with the given width and height on the map canvas
        room_id = len(self.rooms)
        x1 = 10 + 100 * (room_id - 1)  # Adjust positioning as needed
        y1 = 10
        x2 = x1 + width
        y2 = y1 + length
        
        self.rooms[name].update({"drag_ref": DraggableRectangle(self.map_canvas, name, x1, y1, x2, y2, fill="#47474a", outline="black")})

        self.update_video_grid()
        
        new_node = Node(name, self.rooms[name]["capacity"], is_outer=is_outer)  # Assuming you have a capacity attribute
        self.node_graph.add_node(new_node)
    
    def format_evac_path(self, path):
        try:
            final = " -> ".join([node.name for node in path[0]])
            return final + " -> exit"
        except:
            return "No Evac Route Found."
    
    def calc_evacuation_route(self):
        while True:
            for node in self.node_graph.nodes:
                if (node.name.startswith("Gate from")):
                    continue
                self.rooms[node.name]["evacuation_path"] = self.format_evac_path(self.node_graph.find_optimal_path(node))
            time.sleep(4)
    
    def on_tab_change(self, *_, **__):
        selected_tab_index = self.notebook.select()
        self.current_stream = self.notebook.tab(selected_tab_index, "text")
    
    def setup_layout_tab(self):
        # Input frame
        self.input_frame = tk.CTkFrame(self.layout_tab)
        self.input_frame.pack(side=tk.LEFT, fill=tk.BOTH)

        tk.CTkLabel(self.input_frame, text="Add Room", font=("Arial", 14)).pack(pady=5)
        
        tk.CTkLabel(self.input_frame, text="Room Name:").pack()
        self.room_name_entry = tk.CTkEntry(self.input_frame)
        self.room_name_entry.pack()

        tk.CTkLabel(self.input_frame, text="Width (m):").pack()
        self.room_width_entry = tk.CTkEntry(self.input_frame)
        self.room_width_entry.pack()

        tk.CTkLabel(self.input_frame, text="Length (m):").pack()
        self.room_length_entry = tk.CTkEntry(self.input_frame)
        self.room_length_entry.pack()

        tk.CTkLabel(self.input_frame, text="Capacity (number of people):").pack()
        self.room_capacity_entry = tk.CTkEntry(self.input_frame)
        self.room_capacity_entry.pack()

        self.room_exit_checkbox = tk.BooleanVar()
        tk.CTkCheckBox(self.input_frame, text="is exit", variable=self.room_exit_checkbox).pack()

        tk.CTkButton(self.input_frame, text="Add Room", command=self.add_room).pack(pady=10)

        # Map frame
        self.map_frame = tk.CTkFrame(self.layout_tab)
        self.map_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.map_canvas = stk.Canvas(self.map_frame, width=800, height=600, bg="#202120")
        self.map_canvas.pack(fill=tk.BOTH, expand=True)

        # Right sidebar frame for adding gates
        self.gate_input_frame = tk.CTkFrame(self.layout_tab)
        self.gate_input_frame.pack(side=tk.RIGHT, fill=tk.Y)

        tk.CTkLabel(self.gate_input_frame, text="Add Gate", font=("Arial", 14)).pack(pady=5)

        tk.CTkLabel(self.gate_input_frame, text="Room 1 Name:").pack()
        self.room_1_name_entry = tk.CTkEntry(self.gate_input_frame)
        self.room_1_name_entry.pack()

        tk.CTkLabel(self.gate_input_frame, text="Room 2 Name:").pack()
        self.room_2_name_entry = tk.CTkEntry(self.gate_input_frame)
        self.room_2_name_entry.pack()

        tk.CTkLabel(self.gate_input_frame, text="Hallway Capacity").pack()
        self.gate_capacity_entry = tk.CTkEntry(self.gate_input_frame)
        self.gate_capacity_entry.pack()

        tk.CTkButton(self.gate_input_frame, text="Add Gate", command=self.add_gate).pack(pady=10)

        threading.Thread(target=self.update_gates, daemon=True).start()
    
    def update_gates(self):
        while True:
            for gate, d1, d2 in self.gates_look:
                gate: Line
                gate.update(d1.start_x,d1.start_y, d2.start_x,d2.start_y)
            time.sleep(0.1)

    def create_analysis_tabs(self):
        tab_names = ["CCTV Input", "Count (Heatmap)", "Heatmap"]
        
        for tab_name in tab_names:
            tab = tk.CTkFrame(self.notebook)
            self.notebook.bind("<<NotebookTabChanged>>", )
            self.notebook.add(tab, text=tab_name)
            self.tabs[tab_name] = tab
            
            # Create a common frame for video display
        self.create_video_display_frame(tab, tab_name)

    def create_video_display_frame(self, tab, tab_name): # TODO: misleading name, tab_name is actually room_name
        # Create a frame for video display
        video_frame = tk.CTkFrame(tab)
        video_frame.pack(fill=tk.BOTH, expand=True, padx=5)

        tk.CTkLabel(video_frame, text=f"Video Feed for {tab_name}").pack()

        if tab_name == "Evacuation Map":
            tk.CTkLabel(
                video_frame,
                text=self.rooms[tab_name]["evacuation_path"]
            ).pack(pady=5)
        elif tab_name == "CCTV Input":
            tk.CTkButton(
                video_frame,
                text="Select Video",
                command=lambda: self.select_video(tab_name)
            ).pack(pady=5)

        # Create a label for video display
        video_label = tk.CTkLabel(video_frame)
        video_label.pack(expand=True, fill=tk.BOTH)

        if tab_name not in self.video_labels:
            self.video_labels[tab_name] = {}
        self.video_labels[tab_name]['video'] = video_label

        # Script selection and analysis buttons
        script_frame = tk.CTkFrame(tab)
        script_frame.pack(fill=tk.X, padx=5)

        tk.CTkLabel(script_frame, text=f"Select {tab_name} Script:").pack(side=tk.LEFT, padx=5)
        tk.CTkButton(
            script_frame, 
            text="Browse", 
            command=lambda t=tab_name: self.select_script(t)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.CTkButton(
            script_frame, 
            text="Run Analysis", 
            command=lambda t=tab_name: self.run_analysis(t)
        ).pack(side=tk.LEFT, padx=5)

        tk.CTkButton(
            script_frame, 
            text="Stop Analysis", 
            command=lambda t=tab_name: self.stop_analysis(t)
        ).pack(side=tk.LEFT, padx=5)

    def select_script(self, tab_name):
        script_path = filedialog.askopenfilename(
            title=f"Select {tab_name} Script",
            filetypes=[("Python Files", "*.py")]
        )
        if script_path:
            self.scripts[tab_name] = script_path
            messagebox.showinfo("Script Selected", f"{tab_name} script set to: {script_path}")

    def run_analysis(self, tab_name):
        if tab_name not in self.analysis_running:
            self.analysis_running[tab_name] = {}

        if tab_name == "People Count":
            if self.model is None:
                try:
                    self.model = YOLO("yolo11n.pt")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load YOLO model: {str(e)}")
                    return

            for room_name in self.rooms:
                if room_name not in self.analysis_running[tab_name]:
                    self.analysis_running[tab_name][room_name] = True
                    thread = threading.Thread(
                        target=self.run_people_counter,
                        args=(room_name,),
                        daemon=True
                    )
                    thread.start()

    def stop_analysis(self, tab_name):
        if tab_name in self.analysis_running:
            for room_name in self.analysis_running[tab_name]:
                self.analysis_running[tab_name][room_name] = False
            self.analysis_running[tab_name] = {}

    def run_people_counter(self, room_name):
        if room_name not in self.video_streams:
            return

        while (self.running and 
               "People Count" in self.analysis_running and 
               room_name in self.analysis_running["People Count"] and 
               self.analysis_running["People Count"][room_name]):
            
            stream_data = self.video_streams[room_name]
            cap = stream_data["capture"]
            ret, frame = cap.read()

            if ret:
                # Resize frame
                frame = cv2.resize(frame, (300, 200))
                
                # Run YOLO detection
                results = self.model.track(frame, persist=True)
                
                # Process results
                if results[0].boxes is not None and results[0].boxes.id is not None:
                    boxes = results[0].boxes.xyxy.int().cpu().tolist()
                    class_ids = results[0].boxes.cls.int().cpu().tolist()
                    track_ids = results[0].boxes.id.int().cpu().tolist()
                    
                    # Draw detected people
                    for box, class_id, track_id in zip(boxes, class_ids, track_ids):
                        if self.model.names[class_id] == 'person':
                            x1, y1, x2, y2 = box
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(frame, f'ID: {track_id}', (x1, y1-10),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Convert to PhotoImage and update display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(image=img)
                
                # Update the People Count tab
                if room_name in self.video_labels.get("People Count", {}):
                    label = self.video_labels["People Count"][room_name]
                    label.configure(image=photo)
                    label.image = photo
            else:
                # Reset video to beginning
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def update_video_grid(self):
        # Clear existing grid in all tabs
        for tab_name, tab in self.tabs.items():
            for widget in tab.winfo_children():
                widget.destroy()

        # Calculate grid dimensions
        num_rooms = len(self.rooms)
        grid_size = max(1, int((num_rooms ** 0.5 + 0.9)))


        # Create video frames in each tab
        for tab_name, tab in self.tabs.items():
            for i, room_name in enumerate(self.rooms.keys()):
                frame = tk.CTkFrame(tab)
                frame.pack(padx=5, fill=tk.BOTH, expand=True)
                
                tk.CTkLabel(frame, text=room_name).pack()
                
                video_label = tk.CTkLabel(frame, text="")
                video_label.pack(expand=True, fill=tk.BOTH)
                
                if tab_name not in self.video_labels:
                    self.video_labels[tab_name] = {}
                self.video_labels[tab_name][room_name] = video_label
                if tab_name == "CCTV Input":
                    tk.CTkButton(
                        frame,
                        text="Select Video",
                        command=lambda r=room_name: self.select_video(r)
                    ).pack(pady=5)
                

                self.room_frames[room_name]["frame"] = frame

    def select_video(self, room_name):
        video_path = filedialog.askopenfilename(
            title=f"Select CCTV Feed for {room_name}",
            filetypes=[("Video Files", "*.mp4 *.avi"), ("All Files", "*.*")]
        )
        if video_path:
            if room_name in self.video_streams:
                self.video_streams[room_name]["running"] = False
                
            self.video_streams[room_name] = {
                "path": video_path,
                "running": True,
                "capture": cv2.VideoCapture(video_path),
                "smoke_capture": cv2.VideoCapture(video_path)
            }
            
            # Start a thread to stream the video
            thread = threading.Thread(
                target=self.stream_video,
                args=(room_name,),
                daemon=True
            )
            thread.start()
    def show_image(self, frame):
        def runner():
            while True:
                cv2.imshow('', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        # threading.Thread(target=runner, daemon=True).start()
        runner()
    def calc_gradient(self, room_name):
        while True:
            try:
                while not room_name in self.current_frame:
                    time.sleep(0.1)
                if self.current_stream == "Heatmap":
                    _, buffer = cv2.imencode(".jpeg", self.current_frame[room_name])
                    response = requests.post(
                        "http://localhost:8080/uploadimagejpeg",
                        files={'files': buffer.tobytes()}
                    )
                    self.gradient[room_name] = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR)
                elif self.current_stream == "Count (Heatmap)":
                    _, buffer = cv2.imencode(".jpeg", self.current_frame[room_name])
                    
                    #from key 2WqPAb6RElk7pdtvp34ihETJmEo_2xxxxxxxxxxxxxxxxxxxx U...21.ipynb colab.
                    response = requests.post(
                        "https://apparent-stirred-bluegill.ngrok-free.app/heatmap", 
                        files={'files': buffer.tobytes()}
                    )
                    self.gradient[room_name] = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR)
                else:
                    time.sleep(0.1)
            except:
                pass
    
    def stream_video(self, room_name):
        threading.Thread(target=lambda: self.calc_gradient(room_name), daemon=True).start()
        stream_data = self.video_streams[room_name]
        while stream_data["running"] and self.running:
            cap = stream_data["capture"]
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset video to beginning if end is reached TODO: This is onlt for videos.
                continue
            frame = cv2.resize(frame, (300, 200), interpolation=cv2.INTER_AREA)
            self.current_frame[room_name] = frame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB

            if self.current_stream == "Heatmap":
                try:
                    frame = cv2.addWeighted(frame, 0.7, self.gradient[room_name], 0.3, 0)
                except Exception as e:
                    pass
            if self.current_stream == "Count (Heatmap)":
                try:
                    frame = cv2.addWeighted(frame, 0.7, self.gradient[room_name], 0.3, 0)
                except:
                    pass
            img = Image.fromarray(frame)  # Convert to Image
            photo = ImageTk.PhotoImage(image=img)  # Convert to PhotoImage
            
            # Update the video label in the corresponding tab
            for tab_name, labels in self.video_labels.items():
                label = labels[room_name]
                label.configure(image=photo)
                label.image = photo  # Keep a reference to avoid garbage collection


    def add_room(self):
        name = self.room_name_entry.get()
        try:
            width = float(self.room_width_entry.get())
            length = float(self.room_length_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values for width and length.")
            return

        if not name:
            messagebox.showerror("Input Error", "Please enter a valid room name.")
            return

        if name in self.rooms:
            messagebox.showerror("Duplicate Room", "Room with this name already exists.")
            return

        self.rooms[name] = {
            "width": width,
            "length": length,
            "area": width * length,
            "capacity": int(self.room_capacity_entry.get()),
            "current_occupency": 0,
            "is_exit": self.room_exit_checkbox.get(),
            "evacuation_path": ""
        }

        # Create a rectangle with the given width and height on the map canvas
        room_id = len(self.rooms)
        x1 = 10 + 100 * (room_id - 1)  # Adjust positioning as needed
        y1 = 10
        x2 = x1 + width
        y2 = y1 + length
        
        self.rooms[name].update({"drag_ref": DraggableRectangle(self.map_canvas, name, x1, y1, x2, y2, fill="#47474a", outline="black")})

        self.update_video_grid()
        
        self.room_name_entry.delete(0, tk.END)
        self.room_width_entry.delete(0, tk.END)
        self.room_length_entry.delete(0, tk.END)
        self.room_capacity_entry.delete(0, tk.END)
        
        new_node = Node(name, self.rooms[name]["capacity"], self.rooms[name]['is_exit'])  # Assuming you have a capacity attribute
        self.node_graph.add_node(new_node)

        messagebox.showinfo("Success", f"Room '{name}' added successfully.")
    
    def add_gate(self):
        try:
            room1 = self.room_1_name_entry.get()
            room2 = self.room_2_name_entry.get()
            assert (room1 in self.rooms) and (room2 in self.rooms)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter existing room names.")
            return
    
        self.gates_look.append([
            Line(
                self.map_canvas,
                _Point(self.rooms[room1]["drag_ref"].start_x,
                       self.rooms[room1]["drag_ref"].start_y
                ), 
                _Point(self.rooms[room2]["drag_ref"].start_x,
                       self.rooms[room2]["drag_ref"].start_y
                )
            ),
            self.rooms[room1]["drag_ref"],
            self.rooms[room2]["drag_ref"],
        ])
        
        self.rooms["Gate from "+room1+" To "+room2] = {
            "width": 0,
            "length": 0,
            "area": 0,
            'current_occupency': 0,
            "capacity": self.gate_capacity_entry.get(),
            "evacuation_path": ''
        }

        self.update_video_grid()
        room2_index = None
        room1_index = None

        for i in range(len(self.node_graph.nodes)):
            if self.node_graph.nodes[i].name == room1:
                room1_index = i
            elif self.node_graph.nodes[i].name == room2:
                room2_index = i
        
        self.node_graph.nodes[room1_index].add_connection(self.node_graph.nodes[room2_index])
        self.node_graph.nodes[room2_index].add_connection(self.node_graph.nodes[room1_index])

    def on_closing(self):
        self.running = False
        for stream_data in self.video_streams.values():
            stream_data["running"] = False
            if "capture" in stream_data:
                stream_data["capture"].release()
        self.root.destroy()
        for proc in self.processes:
            proc.kill()
root = None
if __name__ == "__main__":
    root = tk.CTk()
    root.configure(bg="#202120")
    app = CrowdManagementApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()