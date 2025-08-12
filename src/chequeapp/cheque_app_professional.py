"""
Aplicación principal de Cheques - Nueva Arquitectura
Frame vacío simplificado que sigue el patrón de solicitud_app_professional.py
"""
import tkinter as tk
from tkinter import simpledialog, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from typing import Optional
import logging
import sys
import os
from datetime import date

# Importar LayoutExporter con manejo de rutas
try:
    # Intentar importación relativa (cuando se ejecuta desde main_app)
    from src.chequeapp.exportar_layout import LayoutExporter
    LAYOUT_EXPORTER_AVAILABLE = True
except ImportError:
    try:
        # Intentar importación local (cuando se ejecuta de forma independiente)
        from exportar_layout import LayoutExporter
        LAYOUT_EXPORTER_AVAILABLE = True
    except ImportError:
        try:
            # Intentar agregar ruta y importar
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            from exportar_layout import LayoutExporter
            LAYOUT_EXPORTER_AVAILABLE = True
        except ImportError as e:
            print(f"Warning: No se pudo importar LayoutExporter: {e}")
            LAYOUT_EXPORTER_AVAILABLE = False
            # Fallback class
            class LayoutExporter:
                def __init__(self, layout):
                    self.layout = layout
                def exportar_layout_excel(self, ruta_archivo=None):
                    print("LayoutExporter no disponible - usando fallback")
                    return None

# Configurar logging primero
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar la clase de base de datos de cheques
try:
    # Intentar importación relativa (cuando se ejecuta desde main_app)
    from src.chequeapp.cheque_database import ChequeDatabase
    DATABASE_IMPORT_SUCCESS = True
except ImportError:
    try:
        # Intentar importación local (cuando se ejecuta de forma independiente)
        from cheque_database import ChequeDatabase
        DATABASE_IMPORT_SUCCESS = True
    except ImportError:
        try:
            # Intentar agregar ruta y importar
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            from cheque_database import ChequeDatabase
            DATABASE_IMPORT_SUCCESS = True
        except ImportError as e:
            logger.warning(f"Error importando ChequeDatabase: {e}")
            DATABASE_IMPORT_SUCCESS = False
            # Fallback si no se puede importar
            class ChequeDatabase:
                def search_cheques(self, **kwargs):
                    return []

# Importar utilidades seguras si están disponibles
try:
    from app.utils.ui_helpers import safe_set_geometry, get_safe_window_size, center_window_on_parent
    from config.settings import WINDOW_SIZES
    UI_HELPERS_AVAILABLE = True
except ImportError:
    try:
        # Intentar importación absoluta desde la raíz del proyecto
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from app.utils.ui_helpers import safe_set_geometry, get_safe_window_size, center_window_on_parent
        from config.settings import WINDOW_SIZES
        UI_HELPERS_AVAILABLE = True
    except ImportError:
        UI_HELPERS_AVAILABLE = False
        WINDOW_SIZES = {"cheque_app": "1300x700"}
        logging.warning("Utilidades de UI no disponibles, usando métodos básicos")
        
        # Definir funciones de fallback
        def center_window_on_parent(window, parent=None):
            pass
        
        def safe_set_geometry(window, geometry):
            window.geometry(geometry)
            
        def get_safe_window_size(key, default="800x600"):
            return WINDOW_SIZES.get(key, default)


class ChequeAppProfessional(tb.Frame):
    """
    Aplicación profesional de Cheques - Frame vacío
    Sigue el patrón de solicitud_app_professional.py
    """
    
    def __init__(self, master=None):
        """
        Inicializa la aplicación de cheques
        
        Args:
            master: Widget padre
        """
        super().__init__(master)
        self.master = master
        self.logger = logger
        
        # Variables de estado
        self.initialized = False
        
        # Inicializar base de datos
        try:
            if DATABASE_IMPORT_SUCCESS:
                self.cheque_db = ChequeDatabase()
                self.logger.info("Base de datos de cheques inicializada correctamente")
            else:
                self.cheque_db = ChequeDatabase()  # Fallback class
                self.logger.warning("Usando base de datos fallback")
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
            self.cheque_db = ChequeDatabase()  # Fallback class
        
        # Referencias a widgets para acceso posterior
        self.initial_date = None
        self.final_date = None
        self.class_entry = None
        self.cheque_table = None
        self.layout_table = None
        
        self._setup_ui()
        self._post_init()
        
        self.logger.info("Aplicación profesional de cheques inicializada (frame vacío)")
    
    def _setup_ui(self):
        """Configura la interfaz de usuario básica."""
        try:
            # Configurar el frame principal
            self.pack(fill=BOTH, expand=True)
            
            # Frame principal con padding
            main_container = tb.Frame(self, padding=10)
            main_container.pack(fill=BOTH, expand=True, padx=10)
            
            # Controles de busqueda
            search_frame = tb.LabelFrame(main_container, text="Buscar")
            search_frame.pack(side=TOP, fill=X, pady=15)

            initial_date_label = tb.Label(search_frame, text="Fecha Inicial:")
            initial_date_label.pack(side=LEFT, padx=(10, 5), anchor=W)
            self.initial_date = tb.DateEntry(search_frame, width=12, dateformat='%d/%m/%Y')
            self.initial_date.pack(side=LEFT, padx=(0, 5), anchor=W)

            final_date_label = tb.Label(search_frame, text="Fecha Final:")
            final_date_label.pack(side=LEFT, padx=(0, 5), anchor=W)
            self.final_date = tb.DateEntry(search_frame, width=12, dateformat='%d/%m/%Y')
            self.final_date.pack(side=LEFT, padx=(0, 5), anchor=W)

            class_label = tb.Label(search_frame, text="Clase:")
            class_label.pack(side=LEFT, padx=(0, 5), anchor=W)
            self.class_entry = tb.Entry(search_frame)
            self.class_entry.pack(side=LEFT, padx=(0, 5), anchor=W)

            only_uncharged_label = tb.Label(search_frame, text="No Cargados:")
            only_uncharged_label.pack(side=LEFT, padx=(0, 5), anchor=W)
            self.only_uncharged_var = tk.BooleanVar()
            only_uncharged_checkbox = tb.Checkbutton(search_frame, variable=self.only_uncharged_var)
            only_uncharged_checkbox.pack(side=LEFT, padx=(0, 5), anchor=W)

            search_cheque_button = tb.Button(search_frame, text="Buscar cheques", command=self.on_search_cheques, width=15)
            search_cheque_button.pack(side=RIGHT, padx=(5, 10), pady=5, anchor=E)

            search_layout_button = tb.Button(search_frame, text="Buscar layouts", command=self.on_search_layout, width=15)
            search_layout_button.pack(side=RIGHT, padx=(25, 5), pady=10, anchor=E)

            clean_button = tb.Button(search_frame, text="Limpiar filtros", command=self.on_clean_filters, width=15)
            clean_button.pack(side=RIGHT, padx=(5, 5), pady=10, anchor=E)

            # Contenido principal
            content_frame = tb.LabelFrame(main_container, text="Agregar cheques a layout")
            content_frame.pack(fill=BOTH, expand=True)
            
            left_frame = tb.Frame(content_frame, padding=5)  # Reducir de 10 a 5
            left_frame.pack(side=LEFT, fill=BOTH, expand=True)

            center_frame = tb.Frame(content_frame, width=120, padding=5)  # Reducir de 10 a 5
            center_frame.pack(side=LEFT, fill=Y, expand=False)
            center_frame.pack_propagate(False)  # Mantener el ancho fijo 

            right_frame = tb.Frame(content_frame, padding=5)  # Reducir de 10 a 5
            right_frame.pack(side=LEFT, fill=BOTH, expand=True)

            # Trees de los cheques a cargar
            columns = ["id", "fecha", "vale", "folio", "proveedor", "monto", "banco"]
            self.cheque_table = tb.Treeview(left_frame, columns=columns, show="headings")
            self.cheque_table.pack(fill=BOTH, expand=True, padx=5, pady=5)  # Reducir de 10 a 5

            self.cargar_table = tb.Treeview(right_frame, columns=columns, show="headings")
            self.cargar_table.pack(fill=BOTH, expand=True, padx=5, pady=5)  # Reducir de 10 a 5

            for col in columns:
                self.cheque_table.heading(col, text=col.capitalize(), anchor=W)
                self.cheque_table.column(col, anchor=W)

                self.cargar_table.heading(col, text=col.capitalize(), anchor=W)
                self.cargar_table.column(col, anchor=W)

            # Definir ancho de columnas (opcional)
            c_smallest = 30
            c_small = 65
            c_medium = 100
            c_large = 200
            self.cheque_table.column("id", width=c_smallest)
            self.cheque_table.column("fecha", width=c_small)
            self.cheque_table.column("vale", width=c_small)
            self.cheque_table.column("folio", width=c_small)
            self.cheque_table.column("proveedor", width=c_medium)
            self.cheque_table.column("monto", width=c_small+5)
            self.cheque_table.column("banco", width=c_small)

            self.cargar_table.column("id", width=c_smallest)
            self.cargar_table.column("fecha", width=c_small)
            self.cargar_table.column("vale", width=c_small)
            self.cargar_table.column("folio", width=c_small)
            self.cargar_table.column("proveedor", width=c_medium)
            self.cargar_table.column("monto", width=c_small+5)
            self.cargar_table.column("banco", width=c_small)

            #cheque_table.insert("", "end", values=("2024-08-10", "V156486", "12456", "Servicio Nava Medrano", "100000.00", "BTC23"))
            #cargar_table.insert("", "end", values=("2024-08-10", "V156486", "12456", "Servicio Nava Medrano", "100000.00", "BTC23"))

            # Botones de acción
            center_buttons_width = 10  # Reducir el width a un valor más razonable en caracteres

            button_container = tb.Frame(center_frame)
            button_container.place(relx=0.5, rely=0.5, anchor=CENTER)  # Centrar en el medio del frame

            button_agregar = tb.Button(button_container, text="Agregar", command=self.on_agregar, width=center_buttons_width)
            button_agregar.pack(side=TOP, pady=(5, 5))

            button_quitar = tb.Button(button_container, text="Quitar", command=self.on_quitar, width=center_buttons_width)
            button_quitar.pack(side=TOP, pady=(5, 5))

            button_layout = tb.Button(button_container, text="Layout", command=self.on_crear_layout, width=center_buttons_width)
            button_layout.pack(side=TOP, pady=(5, 5))

            # Frame layouts
            layout_frame = tb.LabelFrame(main_container, text="Reimprimir layouts")
            layout_frame.pack(side=TOP, fill=BOTH, expand=True, pady=5)  # Reducir de 10 a 5

            layout_left_frame = tb.Frame(layout_frame)
            layout_left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5)  # Reducir de 10 a 5

            layout_right_frame = tb.Frame(layout_frame)
            layout_right_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=5)  # Reducir de 10 a 5

            # Frame de layout
            columns = ["id", "fecha", "nombre", "monto"]
            self.layout_table = tb.Treeview(layout_left_frame, columns=columns, show="headings")
            self.layout_table.pack(fill=BOTH, expand=True, padx=5, pady=5)  # Reducir de 10 a 5
            
            for col in columns:
                self.layout_table.heading(col, text=col.capitalize(), anchor=W)
                self.layout_table.column(col, anchor=W)

            self.layout_table.column("id", width=c_smallest)
            self.layout_table.column("fecha", width=c_smallest)
            self.layout_table.column("nombre", width=c_medium)
            self.layout_table.column("monto", width=c_small)
            
            frame_control_layout = tb.Frame(layout_left_frame)
            frame_control_layout.pack(side=BOTTOM, fill=X, padx=5)

            button_mostrar = tb.Button(frame_control_layout, text="Mostrar", command=self.on_mostrar, width=10)
            button_mostrar.pack(side=RIGHT, padx=(5, 0), pady=(0, 5))

            button_exportar = tb.Button(frame_control_layout, text="Exportar", command=self.on_generar, width=10)
            button_exportar.pack(side=RIGHT, padx=(5, 0), pady=(0, 5))

            button_modificar = tb.Button(frame_control_layout, text="Modificar", command=self.on_modificar, width=10)
            button_modificar.pack(side=RIGHT, padx=(5, 0), pady=(0, 5))

            button_eliminar = tb.Button(frame_control_layout, text="Eliminar", command=self.on_eliminar, width=10)
            button_eliminar.pack(side=RIGHT, padx=(5, 0), pady=(0, 5))

            columns = ["alias", "nombre", "importe", "descripcion", "referencia"]
            self.layout = tb.Treeview(layout_right_frame, columns=columns, show="headings")
            self.layout.pack(fill=BOTH, expand=True, padx=5, pady=5)  # Reducir de 10 a 5

            for col in columns:
                self.layout.heading(col, text=col.capitalize(), anchor=W)
                self.layout.column(col, anchor=W)

            self.layout.column("alias", width=c_small-20)
            self.layout.column("nombre", width=c_medium)
            self.layout.column("importe", width=c_small)
            self.layout.column("descripcion", width=c_large)
            self.layout.column("referencia", width=c_small)

            button_copy_layout_names = [
                ["Alias", lambda: self.copy_layout("alias")],
                ["Importe", lambda: self.copy_layout("importe")],
                ["Descripción", lambda: self.copy_layout("descripcion")],
                ["Referencia", lambda: self.copy_layout("referencia")]
            ]

            for button_name, command in reversed(button_copy_layout_names):
                button = tb.Button(layout_right_frame, text=button_name, command=command, width=11)
                button.pack(side=RIGHT, padx=(5, 0), pady=(0, 5))

            label_copyclipboard = tb.Label(layout_right_frame, text="Copiar al portapapeles:", anchor=E)
            label_copyclipboard.pack(side=RIGHT, padx=10, pady=(10, 0))

            self.logger.info("Interfaz de usuario configurada correctamente")
            
        except Exception as e:
            self.logger.error(f"Error configurando interfaz: {e}")
            self._create_error_content(str(e))
    
    def _format_date(self, date_str):
        """Formatea una fecha de YYYY-MM-DD a DD/MM/YY"""
        if not date_str:
            return ""
        
        try:
            from datetime import datetime
            # Intentar parsear diferentes formatos
            if len(date_str) == 10 and '-' in date_str:  # YYYY-MM-DD
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            elif len(date_str) == 8:  # YYYYMMDD
                date_obj = datetime.strptime(date_str, '%Y%m%d')
            elif '/' in date_str:  # Ya está en formato DD/MM/YYYY o similar
                if len(date_str.split('/')[-1]) == 2:  # Ya es DD/MM/YY
                    return date_str
                else:  # DD/MM/YYYY
                    date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            else:
                return date_str  # Retornar sin cambios si no se reconoce
            
            # Formatear como DD/MM/YY
            return date_obj.strftime('%d/%m/%y')
        except Exception:
            return date_str  # En caso de error, retornar la fecha original
    
    
    def _create_error_content(self, error_msg):
        """Crea contenido de error en caso de fallo."""
        error_frame = tb.Frame(self, padding=20)
        error_frame.pack(fill=BOTH, expand=True)
        
        error_label = tb.Label(
            error_frame,
            text=f"❌ Error al cargar la aplicación de cheques:\n{error_msg}",
            font=("Segoe UI", 12),
            bootstyle="danger",
            justify=CENTER
        )
        error_label.pack(expand=True)
    
    def _post_init(self):
        """Realiza tareas de inicialización posteriores."""
        try:
            # Marcar como inicializado
            self.initialized = True
            
            # Log de estado final
            self.logger.info("Aplicación de cheques completamente inicializada")
            
        except Exception as e:
            self.logger.error(f"Error en post-inicialización: {e}")
    
    def refresh(self):
        """Refresca la aplicación (método requerido por la nueva arquitectura)."""
        try:
            self.logger.info("Refrescando aplicación de cheques")
            # En una implementación completa, aquí se recargarían los datos
            
        except Exception as e:
            self.logger.error(f"Error refrescando aplicación: {e}")
    
    def get_state(self):
        """Obtiene el estado actual de la aplicación."""
        return {
            'initialized': self.initialized,
            'module': 'cheques',
            'status': 'ready'
        }
    
    def on_search_cheques(self):
        """Manejador del botón de búsqueda."""
        try:
            # Obtener valores de los filtros
            fecha_inicial = self.initial_date.entry.get()
            fecha_final = self.final_date.entry.get()
            clase = self.class_entry.get().strip()
            solo_no_cargados = self.only_uncharged_var.get()
            
            self.logger.info("Búsqueda iniciada")
            
            # Buscar en base de datos
            filters = {
                'fecha_inicial': fecha_inicial if fecha_inicial else None,
                'fecha_final': fecha_final if fecha_final else None,
                'clase': clase if clase else None,
                'solo_no_cargados': solo_no_cargados
            }
            cheques = self.cheque_db.search_cheques(filters)
            
            # Limpiar tabla
            for item in self.cheque_table.get_children():
                self.cheque_table.delete(item)
            
            # Llenar tabla con resultados
            for cheque in cheques:
                self.cheque_table.insert("", "end", values=(
                    cheque.get("id", ""),
                    self._format_date(cheque.get("fecha", "")),
                    cheque.get("vale", ""),
                    cheque.get("folio", ""),
                    cheque.get("proveedor", ""),
                    cheque.get("monto", ""),
                    cheque.get("banco", "")
                ))
            
            self.logger.info(f"Se encontraron {len(cheques)} cheques")
                
        except Exception as e:
            self.logger.error(f"Error en búsqueda: {e}")
            # En caso de error, mostrar datos de ejemplo

    def on_search_layout(self):
        """Manejador del botón de búsqueda en layout."""
        try:
            # Obtener valores de los filtros del search_frame
            fecha_inicial = self.initial_date.entry.get()
            fecha_final = self.final_date.entry.get()
            clase = self.class_entry.get().strip()
            solo_no_cargados = self.only_uncharged_var.get()

            self.logger.info("Búsqueda en layout iniciada")

            # Construir filtros
            filters = {
                'fecha_inicial': fecha_inicial if fecha_inicial else None,
                'fecha_final': fecha_final if fecha_final else None,
                'clase': clase if clase else None,
                'solo_no_cargados': solo_no_cargados
            }

            # Buscar layouts en base de datos
            layouts = self.cheque_db.search_layouts(filters)

            # Limpiar tabla
            for item in self.layout_table.get_children():
                self.layout_table.delete(item)

            # Llenar tabla con resultados
            for layout in layouts:
                self.layout_table.insert("", "end", values=(
                    layout.get("id", ""),
                    self._format_date(layout.get("fecha", "")),
                    layout.get("nombre", ""),
                    f"${float(layout.get('monto', 0)):,.2f}"
                ))

            self.logger.info(f"Layout table actualizada con {len(layouts)} layouts encontrados")

        except Exception as e:
            self.logger.error(f"Error en búsqueda en layout: {e}")

    def on_clean_filters(self):
        """Manejador del botón de limpiar filtros."""
        try:
            # Limpiar campos de búsqueda
            self.initial_date.set('')
            self.final_date.set('')
            self.class_entry.delete(0, 'end')
            self.only_uncharged_var.set(False)
            self.logger.info("Filtros limpiados")
            
        except Exception as e:
            self.logger.error(f"Error limpiando filtros: {e}")

    def on_agregar(self):
        """Manejador del botón de agregar cheque."""
        try:
            # Obtener los itmes seleccionados en la tabla de cheques
            selected_items = self.cheque_table.selection()
            if not selected_items:
                messagebox.showwarning("Agregar Cheque", "Por favor, seleccione al menos un cheque para agregar.")
                return
            
            # Para cada item seleccionado, obtener valores y agregarlos a tabla de cargados
            for item in selected_items:
                values = self.cheque_table.item(item, "values")
                # Evitar duplicados en cargar_table
                exists = False
                for cargar_item in self.cargar_table.get_children():
                    if self.cargar_table.item(cargar_item, "values") == values:
                        exists = True
                        break
                if not exists:
                    self.cargar_table.insert("", "end", values=values)

                # Eliminar el item de la tabla de cheques
                self.cheque_table.delete(item)

            self.logger.info(f"Agregados {len(selected_items)} cheques a la tabla de cargados")

        except Exception as e:
            self.logger.error(f"Error al agregar cheque: {e}")

    def on_quitar(self):
        """Manejador del botón de quitar cheque."""
        try:
            # Obtener los items seleccionados en cargar_table
            selected_items = self.cargar_table.selection()
            if not selected_items:
                messagebox.showwarning("Quitar Cheque", "Por favor, seleccione al menos un cheque para quitar.")
                return

            for item in selected_items:
                values = self.cargar_table.item(item, "values")
                # Eliminar el item de cargar_table
                self.cargar_table.delete(item)
                # Verificar que no exista ya en cheque_table antes de insertarlo
                exists = False
                for cheque_item in self.cheque_table.get_children():
                    if self.cheque_table.item(cheque_item, "values") == values:
                        exists = True
                        break
                if not exists:
                    self.cheque_table.insert("", "end", values=values)

            self.logger.info(f"Quitados {len(selected_items)} cheques de la tabla de cargados y regresados a la tabla de cheques")

        except Exception as e:
            self.logger.error(f"Error al quitar cheque: {e}")

    def on_crear_layout(self):
        """Manejador del botón de crear layout (sin exportar automáticamente)."""
        try:
            # Verificar que hay elementos en cargar_table
            items_to_export = self.cargar_table.get_children()
            if not items_to_export:
                messagebox.showwarning("Crear Layout", "No hay cheques para crear layout en la tabla de cargados.")
                return

            # Pedir al usuario un nombre para el layout
            layout_name = simpledialog.askstring(
                "Nombre del Layout",
                "Ingrese un nombre para el nuevo layout:",
                initialvalue=f"Layout {date.today().strftime('%Y-%m-%d')}"
            )
            
            if not layout_name or not layout_name.strip():
                messagebox.showwarning("Crear Layout", "Debe proporcionar un nombre válido para el layout.")
                return
            
            layout_name = layout_name.strip()
            
            # Obtener fecha de hoy en formato string
            fecha_hoy = date.today().strftime('%Y-%m-%d')
            
            # Crear el nuevo layout en la base de datos
            self.logger.info(f"Creando layout: {layout_name}")
            layout_id = self.cheque_db.create_layout(
                nombre=layout_name,
                fecha=fecha_hoy,
                monto=0.0
            )
            
            if not layout_id:
                messagebox.showerror("Error", "No se pudo crear el layout en la base de datos.")
                return
            
            # Obtener los IDs de los cheques en cargar_table
            cheque_ids = []
            monto_total = 0.0
            
            for item in items_to_export:
                values = self.cargar_table.item(item, "values")
                # Suponiendo que el ID está en la primera columna (índice 0)
                try:
                    cheque_id = int(values[0])  # ID del cheque
                    cheque_ids.append(cheque_id)
                    
                    # Sumar al monto total (monto está en índice 5)
                    try:
                        monto_str = str(values[5]).replace('$', '').replace(',', '')
                        monto = float(monto_str)
                        monto_total += monto
                    except (ValueError, IndexError):
                        self.logger.warning(f"No se pudo parsear el monto del cheque {cheque_id}")
                        
                except (ValueError, IndexError):
                    self.logger.warning(f"No se pudo obtener el ID del cheque en item: {values}")
                    continue
            
            if not cheque_ids:
                messagebox.showerror("Error", "No se pudieron obtener los IDs de los cheques.")
                return
            
            # Asignar los cheques al layout
            self.logger.info(f"Asignando {len(cheque_ids)} cheques al layout {layout_id}")
            success = self.cheque_db.assign_cheques_to_layout(layout_id, cheque_ids)
            
            if not success:
                messagebox.showerror("Error", "No se pudieron asignar los cheques al layout.")
                return
            
            # Borrar todos los items de cargar_table
            for item in items_to_export:
                self.cargar_table.delete(item)
            
            self.logger.info("Items eliminados de cargar_table")
            
            # Actualizar layout_table con los layouts de hoy
            self._refresh_layout_table()
            
            # Mostrar mensaje de éxito (SIN generar Excel automáticamente)
            messagebox.showinfo(
                "Éxito", 
                f"Layout '{layout_name}' creado exitosamente con {len(cheque_ids)} cheques.\n"
                f"Monto total: ${monto_total:,.2f}\n\n"
                f"Use el botón 'Exportar' para generar el archivo Excel."
            )
            
            self.logger.info(f"Layout '{layout_name}' creado exitosamente con {len(cheque_ids)} cheques")

        except Exception as e:
            self.logger.error(f"Error al crear layout: {e}")
            messagebox.showerror("Error", f"Error inesperado al crear layout: {str(e)}")

    def on_exportar(self):
        """Manejador del botón de exportar cheques."""
        try:
            # Verificar que hay elementos en cargar_table
            items_to_export = self.cargar_table.get_children()
            if not items_to_export:
                messagebox.showwarning("Exportar Layout", "No hay cheques para exportar en la tabla de cargados.")
                return

            # Pedir al usuario un nombre para el layout
            layout_name = simpledialog.askstring(
                "Nombre del Layout",
                "Ingrese un nombre para el nuevo layout:",
                initialvalue=f"Layout {date.today().strftime('%Y-%m-%d')}"
            )
            
            if not layout_name or not layout_name.strip():
                messagebox.showwarning("Exportar Layout", "Debe proporcionar un nombre válido para el layout.")
                return
            
            layout_name = layout_name.strip()
            
            # Obtener fecha de hoy en formato string
            fecha_hoy = date.today().strftime('%Y-%m-%d')
            
            # Crear el nuevo layout en la base de datos
            self.logger.info(f"Creando layout: {layout_name}")
            layout_id = self.cheque_db.create_layout(
                nombre=layout_name,
                fecha=fecha_hoy,
                monto=0.0
            )
            
            if not layout_id:
                messagebox.showerror("Error", "No se pudo crear el layout en la base de datos.")
                return
            
            # Obtener los IDs de los cheques en cargar_table
            cheque_ids = []
            monto_total = 0.0
            
            for item in items_to_export:
                values = self.cargar_table.item(item, "values")
                # Suponiendo que el ID está en la primera columna (índice 0)
                try:
                    cheque_id = int(values[0])  # ID del cheque
                    cheque_ids.append(cheque_id)
                    
                    # Sumar al monto total (monto está en índice 5)
                    try:
                        monto_str = str(values[5]).replace('$', '').replace(',', '')
                        monto = float(monto_str)
                        monto_total += monto
                    except (ValueError, IndexError):
                        self.logger.warning(f"No se pudo parsear el monto del cheque {cheque_id}")
                        
                except (ValueError, IndexError):
                    self.logger.warning(f"No se pudo obtener el ID del cheque en item: {values}")
                    continue
            
            if not cheque_ids:
                messagebox.showerror("Error", "No se pudieron obtener los IDs de los cheques.")
                return
            
            # Asignar los cheques al layout
            self.logger.info(f"Asignando {len(cheque_ids)} cheques al layout {layout_id}")
            success = self.cheque_db.assign_cheques_to_layout(layout_id, cheque_ids)
            
            if not success:
                messagebox.showerror("Error", "No se pudieron asignar los cheques al layout.")
                return
            
            # Borrar todos los items de cargar_table
            for item in items_to_export:
                self.cargar_table.delete(item)
            
            self.logger.info("Items eliminados de cargar_table")
            
            # Actualizar layout_table con los layouts de hoy
            self._refresh_layout_table()
            
            # Mostrar mensaje de éxito
            messagebox.showinfo(
                "Éxito", 
                f"Layout '{layout_name}' creado exitosamente con {len(cheque_ids)} cheques.\n"
                f"Monto total: ${monto_total:,.2f}"
            )
            
            self.logger.info(f"Layout '{layout_name}' exportado exitosamente con {len(cheque_ids)} cheques")

            # Generar Excel y abrir archivo
            ruta_archivo = self.layout_a_excel(layout_id)
            if ruta_archivo:
                try:
                    import os
                    import subprocess
                    import platform
                    
                    # Abrir el archivo según el sistema operativo
                    if platform.system() == "Windows":
                        os.startfile(ruta_archivo)
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.call(["open", ruta_archivo])
                    else:  # Linux
                        subprocess.call(["xdg-open", ruta_archivo])
                    
                    self.logger.info(f"Archivo Excel abierto automáticamente: {ruta_archivo}")
                except Exception as e:
                    self.logger.warning(f"No se pudo abrir el archivo automáticamente: {e}")

        except Exception as e:
            self.logger.error(f"Error al exportar cheques: {e}")
            messagebox.showerror("Error", f"Error inesperado al exportar layout: {str(e)}")

    def layout_a_excel(self, layout_id):
        layout_obj = self.cheque_db.get_layout_by_id(layout_id)
        if layout_obj:
            exportador = LayoutExporter(layout_obj)
            ruta_archivo = exportador.exportar_layout_excel()
            return ruta_archivo
        return None

    def _refresh_layout_table(self):
        """Actualiza la tabla de layouts con los layouts de hoy"""
        try:
            # Limpiar la tabla actual
            for item in self.layout_table.get_children():
                self.layout_table.delete(item)
            
            # Obtener la fecha de hoy
            fecha_hoy = date.today().strftime('%Y-%m-%d')
            
            # Buscar layouts de hoy
            filters = {
                'fecha_inicial': fecha_hoy,
                'fecha_final': fecha_hoy
            }
            
            layouts = self.cheque_db.search_layouts(filters)
            
            # Agregar layouts a la tabla
            for layout in layouts:
                self.layout_table.insert("", "end", values=(
                    layout.get("id", ""),
                    self._format_date(layout.get("fecha", "")),
                    layout.get("nombre", ""),
                    f"${float(layout.get('monto', 0)):,.2f}"
                ))
            
            self.logger.info(f"Layout table actualizada con {len(layouts)} layouts de hoy")
            
        except Exception as e:
            self.logger.error(f"Error actualizando layout_table: {e}")
    
    def on_generar(self):
        """Manejador del botón de generar layout - Exporta layout seleccionado a Excel."""
        try:
            # Verificar que hay un layout seleccionado en layout_table
            selected_items = self.layout_table.selection()
            if not selected_items:
                messagebox.showwarning("Generar Layout", "Por favor, seleccione un layout de la tabla para exportar a Excel.")
                return
            
            # Obtener el primer item seleccionado
            selected_item = selected_items[0]
            values = self.layout_table.item(selected_item, "values")
            
            # El ID del layout está en la primera columna (índice 0)
            try:
                layout_id = int(values[0])
                layout_nombre = values[2]  # Nombre está en índice 2
            except (ValueError, IndexError):
                messagebox.showerror("Error", "No se pudo obtener el ID del layout seleccionado.")
                return
            
            self.logger.info(f"Generando Excel para layout: {layout_nombre} (ID: {layout_id})")
            
            # Usar el método layout_a_excel existente y obtener la ruta del archivo
            ruta_archivo = self.layout_a_excel(layout_id)
            
            if ruta_archivo:
                # Abrir el archivo Excel generado
                try:
                    import os
                    import subprocess
                    import platform
                    
                    # Abrir el archivo según el sistema operativo
                    if platform.system() == "Windows":
                        os.startfile(ruta_archivo)
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.call(["open", ruta_archivo])
                    else:  # Linux
                        subprocess.call(["xdg-open", ruta_archivo])
                    
                    self.logger.info(f"Archivo Excel abierto: {ruta_archivo}")
                    
                    # Mostrar mensaje de éxito
                    messagebox.showinfo(
                        "Layout Generado", 
                        f"El layout '{layout_nombre}' ha sido exportado a Excel exitosamente.\n"
                        f"El archivo se ha abierto automáticamente."
                    )
                except Exception as e:
                    self.logger.warning(f"No se pudo abrir el archivo automáticamente: {e}")
                    # Mostrar mensaje de éxito sin el auto-abrir
                    messagebox.showinfo(
                        "Layout Generado", 
                        f"El layout '{layout_nombre}' ha sido exportado a Excel exitosamente.\n"
                        f"Archivo guardado en: {ruta_archivo}"
                    )
            else:
                messagebox.showerror("Error", "No se pudo generar el archivo Excel.")
            
        except Exception as e:
            self.logger.error(f"Error al generar layout: {e}")
            messagebox.showerror("Error", f"Error inesperado al generar layout: {str(e)}")

    def on_modificar(self):
        """Manejador del botón de modificar cheque."""
        try:
            # Aquí se implementaría la lógica para modificar un cheque seleccionado
            self.logger.info("Modificar cheque (lógica no implementada)")
            # Simulación de modificar cheque
            messagebox.showinfo("Modificar Cheque", "Funcionalidad de modificar cheque aún no implementada.")

        except Exception as e:
            self.logger.error(f"Error al modificar cheque: {e}")

    def on_eliminar(self):
        """Manejador del botón de eliminar layout - Elimina layouts seleccionados."""
        try:
            # Verificar que hay layouts seleccionados en layout_table
            selected_items = self.layout_table.selection()
            if not selected_items:
                messagebox.showwarning("Eliminar Layout", "Por favor, seleccione uno o más layouts para eliminar.")
                return
            
            # Obtener información de los layouts seleccionados
            layouts_to_delete = []
            layout_names = []
            
            for selected_item in selected_items:
                values = self.layout_table.item(selected_item, "values")
                try:
                    layout_id = int(values[0])  # ID en la primera columna
                    layout_name = values[2]     # Nombre en la tercera columna
                    layouts_to_delete.append(layout_id)
                    layout_names.append(layout_name)
                except (ValueError, IndexError):
                    self.logger.warning(f"No se pudo obtener información del layout: {values}")
                    continue
            
            if not layouts_to_delete:
                messagebox.showerror("Error", "No se pudieron obtener los IDs de los layouts seleccionados.")
                return
            
            # Crear mensaje de confirmación
            if len(layouts_to_delete) == 1:
                mensaje = f"¿Está seguro que desea eliminar el layout '{layout_names[0]}'?\n\n"
                mensaje += "Esta acción:\n"
                mensaje += "• Eliminará el layout de la base de datos\n"
                mensaje += "• Desasociará todos los cheques de este layout\n"
                mensaje += "• No se puede deshacer"
            else:
                mensaje = f"¿Está seguro que desea eliminar {len(layouts_to_delete)} layouts?\n\n"
                mensaje += "Layouts a eliminar:\n"
                for name in layout_names[:5]:  # Mostrar máximo 5 nombres
                    mensaje += f"• {name}\n"
                if len(layout_names) > 5:
                    mensaje += f"• ... y {len(layout_names) - 5} más\n"
                mensaje += "\nEsta acción:\n"
                mensaje += "• Eliminará los layouts de la base de datos\n"
                mensaje += "• Desasociará todos los cheques de estos layouts\n"
                mensaje += "• No se puede deshacer"
            
            # Confirmar con el usuario
            confirm = messagebox.askyesno(
                "Confirmar Eliminación",
                mensaje,
                icon="warning"
            )
            
            if not confirm:
                self.logger.info("Eliminación de layouts cancelada por el usuario")
                return
            
            # Proceder con la eliminación
            deleted_count = 0
            errors = []
            
            for layout_id, layout_name in zip(layouts_to_delete, layout_names):
                self.logger.info(f"Eliminando layout: {layout_name} (ID: {layout_id})")
                success = self.cheque_db.delete_layout(layout_id)
                
                if success:
                    deleted_count += 1
                else:
                    errors.append(layout_name)
            
            # Refrescar la tabla de layouts
            self._refresh_layout_table()
            
            # Mostrar resultado
            if deleted_count == len(layouts_to_delete):
                if deleted_count == 1:
                    messagebox.showinfo(
                        "Eliminación Exitosa",
                        f"El layout '{layout_names[0]}' ha sido eliminado exitosamente."
                    )
                else:
                    messagebox.showinfo(
                        "Eliminación Exitosa",
                        f"Se eliminaron {deleted_count} layouts exitosamente."
                    )
            elif deleted_count > 0:
                mensaje_error = f"Se eliminaron {deleted_count} de {len(layouts_to_delete)} layouts.\n\n"
                mensaje_error += "Layouts que no se pudieron eliminar:\n"
                for error_name in errors:
                    mensaje_error += f"• {error_name}\n"
                messagebox.showwarning("Eliminación Parcial", mensaje_error)
            else:
                messagebox.showerror(
                    "Error en Eliminación",
                    "No se pudo eliminar ningún layout. Revise los logs para más detalles."
                )
                
        except Exception as e:
            self.logger.error(f"Error al eliminar layouts: {e}")
            messagebox.showerror("Error", f"Error inesperado al eliminar layouts: {str(e)}")

    def on_mostrar(self):
        """Muestra el contenido de un layout específico."""
        try:
            selected_items = self.layout_table.selection()
            if not selected_items:
                messagebox.showwarning("Sin Selección", "Por favor, seleccione un layout para mostrar su contenido.")
                return

            # Obtener el primer item seleccionado
            values = self.layout_table.item(selected_items[0], "values")
            layout_id = int(values[0])  # ID del layout está en la primera columna

            layout_content = self.cheque_db.show_layout_content(layout_id)
            if not layout_content:
                messagebox.showwarning("Sin Contenido", f"No se encontró contenido para el Layout {layout_id}")
                return
            
            # Borramos el contenido en layout
            self.layout.delete(*self.layout.get_children())

            for cheque in layout_content:
                # Extraer datos del cheque correctamente (sin comas finales)
                codigo = str(cheque.get('codigo', ''))  # Forzar como string para Excel
                nombre = cheque.get('proveedor', '')
                importe = cheque.get('monto', 0)
                descripcion_conceptos = cheque.get('descripcion', '')  # Obtener las descripciones de los vales
                vale = cheque.get('vale', '')
                folio = cheque.get('folio', '')
                
                # Crear referencia: tomar solo el primer vale (antes del espacio) sin la "V"
                if vale:
                    primer_vale = vale.split()[0]  # Obtener solo el primer vale antes del espacio
                    referencia = primer_vale[1:] if len(primer_vale) > 1 else primer_vale
                else:
                    referencia = ""
                
                # Asegurar que importe sea float
                try:
                    importe_float = float(importe) if importe else 0.0
                except (ValueError, TypeError):
                    importe_float = 0.0
                
                # Crear descripción completa: vale + folio + conceptos de los vales
                descripcion = f"{vale} "
                if folio:
                    descripcion += f"F-{folio} "
                if descripcion_conceptos:  # Si hay descripciones de vales, agregarlas
                    descripcion += f"{descripcion_conceptos}"
                
                # Insertar en el treeview con los valores correctos en el orden de las columnas
                # Columnas: "alias", "nombre", "importe", "descripcion", "referencia"
                self.layout.insert("", "end", values=(
                    codigo,           # Alias
                    nombre,           # Nombre (Proveedor)
                    importe_float,    # Importe como float
                    descripcion,      # Descripción completa con conceptos
                    referencia        # Referencia
                ))

        except Exception as e:
            self.logger.error(f"Error al mostrar contenido de layout {layout_id}: {e}")

    def copy_layout(self, column):
        """Copia todas las filas de una columna específica al portapapeles."""
        try:
            # Mapear nombres de parámetros a índices de columnas
            column_mapping = {
                "alias": 0,      # Columna "alias" 
                "nombre": 1,     # Columna "nombre"
                "importe": 2,    # Columna "importe"
                "descripcion": 3, # Columna "descripcion"
                "referencia": 4  # Columna "referencia"
            }
            
            # Verificar que la columna solicitada existe
            if column not in column_mapping:
                messagebox.showerror("Error", f"Columna '{column}' no válida. Columnas disponibles: {list(column_mapping.keys())}")
                return
            
            # Obtener el índice de la columna
            column_index = column_mapping[column]
            
            # Obtener todos los elementos de la tabla layout
            items = self.layout.get_children()
            
            if not items:
                messagebox.showwarning("Sin Datos", "No hay datos en la tabla de layout para copiar.")
                return
            
            # Extraer valores de la columna especificada
            column_values = []
            for item in items:
                values = self.layout.item(item, "values")
                if len(values) > column_index:
                    value = str(values[column_index])
                    column_values.append(value)
            
            if not column_values:
                messagebox.showwarning("Sin Datos", f"No se encontraron datos en la columna '{column}'.")
                return
            
            # Unir todos los valores con saltos de línea
            clipboard_text = "\n".join(column_values)
            
            # Copiar al portapapeles usando la ventana actual
            self.master.clipboard_clear()
            self.master.clipboard_append(clipboard_text)
            self.master.update()  # Asegurar que se copie
            
            self.logger.info(f"Copiados {len(column_values)} valores de la columna '{column}' al portapapeles")
            
        except Exception as e:
            self.logger.error(f"Error al copiar columna '{column}' al portapapeles: {e}")
            messagebox.showerror("Error", f"Error al copiar al portapapeles: {str(e)}")

    def on_desenlazar(self):
        """Manejador del botón de desenlazar factura."""
        try:
            # Aquí se implementaría la lógica para desenlazar una factura seleccionada
            self.logger.info("Desenlazar factura (lógica no implementada)")
            # Simulación de desenlazar factura
            messagebox.showinfo("Desenlazar Factura", "Funcionalidad de desenlazar factura aún no implementada.")

        except Exception as e:
            self.logger.error(f"Error al desenlazar factura: {e}")


# Función de conveniencia para ejecutar independientemente
def main():
    """Ejecuta la aplicación de forma independiente para pruebas."""
    try:
        # Crear ventana principal
        root = tb.Window(themename="cosmo")
        root.title("Aplicación de Cheques - Profesional")
        
        # Configurar geometría
        if UI_HELPERS_AVAILABLE:
            safe_set_geometry(root, WINDOW_SIZES.get('cheque_app', '1300x700'))
        else:
            root.geometry("1300x700")
        
        # Crear y mostrar aplicación
        app = ChequeAppProfessional(root)
        
        # Centrar ventana si las utilidades están disponibles
        if UI_HELPERS_AVAILABLE:
            center_window_on_parent(root, None)
        
        # Iniciar loop principal
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Error ejecutando aplicación independiente: {e}")
        raise


if __name__ == "__main__":
    main()
