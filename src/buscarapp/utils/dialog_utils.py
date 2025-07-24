"""
Utilidades para diálogos y mensajes
"""
import ttkbootstrap as tb
from tkinter import filedialog
from typing import Optional, Tuple


class DialogUtils:
    """Utilidades para mostrar diálogos estándar"""
    
    def __init__(self, parent=None):
        """
        Inicializa DialogUtils
        
        Args:
            parent: Widget padre para los diálogos
        """
        self.parent = parent
    
    def show_warning(self, title: str, message: str, parent=None) -> None:
        """Muestra un diálogo de advertencia"""
        parent = parent or self.parent
        tb.dialogs.Messagebox.show_warning(
            title=title,
            message=message,
            parent=parent
        )
    
    def show_info(self, title: str, message: str, parent=None) -> None:
        """Muestra un diálogo informativo"""
        parent = parent or self.parent
        tb.dialogs.Messagebox.show_info(
            title=title,
            message=message,
            parent=parent
        )
    
    def show_error(self, title: str, message: str, parent=None) -> None:
        """Muestra un diálogo de error"""
        parent = parent or self.parent
        tb.dialogs.Messagebox.show_error(
            title=title,
            message=message,
            parent=parent
        )
    
    def ask_yes_no(self, title: str, message: str, parent=None) -> bool:
        """
        Muestra un diálogo de confirmación Sí/No
        
        Returns:
            bool: True si el usuario seleccionó "Yes", False en caso contrario
        """
        parent = parent or self.parent
        result = tb.dialogs.Messagebox.yesno(
            title=title,
            message=message,
            parent=parent
        )
        return result == "Yes"
    
    @staticmethod
    def save_file_dialog(parent, title: str, default_filename: str = "", 
                        file_types: list = None) -> Optional[str]:
        """
        Muestra un diálogo para guardar archivo
        
        Args:
            parent: Ventana padre
            title: Título del diálogo
            default_filename: Nombre por defecto del archivo
            file_types: Lista de tipos de archivo [("Descripción", "*.ext")]
            
        Returns:
            Optional[str]: Ruta del archivo seleccionado o None si se canceló
        """
        if file_types is None:
            file_types = [("Archivos PDF", "*.pdf")]
            
        return filedialog.asksaveasfilename(
            title=title,
            defaultextension=file_types[0][1].replace("*", ""),
            filetypes=file_types,
            initialfile=default_filename,
            parent=parent
        )


def show_no_selection_warning(parent) -> None:
    """Muestra advertencia cuando no hay selección"""
    DialogUtils.show_warning(
        parent, 
        "Sin selección",
        "Por favor seleccione una factura."
    )


def show_no_database_info(parent, operation: str) -> None:
    """Muestra información cuando no hay base de datos disponible"""
    DialogUtils.show_info(
        parent,
        operation,
        f"{operation} solo está disponible con datos reales de la base de datos."
    )


def confirm_estado_change(parent, folio: str, current_state: bool, 
                         operation: str) -> bool:
    """
    Confirma cambio de estado de una factura
    
    Args:
        parent: Ventana padre
        folio: Folio de la factura
        current_state: Estado actual
        operation: Nombre de la operación
        
    Returns:
        bool: True si el usuario confirma el cambio
    """
    if not current_state:
        message = f"¿Desea marcar la factura {folio} como {operation.upper()}?"
        title = f"Marcar como {operation}"
    else:
        message = f"La factura {folio} está actualmente {operation.upper()}.\n\n¿Desea cambiarla a NO {operation.upper()}?"
        title = f"Cambiar a No {operation}"
    
    return DialogUtils.ask_yes_no(parent, title, message)
