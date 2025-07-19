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
 
import sys
import os
# Agregar el directorio src al path para importaciones absolutas
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
else:
    # Cuando se ejecuta desde main.py, usar rutas relativas al src
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from solicitudapp.models.solicitud import Solicitud, Proveedor, Concepto, Totales
from solicitudapp.services.validation import ValidationService
from solicitudapp.config.app_config import AppConfig
from solicitudapp.views.components import ProveedorFrame, SolicitudFrame, ConceptoPopup, BaseFrame
from solicitudapp.logic_solicitud import SolicitudLogica
from solicitudapp.form_control import FormPDF
from bd.models import Factura, Proveedor, Reparto
from bd.bd_control import DBManager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SolicitudApp(tb.Frame):
    """
    Aplicación principal para gestión de solicitudes de compra.
    Versión profesional con arquitectura limpia y separación de responsabilidades.
    """
    
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        
        # Inicializar base de datos
        self.db_manager = DBManager()
        
        # Servicios
        self.validation_service = ValidationService()
        self.control = SolicitudLogica()
        
        # Estado de la aplicación
        self.solicitudes_restantes = 0
        self.solicitud_actual: Optional[Solicitud] = None
        self.factura_duplicada = False  # Flag para indicar si la factura está duplicada
        self.folio_interno_manual = None  # Almacenar folio interno ingresado manualmente
        
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

        # Botón calcular
        tb.Button(
            frame_btn_tabla,
            text="🧮",
            width=btn_width,
            command=self.calcular_totales,
            bootstyle="primary"
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
        width_btn = 10
        tb.Button(
            frame_barra,
            text="Generar",
            bootstyle="success",
            command=self.generar,
            width=width_btn
        ).pack(side=RIGHT, padx=5)
        
        tb.Button(
            frame_barra,
            text="Cargar XML",
            bootstyle="primary",
            command=self.cargar_xml,
            width=width_btn
        ).pack(side=RIGHT, padx=5)
        
        # Checkbox dividir
        self.dividir_var = tb.BooleanVar()
        self.chb_dividir = tb.Checkbutton(
            frame_barra,
            text="Dividir",
            variable=self.dividir_var,
            bootstyle="info"
        )
        self.chb_dividir.pack(side=RIGHT, padx=5)
    
    def _setup_bindings(self):
        """Configura los eventos y bindings."""
        # Doble click en la tabla para editar
        self.tree.bind("<Double-1>", lambda e: self.editar_concepto_seleccionado())
        
        # Delete key para eliminar conceptos
        self.tree.bind("<Delete>", lambda e: self.eliminar_concepto_seleccionado())
    
    def _extraer_clave_tipo(self, tipo_completo: str) -> str:
        """
        Extrae la clave del tipo de vale del formato 'CLAVE - DESCRIPCION'.
        Si no está en ese formato, devuelve el valor tal como está.
        """
        if not tipo_completo:
            return "VC"  # Valor por defecto
        
        # Si está en formato "CLAVE - DESCRIPCION", extraer solo la clave
        if " - " in tipo_completo:
            return tipo_completo.split(" - ")[0].strip()
        
        # Si no está en ese formato, asumir que ya es la clave
        return tipo_completo.strip()

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
            
            # Obtén los datos del primer XML
            datos = self.control.get_solicitud()
            if not datos:
                return

            # Comprobación en la base de datos
            proveedor_rfc = getattr(datos, "rfc_emisor", "")
            serie = getattr(datos, "serie", "")
            folio = getattr(datos, "folio", "")

            self.factura_duplicada = False  # Resetear flag
            self.folio_interno_manual = None  # Resetear folio manual

            proveedor = Proveedor.get_or_none(Proveedor.rfc == proveedor_rfc)
            if proveedor:
                factura_existente = Factura.get_or_none(
                    (Factura.proveedor == proveedor) &
                    (Factura.serie == serie) &
                    (Factura.folio == folio)
                )
                if factura_existente:
                    # Marcar como duplicada pero continuar con el proceso
                    self.factura_duplicada = True
                    
                    # Mostrar mensaje informativo
                    messagebox.showwarning(
                        "Factura duplicada",
                        f"La factura con serie {serie} y folio {folio} del proveedor {proveedor.nombre} "
                        f"ya se encuentra en la base de datos.\n\n"
                        f"Se rellenará el formulario pero no se guardará en la base de datos."
                    )
                    
                    # Usar el folio interno de la factura existente como valor inicial
                    folio_inicial = str(factura_existente.folio_interno)
                    
                    # Solicitar folio interno manual
                    folio_manual = simpledialog.askstring(
                        "Folio interno manual",
                        f"La factura ya existe con folio interno: {folio_inicial}\n\n"
                        f"Ingrese el número de folio interno para el documento:",
                        initialvalue=folio_inicial
                    )
                    
                    if folio_manual:
                        self.folio_interno_manual = folio_manual
                    else:
                        self.folio_interno_manual = folio_inicial

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

            # Rellenar categorías y tipo desde la última factura del proveedor
            self.rellenar_datos_proveedor_anterior(getattr(datos, "rfc_emisor", ""))
            
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
            self.borrar_conceptos()
            
            # Insertar conceptos
            for concepto in conceptos:
                self.tree.insert("", "end", values=concepto)

            self.comprobar_numero_conceptos()
            
        except Exception as e:
            logger.error(f"Error al rellenar conceptos: {e}")

    def borrar_conceptos(self):
        # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)
    
    def rellenar_datos_proveedor_anterior(self, rfc_emisor: str):
        """
        Rellena los campos de categorías y tipo con los datos de la última factura
        del proveedor si existe en la base de datos.
        """
        print(f"🔍 DEBUG: rellenar_datos_proveedor_anterior llamado con RFC: {rfc_emisor}")
        try:
            if not rfc_emisor:
                print("🔍 DEBUG: RFC emisor vacío, retornando")
                return
            
            print(f"🔍 DEBUG: Buscando proveedor con RFC: {rfc_emisor}")
            # Buscar el proveedor en la base de datos
            proveedor_bd = Proveedor.get_or_none(Proveedor.rfc == rfc_emisor)
            if not proveedor_bd:
                print(f"🔍 DEBUG: Proveedor con RFC {rfc_emisor} no encontrado en BD")
                logger.info(f"Proveedor con RFC {rfc_emisor} no encontrado en BD")
                return
            print(f"🔍 DEBUG: Proveedor encontrado: {proveedor_bd.nombre}")
            
            # Buscar la última factura del proveedor
            ultima_factura = (Factura
                            .select()
                            .where(Factura.proveedor == proveedor_bd)
                            .order_by(Factura.folio_interno.desc())
                            .first())
            
            if not ultima_factura:
                print(f"🔍 DEBUG: No se encontraron facturas anteriores para {proveedor_bd.nombre}")
                logger.info(f"No se encontraron facturas anteriores para el proveedor {proveedor_bd.nombre}")
                return
            print(f"🔍 DEBUG: Factura encontrada: {ultima_factura.serie}-{ultima_factura.folio}, Tipo: {ultima_factura.tipo}")
            logger.info(f"Encontrada factura anterior para {proveedor_bd.nombre}: {ultima_factura.serie}-{ultima_factura.folio}")
            
            # Buscar el reparto de la última factura
            ultimo_reparto = Reparto.get_or_none(Reparto.factura == ultima_factura)
            
            if ultimo_reparto:
                print(f"🔍 DEBUG: Reparto encontrado, rellenando categorías...")
                # Rellenar categorías con los datos del último reparto
                categorias_data = {
                    "Comer": ultimo_reparto.comercial or 0,
                    "Fleet": ultimo_reparto.fleet or 0,
                    "Semis": ultimo_reparto.seminuevos or 0,
                    "Refa": ultimo_reparto.refacciones or 0,
                    "Serv": ultimo_reparto.servicio or 0,
                    "HyP": ultimo_reparto.hyp or 0,
                    "Admin": ultimo_reparto.administracion or 0
                }
                
                # Llenar los campos de categorías
                for categoria, valor in categorias_data.items():
                    if categoria in self.entries_categorias:
                        self.entries_categorias[categoria].delete(0, "end")
                        if valor and valor != 0:
                            self.entries_categorias[categoria].insert(0, str(valor))
                
                logger.info("Categorías rellenadas desde la última factura")
            
            # Usar el tipo directamente del modelo Factura
            if ultima_factura.tipo:
                # Buscar el tipo en el diccionario TIPO_VALE
                tipo_factura = ultima_factura.tipo.strip()
                
                # Si el tipo está en formato "KEY - VALUE", extraer solo la clave
                if " - " in tipo_factura:
                    clave_tipo = tipo_factura.split(" - ")[0]
                else:
                    clave_tipo = tipo_factura
                
                # Verificar si la clave existe en TIPO_VALE
                if clave_tipo in AppConfig.TIPO_VALE:
                    tipo_sugerido = f"{clave_tipo} - {AppConfig.TIPO_VALE[clave_tipo]}"
                    logger.info(f"Tipo encontrado en Factura: {tipo_sugerido}")
                else:
                    # Si no está en el diccionario, usar valor por defecto
                    tipo_sugerido = AppConfig.DEFAULT_VALUES["tipo_solicitud"]
                    logger.info(f"Tipo de factura no encontrado en diccionario, usando por defecto: {tipo_sugerido}")
            else:
                # Fallback: usar valor por defecto
                tipo_sugerido = AppConfig.DEFAULT_VALUES["tipo_solicitud"]
                logger.info(f"Sin tipo en factura, usando por defecto: {tipo_sugerido}")
            
            # Actualizar el tipo en la interfaz
            solicitud_data = self.solicitud_frame.get_data()
            solicitud_data["Tipo"] = tipo_sugerido
            self.solicitud_frame.set_data(solicitud_data)
            logger.info(f"Tipo de solicitud establecido como: {tipo_sugerido}")
            
        except Exception as e:
            logger.error(f"Error al cargar datos del proveedor anterior: {e}")
            # No mostramos error al usuario ya que es una funcionalidad adicional
    
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

    def calcular_totales(self):
        """Calcula Subtotal, IVA (16%) y Total en los campos correspondientes."""
        try:
            # Sumar columna 'Total' para obtener el Subtotal
            subtotal = 0.0
            for item in self.tree.get_children():
                valores = self.tree.item(item, "values")
                if len(valores) >= 4:
                    try:
                        subtotal += float(valores[3])
                    except (ValueError, TypeError):
                        continue  # Ignora valores no numéricos

            # Calcular IVA (16% del subtotal)
            iva = subtotal * 0.16
            # Calcular Total (subtotal + iva)
            total = subtotal + iva

            # Actualizar los campos
            self.entries_totales["Subtotal"].delete(0, "end")
            self.entries_totales["Subtotal"].insert(0, f"{subtotal:.2f}")

            self.entries_totales["IVA"].delete(0, "end")
            self.entries_totales["IVA"].insert(0, f"{iva:.2f}")

            self.entries_totales["TOTAL"].delete(0, "end")
            self.entries_totales["TOTAL"].insert(0, f"{total:.2f}")

            logger.info(f"Totales calculados: Subtotal={subtotal:.2f}, IVA={iva:.2f}, Total={total:.2f}")
        except Exception as e:
            logger.error(f"Error al calcular totales: {e}")
            messagebox.showerror("Error", f"Error al calcular totales: {str(e)}")
    
    def comprobar_numero_conceptos(self):
        """Comprueba si hay demasiados conceptos."""
        num_conceptos = len(self.tree.get_children())
        if num_conceptos > AppConfig.MAX_CONCEPTOS_RECOMENDADOS:
            respuesta = messagebox.askyesno(
                "Demasiados conceptos",
                AppConfig.ERROR_MESSAGES["demasiados_conceptos"]
            )
            if respuesta:
                self.borrar_conceptos()
                self.agregar_concepto_general()
    
    def agregar_concepto_general(self):
        """Agrega un concepto general."""
        try:
            """""
            descripcion = simpledialog.askstring(
                "Concepto general",
                "Escriba el concepto general que desea usar:"
            )
            if not descripcion:
                return
            """
            
            datos = self.control.get_solicitud()
            if not datos:
                messagebox.showerror("Error", AppConfig.ERROR_MESSAGES["no_datos"])
                return
            
            valores_iniciales = [
                "1",
                "",
                getattr(datos, "total", ""),
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

            logger.info("Concepto general agregado correctamente")
            
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
            # Resetear flags de factura duplicada
            self.factura_duplicada = False
            self.folio_interno_manual = None
            
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
            logger.info("Inicio de generación de documento")
            # Validar datos antes de generar
            es_valido, errores = self.validar_formulario()
            if not es_valido:
                mensaje_error = "\n".join(errores)
                logger.error(f"Errores de validación: {mensaje_error}")
                messagebox.showerror("Errores de validación", mensaje_error)
                return
            
            # Recopilar datos del formulario
            proveedor_data = self.proveedor_frame.get_data()
            solicitud_data = self.solicitud_frame.get_data()
            conceptos = [self.tree.item(item, "values") for item in self.tree.get_children()]
            totales = {k: v.get() for k, v in self.entries_totales.items()}
            categorias = {k: v.get() for k, v in self.entries_categorias.items()}
            comentarios = self.comentarios.get("1.0", "end").strip()
            logger.info("Datos del formulario recopilados correctamente")

            # Seleccionar ruta de guardado
            ruta = filedialog.asksaveasfilename(
                title="Guardar solicitud",
                filetypes=[("PDF", "*.pdf")],
                initialfile=f"{solicitud_data.get('Folio', '')} {proveedor_data.get('Nombre', '')}".strip()
            )
            if not ruta:
                logger.info("Exportación cancelada por el usuario")
                return
            if not ruta.lower().endswith(".pdf"):
                ruta += ".pdf"
            logger.info(f"Ruta de guardado seleccionada: {ruta}")

            # Dividir totales si el checkbox está marcado y habilitado
            dividir_marcado = self.dividir_var.get()
            dividir_habilitado = str(self.chb_dividir.cget('state')) == "normal"
            if dividir_marcado and dividir_habilitado:
                logger.info("Casilla dividir activa, dividiendo totales")
                for k in ["Subtotal", "Ret", "IVA", "TOTAL"]:
                    try:
                        valor = float(totales.get(k, "0"))
                        totales[k] = f"{valor / 2:.2f}"
                        self.entries_totales[k].delete(0, "end")
                        self.entries_totales[k].insert(0, totales[k])
                    except (ValueError, TypeError):
                        logger.error(f"Error al dividir el total para {k}")
                        pass

            data = {
                "TIPO DE VALE": solicitud_data.get("Tipo", ""),
                "C A N T I D A D": "\n".join([c[0] for c in conceptos]),
                "C O M E N T A R I O S": comentarios,
                "Nombre de Empresa": proveedor_data.get("Nombre", ""), 
                "RFC": proveedor_data.get("RFC", ""), 
                "Teléfono": proveedor_data.get("Teléfono", ""), 
                "Correo": proveedor_data.get("Correo", ""), 
                "Nombre Contacto": proveedor_data.get("Contacto", ""),
                "Menudeo": categorias.get("Comer", ""), 
                "Seminuevos": categorias.get("Semis", ""), 
                "Flotas": categorias.get("Fleet", ""),
                "Administración": categorias.get("Admin", ""),
                "Refacciones": categorias.get("Refa", ""),
                "Servicio": categorias.get("Serv", ""),
                "HYP": categorias.get("HyP", ""),
                "DESCRIPCIÓN": "\n".join([c[1] for c in conceptos]),
                "PRECIO UNITARIO": "\n".join([c[2] for c in conceptos]),
                "TOTAL": "\n".join([c[3] for c in conceptos]),
                "FECHA GERENTE DE ÁREA": "", 
                "FECHA GERENTE ADMINISTRATIVO": "", 
                "FECHA DE AUTORIZACIÓN GG O DIRECTOR DE MARCA": "", 
                "SUBTOTAL": totales.get("Subtotal", ""), 
                "IVA": totales.get("IVA", ""), 
                "TOTAL, SUMATORIA": totales.get("TOTAL", ""), 
                "FECHA CREACIÓN SOLICITUD": solicitud_data.get("Fecha", ""), 
                "FOLIO": "",
                "RETENCIÓN": totales.get("Ret", ""), 
                "Departamento": solicitud_data.get("Depa", "")
            }
            logger.info("Datos preparados para generación de documento")

            # TODO: Aquí deberías llamar a tu servicio de generación de PDF/documento
            try:
                # Verificar si la factura está duplicada
                if self.factura_duplicada:
                    logger.info("Factura duplicada detectada, omitiendo guardado en base de datos")
                    # Usar el folio interno manual proporcionado por el usuario
                    data["FOLIO"] = self.folio_interno_manual or "DUPLICADO"
                else:
                    # Proceder con el guardado normal en la base de datos
                    # Mapear los datos correctamente para guardar_solicitud
                    proveedor_mapped = {
                        "nombre": proveedor_data.get("Nombre", ""),
                        "rfc": proveedor_data.get("RFC", ""),
                        "telefono": proveedor_data.get("Teléfono", ""),
                        "email": proveedor_data.get("Correo", ""),
                        "nombre_contacto": proveedor_data.get("Contacto", "")
                    }
                    
                    solicitud_mapped = {
                        "serie": getattr(self.control.get_solicitud(), "serie", "A") if self.control.get_solicitud() else "A",
                        "folio": solicitud_data.get("Folio", "001"),
                        "fecha": solicitud_data.get("Fecha", ""),
                        "tipo": self._extraer_clave_tipo(solicitud_data.get("Tipo", "")),  # Extraer solo la clave
                        "nombre_receptor": "TCM MATEHUALA",  # Valor por defecto
                        "rfc_receptor": "TMM860630PH1"  # Valor por defecto
                    }
                    
                    totales_mapped = {
                        "subtotal": totales.get("Subtotal", ""),
                        "iva_trasladado": totales.get("IVA", ""),
                        "ret_iva": totales.get("Ret", ""),
                        "ret_isr": "0",  # Por defecto
                        "total": totales.get("TOTAL", "")
                    }
                    
                    comentarios_mapped = {
                        "comentario": comentarios
                    }
                    
                    # Mapear conceptos
                    conceptos_mapped = []
                    for concepto in conceptos:
                        if len(concepto) >= 4:
                            conceptos_mapped.append({
                                "descripcion": concepto[1],
                                "cantidad": concepto[0],
                                "unidad": "PZ",  # Por defecto
                                "precio_unitario": concepto[2],
                                "importe": concepto[3]
                            })
                    
                    categorias_mapped = {
                        "comercial": categorias.get("Comer", ""),
                        "fleet": categorias.get("Fleet", ""),
                        "seminuevos": categorias.get("Semis", ""),
                        "refacciones": categorias.get("Refa", ""),
                        "servicio": categorias.get("Serv", ""),
                        "hyp": categorias.get("HyP", ""),
                        "administracion": categorias.get("Admin", "")
                    }
                    
                    factura = self.control.guardar_solicitud(
                        proveedor_mapped, solicitud_mapped, conceptos_mapped, 
                        totales_mapped, categorias_mapped, comentarios_mapped
                    )
                    logger.info(f"Factura guardada en la base de datos con folio_interno: {factura.folio_interno}")
                    data["FOLIO"] = str(factura.folio_interno)
                
            except Exception as db_error:
                logger.warning(f"Error al guardar en base de datos: {db_error}")
                # Continúa sin guardar en BD pero genera el PDF
                data["FOLIO"] = self.folio_interno_manual or "ERROR"
                
            self.control.rellenar_formulario(data, ruta)
            logger.info("Formulario rellenado con datos de la factura")

            # Mensaje de éxito personalizado según si se guardó en BD o no
            if self.factura_duplicada:
                mensaje_exito = (
                    f"Solicitud generada correctamente en:\n{ruta}\n\n"
                    f"NOTA: La factura ya existía en la base de datos, "
                    f"por lo que no se guardó nuevamente.\n"
                    f"Folio interno asignado: {self.folio_interno_manual}"
                )
            else:
                mensaje_exito = f"Solicitud generada y guardada correctamente en:\n{ruta}"
            
            messagebox.showinfo("Éxito", mensaje_exito)
            logger.info(f"Solicitud generada y guardada en: {ruta}")

            # Alternar estado del checkbox dividir
            if dividir_habilitado and dividir_marcado:
                self.chb_dividir.config(state="disabled")
                self.solicitud_frame.entries["Tipo"].set("VC - VALE DE CONTROL")
                logger.info("Checkbox dividir deshabilitado y tipo de vale cambiado")
                return
            else:
                self.chb_dividir.config(state="normal")
                logger.info("Checkbox dividir habilitado")

            # Limpiar formulario y actualizar solicitudes restantes
            self.control.delete_solicitud()
            self.limpiar_todo()
            self.rellenar_campos()
            self.actualizar_solicitudes_restantes()

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
            if not solicitud_data.get("Tipo", "").strip():
                errores.append("El tipo de vale es obligatorio")

            # Validar suma de categorías
            valores = [entry.get() for entry in self.entries_categorias.values()]
            es_valido, mensaje = self.validation_service.validar_suma_categorias(valores)
            if not es_valido:
                errores.append(mensaje)

        except Exception as e:
            logger.error(f"Error en validación: {e}")
            errores.append(f"Error en validación: {str(e)}")
        
        return len(errores) == 0, errores

    def validar_suma_categorias(self) -> bool:
        """
        Valida que la suma de los valores numéricos de las categorías sea exactamente 100.
        Muestra un mensaje de error si no se cumple la condición.
        """
        valores = [entry.get() for entry in self.entries_categorias.values()]
        es_valido, mensaje = self.validation_service.validar_suma_categorias(valores)
        if not es_valido:
            messagebox.showerror("Error de validación", mensaje)
        return es_valido


def main():
    """Función principal para ejecutar la aplicación."""
    try:
        app = tb.Window(themename=AppConfig.THEME)
        app.title("Solicitud de Compra - Versión Profesional")
        app.geometry(AppConfig.WINDOW_SIZE)
        
        frame = SolicitudApp(app)
        frame.pack(fill="both", expand=True)
        
        logger.info("Aplicación iniciada")
        app.mainloop()
        
    except Exception as e:
        logger.error(f"Error crítico en la aplicación: {e}")
        messagebox.showerror("Error crítico", f"Error al iniciar la aplicación: {str(e)}")


if __name__ == "__main__":
    main()
