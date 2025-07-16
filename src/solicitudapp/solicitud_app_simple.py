"""
Vista principal simplificada - Versión Profesional.
"""
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, simpledialog
from typing import List, Optional
import datetime
import logging

try:
    from src.solicitudapp.logic_solicitud import SolicitudLogica
except ImportError:
    SolicitudLogica = None

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppConfig:
    """Configuración simplificada."""
    TIPOS_SOLICITUD = ["Compra", "Servicio"]
    DEPARTAMENTOS = ["Administracion", "Ventas", "Servicio", "Refacciones", "HyP"]
    CATEGORIAS = ["Comer", "Fleet", "Semis", "Refa", "Serv", "HyP", "Admin"]
    WINDOW_SIZE = "1024x850"
    THEME = "darkly"
    MAX_CONCEPTOS_RECOMENDADOS = 8


class SolicitudAppSimple(tb.Frame):
    """
    Aplicación simplificada para gestión de solicitudes de compra.
    """
    
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        
        # Control de lógica
        self.control = SolicitudLogica() if SolicitudLogica else None
        
        # Estado
        self.solicitudes_restantes = 0
        
        # Widgets
        self.entries_prov = {}
        self.entries_sol = {}
        self.entries_totales = {}
        self.entries_categorias = {}
        self.tree = None
        self.comentarios = None
        self.lbl_sol_rest = None
        self.dividir_var = None
        
        self._build_ui()
        logger.info("Aplicación inicializada correctamente")
    
    def _build_ui(self):
        """Construye la interfaz de usuario."""
        # Frame superior
        frame_sup = tb.Frame(self)
        frame_sup.pack(fill=X, padx=15, pady=10)
        
        # Proveedor
        self._create_proveedor_frame(frame_sup)
        
        # Solicitud
        self._create_solicitud_frame(frame_sup)
        
        # Tabla
        self._create_table_frame()
        
        # Frame inferior
        self._create_bottom_frame()
        
        # Comentarios
        self._create_comments()
        
        # Barra de estado
        self._create_status_bar()
    
    def _create_proveedor_frame(self, parent):
        """Crea el frame de proveedor."""
        frame_prov = tb.Labelframe(parent, text="Datos de proveedor", width=350)
        frame_prov.pack_propagate(False)
        frame_prov.pack(side=LEFT, fill=Y, expand=False, padx=(0,10), pady=0)
        
        campos = ["Nombre", "RFC", "Teléfono", "Correo", "Contacto"]
        for i, campo in enumerate(campos):
            tb.Label(frame_prov, text=f"{campo}:").grid(row=i, column=0, sticky=E, padx=5, pady=4)
            entry = tb.Entry(frame_prov, width=40, bootstyle="dark")
            entry.grid(row=i, column=1, padx=5, pady=4)
            self.entries_prov[campo] = entry
    
    def _create_solicitud_frame(self, parent):
        """Crea el frame de solicitud."""
        frame_sol = tb.Labelframe(parent, text="Datos de la solicitud", width=320)
        frame_sol.pack_propagate(False)
        frame_sol.pack(side=RIGHT, fill=Y, expand=False, padx=(10,0), pady=0)
        
        campos = ["Fecha", "Clase", "Tipo", "Depa", "Folio"]
        for i, campo in enumerate(campos):
            tb.Label(frame_sol, text=f"{campo}:").grid(row=i, column=0, sticky=E, padx=5, pady=4)
            
            if campo == "Tipo":
                widget = tb.Combobox(frame_sol, values=AppConfig.TIPOS_SOLICITUD, width=22, bootstyle="dark")
                widget.set("Compra")
            elif campo == "Depa":
                widget = tb.Combobox(frame_sol, values=AppConfig.DEPARTAMENTOS, width=22, bootstyle="dark")
                widget.set("Administracion")
            elif campo == "Fecha":
                widget = tb.DateEntry(frame_sol, width=19, bootstyle="dark")
            else:
                widget = tb.Entry(frame_sol, width=24, bootstyle="dark")
            
            widget.grid(row=i, column=1, padx=5, pady=4, sticky=E)
            self.entries_sol[campo] = widget
    
    def _create_table_frame(self):
        """Crea la tabla de conceptos."""
        frame_tabla = tb.Frame(self)
        frame_tabla.pack(fill=BOTH, expand=True, padx=15, pady=10)
        
        # Tabla
        cols = ("Cantidad", "Descripción", "Precio", "Total")
        self.tree = tb.Treeview(frame_tabla, columns=cols, show="headings", height=6, bootstyle="dark")
        
        for col in cols:
            self.tree.heading(col, text=col)
            if col == "Cantidad":
                self.tree.column(col, width=80, anchor=W, stretch=False)
            elif col == "Descripción":
                self.tree.column(col, width=400, anchor=W, stretch=True)
            elif col == "Precio":
                self.tree.column(col, width=80, anchor=W, stretch=False)
            elif col == "Total":
                self.tree.column(col, width=80, anchor=W, stretch=False)
        
        self.tree.pack(fill=BOTH, expand=True)
        
        # Botones
        frame_btn = tb.Frame(frame_tabla)
        frame_btn.pack(fill=X, padx=15, pady=10)
        
        tb.Button(frame_btn, text="➕", width=6, command=self.agregar_concepto, bootstyle="success").pack(side=RIGHT, padx=(0,5))
        tb.Button(frame_btn, text="➖", width=6, command=self.eliminar_concepto, bootstyle="danger").pack(side=RIGHT, padx=(0,5))
        tb.Button(frame_btn, text="✏️", width=6, command=self.editar_concepto, bootstyle="warning").pack(side=RIGHT, padx=(0,5))
    
    def _create_bottom_frame(self):
        """Crea el frame inferior."""
        frame_inf = tb.Frame(self)
        frame_inf.pack(fill=X, padx=15, pady=10)
        
        # Categorías
        frame_cat = tb.Labelframe(frame_inf, text="Categorías", width=500)
        frame_cat.pack_propagate(False)
        frame_cat.pack(side=LEFT, fill=Y, expand=False, padx=(0,10))
        
        for col, categoria in enumerate(AppConfig.CATEGORIAS):
            tb.Label(frame_cat, text=categoria).grid(row=0, column=col, padx=8, pady=(0,0), sticky="nw")
            entry = tb.Entry(frame_cat, width=5, bootstyle="dark")
            entry.grid(row=1, column=col, padx=8, pady=(0,0), sticky="new")
            self.entries_categorias[categoria] = entry
        
        # Botones de categorías
        frame_cat_btns = tb.Frame(frame_cat)
        frame_cat_btns.grid(row=0, column=len(AppConfig.CATEGORIAS)+1, rowspan=2, padx=(16,0), pady=(0,6), sticky="ns")
        
        tb.Button(frame_cat_btns, text="Limpiar", bootstyle="warning", width=12, command=self.limpiar_categorias).pack(pady=(0,8), fill="x")
        tb.Button(frame_cat_btns, text="Guardar", bootstyle="success", width=12, command=self.guardar_categorias).pack(fill="x")
        
        # Totales
        frame_tot = tb.Labelframe(frame_inf, text="Totales", width=320)
        frame_tot.pack_propagate(False)
        frame_tot.pack(side=RIGHT, fill=Y, expand=False, padx=(10,0))
        
        for i, label in enumerate(["Subtotal", "Ret", "IVA", "TOTAL"]):
            tb.Label(frame_tot, text=label).grid(row=i, column=0, sticky=E, padx=5, pady=4)
            entry = tb.Entry(frame_tot, width=24, bootstyle="dark")
            entry.grid(row=i, column=1, padx=5, pady=4)
            self.entries_totales[label] = entry
    
    def _create_comments(self):
        """Crea la sección de comentarios."""
        tb.Label(self, text="Comentarios").pack(anchor=W, padx=18, pady=(10,0))
        self.comentarios = tb.Text(self, height=3)
        self.comentarios.pack(fill=X, padx=15, pady=5)
    
    def _create_status_bar(self):
        """Crea la barra de estado."""
        frame_barra = tb.Frame(self)
        frame_barra.pack(fill=X, side=BOTTOM, padx=15, pady=10)
        
        self.lbl_sol_rest = tb.Label(frame_barra, text=f"Solicitudes restantes: {self.solicitudes_restantes}")
        self.lbl_sol_rest.pack(side=LEFT, padx=2)
        
        tb.Button(frame_barra, text="Generar", bootstyle="success", command=self.generar).pack(side=RIGHT, padx=5)
        tb.Button(frame_barra, text="Cargar XML", bootstyle="primary", command=self.cargar_xml).pack(side=RIGHT, padx=5)
        
        self.dividir_var = tb.BooleanVar()
        tb.Checkbutton(frame_barra, text="Dividir", variable=self.dividir_var, bootstyle="info").pack(side=RIGHT, padx=5)
    
    def cargar_xml(self):
        """Carga archivos XML."""
        try:
            rutas = filedialog.askopenfilenames(
                title="Selecciona los archivos XML",
                filetypes=[("Archivos XML", "*.xml")]
            )
            
            if not rutas:
                return
            
            if self.control:
                self.limpiar_todo()
                self.control.agregar_solicitud(rutas)
                self.actualizar_solicitudes_restantes()
                self.rellenar_campos()
                logger.info(f"Cargados {len(rutas)} archivos XML")
            else:
                messagebox.showinfo("Info", "Sistema de carga XML no disponible")
                
        except Exception as e:
            logger.error(f"Error al cargar XML: {e}")
            messagebox.showerror("Error", f"Error al cargar XML: {str(e)}")
    
    def rellenar_campos(self):
        """Rellena los campos con datos del XML."""
        if not self.control:
            return
            
        try:
            datos = self.control.get_solicitud()
            if not datos:
                return
            
            # Rellenar proveedor
            self.entries_prov["Nombre"].insert(0, getattr(datos, "nombre_emisor", ""))
            self.entries_prov["RFC"].insert(0, getattr(datos, "rfc_emisor", ""))
            
            # Rellenar solicitud
            self.entries_sol["Folio"].insert(0, getattr(datos, "folio", ""))
            
            # Fecha actual
            fecha_hoy = datetime.date.today().strftime("%d/%m/%Y")
            self.entries_sol["Fecha"].entry.delete(0, "end")
            self.entries_sol["Fecha"].entry.insert(0, fecha_hoy)
            
            # Rellenar totales
            self.entries_totales["Subtotal"].insert(0, getattr(datos, "subtotal", ""))
            self.entries_totales["IVA"].insert(0, getattr(datos, "iva", ""))
            self.entries_totales["TOTAL"].insert(0, getattr(datos, "total", ""))
            
            # Comentarios
            comentario = f"Factura: {getattr(datos, 'serie', '')} {getattr(datos, 'folio', '')}".strip()
            self.comentarios.insert("1.0", comentario)
            
            # Conceptos
            conceptos = getattr(datos, "conceptos", [])
            for concepto in conceptos:
                self.tree.insert("", "end", values=concepto)
                
        except Exception as e:
            logger.error(f"Error al rellenar campos: {e}")
            messagebox.showerror("Error", f"Error al rellenar campos: {str(e)}")
    
    def agregar_concepto(self):
        """Agrega un concepto."""
        self._mostrar_popup_concepto("Agregar concepto", "Agregar", self._insertar_concepto)
    
    def editar_concepto(self):
        """Edita el concepto seleccionado."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un concepto para editar.")
            return
        
        item_id = selected[0]
        valores_actuales = list(self.tree.item(item_id, "values"))
        
        def actualizar_concepto(values):
            self.tree.item(item_id, values=values)
        
        self._mostrar_popup_concepto("Editar concepto", "Guardar", actualizar_concepto, valores_actuales)
    
    def eliminar_concepto(self):
        """Elimina el concepto seleccionado."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un concepto para eliminar.")
            return
        
        for item in selected:
            self.tree.delete(item)
    
    def _mostrar_popup_concepto(self, title, button_text, callback, valores_iniciales=None):
        """Muestra el popup para agregar/editar concepto."""
        popup = tk.Toplevel(self)
        popup.title(title)
        popup.geometry("720x120")
        popup.grab_set()
        
        labels = ["Cantidad", "Descripción", "Precio", "Total"]
        entries = {}
        
        for i, label in enumerate(labels):
            tk.Label(popup, text=label).grid(row=0, column=i, padx=10, pady=8, sticky="w")
            
            width = 70 if label == "Descripción" else 12
            entry = tk.Entry(popup, width=width)
            entry.grid(row=1, column=i, padx=10, pady=8)
            
            if valores_iniciales and i < len(valores_iniciales):
                entry.insert(0, valores_iniciales[i])
            
            entries[label] = entry
        
        def on_ok():
            values = [entries[l].get().strip() for l in labels]
            
            if not all(values):
                messagebox.showerror("Error", "Todos los campos son obligatorios.")
                return
            
            # Validar números
            try:
                float(values[0])  # Cantidad
                float(values[2])  # Precio
                float(values[3])  # Total
            except ValueError:
                messagebox.showerror("Error", "Cantidad, Precio y Total deben ser números válidos.")
                return
            
            callback(values)
            popup.destroy()
        
        tk.Button(popup, text=button_text, command=on_ok).grid(row=2, column=0, columnspan=len(labels), pady=12)
    
    def _insertar_concepto(self, values):
        """Inserta un concepto en la tabla."""
        self.tree.insert("", "end", values=values)
        
        # Comprobar número de conceptos
        if len(self.tree.get_children()) > AppConfig.MAX_CONCEPTOS_RECOMENDADOS:
            respuesta = messagebox.askyesno(
                "Demasiados conceptos",
                "La lista de conceptos es demasiado larga.\\n¿Prefiere usar un concepto general?"
            )
            if respuesta:
                self._agregar_concepto_general()
    
    def _agregar_concepto_general(self):
        """Agrega un concepto general."""
        descripcion = simpledialog.askstring(
            "Concepto general",
            "Escriba el concepto general que desea usar:"
        )
        if not descripcion:
            return
        
        if self.control:
            datos = self.control.get_solicitud()
            if datos:
                valores = ["1", descripcion, getattr(datos, "subtotal", ""), getattr(datos, "total", "")]
                self._mostrar_popup_concepto("Agregar concepto general", "Agregar", self._insertar_concepto, valores)
    
    def actualizar_solicitudes_restantes(self):
        """Actualiza el contador de solicitudes restantes."""
        if self.control:
            self.solicitudes_restantes = self.control.get_solicitudes_restantes()
            self.lbl_sol_rest.config(text=f"Solicitudes restantes: {self.solicitudes_restantes}")
    
    def limpiar_todo(self):
        """Limpia todos los campos."""
        # Limpiar proveedor
        for entry in self.entries_prov.values():
            entry.delete(0, "end")
        
        # Limpiar solicitud (mantener valores por defecto)
        for campo, widget in self.entries_sol.items():
            if campo == "Fecha":
                widget.entry.delete(0, "end")
            elif campo == "Tipo":
                widget.set("Compra")
            elif campo == "Depa":
                widget.set("Administracion")
            else:
                widget.delete(0, "end")
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Limpiar totales
        for entry in self.entries_totales.values():
            entry.delete(0, "end")
        
        # Limpiar categorías
        self.limpiar_categorias()
        
        # Limpiar comentarios
        self.comentarios.delete("1.0", "end")
    
    def limpiar_categorias(self):
        """Limpia las categorías."""
        for entry in self.entries_categorias.values():
            entry.delete(0, "end")
    
    def guardar_categorias(self):
        """Guarda las categorías."""
        messagebox.showinfo("Info", "Función de guardar categorías pendiente de implementar")
    
    def generar(self):
        """Genera el documento."""
        # Validaciones básicas
        proveedor_data = {k: v.get() for k, v in self.entries_prov.items()}
        if not proveedor_data["Nombre"] or not proveedor_data["RFC"]:
            messagebox.showerror("Error", "Nombre y RFC del proveedor son obligatorios")
            return
        
        if not self.tree.get_children():
            messagebox.showerror("Error", "Debe agregar al menos un concepto")
            return
        
        folio = self.entries_sol["Folio"].get()
        if not folio:
            messagebox.showerror("Error", "El folio es obligatorio")
            return
        
        messagebox.showinfo("Info", "Función de generar documento pendiente de implementar")


def main():
    """Función principal."""
    try:
        app = tb.Window(themename=AppConfig.THEME)
        app.title("Solicitud de Compra - Versión Profesional")
        app.geometry(AppConfig.WINDOW_SIZE)
        
        frame = SolicitudAppSimple(app)
        frame.pack(fill="both", expand=True)
        
        logger.info("Aplicación iniciada")
        app.mainloop()
        
    except Exception as e:
        logger.error(f"Error crítico: {e}")
        messagebox.showerror("Error crítico", f"Error al iniciar: {str(e)}")


if __name__ == "__main__":
    main()
