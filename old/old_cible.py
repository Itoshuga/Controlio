import socket
import pygame
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

# Initialiser le son avec pygame
pygame.mixer.init()

# Fonction pour démuter et mettre le volume à 100%
def set_max_volume():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    # Démute
    if volume.GetMute():
        volume.SetMute(0, None)

    # Met le volume à 100%
    volume.SetMasterVolumeLevelScalar(0.3, None)

# Paramètres du serveur
HOST = '0.0.0.0'
PORT = 5001

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("En attente de connexion...")

    while True:
        conn, addr = s.accept()
        with conn:
            print(f"Connexion depuis {addr}")
            data = conn.recv(1024)
            if data == b'play':
                print("Commande reçue : jouer un son !")
                set_max_volume()
                pygame.mixer.music.load("son.mp3")  # Remplacer par le chemin correct
                pygame.mixer.music.play()
