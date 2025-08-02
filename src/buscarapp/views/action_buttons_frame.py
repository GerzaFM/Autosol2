"""
Vista para el frame de botones de acción
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import Callable, Optional
import logging


class ActionButtonsFrame:
    """Frame que contiene los botones de acción"""
    
    def __init__(self, parent, 
                 on_autocarga_callback: Optional[Callable] = None,
                 on_reimprimir_callback: Optional[Callable] = None,
                 on_toggle_cargada_callback: Optional[Callable] = None,
                 on_toggle_pagada_callback: Optional[Callable] = None,
                 on_abrir_xml_callback: Optional[Callable] = None,
                 on_abrir_pdf_callback: Optional[Callable] = None,
                 on_export_callback: Optional[Callable] = None,
                 on_detalles_callback: Optional[Callable] = None,
                 on_modificar_callback: Optional[Callable] = None,
                 on_cheque_callback: Optional[Callable] = None):
        
        self.parent = parent
        self.on_autocarga_callback = on_autocarga_callback
        self.on_reimprimir_callback = on_reimprimir_callback
        self.on_toggle_cargada_callback = on_toggle_cargada_callback
        self.on_toggle_pagada_callback = on_toggle_pagada_callback
        self.on_abrir_xml_callback = on_abrir_xml_callback
        self.on_abrir_pdf_callback = on_abrir_pdf_callback
        self.on_export_callback = on_export_callback
        self.on_detalles_callback = on_detalles_callback
        self.on_modificar_callback = on_modificar_callback
        self.on_cheque_callback = on_cheque_callback
        self.logger = logging.getLogger(__name__)
        
        # Estado actual de la selección
        self.selected_data = None
        
        # Crear frame principal sin padding extra (se maneja internamente)
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill="x")
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea todos los widgets del frame de botones"""
        
        # Frame contenedor con padding igual al original
        controls_frame = ttk.Frame(self.main_frame, padding=10)
        controls_frame.pack(fill="x")
        
        # Frame izquierdo para controles adicionales (vacío por ahora)
        left_controls = ttk.Frame(controls_frame)
        left_controls.pack(side="left")
        
        # Frame derecho para botones de acción
        right_controls = ttk.Frame(controls_frame)
        right_controls.pack(side="right")
        
        # Botones de acción en el orden exacto del original (todos con el mismo ancho)
        button_width = 12  # Ancho uniforme para todos los botones
        
        # Botón Cheque (a la derecha del botón Cargado)
        self.cheque_btn = ttk.Button(
            right_controls,
            text="Cheque",
            command=self._on_cheque_clicked,
            bootstyle="success",
            width=button_width,
            state="disabled"
        )
        self.cheque_btn.pack(side="right", padx=(10, 0))
        
        # Botón Cargado 
        self.toggle_cargada_btn = ttk.Button(
            right_controls,
            text="Cargado",
            command=self._on_toggle_cargada_clicked,
            bootstyle="primary",
            width=button_width,
            state="disabled"
        )
        self.toggle_cargada_btn.pack(side="right", padx=(10, 0))
        
        # Botón Detalles
        self.detalles_btn = ttk.Button(
            right_controls,
            text="Detalles",
            command=self._on_detalles_clicked,
            bootstyle="primary",
            width=button_width,
            state="disabled"
        )
        self.detalles_btn.pack(side="right", padx=(10, 0))
        
        # Botón Modificar
        self.modificar_btn = ttk.Button(
            right_controls,
            text="Modificar",
            command=self._on_modificar_clicked,
            bootstyle="primary",
            width=button_width,
            state="disabled"
        )
        self.modificar_btn.pack(side="right", padx=(10, 0))
        
        # Botón Exportar
        self.export_btn = ttk.Button(
            right_controls,
            text="Exportar",
            command=self._on_export_clicked,
            bootstyle="primary",
            width=button_width,
            state="disabled"
        )
        self.export_btn.pack(side="right", padx=(10, 0))
        
        # Botón Autocarga
        self.autocarga_btn = ttk.Button(
            right_controls,
            text="Autocarga",
            command=self._on_autocarga_clicked,
            bootstyle="primary",
            width=button_width,
            state="disabled"
        )
        self.autocarga_btn.pack(side="right", padx=(10, 0))
        
        # Botón Reimprimir (al principio)
        self.reimprimir_btn = ttk.Button(
            right_controls,
            text="Reimprimir",
            command=self._on_reimprimir_clicked,
            bootstyle="primary",
            width=button_width,
            state="disabled"
        )
        self.reimprimir_btn.pack(side="right", padx=(10, 0))
    
    def _on_detalles_clicked(self):
        """Maneja el click en Detalles"""
        self.logger.info("Botón Detalles clickeado")
        if self.on_detalles_callback and self.selected_data:
            self.on_detalles_callback(self.selected_data)
    
    def _on_modificar_clicked(self):
        """Maneja el click en Modificar"""
        self.logger.info("Botón Modificar clickeado")
        if self.on_modificar_callback and self.selected_data:
            self.on_modificar_callback(self.selected_data)
    
    def _on_autocarga_clicked(self):
        """Maneja el click en Autocarga"""
        self.logger.info("Botón Autocarga clickeado")
        if self.on_autocarga_callback:
            self.on_autocarga_callback()
    
    def _on_reimprimir_clicked(self):
        """Maneja el click en Reimprimir"""
        self.logger.info("Botón Reimprimir clickeado")
        if self.on_reimprimir_callback and self.selected_data:
            self.on_reimprimir_callback(self.selected_data)
    
    def _on_toggle_cargada_clicked(self):
        """Maneja el toggle de estado cargada"""
        if self.on_toggle_cargada_callback and self.selected_data:
            folio_interno = self.selected_data.get('folio_interno')
            if folio_interno:
                self.on_toggle_cargada_callback(folio_interno)
    
    def _on_toggle_pagada_clicked(self):
        """Maneja el toggle de estado pagada"""
        if self.on_toggle_pagada_callback and self.selected_data:
            folio_interno = self.selected_data.get('folio_interno')
            if folio_interno:
                self.on_toggle_pagada_callback(folio_interno)
    
    def _on_abrir_xml_clicked(self):
        """Maneja el click en Abrir XML"""
        if self.on_abrir_xml_callback and self.selected_data:
            self.on_abrir_xml_callback(self.selected_data)
    
    def _on_abrir_pdf_clicked(self):
        """Maneja el click en Abrir PDF"""
        if self.on_abrir_pdf_callback and self.selected_data:
            self.on_abrir_pdf_callback(self.selected_data)
    
    def _on_export_clicked(self):
        """Maneja el click en Exportar"""
        if self.on_export_callback:
            self.on_export_callback()
    
    def _on_cheque_clicked(self):
        """Maneja el click en Cheque"""
        self.logger.info("Botón Cheque clickeado")
        if self.on_cheque_callback:
            self.on_cheque_callback()
    
    def set_selected_data(self, data):
        """
        Establece los datos del elemento seleccionado
        
        Args:
            data: Datos del elemento seleccionado o None si no hay selección
        """
        self.selected_data = data
        self._update_buttons_state(data is not None)
        
        # Actualizar texto de botones según el estado actual
        if data:
            self._update_button_texts(data)
    
    def _update_buttons_state(self, enabled: bool):
        """
        Actualiza el estado habilitado/deshabilitado de los botones
        
        Args:
            enabled: True para habilitar, False para deshabilitar
        """
        buttons_que_requieren_seleccion = [
            self.reimprimir_btn,
            self.autocarga_btn,
            self.export_btn,
            self.modificar_btn,
            self.detalles_btn,
            self.toggle_cargada_btn,
            self.cheque_btn
        ]
        
        state = "normal" if enabled else "disabled"
        for button in buttons_que_requieren_seleccion:
            button.config(state=state)
    
    def _update_button_texts(self, data):
        """
        Actualiza el texto de los botones según el estado actual
        
        Args:
            data: Datos del elemento seleccionado
        """
        # Actualizar texto de botón cargada según el estado
        if hasattr(data, 'cargada') and data.cargada:
            self.toggle_cargada_btn.config(text="Cargado")
        else:
            self.toggle_cargada_btn.config(text="Cargado")
    
    def update_selection(self, data):
        """
        Alias para set_selected_data para compatibilidad
        
        Args:
            data: Datos del elemento seleccionado o None si no hay selección
        """
        self.set_selected_data(data)
    
    def update_display(self):
        """Actualiza la visualización del frame"""
        # Método para futuras actualizaciones si es necesario
        pass
    
    def set_callbacks(self, **callbacks):
        """
        Permite establecer callbacks después de la inicialización
        
        Args:
            **callbacks: Diccionario con los callbacks a establecer
        """
        for name, callback in callbacks.items():
            callback_attr = f"on_{name}_callback"
            if hasattr(self, callback_attr):
                setattr(self, callback_attr, callback)