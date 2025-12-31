import tkinter as tk
from PIL import Image, ImageTk
import cv2
from pyzbar.pyzbar import decode
import sqlite3
import time
import pyttsx3
import threading  
import pyttsx3
import threading

import pygame
import threading

pygame.mixer.init()


def speak_message(file_path, callback):
    def run():
        try:
            print("Playing audio:", file_path)
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            print("Audio finished.")
        except Exception as e:
            print(f"[ERROR] Audio playback failed: {e}")
        finally:
            # Make sure callback is ALWAYS called, even if playback fails
            print("Calling callback...")
            callback()

    threading.Thread(target=run, daemon=True).start()








# Step 1: Set up the SQLite database with the new schema
def setup_database():
    conn = sqlite3.connect("projects.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            abstract TEXT NOT NULL,
            description TEXT NOT NULL,
            image BLOB
        )
    ''')
    
    sample_data = [
        (1, "Switch Sense", 
         "This IoT-enabled smart lab uses ESP32, sensors, and gesture control for efficient device management. It ensures safety and sustainability through automation and real-time monitoring",
         "This IoT-enabled smart lab uses ESP32-based custom PCBs and intelligent sensors for real-time monitoring and automation. It features a matrix grid layout with section-wise control based on occupancy and gesture detection via OpenCV. Environmental factors like temperature, humidity, air quality, current, and voltage are continuously tracked. A wireless sensor network ensures seamless communication, making the system scalable, reliable, and energy-efficient.",
         None)
    ]
    
    cursor.executemany("INSERT OR IGNORE INTO projects (id, name, abstract, description, image) VALUES (?, ?, ?, ?, ?)", sample_data)
    conn.commit()
    conn.close()

# Step 2: Fetch project details from the database
def get_project_details(qr_id):
    conn = sqlite3.connect("projects.db")
    cursor = conn.cursor()
    
    try:
        qr_id = int(qr_id)  # Convert QR code data to integer
    except ValueError:
        return None
    
    cursor.execute("SELECT name, abstract, description, image FROM projects WHERE id = ?", (qr_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        name, abstract, description, image_data = row
        # If there's an image, convert it from BLOB to Image
        image = None
        if image_data:
            from io import BytesIO
            image = Image.open(BytesIO(image_data))  # Convert BLOB data to image using BytesIO
        return {"name": name, "abstract": abstract, "description": description, "image": image, "id": qr_id}
    else:
        return None


class QRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IoT Lab Assistant")
        self.root.geometry("800x480")
        self.root.attributes("-fullscreen", True)

        self.frames = {}
        self.setup_frames()
        self.show_frame("welcome")
        self.speak_welcome()

        self.cap = None
        self.is_scanning = False
        self.scanned_codes = set()

    def setup_frames(self):
        # ------------------- 
        # 🎉 Welcome Screen
        # ------------------- 
        welcome = tk.Frame(self.root, bg="#0F111A")
        welcome.pack(fill="both", expand=True)

        try:
            image = Image.open("welcome.jpg")
            image = image.resize((500, 300), Image.Resampling.LANCZOS)
            self.bg_img = ImageTk.PhotoImage(image)
            img_label = tk.Label(welcome, image=self.bg_img, bg="#0F111A")
            img_label.place(relx=0.5, rely=0.35, anchor="center")
        except Exception:
            tk.Label(welcome, text="Welcome Image Not Found", bg="#0F111A", fg="white",
                     font=("Helvetica Neue", 20, "bold")).pack(expand=True)

        tk.Label(welcome, text="Welcome to the IoT Lab Assistant",
                 font=("Segoe UI", 24, "bold"), fg="#00E5FF", bg="#0F111A").place(relx=0.5, rely=0.7, anchor="center")

        tk.Label(welcome, text="Smart Project Display using QR Code",
                 font=("Segoe UI", 14), fg="white", bg="#0F111A").place(relx=0.5, rely=0.78, anchor="center")

        self.frames["welcome"] = welcome

        # --------------------------
        # 🎬 Project Display Screen
        # --------------------------
        project = tk.Frame(self.root, bg="#0A192F")
        self.canvas = tk.Canvas(project, bg="#0A192F", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Canvas sizes
        canvas_width = 1270
        canvas_height = 600

        # Header
        self.canvas.create_text(canvas_width / 2, 50, text="Smart Lab Project Explorer",
                                font=("Segoe UI", 24, "bold"), fill="#00FFC6", anchor="center")

        # Dynamic box sizes and positioning
        box_margin_x = 80
        box_width = canvas_width - (2 * box_margin_x)
        name_y = 100
        abstract_y = 220
        desc_y = 350

        # Project Name Box
        self.canvas.create_rectangle(box_margin_x, name_y - 20, canvas_width - box_margin_x, name_y + 30,
                                    fill="#112240", outline="#00FFC6", width=2)

        # Project Name Text (Normal)
        self.name_text = self.canvas.create_text(canvas_width / 2, name_y, text="Project Name Here",
                                                font=("Helvetica Neue", 18, "bold"), fill="#00E5FF", anchor="center", width=box_width - 20)

        # Project Name Text (Glowing effect, initially hidden)
        self.name_glow = self.canvas.create_text(canvas_width / 2, name_y, text="Project Name Here",
                                                 font=("Helvetica Neue", 18, "bold"), fill="#00E5FF", anchor="center", width=box_width - 20, state="hidden")

        # Adjusting the height of the Abstract Box
        # Abstract Box Rectangle
        abstract_box_height = 100
        padding_y = 10  # Vertical padding
        self.canvas.create_rectangle(box_margin_x, (abstract_y - abstract_box_height // 2)-40,
                                     canvas_width - box_margin_x,( abstract_y + abstract_box_height // 2)+30,
                                     fill="#1C2541", outline="#00BFFF", width=2)

        # Abstract Text with Padding
        self.abstract_text = self.canvas.create_text(canvas_width / 2, abstract_y - 15,
                                                     text="Abstract will show up here after scanning a QR code.",
                                                     font=("Segoe UI", 16),
                                                     fill="#D9D9D9", anchor="center",
                                                     width=box_width - 60)  # 60px margin for left/right padding

        # Adjusting the height of the Description Box
        desc_box_height = 150  # Increased height from 100 to 150
        self.canvas.create_rectangle(box_margin_x, desc_y - desc_box_height // 2, 
                                     canvas_width - box_margin_x, desc_y + desc_box_height // 2,
                                     fill="#1B263B", outline="#00BFFF", width=2)
        self.desc_text = self.canvas.create_text(canvas_width / 2, desc_y   , 
                                         text="Project description will be displayed here.",
                                         font=("Segoe UI", 16), fill="#B0BEC5", anchor="center", width=box_width - 30)

        # Scanning Status
        self.scanning_note = self.canvas.create_text(canvas_width / 2, 440, text="📷 Scanning for QR Code...",
                                                    font=("Segoe UI", 12, "italic"), fill="#AAAAAA", anchor="center")

        # Restart Button
        restart_btn = tk.Button(project, text="Restart", font=("Segoe UI", 12, "bold"),
                                bg="#00E5FF", fg="#001F3F", activebackground="#00BCD4",
                                relief="flat", bd=0, padx=10, pady=5,
                                command=self.restart_app)
        restart_btn_window = self.canvas.create_window(canvas_width - 100, 450, window=restart_btn)

        self.frames["project"] = project

    def show_frame(self, name):
        print(f"🟡 Showing frame: {name}")  # Debugging the frame transition
        for frame in self.frames.values():
            frame.pack_forget()  # Hide all frames
        self.frames[name].pack(fill="both", expand=True)  # Show the selected frame


    def speak_welcome(self):
        msg = ("Welcome to the IoT Lab of GSFC University. I will guide you through smart project displays. Please wait.")
        self.root.after(100, lambda: speak_message('audio/starting.mp3', self.start_qr_scanning))

    def start_qr_scanning(self):
        print("🟢 In start_qr_scanning(): Showing project screen and starting camera.")
        self.show_frame("project")
        self.root.update()  # Force refresh of the window to ensure it shows the frame.

        # Safe camera initialization
        if self.cap and self.cap.isOpened():
            self.cap.release()  # Ensure the camera is released before reopening
        self.cap = cv2.VideoCapture(0)

        # Ensure the camera is opened
        if not self.cap.isOpened():
            print("Error: Unable to open camera.")
            return

        # Allow the camera to settle and configure settings
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.is_scanning = True  # Allow scanning to start

        # Run the scanning in a separate thread to avoid blocking the main GUI thread
        threading.Thread(target=self.scan, daemon=True).start()

    def restart_app(self):
        # Stop scanning and release the camera
        self.is_scanning = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None

        # Clear any previously scanned data
        self.canvas.itemconfig(self.name_text, text="Project Name Here", fill="#00E5FF", state="normal")
        self.canvas.itemconfig(self.name_glow, text="Project Name Here", state="hidden")
        self.canvas.itemconfig(self.abstract_text, text="Abstract will show up here after scanning a QR code.")
        self.canvas.itemconfig(self.desc_text, text="Project description will be displayed here.")
        self.canvas.itemconfig(self.scanning_note, text="📷 Scanning for QR Code...")

        self.clear_image()  # Remove old project image

        self.scanned_codes.clear()  # Allow re-scanning same codes

        # Show the welcome screen again
        self.show_frame("welcome")
        self.root.update()

        # Speak welcome message and start scanning again after a short delay
        self.root.after(1000, self.speak_welcome)



    def start_qr_scanning(self):
        print("🟢 In start_qr_scanning(): Showing project screen and starting camera.")
        self.show_frame("project")

        # Safe camera initialization
        if self.cap and self.cap.isOpened():
            self.cap.release()  # Ensure the camera is released before reopening
        self.cap = cv2.VideoCapture(0)
        
        # Ensure the camera is opened
        if not self.cap.isOpened():
            print("Error: Unable to open camera.")
            return

        # Allow the camera to settle and configure settings
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.is_scanning = True  # Allow scanning to start
        
        # Start the QR scanning in a separate thread
        threading.Thread(target=self.scan, daemon=True).start()

    def scan(self):
        print("🟢 Scanning started.")
        while True:
            if not self.cap.isOpened():
                print("Error: Unable to access camera.")
                break

            success, frame = self.cap.read()
            if not success:
                continue

            # Decode QR codes
            qrcodes = decode(frame)
            if qrcodes:
                for qr in qrcodes:
                    data = qr.data.decode("utf-8")

                    # Process the QR code only if it hasn't been scanned yet
                    if data not in self.scanned_codes and self.is_scanning:
                        self.scanned_codes.add(data)  # Mark this QR code as scanned
                        self.is_scanning = False  # Stop scanning temporarily to process the QR code
                        info = get_project_details(data)
                        if info:
                            # Update project name and description
                            self.canvas.itemconfig(self.name_glow, text=info['name'])
                            self.canvas.itemconfig(self.name_text, text=info['name'], fill="#00E5FF")
                            self.canvas.itemconfig(self.abstract_text, text=info['abstract'])
                            self.canvas.itemconfig(self.desc_text, text=info['description'])

                            # Show glowing name text, hide normal text for glow effect
                            self.canvas.itemconfig(self.name_glow, state="normal")  # Show glowing text
                            self.canvas.itemconfig(self.name_text, state="hidden")  # Hide normal text
                            
                            self.root.after(400, lambda: self.canvas.itemconfig(self.name_glow, state="hidden"))
                            self.root.after(400, lambda: self.canvas.itemconfig(self.name_text, state="normal"))

                            # Display the image if available
                            if info['image']:
                                self.display_image(info['image'])
                            else:
                                self.canvas.itemconfig(self.name_text, text="No image found for this project.")
                            
                            # Play the corresponding audio file for the project
                            mp3_file_path = f"audio/{info['id']}.mp3"  # Assuming all .mp3 files are in the 'audio' directory
                            speak_message(mp3_file_path, self.restart_scanning)
                        else:
                            self.canvas.itemconfig(self.name_text, text="Unknown Project", fill="#FF6E6E")
                            self.canvas.itemconfig(self.abstract_text, text="No project details found for this QR code.")
                            self.canvas.itemconfig(self.desc_text, text="")
                            self.root.after(400, lambda: self.canvas.itemconfig(self.name_text, fill="#FFFFFF"))
                            
                            # Clear the image for unknown projects
                            self.clear_image()
                            
                            speak_message("Unknown project.", self.restart_scanning)

                    time.sleep(0.1)

    def display_image(self, image):
        # Resize image to fit the space on the right
        image = image.resize((300, 300), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        # If the image is already displayed, remove the old one
        if hasattr(self, 'image_label'):
            self.image_label.destroy()

        # Display the new image on the right side
        self.image_label = tk.Label(self.canvas, image=photo, bg="#0A192F")
        self.image_label.image = photo  # Prevent garbage collection

        # Place the image around x=650 (right side), y=280 (aligned with description)
        self.canvas.create_window(1270 / 2, 600, window=self.image_label, anchor="center")

    def clear_image(self):
        # If there is an image, remove it
        if hasattr(self, 'image_label'):
            self.image_label.destroy()


    def restart_scanning(self):
        # Restart scanning after the message is spoken
        self.is_scanning = True

    def stop_scanning(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()  # Release the camera resource


if __name__ == "__main__":
    # setup_database()
    root = tk.Tk()
    app = QRApp(root)
    root.mainloop()
