"""
Diálogo para asociación manual de facturas con vales.
Permite al usuario seleccionar un vale de la lista cuando una factura no pudo ser asociada automáticamente.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk_bootstrap
from ttkbootstrap.constants import *
from typing import Dict, List, Any, Optional, Tuple
import logging


class DialogoAsociacionManual:
    """
    Diálogo que muestra vales disponibles del mismo proveedor para asociación manual
    """
    
    def __init__(self, parent, vale_data: Dict, facturas_disponibles: List[Dict], titulo: str = "Asociación Manual"):
        """
        Inicializa el diálogo de asociación manual
        
        Args:
            parent: Ventana padre
            vale_data: Datos del vale que no pudo ser asociado
            facturas_disponibles: Lista de facturas del mismo proveedor disponibles
            titulo: Título del diálogo
        """
        self.parent = parent
        self.vale_data = vale_data
        self.facturas_disponibles = facturas_disponibles
        self.titulo = titulo
        
        # Resultado de la selección
        self.factura_seleccionada = None
        self.resultado = None  # 'asociar', 'omitir', 'cancelar'
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
        
        # Crear la ventana
        self._crear_ventana()
        
    def _crear_ventana(self):
        """Crea y configura la ventana del diálogo"""
        # Crear ventana modal
        self.ventana = tk.Toplevel(self.parent)
        self.ventana.title(self.titulo)
        self.ventana.transient(self.parent)
        self.ventana.grab_set()
        
        # Configurar tamaño y posición
        ancho = 900
        alto = 650  # Aumentado de 600 a 650 para dar más espacio a los botones
        
        # Centrar en la pantalla
        screen_width = self.ventana.winfo_screenwidth()
        screen_height = self.ventana.winfo_screenheight()
        x = (screen_width - ancho) // 2
        y = (screen_height - alto) // 2
        
        self.ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.ventana.resizable(True, True)
        
        # Crear contenido
        self._crear_contenido()
        
        # Enfocar el TreeView
        self.tree.focus_set()
        
        # Manejar cierre de ventana
        self.ventana.protocol("WM_DELETE_WINDOW", self._on_cancelar)
        
    def _crear_contenido(self):
        """Crea el contenido del diálogo"""
        # Frame principal
        main_frame = ttk.Frame(self.ventana, padding="10")
        main_frame.pack(fill=BOTH, expand=True)
        
        # Título y descripción
        titulo_label = ttk.Label(
            main_frame, 
            text="Asociación Manual de Vale con Factura",
            font=("Arial", 14, "bold")
        )
        titulo_label.pack(pady=(0, 10))
        
        # Información del vale
        self._crear_seccion_vale(main_frame)
        
        # Separador
        ttk.Separator(main_frame, orient=HORIZONTAL).pack(fill=X, pady=10)
        
        # Lista de facturas disponibles
        self._crear_seccion_facturas(main_frame)
        
        # Botones de acción
        self._crear_botones(main_frame)
        
    def _crear_seccion_vale(self, parent):
        """Crea la sección con información del vale"""
        vale_frame = ttk.LabelFrame(parent, text="Vale sin Asociar", padding="10")
        vale_frame.pack(fill=X, pady=(0, 10))
        
        # Grid para mostrar datos del vale
        info_frame = ttk.Frame(vale_frame)
        info_frame.pack(fill=X)
        
        # Configurar columnas
        info_frame.columnconfigure(1, weight=1)
        info_frame.columnconfigure(3, weight=1)
        
        row = 0
        
        # Folio Vale y No. Documento
        ttk.Label(info_frame, text="Folio Vale:").grid(row=row, column=0, sticky=W, padx=(0, 5))
        ttk.Label(info_frame, text=self.vale_data.get('folio_vale', 'N/A'), 
                 font=("Arial", 9, "bold")).grid(row=row, column=1, sticky=W, padx=(0, 20))
        
        ttk.Label(info_frame, text="No. Documento:").grid(row=row, column=2, sticky=W, padx=(0, 5))
        ttk.Label(info_frame, text=str(self.vale_data.get('no_documento', 'N/A')), 
                 font=("Arial", 9, "bold")).grid(row=row, column=3, sticky=W)
        
        row += 1
        
        # Proveedor y Total
        ttk.Label(info_frame, text="Proveedor:").grid(row=row, column=0, sticky=W, padx=(0, 5), pady=(5, 0))
        proveedor_text = self.vale_data.get('proveedor', 'N/A')
        if len(proveedor_text) > 30:
            proveedor_text = proveedor_text[:30] + "..."
        ttk.Label(info_frame, text=proveedor_text, 
                 font=("Arial", 9, "bold")).grid(row=row, column=1, sticky=W, padx=(0, 20), pady=(5, 0))
        
        ttk.Label(info_frame, text="Total:").grid(row=row, column=2, sticky=W, padx=(0, 5), pady=(5, 0))
        total = self.vale_data.get('total', 0)
        total_formatted = f"${total:,.2f}" if isinstance(total, (int, float)) else str(total)
        ttk.Label(info_frame, text=total_formatted, 
                 font=("Arial", 9, "bold")).grid(row=row, column=3, sticky=W, pady=(5, 0))
        
        # Descripción del problema
        problema_frame = ttk.Frame(vale_frame)
        problema_frame.pack(fill=X, pady=(10, 0))
        
        problema_label = ttk.Label(
            problema_frame,
            text="❌ Este vale no pudo ser asociado automáticamente. Seleccione una factura de la lista para asociar manualmente, o elija 'Omitir' para continuar sin asociar.",
            wraplength=800,
            foreground="red"
        )
        problema_label.pack()
        
    def _crear_seccion_facturas(self, parent):
        """Crea la sección con la lista de facturas disponibles"""
        facturas_frame = ttk.LabelFrame(parent, text=f"Facturas Disponibles del Mismo Proveedor ({len(self.facturas_disponibles)})", padding="10")
        facturas_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        if not self.facturas_disponibles:
            # No hay facturas disponibles
            no_facturas_label = ttk.Label(
                facturas_frame,
                text="⚠️ No hay facturas disponibles del mismo proveedor para asociar.",
                foreground="orange",
                font=("Arial", 10, "bold")
            )
            no_facturas_label.pack(pady=20)
            return
        
        # Crear TreeView
        tree_frame = ttk.Frame(facturas_frame)
        tree_frame.pack(fill=BOTH, expand=True)
        
        # Configurar columnas del TreeView
        columnas = ('serie', 'folio', 'total', 'fecha', 'estado')
        self.tree = ttk.Treeview(tree_frame, columns=columnas, show='headings', height=10)
        
        # Configurar encabezados
        self.tree.heading('serie', text='Serie')
        self.tree.heading('folio', text='Folio')
        self.tree.heading('total', text='Total')
        self.tree.heading('fecha', text='Fecha')
        self.tree.heading('estado', text='Estado')
        
        # Configurar anchos de columna
        self.tree.column('serie', width=100)
        self.tree.column('folio', width=100)
        self.tree.column('total', width=120)
        self.tree.column('fecha', width=100)
        self.tree.column('estado', width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Empaquetar TreeView y scrollbars usando pack
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        v_scrollbar.pack(side=RIGHT, fill=Y)
        
        tree_frame.pack(fill=BOTH, expand=True)
        
        # Llenar TreeView con datos
        self._llenar_treeview()
        
        # Bind doble click
        self.tree.bind('<Double-1>', self._on_doble_click)
        
        # Instrucciones
        instrucciones_label = ttk.Label(
            facturas_frame,
            text="💡 Doble click en una factura para asociarla, o seleccione una factura y presione 'Asociar'",
            foreground="blue"
        )
        instrucciones_label.pack(pady=(5, 0))
        
    def _llenar_treeview(self):
        """Llena el TreeView con los datos de las facturas"""
        for i, factura in enumerate(self.facturas_disponibles):
            # Formatear datos
            serie = factura.get('serie', 'N/A')
            folio = factura.get('folio', 'N/A')
            total = factura.get('total', 0)
            total_formatted = f"${total:,.2f}" if isinstance(total, (int, float)) else str(total)
            fecha = factura.get('fecha', 'N/A')
            estado = 'Disponible'  # Todas las facturas en esta lista están disponibles
            
            # Insertar fila
            item_id = self.tree.insert('', 'end', values=(
                serie,
                folio, 
                total_formatted,
                fecha,
                estado
            ), tags=(str(i),))  # Usar tags en lugar de column #0
            
    def _crear_botones(self, parent):
        """Crea los botones de acción"""
        botones_frame = ttk.Frame(parent)
        botones_frame.pack(fill=X, side=BOTTOM, pady=(10, 0))
        
        # Frame para centrar botones
        center_frame = ttk.Frame(botones_frame)
        center_frame.pack(expand=True)
        
        # Botón Asociar
        self.btn_asociar = ttk_bootstrap.Button(
            center_frame,
            text="Asociar Seleccionado",
            bootstyle=SUCCESS,
            command=self._on_asociar,
            width=18
        )
        self.btn_asociar.pack(side=LEFT, padx=(0, 10))
        
        # Botón Omitir
        self.btn_omitir = ttk_bootstrap.Button(
            center_frame,
            text="Omitir (Sin Asociar)",
            bootstyle=WARNING,
            command=self._on_omitir,
            width=18
        )
        self.btn_omitir.pack(side=LEFT, padx=(0, 10))
        
        # Botón Cancelar
        self.btn_cancelar = ttk_bootstrap.Button(
            center_frame,
            text="Cancelar Proceso",
            bootstyle=DANGER,
            command=self._on_cancelar,
            width=18
        )
        self.btn_cancelar.pack(side=LEFT)
        
        # Bind teclas
        self.ventana.bind('<Return>', lambda e: self._on_asociar())
        self.ventana.bind('<Escape>', lambda e: self._on_cancelar())
        
    def _on_doble_click(self, event):
        """Maneja el doble click en el TreeView"""
        self._on_asociar()
        
    def _on_asociar(self):
        """Maneja la acción de asociar"""
        seleccion = self.tree.selection()
        if not seleccion:
            tk.messagebox.showwarning(
                "Selección Requerida",
                "Por favor seleccione una factura de la lista para asociar."
            )
            return
            
        # Obtener la factura seleccionada
        item_id = seleccion[0]
        try:
            # Obtener el índice de la factura desde los tags
            tags = self.tree.item(item_id, 'tags')
            if tags:
                indice_factura = int(tags[0])
                self.factura_seleccionada = self.facturas_disponibles[indice_factura]
                self.resultado = 'asociar'
                
                self.logger.info(f"Usuario seleccionó factura para asociar: {self.factura_seleccionada.get('serie', 'N/A')}-{self.factura_seleccionada.get('folio', 'N/A')}")
                self.ventana.destroy()
            else:
                raise ValueError("No se encontraron tags en el item seleccionado")
                
        except (ValueError, IndexError) as e:
            self.logger.error(f"Error obteniendo factura seleccionada: {e}")
            tk.messagebox.showerror(
                "Error",
                "Error al obtener la factura seleccionada. Intente nuevamente."
            )
            
    def _on_omitir(self):
        """Maneja la acción de omitir"""
        self.resultado = 'omitir'
        self.factura_seleccionada = None
        self.logger.info("Usuario eligió omitir la asociación")
        self.ventana.destroy()
        
    def _on_cancelar(self):
        """Maneja la acción de cancelar"""
        self.resultado = 'cancelar'
        self.factura_seleccionada = None
        self.logger.info("Usuario canceló el diálogo de asociación")
        self.ventana.destroy()
        
    def mostrar(self) -> Tuple[Optional[Dict], str]:
        """
        Muestra el diálogo y espera la respuesta del usuario
        
        Returns:
            Tuple[Optional[Dict], str]: (factura_seleccionada, resultado)
                - factura_seleccionada: Datos de la factura seleccionada (None si no se seleccionó)
                - resultado: 'asociar', 'omitir', o 'cancelar'
        """
        # Esperar a que se cierre la ventana
        self.ventana.wait_window()
        
        return self.factura_seleccionada, self.resultado


# Función helper para usar el diálogo
def mostrar_dialogo_asociacion_manual(parent, vale_data: Dict, facturas_disponibles: List[Dict]) -> Tuple[Optional[Dict], str]:
    """
    Función helper para mostrar el diálogo de asociación manual
    
    Args:
        parent: Ventana padre
        vale_data: Datos del vale sin asociar
        facturas_disponibles: Lista de facturas disponibles del mismo proveedor
        
    Returns:
        Tuple[Optional[Dict], str]: (factura_seleccionada, resultado)
    """
    dialogo = DialogoAsociacionManual(parent, vale_data, facturas_disponibles)
    return dialogo.mostrar()
