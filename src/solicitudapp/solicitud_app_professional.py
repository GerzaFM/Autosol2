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

# Agregar el directorio raíz para acceder a las utilidades
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# from solicitudapp.models.solicitud import Solicitud, Proveedor, Concepto, Totales  # ELIMINADO: No se usa
from solicitudapp.services.validation import ValidationService
from solicitudapp.config.app_config import AppConfig
from solicitudapp.views.components import ProveedorFrame, SolicitudFrame, ConceptoPopup, BaseFrame
from solicitudapp.logic_solicitud import SolicitudLogica
from solicitudapp.form_control import FormPDF
from bd.models import Factura, Proveedor, Reparto
from bd.bd_control import DBManager

# Importar utilidades seguras si están disponibles
try:
    from app.utils.ui_helpers import safe_set_geometry, get_safe_window_size, center_window_on_parent
    from config.settings import WINDOW_SIZES
    UI_HELPERS_AVAILABLE = True
except ImportError:
    UI_HELPERS_AVAILABLE = False
    logging.warning("Utilidades de UI no disponibles, usando métodos básicos")

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
        self.solicitud_actual = None  # Eliminado type hint Optional[Solicitud]
        self.factura_duplicada = False  # Flag para indicar si la factura está duplicada
        self.folio_interno_manual = None  # Almacenar folio interno ingresado manualmente
        self.folio_segunda_factura = None  # Almacenar folio para la segunda factura en división
        self.valores_ya_divididos = False  # Flag para indicar si los valores ya fueron divididos
        self.division_con_duplicado = False  # Flag para indicar división con factura duplicada
        
        # Valores originales para calcular complementos
        self.valores_originales_totales = {}  # Almacenar totales originales del XML
        self.valores_originales_conceptos = []  # Almacenar conceptos originales del XML
        self.valores_antes_dividir_totales = {}  # Almacenar totales antes de dividir para calcular complementos
        self.valores_antes_dividir_conceptos = []  # Almacenar conceptos antes de dividir para calcular complementos
        
        # Componentes UI
        self.proveedor_frame: Optional[ProveedorFrame] = None
        self.solicitud_frame: Optional[SolicitudFrame] = None
        self.tree: Optional[tb.Treeview] = None
        self.entries_totales = {}
        self.entries_categorias = {}
        self.comentarios: Optional[tb.Text] = None
        
        # Inicializar la interfaz de usuario
        self.setup_ui()
        
        # Sincronizar secuencia de folio al inicializar
        self.sincronizar_secuencia_folio()
        
    def obtener_proximo_folio_interno(self):
        """Obtiene el próximo folio interno que sería asignado en la base de datos."""
        try:
            # Obtener el máximo folio_interno actual
            ultima_factura = Factura.select().order_by(Factura.folio_interno.desc()).first()
            if ultima_factura:
                return ultima_factura.folio_interno + 1
            else:
                return 1  # Primera factura
        except Exception as e:
            logger.warning(f"Error al obtener próximo folio interno: {e}")
            return "001"  # Fallback
    
    def sincronizar_secuencia_folio(self):
        """Sincroniza la secuencia PostgreSQL con el máximo folio_interno actual."""
        try:
            from src.bd.database import db
            
            # Obtener el máximo folio_interno actual
            ultima_factura = Factura.select().order_by(Factura.folio_interno.desc()).first()
            if ultima_factura:
                max_folio = ultima_factura.folio_interno
                
                # Ajustar la secuencia al valor máximo actual
                db.execute_sql(f"SELECT setval('facturas_folio_interno_seq', {max_folio}, true);")
                logger.info(f"Secuencia PostgreSQL sincronizada al folio_interno máximo: {max_folio}")
                
                # Verificar que la sincronización funcionó
                cursor = db.execute_sql('SELECT last_value FROM facturas_folio_interno_seq;')
                nuevo_valor = cursor.fetchone()[0]
                logger.info(f"Secuencia ahora está en: {nuevo_valor} (próximo será: {nuevo_valor + 1})")
            else:
                logger.warning("No hay facturas en la base de datos para sincronizar la secuencia")
        except Exception as e:
            logger.error(f"Error al sincronizar la secuencia: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        self.lbl_sol_rest: Optional[tb.Label] = None
        self.dividir_var: Optional[tb.BooleanVar] = None
        
        # ID del usuario actual (Usuario migrado de SQLite)
        self.usuario_actual_id = 294379  # Usuario Gerzahin Flores Martinez
        
        # Lista para guardar referencias a los botones de favoritos
        self.botones_favoritos = []
        
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
        
        # Frame de proveedor (ahora con db_manager)
        self.proveedor_frame = ProveedorFrame(frame_sup, db_manager=self.db_manager)
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

        # Botón dividir
        tb.Button(
            frame_btn_tabla,
            text="1/2",
            width=btn_width,
            command=self.dividir_totales_conceptos,
            bootstyle="info"
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
        
        self.botones_favoritos = []
        for i in range(5):
            btn = tb.Button(
                frame_fav,
                text=f"Favorito {i + 1}",
                bootstyle="info",
                width=12,
                command=lambda idx=i: self.cargar_favorito(idx)
            )
            btn.grid(row=0, column=i, padx=4, pady=6, sticky="s")
            self.botones_favoritos.append(btn)
        
        # Cargar nombres de favoritos al inicializar
        self.actualizar_nombres_favoritos()
        
        parent.grid_rowconfigure(3, weight=1)
    
    def actualizar_nombres_favoritos(self):
        """Actualiza los nombres de los botones de favoritos desde la base de datos."""
        try:
            favoritos = self.db_manager.obtener_favoritos_usuario(self.usuario_actual_id)
            
            # Resetear todos los botones a nombres por defecto
            for i, btn in enumerate(self.botones_favoritos):
                btn.config(text=f"Favorito {i + 1}")
            
            # Actualizar botones con nombres personalizados
            for favorito in favoritos:
                if 0 <= favorito.posicion < len(self.botones_favoritos):
                    self.botones_favoritos[favorito.posicion].config(
                        text=favorito.nombre_personalizado
                    )
        except Exception as e:
            logger.error(f"Error al actualizar nombres de favoritos: {e}")

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
    
    def _get_tipo_value_from_solicitud_frame(self) -> str:
        """Obtiene el valor del tipo de vale desde el frame de solicitud."""
        try:
            if hasattr(self.solicitud_frame, 'tipo_search') and self.solicitud_frame.tipo_search:
                # Si usa SearchEntry
                selected_item = self.solicitud_frame.tipo_search.get_selected_item()
                if selected_item:
                    return selected_item.get('clave', 'VC')
            else:
                # Si usa Combobox tradicional
                solicitud_data = self.solicitud_frame.get_data()
                tipo_completo = solicitud_data.get("Tipo", "")
                return self._extraer_clave_tipo(tipo_completo)
        except:
            pass
        return "VC"  # Valor por defecto

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
            self.folio_segunda_factura = None  # Resetear folio segunda factura
            self.valores_ya_divididos = False  # Resetear flag de división
            self.division_con_duplicado = False  # Resetear flag de división con duplicado

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
                    
                    # Si dividir está activado, marcar contexto de división con duplicado
                    if hasattr(self, 'dividir_var') and self.dividir_var and self.dividir_var.get():
                        self.division_con_duplicado = True
                        logger.info("División con factura duplicada detectada - ambas facturas requerirán folio manual")
                    
                    # Mostrar mensaje informativo
                    messagebox.showwarning(
                        "Factura duplicada",
                        f"La factura con serie {serie} y folio {folio} del proveedor {proveedor.nombre} "
                        f"ya se encuentra en la base de datos.\n\n"
                        f"Se rellenará el formulario pero no se guardará en la base de datos."
                    )
                    
                    # Usar el folio interno de la factura existente como valor inicial
                    folio_inicial = str(factura_existente.folio_interno)
                    
                    # Si es división con duplicado, solicitar ambos folios al inicio
                    if self.division_con_duplicado:
                        # Solicitar folio para la primera factura (SC)
                        folio_manual_sc = simpledialog.askstring(
                            "Folio para Primera Factura (SC)",
                            f"La factura ya existe con folio interno: {folio_inicial}\n\n"
                            f"Ingrese el folio interno para la PRIMERA factura (SC):",
                            initialvalue=folio_inicial
                        )
                        
                        if folio_manual_sc:
                            self.folio_interno_manual = folio_manual_sc
                        else:
                            self.folio_interno_manual = folio_inicial
                        
                        # Solicitar folio para la segunda factura (VC)
                        try:
                            folio_siguiente = str(int(self.folio_interno_manual) + 1)
                        except ValueError:
                            folio_siguiente = f"{self.folio_interno_manual}_VC"
                        
                        folio_manual_vc = simpledialog.askstring(
                            "Folio para Segunda Factura (VC)",
                            f"Ingrese el folio interno para la SEGUNDA factura (VC):",
                            initialvalue=folio_siguiente
                        )
                        
                        if folio_manual_vc:
                            # Guardar el folio de la segunda factura para uso posterior
                            self.folio_segunda_factura = folio_manual_vc
                            logger.info(f"Folios configurados - SC: {self.folio_interno_manual}, VC: {self.folio_segunda_factura}")
                        else:
                            logger.warning("Usuario canceló la entrada de folio para segunda factura")
                            messagebox.showwarning("Advertencia", "Debe ingresar ambos folios para usar la división")
                            return
                    else:
                        # Caso normal: solo una factura
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
            # Guardar valores originales para cálculos de complemento (SOLO del XML, sin modificaciones)
            self.valores_originales_totales = {
                "Subtotal": str(getattr(datos, "subtotal", "")),
                "IVA": str(getattr(datos, "iva", "")),
                "TOTAL": str(getattr(datos, "total", ""))
            }
            
            # Calcular retenciones originales
            try:
                iva_ret = float(getattr(datos, "iva_ret", 0))
                isr_ret = float(getattr(datos, "isr_ret", 0))
                ret_total = str(iva_ret + isr_ret) if (iva_ret + isr_ret) > 0 else ""
                self.valores_originales_totales["Ret"] = ret_total
            except (ValueError, TypeError):
                ret_total = ""
                self.valores_originales_totales["Ret"] = ret_total
            
            logger.info(f"Valores originales del XML guardados para complementarios: {self.valores_originales_totales}")
            
            # Rellenar campos en la interfaz
            self.entries_totales["Subtotal"].delete(0, "end")
            self.entries_totales["Subtotal"].insert(0, getattr(datos, "subtotal", ""))
            
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
            # Guardar conceptos originales para cálculos de complemento (SOLO del XML, sin modificaciones)
            self.valores_originales_conceptos = []
            for concepto in conceptos:
                if len(concepto) >= 4:  # [cantidad, descripcion, precio_unitario, total]
                    self.valores_originales_conceptos.append({
                        "cantidad": concepto[0],
                        "descripcion": concepto[1], 
                        "precio_unitario": float(concepto[2]) if concepto[2] else 0.0,
                        "total": float(concepto[3]) if concepto[3] else 0.0
                    })
            
            logger.info(f"Conceptos originales del XML guardados para complementarios: {len(self.valores_originales_conceptos)} conceptos")
            
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
            if hasattr(self.solicitud_frame, 'tipo_search') and self.solicitud_frame.tipo_search:
                # Si usa SearchEntry, buscar el item correspondiente
                for item in self.solicitud_frame.tipo_search.items:
                    if item.get('clave') == clave_tipo:
                        self.solicitud_frame.tipo_search.set_selection(item)
                        break
            else:
                # Si usa Combobox tradicional
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
            logger.info("Iniciando cálculo de totales...")
            
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

            logger.info(f"Valores calculados antes de actualizar campos: Subtotal={subtotal:.2f}, IVA={iva:.2f}, Total={total:.2f}")

            # Actualizar los campos
            self.entries_totales["Subtotal"].delete(0, "end")
            self.entries_totales["Subtotal"].insert(0, f"{subtotal:.2f}")
            logger.info(f"Campo Subtotal actualizado: {self.entries_totales['Subtotal'].get()}")

            self.entries_totales["IVA"].delete(0, "end")
            self.entries_totales["IVA"].insert(0, f"{iva:.2f}")
            logger.info(f"Campo IVA actualizado: {self.entries_totales['IVA'].get()}")

            self.entries_totales["TOTAL"].delete(0, "end")
            self.entries_totales["TOTAL"].insert(0, f"{total:.2f}")
            logger.info(f"Campo TOTAL actualizado: {self.entries_totales['TOTAL'].get()}")

            # Forzar actualización de la interfaz
            self.update()

            # Resetear el flag de división al recalcular
            if hasattr(self, 'valores_ya_divididos'):
                self.valores_ya_divididos = False
                logger.info("Flag valores_ya_divididos reseteado a False")

            logger.info(f"Totales calculados: Subtotal={subtotal:.2f}, IVA={iva:.2f}, Total={total:.2f}")
        except Exception as e:
            logger.error(f"Error al calcular totales: {e}")
            messagebox.showerror("Error", f"Error al calcular totales: {str(e)}")
    
    def dividir_totales_conceptos(self):
        """Divide totales y conceptos a la mitad."""
        try:
            logger.info("Iniciando división manual de totales y conceptos")
            
            # Verificar si ya se dividieron los valores
            if hasattr(self, 'valores_ya_divididos') and self.valores_ya_divididos:
                messagebox.showwarning("Advertencia", "Los valores ya han sido divididos. Use 'Calcular' para restaurar los valores originales antes de dividir nuevamente.")
                return
            
            # GUARDAR VALORES ANTES DE DIVIDIR para poder calcular complementos correctamente
            # Obtener totales actuales ANTES de dividir con manejo de valores vacíos
            totales_antes_dividir = {}
            for k, v in self.entries_totales.items():
                valor = v.get().strip()
                totales_antes_dividir[k] = valor if valor else "0"
            
            self.valores_antes_dividir_totales = totales_antes_dividir.copy()
            logger.info(f"Valores totales guardados antes de dividir: {self.valores_antes_dividir_totales}")
            
            # Guardar conceptos ANTES de dividir
            self.valores_antes_dividir_conceptos = []
            for item_id in self.tree.get_children():
                try:
                    valores = list(self.tree.item(item_id, "values"))
                    if len(valores) >= 4:
                        self.valores_antes_dividir_conceptos.append({
                            "cantidad": valores[0],
                            "descripcion": valores[1],
                            "precio_unitario": float(valores[2]),
                            "total": float(valores[3])
                        })
                except (ValueError, TypeError, IndexError) as e:
                    logger.error(f"Error al guardar concepto antes de dividir: {e}")
                    continue
            logger.info(f"Conceptos guardados antes de dividir: {len(self.valores_antes_dividir_conceptos)} conceptos")
            
            # Obtener totales actuales para dividir
            totales = {k: v.get() for k, v in self.entries_totales.items()}
            
            # Dividir totales
            for k in ["Subtotal", "Ret", "IVA", "TOTAL"]:
                try:
                    valor_str = totales.get(k, "0").strip()
                    # Manejar valores vacíos
                    if not valor_str:
                        valor_str = "0"
                    
                    valor = float(valor_str)
                    nuevo_valor = valor / 2
                    totales[k] = f"{nuevo_valor:.2f}"
                    self.entries_totales[k].delete(0, "end")
                    self.entries_totales[k].insert(0, totales[k])
                except (ValueError, TypeError) as e:
                    logger.error(f"Error al dividir el total para {k}: {e}")
                    # En caso de error, poner 0
                    self.entries_totales[k].delete(0, "end")
                    self.entries_totales[k].insert(0, "0.00")
                    pass
            logger.info(f"Totales divididos: {totales}")
            
            # Dividir conceptos en la tabla (precio unitario y total, cantidad permanece igual)
            logger.info("Dividiendo conceptos en la tabla")
            for item_id in self.tree.get_children():
                try:
                    valores_actuales = list(self.tree.item(item_id, "values"))
                    if len(valores_actuales) >= 4:  # [cantidad, descripcion, precio_unitario, total]
                        cantidad = valores_actuales[0]  # Cantidad permanece igual
                        descripcion = valores_actuales[1]  # Descripción permanece igual
                        precio_unitario = float(valores_actuales[2])
                        total_actual = float(valores_actuales[3])
                        
                        # Dividir precio unitario y total por 2
                        nuevo_precio = precio_unitario / 2
                        nuevo_total = total_actual / 2
                        
                        # Actualizar valores en la tabla
                        nuevos_valores = [
                            cantidad,  # Cantidad igual
                            descripcion,  # Descripción igual
                            f"{nuevo_precio:.2f}",  # Precio dividido
                            f"{nuevo_total:.2f}"  # Total dividido
                        ]
                        
                        self.tree.item(item_id, values=nuevos_valores)
                        logger.info(f"Concepto dividido: {descripcion} - Precio: {precio_unitario:.2f} → {nuevo_precio:.2f}, Total: {total_actual:.2f} → {nuevo_total:.2f}")
                    
                except (ValueError, TypeError, IndexError) as e:
                    logger.error(f"Error al dividir concepto {item_id}: {e}")
                    continue
            
            logger.info("División de conceptos completada")
            
            # Marcar que los valores ya fueron divididos
            self.valores_ya_divididos = True
            logger.info("Flag valores_ya_divididos establecido a True")
            
            messagebox.showinfo("División Completada", "Los totales y conceptos han sido divididos a la mitad.")
            
        except Exception as e:
            logger.error(f"Error al dividir totales y conceptos: {e}")
            messagebox.showerror("Error", f"Error al dividir: {str(e)}")
    
    def calcular_valores_complementarios(self):
        """Calcula los valores complementarios para la segunda factura dividida."""
        try:
            logger.info("Iniciando cálculo de valores complementarios")
            
            # Verificar que tengamos valores originales guardados (del XML)
            if not hasattr(self, 'valores_originales_totales') or not self.valores_originales_totales:
                logger.error("No se encontraron valores originales para calcular complementos")
                messagebox.showerror("Error", 
                    "No se encontraron valores originales para calcular complementos.\n\n"
                    "Los valores originales se guardan automáticamente cuando se carga el XML.\n"
                    "Por favor, cargue nuevamente el archivo XML.")
                return
            
            # Obtener valores actuales de la primera factura desde la interfaz (valores modificados por el usuario)
            totales_primera = {k: v.get() for k, v in self.entries_totales.items()}
            logger.info(f"Totales primera factura (modificados por usuario): {totales_primera}")
            logger.info(f"Valores originales del XML (sin modificaciones): {self.valores_originales_totales}")
            
            # Calcular complementos para totales: Original - Primera = Complemento
            for k in ["Subtotal", "Ret", "IVA", "TOTAL"]:
                try:
                    # Manejar valores vacíos o None
                    valor_original_str = self.valores_originales_totales.get(k, "0")
                    valor_primera_str = totales_primera.get(k, "0")
                    
                    # Convertir valores vacíos o None a "0"
                    if not valor_original_str or valor_original_str.strip() == "":
                        valor_original_str = "0"
                    if not valor_primera_str or valor_primera_str.strip() == "":
                        valor_primera_str = "0"
                    
                    valor_original = float(valor_original_str)
                    valor_primera = float(valor_primera_str)
                    valor_complemento = valor_original - valor_primera
                    
                    # Actualizar en la interfaz
                    self.entries_totales[k].delete(0, "end")
                    self.entries_totales[k].insert(0, f"{valor_complemento:.2f}")
                    
                    logger.info(f"{k}: Original={valor_original:.2f}, Primera={valor_primera:.2f}, Complemento={valor_complemento:.2f}")
                    
                except (ValueError, TypeError) as e:
                    logger.error(f"Error al calcular complemento para {k}: {e}")
                    # En caso de error, poner 0 como valor complementario
                    self.entries_totales[k].delete(0, "end")
                    self.entries_totales[k].insert(0, "0.00")
                    continue
            
            # Calcular complementos para conceptos
            logger.info("Calculando complementos para conceptos")
            conceptos_primera = []
            for item_id in self.tree.get_children():
                try:
                    valores = list(self.tree.item(item_id, "values"))
                    if len(valores) >= 4:
                        conceptos_primera.append({
                            "cantidad": valores[0],
                            "descripcion": valores[1],
                            "precio_unitario": float(valores[2]),
                            "total": float(valores[3])
                        })
                except (ValueError, TypeError, IndexError) as e:
                    logger.error(f"Error al procesar concepto {item_id}: {e}")
                    continue
            
            # Verificar que tengamos conceptos originales
            if not hasattr(self, 'valores_originales_conceptos') or not self.valores_originales_conceptos:
                logger.error("No se encontraron conceptos originales")
                messagebox.showwarning("Advertencia", 
                    "No se encontraron conceptos originales.\n"
                    "Los complementos de totales se calcularon correctamente,\n"
                    "pero los conceptos permanecerán sin cambios.")
                return
            
            # Calcular complementos para cada concepto: Original - Primera = Complemento
            for i, (concepto_original, concepto_primera) in enumerate(zip(self.valores_originales_conceptos, conceptos_primera)):
                try:
                    # Precio unitario complementario
                    precio_original = concepto_original["precio_unitario"]
                    precio_primera = concepto_primera["precio_unitario"]
                    precio_complemento = precio_original - precio_primera
                    
                    # Total complementario
                    total_original = concepto_original["total"]
                    total_primera = concepto_primera["total"]
                    total_complemento = total_original - total_primera
                    
                    # Actualizar en la tabla (cantidad y descripción permanecen iguales)
                    item_id = list(self.tree.get_children())[i]
                    nuevos_valores = [
                        concepto_original["cantidad"],  # Cantidad igual
                        concepto_original["descripcion"],  # Descripción igual
                        f"{precio_complemento:.2f}",  # Precio complementario
                        f"{total_complemento:.2f}"  # Total complementario
                    ]
                    
                    self.tree.item(item_id, values=nuevos_valores)
                    logger.info(f"Concepto {i+1}: {concepto_original['descripcion']} - "
                              f"Precio original: {precio_original:.2f}, Primera: {precio_primera:.2f}, Complemento: {precio_complemento:.2f}")
                    
                except (ValueError, TypeError, IndexError) as e:
                    logger.error(f"Error al calcular complemento para concepto {i}: {e}")
                    continue
            
            logger.info("Cálculo de valores complementarios completado")
            
        except Exception as e:
            logger.error(f"Error al calcular valores complementarios: {e}")
            messagebox.showerror("Error", f"Error al calcular complementos: {str(e)}")
    
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
                getattr(datos, "subtotal", ""),
                getattr(datos, "subtotal", "")
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
            self.folio_segunda_factura = None
            self.valores_ya_divididos = False
            self.division_con_duplicado = False
            
            # Limpiar valores originales del XML (para cálculo de complementarios)
            self.valores_originales_totales = {}
            self.valores_originales_conceptos = []
            
            # Limpiar valores antes de dividir (para el método dividir_totales_conceptos)
            self.valores_antes_dividir_totales = {}
            self.valores_antes_dividir_conceptos = []
            
            # Limpiar frames principales
            self.proveedor_frame.clear_entries()
            self.solicitud_frame.clear_entries()
            
            # Restablecer valores por defecto de manera segura
            try:
                # Para el campo Tipo
                if hasattr(self.solicitud_frame, 'tipo_search') and self.solicitud_frame.tipo_search:
                    # Es SearchEntry, buscar el valor por defecto
                    default_tipo = AppConfig.DEFAULT_VALUES["tipo_solicitud"]
                    for item in self.solicitud_frame.tipo_search.items:
                        if item.get('clave') in default_tipo or default_tipo in str(item):
                            self.solicitud_frame.tipo_search.set_selection(item)
                            break
                else:
                    # Es Combobox tradicional
                    self.solicitud_frame.entries["Tipo"].set(AppConfig.DEFAULT_VALUES["tipo_solicitud"])
                
                # Para el campo Depa (siempre es Combobox)
                self.solicitud_frame.entries["Depa"].set(AppConfig.DEFAULT_VALUES["departamento"])
            except Exception as e:
                logger.error(f"Error al restablecer valores por defecto: {e}")
                # Continuar con la limpieza aunque falle el restablecimiento
            
            # Limpiar tabla de conceptos
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Limpiar totales
            logger.info("Limpiando campos de totales...")
            for nombre, entry in self.entries_totales.items():
                entry.delete(0, "end")
                logger.debug(f"Total {nombre} limpiado")
            
            # Limpiar categorías
            logger.info("Limpiando categorías...")
            self.limpiar_categorias()
            
            # Limpiar comentarios
            self.comentarios.delete("1.0", "end")
            
            logger.info("Formulario limpiado")
            
        except Exception as e:
            logger.error(f"Error al limpiar formulario: {e}")
    
    def limpiar_categorias(self):
        """Limpia las categorías."""
        for nombre, entry in self.entries_categorias.items():
            entry.delete(0, "end")
            logger.debug(f"Categoría {nombre} limpiada")
    
    def guardar_categorias(self):
        """Guarda las categorías como favorito."""
        try:
            # Obtener valores actuales de las categorías
            categorias = {k: v.get() for k, v in self.entries_categorias.items()}
            
            # Verificar que hay al menos un valor
            if not any(categorias.values()):
                messagebox.showwarning("Advertencia", "No hay valores en las categorías para guardar.")
                return
            
            # Validar que la suma sea 100 antes de mostrar el popup
            valores = [entry.get() for entry in self.entries_categorias.values()]
            es_valido, mensaje = self.validation_service.validar_suma_categorias(valores)
            if not es_valido:
                messagebox.showerror("Error de validación", mensaje)
                return
            
            # Popup para seleccionar posición y nombre
            self.mostrar_popup_guardar_favorito(categorias)
            
        except Exception as e:
            logger.error(f"Error al guardar categorías: {e}")
            messagebox.showerror("Error", f"Error al guardar categorías: {str(e)}")

    def mostrar_popup_guardar_favorito(self, categorias):
        """Muestra popup para guardar favorito con diseño horizontal usando ttkbootstrap."""
        popup = tb.Toplevel(self)
        popup.title("Guardar Favorito")
        
        # Usar utilidades seguras si están disponibles
        if UI_HELPERS_AVAILABLE:
            geometry = get_safe_window_size("popup_favoritos")
            safe_set_geometry(popup, geometry, "600x280")
        else:
            popup.geometry("600x280")
            
        popup.resizable(False, False)
        popup.grab_set()  # Modal
        
        # Centrar el popup de forma segura
        popup.transient(self)
        if UI_HELPERS_AVAILABLE:
            center_window_on_parent(popup, self, offset_x=50, offset_y=50)
        else:
            # Método básico de centrado
            try:
                popup.geometry("+%d+%d" % (
                    self.winfo_rootx() + 50,
                    self.winfo_rooty() + 50
                ))
            except Exception as e:
                logger.warning(f"Error al centrar popup: {e}")
                # Usar posición por defecto si falla
                popup.geometry("+100+100")
        
        # Frame principal
        main_frame = tb.Frame(popup)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        tb.Label(
            main_frame, 
            text="Nombre del favorito:", 
            font=("Segoe UI", 14, "bold"),
            #bootstyle="inverse"
        ).pack(pady=(0, 15))
        
        # Entry para el nombre
        entry_nombre = tb.Entry(
            main_frame, 
            width=40, 
            font=("Segoe UI", 12),
            justify="center",
            bootstyle="dark"
        )
        entry_nombre.pack(pady=(0, 25))
        entry_nombre.insert(0, "Nuevo Favorito")
        entry_nombre.select_range(0, "end")
        entry_nombre.focus()
        
        # Frame para los 5 botones horizontales
        frame_botones = tb.Frame(main_frame)
        frame_botones.pack(pady=10)
        
        # Obtener favoritos existentes para mostrar nombres actuales
        try:
            favoritos_existentes = self.db_manager.obtener_favoritos_usuario(self.usuario_actual_id)
            favoritos_dict = {f.posicion: f.nombre_personalizado for f in favoritos_existentes}
        except:
            favoritos_dict = {}
        
        def guardar_favorito(posicion):
            """Guarda el favorito en la posición especificada."""
            nombre = entry_nombre.get().strip()
            if not nombre:
                messagebox.showerror("Error", "El nombre no puede estar vacío.")
                entry_nombre.focus()
                return
            
            # Confirmar si va a sobrescribir
            if posicion in favoritos_dict:
                respuesta = messagebox.askyesno(
                    "Confirmar sobrescritura",
                    f"¿Desea sobrescribir el favorito '{favoritos_dict[posicion]}'?"
                )
                if not respuesta:
                    return
    
        # Guardar en la base de datos
            try:
                favorito = self.db_manager.guardar_reparto_favorito(
                    self.usuario_actual_id, posicion, nombre, categorias
                )
                
                if favorito:
                    messagebox.showinfo("Éxito", f"Favorito '{nombre}' guardado en posición {posicion + 1}")
                    self.actualizar_nombres_favoritos()
                    popup.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo guardar el favorito.")
            except Exception as e:
                logger.error(f"Error al guardar favorito: {e}")
                messagebox.showerror("Error", f"Error al guardar favorito: {str(e)}")

    # Crear los 5 botones horizontales
        for i in range(5):
            nombre_actual = favoritos_dict.get(i, "Vacío")
            texto_boton = f"Pos {i + 1}\n{nombre_actual}"
            
            # Determinar estilo del botón
            if i in favoritos_dict:
                estilo = "warning"  # Naranja para ocupados
            else:
                estilo = "success"  # Verde para vacíos
            
            btn = tb.Button(
                frame_botones,
                text=texto_boton,
                bootstyle=estilo,
                width=12,
                command=lambda pos=i: guardar_favorito(pos)
            )
            btn.grid(row=0, column=i, padx=5, pady=5)
        
        # Frame para botón cancelar
        frame_cancelar = tb.Frame(main_frame)
        frame_cancelar.pack(pady=(20, 0))
        
        tb.Button(
            frame_cancelar,
            text="Cancelar",
            bootstyle="danger",
            width=15,
            command=popup.destroy
        ).pack()
        
        # Solo Escape para cancelar (no Enter)
        popup.bind('<Escape>', lambda e: popup.destroy())
        
        # Enfocar el entry al mostrar el popup
        popup.after(100, lambda: entry_nombre.focus())

    def cargar_favorito(self, indice: int):
        """Carga un favorito en los campos de categorías."""
        try:
            favorito = self.db_manager.obtener_favorito_por_posicion(self.usuario_actual_id, indice)
            
            if not favorito:
                messagebox.showinfo("Info", f"No hay favorito guardado en la posición {indice + 1}")
                return
            
            # Limpiar categorías actuales
            self.limpiar_categorias()
            
            # Cargar valores del favorito
            valores_favorito = {
                "Comer": favorito.comercial or 0,
                "Fleet": favorito.fleet or 0,
                "Semis": favorito.seminuevos or 0,
                "Refa": favorito.refacciones or 0,
                "Serv": favorito.servicio or 0,
                "HyP": favorito.hyp or 0,
                "Admin": favorito.administracion or 0
            }
            
            # Llenar los campos
            for categoria, valor in valores_favorito.items():
                if categoria in self.entries_categorias and valor != 0:
                    self.entries_categorias[categoria].delete(0, "end")
                    self.entries_categorias[categoria].insert(0, str(valor))
            
            logger.info(f"Favorito '{favorito.nombre_personalizado}' cargado desde posición {indice + 1}")
            
        except Exception as e:
            logger.error(f"Error al cargar favorito: {e}")
            messagebox.showerror("Error", f"Error al cargar favorito: {str(e)}")
    
    def _formatear_numero(self, valor):
        """
        Formatea un número para mostrar:
        - Sin decimales si es entero (1.00 -> 1)
        - Máximo 2 decimales si tiene decimales (2.5839572 -> 2.58)
        """
        try:
            # Convertir a float
            numero = float(valor)
            
            # Si es un número entero, mostrar sin decimales
            if numero == int(numero):
                return str(int(numero))
            else:
                # Si tiene decimales, redondear a 2 decimales
                return f"{numero:.2f}"
                
        except (ValueError, TypeError):
            # Si no se puede convertir, devolver el valor original
            return str(valor)
    
    def _formatear_porcentaje(self, valor):
        """
        Formatea un valor de porcentaje:
        - Si es 0 o vacío, devuelve cadena vacía
        - Si es diferente de 0, agrega el símbolo %
        """
        try:
            # Si está vacío o es None, devolver vacío
            if not valor or str(valor).strip() == "":
                return ""
            
            # Convertir a float para validar
            numero = float(valor)
            
            # Si es 0, devolver vacío
            if numero == 0:
                return ""
            else:
                # Si es diferente de 0, formatear y agregar %
                if numero == int(numero):
                    return f"{int(numero)}%"
                else:
                    return f"{numero:.2f}%"
                    
        except (ValueError, TypeError):
            # Si no se puede convertir pero no está vacío, devolver con %
            valor_str = str(valor).strip()
            if valor_str and valor_str != "0":
                return f"{valor_str}%"
            else:
                return ""
    
    def _formatear_moneda(self, valor):
        """
        Formatea un valor monetario con formato $x,xxx.xx
        - Agrega símbolo de peso $
        - Usa comas para separar miles
        - Siempre muestra 2 decimales
        """
        try:
            # Si está vacío o es None, devolver vacío
            if not valor or str(valor).strip() == "":
                return ""
            
            # Convertir a float
            numero = float(valor)
            
            # Si es 0, devolver $0.00
            if numero == 0:
                return "$0.00"
            
            # Formatear con comas y 2 decimales
            return f"${numero:,.2f}"
                
        except (ValueError, TypeError):
            # Si no se puede convertir, devolver el valor original
            return str(valor)
    
    def _obtener_nombre_para_archivo(self, proveedor_data):
        """Obtiene el nombre del proveedor para el archivo, priorizando nombre_contacto"""
        if not proveedor_data:
            return "PROVEEDOR_DESCONOCIDO"
        
        rfc = proveedor_data.get("RFC", "").strip()
        
        if rfc:
            try:
                # Buscar el proveedor por RFC en la base de datos
                from bd.models import Proveedor
                proveedor = Proveedor.get(Proveedor.rfc == rfc)
                
                # Priorizar nombre_contacto si existe y no está vacío
                if hasattr(proveedor, 'nombre_contacto') and proveedor.nombre_contacto and proveedor.nombre_contacto.strip():
                    return proveedor.nombre_contacto.strip()
                # Si no hay nombre_contacto, usar nombre_emisor
                elif hasattr(proveedor, 'nombre_emisor') and proveedor.nombre_emisor and proveedor.nombre_emisor.strip():
                    return proveedor.nombre_emisor.strip()
            except:
                # Si no se encuentra en la base de datos o hay error, usar el nombre del formulario
                pass
        
        # Fallback al nombre del formulario
        nombre_formulario = proveedor_data.get("Nombre", "").strip()
        return nombre_formulario if nombre_formulario else "PROVEEDOR_DESCONOCIDO"
    
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
            
            # Recopilar datos del formulario (excepto conceptos, que se recopilarán después de división)
            proveedor_data = self.proveedor_frame.get_data()
            solicitud_data = self.solicitud_frame.get_data()
            totales = {k: v.get() for k, v in self.entries_totales.items()}
            categorias = {k: v.get() for k, v in self.entries_categorias.items()}
            comentarios = self.comentarios.get("1.0", "end").strip()
            logger.info("Datos del formulario recopilados correctamente (conceptos se recopilarán después de división)")

            # Detectar si es la segunda factura después de dividir
            dividir_marcado = self.dividir_var.get()
            dividir_habilitado = str(self.chb_dividir.cget('state')) == "normal"
            
            # LÓGICA CORREGIDA: Detectar segunda factura basándose en:
            # 1. Checkbox dividir deshabilitado (ya se generó primera factura)
            # No importa el tipo específico, ya que puede ser VC u otro tipo
            es_segunda_factura = not dividir_habilitado
            
            if es_segunda_factura:
                logger.info("Detectada segunda factura después de dividir")
                
                # Si la factura original estaba duplicada (XML ya existía), 
                # usar el folio que ya se pidió al inicio
                if self.factura_duplicada and hasattr(self, 'folio_segunda_factura') and self.folio_segunda_factura:
                    logger.info("Usando folio pre-configurado para segunda factura")
                    folio_vc = self.folio_segunda_factura
                    # Actualizar el folio interno manual para la segunda factura
                    self.folio_interno_manual = folio_vc
                    logger.info(f"Folio asignado para segunda factura: {folio_vc}")
                elif self.factura_duplicada:
                    # Fallback: pedir folio si no se configuró al inicio (no debería pasar)
                    logger.warning("Folio para segunda factura no fue configurado, pidiendo ahora")
                    
                    # Usar el folio manual actual como valor inicial para la segunda factura
                    folio_inicial_segunda = self.folio_interno_manual or "001"
                    
                    # Pedir folio manual para la segunda factura
                    folio_manual_segunda = simpledialog.askstring(
                        "Folio para Segunda Factura (VC)",
                        f"El XML original ya existía en la base de datos.\n\n"
                        f"Ingrese el folio interno para la segunda factura (VC):",
                        initialvalue=folio_inicial_segunda
                    )
                    
                    if folio_manual_segunda and folio_manual_segunda.strip():
                        folio_vc = folio_manual_segunda.strip()
                        # Actualizar el folio interno manual para la segunda factura
                        self.folio_interno_manual = folio_vc
                        logger.info(f"Folio manual asignado para segunda factura: {folio_vc}")
                    else:
                        logger.warning("Usuario canceló la entrada de folio para segunda factura")
                        messagebox.showwarning("Advertencia", "Debe ingresar un folio para la segunda factura")
                        return
                else:
                    # Para facturas divididas, mantener el mismo folio que la primera factura
                    folio_original = solicitud_data.get("Folio", "001")
                    folio_vc = folio_original  # Mantener el mismo folio
                    
                    logger.info(f"Folio mantenido para segunda factura dividida: {folio_vc}")
                
                # Actualizar el folio en el formulario y en los datos
                folio_widget = self.solicitud_frame.entries["Folio"]
                folio_widget.delete(0, 'end')
                folio_widget.insert(0, folio_vc)
                solicitud_data["Folio"] = folio_vc
                logger.info(f"Folio actualizado para segunda factura: {folio_vc}")

            # Recopilar conceptos (ya no hay división automática)
            conceptos = [self.tree.item(item, "values") for item in self.tree.get_children()]
            logger.info(f"Conceptos recopilados: {len(conceptos)} conceptos")

            data = {
                "TIPO DE VALE": solicitud_data.get("Tipo", ""),
                "C A N T I D A D": "\n".join([self._formatear_numero(c[0]) for c in conceptos]),
                "C O M E N T A R I O S": comentarios,
                "Nombre de Empresa": proveedor_data.get("Nombre", ""), 
                "RFC": proveedor_data.get("RFC", ""), 
                "Teléfono": proveedor_data.get("Teléfono", ""), 
                "Correo": proveedor_data.get("Correo", ""), 
                "Nombre Contacto": proveedor_data.get("Contacto", ""),
                "Menudeo": self._formatear_porcentaje(categorias.get("Comer", "")), 
                "Seminuevos": self._formatear_porcentaje(categorias.get("Semis", "")), 
                "Flotas": self._formatear_porcentaje(categorias.get("Fleet", "")),
                "Administración": self._formatear_porcentaje(categorias.get("Admin", "")),
                "Refacciones": self._formatear_porcentaje(categorias.get("Refa", "")),
                "Servicio": self._formatear_porcentaje(categorias.get("Serv", "")),
                "HYP": self._formatear_porcentaje(categorias.get("HyP", "")),
                "DESCRIPCIÓN": "\n".join([c[1] for c in conceptos]),
                "PRECIO UNITARIO": "\n".join([self._formatear_moneda(c[2]) for c in conceptos]),
                "TOTAL": "\n".join([self._formatear_moneda(c[3]) for c in conceptos]),
                "FECHA GERENTE DE ÁREA": "", 
                "FECHA GERENTE ADMINISTRATIVO": "", 
                "FECHA DE AUTORIZACIÓN GG O DIRECTOR DE MARCA": "", 
                "SUBTOTAL": self._formatear_moneda(totales.get("Subtotal", "")), 
                "IVA": self._formatear_moneda(totales.get("IVA", "")), 
                "TOTAL, SUMATORIA": self._formatear_moneda(totales.get("TOTAL", "")), 
                "FECHA CREACIÓN SOLICITUD": solicitud_data.get("Fecha", ""), 
                "FOLIO": "",
                "RETENCIÓN": self._formatear_moneda(totales.get("Ret", "")), 
                "Departamento": solicitud_data.get("Depa", "")
            }
            logger.info("Datos preparados para generación de documento")

            # TODO: Aquí deberías llamar a tu servicio de generación de PDF/documento
            try:
                # DEBUG: Logging de variables críticas
                logger.debug(f"DEBUG - factura_duplicada: {self.factura_duplicada}")
                logger.debug(f"DEBUG - division_con_duplicado: {self.division_con_duplicado}")
                logger.debug(f"DEBUG - es_segunda_factura: {es_segunda_factura}")
                logger.debug(f"DEBUG - folio_interno_manual: {self.folio_interno_manual}")
                logger.debug(f"DEBUG - dividir_marcado: {dividir_marcado}")
                logger.debug(f"DEBUG - dividir_habilitado: {dividir_habilitado}")
                
                # Verificar si la factura NO debe guardarse en base de datos
                # Casos donde NO se guarda:
                # 1. Factura duplicada sin división (primera factura normal duplicada)
                # 2. Primera factura de división con duplicado (la SC ya existe en BD)
                # 
                # Casos donde SÍ se guarda:
                # 1. Primera factura de división normal (SC nueva)
                # 2. Segunda factura de división (VC siempre es nueva, incluso con duplicado)
                # 3. Factura normal sin división
                es_contexto_no_guardar = (
                    # Factura duplicada sin división
                    (self.factura_duplicada and not (dividir_marcado or es_segunda_factura)) or
                    # Primera factura de división con duplicado (SC ya existe)
                    (self.division_con_duplicado and not es_segunda_factura)
                )
                
                logger.debug(f"DEBUG - es_contexto_no_guardar: {es_contexto_no_guardar}")
                
                # Seleccionar ruta de guardado
                # Construir nombre de archivo con formato: Folio Interno, Proveedor, Folio factura, Clase
                # Obtener el folio interno que se usará en la BD (si no es contexto de no guardar)
                if not es_contexto_no_guardar:
                    # Se guardará en BD: obtener el próximo folio interno
                    folio_interno = str(self.obtener_proximo_folio_interno())
                else:
                    # No se guardará en BD: usar folio manual si existe
                    folio_interno = self.folio_interno_manual
                
                proveedor = self._obtener_nombre_para_archivo(proveedor_data)
                folio_factura = solicitud_data.get("Folio", "")
                clase = solicitud_data.get("Clase", "")  # Campo específico del formulario
                
                # Construcción del nombre según el formato solicitado: Folio Interno, Proveedor, Folio factura, Clase
                if folio_interno:
                    nombre_elementos = [folio_interno, proveedor, folio_factura, clase]
                else:
                    # Si no hay folio interno, usar formato reducido
                    nombre_elementos = [proveedor, folio_factura, clase]
                
                # Filtrar campos vacíos y construir nombre con espacios
                nombre_archivo = " ".join(filter(lambda x: x and x.strip(), nombre_elementos))
                
                ruta = filedialog.asksaveasfilename(
                    title="Guardar solicitud",
                    filetypes=[("PDF", "*.pdf")],
                    initialfile=nombre_archivo
                )
                if not ruta:
                    logger.info("Exportación cancelada por el usuario")
                    return
                if not ruta.lower().endswith(".pdf"):
                    ruta += ".pdf"
                logger.info(f"Ruta de guardado seleccionada: {ruta}")
                
                if es_contexto_no_guardar:
                    if self.factura_duplicada and not (dividir_marcado or es_segunda_factura):
                        logger.info("Factura duplicada sin división detectada, omitiendo guardado en base de datos")
                    elif self.division_con_duplicado and not es_segunda_factura:
                        logger.info("Primera factura en división con duplicado (SC ya existe), omitiendo guardado en base de datos")
                    
                    # Usar el folio interno manual proporcionado por el usuario
                    folio_a_usar = self.folio_interno_manual or "DUPLICADO"
                    logger.info(f"DEBUG - Asignando folio manual: {folio_a_usar} (folio_interno_manual: {self.folio_interno_manual})")
                    data["FOLIO"] = folio_a_usar
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
                        "tipo": self._get_tipo_value_from_solicitud_frame(),  # Usar método mejorado
                        "nombre_receptor": "TCM MATEHUALA",  # Valor por defecto
                        "rfc_receptor": "TMM860630PH1",  # Valor por defecto
                        "clase": solicitud_data.get("Clase", ""),  # Campo clase
                        "departamento": solicitud_data.get("Depa", ""),  # Campo departamento
                        "es_segunda_factura_dividida": es_segunda_factura  # Agregar flag para la segunda factura
                    }
                    
                    # IMPORTANTE: Usar los totales ya divididos si la funcionalidad está activa
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
                    if factura and hasattr(factura, 'folio_interno') and factura.folio_interno:
                        logger.info(f"Factura guardada en la base de datos con folio_interno: {factura.folio_interno}")
                        data["FOLIO"] = str(factura.folio_interno)
                        
                        # Sincronizar la secuencia PostgreSQL después de guardar
                        self.sincronizar_secuencia_folio()
                    else:
                        logger.warning("Factura guardada pero sin folio_interno válido")
                        data["FOLIO"] = "SIN_FOLIO"
                
            except Exception as db_error:
                logger.warning(f"Error al guardar en base de datos: {db_error}")
                logger.debug(f"DEBUG - Exception caught, folio_interno_manual: {self.folio_interno_manual}")
                # Continúa sin guardar en BD pero genera el PDF
                folio_error = self.folio_interno_manual or "ERROR"
                logger.warning(f"DEBUG - Asignando folio por excepción: {folio_error}")
                data["FOLIO"] = folio_error
                
            self.control.rellenar_formulario(data, ruta)
            logger.info("Formulario rellenado con datos de la factura")

            # Mensaje de éxito personalizado según si se guardó en BD o no
            if es_contexto_no_guardar:
                if self.factura_duplicada and not (dividir_marcado or es_segunda_factura):
                    mensaje_exito = (
                        f"Solicitud generada correctamente en:\n{ruta}\n\n"
                        f"NOTA: La factura ya existía en la base de datos, "
                        f"por lo que no se guardó nuevamente.\n"
                        f"Folio interno asignado: {self.folio_interno_manual}"
                    )
                elif self.division_con_duplicado and not es_segunda_factura:
                    mensaje_exito = (
                        f"Primera factura (SC) generada correctamente en:\n{ruta}\n\n"
                        f"NOTA: Esta factura ya existía en la base de datos, "
                        f"por lo que no se guardó nuevamente.\n"
                        f"Folio interno asignado: {self.folio_interno_manual}"
                    )
                else:
                    mensaje_exito = (
                        f"Solicitud generada correctamente en:\n{ruta}\n\n"
                        f"NOTA: No se guardó en la base de datos.\n"
                        f"Folio interno asignado: {self.folio_interno_manual}"
                    )
            else:
                if es_segunda_factura:
                    mensaje_exito = f"Segunda factura (VC) generada y guardada correctamente en:\n{ruta}"
                else:
                    mensaje_exito = f"Solicitud generada y guardada correctamente en:\n{ruta}"
            
            messagebox.showinfo("Éxito", mensaje_exito)
            logger.info(f"Solicitud generada y guardada en: {ruta}")

            # Alternar estado del checkbox dividir
            if dividir_habilitado and dividir_marcado:
                self.chb_dividir.config(state="disabled")
                
                # Configurar el tipo de vale a VC por defecto (el usuario puede cambiarlo si necesita)
                if hasattr(self.solicitud_frame, 'tipo_search') and self.solicitud_frame.tipo_search:
                    # Es SearchEntry, buscar específicamente el item con clave 'VC'
                    logger.info("Estableciendo VC como tipo por defecto para segunda factura")
                    vc_encontrado = False
                    for item in self.solicitud_frame.tipo_search.items:
                        if item.get('clave') == 'VC':
                            self.solicitud_frame.tipo_search.set_selection(item)
                            logger.info(f"Tipo VC seleccionado por defecto: {item}")
                            vc_encontrado = True
                            break
                    
                    if not vc_encontrado:
                        logger.warning("No se encontró item VC en SearchEntry")
                        # Fallback: intentar buscar por descripción
                        for item in self.solicitud_frame.tipo_search.items:
                            if 'VALE DE CONTROL' in str(item).upper():
                                self.solicitud_frame.tipo_search.set_selection(item)
                                logger.info(f"Tipo VC encontrado por descripción: {item}")
                                break
                else:
                    # Es Combobox tradicional (caso poco probable según la verificación)
                    logger.info("Usando Combobox tradicional para establecer VC por defecto")
                    tipo_widget = self.solicitud_frame.entries["Tipo"]
                    if hasattr(tipo_widget, 'set'):
                        tipo_widget.set("VC - VALE DE CONTROL")
                        logger.info("Tipo VC establecido por defecto en Combobox")
                    else:
                        logger.warning("Widget Tipo no soporta método set()")
                        
                logger.info("Checkbox dividir deshabilitado y tipo de vale establecido a VC por defecto")
                
                # CALCULAR VALORES COMPLEMENTARIOS INMEDIATAMENTE ANTES DEL SIGUIENTE GENERAR
                logger.info("Calculando valores complementarios para actualizar la interfaz")
                self.calcular_valores_complementarios()
                
                # Mostrar mensaje al usuario indicando que debe generar nuevamente
                messagebox.showinfo(
                    "Segunda Factura Lista", 
                    f"Primera factura (SC) guardada correctamente.\n\n"
                    f"El tipo se ha establecido a 'VC - VALE DE CONTROL' por defecto.\n"
                    f"NOTA: Puede cambiar el tipo si la segunda factura no es VC.\n\n"
                    f"Los valores complementarios han sido calculados automáticamente.\n"
                    f"Haga clic en 'Generar' nuevamente para guardar la segunda factura."
                )
                
                return
            elif es_segunda_factura:
                # Es la segunda factura (VC), habilitar nuevamente el checkbox
                self.chb_dividir.config(state="normal")
                self.dividir_var.set(False)  # Desmarcar el checkbox
                self.valores_ya_divididos = False  # Resetear flag de división
                self.division_con_duplicado = False  # Resetear flag de división con duplicado
                self.folio_segunda_factura = None  # Resetear folio segunda factura
                
                # Limpiar valores originales y de división después de completar la división
                self.valores_originales_totales = {}
                self.valores_originales_conceptos = []
                self.valores_antes_dividir_totales = {}
                self.valores_antes_dividir_conceptos = []
                
                logger.info("Segunda factura (VC) completada, checkbox dividir habilitado y desmarcado")
                logger.info("Flags de división y valores originales reseteados después de completar división")
            else:
                self.chb_dividir.config(state="normal")
                logger.info("Checkbox dividir habilitado")

            # Limpiar formulario y actualizar solicitudes restantes
            self.control.delete_solicitud()
            self.actualizar_solicitudes_restantes()
            solicitudes_restantes = self.control.get_solicitudes_restantes()
            
            # Siempre limpiar primero
            self.limpiar_todo()
            
            # Solo rellenar campos si hay más solicitudes pendientes
            if solicitudes_restantes > 0:
                self.rellenar_campos()
                logger.info(f"Rellenando campos para siguiente factura. Restantes: {solicitudes_restantes}")
            else:
                logger.info("No hay más facturas. Formulario limpio.")

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
