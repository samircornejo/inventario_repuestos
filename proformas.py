import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3

# Configuración inicial
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Variables globales
carrito = []

# --- CONEXIÓN BD ---
def obtener_productos():
    conn = sqlite3.connect("inventario.db")
    c = conn.cursor()
    c.execute("SELECT * FROM repuestos")
    productos = c.fetchall()
    conn.close()
    return productos

# --- FUNCIONES CARRITO ---
def agregar_al_carrito(item):
    for prod in carrito:
        if prod["id"] == item[0]:
            prod["cantidad"] += 1
            actualizar_resumen()
            return
    carrito.append({
        "id": item[0],
        "descripcion": item[2],
        "precio": item[6],
        "cantidad": 1
    })
    actualizar_resumen()

def quitar_del_carrito(item_id):
    for prod in carrito:
        if prod["id"] == item_id:
            prod["cantidad"] -= 1
            if prod["cantidad"] <= 0:
                carrito.remove(prod)
            break
    actualizar_resumen()

def actualizar_resumen():
    resumen_textbox.configure(state="normal")
    resumen_textbox.delete("1.0", "end")
    total = 0
    for p in carrito:
        subtotal = p["cantidad"] * p["precio"]
        resumen_textbox.insert("end", f"{p['descripcion']} x{p['cantidad']} = S/ {subtotal:.2f}\n")
        total += subtotal
    resumen_textbox.insert("end", f"\nTotal: S/ {total:.2f}")
    resumen_textbox.configure(state="disabled")

# --- INTERFAZ ---
app = ctk.CTk()
app.title("Módulo Proformas")
app.geometry("1280x720")

# Sección izquierda: productos
frame_izquierda = ctk.CTkFrame(app)
frame_izquierda.pack(side="left", fill="both", expand=True, padx=10, pady=10)

busqueda_var = ctk.StringVar()

entry_busqueda = ctk.CTkEntry(frame_izquierda, textvariable=busqueda_var, placeholder_text="Buscar producto")
entry_busqueda.pack(pady=10)

def cargar_tabla_productos():
    for row in tree.get_children():
        tree.delete(row)
    filtro = busqueda_var.get().lower()
    productos = obtener_productos()
    for prod in productos:
        if filtro in prod[2].lower():
            tree.insert('', 'end', values=prod)

btn_buscar = ctk.CTkButton(frame_izquierda, text="Buscar", command=cargar_tabla_productos)
btn_buscar.pack(pady=5)

columns = ("ID", "Tipo", "Descripción", "Cantidad", "Marca", "P. Adquirido", "P. Venta")
tree = ttk.Treeview(frame_izquierda, columns=columns, show="headings", height=20)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=130 if col == "Descripción" else 90)
tree.pack(fill="both", expand=True)

def agregar_producto_evento(event):
    selected = tree.selection()
    if not selected:
        return
    item = tree.item(selected[0])["values"]
    agregar_al_carrito(item)

tree.bind('<Double-1>', agregar_producto_evento)

# Sección derecha: resumen
frame_derecha = ctk.CTkFrame(app, width=400)
frame_derecha.pack(side="right", fill="y", padx=10, pady=10)

label_resumen = ctk.CTkLabel(frame_derecha, text="Resumen de Proforma", font=ctk.CTkFont(size=16, weight="bold"))
label_resumen.pack(pady=10)

resumen_textbox = ctk.CTkTextbox(frame_derecha, height=500, width=380)
resumen_textbox.pack(padx=10, pady=10)
resumen_textbox.configure(state="disabled")

def generar_pdf_placeholder():
    messagebox.showinfo("Proforma", "Aquí se generaría el PDF de la proforma.")

btn_generar = ctk.CTkButton(frame_derecha, text="Generar PDF", command=generar_pdf_placeholder, fg_color="green")
btn_generar.pack(pady=20)

# Inicializar
cargar_tabla_productos()
app.mainloop()
