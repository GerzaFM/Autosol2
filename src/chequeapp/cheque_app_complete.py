"""
Aplicación completa de gestión de Cheques
Versión profesional con funcionalidades completas
"""
import logging
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
from typing import Optional, Dict, Any
import csv
from datetime import date

# Importar componentes de la aplicación
from .models.cheque_models import ChequeData
from .controllers.cheque_controller import ChequeController
from .views.cheque_filter_frame import ChequeFilterFrame
from .views.cheque_table_frame import ChequeTableFrame
from .views.cheque_action_frame import ChequeActionFrame

# Configurar logging
logger = logging.getLogger(__name__)


class ChequeAppComplete(tb.Frame):
    """
    Aplicación completa de gestión de Cheques
    Incluye filtros, tabla, acciones y diálogos
    """
    
    def __init__(self, master=None):
        """
        Inicializa la aplicación completa de cheques
        
        Args:
            master: Widget padre
        """
        super().__init__(master)
        self.master = master
        self.logger = logger
        
        # Controlador principal
        self.cheque_controller: Optional[ChequeController] = None
        
        # Componentes UI
        self.filter_frame: Optional[ChequeFilterFrame] = None
        self.table_frame: Optional[ChequeTableFrame] = None
        self.action_frame: Optional[ChequeActionFrame] = None
        
        # Estado actual
        self.selected_cheque_data: Optional[Dict[str, Any]] = None
        
        self._initialize_components()
        self._setup_ui()
        
        self.logger.info("Aplicación completa de cheques inicializada")
    
    def _initialize_components(self):
        """Inicializa los componentes de la aplicación"""
        try:
            # Inicializar controlador de cheques
            self.cheque_controller = ChequeController()
            self.cheque_controller.load_cheques()
            
            self.logger.info("Componentes inicializados correctamente")
            
        except Exception as e:
            self.logger.error(f"Error inicializando componentes: {e}")
            raise
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Configurar el frame principal
        self.pack(fill=BOTH, expand=True)
        
        # Frame principal con padding
        main_container = tb.Frame(self, padding=5)
        main_container.pack(fill=BOTH, expand=True)
        
        # Frame de filtros (parte superior)
        self.filter_frame = ChequeFilterFrame(
            parent=main_container,
            search_callback=self._on_search,
            clear_callback=self._on_clear_filters
        )
        self.filter_frame.main_frame.pack(fill=X, pady=(0, 5))
        
        # Frame de tabla (centro)
        self.table_frame = ChequeTableFrame(
            parent=main_container,
            on_selection_callback=self._on_table_selection,
            on_double_click_callback=self._on_table_double_click
        )
        self.table_frame.main_frame.pack(fill=BOTH, expand=True, pady=(0, 5))
        
        # Frame de acciones (parte inferior)
        self.action_frame = ChequeActionFrame(
            parent=main_container,
            on_new_callback=self._on_new_cheque,
            on_edit_callback=self._on_edit_cheque,
            on_delete_callback=self._on_delete_cheque,
            on_mark_cobrado_callback=self._on_mark_cobrado,
            on_mark_cancelado_callback=self._on_mark_cancelado,
            on_print_callback=self._on_print_cheque,
            on_export_callback=self._on_export_data
        )
        self.action_frame.main_frame.pack(fill=X)
        
        # Realizar búsqueda inicial
        self._perform_initial_search()
    
    def _perform_initial_search(self):
        """Realiza una búsqueda inicial para mostrar todos los cheques"""
        try:
            if self.cheque_controller:
                state = self.cheque_controller.get_state()
                results = [cheque.to_dict() for cheque in state.all_cheques]
                self.table_frame.load_data(results)
                self.logger.info(f"Búsqueda inicial: {len(results)} cheques cargados")
        except Exception as e:
            self.logger.error(f"Error en búsqueda inicial: {e}")
    
    def _on_search(self):
        """Maneja el evento de búsqueda"""
        try:
            if not self.cheque_controller or not self.filter_frame:
                return
            
            # Obtener filtros
            filters_dict = self.filter_frame.get_filters()
            
            # Aplicar filtros
            results = self.cheque_controller.apply_filters(filters_dict)
            
            # Actualizar tabla
            self.table_frame.load_data(results)
            
            self.logger.info(f"Búsqueda completada: {len(results)} cheques encontrados")
            
        except Exception as e:
            self.logger.error(f"Error durante la búsqueda: {e}")
            messagebox.showerror("Error", f"Error durante la búsqueda: {e}")
    
    def _on_clear_filters(self):
        """Maneja el evento de limpiar filtros"""
        try:
            # Limpiar filtros en el controlador
            if self.cheque_controller:
                self.cheque_controller.clear_filters()
            
            # Realizar búsqueda sin filtros
            self._perform_initial_search()
            
            self.logger.info("Filtros limpiados")
            
        except Exception as e:
            self.logger.error(f"Error limpiando filtros: {e}")
    
    def _on_table_selection(self, selected_data: Dict[str, Any]):
        """Maneja el evento de selección en la tabla"""
        try:
            self.selected_cheque_data = selected_data
            
            # Actualizar botones de acción
            if self.action_frame:
                self.action_frame.update_selection(selected_data)
            
            if selected_data:
                self.logger.debug(f"Cheque seleccionado: {selected_data.get('numero_cheque', 'N/A')}")
                
        except Exception as e:
            self.logger.error(f"Error en selección: {e}")
    
    def _on_table_double_click(self, selected_data: Dict[str, Any]):
        """Maneja el evento de doble click en la tabla"""
        try:
            # Doble click abre el diálogo de edición
            self._on_edit_cheque(selected_data)
            
        except Exception as e:
            self.logger.error(f"Error en doble click: {e}")
    
    def _on_new_cheque(self):
        """Maneja la creación de un nuevo cheque"""
        try:
            # Crear diálogo para nuevo cheque
            dialog = ChequeFormDialog(self, title="Nuevo Cheque")
            result = dialog.show()
            
            if result:
                # Crear el cheque
                success = self.cheque_controller.create_cheque(result)
                if success:
                    messagebox.showinfo("Éxito", "Cheque creado correctamente")
                    self._perform_initial_search()  # Refrescar tabla
                else:
                    messagebox.showerror("Error", "Error al crear el cheque")
            
        except Exception as e:
            self.logger.error(f"Error creando nuevo cheque: {e}")
            messagebox.showerror("Error", f"Error creando nuevo cheque: {e}")
    
    def _on_edit_cheque(self, cheque_data: Dict[str, Any]):
        """Maneja la edición de un cheque"""
        try:
            if not cheque_data:
                return
            
            # Obtener el ID del cheque
            cheque_id = cheque_data.get('id')
            if not cheque_id:
                messagebox.showerror("Error", "No se pudo obtener el ID del cheque")
                return
            
            # Obtener datos completos del cheque
            cheque_obj = self.cheque_controller.get_cheque_by_id(int(cheque_id))
            if not cheque_obj:
                messagebox.showerror("Error", "Cheque no encontrado")
                return
            
            # Crear diálogo para editar cheque
            dialog = ChequeFormDialog(self, title="Editar Cheque", cheque_data=cheque_obj)
            result = dialog.show()
            
            if result:
                # Actualizar el cheque
                success = self.cheque_controller.update_cheque(result)
                if success:
                    messagebox.showinfo("Éxito", "Cheque actualizado correctamente")
                    self._on_search()  # Refrescar con filtros actuales
                else:
                    messagebox.showerror("Error", "Error al actualizar el cheque")
            
        except Exception as e:
            self.logger.error(f"Error editando cheque: {e}")
            messagebox.showerror("Error", f"Error editando cheque: {e}")
    
    def _on_delete_cheque(self, cheque_data: Dict[str, Any]):
        """Maneja la eliminación de un cheque"""
        try:
            if not cheque_data:
                return
            
            numero_cheque = cheque_data.get('numero_cheque', 'N/A')
            
            # Confirmar eliminación
            confirm = messagebox.askyesno(
                "Confirmar Eliminación",
                f"¿Está seguro de eliminar el cheque {numero_cheque}?\n\nEsta acción no se puede deshacer."
            )
            
            if not confirm:
                return
            
            # Obtener ID del cheque
            cheque_id = cheque_data.get('id')
            if not cheque_id:
                messagebox.showerror("Error", "No se pudo obtener el ID del cheque")
                return
            
            # Eliminar el cheque
            success = self.cheque_controller.delete_cheque(int(cheque_id))
            if success:
                messagebox.showinfo("Éxito", "Cheque eliminado correctamente")
                self._on_search()  # Refrescar tabla
            else:
                messagebox.showerror("Error", "Error al eliminar el cheque")
            
        except Exception as e:
            self.logger.error(f"Error eliminando cheque: {e}")
            messagebox.showerror("Error", f"Error eliminando cheque: {e}")
    
    def _on_mark_cobrado(self, cheque_data: Dict[str, Any]):
        """Marca un cheque como cobrado"""
        try:
            if not cheque_data:
                return
            
            cheque_id = cheque_data.get('id')
            numero_cheque = cheque_data.get('numero_cheque', 'N/A')
            
            if not cheque_id:
                messagebox.showerror("Error", "No se pudo obtener el ID del cheque")
                return
            
            # Confirmar acción
            confirm = messagebox.askyesno(
                "Confirmar Cambio de Estado",
                f"¿Marcar el cheque {numero_cheque} como COBRADO?"
            )
            
            if not confirm:
                return
            
            # Cambiar estado
            success = self.cheque_controller.change_cheque_status(int(cheque_id), "COBRADO")
            if success:
                messagebox.showinfo("Éxito", "Cheque marcado como cobrado")
                self._on_search()  # Refrescar tabla
            else:
                messagebox.showerror("Error", "Error al cambiar el estado del cheque")
            
        except Exception as e:
            self.logger.error(f"Error marcando cheque como cobrado: {e}")
            messagebox.showerror("Error", f"Error marcando cheque como cobrado: {e}")
    
    def _on_mark_cancelado(self, cheque_data: Dict[str, Any]):
        """Marca un cheque como cancelado"""
        try:
            if not cheque_data:
                return
            
            cheque_id = cheque_data.get('id')
            numero_cheque = cheque_data.get('numero_cheque', 'N/A')
            
            if not cheque_id:
                messagebox.showerror("Error", "No se pudo obtener el ID del cheque")
                return
            
            # Confirmar acción
            confirm = messagebox.askyesno(
                "Confirmar Cambio de Estado",
                f"¿Marcar el cheque {numero_cheque} como CANCELADO?"
            )
            
            if not confirm:
                return
            
            # Cambiar estado
            success = self.cheque_controller.change_cheque_status(int(cheque_id), "CANCELADO")
            if success:
                messagebox.showinfo("Éxito", "Cheque marcado como cancelado")
                self._on_search()  # Refrescar tabla
            else:
                messagebox.showerror("Error", "Error al cambiar el estado del cheque")
            
        except Exception as e:
            self.logger.error(f"Error marcando cheque como cancelado: {e}")
            messagebox.showerror("Error", f"Error marcando cheque como cancelado: {e}")
    
    def _on_print_cheque(self, cheque_data: Dict[str, Any]):
        """Imprime un cheque"""
        try:
            if not cheque_data:
                return
            
            numero_cheque = cheque_data.get('numero_cheque', 'N/A')
            
            # Por ahora, solo mostrar un mensaje
            messagebox.showinfo(
                "Imprimir Cheque",
                f"Funcionalidad de impresión para el cheque {numero_cheque}\n\n" +
                "Esta funcionalidad será implementada en una versión futura."
            )
            
        except Exception as e:
            self.logger.error(f"Error imprimiendo cheque: {e}")
            messagebox.showerror("Error", f"Error imprimiendo cheque: {e}")
    
    def _on_export_data(self):
        """Exporta los datos actuales a CSV"""
        try:
            # Obtener datos actuales de la tabla
            if not self.cheque_controller:
                return
            
            state = self.cheque_controller.get_state()
            data_to_export = state.filtered_cheques
            
            if not data_to_export:
                messagebox.showwarning("Advertencia", "No hay datos para exportar")
                return
            
            # Seleccionar archivo de destino
            filename = filedialog.asksaveasfilename(
                title="Exportar Cheques",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialname=f"cheques_{date.today().strftime('%Y%m%d')}.csv"
            )
            
            if not filename:
                return
            
            # Exportar a CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'numero_cheque', 'fecha_cheque', 'beneficiario', 'monto',
                    'banco', 'cuenta', 'estado', 'fecha_cobro', 'concepto', 'observaciones'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for cheque in data_to_export:
                    row = cheque.to_dict()
                    # Filtrar solo los campos que queremos exportar
                    filtered_row = {field: row.get(field, '') for field in fieldnames}
                    writer.writerow(filtered_row)
            
            messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filename}")
            
        except Exception as e:
            self.logger.error(f"Error exportando datos: {e}")
            messagebox.showerror("Error", f"Error exportando datos: {e}")


# Placeholder para el diálogo de formulario
class ChequeFormDialog:
    """Diálogo para crear/editar cheques (placeholder)"""
    
    def __init__(self, parent, title="Cheque", cheque_data=None):
        self.parent = parent
        self.title = title
        self.cheque_data = cheque_data
    
    def show(self):
        """Muestra el diálogo (placeholder)"""
        # Por ahora, solo un mensaje de placeholder
        messagebox.showinfo(
            "Diálogo de Cheque",
            f"Esta funcionalidad ({self.title}) será implementada en el futuro.\n\n" +
            "Incluirá un formulario completo para crear/editar cheques con todos los campos necesarios."
        )
        return None


if __name__ == "__main__":
    # Ejecutar la aplicación completa de forma independiente
    root = tb.Window(themename="darkly")
    root.title("Gestión Completa de Cheques")
    root.geometry("1400x900")
    
    app = ChequeAppComplete(root)
    
    root.mainloop()
