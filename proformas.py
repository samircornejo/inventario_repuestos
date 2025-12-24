import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
import os

# Configuración inicial
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Variables globales
carrito = []

# --- CONEXIÓN BD ---
def obtener_productos(filtro_tipo="", filtro_busqueda=""):
    conn = sqlite3.connect("inventario.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    query = "SELECT id, codigo, tipo, descripcion, cantidad, marca, precio_adquirido, precio_venta FROM repuestos WHERE 1=1"
    params = []
    
    if filtro_tipo:
        query += " AND tipo LIKE ?"
        params.append(f"%{filtro_tipo}%")
    
    if filtro_busqueda:
        query += " AND (codigo LIKE ? OR descripcion LIKE ? OR marca LIKE ?)"
        params.extend([f"%{filtro_busqueda}%", f"%{filtro_busqueda}%", f"%{filtro_busqueda}%"])
    
    c.execute(query, params)
    productos = c.fetchall()
    conn.close()
    return productos

# --- FUNCIONES CARRITO ---
class DialogoCantidad(ctk.CTkToplevel):
    def __init__(self, parent, producto, max_cantidad):
        super().__init__(parent)
        self.resultado = None
        self.producto = producto
        self.max_cantidad = max_cantidad
        
        self.title("Seleccionar Cantidad")
        self.geometry("450x450")
        self.resizable(False, False)
        self.transient(parent)
        
        # Información del producto
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(pady=15, padx=20, fill="x")
        
        ctk.CTkLabel(info_frame, text=f"Producto: {producto['descripcion']}", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=5)
        ctk.CTkLabel(info_frame, text=f"Codigo: {producto['codigo']}", font=ctk.CTkFont(size=12)).pack(pady=2)
        ctk.CTkLabel(info_frame, text=f"Stock disponible: {max_cantidad}", font=ctk.CTkFont(size=12)).pack(pady=2)
        ctk.CTkLabel(info_frame, text=f"Precio: S/ {producto['precio_venta']:.2f}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#28a745").pack(pady=2)
        
        # Campo de cantidad
        cantidad_frame = ctk.CTkFrame(self)
        cantidad_frame.pack(pady=15, padx=20, fill="x")
        
        ctk.CTkLabel(cantidad_frame, text="Cantidad:", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=5)
        self.entry_cantidad = ctk.CTkEntry(cantidad_frame, height=40, font=ctk.CTkFont(size=14), justify="center")
        self.entry_cantidad.pack(pady=5, fill="x", padx=20)
        self.entry_cantidad.insert(0, "1")
        self.entry_cantidad.focus()
        
        # Subtotal estimado
        subtotal_frame = ctk.CTkFrame(self)
        subtotal_frame.pack(pady=10, padx=20, fill="x")
        
        self.label_subtotal = ctk.CTkLabel(subtotal_frame, text=f"Subtotal: S/ {producto['precio_venta']:.2f}", font=ctk.CTkFont(size=14, weight="bold"))
        self.label_subtotal.pack(pady=10)
        
        # Actualizar subtotal al cambiar cantidad
        self.entry_cantidad.bind('<KeyRelease>', self.actualizar_subtotal)
        
        # Botones
        btn_agregar = ctk.CTkButton(self, text="AGREGAR", command=self.aceptar, width=200, height=40)
        btn_agregar.pack(pady=10)
        
        btn_cancelar = ctk.CTkButton(self, text="CANCELAR", command=self.cancelar, width=200, height=40)
        btn_cancelar.pack(pady=5)
        
        self.after(10, self.grab_set)
        self.wait_window()
    
    def actualizar_subtotal(self, event=None):
        try:
            cantidad = int(self.entry_cantidad.get())
            if cantidad > 0:
                subtotal = cantidad * self.producto['precio_venta']
                self.label_subtotal.configure(text=f"Subtotal: S/ {subtotal:.2f}")
        except:
            pass
    
    def aceptar(self):
        try:
            cantidad = int(self.entry_cantidad.get())
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor a 0", parent=self)
                return
            if cantidad > self.max_cantidad:
                messagebox.showerror("Error", f"Stock insuficiente. Maximo disponible: {self.max_cantidad}", parent=self)
                return
            self.resultado = cantidad
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Ingresa un numero valido", parent=self)
    
    def cancelar(self):
        self.destroy()

def agregar_al_carrito_con_dialogo(producto_data):
    # Verificar stock disponible
    stock_disponible = producto_data['cantidad']
    
    # Verificar cuánto ya está en el carrito
    cantidad_en_carrito = 0
    for prod in carrito:
        if prod["id"] == producto_data['id']:
            cantidad_en_carrito = prod["cantidad"]
            break
    
    stock_restante = stock_disponible - cantidad_en_carrito
    
    if stock_restante <= 0:
        messagebox.showwarning("Sin stock", "No hay mas stock disponible de este producto.")
        return
    
    # Mostrar diálogo para seleccionar cantidad
    dialogo = DialogoCantidad(app, producto_data, stock_restante)
    
    if dialogo.resultado:
        # Verificar si ya existe en el carrito
        encontrado = False
        for prod in carrito:
            if prod["id"] == producto_data['id']:
                prod["cantidad"] += dialogo.resultado
                encontrado = True
                break
        
        if not encontrado:
            carrito.append({
                "id": producto_data['id'],
                "codigo": producto_data['codigo'],
                "tipo": producto_data['tipo'],
                "descripcion": producto_data['descripcion'],
                "precio": producto_data['precio_venta'],
                "cantidad": dialogo.resultado
            })
        
        actualizar_resumen()
        messagebox.showinfo("Agregado", f"Se agregaron {dialogo.resultado} unidad(es) al carrito")

def limpiar_carrito():
    global carrito
    if carrito:
        respuesta = messagebox.askyesno("Confirmar", "¿Deseas limpiar todo el carrito?")
        if respuesta:
            carrito = []
            actualizar_resumen()

def actualizar_resumen():
    resumen_textbox.configure(state="normal")
    resumen_textbox.delete("1.0", "end")
    
    if not carrito:
        resumen_textbox.insert("end", "El carrito esta vacio\n\n")
        resumen_textbox.insert("end", "Haz doble clic en un producto\npara agregarlo")
        resumen_textbox.configure(state="disabled")
        return
    
    total = 0
    resumen_textbox.insert("end", "PRODUCTOS EN CARRITO\n")
    resumen_textbox.insert("end", "=" * 45 + "\n\n")
    
    for i, p in enumerate(carrito, 1):
        subtotal = p["cantidad"] * p["precio"]
        resumen_textbox.insert("end", f"{i}. [{p['codigo']}] {p['descripcion']}\n")
        resumen_textbox.insert("end", f"   Tipo: {p['tipo']}\n")
        resumen_textbox.insert("end", f"   Cantidad: {p['cantidad']} x S/ {p['precio']:.2f} = S/ {subtotal:.2f}\n\n")
        total += subtotal
    
    resumen_textbox.insert("end", "=" * 45 + "\n")
    resumen_textbox.insert("end", f"TOTAL ESTIMADO: S/ {total:.2f}\n")
    resumen_textbox.insert("end", "=" * 45)
    resumen_textbox.configure(state="disabled")

def generar_pdf():
    if not carrito:
        messagebox.showwarning("Carrito vacio", "Agrega productos al carrito antes de generar el PDF.")
        return
    
    # Crear carpeta proformas si no existe
    if not os.path.exists("proformas"):
        os.makedirs("proformas")
    
    # Nombre del archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"proformas/proforma_{timestamp}.pdf"
    
    # Crear documento PDF
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para el título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Título
    elements.append(Paragraph("TODOREPUESTOS", title_style))
    elements.append(Paragraph("Proforma de Venta", styles['Heading2']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Fecha
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    elements.append(Paragraph(f"<b>Fecha:</b> {fecha_actual}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Crear tabla de productos
    data = [["Codigo", "Tipo", "Descripcion", "Cant.", "P. Unit.", "Subtotal"]]
    
    total = 0
    for p in carrito:
        subtotal = p["cantidad"] * p["precio"]
        data.append([
            p["codigo"],
            p["tipo"],
            p["descripcion"][:30],
            str(p["cantidad"]),
            f"S/ {p['precio']:.2f}",
            f"S/ {subtotal:.2f}"
        ])
        total += subtotal
    
    # Agregar fila de total
    data.append(["", "", "", "", "TOTAL:", f"S/ {total:.2f}"])
    
    # Crear tabla con estilos
    table = Table(data, colWidths=[0.8*inch, 1*inch, 2.5*inch, 0.6*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('GRID', (0, 0), (-1, -2), 1, colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d4edda')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#155724')),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Nota al pie
    nota_style = ParagraphStyle(
        'NotaStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey
    )
    elements.append(Paragraph("Esta proforma tiene validez de 7 dias.", nota_style))
    elements.append(Paragraph("Los precios estan expresados en Soles (S/).", nota_style))
    
    # Generar PDF
    doc.build(elements)
    
    messagebox.showinfo("PDF Generado", f"Proforma guardada exitosamente en:\n{os.path.abspath(filename)}")
    
    # Opcional: Abrir el PDF automáticamente
    try:
        os.system(f'xdg-open "{filename}"')
    except:
        pass

# --- INTERFAZ ---
app = ctk.CTk()
app.title("Modulo Proformas - TodoRepuestos")
app.geometry("1400x750")

# Sección izquierda: productos
frame_izquierda = ctk.CTkFrame(app)
frame_izquierda.pack(side="left", fill="both", expand=True, padx=10, pady=10)

# Header
header_frame = ctk.CTkFrame(frame_izquierda)
header_frame.pack(pady=10, padx=10, fill="x")

ctk.CTkLabel(header_frame, text="Buscar Repuestos", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=5)

# Filtros
filtro_frame = ctk.CTkFrame(frame_izquierda)
filtro_frame.pack(pady=5, padx=10, fill="x")

filtro_tipo_var = ctk.StringVar()
filtro_busqueda_var = ctk.StringVar()

ctk.CTkLabel(filtro_frame, text="Tipo:").pack(side="left", padx=5)
entry_tipo = ctk.CTkEntry(filtro_frame, textvariable=filtro_tipo_var, placeholder_text="Filtrar por tipo", width=150)
entry_tipo.pack(side="left", padx=5)

ctk.CTkLabel(filtro_frame, text="Buscar:").pack(side="left", padx=5)
entry_busqueda = ctk.CTkEntry(filtro_frame, textvariable=filtro_busqueda_var, placeholder_text="Codigo, descripcion o marca", width=250)
entry_busqueda.pack(side="left", padx=5)

def cargar_tabla_productos():
    for row in tree.get_children():
        tree.delete(row)
    filtro_tipo = filtro_tipo_var.get()
    filtro_busq = filtro_busqueda_var.get()
    productos = obtener_productos(filtro_tipo, filtro_busq)
    
    for prod in productos:
        tree.insert('', 'end', values=(
            prod['id'], 
            prod['codigo'], 
            prod['tipo'], 
            prod['descripcion'], 
            prod['cantidad'], 
            prod['marca'], 
            f"S/ {prod['precio_adquirido']:.2f}",
            f"S/ {prod['precio_venta']:.2f}"
        ))

btn_buscar = ctk.CTkButton(filtro_frame, text="Buscar", command=cargar_tabla_productos, fg_color="#007bff", hover_color="#0056b3", width=100)
btn_buscar.pack(side="left", padx=5)

btn_limpiar = ctk.CTkButton(filtro_frame, text="Limpiar", command=lambda: [filtro_tipo_var.set(""), filtro_busqueda_var.set(""), cargar_tabla_productos()], fg_color="#6c757d", hover_color="#5a6268", width=100)
btn_limpiar.pack(side="left", padx=5)

# Tabla de productos
columns = ("ID", "Codigo", "Tipo", "Descripcion", "Stock", "Marca", "P. Adquirido", "P. Venta")
tree = ttk.Treeview(frame_izquierda, columns=columns, show="headings", height=20)
for col in columns:
    tree.heading(col, text=col)
    if col == "Descripcion":
        tree.column(col, width=250)
    elif col == "Codigo":
        tree.column(col, width=100)
    elif col == "Tipo":
        tree.column(col, width=120)
    elif col == "Stock":
        tree.column(col, width=70)
    else:
        tree.column(col, width=100)
tree.pack(fill="both", expand=True, padx=10, pady=5)

def agregar_producto_evento(event):
    selected = tree.selection()
    if not selected:
        return
    
    item_values = tree.item(selected[0])["values"]
    
    # Obtener datos completos del producto
    conn = sqlite3.connect("inventario.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM repuestos WHERE id=?", (item_values[0],))
    producto = c.fetchone()
    conn.close()
    
    if producto:
        agregar_al_carrito_con_dialogo(producto)

tree.bind('<Double-1>', agregar_producto_evento)

# Instrucciones
ctk.CTkLabel(frame_izquierda, text="Haz doble clic en un producto para agregarlo al carrito", font=ctk.CTkFont(size=11), text_color="gray").pack(pady=5)

# Sección derecha: resumen
frame_derecha = ctk.CTkFrame(app, width=450)
frame_derecha.pack(side="right", fill="y", padx=10, pady=10)
frame_derecha.pack_propagate(False)

label_resumen = ctk.CTkLabel(frame_derecha, text="CARRITO DE PROFORMA", font=ctk.CTkFont(size=18, weight="bold"))
label_resumen.pack(pady=15)

resumen_textbox = ctk.CTkTextbox(frame_derecha, height=500, width=420, font=ctk.CTkFont(size=12))
resumen_textbox.pack(padx=10, pady=10)
resumen_textbox.configure(state="disabled")

# Botones de acción
btn_frame = ctk.CTkFrame(frame_derecha)
btn_frame.pack(pady=10)

btn_limpiar_carrito = ctk.CTkButton(btn_frame, text="Limpiar Carrito", command=limpiar_carrito, fg_color="#ffc107", hover_color="#e0a800", width=200, height=40)
btn_limpiar_carrito.pack(pady=5)

btn_generar = ctk.CTkButton(btn_frame, text="Generar PDF", command=generar_pdf, fg_color="#28a745", hover_color="#218838", width=200, height=50, font=ctk.CTkFont(size=16, weight="bold"))
btn_generar.pack(pady=10)

# Inicializar
cargar_tabla_productos()
actualizar_resumen()
app.mainloop()
