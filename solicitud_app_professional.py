"""
Vista principal de la aplicación - Versión Profesional.
"""
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, simpledialog
from typing import List, Optional
import datetime
import logging

from models.solicitud import Solicitud, Proveedor, Concepto, Totales
from services.validation import ValidationService
from config.app_config import AppConfig
from views.components import ProveedorFrame, SolicitudFrame, ConceptoPopup, BaseFrame
from logic_solicitud import SolicitudLogica

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SolicitudAppProfessional(tb.Frame):
    """
    Aplicación principal para gestión de solicitudes de compra.
    Versión profesional con arquitectura limpia y separación de responsabilidades.
    """
    
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        
        # Servicios
        self.validation_service = ValidationService()
        self.control = SolicitudLogica()
        
        # Estado de la aplicación
        self.solicitudes_restantes = 0
        self.solicitud_actual: Optional[Solicitud] = None
        
        # Componentes UI
        self.proveedor_frame: Optional[ProveedorFrame] = None
        self.solicitud_frame: Optional[SolicitudFrame] = None
        self.tree: Optional[tb.Treeview] = None
        self.entries_totales = {}
        self.entries_categorias = {}
        self.comentarios: Optional[tb.Text] = None
        self.lbl_sol_rest: Optional[tb.Label] = None
        self.dividir_var: Optional[tb.BooleanVar] = None
        
        self._build_ui()
        self._setup_bindings()
        logger.info("Aplicación inicializada correctamente")
    
    def _build_ui(self):
        """Construye la interfaz de usuario."""
        self._create_top_frame()
        self._create_table_frame()
        self._create_bottom_frame()
        self._create_comments_section()
        self._create_status_bar()
    
    def _create_top_frame(self):
        """Crea el frame superior con datos de proveedor y solicitud."""
        frame_sup = tb.Frame(self)
        frame_sup.pack(fill=X, padx=15, pady=10)
        
        # Frame de proveedor
        self.proveedor_frame = ProveedorFrame(frame_sup)
        self.proveedor_frame.pack(side=LEFT, fill=Y, expand=False, padx=(0, 10), pady=0)
        
        # Frame de solicitud
        self.solicitud_frame = SolicitudFrame(frame_sup)
        self.solicitud_frame.pack(side=RIGHT, fill=Y, expand=False, padx=(10, 0), pady=0)
    
    def _create_table_frame(self):
        """Crea el frame con la tabla de conceptos."""
        frame_tabla = tb.Frame(self)
        frame_tabla.pack(fill=BOTH, expand=True, padx=15, pady=10)
        
        # Tabla de conceptos
        cols = ("Cantidad", "Descripción", "Precio", "Total")
        self.tree = tb.Treeview(
            frame_tabla, 
            columns=cols, 
            show="headings", 
            height=6, 
            bootstyle="dark"
        )
        
        # Configurar columnas
        for col in cols:
            self.tree.heading(col, text=col)
            width = AppConfig.COLUMN_WIDTHS.get(col, 100)
            stretch = col == "Descripción"
            self.tree.column(col, width=width, anchor=W, stretch=stretch)
        
        self.tree.pack(fill=BOTH, expand=True)
        
        # Frame de botones de la tabla
        self._create_table_buttons(frame_tabla)
    
    def _create_table_buttons(self, parent):
        """Crea los botones para la tabla de conceptos."""
        frame_btn_tabla = tb.Frame(parent)
        frame_btn_tabla.pack(fill=X, padx=15, pady=10)
        
        btn_width = 6
        
        # Botón agregar
        tb.Button(
            frame_btn_tabla,
            text="➕",
            width=btn_width,
            command=self.agregar_concepto,
            bootstyle="success"
        ).pack(side=RIGHT, padx=(0, 5))
        
        # Botón eliminar
        tb.Button(
            frame_btn_tabla,
            text="➖",
            width=btn_width,
            command=self.eliminar_concepto_seleccionado,
            bootstyle="danger"
        ).pack(side=RIGHT, padx=(0, 5))
        
        # Botón editar
        tb.Button(
            frame_btn_tabla,
            text="✏️",
            width=btn_width,
            command=self.editar_concepto_seleccionado,
            bootstyle="warning"
        ).pack(side=RIGHT, padx=(0, 5))
    
    def _create_bottom_frame(self):
        """Crea el frame inferior con categorías y totales."""
        frame_inf = tb.Frame(self)
        frame_inf.pack(fill=X, padx=15, pady=10)
        
        # Frame de categorías
        self._create_categories_frame(frame_inf)
        
        # Frame de totales
        self._create_totals_frame(frame_inf)
    
    def _create_categories_frame(self, parent):
        """Crea el frame de categorías."""
        frame_cat = tb.Labelframe(parent, text="Categorías", width=500)
        frame_cat.pack_propagate(False)
        frame_cat.pack(side=LEFT, fill=Y, expand=False, padx=(0, 10))
        
        # Entradas de categorías
        for col, categoria in enumerate(AppConfig.CATEGORIAS):
            tb.Label(frame_cat, text=categoria).grid(
                row=0, column=col, padx=8, pady=(0, 0), sticky="nw"
            )
            entry = tb.Entry(frame_cat, width=5, bootstyle="dark")
            entry.grid(row=1, column=col, padx=8, pady=(0, 0), sticky="new")
            self.entries_categorias[categoria] = entry
        
        # Botones de categorías
        self._create_category_buttons(frame_cat)
        
        # Botones favoritos
        self._create_favorites_buttons(frame_cat)
    
    def _create_category_buttons(self, parent):
        """Crea los botones de limpiar y guardar para categorías."""
        frame_cat_btns = tb.Frame(parent)
        frame_cat_btns.grid(
            row=0, column=len(AppConfig.CATEGORIAS) + 1, 
            rowspan=3, padx=(16, 0), pady=(0, 6), sticky="ns"
        )
        
        tb.Button(
            frame_cat_btns,
            text="Limpiar",
            bootstyle="warning",
            width=12,
            command=self.limpiar_categorias
        ).pack(pady=(0, 8), fill="x", padx=(0, 5))
        
        tb.Button(
            frame_cat_btns,
            text="Guardar",
            bootstyle="success",
            width=12,
            command=self.guardar_categorias
        ).pack(pady=(0, 8), fill="x", padx=(0, 5))
    
    def _create_favorites_buttons(self, parent):
        """Crea los botones de favoritos."""
        frame_fav = tb.Frame(parent)
        frame_fav.grid(
            row=3, column=0, columnspan=len(AppConfig.CATEGORIAS) + 1,
            padx=8, pady=(10, 0), sticky="ew"
        )
        
        for i in range(5):
            tb.Button(
                frame_fav,
                text=f"Favorito {i + 1}",
                bootstyle="info",
                width=10,
                command=lambda idx=i: self.cargar_favorito(idx)
            ).grid(row=0, column=i, padx=4, pady=6, sticky="s")
        
        parent.grid_rowconfigure(3, weight=1)
    
    def _create_totals_frame(self, parent):
        """Crea el frame de totales."""
        frame_tot = tb.Labelframe(parent, text="Totales", width=320)
        frame_tot.pack_propagate(False)
        frame_tot.pack(side=RIGHT, fill=Y, expand=False, padx=(10, 0))
        
        totales_labels = ["Subtotal", "Ret", "IVA", "TOTAL"]
        
        for i, label in enumerate(totales_labels):
            tb.Label(frame_tot, text=label).grid(
                row=i, column=0, sticky=E, padx=5, pady=4
            )
            entry = tb.Entry(frame_tot, width=24, bootstyle="dark")
            entry.grid(row=i, column=1, padx=5, pady=4)
            self.entries_totales[label] = entry
    
    def _create_comments_section(self):
        """Crea la sección de comentarios."""
        tb.Label(self, text="Comentarios").pack(anchor=W, padx=18, pady=(10, 0))
        self.comentarios = tb.Text(self, height=3)
        self.comentarios.pack(fill=X, padx=15, pady=5)
    
    def _create_status_bar(self):
        """Crea la barra de estado y botones principales."""
        frame_barra = tb.Frame(self)
        frame_barra.pack(fill=X, side=BOTTOM, padx=15, pady=10)
        
        # Label de solicitudes restantes
        self.lbl_sol_rest = tb.Label(
            frame_barra, 
            text=f"Solicitudes restantes: {self.solicitudes_restantes}"
        )
        self.lbl_sol_rest.pack(side=LEFT, padx=2)
        
        # Botones principales
        tb.Button(
            frame_barra,
            text="Generar",
            bootstyle="success",
            command=self.generar
        ).pack(side=RIGHT, padx=5)
        
        tb.Button(
            frame_barra,
            text="Cargar XML",
            bootstyle="primary",
            command=self.cargar_xml
        ).pack(side=RIGHT, padx=5)
        
        # Checkbox dividir
        self.dividir_var = tb.BooleanVar()
        tb.Checkbutton(
            frame_barra,
            text="Dividir",
            variable=self.dividir_var,
            bootstyle="info"
        ).pack(side=RIGHT, padx=5)
    
    def _setup_bindings(self):
        """Configura los eventos y bindings."""
        # Doble click en la tabla para editar
        self.tree.bind("<Double-1>", lambda e: self.editar_concepto_seleccionado())
        
        # Delete key para eliminar conceptos
        self.tree.bind("<Delete>", lambda e: self.eliminar_concepto_seleccionado())
    
    # Métodos de negocio
    
    def cargar_xml(self):
        """Carga archivos XML y rellena los campos."""
        try:
            rutas = filedialog.askopenfilenames(
                title="Selecciona los archivos XML",
                filetypes=[("Archivos XML", "*.xml")]
            )
            
            if not rutas:
                return
            
            self.limpiar_todo()
            self.control.agregar_solicitud(rutas)
            self.actualizar_solicitudes_restantes()
            self.rellenar_campos()
            
            logger.info(f"Cargados {len(rutas)} archivos XML")
            
        except Exception as e:
            logger.error(f"Error al cargar XML: {e}")
            messagebox.showerror("Error", f"Error al cargar XML: {str(e)}")
    
    def rellenar_campos(self):
        """Rellena los campos con datos del XML."""
        try:
            datos = self.control.get_solicitud()
            if not datos:
                return
            
            # Rellenar proveedor
            proveedor_data = {
                "Nombre": getattr(datos, "nombre_emisor", ""),
                "RFC": getattr(datos, "rfc_emisor", ""),
                "Teléfono": "",
                "Correo": "",
                "Contacto": ""
            }
            self.proveedor_frame.set_data(proveedor_data)
            
            # Rellenar solicitud
            fecha_hoy = datetime.date.today().strftime("%d/%m/%Y")
            solicitud_data = {
                "Folio": getattr(datos, "folio", ""),
                "Fecha": fecha_hoy,
                "Clase": "",
                "Tipo": AppConfig.DEFAULT_VALUES["tipo_solicitud"],
                "Depa": AppConfig.DEFAULT_VALUES["departamento"]
            }
            self.solicitud_frame.set_data(solicitud_data)
            
            # Rellenar totales
            self._rellenar_totales(datos)
            
            # Rellenar comentarios
            comentario = f"Factura: {getattr(datos, 'serie', '')} {getattr(datos, 'folio', '')}".strip()
            self.comentarios.delete("1.0", "end")
            self.comentarios.insert("1.0", comentario)
            
            # Rellenar conceptos
            self.rellenar_conceptos(getattr(datos, "conceptos", []))
            
        except Exception as e:
            logger.error(f"Error al rellenar campos: {e}")
            messagebox.showerror("Error", f"Error al rellenar campos: {str(e)}")
    
    def _rellenar_totales(self, datos):
        """Rellena los campos de totales."""
        try:
            self.entries_totales["Subtotal"].delete(0, "end")
            self.entries_totales["Subtotal"].insert(0, getattr(datos, "subtotal", ""))
            
            # Calcular retenciones
            try:
                iva_ret = float(getattr(datos, "iva_ret", 0))
                isr_ret = float(getattr(datos, "isr_ret", 0))
                ret_total = str(iva_ret + isr_ret)
            except (ValueError, TypeError):
                ret_total = ""
            
            self.entries_totales["Ret"].delete(0, "end")
            self.entries_totales["Ret"].insert(0, ret_total)
            
            self.entries_totales["IVA"].delete(0, "end")
            self.entries_totales["IVA"].insert(0, getattr(datos, "iva", ""))
            
            self.entries_totales["TOTAL"].delete(0, "end")
            self.entries_totales["TOTAL"].insert(0, getattr(datos, "total", ""))
            
        except Exception as e:
            logger.error(f"Error al rellenar totales: {e}")
    
    def rellenar_conceptos(self, conceptos):
        """Rellena la tabla de conceptos."""
        try:
            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Insertar conceptos
            for concepto in conceptos:
                self.tree.insert("", "end", values=concepto)
            
            self.comprobar_numero_conceptos()
            
        except Exception as e:
            logger.error(f"Error al rellenar conceptos: {e}")
    
    def agregar_concepto(self):
        """Muestra el popup para agregar un concepto."""
        def insertar_concepto(values):
            try:
                self.tree.insert("", "end", values=values)
                self.comprobar_numero_conceptos()
                logger.info("Concepto agregado correctamente")
            except Exception as e:
                logger.error(f"Error al insertar concepto: {e}")
                messagebox.showerror("Error", f"Error al agregar concepto: {str(e)}")
        
        ConceptoPopup(
            self,
            "Agregar concepto",
            "Agregar",
            insertar_concepto
        )
    
    def editar_concepto_seleccionado(self):
        """Edita el concepto seleccionado."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un concepto para editar.")
            return
        
        item_id = selected[0]
        valores_actuales = self.tree.item(item_id, "values")
        
        def actualizar_concepto(values):
            try:
                self.tree.item(item_id, values=values)
                logger.info("Concepto editado correctamente")
            except Exception as e:
                logger.error(f"Error al actualizar concepto: {e}")
                messagebox.showerror("Error", f"Error al editar concepto: {str(e)}")
        
        ConceptoPopup(
            self,
            "Editar concepto",
            "Guardar",
            actualizar_concepto,
            valores_actuales
        )
    
    def eliminar_concepto_seleccionado(self):
        """Elimina el concepto seleccionado."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un concepto para eliminar.")
            return
        
        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            "¿Está seguro de que desea eliminar el concepto seleccionado?"
        )
        
        if respuesta:
            for item in selected:
                self.tree.delete(item)
            logger.info(f"Eliminados {len(selected)} concepto(s)")
    
    def comprobar_numero_conceptos(self):
        """Comprueba si hay demasiados conceptos."""
        num_conceptos = len(self.tree.get_children())
        if num_conceptos > AppConfig.MAX_CONCEPTOS_RECOMENDADOS:
            respuesta = messagebox.askyesno(
                "Demasiados conceptos",
                AppConfig.ERROR_MESSAGES["demasiados_conceptos"]
            )
            if respuesta:
                self.agregar_concepto_general()
    
    def agregar_concepto_general(self):
        """Agrega un concepto general."""
        try:
            descripcion = simpledialog.askstring(
                "Concepto general",
                "Escriba el concepto general que desea usar:"
            )
            if not descripcion:
                return
            
            datos = self.control.get_solicitud()
            if not datos:
                messagebox.showerror("Error", AppConfig.ERROR_MESSAGES["no_datos"])
                return
            
            valores_iniciales = [
                "1",
                descripcion,
                getattr(datos, "subtotal", ""),
                getattr(datos, "total", "")
            ]
            
            def insertar_concepto(values):
                self.tree.insert("", "end", values=values)
            
            ConceptoPopup(
                self,
                "Agregar concepto general",
                "Agregar",
                insertar_concepto,
                valores_iniciales
            )
            
        except Exception as e:
            logger.error(f"Error al agregar concepto general: {e}")
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def actualizar_solicitudes_restantes(self):
        """Actualiza el contador de solicitudes restantes."""
        try:
            self.solicitudes_restantes = self.control.get_solicitudes_restantes()
            self.lbl_sol_rest.config(
                text=f"Solicitudes restantes: {self.solicitudes_restantes}"
            )
        except Exception as e:
            logger.error(f"Error al actualizar solicitudes restantes: {e}")
    
    def limpiar_todo(self):
        """Limpia todos los campos del formulario."""
        try:
            # Limpiar frames principales
            self.proveedor_frame.clear_entries()
            self.solicitud_frame.clear_entries()
            
            # Restablecer valores por defecto
            self.solicitud_frame.entries["Tipo"].set(AppConfig.DEFAULT_VALUES["tipo_solicitud"])
            self.solicitud_frame.entries["Depa"].set(AppConfig.DEFAULT_VALUES["departamento"])
            
            # Limpiar tabla de conceptos
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Limpiar totales
            for entry in self.entries_totales.values():
                entry.delete(0, "end")
            
            # Limpiar categorías
            self.limpiar_categorias()
            
            # Limpiar comentarios
            self.comentarios.delete("1.0", "end")
            
            logger.info("Formulario limpiado")
            
        except Exception as e:
            logger.error(f"Error al limpiar formulario: {e}")
    
    def limpiar_categorias(self):
        """Limpia las categorías."""
        for entry in self.entries_categorias.values():
            entry.delete(0, "end")
    
    def guardar_categorias(self):
        """Guarda las categorías (placeholder)."""
        # TODO: Implementar guardado de categorías
        messagebox.showinfo("Info", "Función de guardar categorías pendiente de implementar")
    
    def cargar_favorito(self, indice: int):
        """Carga un favorito (placeholder)."""
        # TODO: Implementar carga de favoritos
        messagebox.showinfo("Info", f"Función de cargar favorito {indice + 1} pendiente de implementar")
    
    def generar(self):
        """Genera el documento final."""
        try:
            # Validar datos antes de generar
            es_valido, errores = self.validar_formulario()
            
            if not es_valido:
                mensaje_error = "\\n".join(errores)
                messagebox.showerror("Errores de validación", mensaje_error)
                return
            
            # TODO: Implementar generación de documento
            messagebox.showinfo("Info", "Función de generar documento pendiente de implementar")
            logger.info("Solicitud de generación de documento")
            
        except Exception as e:
            logger.error(f"Error al generar documento: {e}")
            messagebox.showerror("Error", f"Error al generar documento: {str(e)}")
    
    def validar_formulario(self) -> tuple[bool, List[str]]:
        """Valida todo el formulario."""
        errores = []
        
        try:
            # Validar proveedor
            proveedor_valido, errores_proveedor = self.proveedor_frame.validate()
            if not proveedor_valido:
                errores.extend(errores_proveedor)
            
            # Validar que hay conceptos
            if not self.tree.get_children():
                errores.append(AppConfig.ERROR_MESSAGES["sin_conceptos"])
            
            # Validar datos de solicitud
            solicitud_data = self.solicitud_frame.get_data()
            if not solicitud_data.get("Folio", "").strip():
                errores.append("El folio es obligatorio")
            
        except Exception as e:
            logger.error(f"Error en validación: {e}")
            errores.append(f"Error en validación: {str(e)}")
        
        return len(errores) == 0, errores


def main():
    """Función principal para ejecutar la aplicación."""
    try:
        app = tb.Window(themename=AppConfig.THEME)
        app.title("Solicitud de Compra - Versión Profesional")
        app.geometry(AppConfig.WINDOW_SIZE)
        
        frame = SolicitudAppProfessional(app)
        frame.pack(fill="both", expand=True)
        
        logger.info("Aplicación iniciada")
        app.mainloop()
        
    except Exception as e:
        logger.error(f"Error crítico en la aplicación: {e}")
        messagebox.showerror("Error crítico", f"Error al iniciar la aplicación: {str(e)}")


if __name__ == "__main__":
    main()
