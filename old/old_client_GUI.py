import socket
import tkinter as tk
from tkinter import ttk, scrolledtext

PORT = 5001

# Fonction de connexion
def send_play_command():
    ip = ip_entry.get().strip()
    if not ip:
        log("⛔️ Veuillez entrer une adresse IP.")
        return

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect((ip, PORT))
            s.sendall(b'play')
            log(f"✅ Commande envoyée à {ip}")
    except Exception as e:
        log(f"❌ Erreur : {e}")

# Fonction pour écrire dans la console
def log(message):
    console.configure(state='normal')
    console.insert(tk.END, f"{message}\n")
    console.configure(state='disabled')
    console.see(tk.END)

# Interface graphique
root = tk.Tk()
root.title("Contrôle du son distant")
root.geometry("450x300")
root.resizable(False, False)

# Champ IP
frame_top = ttk.Frame(root, padding=10)
frame_top.pack(fill=tk.X)

ttk.Label(frame_top, text="Adresse IP du serveur :").pack(side=tk.LEFT)
ip_entry = ttk.Entry(frame_top, width=20)
ip_entry.pack(side=tk.LEFT, padx=10)
ip_entry.insert(0, "192.168.1.106")  # IP par défaut

# Bouton envoyer
btn = ttk.Button(root, text="🔊 Lancer le son", command=send_play_command)
btn.pack(pady=10)

# Console
console = scrolledtext.ScrolledText(root, height=10, state='disabled', font=("Courier", 10))
console.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

# Lancement
root.mainloop()
