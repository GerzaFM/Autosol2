"""
Aplicación principal de Cheques.
Aplicación simplificada para búsqueda de facturas.
"""
import logging
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from typing import Optional

# Importar componentes de la aplicación
from .views.search_frame import SearchFrame
from .views.table_frame import TableFrame
from .controllers.search_controller import SearchController

# Configurar logging
logger = logging.getLogger(__name__)


class ChequeApp(tb.Frame):
    """
    Aplicación principal de Cheques.
    Aplicación simplificada para búsqueda de facturas.
    """
    
    def __init__(self, master=None):
        """
        Inicializa la aplicación de cheques.
        
        Args:
            master: Widget padre
        """
        super().__init__(master)
        self.master = master
        self.logger = logger
        
        # Controladores
        self.search_controller: Optional[SearchController] = None
        
        # Componentes UI
        self.search_frame: Optional[SearchFrame] = None
        self.table_frame: Optional[TableFrame] = None
        
        self._initialize_components()
        self._setup_ui()
        
        self.logger.info("Aplicación de cheques inicializada")
    
    def _initialize_components(self):
        """Inicializa los componentes de la aplicación."""
        try:
            # Inicializar controlador de búsqueda
            self.search_controller = SearchController()
            self.search_controller.load_initial_data()
            
            self.logger.info("Componentes inicializados correctamente")
            
        except Exception as e:
            self.logger.error(f"Error inicializando componentes: {e}")
            raise
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        # Frame principal
        main_frame = tb.Frame(self)
        main_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Frame de búsqueda (parte superior)
        self.search_frame = SearchFrame(
            parent=main_frame,
            search_callback=self._on_search,
            clear_callback=self._on_clear_filters
        )
        self.search_frame.main_frame.pack(fill=X, padx=5, pady=(5, 0))
        
        # Pasar datos iniciales al SearchFrame
        if self.search_controller:
            state = self.search_controller.get_state()
            
            # Pasar datos de tipos de vale
            if hasattr(state, 'tipos_data'):
                if hasattr(self.search_frame, 'set_tipos_data'):
                    self.search_frame.set_tipos_data(state.tipos_data)
            
            # Pasar datos de proveedores
            if hasattr(state, 'proveedores_data'):
                if hasattr(self.search_frame, 'set_proveedores_data'):
                    self.search_frame.set_proveedores_data(state.proveedores_data)
        
        # Frame de tabla (parte inferior)
        self.table_frame = TableFrame(
            parent=main_frame,
            on_selection_callback=self._on_table_selection,
            on_double_click_callback=self._on_table_double_click
        )
        self.table_frame.main_frame.pack(fill=BOTH, expand=True, padx=5, pady=(5, 5))
        
        # Realizar búsqueda inicial
        self._perform_initial_search()
    
    def _perform_initial_search(self):
        """Realiza una búsqueda inicial para mostrar datos."""
        try:
            if self.search_controller:
                # Limpiar filtros para mostrar todos los datos
                self.search_controller.clear_filters()
                state = self.search_controller.get_state()
                self.table_frame.load_data(state.all_facturas)
                self.logger.info(f"Búsqueda inicial completada: {len(state.all_facturas)} resultados")
        except Exception as e:
            self.logger.error(f"Error en búsqueda inicial: {e}")
    
    def _on_search(self):
        """Maneja el evento de búsqueda."""
        try:
            if not self.search_controller or not self.search_frame:
                return
            
            # Obtener filtros del SearchFrame
            filters_dict = self.search_frame.get_filters()
            
            # Aplicar filtros usando el nuevo método
            results = self.search_controller.apply_filters(filters_dict)
            
            # Actualizar tabla
            self.table_frame.load_data(results)
            
            self.logger.info(f"Búsqueda completada: {len(results)} resultados encontrados")
            
        except Exception as e:
            self.logger.error(f"Error durante la búsqueda: {e}")
    
    def _on_clear_filters(self):
        """Maneja el evento de limpiar filtros."""
        try:
            # Limpiar filtros en el SearchFrame
            if self.search_frame:
                self.search_frame.clear_filters()
            
            # Limpiar filtros en el controlador
            if self.search_controller:
                self.search_controller.clear_filters()
            
            # Realizar búsqueda sin filtros
            self._perform_initial_search()
            
            self.logger.info("Filtros limpiados")
            
        except Exception as e:
            self.logger.error(f"Error limpiando filtros: {e}")
            
        except Exception as e:
            self.logger.error(f"Error limpiando filtros: {e}")
    
    def _on_table_selection(self, selected_data):
        """
        Maneja el evento de selección en la tabla.
        
        Args:
            selected_data: Datos de la fila seleccionada
        """
        # En la aplicación de cheques, solo necesitamos la selección básica
        if selected_data:
            self.logger.debug(f"Factura seleccionada: {selected_data.get('folio_interno', 'N/A')}")
    
    def _on_table_double_click(self, selected_data):
        """
        Maneja el evento de doble click en la tabla.
        
        Args:
            selected_data: Datos de la fila seleccionada
        """
        # En la aplicación de cheques, el doble click no tiene funcionalidad especial
        if selected_data:
            self.logger.debug(f"Doble click en factura: {selected_data.get('folio_interno', 'N/A')}")


if __name__ == "__main__":
    # Ejecutar la aplicación de forma independiente para pruebas
    root = tb.Window(themename="darkly")
    root.title("Aplicación de Cheques")
    root.geometry("1200x800")
    
    app = ChequeApp(root)
    app.pack(fill=BOTH, expand=True)
    
    root.mainloop()
