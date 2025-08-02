"""
Frame de botones de acción para cheques
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import Callable, Optional, Dict, Any
import logging


class ChequeActionFrame:
    """Frame que contiene los botones de acción para cheques"""
    
    def __init__(self, parent,
                 on_new_callback: Optional[Callable] = None,
                 on_edit_callback: Optional[Callable] = None,
                 on_delete_callback: Optional[Callable] = None,
                 on_mark_cobrado_callback: Optional[Callable] = None,
                 on_mark_cancelado_callback: Optional[Callable] = None,
                 on_print_callback: Optional[Callable] = None,
                 on_export_callback: Optional[Callable] = None):
        
        self.parent = parent
        self.on_new_callback = on_new_callback
        self.on_edit_callback = on_edit_callback
        self.on_delete_callback = on_delete_callback
        self.on_mark_cobrado_callback = on_mark_cobrado_callback
        self.on_mark_cancelado_callback = on_mark_cancelado_callback
        self.on_print_callback = on_print_callback
        self.on_export_callback = on_export_callback
        self.logger = logging.getLogger(__name__)
        
        # Estado actual de la selección
        self.selected_data: Optional[Dict[str, Any]] = None
        
        # Crear frame principal
        self.main_frame = ttk.Frame(parent)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea todos los widgets del frame de botones"""
        
        # Frame contenedor con padding
        controls_frame = ttk.Frame(self.main_frame, padding=10)
        controls_frame.pack(fill="x")
        
        # Frame izquierdo para botones de gestión
        left_controls = ttk.Frame(controls_frame)
        left_controls.pack(side="left")
        
        # Frame derecho para botones de estado
        right_controls = ttk.Frame(controls_frame)
        right_controls.pack(side="right")
        
        # Botones de gestión (izquierda)
        button_width = 12
        
        # Botón Nuevo
        self.new_btn = ttk.Button(
            left_controls,
            text="Nuevo",
            command=self._on_new_clicked,
            bootstyle="success",
            width=button_width
        )
        self.new_btn.pack(side="left", padx=(0, 5))
        
        # Botón Editar
        self.edit_btn = ttk.Button(
            left_controls,
            text="Editar",
            command=self._on_edit_clicked,
            bootstyle="primary",
            width=button_width,
            state="disabled"
        )
        self.edit_btn.pack(side="left", padx=(0, 5))
        
        # Botón Eliminar
        self.delete_btn = ttk.Button(
            left_controls,
            text="Eliminar",
            command=self._on_delete_clicked,
            bootstyle="danger",
            width=button_width,
            state="disabled"
        )
        self.delete_btn.pack(side="left", padx=(0, 5))
        
        # Separador
        separator = ttk.Separator(left_controls, orient="vertical")
        separator.pack(side="left", fill="y", padx=10)
        
        # Botón Imprimir
        self.print_btn = ttk.Button(
            left_controls,
            text="Imprimir",
            command=self._on_print_clicked,
            bootstyle="info",
            width=button_width,
            state="disabled"
        )
        self.print_btn.pack(side="left", padx=(0, 5))
        
        # Botón Exportar
        self.export_btn = ttk.Button(
            left_controls,
            text="Exportar",
            command=self._on_export_clicked,
            bootstyle="secondary",
            width=button_width
        )
        self.export_btn.pack(side="left", padx=(0, 5))
        
        # Botones de estado (derecha)
        
        # Botón Marcar Cobrado
        self.mark_cobrado_btn = ttk.Button(
            right_controls,
            text="Marcar Cobrado",
            command=self._on_mark_cobrado_clicked,
            bootstyle="success-outline",
            width=15,
            state="disabled"
        )
        self.mark_cobrado_btn.pack(side="right", padx=(10, 0))
        
        # Botón Marcar Cancelado
        self.mark_cancelado_btn = ttk.Button(
            right_controls,
            text="Marcar Cancelado",
            command=self._on_mark_cancelado_clicked,
            bootstyle="danger-outline",
            width=15,
            state="disabled"
        )
        self.mark_cancelado_btn.pack(side="right", padx=(10, 0))
    
    def update_selection(self, selected_data: Optional[Dict[str, Any]]):
        """Actualiza el estado de los botones según la selección"""
        self.selected_data = selected_data
        
        if selected_data:
            # Habilitar botones que requieren selección
            self.edit_btn.config(state="normal")
            self.delete_btn.config(state="normal")
            self.print_btn.config(state="normal")
            
            # Habilitar botones de estado según el estado actual
            current_estado = selected_data.get('estado', '')
            
            if current_estado == "PENDIENTE":
                self.mark_cobrado_btn.config(state="normal")
                self.mark_cancelado_btn.config(state="normal")
            elif current_estado == "COBRADO":
                self.mark_cobrado_btn.config(state="disabled")
                self.mark_cancelado_btn.config(state="normal")
            elif current_estado == "CANCELADO":
                self.mark_cobrado_btn.config(state="disabled")
                self.mark_cancelado_btn.config(state="disabled")
            else:
                self.mark_cobrado_btn.config(state="disabled")
                self.mark_cancelado_btn.config(state="disabled")
        else:
            # Deshabilitar botones que requieren selección
            self.edit_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")
            self.print_btn.config(state="disabled")
            self.mark_cobrado_btn.config(state="disabled")
            self.mark_cancelado_btn.config(state="disabled")
    
    def _on_new_clicked(self):
        """Maneja el evento de nuevo cheque"""
        try:
            if self.on_new_callback:
                self.on_new_callback()
        except Exception as e:
            self.logger.error(f"Error en nuevo cheque: {e}")
    
    def _on_edit_clicked(self):
        """Maneja el evento de editar cheque"""
        try:
            if self.on_edit_callback and self.selected_data:
                self.on_edit_callback(self.selected_data)
        except Exception as e:
            self.logger.error(f"Error editando cheque: {e}")
    
    def _on_delete_clicked(self):
        """Maneja el evento de eliminar cheque"""
        try:
            if self.on_delete_callback and self.selected_data:
                self.on_delete_callback(self.selected_data)
        except Exception as e:
            self.logger.error(f"Error eliminando cheque: {e}")
    
    def _on_mark_cobrado_clicked(self):
        """Maneja el evento de marcar como cobrado"""
        try:
            if self.on_mark_cobrado_callback and self.selected_data:
                self.on_mark_cobrado_callback(self.selected_data)
        except Exception as e:
            self.logger.error(f"Error marcando como cobrado: {e}")
    
    def _on_mark_cancelado_clicked(self):
        """Maneja el evento de marcar como cancelado"""
        try:
            if self.on_mark_cancelado_callback and self.selected_data:
                self.on_mark_cancelado_callback(self.selected_data)
        except Exception as e:
            self.logger.error(f"Error marcando como cancelado: {e}")
    
    def _on_print_clicked(self):
        """Maneja el evento de imprimir cheque"""
        try:
            if self.on_print_callback and self.selected_data:
                self.on_print_callback(self.selected_data)
        except Exception as e:
            self.logger.error(f"Error imprimiendo cheque: {e}")
    
    def _on_export_clicked(self):
        """Maneja el evento de exportar datos"""
        try:
            if self.on_export_callback:
                self.on_export_callback()
        except Exception as e:
            self.logger.error(f"Error exportando datos: {e}")
