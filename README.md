# Minor-Project-1
The Lab Assistant Robot helps visitors explore a laboratory by navigating between project stations, scanning QR codes, and presenting project information through audio. Controlled via a mobile app, it enables self-guided, organized lab exploration without the need for a human guide.

# 📱 IoT Lab Assistant – QR Code Project Explorer

A fullscreen interactive lab assistant application built using Python, Tkinter, OpenCV, and SQLite, designed to run on Linux (Raspberry Pi).
The system scans QR codes placed at project stations and automatically displays project details, images, and audio explanations.

---

🚀 Features

- 📷 Real-time QR code scanning using OpenCV & Pyzbar  
- 🖥️ Touch-friendly fullscreen UI (Tkinter)  
- 🗂️ SQLite database for project information  
- 🔊 MP3 audio playback per project using Pygame  
- ✨ Animated UI effects (glowing project title)  
- 🔁 Auto reset & rescan after audio completes  
- 🧠 Threaded execution for smooth performance  

---

🛠️ Technologies Used

- Python 3
- Tkinter
- OpenCV
- Pyzbar
- SQLite3
- Pillow (PIL)
- Pygame
- Linux (Raspberry Pi recommended)

---

 📂 Project Structure

Lab-Assistant-Code/<br>
├── app.py<br>
├── projects.db<br>
├── welcome.jpg<br>
├── audio/<br>
│   ├── starting.mp3<br>
│   ├── 1.mp3<br>
├── README.md<br>

---

🧠 How It Works

1. Application starts in fullscreen welcome mode  
2. Welcome audio plays automatically  
3. Camera activates and QR scanning begins  
4. On QR detection:
   - Project details fetched from database
   - UI updates with name, abstract, description
   - Project image displayed (if available)
   - Corresponding MP3 audio plays
5. After audio ends, system resets and waits for next scan

---

 ▶️ How to Run

1.Create Virtual Enviornment(using below given codes line by line in command prompt)
>sudo apt update<br>
>sudo apt install python3-venv python3-pip<br>
>python3 -m venv venv<br>
>source venv/bin/activate<br>

2.Install Dependencies
>pip install opencv-python pillow pyzbar pygame

Linux dependency:
>sudo apt install libzbar0

3.Run Application
>python3 app.py

---

 ➕ How to Add a New Project

Step 1: Add Project to Database

Each project must have a unique numeric ID.
Example:

INSERT INTO projects (id, name, abstract, description, image)
VALUES (2, 'Smart Energy Monitor', 'Short abstract', 'Full description', NULL);

---
Step 2: Generate QR Code
QR code value must be exactly the project ID.
Example:
2

---
Step 3: Add Project Audio
Audio file must be placed in the audio folder.
audio/2.mp3

---

🖼️ Automatic Image → BLOB Conversion
Project images are automatically converted to BLOB format.
You do NOT need to manually convert images.

Internally:
- Image is read in binary mode
- Stored as BLOB in SQLite
- Converted back and displayed using Pillow

Supported formats:
- JPG
- PNG

---

🔄 Restart Behavior

- Manual Restart button available
- Automatic reset after audio playback
- Same QR can be scanned again after reset


This project also includes an ESP32-based Bluetooth-controlled robot module for IoT and robotics lab
demonstrations.<br>

📱 Control Instructions:<br>
1.Pair phone with Bluetooth device "Lab Assistant"<br>
2.Use  RC app (apk link given)<br>
3.Press Buttons in app to pass diffrent commands<br>

## 👨‍💻 Author

Developed as part of an IoT Smart Lab Assistant Project.

