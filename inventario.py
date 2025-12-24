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
            codigo TEXT,
            tipo TEXT,
            descripcion TEXT,
            cantidad INTEGER,
            marca TEXT,
            precio_adquirido REAL,
            precio_venta REAL
        )
    ''')
    
    # Verificar si la columna 'codigo' existe, si no, agregarla
    c.execute("PRAGMA table_info(repuestos)")
    columns = [column[1] for column in c.fetchall()]
    if 'codigo' not in columns:
        try:
            c.execute('ALTER TABLE repuestos ADD COLUMN codigo TEXT')
            conn.commit()
            print("Columna 'codigo' agregada exitosamente")
        except Exception as e:
            print(f"Error al agregar columna: {e}")
    
    conn.commit()
    conn.close()

# --- MODALES ---
class ModalAgregar(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Agregar Repuesto")
        self.geometry("550x680")
        self.resizable(False, False)
        
        # Centrar ventana
        self.transient(parent)
        
        # Título
        label_titulo = ctk.CTkLabel(self, text="AGREGAR NUEVO REPUESTO", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1f6aa5")
        label_titulo.pack(pady=(20, 15))
        
        # Frame para el formulario con borde visible
        frame_formulario = ctk.CTkFrame(self, corner_radius=10, border_width=2, border_color="#1f6aa5", fg_color="#1a1a1a")
        frame_formulario.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Título del formulario
        ctk.CTkLabel(frame_formulario, text="Información del Repuesto", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        # Frame interno para campos
        frame_campos = ctk.CTkFrame(frame_formulario, fg_color="transparent")
        frame_campos.pack(padx=30, pady=10, fill="both", expand=True)
        
        # Campos del formulario
        ctk.CTkLabel(frame_campos, text="Código:", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(pady=(5, 2), fill="x")
        self.entry_codigo = ctk.CTkEntry(frame_campos, height=35, placeholder_text="Ej: REP001")
        self.entry_codigo.pack(pady=(0, 10), fill="x")
        
        ctk.CTkLabel(frame_campos, text="Tipo:", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(pady=(5, 2), fill="x")
        self.entry_tipo = ctk.CTkEntry(frame_campos, height=35, placeholder_text="Ej: Motor, Frenos, Suspensión")
        self.entry_tipo.pack(pady=(0, 10), fill="x")
        
        ctk.CTkLabel(frame_campos, text="Descripción:", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(pady=(5, 2), fill="x")
        self.entry_desc = ctk.CTkEntry(frame_campos, height=35, placeholder_text="Descripción detallada del repuesto")
        self.entry_desc.pack(pady=(0, 10), fill="x")
        
        # Frame para cantidad y marca (2 columnas)
        frame_row1 = ctk.CTkFrame(frame_campos, fg_color="transparent")
        frame_row1.pack(fill="x", pady=(5, 10))
        
        frame_cantidad = ctk.CTkFrame(frame_row1, fg_color="transparent")
        frame_cantidad.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(frame_cantidad, text="Cantidad:", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(pady=(0, 2), fill="x")
        self.entry_cantidad = ctk.CTkEntry(frame_cantidad, height=35, placeholder_text="0")
        self.entry_cantidad.pack(fill="x")
        
        frame_marca = ctk.CTkFrame(frame_row1, fg_color="transparent")
        frame_marca.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(frame_marca, text="Marca:", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(pady=(0, 2), fill="x")
        self.entry_marca = ctk.CTkEntry(frame_marca, height=35, placeholder_text="Marca del producto")
        self.entry_marca.pack(fill="x")
        
        # Frame para precios (2 columnas)
        frame_row2 = ctk.CTkFrame(frame_campos, fg_color="transparent")
        frame_row2.pack(fill="x", pady=(5, 10))
        
        frame_precio_adq = ctk.CTkFrame(frame_row2, fg_color="transparent")
        frame_precio_adq.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(frame_precio_adq, text="Precio Adquirido (S/):", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(pady=(0, 2), fill="x")
        self.entry_precio_adq = ctk.CTkEntry(frame_precio_adq, height=35, placeholder_text="0.00")
        self.entry_precio_adq.pack(fill="x")
        
        frame_precio_venta = ctk.CTkFrame(frame_row2, fg_color="transparent")
        frame_precio_venta.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(frame_precio_venta, text="Precio Venta (S/):", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(pady=(0, 2), fill="x")
        self.entry_precio_venta = ctk.CTkEntry(frame_precio_venta, height=35, placeholder_text="0.00")
        self.entry_precio_venta.pack(fill="x")
        
        # Botones
        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.pack(pady=20)
        
        btn_agregar = ctk.CTkButton(frame_botones, text="Agregar Repuesto", command=self.guardar, fg_color="#28a745", hover_color="#218838", height=40, width=200, font=ctk.CTkFont(size=14, weight="bold"))
        btn_agregar.pack(side="left", padx=10)
        
        btn_regresar = ctk.CTkButton(frame_botones, text="Regresar", command=self.destroy, fg_color="#6c757d", hover_color="#5a6268", height=40, width=180, font=ctk.CTkFont(size=14, weight="bold"))
        btn_regresar.pack(side="left", padx=10)
        
        # Aplicar grab después de que todo esté creado
        self.after(10, self.grab_set)
    
    def guardar(self):
        codigo = self.entry_codigo.get().strip()
        tipo = self.entry_tipo.get().strip()
        desc = self.entry_desc.get().strip()
        cantidad = self.entry_cantidad.get().strip()
        marca = self.entry_marca.get().strip()
        precio_adq = self.entry_precio_adq.get().strip()
        precio_venta = self.entry_precio_venta.get().strip()
        
        if not (codigo and tipo and desc and cantidad and marca and precio_adq and precio_venta):
            messagebox.showwarning("Campos vacíos", "Completa todos los campos.", parent=self)
            return
        
        try:
            cantidad = int(cantidad)
            precio_adq = float(precio_adq)
            precio_venta = float(precio_venta)
        except ValueError:
            messagebox.showerror("Error", "Cantidad, precio adquirido y precio venta deben ser números.", parent=self)
            return
        
        try:
            conn = sqlite3.connect("inventario.db")
            c = conn.cursor()
            c.execute('INSERT INTO repuestos (codigo, tipo, descripcion, cantidad, marca, precio_adquirido, precio_venta) VALUES (?, ?, ?, ?, ?, ?, ?)',
                      (codigo, tipo, desc, cantidad, marca, precio_adq, precio_venta))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Repuesto agregado correctamente.", parent=self)
            self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}", parent=self)

class ModalEditar(ctk.CTkToplevel):
    def __init__(self, parent, callback, repuesto):
        super().__init__(parent)
        self.callback = callback
        self.repuesto_id = repuesto['id']
        self.title("Editar Repuesto")
        self.geometry("550x680")
        self.resizable(False, False)
        
        # Centrar ventana
        self.transient(parent)
        
        # Título
        label_titulo = ctk.CTkLabel(self, text=f"EDITAR REPUESTO - ID: {repuesto['id']}", font=ctk.CTkFont(size=20, weight="bold"), text_color="#ff9800")
        label_titulo.pack(pady=(20, 15))
        
        # Frame para el formulario con borde visible
        frame_formulario = ctk.CTkFrame(self, corner_radius=10, border_width=2, border_color="#ff9800", fg_color="#1a1a1a")
        frame_formulario.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Frame interno para campos con padding
        frame_campos = ctk.CTkFrame(frame_formulario, fg_color="transparent")
        frame_campos.pack(padx=25, pady=20, fill="both", expand=True)
        
        # Campos del formulario con valores actuales
        ctk.CTkLabel(frame_campos, text="Codigo:", font=ctk.CTkFont(size=13, weight="bold"), anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 5), padx=5)
        self.entry_codigo = ctk.CTkEntry(frame_campos, height=35)
        self.entry_codigo.insert(0, repuesto['codigo'] if repuesto['codigo'] else "")
        self.entry_codigo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15), padx=5)
        
        ctk.CTkLabel(frame_campos, text="Tipo:", font=ctk.CTkFont(size=13, weight="bold"), anchor="w").grid(row=2, column=0, sticky="w", pady=(0, 5), padx=5)
        self.entry_tipo = ctk.CTkEntry(frame_campos, height=35)
        self.entry_tipo.insert(0, repuesto['tipo'] if repuesto['tipo'] else "")
        self.entry_tipo.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 15), padx=5)
        
        ctk.CTkLabel(frame_campos, text="Descripcion:", font=ctk.CTkFont(size=13, weight="bold"), anchor="w").grid(row=4, column=0, sticky="w", pady=(0, 5), padx=5)
        self.entry_desc = ctk.CTkEntry(frame_campos, height=35)
        self.entry_desc.insert(0, repuesto['descripcion'] if repuesto['descripcion'] else "")
        self.entry_desc.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 15), padx=5)
        
        ctk.CTkLabel(frame_campos, text="Cantidad:", font=ctk.CTkFont(size=13, weight="bold"), anchor="w").grid(row=6, column=0, sticky="w", pady=(0, 5), padx=5)
        self.entry_cantidad = ctk.CTkEntry(frame_campos, height=35)
        self.entry_cantidad.insert(0, str(repuesto['cantidad']) if repuesto['cantidad'] else "0")
        self.entry_cantidad.grid(row=7, column=0, sticky="ew", pady=(0, 15), padx=(5, 10))
        
        ctk.CTkLabel(frame_campos, text="Marca:", font=ctk.CTkFont(size=13, weight="bold"), anchor="w").grid(row=6, column=1, sticky="w", pady=(0, 5), padx=5)
        self.entry_marca = ctk.CTkEntry(frame_campos, height=35)
        self.entry_marca.insert(0, repuesto['marca'] if repuesto['marca'] else "")
        self.entry_marca.grid(row=7, column=1, sticky="ew", pady=(0, 15), padx=(10, 5))
        
        ctk.CTkLabel(frame_campos, text="Precio Adquirido (S/):", font=ctk.CTkFont(size=13, weight="bold"), anchor="w").grid(row=8, column=0, sticky="w", pady=(0, 5), padx=5)
        self.entry_precio_adq = ctk.CTkEntry(frame_campos, height=35)
        self.entry_precio_adq.insert(0, str(repuesto['precio_adquirido']) if repuesto['precio_adquirido'] else "0.00")
        self.entry_precio_adq.grid(row=9, column=0, sticky="ew", pady=(0, 15), padx=(5, 10))
        
        ctk.CTkLabel(frame_campos, text="Precio Venta (S/):", font=ctk.CTkFont(size=13, weight="bold"), anchor="w").grid(row=8, column=1, sticky="w", pady=(0, 5), padx=5)
        self.entry_precio_venta = ctk.CTkEntry(frame_campos, height=35)
        self.entry_precio_venta.insert(0, str(repuesto['precio_venta']) if repuesto['precio_venta'] else "0.00")
        self.entry_precio_venta.grid(row=9, column=1, sticky="ew", pady=(0, 15), padx=(10, 5))
        
        # Configurar peso de columnas
        frame_campos.grid_columnconfigure(0, weight=1)
        frame_campos.grid_columnconfigure(1, weight=1)
        
        # Botones
        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.pack(pady=(0, 20))
        
        btn_guardar = ctk.CTkButton(frame_botones, text="Guardar Cambios", command=self.guardar, fg_color="#28a745", hover_color="#218838", height=40, width=180, font=ctk.CTkFont(size=14, weight="bold"))
        btn_guardar.pack(side="left", padx=10)
        
        btn_cancelar = ctk.CTkButton(frame_botones, text="Cancelar", command=self.destroy, fg_color="#dc3545", hover_color="#c82333", height=40, width=180, font=ctk.CTkFont(size=14, weight="bold"))
        btn_cancelar.pack(side="left", padx=10)
        
        # Aplicar grab después de que todo esté creado
        self.after(10, self.grab_set)
    
    def guardar(self):
        codigo = self.entry_codigo.get().strip()
        tipo = self.entry_tipo.get().strip()
        desc = self.entry_desc.get().strip()
        cantidad = self.entry_cantidad.get().strip()
        marca = self.entry_marca.get().strip()
        precio_adq = self.entry_precio_adq.get().strip()
        precio_venta = self.entry_precio_venta.get().strip()
        
        if not (codigo and tipo and desc and cantidad and marca and precio_adq and precio_venta):
            messagebox.showwarning("Campos vacíos", "Completa todos los campos.", parent=self)
            return
        
        try:
            cantidad = int(cantidad)
            precio_adq = float(precio_adq)
            precio_venta = float(precio_venta)
        except ValueError:
            messagebox.showerror("Error", "Cantidad, precio adquirido y precio venta deben ser números.", parent=self)
            return
        
        try:
            conn = sqlite3.connect("inventario.db")
            c = conn.cursor()
            c.execute('''
                UPDATE repuestos SET codigo=?, tipo=?, descripcion=?, cantidad=?, marca=?, precio_adquirido=?, precio_venta=?
                WHERE id=?
            ''', (codigo, tipo, desc, cantidad, marca, precio_adq, precio_venta, self.repuesto_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Repuesto actualizado correctamente.", parent=self)
            self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}", parent=self)

# --- FUNCIONES CRUD ---
def listar_repuestos():
    for row in tree.get_children():
        tree.delete(row)
    conn = sqlite3.connect("inventario.db")
    conn.row_factory = sqlite3.Row  # Para acceder por nombre de columna
    c = conn.cursor()
    c.execute('SELECT id, codigo, tipo, descripcion, cantidad, marca, precio_adquirido, precio_venta FROM repuestos')
    for row in c.fetchall():
        # Insertar en el orden correcto de las columnas de la tabla
        tree.insert('', 'end', values=(row['id'], row['codigo'], row['tipo'], row['descripcion'], row['cantidad'], row['marca'], row['precio_adquirido'], row['precio_venta']))
    conn.close()

def eliminar_repuesto():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Selecciona", "Selecciona un repuesto para eliminar.")
        return
    item = tree.item(selected[0])
    repuesto_id = item['values'][0]
    
    respuesta = messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este repuesto?")
    if not respuesta:
        return
    
    conn = sqlite3.connect("inventario.db")
    c = conn.cursor()
    c.execute('DELETE FROM repuestos WHERE id=?', (repuesto_id,))
    conn.commit()
    conn.close()
    listar_repuestos()
    cargar_filtros()

def abrir_modal_agregar():
    modal = ModalAgregar(app, lambda: [listar_repuestos(), cargar_filtros()])

def abrir_modal_editar(event):
    selected = tree.selection()
    if not selected:
        return
    item = tree.item(selected[0])
    valores = item['values']
    # Crear diccionario con nombres de columnas para evitar confusión
    repuesto = {
        'id': valores[0],
        'codigo': valores[1],
        'tipo': valores[2],
        'descripcion': valores[3],
        'cantidad': valores[4],
        'marca': valores[5],
        'precio_adquirido': valores[6],
        'precio_venta': valores[7]
    }
    modal = ModalEditar(app, lambda: [listar_repuestos(), cargar_filtros()], repuesto)

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
def limpiar_filtros():
    filtro_marca.set("")
    filtro_tipo.set("")
    busqueda_desc.set("")

def cargar_filtros():
    conn = sqlite3.connect("inventario.db")
    c = conn.cursor()
    c.execute('SELECT DISTINCT marca FROM repuestos')
    marcas = [row[0] for row in c.fetchall()]
    combo_marca.configure(values=[""] + marcas)

    c.execute('SELECT DISTINCT tipo FROM repuestos')
    tipos = [row[0] for row in c.fetchall()]
    combo_tipo.configure(values=[""] + tipos)

    conn.close()

# --- INTERFAZ ---
app = ctk.CTk()
app.title("Inventario de Repuestos")
app.geometry("1280x720")
app.configure(fg_color="#2e2e2e")

filtro_marca = ctk.StringVar()
filtro_tipo = ctk.StringVar()
busqueda_desc = ctk.StringVar()

# Título y botones superiores
header_frame = ctk.CTkFrame(app)
header_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky='ew')

label_titulo = ctk.CTkLabel(header_frame, text="Inventario de Repuestos", font=ctk.CTkFont(size=24, weight="bold"))
label_titulo.pack(side="left", padx=20)

btn_agregar = ctk.CTkButton(header_frame, text="➕ Agregar Repuesto", command=abrir_modal_agregar, fg_color="#28a745", hover_color="#218838", corner_radius=10, height=40, width=200)
btn_agregar.pack(side="right", padx=10)

btn_eliminar = ctk.CTkButton(header_frame, text="🗑️ Eliminar", command=eliminar_repuesto, fg_color="#dc3545", hover_color="#c82333", corner_radius=10, height=40, width=150)
btn_eliminar.pack(side="right", padx=10)

# Filtros
filter_frame = ctk.CTkFrame(app)
filter_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky='ew')

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

btn_buscar = ctk.CTkButton(filter_frame, text="🔍 Buscar", command=filtrar_repuestos, fg_color="#007bff", hover_color="#0056b3", corner_radius=10)
btn_buscar.pack(side='left', padx=5)
btn_reset = ctk.CTkButton(filter_frame, text="🔄 Restablecer", command=lambda: [listar_repuestos(), limpiar_filtros(), cargar_filtros()], fg_color="#6c757d", hover_color="#5a6268", corner_radius=10)
btn_reset.pack(side='left', padx=5)

# Tabla
columns = ("ID", "Código", "Tipo", "Descripción", "Cantidad", "Marca", "Precio Adquirido", "Precio Venta")
tree = ttk.Treeview(app, columns=columns, show='headings')

col_widths = {
    "ID": 60,
    "Código": 100,
    "Tipo": 100,
    "Descripción": 250,
    "Cantidad": 80,
    "Marca": 120,
    "Precio Adquirido": 130,
    "Precio Venta": 130
}

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=col_widths.get(col, 100))

tree.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky='nsew')
tree.bind('<Double-1>', abrir_modal_editar)

# Configurar peso de las filas para que la tabla se expanda
app.grid_rowconfigure(2, weight=1)
app.grid_columnconfigure(0, weight=1)

# Inicialización
conectar_db()
listar_repuestos()
cargar_filtros()

app.mainloop()
