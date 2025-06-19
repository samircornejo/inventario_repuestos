import customtkinter as ctk
import subprocess
import sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("Menú Principal")
app.geometry("400x300")

def abrir_inventario():
    subprocess.Popen([sys.executable, "inventario.py"])

def abrir_proformas():
    subprocess.Popen([sys.executable, "proformas.py"])

label = ctk.CTkLabel(app, text="Todorepuestos", font=ctk.CTkFont(size=24, weight="bold"))
label.pack(pady=40)

btn_inventario = ctk.CTkButton(app, text="Inventario", command=abrir_inventario, width=200)
btn_inventario.pack(pady=10)

btn_proformas = ctk.CTkButton(app, text="Proformas", command=abrir_proformas, width=200)
btn_proformas.pack(pady=10)

app.mainloop()
