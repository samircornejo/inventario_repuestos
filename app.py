import customtkinter as ctk
import sqlite3
from tkinter import ttk, messagebox

# Inicializar CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# --- CONEXIÓN BD ---
def conectar_db():
    conn = sqlite3.connect("inventario.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS repuestos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            descripcion TEXT,
            cantidad INTEGER,
            marca TEXT,
            precio_adquirido REAL,
            precio_venta REAL
        )
    ''')
    conn.commit()
    conn.close()

# --- FUNCIONES CRUD ---
def agregar_repuesto():
    tipo = entry_tipo.get()
    desc = entry_desc.get()
    cantidad = entry_cantidad.get()
    marca = entry_marca.get()
    precio_adq = entry_precio_adq.get()
    precio_venta = entry_precio_venta.get()

    if not (tipo and desc and cantidad and marca and precio_adq and precio_venta):
        messagebox.showwarning("Campos vacíos", "Completa todos los campos.")
        return

    conn = sqlite3.connect("inventario.db")
    c = conn.cursor()
    c.execute('INSERT INTO repuestos (tipo, descripcion, cantidad, marca, precio_adquirido, precio_venta) VALUES (?, ?, ?, ?, ?, ?)',
              (tipo, desc, int(cantidad), marca, float(precio_adq), float(precio_venta)))
    conn.commit()
    conn.close()
    listar_repuestos()
    limpiar_campos()
    cargar_filtros()

def listar_repuestos():
    for row in tree.get_children():
        tree.delete(row)
    conn = sqlite3.connect("inventario.db")
    c = conn.cursor()
    c.execute('SELECT * FROM repuestos')
    for row in c.fetchall():
        tree.insert('', 'end', values=row)
    conn.close()

def eliminar_repuesto():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Selecciona", "Selecciona un repuesto para eliminar.")
        return
    item = tree.item(selected[0])
    repuesto_id = item['values'][0]
    conn = sqlite3.connect("inventario.db")
    c = conn.cursor()
    c.execute('DELETE FROM repuestos WHERE id=?', (repuesto_id,))
    conn.commit()
    conn.close()
    listar_repuestos()

def cargar_repuesto(event):
    selected = tree.selection()
    if not selected:
        return
    item = tree.item(selected[0])
    repuesto = item['values']

    entry_tipo.set(repuesto[1])
    entry_desc.delete(0, ctk.END)
    entry_desc.insert(0, repuesto[2])
    entry_cantidad.delete(0, ctk.END)
    entry_cantidad.insert(0, repuesto[3])
    entry_marca.delete(0, ctk.END)
    entry_marca.insert(0, repuesto[4])
    entry_precio_adq.delete(0, ctk.END)
    entry_precio_adq.insert(0, repuesto[5])
    entry_precio_venta.delete(0, ctk.END)
    entry_precio_venta.insert(0, repuesto[6])

    id_edicion.set(repuesto[0])
    modo_edicion()

def guardar_cambios():
    repuesto_id = id_edicion.get()
    tipo = entry_tipo.get()
    desc = entry_desc.get()
    cantidad = entry_cantidad.get()
    marca = entry_marca.get()
    precio_adq = entry_precio_adq.get()
    precio_venta = entry_precio_venta.get()

    conn = sqlite3.connect("inventario.db")
    c = conn.cursor()
    c.execute('''
        UPDATE repuestos SET tipo=?, descripcion=?, cantidad=?, marca=?, precio_adquirido=?, precio_venta=?
        WHERE id=?
    ''', (tipo, desc, int(cantidad), marca, float(precio_adq), float(precio_venta), repuesto_id))
    conn.commit()
    conn.close()
    listar_repuestos()
    limpiar_campos()
    modo_normal()
    cargar_filtros()

def filtrar_repuestos():
    marca = filtro_marca.get()
    tipo = filtro_tipo.get()
    busqueda = busqueda_desc.get()

    query = 'SELECT * FROM repuestos WHERE 1=1'
    params = []

    if marca:
        query += ' AND marca=?'
        params.append(marca)
    if tipo:
        query += ' AND tipo=?'
        params.append(tipo)
    if busqueda:
        query += ' AND descripcion LIKE ?'
        params.append(f'%{busqueda}%')

    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("inventario.db")
    c = conn.cursor()
    c.execute(query, params)
    for row in c.fetchall():
        tree.insert('', 'end', values=row)
    conn.close()

# --- FUNCIONES AUXILIARES ---
def limpiar_campos():
    entry_tipo.set("")
    entry_desc.delete(0, ctk.END)
    entry_cantidad.delete(0, ctk.END)
    entry_marca.delete(0, ctk.END)
    entry_precio_adq.delete(0, ctk.END)
    entry_precio_venta.delete(0, ctk.END)
    id_edicion.set("")

def limpiar_filtros():
    filtro_marca.set("")
    filtro_tipo.set("")
    busqueda_desc.set("")

def modo_edicion():
    btn_agregar.grid_forget()
    btn_guardar.grid(row=6, column=0, pady=10)
    btn_cancelar.grid(row=6, column=1, pady=10)

def modo_normal():
    btn_guardar.grid_forget()
    btn_cancelar.grid_forget()
    btn_agregar.grid(row=6, column=0, pady=10)

def cargar_filtros():
    conn = sqlite3.connect("inventario.db")
    c = conn.cursor()
    c.execute('SELECT DISTINCT marca FROM repuestos')
    marcas = [row[0] for row in c.fetchall()]
    combo_marca.configure(values=[""] + marcas)

    c.execute('SELECT DISTINCT tipo FROM repuestos')
    tipos = [row[0] for row in c.fetchall()]
    combo_tipo.configure(values=[""] + tipos)
    entry_tipo.configure(values=tipos)  # actualizar combo de agregar

    conn.close()

# --- INTERFAZ ---
app = ctk.CTk()
app.title("Inventario de Repuestos")
app.geometry("1280x720")
app.configure(fg_color="#2e2e2e")

id_edicion = ctk.StringVar()
filtro_marca = ctk.StringVar()
filtro_tipo = ctk.StringVar()
busqueda_desc = ctk.StringVar()

label_titulo = ctk.CTkLabel(app, text="Agregar Producto", font=ctk.CTkFont(size=20, weight="bold"))
label_titulo.grid(row=0, column=0, columnspan=4, pady=10)

entry_tipo = ctk.CTkComboBox(app, values=[], width=250)
entry_tipo.grid(row=1, column=0, padx=10, pady=5)

entry_desc = ctk.CTkEntry(app, placeholder_text="Descripción", width=250)
entry_desc.grid(row=1, column=1, padx=10, pady=5)

entry_cantidad = ctk.CTkEntry(app, placeholder_text="Cantidad", width=250)
entry_cantidad.grid(row=2, column=0, padx=10, pady=5)

entry_marca = ctk.CTkEntry(app, placeholder_text="Marca", width=250)
entry_marca.grid(row=2, column=1, padx=10, pady=5)

entry_precio_adq = ctk.CTkEntry(app, placeholder_text="Precio Adquirido", width=250)
entry_precio_adq.grid(row=3, column=0, padx=10, pady=5)

entry_precio_venta = ctk.CTkEntry(app, placeholder_text="Precio Venta", width=250)
entry_precio_venta.grid(row=3, column=1, padx=10, pady=5)

btn_agregar = ctk.CTkButton(app, text="Agregar", command=agregar_repuesto, fg_color="#d9534f", corner_radius=10)
btn_guardar = ctk.CTkButton(app, text="Guardar Cambios", command=guardar_cambios, fg_color="#d9534f", corner_radius=10)
btn_cancelar = ctk.CTkButton(app, text="Cancelar", command=lambda: [limpiar_campos(), modo_normal()], fg_color="#d9534f", corner_radius=10)

btn_eliminar = ctk.CTkButton(app, text="Eliminar", command=eliminar_repuesto, fg_color="#d9534f", corner_radius=10)
btn_eliminar.grid(row=6, column=2, pady=10)
btn_limpiar = ctk.CTkButton(app, text="Limpiar", command=limpiar_campos, fg_color="#d9534f", corner_radius=10)
btn_limpiar.grid(row=6, column=3, pady=10)

# Filtros
filter_frame = ctk.CTkFrame(app)
filter_frame.grid(row=7, column=0, columnspan=4, padx=10, pady=10, sticky='nsew')

label_marca = ctk.CTkLabel(filter_frame, text="Marca:")
label_marca.pack(side='left', padx=5)
combo_marca = ctk.CTkComboBox(filter_frame, variable=filtro_marca, width=150)
combo_marca.pack(side='left', padx=5)

label_tipo = ctk.CTkLabel(filter_frame, text="Tipo:")
label_tipo.pack(side='left', padx=5)
combo_tipo = ctk.CTkComboBox(filter_frame, variable=filtro_tipo, width=150)
combo_tipo.pack(side='left', padx=5)

label_busqueda = ctk.CTkLabel(filter_frame, text="Buscar descripción:")
label_busqueda.pack(side='left', padx=5)
entry_busqueda = ctk.CTkEntry(filter_frame, textvariable=busqueda_desc, placeholder_text="Descripción", width=200)
entry_busqueda.pack(side='left', padx=5)

btn_buscar = ctk.CTkButton(filter_frame, text="Buscar", command=filtrar_repuestos, fg_color="#d9534f", corner_radius=10)
btn_buscar.pack(side='left', padx=5)
btn_reset = ctk.CTkButton(filter_frame, text="Restablecer", command=lambda: [listar_repuestos(), limpiar_filtros(), cargar_filtros()], fg_color="#d9534f", corner_radius=10)
btn_reset.pack(side='left', padx=5)

# Tabla
columns = ("ID", "Tipo", "Descripción", "Cantidad", "Marca", "Precio Adquirido", "Precio Venta")
tree = ttk.Treeview(app, columns=columns, show='headings')

col_widths = {
    "ID": 60,
    "Tipo": 100,
    "Descripción": 300,
    "Cantidad": 80,
    "Marca": 120,
    "Precio Adquirido": 130,
    "Precio Venta": 130
}

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=col_widths.get(col, 100))

tree.grid(row=8, column=0, columnspan=4, padx=10, pady=10, sticky='nsew')
tree.bind('<Double-1>', cargar_repuesto)

# Inicialización
conectar_db()
listar_repuestos()
cargar_filtros()
modo_normal()

app.mainloop()
