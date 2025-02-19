import os
import sys, subprocess
import cv2
import face_recognition
import customtkinter as ctk
from tkinter import messagebox

# Function to match face
def match_face(unknown_face_encoding):
    # Load faces from the 'people' directory
    people_dir = 'people'
    for filename in os.listdir(people_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            person_image = face_recognition.load_image_file(os.path.join(people_dir, filename))
            person_face_encoding = face_recognition.face_encodings(person_image)

            if not person_face_encoding:
                continue

            person_face_encoding = person_face_encoding[0]

            # Compare faces
            results = face_recognition.compare_faces([person_face_encoding], unknown_face_encoding)
            if results[0]:
                messagebox.showinfo("Match Found", f"Match found with {filename}")
                return

    messagebox.showinfo("No Match", "No matching face found.")

# Function to capture image from webcam
def capture_image():
    cap = cv2.VideoCapture(0)
    print("Press 'c' to capture an image, 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        cv2.imshow("Webcam", frame)

        key = cv2.waitKey(1)
        if key == ord('c'):
            # Capture the frame and find encodings
            unknown_face_encoding = face_recognition.face_encodings(frame)
            if unknown_face_encoding:
                match_face(unknown_face_encoding[0])
                subprocess.Popen(f"{sys.executable} {os.path.join(os.path.dirname(__file__))}/../final_project/realgui.py")
                break
            else:
                messagebox.showerror("Error", "No face found in the captured image.")
                break
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    app.destroy()

# Create the GUI
app = ctk.CTk()
app.title("Face Recognition")
app.geometry("300x200")

capture_button = ctk.CTkButton(app, text="Capture Image", command=capture_image)
capture_button.pack(pady=20)

app.mainloop()