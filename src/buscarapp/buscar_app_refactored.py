"""
Aplicación principal refactorizada de búsqueda de facturas usando arquitectura MVC
"""
import sys
import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import logging
from typing import Optional, Dict, Any, List
from tkinter import filedialog

# Agregar paths necesarios
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

# Importar la clase Cheque
try:
    from ctr_cheque import Cheque
except ImportError:
    print("Advertencia: No se pudo importar la clase Cheque")
    Cheque = None

# Intentar imports relativos primero, luego absolutos
try:
    # Imports relativos (cuando se ejecuta como módulo)
    from .controllers import SearchController, InvoiceController, ExportController
    from .controllers.autocarga_controller import AutocargaController
    from .views.search_frame import SearchFrame
    from .views.table_frame import TableFrame
    from .views.action_buttons_frame import ActionButtonsFrame
    from .views.info_panels_frame import InfoPanelsFrame
    from .models.search_models import SearchFilters
    from .utils.dialog_utils import DialogUtils
    from .autocarga.autocarga import AutoCarga
except ImportError:
    # Imports absolutos (cuando se ejecuta directamente)
    from controllers import SearchController, InvoiceController, ExportController
    from controllers.autocarga_controller import AutocargaController
    from views.search_frame import SearchFrame
    from views.table_frame import TableFrame
    from views.action_buttons_frame import ActionButtonsFrame
    from views.info_panels_frame import InfoPanelsFrame
    from models.search_models import SearchFilters
    from utils.dialog_utils import DialogUtils
    from autocarga.autocarga import AutoCarga

# Importar configuración de tipos de vale
try:
    from solicitudapp.config.app_config import AppConfig
    CONFIG_AVAILABLE = True
except ImportError:
    AppConfig = None
    CONFIG_AVAILABLE = False

# Intentar importar base de datos
try:
    from bd.bd_control import DBManager
    from bd.models import Factura, Proveedor, Concepto, Vale, Reparto
    BD_AVAILABLE = True
except ImportError as e:
    print(f"Advertencia: No se pudo importar base de datos: {e}")
    BD_AVAILABLE = False
    DBManager = None
    Factura = Proveedor = Concepto = Vale = Reparto = None


class BuscarAppRefactored(ttk.Frame):
    """
    Aplicación principal de búsqueda de facturas refactorizada con arquitectura MVC
    """
    
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
        
        # Inicializar utilidades
        self.dialog_utils = DialogUtils(self)
        
        # Inicializar base de datos
        self.bd_control = None
        self._initialize_database()
        
        # Inicializar controladores
        self.search_controller = SearchController(self.bd_control)
        self.invoice_controller = InvoiceController(self.bd_control)
        self.export_controller = ExportController()
        self.autocarga_controller = AutocargaController(self.bd_control, self)
        
        # Variables de estado
        self.current_selection = None
        
        # Crear interfaz
        self._create_layout()
        
        # Cargar datos iniciales
        self._load_initial_data()
    
    def _initialize_database(self):
        """Inicializa la conexión a la base de datos"""
        try:
            if BD_AVAILABLE:
                self.bd_control = DBManager()
                self.logger.info("Conexión a base de datos establecida")
            else:
                self.bd_control = None
                self.logger.warning("Base de datos no disponible - usando datos de ejemplo")
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
            self.bd_control = None
    
    def _create_layout(self):
        """Crea el layout principal de la aplicación"""
        
        # Frame principal con padding
        main_container = ttk.Frame(self, padding=10)
        main_container.pack(fill="both", expand=True)
        
        # Frame de búsqueda
        self.search_frame = SearchFrame(
            main_container,
            on_search_callback=self._on_search,
            on_clear_callback=self._on_clear_search
        )
        
        # Frame de tabla
        self.table_frame = TableFrame(
            main_container,
            on_selection_callback=self._on_table_selection,
            on_double_click_callback=self._on_table_double_click
        )
        
        # Frame de botones de acción
        self.action_buttons_frame = ActionButtonsFrame(
            main_container,
            on_autocarga_callback=self._on_autocarga,
            on_reimprimir_callback=self._on_reimprimir,
            on_toggle_cargada_callback=self._on_toggle_cargada,
            on_export_callback=self._on_export,
            on_detalles_callback=self._on_detalles,
            on_modificar_callback=self._on_modificar,
            on_cheque_callback=self._on_cheque
        )
        
        # Frame de paneles de información
        self.info_panels_frame = InfoPanelsFrame(main_container)
        
        # Frame de estado de BD en la parte inferior
        self.status_bar_frame = ttk.Frame(self)
        self.status_bar_frame.pack(side="bottom", fill="x", padx=5, pady=(0, 5))
        
        # Label de estado de BD en la esquina inferior derecha
        self.db_status_label = ttk.Label(
            self.status_bar_frame,
            text="",
            font=("Segoe UI", 9),
            bootstyle="success"
        )
        self.db_status_label.pack(side="right", padx=(0, 10))
        
        # Mensaje de estado inicial
        if not self.bd_control:
            self.dialog_utils.show_warning(
                "Base de datos no disponible",
                "La base de datos no está disponible. "
                "Se mostrarán datos de ejemplo para demostración."
            )
    
    def _load_initial_data(self):
        """Carga los datos iniciales"""
        try:
            # Cargar facturas
            success = self.search_controller.load_facturas()
            if success:
                self.logger.info("Datos de facturas cargados correctamente")
            else:
                self.logger.warning("No se pudieron cargar las facturas")
            
            # Cargar proveedores
            self.search_controller.load_proveedores()
            
            # Pasar datos de proveedores al SearchFrame
            if hasattr(self.search_controller.get_state(), 'proveedores_data'):
                proveedores_data = self.search_controller.get_state().proveedores_data
                if hasattr(self.search_frame, 'set_proveedores_data'):
                    self.search_frame.set_proveedores_data(proveedores_data)
                    self.logger.info(f"Datos de proveedores pasados al SearchFrame: {len(proveedores_data)} proveedores")
            
            # Cargar y pasar datos de tipos de vale desde la configuración
            if CONFIG_AVAILABLE and hasattr(AppConfig, 'TIPO_VALE'):
                tipos_data = []
                for clave, descripcion in AppConfig.TIPO_VALE.items():
                    tipos_data.append({
                        'clave': clave,
                        'descripcion': descripcion,
                        'display': f"{clave} - {descripcion}"
                    })
                self.logger.info(f"Tipos de vale cargados desde configuración: {len(tipos_data)} tipos")
                
                if hasattr(self.search_frame, 'set_tipos_data'):
                    self.search_frame.set_tipos_data(tipos_data)
                    self.logger.info(f"Datos de tipos pasados al SearchFrame: {len(tipos_data)} tipos")
            else:
                # No cargar datos falsos si no está disponible la configuración
                self.logger.error("Configuración de tipos de vale no disponible - botones de búsqueda de tipo deshabilitados")
                if hasattr(self.search_frame, 'set_tipos_data'):
                    self.search_frame.set_tipos_data([])  # Lista vacía
            
            # Actualizar estado inicial
            self._update_status_message()
            
        except Exception as e:
            self.logger.error(f"Error cargando datos iniciales: {e}")
            self.dialog_utils.show_error("Error cargando datos", f"Error cargando datos: {str(e)}")
    
    def _on_search(self, filters_dict: Dict[str, Any]):
        """Maneja el evento de búsqueda"""
        try:
            # Convertir diccionario a objeto SearchFilters
            search_filters = SearchFilters(
                fecha_inicial=filters_dict.get('fecha_inicial', ''),
                fecha_final=filters_dict.get('fecha_final', ''),
                tipo_filtro=filters_dict.get('tipo_filtro', ''),
                proveedor_filtro=filters_dict.get('proveedor_filtro', ''),
                no_vale_filtro=filters_dict.get('no_vale_filtro', ''),
                clase_filtro=filters_dict.get('clase_filtro', ''),
                solo_cargado=filters_dict.get('solo_cargado', False),
                solo_pagado=filters_dict.get('solo_pagado', False),
                texto_busqueda=filters_dict.get('texto_busqueda', '')
            )
            
            # Deshabilitar controles durante búsqueda
            self.search_frame.enable_controls(False)
            
            # Aplicar filtros
            filtered_results = self.search_controller.apply_filters(search_filters)
            
            # Actualizar tabla
            self.table_frame.load_data(filtered_results)
            
            # Actualizar estadísticas
            search_state = self.search_controller.get_state()
            self.info_panels_frame.update_estadisticas(
                search_state.all_facturas,
                search_state.filtered_facturas
            )
            
            # Limpiar información de detalles
            self.info_panels_frame.clear_all_info()
            self.action_buttons_frame.update_selection(None)
            
            result_count = len(filtered_results)
            self.logger.info(f"Búsqueda completada - {result_count} resultados")
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda: {e}")
            self.dialog_utils.show_error("Error en búsqueda", f"Error en la búsqueda: {str(e)}")
        finally:
            self.search_frame.enable_controls(True)
    
    def _on_clear_search(self):
        """Maneja el evento de limpiar búsqueda"""
        try:
            # Limpiar controlador de búsqueda
            self.search_controller.clear_filters()
            
            # Limpiar tabla
            self.table_frame.clear_table()
            
            # Limpiar paneles de información
            self.info_panels_frame.clear_all_info()
            
            # Actualizar botones de acción
            self.action_buttons_frame.update_selection(None)
            
            self.logger.info("Búsqueda y filtros limpiados")
            
        except Exception as e:
            self.logger.error(f"Error limpiando búsqueda: {e}")
    
    def _on_table_selection(self, selected_data: Optional[Dict[str, Any]]):
        """Maneja el evento de selección en la tabla"""
        try:
            self.current_selection = selected_data
            
            # Actualizar botones de acción
            self.action_buttons_frame.update_selection(selected_data)
            
            if selected_data:
                # Obtener detalles completos si hay base de datos
                if self.bd_control:
                    folio_interno = selected_data.get('folio_interno')
                    if folio_interno:
                        details = self.invoice_controller.get_invoice_details(folio_interno)
                        if details:
                            self._update_detail_panels(details)
                        else:
                            self.info_panels_frame.clear_all_info()
                else:
                    # Solo mostrar información básica para datos de ejemplo
                    self.info_panels_frame.update_factura_info(selected_data)
            else:
                self.info_panels_frame.clear_all_info()
                
        except Exception as e:
            self.logger.error(f"Error en selección de tabla: {e}")
    
    def _on_table_double_click(self, selected_data: Dict[str, Any]):
        """Maneja el evento de doble click en la tabla"""
        try:
            if not selected_data:
                return
            
            if not self.bd_control:
                self.dialog_utils.show_info(
                    "La vista de detalles completos solo está disponible con datos reales de la base de datos."
                )
                return
            
            # Mostrar ventana de detalles
            self._show_details_window(selected_data)
            
        except Exception as e:
            self.logger.error(f"Error en doble click: {e}")
    
    def _update_detail_panels(self, details: Dict[str, Any]):
        """Actualiza los paneles de información con detalles completos"""
        try:
            # Actualizar información de factura
            if 'factura' in details:
                self.info_panels_frame.update_factura_info(details['factura'])
            
            # Actualizar información de proveedor
            if 'proveedor' in details:
                self.info_panels_frame.update_proveedor_info(details['proveedor'])
            
            # Actualizar conceptos
            if 'conceptos' in details:
                self.info_panels_frame.update_conceptos_info(details['conceptos'])
            
            # Actualizar vale
            if 'vale' in details and details['vale'] is not None:
                self.info_panels_frame.update_vale_info(details['vale'])
            
            # Actualizar orden de compra
            if 'orden_compra' in details and details['orden_compra'] is not None:
                orden_data = {
                    'importe': float(details['orden_compra'].importe) if details['orden_compra'].importe else 0.0,
                    'iva': float(details['orden_compra'].iva) if details['orden_compra'].iva else 0.0,
                    'importe_letras': details['orden_compra'].importe_en_letras or '-',
                    'cuenta_mayor': details['orden_compra'].cuenta_mayor or '-',
                    'banco_codigo': details['orden_compra'].codigo_banco or '-'
                }
                self.info_panels_frame.update_orden_compra_info(orden_data)
            
        except Exception as e:
            self.logger.error(f"Error actualizando paneles de detalle: {e}")
    
    def _show_details_window(self, selected_data: Dict[str, Any]):
        """Muestra una ventana con los detalles completos de la factura"""
        try:
            folio_interno = selected_data.get('folio_interno')
            if not folio_interno:
                return
            
            details = self.invoice_controller.get_invoice_details(folio_interno)
            if not details:
                self.dialog_utils.show_warning("No se pudieron obtener los detalles de la factura")
                return
            
            # Crear ventana de detalles
            details_window = ttk.Toplevel(self)
            details_window.title(f"Detalles - Factura {folio_interno}")
            details_window.geometry("600x500")
            details_window.transient(self)
            details_window.grab_set()
            
            # Frame principal con padding
            main_frame = ttk.Frame(details_window, padding=20)
            main_frame.pack(fill="both", expand=True)
            
            # Título
            factura_info = details.get('factura', {})
            serie = factura_info.get('serie', '')
            folio = factura_info.get('folio', '')
            titulo = f"Factura {serie} {folio}".strip() if serie or folio else f"Factura {folio_interno}"
            
            title_label = ttk.Label(
                main_frame,
                text=titulo,
                font=("Segoe UI", 16, "bold"),
                bootstyle="inverse-primary"
            )
            title_label.pack(pady=(0, 20))
            
            # Crear notebook para organizar la información
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill="both", expand=True)
            
            # Tab de información básica
            basic_frame = ttk.Frame(notebook)
            notebook.add(basic_frame, text="Información Básica")
            
            # Mostrar información básica
            basic_info = [
                ("Folio Interno:", factura_info.get('folio_interno', 'N/A')),
                ("Tipo:", factura_info.get('tipo', 'N/A')),
                ("Fecha:", self._format_date(factura_info.get('fecha', 'N/A'))),
                ("Emisor:", factura_info.get('nombre_emisor', 'N/A')),
                ("RFC Emisor:", factura_info.get('rfc_emisor', 'N/A')),
                ("Subtotal:", f"${factura_info.get('subtotal', 0):,.2f}"),
                ("IVA:", f"${factura_info.get('iva_trasladado', 0):,.2f}"),
                ("Total:", f"${factura_info.get('total', 0):,.2f}"),
                ("Cargada:", "✓ Sí" if factura_info.get('cargada') else "✗ No"),
                ("Pagada:", "✓ Sí" if factura_info.get('pagada') else "✗ No")
            ]
            
            for i, (label_text, value) in enumerate(basic_info):
                row_frame = ttk.Frame(basic_frame)
                row_frame.pack(fill="x", padx=10, pady=5)
                
                ttk.Label(
                    row_frame,
                    text=label_text,
                    font=("Segoe UI", 10, "bold"),
                    width=15,
                    anchor="w"
                ).pack(side="left")
                
                ttk.Label(
                    row_frame,
                    text=str(value),
                    font=("Segoe UI", 10),
                    anchor="w"
                ).pack(side="left", fill="x", expand=True)
            
            # Tab de conceptos si existen
            conceptos = details.get('conceptos', [])
            if conceptos:
                conceptos_frame = ttk.Frame(notebook)
                notebook.add(conceptos_frame, text=f"Conceptos ({len(conceptos)})")
                
                # Crear lista de conceptos
                conceptos_text = ttk.Text(conceptos_frame, wrap="word", height=10)
                scrollbar = ttk.Scrollbar(conceptos_frame, orient="vertical", command=conceptos_text.yview)
                conceptos_text.configure(yscrollcommand=scrollbar.set)
                
                for i, concepto in enumerate(conceptos, 1):
                    concepto_info = (
                        f"{i}. {concepto.get('descripcion', 'Sin descripción')}\n"
                        f"   Cantidad: {concepto.get('cantidad', 0):.2f} {concepto.get('unidad', '')}\n"
                        f"   Precio: ${concepto.get('valor_unitario', 0):,.2f}\n"
                        f"   Importe: ${concepto.get('importe', 0):,.2f}\n\n"
                    )
                    conceptos_text.insert("end", concepto_info)
                
                conceptos_text.config(state="disabled")
                conceptos_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
                scrollbar.pack(side="right", fill="y", pady=5)
            
            # Botón cerrar
            ttk.Button(
                main_frame,
                text="Cerrar",
                bootstyle="secondary",
                command=details_window.destroy
            ).pack(pady=(20, 0))
            
        except Exception as e:
            self.logger.error(f"Error mostrando ventana de detalles: {e}")
            self.dialog_utils.show_error(f"Error mostrando detalles: {str(e)}")
    
    def _on_detalles(self, selected_data: Dict[str, Any]):
        """Maneja el evento de ver detalles"""
        try:
            if not selected_data:
                return
            
            # Usar el mismo método que el doble click
            self._on_table_double_click(selected_data)
            
        except Exception as e:
            self.logger.error(f"Error en detalles: {e}")
    
    def _on_modificar(self, selected_data: Dict[str, Any]):
        """Maneja el evento de modificar"""
        try:
            if not selected_data:
                return
            
            self.dialog_utils.show_info(
                "Funcionalidad de Modificar",
                "Esta funcionalidad estará disponible en una próxima actualización."
            )
            
        except Exception as e:
            self.logger.error(f"Error en modificar: {e}")
    
    def _on_autocarga(self):
        """Maneja el evento de autocarga"""
        try:
            if not self.bd_control:
                self.dialog_utils.show_warning(
                    "Base de datos no disponible",
                    "La funcionalidad de autocarga requiere conexión a la base de datos."
                )
                return
            
            # Obtener facturas seleccionadas del tree
            facturas_seleccionadas = self.table_frame.get_selected_data_multiple()
            
            if not facturas_seleccionadas:
                self.dialog_utils.show_warning(
                    "Sin Selección",
                    "Debe seleccionar al menos una factura en la tabla para asociar los vales.\n\n"
                    "Use Ctrl+Click para seleccionar múltiples facturas."
                )
                return
            
            # Ejecutar autocarga con facturas seleccionadas
            self.logger.info(f"Iniciando proceso de autocarga con {len(facturas_seleccionadas)} facturas seleccionadas")
            success, stats = self.autocarga_controller.ejecutar_autocarga_con_configuracion(facturas_seleccionadas)
            
            if success:
                self.logger.info("Autocarga completada exitosamente")
                
                # Refrescar datos en la aplicación
                self._refresh_after_autocarga(stats)
            else:
                self.logger.warning("Autocarga cancelada o falló")
                
        except Exception as e:
            self.logger.error(f"Error en autocarga: {e}")
            self.dialog_utils.show_error("Error en Autocarga", f"Error durante la autocarga: {str(e)}")
    
    def _refresh_after_autocarga(self, stats: Optional[Dict] = None):
        """Refresca los datos de la aplicación después de la autocarga"""
        try:
            # Recargar facturas
            self.search_controller.load_facturas()
            
            # Recargar proveedores
            self.search_controller.load_proveedores()
            
            # Pasar datos actualizados al SearchFrame
            if hasattr(self.search_controller.get_state(), 'proveedores_data'):
                proveedores_data = self.search_controller.get_state().proveedores_data
                if hasattr(self.search_frame, 'set_proveedores_data'):
                    self.search_frame.set_proveedores_data(proveedores_data)
            
            # Recargar tipos de vale desde configuración
            if CONFIG_AVAILABLE and hasattr(AppConfig, 'TIPO_VALE'):
                tipos_data = []
                for clave, descripcion in AppConfig.TIPO_VALE.items():
                    tipos_data.append({
                        'clave': clave,
                        'descripcion': descripcion,
                        'display': f"{clave} - {descripcion}"
                    })
                
                if hasattr(self.search_frame, 'set_tipos_data'):
                    self.search_frame.set_tipos_data(tipos_data)
            else:
                # No cargar datos falsos
                if hasattr(self.search_frame, 'set_tipos_data'):
                    self.search_frame.set_tipos_data([])
            
            # Limpiar búsqueda actual para mostrar datos actualizados
            self._on_clear_search()
            
            # Si hay estadísticas de autocarga, mostrar el último vale procesado
            if stats and hasattr(self, 'info_panels'):
                self._mostrar_ultimo_vale_procesado()
                
        except Exception as e:
            self.logger.error(f"Error refrescando después de autocarga: {e}")
    
    def _mostrar_ultimo_vale_procesado(self):
        """Muestra el último vale procesado en el frame de información"""
        try:
            if not self.bd_control:
                return
            
            # Obtener el último vale insertado
            ultimo_vale = self.bd_control.obtener_ultimo_vale()
            
            if ultimo_vale:
                # Convertir datos del vale a formato para mostrar
                vale_data = {
                    'noVale': ultimo_vale.noVale,
                    'tipo': ultimo_vale.tipo,
                    'total': ultimo_vale.total,
                    'proveedor': ultimo_vale.proveedor,
                    'fechaVale': ultimo_vale.fechaVale,
                    'referencia': ultimo_vale.referencia,
                    'departamento': ultimo_vale.departamento,
                    'descripcion': ultimo_vale.descripcion
                }
                
                # Actualizar panel de información
                self.info_panels.update_vale_info(vale_data)
                
                self.logger.info(f"Mostrando información del último vale procesado: {ultimo_vale.noVale}")
            
        except Exception as e:
            self.logger.error(f"Error mostrando último vale procesado: {e}")
            
            # Actualizar estado
            self._update_status_message()
            
            self.logger.info("Datos actualizados después de autocarga")
            
        except Exception as e:
            self.logger.error(f"Error refrescando datos después de autocarga: {e}")
    
    def _on_reimprimir(self, selected_data: Dict[str, Any]):
        """Maneja el evento de reimprimir"""
        try:
            if not self.bd_control:
                self.dialog_utils.show_warning(
                    "La reimpresión solo está disponible con datos reales de la base de datos."
                )
                return
            
            # Usar el controlador de facturas para reimprimir
            success = self.invoice_controller.reimprimir_factura(selected_data)
            
            if success:
                self.logger.info(f"Factura reimpresa: {selected_data.get('folio_interno')}")
            
        except Exception as e:
            self.logger.error(f"Error en reimpresión: {e}")
    
    def _on_toggle_cargada(self, folio_interno: str):
        """Maneja el cambio de estado 'cargada'"""
        try:
            if not self.bd_control:
                self.dialog_utils.show_warning(
                    "El cambio de estado solo está disponible con datos reales de la base de datos."
                )
                return
            
            # Confirmar cambio
            if self.dialog_utils.ask_yes_no(
                "Cambiar Estado",
                f"¿Desea cambiar el estado de 'cargada' para la factura {folio_interno}?"
            ):
                success = self.invoice_controller.toggle_cargada_status(folio_interno)
                
                if success:
                    # Actualizar tabla
                    self.table_frame.update_row_status(folio_interno, cargada=None)
                    # Refrescar búsqueda para mostrar cambios
                    self._refresh_current_search()
                    self.logger.info(f"Estado 'cargada' cambiado para factura {folio_interno}")
                
        except Exception as e:
            self.logger.error(f"Error cambiando estado 'cargada': {e}")
    
    def _on_toggle_pagada(self, folio_interno: str):
        """Maneja el cambio de estado 'pagada'"""
        try:
            if not self.bd_control:
                self.dialog_utils.show_warning(
                    "El cambio de estado solo está disponible con datos reales de la base de datos."
                )
                return
            
            # Confirmar cambio
            if self.dialog_utils.ask_yes_no(
                "Cambiar Estado",
                f"¿Desea cambiar el estado de 'pagada' para la factura {folio_interno}?"
            ):
                success = self.invoice_controller.toggle_pagada_status(folio_interno)
                
                if success:
                    # Actualizar tabla
                    self.table_frame.update_row_status(folio_interno, pagada=None)
                    # Refrescar búsqueda para mostrar cambios
                    self._refresh_current_search()
                    self.logger.info(f"Estado 'pagada' cambiado para factura {folio_interno}")
                
        except Exception as e:
            self.logger.error(f"Error cambiando estado 'pagada': {e}")
    
    def _on_abrir_xml(self, xml_path: str):
        """Maneja la apertura de archivo XML"""
        success = self.invoice_controller.abrir_archivo(xml_path)
        if success:
            self.logger.info(f"Archivo XML abierto: {xml_path}")
    
    def _on_abrir_pdf(self, pdf_path: str):
        """Maneja la apertura de archivo PDF"""
        success = self.invoice_controller.abrir_archivo(pdf_path)
        if success:
            self.logger.info(f"Archivo PDF abierto: {pdf_path}")
    
    def _on_export(self):
        """Maneja el evento de exportación"""
        try:
            # Obtener datos actuales de la tabla
            current_data = self.table_frame.get_all_data()
            
            if not current_data:
                self.dialog_utils.show_warning("No hay datos para exportar")
                return
            
            # Mostrar opciones de exportación
            export_formats = self.export_controller.get_export_formats()
            
            # Por simplicidad, usar CSV como formato por defecto
            # En una implementación completa, se podría mostrar un diálogo de selección
            success = self.export_controller.export_to_csv(current_data)
            
            if success:
                self.logger.info(f"Datos exportados: {len(current_data)} registros")
            
        except Exception as e:
            self.logger.error(f"Error en exportación: {e}")
    
    def _refresh_current_search(self):
        """Refresca la búsqueda actual para mostrar cambios"""
        try:
            # Obtener filtros actuales
            current_filters = self.search_frame.get_filters()
            
            # Recargar datos
            self.search_controller.load_facturas()
            
            # Reaplicar filtros si hay alguno activo
            if any(current_filters.values()):
                self._on_search(current_filters)
            
        except Exception as e:
            self.logger.error(f"Error refrescando búsqueda: {e}")
    
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
    
    def _on_cheque(self):
        """Maneja el evento del botón Cheque - Genera cheques individuales o múltiples consolidados"""
        try:
            # Obtener elementos seleccionados en la tabla
            selected_items = self.table_frame.get_selected_data_multiple()
            
            if not selected_items:
                self.dialog_utils.show_warning("Sin Selección", "Debe seleccionar al menos un elemento en la tabla.")
                return
            
            ruta_exportacion = ""
            
            if len(selected_items) == 1:
                # Un solo elemento seleccionado
                item = selected_items[0]
                no_vale = str(item.get('no_vale', 'SinVale'))
                proveedor = self._obtener_nombre_para_archivo(item)  # Usar función que considera nombre_contacto
                folio_factura = str(item.get('folio', 'SinFolio'))  # Solo folio, no serie_folio
                clase = str(item.get('clase', 'SinClase'))
                
                # Limpiar caracteres no válidos para nombres de archivo
                no_vale = self._limpiar_nombre_archivo(no_vale)
                proveedor = self._limpiar_nombre_archivo(proveedor)
                folio_factura = self._limpiar_nombre_archivo(folio_factura)
                clase = self._limpiar_nombre_archivo(clase)
                
                # Crear nombre del archivo - solo incluir clase si no está vacía
                if clase and clase not in ['Vacio', 'SinClase', 'Item']:
                    nombre_archivo = f"{no_vale} {proveedor} {folio_factura} {clase}.pdf"
                else:
                    nombre_archivo = f"{no_vale} {proveedor} {folio_factura}.pdf"
                
                # Mostrar diálogo para guardar
                filename = filedialog.asksaveasfilename(
                    title="Guardar documento de cheque",
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                    initialfile=nombre_archivo,
                    parent=self
                )
                
                if filename:
                    ruta_exportacion = filename
                    self.logger.info(f"Ruta de exportación (1 elemento): {ruta_exportacion}")
            
            else:
                # Múltiples elementos seleccionados - verificar que sean del mismo proveedor
                primer_proveedor = str(selected_items[0].get('nombre_emisor', ''))
                
                # Verificar que todos sean del mismo proveedor
                mismo_proveedor = all(str(item.get('nombre_emisor', '')) == primer_proveedor for item in selected_items)
                
                if not mismo_proveedor:
                    self.dialog_utils.show_warning(
                        "Proveedores Diferentes", 
                        "Los elementos seleccionados deben ser del mismo proveedor para crear un cheque conjunto.\n\n"
                        "Facturas seleccionadas por proveedor:\n" +
                        "\n".join([f"• {item.get('nombre_emisor', 'Sin proveedor')}: Vale {item.get('no_vale', 'N/A')}" 
                                 for item in selected_items])
                    )
                    return
                
                # Verificar que todas las facturas tengan totales válidos
                facturas_sin_total = [item for item in selected_items if not item.get('total') or float(item.get('total', 0)) <= 0]
                if facturas_sin_total:
                    folios_problematicos = [item.get('folio', 'N/A') for item in facturas_sin_total]
                    self.dialog_utils.show_warning(
                        "Facturas sin Total", 
                        f"Las siguientes facturas no tienen un total válido y no pueden ser procesadas:\n" +
                        f"Folios: {', '.join(folios_problematicos)}\n\n"
                        "Por favor, seleccione solo facturas con importes válidos."
                    )
                    return
                
                # Crear nombre con múltiples vales
                numeros_vale = []
                folios_factura = []
                folios_ya_agregados = set()  # Para evitar duplicados de folios complementarios
                
                for item in selected_items:
                    no_vale = str(item.get('no_vale', 'SinVale'))
                    folio_factura = str(item.get('folio', 'SinFolio'))  # Solo folio, no serie_folio
                    serie_factura = str(item.get('serie', ''))  # Obtener la serie
                    
                    # Agregar el número de vale (siempre se agrega)
                    numeros_vale.append(self._limpiar_nombre_archivo(no_vale))
                    
                    # Para folios: si la serie empieza con "div-", es una factura complementaria
                    # Solo agregar el folio si no es complementaria O si el folio no ha sido agregado antes
                    es_complementaria = serie_factura.lower().startswith('div-')
                    
                    if es_complementaria:
                        # Es complementaria, verificar si el folio ya fue agregado
                        if folio_factura not in folios_ya_agregados:
                            folios_factura.append(self._limpiar_nombre_archivo(folio_factura))
                            folios_ya_agregados.add(folio_factura)
                            self.logger.info(f"Factura complementaria detectada (serie: {serie_factura}), folio {folio_factura} agregado por primera vez")
                        else:
                            self.logger.info(f"Factura complementaria detectada (serie: {serie_factura}), folio {folio_factura} omitido (ya agregado)")
                    else:
                        # No es complementaria, agregar normalmente
                        folios_factura.append(self._limpiar_nombre_archivo(folio_factura))
                        folios_ya_agregados.add(folio_factura)
                
                # Obtener datos del primer elemento para proveedor y clase
                proveedor = self._limpiar_nombre_archivo(self._obtener_nombre_para_archivo(selected_items[0]))
                clase = self._limpiar_clase(str(selected_items[0].get('clase', 'SinClase')))
                
                # Crear nombre del archivo
                vales_str = " ".join(numeros_vale)  # Unir múltiples vales con guión bajo
                folios_str = " ".join(folios_factura)  # Unir múltiples folios con guión bajo
                
                # Solo incluir clase si NO es "Vacio"
                if clase and clase.lower() != 'vacio':
                    nombre_archivo = f"{vales_str} {proveedor} {folios_str} {clase}.pdf"
                else:
                    nombre_archivo = f"{vales_str} {proveedor} {folios_str}.pdf"
                
                # Mostrar diálogo para guardar
                filename = filedialog.asksaveasfilename(
                    title="Guardar documento de cheque (múltiples elementos)",
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                    initialfile=nombre_archivo,
                    parent=self
                )
                
                if filename:
                    ruta_exportacion = filename
                    print(f"🔄 [DEBUG] Usuario seleccionó ruta para {len(selected_items)} elementos: {ruta_exportacion}")
                    self.logger.info(f"Ruta de exportación ({len(selected_items)} elementos): {ruta_exportacion}")
            
            # Variable ruta_exportacion ya contiene la ruta seleccionada
            if ruta_exportacion:
                self.logger.info(f"Documento de cheque será guardado en: {ruta_exportacion}")
                
                # Procesar con la clase Cheque
                try:
                    if Cheque is None:
                        self.dialog_utils.show_error(
                            "Error", 
                            "La clase Cheque no está disponible. Verifique la instalación."
                        )
                        return
                    
                    if len(selected_items) == 1:
                        # Un solo elemento - usar la primera factura
                        try:
                            cheque = Cheque(selected_items[0], ruta_exportacion)
                            
                            # Generar el cheque
                            if cheque.exportar():
                                self.dialog_utils.show_info(
                                    "Cheque Generado", 
                                    f"El cheque ha sido generado exitosamente:\n{ruta_exportacion}"
                                )
                                self.logger.info(f"Cheque generado exitosamente: {ruta_exportacion}")
                            else:
                                self.dialog_utils.show_error(
                                    "Error", 
                                    f"Error al generar el cheque en:\n{ruta_exportacion}"
                                )
                        except ValueError as ve:
                            self.logger.error(f"Error de validación en cheque individual: {ve}")
                            self.dialog_utils.show_error(
                                "Error de Validación", 
                                f"Error validando datos para el cheque:\n{str(ve)}"
                            )
                        except Exception as ie:
                            self.logger.error(f"Error inesperado generando cheque individual: {ie}")
                            self.dialog_utils.show_error(
                                "Error Inesperado", 
                                f"Error inesperado al generar el cheque:\n{str(ie)}\n\n"
                                "Revise el log para más detalles."
                            )
                    else:
                        # Múltiples elementos - usar la funcionalidad de facturas múltiples
                        self.logger.info(f"Iniciando generación de cheque múltiple para {len(selected_items)} facturas del proveedor: {primer_proveedor}")
                        
                        # DEBUG: Mostrar datos de cada factura seleccionada
                        self.logger.info("DEBUG - Facturas seleccionadas:")
                        facturas_complementarias_count = 0
                        for i, item in enumerate(selected_items, 1):
                            serie = str(item.get('serie', ''))
                            es_complementaria = serie.lower().startswith('div-')
                            if es_complementaria:
                                facturas_complementarias_count += 1
                            self.logger.info(f"  {i}. Vale: {item.get('no_vale', 'N/A')}, Serie: {serie}, Folio: {item.get('folio', 'N/A')}, Total: {item.get('total', 'N/A')}, Complementaria: {es_complementaria}")
                        
                        self.logger.info(f"Total facturas complementarias detectadas: {facturas_complementarias_count}")
                        self.logger.info(f"Folios únicos a incluir en nombre: {folios_factura}")
                        
                        try:
                            print(f"🔄 [DEBUG] Llamando crear_multiple con ruta: {ruta_exportacion}")
                            cheque = Cheque.crear_multiple(selected_items, ruta_exportacion)
                            
                            # DEBUG: Verificar datos del formulario antes de generar
                            datos_formulario = cheque.get_datos_formulario()
                            campo_costos_debug = datos_formulario.get('Costos', '')
                            self.logger.info(f"DEBUG - Campo Costos generado: '{campo_costos_debug}' (longitud: {len(campo_costos_debug)})")
                            
                            # Generar el cheque consolidado
                            if cheque.exportar():
                                # Calcular estadísticas para el mensaje
                                total_consolidado = sum(float(item.get('total', 0)) for item in selected_items)
                                iva_consolidado = sum(float(item.get('iva_trasladado', 0)) for item in selected_items)
                                
                                # Contar facturas complementarias
                                facturas_complementarias = [item for item in selected_items 
                                                           if str(item.get('serie', '')).lower().startswith('div-')]
                                tiene_complementarias = len(facturas_complementarias) > 0
                                
                                mensaje_detalle = (
                                    f"Cheque múltiple generado exitosamente:\n"
                                    f"Archivo: {ruta_exportacion}\n\n"
                                    f"Resumen:\n"
                                    f"• Facturas consolidadas: {len(selected_items)}\n"
                                    f"• Proveedor: {primer_proveedor}\n"
                                    f"• Total consolidado: ${total_consolidado:,.2f}\n"
                                    f"• IVA consolidado: ${iva_consolidado:,.2f}\n"
                                    f"• Vales: {', '.join(numeros_vale)}\n"
                                    f"• Folios únicos: {', '.join(folios_factura)}"
                                )
                                
                                if tiene_complementarias:
                                    mensaje_detalle += f"\n• Facturas complementarias: {len(facturas_complementarias)} (folios no duplicados)"
                                
                                self.dialog_utils.show_info("Cheque Múltiple Generado", mensaje_detalle)
                                self.logger.info(f"Cheque múltiple generado exitosamente: {ruta_exportacion} - {len(selected_items)} facturas consolidadas - Total: ${total_consolidado:,.2f}")
                            else:
                                self.logger.error(f"Error generando cheque múltiple en: {ruta_exportacion}")
                                self.dialog_utils.show_error(
                                    "Error", 
                                    f"Error al generar el cheque múltiple en:\n{ruta_exportacion}\n\n"
                                    "Verifique que la ruta sea válida y tenga permisos de escritura."
                                )
                        
                        except ValueError as ve:
                            self.logger.error(f"Error de validación en cheque múltiple: {ve}")
                            self.dialog_utils.show_error(
                                "Error de Validación", 
                                f"Error validando datos para el cheque múltiple:\n{str(ve)}"
                            )
                        
                        except Exception as me:
                            self.logger.error(f"Error inesperado generando cheque múltiple: {me}")
                            self.dialog_utils.show_error(
                                "Error Inesperado", 
                                f"Error inesperado al generar el cheque múltiple:\n{str(me)}\n\n"
                                "Revise el log para más detalles."
                            )
                        
                except Exception as cheque_error:
                    self.logger.error(f"Error procesando cheque: {cheque_error}")
                    self.dialog_utils.show_error(
                        "Error Procesando Cheque", 
                        f"Error al procesar el cheque:\n{str(cheque_error)}"
                    )
            
        except Exception as e:
            self.logger.error(f"Error en función de cheque: {e}")
            self.dialog_utils.show_error("Error", f"Error procesando cheque: {str(e)}")
    
    def _limpiar_clase(self, clase) -> str:
        """
        Limpia una clase para nombre de archivo preservando formato letra-número
        
        Args:
            clase: String de la clase
            
        Returns:
            String limpio para usar como clase en nombre de archivo
        """
        if clase is None:
            return 'Vacio'
        
        clase_str = str(clase)
        
        if not clase_str or clase_str.strip() == '':
            return 'Vacio'
        
        # Para clases, solo remover caracteres problemáticos pero mantener guiones
        caracteres_invalidos = '<>:"/\\|?*'  # Sin incluir - para preservar Q-15
        clase_limpia = clase_str
        
        for char in caracteres_invalidos:
            clase_limpia = clase_limpia.replace(char, '')
        
        # Limitar longitud
        if len(clase_limpia) > 20:
            clase_limpia = clase_limpia[:20]
        
        # Si queda vacío después de limpiar, usar valor por defecto
        if not clase_limpia:
            return 'Vacio'
        
        return clase_limpia

    def _obtener_nombre_para_archivo(self, item) -> str:
        """
        Obtiene el nombre a usar en el archivo: nombre_contacto si existe, sino nombre_emisor
        
        Args:
            item: Diccionario con los datos del item
            
        Returns:
            String con el nombre a usar (contacto o emisor)
        """
        nombre_contacto = item.get('nombre_contacto', '')
        nombre_emisor = item.get('nombre_emisor', '')
        
        # Si hay nombre_contacto y no está vacío, usarlo
        if nombre_contacto and str(nombre_contacto).strip():
            return str(nombre_contacto).strip()
        else:
            # Si no hay nombre_contacto, usar nombre_emisor
            return str(nombre_emisor).strip()

    def _limpiar_nombre_archivo(self, nombre) -> str:
        """
        Limpia un string para que pueda ser usado como nombre de archivo
        
        Args:
            nombre: String o número a limpiar
            
        Returns:
            String limpio para usar como nombre de archivo
        """
        # Convertir a string si no lo es
        if nombre is None:
            return 'Vacio'
        
        nombre_str = str(nombre)
        
        if not nombre_str or nombre_str.strip() == '':
            return 'Vacio'
        
        # Reemplazar caracteres no válidos
        caracteres_invalidos = '<>:"/\\|?*_-'  # Agregado _ y - para quitarlos
        nombre_limpio = nombre_str
        
        for char in caracteres_invalidos:
            nombre_limpio = nombre_limpio.replace(char, '')  # Reemplazar con vacío en lugar de _
        
        # Reemplazar espacios por nada (quitar espacios)
        #nombre_limpio = nombre_limpio.replace(' ', '')
        
        # Si es un folio con serie (contiene guión y la parte después del guión es solo números), 
        # tomar solo la parte después del guión
        if '-' in nombre_str:
            partes = nombre_str.split('-')
            if len(partes) > 1:
                ultima_parte = partes[-1]
                # Solo quitar la serie si la última parte son solo números (típico de folios)
                if ultima_parte.isdigit():
                    nombre_limpio = ultima_parte
                    # Limpiar caracteres especiales de la parte seleccionada
                    for char in '<>:"/\\|?*_':
                        nombre_limpio = nombre_limpio.replace(char, '')
                    nombre_limpio = nombre_limpio.replace(' ', '')
                else:
                    # Si no es solo números, mantener todo el nombre pero limpiar caracteres
                    for char in caracteres_invalidos:
                        nombre_limpio = nombre_limpio.replace(char, '')
        else:
            # No contiene guión, solo limpiar caracteres inválidos
            for char in caracteres_invalidos:
                nombre_limpio = nombre_limpio.replace(char, '')
        
        # Limitar longitud
        if len(nombre_limpio) > 30:  # Reducido de 50 a 30 para nombres más cortos
            nombre_limpio = nombre_limpio[:30]
        
        # Si queda vacío después de limpiar, usar valor por defecto
        if not nombre_limpio:
            return 'Item'
        
        return nombre_limpio
    
    def _update_status_message(self):
        """Actualiza el mensaje de estado de la base de datos en la esquina inferior derecha"""
        try:
            search_state = self.search_controller.get_state()
            
            if search_state.database_available:
                self.db_status_label.config(
                    text="BD Conectada",
                    bootstyle="success"
                )
            else:
                self.db_status_label.config(
                    text="BD Desconectada", 
                    bootstyle="danger"
                )
                
        except Exception as e:
            self.logger.error(f"Error actualizando mensaje de estado: {e}")
            self.db_status_label.config(
                text="BD Error",
                bootstyle="warning"
            )


def main():
    """Función principal para ejecutar la aplicación refactorizada"""
    try:
        # Configurar logging básico
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Crear ventana principal
        root = ttk.Window(themename="cosmo")
        root.title("Búsqueda de Facturas - Versión Refactorizada")
        root.geometry("1400x800")
        root.minsize(1200, 700)
        
        # Crear aplicación
        app = BuscarAppRefactored(root)
        app.pack(fill="both", expand=True)
        
        # Centrar ventana
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Ejecutar aplicación
        root.mainloop()
        
    except Exception as e:
        print(f"Error ejecutando aplicación refactorizada: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
