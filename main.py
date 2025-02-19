import os
import cv2
import face_recognition

import customtkinter as ctk
from tkinter import messagebox
from tinydb import TinyDB, Query
import subprocess  # Import subprocess module

main_proc: subprocess.Popen = None

# Initialize TinyDB
db = TinyDB('login_info.json')
User  = Query()

# Create 'people' directory if it doesn't exist
people_dir = 'people'
if not os.path.exists(people_dir):
    os.makedirs(people_dir)

# Function to match face
def match_face(unknown_face_encoding):
    for filename in os.listdir(people_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            person_image = face_recognition.load_image_file(os.path.join(people_dir, filename))
            person_face_encoding = face_recognition.face_encodings(person_image)

            if not person_face_encoding:
                continue

            person_face_encoding = person_face_encoding[0]
            results = face_recognition.compare_faces([person_face_encoding], unknown_face_encoding)
            if results[0]:
                return True, filename  # Return True and the matched filename

    return False, None  # No match found

# Function to capture image from webcam for facial recognition
def capture_image_for_login():
    cap = cv2.VideoCapture(0)
    print("Press 'c' to capture an image, 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        cv2.imshow("Webcam - Login", frame)

        key = cv2.waitKey(1)
        if key == ord('c'):
            unknown_face_encoding = face_recognition.face_encodings(frame)
            if unknown_face_encoding:
                match, filename = match_face(unknown_face_encoding[0])
                if match:
                    messagebox.showinfo("Match Found", f"Match found with {filename}")
                    cap.release()
                    cv2.destroyAllWindows()
                    return True  # Return True if face matches
                else:
                    messagebox.showerror("Error", "No matching face found.")
                    break
            else:
                messagebox.showerror("Error", "No face found in the captured image.")
                break
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return False  # Return False if no face is matched or captured

# Function to capture image from webcam for registration
def capture_image_for_registration(username):
    cap = cv2.VideoCapture(0)
    print("Press 's' to save an image, 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        cv2.imshow("Webcam - Registration", frame)

        key = cv2.waitKey(1)
        if key == ord('s'):
            img_name = os.path.join(people_dir, f"{username}.jpg")
            cv2.imwrite(img_name, frame)
            print(f"Image saved as {img_name}")
            messagebox.showinfo("Success", "Face registered successfully!")
            cap.release()
            cv2.destroyAllWindows()
            return True  # Return True if image is saved
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return False  # Return False if no image is saved

# Function to handle login
def login():
    username = entry_username.get()
    password = entry_password.get()

    user = db.search((User .username == username) & (User .password == password))
    
    if user:
        if capture_image_for_login():
            label_status.configure(text="Login Successful!", text_color="green")
            open_control_panel()  # Open control panel after successful login
        else:
            label_status.configure(text="Facial Recognition Failed", text_color="red")
    else:
        label_status.configure(text="Invalid Username or Password", text_color="red")

# Function to open control panel
def open_control_panel():
    # Clear the main window
    for widget in app.winfo_children():
        widget.destroy()

    # Create control panel widgets
    label_control_panel = ctk.CTkLabel(app, text="Control Panel")
    label_control_panel.pack(pady=10)

    button_add_user = ctk.CTkButton(app, text="Add User", command=show_registration_interface)
    button_add_user.pack(pady=10)

    button_launch_app = ctk.CTkButton(app, text="Launch Application", command=launch_application)
    button_launch_app.pack(pady=10)

    button_logout = ctk.CTkButton(app, text="Logout", command=logout)
    button_logout.pack(pady=10)

# Function to launch an application using subprocess
def launch_application():
    global main_proc
    import os
    import sys
    try:
        main_proc = subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "final_project", "gui.py")])
        messagebox.showinfo("Success", "Application launched successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch application: {e}")

# Function to show registration interface
def show_registration_interface():
    # Clear the main window
    for widget in app.winfo_children():
        widget.destroy()

    # Create registration interface widgets
    label_register = ctk.CTkLabel(app, text="Register New User")
    label_register.pack(pady=10)

    label_username = ctk.CTkLabel(app, text="Username:")
    label_username.pack(pady=5)

    entry_new_username = ctk.CTkEntry(app)
    entry_new_username.pack(pady=5)

    label_password = ctk.CTkLabel(app, text="Password:")
    label_password.pack(pady=5)

    entry_new_password = ctk.CTkEntry(app, show="*")
    entry_new_password.pack(pady=5)

    button_register = ctk.CTkButton(app, text="Register", command=lambda: register_user(entry_new_username.get(), entry_new_password.get()))
    button_register.pack(pady=10)

    button_cancel = ctk.CTkButton(app, text="Cancel", command=open_control_panel)
    button_cancel.pack(pady=5)

# Function to register a new user
def register_user(username, password):
    if db.search(User.username == username):
        messagebox.showerror("Error", "Username already exists!")
    else:
        if capture_image_for_registration(username):
            db.insert({'username': username, 'password': password})
            messagebox.showinfo("Success", "User  added successfully!")
            open_control_panel()  # Return to control panel after registration
        else:
            messagebox.showerror("Error", "Face not captured. User addition failed.")

# Function to handle logout
def logout():
    # Clear the main window
    for widget in app.winfo_children():
        widget.destroy()
    main_proc.kill()
    raise SystemExit(0)

# Initialize the main window
app = ctk.CTk()
app.title("Login Page")
app.geometry("300x300")

# Initialize the login interface
label_username = ctk.CTkLabel(app, text="Username:")
label_username.pack(pady=10)

entry_username = ctk.CTkEntry(app)
entry_username.pack(pady=5)

label_password = ctk.CTkLabel(app, text="Password:")
label_password.pack(pady=10)

entry_password = ctk.CTkEntry(app, show="*")
entry_password.pack(pady=5)

button_login = ctk.CTkButton(app, text="Login", command=login)
button_login.pack(pady=10)

label_status = ctk.CTkLabel(app, text="")
label_status.pack(pady=10)

# Run the application
app.mainloop()