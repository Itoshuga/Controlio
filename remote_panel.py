import socket
import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog

PORT = 5001
AVAILABLE_SOUNDS = ["plane", "fart", "bip", "warning", "rizz", "vine", "mimimimi"]

def send_command(command):
    ip = ip_entry.get().strip()
    if not ip:
        log("⛔️ Veuillez entrer une adresse IP.")
        return
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect((ip, PORT))
            s.sendall(command.encode())
            log(f"✅ Commande envoyée : {command}")
    except Exception as e:
        log(f"❌ Erreur : {e}")

def send_sound(name):
    send_command(f"sound:{name}")

def send_speak():
    text = speak_text.get("1.0", tk.END).strip()
    if text:
        send_command(f"speak:{text}")
    else:
        log("⛔️ Texte de parole vide.")

def send_message():
    text = message_text.get("1.0", tk.END).strip()
    if text:
        send_command(f"msg:{text}")
    else:
        log("⛔️ Message vide.")

def log(message):
    console.configure(state='normal')
    console.insert(tk.END, f"{message}\n")
    console.configure(state='disabled')
    console.see(tk.END)

root = tk.Tk()
root.title("🎮 Contrôle Distant")
root.geometry("600x650")
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")

frame_top = ttk.LabelFrame(root, text="Connexion au serveur", padding=15)
frame_top.pack(fill=tk.X, padx=20, pady=(10, 0))

KNOWN_IPS = {
    "Clement": "192.168.1.120",
    "Antoine": "192.168.1.50",
    "Lucas": "192.168.1.106",
    "Autre...": "",
}

ttk.Label(frame_top, text="Adresse IP :").pack(side=tk.LEFT)
ip_choice = ttk.Combobox(frame_top, values=list(KNOWN_IPS.keys()), state="readonly", width=15)
ip_choice.set("Lucas")
ip_choice.pack(side=tk.LEFT, padx=5)

ip_entry = ttk.Entry(frame_top, width=20)
ip_entry.pack(side=tk.LEFT, padx=5)
ip_entry.insert(0, KNOWN_IPS["Lucas"])

def update_ip_entry(event=None):
    selection = ip_choice.get()
    ip_entry.delete(0, tk.END)
    ip_entry.insert(0, KNOWN_IPS.get(selection, ""))

ip_choice.bind("<<ComboboxSelected>>", update_ip_entry)

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

# 🔊 Onglet Sons
frame_sound = ttk.Frame(notebook)
notebook.add(frame_sound, text="🔊 Sons")
ttk.Label(frame_sound, text="Sélectionnez un son à jouer sur le PC distant :").pack(pady=10)
for sound in AVAILABLE_SOUNDS:
    ttk.Button(frame_sound, text=f"▶ {sound}", command=lambda s=sound: send_sound(s)).pack(fill=tk.X, padx=50, pady=2)

# 💬 Onglet Parole
frame_speak = ttk.Frame(notebook)
notebook.add(frame_speak, text="💬 Faire parler")
ttk.Label(frame_speak, text="Texte à faire dire au PC distant :").pack(anchor='w', pady=5, padx=10)
speak_text = tk.Text(frame_speak, height=5, wrap="word")
speak_text.pack(fill=tk.X, padx=10, pady=5)
ttk.Button(frame_speak, text="Parler", command=send_speak).pack(anchor='e', padx=10)

# 📩 Onglet Message
frame_msg = ttk.Frame(notebook)
notebook.add(frame_msg, text="📩 Message popup")
ttk.Label(frame_msg, text="Message à afficher en popup sur le PC distant :").pack(anchor='w', pady=5, padx=10)
message_text = tk.Text(frame_msg, height=5, wrap="word")
message_text.pack(fill=tk.X, padx=10, pady=5)
ttk.Button(frame_msg, text="Afficher", command=send_message).pack(anchor='e', padx=10)

# ⚡ Onglet Actions (Emolio, Souris, Travail)
frame_actions = ttk.Frame(notebook)
notebook.add(frame_actions, text="⚡ Actions")
ttk.Label(frame_actions, text="Commandes rapides à exécuter sur le PC distant :").pack(pady=10)
ttk.Button(frame_actions, text="🌀 Afficher un Emolio", command=lambda: send_command("emolio")).pack(fill=tk.X, padx=40, pady=5)
ttk.Button(frame_actions, text="🖱 Bouger la souris", command=lambda: send_command("move_mouse")).pack(fill=tk.X, padx=40, pady=5)
ttk.Button(frame_actions, text="🛠 Ouvrir page de travail", command=lambda: send_command("work")).pack(fill=tk.X, padx=40, pady=5)
ttk.Button(frame_actions, text="🔒 Verrouiller la session", command=lambda: send_command("lock")).pack(fill=tk.X, padx=40, pady=5)
ttk.Button(frame_actions, text="🖼 Changer le fond d'écran", command=lambda: ask_wallpaper_url()).pack(fill=tk.X, padx=40, pady=5)
ttk.Button(frame_actions, text="🖼 Afficher une image depuis un lien", command=lambda: ask_image_url()).pack(fill=tk.X, padx=40, pady=5)

def ask_wallpaper_url():
    url = simpledialog.askstring("Lien du fond d'écran", "Entre l’URL de l’image (.jpg / .png) :")
    if url and (url.endswith(".png") or url.endswith(".jpg") or url.endswith(".jpeg")):
        send_command(f"set_wallpaper:{url}")
    elif url:
        log("❌ Lien non valide (doit être .jpg/.png)")

def ask_image_url():
    url = simpledialog.askstring("Lien de l’image", "Entre l’URL de l’image (.png / .jpg) à afficher :")
    if url and (url.endswith(".png") or url.endswith(".jpg") or url.endswith(".jpeg")):
        send_command(f"image_url:{url}")
    elif url:
        log("❌ Lien non valide (doit être .jpg/.png)")


# 🎚️ Onglet Volume
frame_volume = ttk.Frame(notebook)
notebook.add(frame_volume, text="🎚️ Volume")
ttk.Label(frame_volume, text="Contrôlez le volume du PC distant :").pack(pady=10)

volume_levels = [("25%", 0.25), ("50%", 0.5), ("75%", 0.75), ("100%", 1.0)]
for label, level in volume_levels:
    ttk.Button(
        frame_volume,
        text=f"🔉 Volume {label}",
        command=lambda lvl=level: send_command(f"volume:set:{lvl}")
    ).pack(fill=tk.X, padx=50, pady=3)

ttk.Separator(frame_volume).pack(fill=tk.X, padx=20, pady=10)

ttk.Button(frame_volume, text="🔇 Mute", command=lambda: send_command("volume:mute")).pack(fill=tk.X, padx=50, pady=3)
ttk.Button(frame_volume, text="🔈 Unmute", command=lambda: send_command("volume:unmute")).pack(fill=tk.X, padx=50, pady=3)


# 🖥 Console
frame_console = ttk.LabelFrame(root, text="Console", padding=10)
frame_console.pack(fill=tk.BOTH, expand=False, padx=20, pady=(0, 15))
console = scrolledtext.ScrolledText(frame_console, height=8, state='disabled', font=("Courier", 10))
console.pack(fill=tk.BOTH, expand=True)

root.mainloop()
