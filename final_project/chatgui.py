import customtkinter as tk
from tkinter import scrolledtext
import time
import threading
import requests
import speech_recognition as sr

recognizer = sr.Recognizer()
mic = sr.Microphone()

tk.set_appearance_mode("System")  # Modes: system (default), light, dark
tk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green


def get_ai_response(user_input):
    return requests.post("http://localhost:9000/frame", json={"room": room_name.get(), "prompt": user_input}).text

def send_message():
    user_input = entry.get()
    if not user_input.strip():
        return
    
    chat_area.configure(state=tk.NORMAL)
    chat_area.insert(tk.END, f"You: {user_input}\n")
    chat_area.configure(state=tk.DISABLED)
    entry.delete(0, tk.END)
    
    send_button.configure(state=tk.DISABLED)  # Disable send button until AI responds
    
    def generate_response():
        response = get_ai_response(user_input)
        chat_area.configure(state=tk.NORMAL)
        chat_area.insert(tk.END, response + "\n")
        chat_area.configure(state=tk.DISABLED)
        chat_area.yview(tk.END)
        send_button.configure(state=tk.NORMAL)  # Re-enable send button
    
    threading.Thread(target=generate_response, daemon=True).start()

# Create the main window
root = tk.CTk()
root.title("ChatBot")
root.geometry("400x500")

def key_pressed():
    with mic as source:
        audio = recognizer.listen(source)

    output = recognizer.recognize_google(audio)

    output += "."

    chat_area.configure(state=tk.NORMAL)
    chat_area.insert(tk.END, f"You: {output}\n")
    chat_area.configure(state=tk.DISABLED)
    
    send_button.configure(state=tk.DISABLED)  # Disable send button until AI responds
    
    def generate_response():
        response = get_ai_response(output)
        chat_area.configure(state=tk.NORMAL)
        chat_area.insert(tk.END, response + "\n")
        chat_area.configure(state=tk.DISABLED)
        chat_area.yview(tk.END)
        send_button.configure(state=tk.NORMAL)  # Re-enable send button
    
    threading.Thread(target=generate_response, daemon=True).start()


tk.CTkButton(root, text="Voice Activation", command=key_pressed).pack(pady=5, padx=10)

# Chat display area
chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED)
chat_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

# Input field
entry = tk.CTkEntry(root, width=50)
entry.pack(pady=5, padx=10, fill=tk.X)

room_name = tk.CTkEntry(root, width=50)
room_name.pack(pady=5, padx=10, fill=tk.X)

# Send button
send_button = tk.CTkButton(root, text="Send", command=send_message)
send_button.pack(pady=5)

# Run the main loop
root.mainloop()
