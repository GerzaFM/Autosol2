"""
Vista para los paneles de información
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import Dict, Any, Optional, List
import logging


class InfoPanelsFrame:
    """Frame que contiene los paneles de información adicional"""
    
    def __init__(self, parent):
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        
        # Crear frame principal sin LabelFrame
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea todos los widgets del frame de información"""
        
        # Frame contenedor principal con grid para distribución proporcional
        main_info_frame = ttk.Frame(self.main_frame, padding=10)
        main_info_frame.pack(fill="both", expand=True)
        
        # Configurar grid para 3 columnas con pesos iguales (1/3 cada una)
        main_info_frame.columnconfigure(0, weight=1, minsize=250)  # Proveedor
        main_info_frame.columnconfigure(1, weight=1, minsize=250)  # Vale
        main_info_frame.columnconfigure(2, weight=1, minsize=250)  # Orden
        main_info_frame.rowconfigure(0, weight=1)
        
        # Evitar propagación del tamaño de los widgets hijos
        main_info_frame.grid_propagate(False)
        
        # Crear tres LabelFrames con grid layout
        
        # 1. Panel de Datos Proveedor
        self._create_proveedor_panel(main_info_frame)
        
        # 2. Panel de Vale
        self._create_vale_panel(main_info_frame)
        
        # 3. Panel de Orden de Compra
        self._create_orden_compra_panel(main_info_frame)
    
    def _create_proveedor_panel(self, parent):
        """Crea el panel de datos del proveedor"""
        proveedor_frame = ttk.LabelFrame(
            parent,
            text="Datos Proveedor",
            padding=10
        )
        proveedor_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Evitar que el frame se redimensione según su contenido
        proveedor_frame.pack_propagate(False)
        
        # Campos del proveedor
        self.proveedor_codigo_label = ttk.Label(
            proveedor_frame,
            text="Código: -",
            font=("Segoe UI", 10),
            anchor="w",
            wraplength=200
        )
        self.proveedor_codigo_label.pack(fill="x", pady=2)
        
        self.proveedor_nombre_label = ttk.Label(
            proveedor_frame,
            text="Nombre: -",
            font=("Segoe UI", 10),
            anchor="w",
            wraplength=200,
            justify="left"
        )
        self.proveedor_nombre_label.pack(fill="x", pady=2)
        
        self.proveedor_rfc_label = ttk.Label(
            proveedor_frame,
            text="RFC: -",
            font=("Segoe UI", 10),
            anchor="w",
            wraplength=200
        )
        self.proveedor_rfc_label.pack(fill="x", pady=2)
        
        self.proveedor_email_label = ttk.Label(
            proveedor_frame,
            text="Email: -",
            font=("Segoe UI", 10),
            anchor="w",
            wraplength=200
        )
        self.proveedor_email_label.pack(fill="x", pady=2)
    
    def _create_vale_panel(self, parent):
        """Crea el panel de información del vale"""
        vale_frame = ttk.LabelFrame(
            parent,
            text="Vale",
            padding=10
        )
        vale_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        
        # Evitar que el frame se redimensione según su contenido
        vale_frame.pack_propagate(False)
        
        # Campos del vale - expandidos para mostrar más información
        self.vale_no_label = ttk.Label(
            vale_frame,
            text="No Vale: -",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
            wraplength=200
        )
        self.vale_no_label.pack(fill="x", pady=2)
        
        self.vale_tipo_label = ttk.Label(
            vale_frame,
            text="Tipo: -",
            font=("Segoe UI", 10),
            anchor="w",
            wraplength=200
        )
        self.vale_tipo_label.pack(fill="x", pady=2)
        
        self.vale_total_label = ttk.Label(
            vale_frame,
            text="Total: -",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
            wraplength=200
        )
        self.vale_total_label.pack(fill="x", pady=2)
        
        self.vale_proveedor_label = ttk.Label(
            vale_frame,
            text="Proveedor: -",
            font=("Segoe UI", 10),
            anchor="w",
            wraplength=200
        )
        self.vale_proveedor_label.pack(fill="x", pady=2)
        
        self.vale_fecha_label = ttk.Label(
            vale_frame,
            text="Fecha: -",
            font=("Segoe UI", 10),
            anchor="w",
            wraplength=200
        )
        self.vale_fecha_label.pack(fill="x", pady=2)
        
        self.vale_referencia_label = ttk.Label(
            vale_frame,
            text="Referencia: -",
            font=("Segoe UI", 10),
            anchor="w",
            wraplength=200
        )
        self.vale_referencia_label.pack(fill="x", pady=2)
        
        self.vale_departamento_label = ttk.Label(
            vale_frame,
            text="Departamento: -",
            font=("Segoe UI", 10),
            anchor="w",
            wraplength=200
        )
        self.vale_departamento_label.pack(fill="x", pady=2)
        
        # Descripción como Label normal (sin bordes, igual que los otros labels)
        self.vale_descripcion_label = ttk.Label(
            vale_frame,
            text="Descripción: Sin información disponible",
            font=("Segoe UI", 10),
            anchor="nw",
            justify="left",
            wraplength=200  # Ajustado para 1/3 del ancho disponible
        )
        self.vale_descripcion_label.pack(fill="both", expand=True, pady=2)
    
    def _create_orden_compra_panel(self, parent):
        """Crea el panel de orden de compra"""
        orden_frame = ttk.LabelFrame(
            parent,
            text="Orden de Compra",
            padding=10
        )
        orden_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        
        # Evitar que el frame se redimensione según su contenido
        orden_frame.pack_propagate(False)
        
        # Campos de la orden
        self.orden_importe_label = ttk.Label(
            orden_frame,
            text="Importe: -",
            font=("Segoe UI", 10),
            anchor="w",
            wraplength=200
        )
        self.orden_importe_label.pack(fill="x", pady=2)
        
        self.orden_iva_label = ttk.Label(
            orden_frame,
            text="IVA: -",
            font=("Segoe UI", 10),
            anchor="w",
            wraplength=200
        )
        self.orden_iva_label.pack(fill="x", pady=2)
        
        self.orden_letras_label = ttk.Label(
            orden_frame,
            text="Importe en Letras: -",
            font=("Segoe UI", 10),
            anchor="w",
            wraplength=200
        )
        self.orden_letras_label.pack(fill="x", pady=2)
        
        self.orden_cuenta_label = ttk.Label(
            orden_frame,
            text="Cuenta Mayor: -",
            font=("Segoe UI", 10),
            anchor="w",
            wraplength=200
        )
        self.orden_cuenta_label.pack(fill="x", pady=2)
        
        self.orden_banco_label = ttk.Label(
            orden_frame,
            text="Banco Código: -",
            font=("Segoe UI", 10),
            anchor="w",
            wraplength=200
        )
        self.orden_banco_label.pack(fill="x", pady=2)
    
    def update_proveedor_info(self, proveedor_data: Dict[str, Any]):
        """
        Actualiza la información del proveedor
        
        Args:
            proveedor_data: Diccionario con los datos del proveedor
        """
        try:
            codigo = proveedor_data.get('codigo', '-')
            nombre = proveedor_data.get('nombre', '-')
            rfc = proveedor_data.get('rfc', '-')
            email = proveedor_data.get('email', '-')
            
            self.proveedor_codigo_label.config(text=f"Código: {codigo}")
            self.proveedor_nombre_label.config(text=f"Nombre: {nombre}")
            self.proveedor_rfc_label.config(text=f"RFC: {rfc}")
            self.proveedor_email_label.config(text=f"Email: {email}")
            
        except Exception as e:
            self.logger.error(f"Error actualizando información de proveedor: {e}")
    
    def update_vale_info(self, vale_data: Dict[str, Any]):
        """
        Actualiza la información del vale con todos los campos extraídos
        
        Args:
            vale_data: Diccionario con los datos del vale (ya procesados o directos del extractor)
        """
        try:
            # Verificar que vale_data no sea None
            if not vale_data:
                self._clear_vale_info()
                return
            
            # Determinar si los datos vienen del extractor (formato original) o de BD (procesados)
            # Los datos del extractor tienen claves como 'Numero', 'Nombre', etc.
            # Los datos de BD tienen claves como 'noVale', 'proveedor', etc.
            
            if 'Numero' in vale_data:  # Datos del extractor
                no_vale = vale_data.get('Numero', '-')
                tipo = vale_data.get('Tipo De Vale', '-')
                total = vale_data.get('Total', '-')
                proveedor = vale_data.get('Nombre', '-')
                fecha = vale_data.get('Fecha', '-')
                referencia = vale_data.get('Referencia', '-')
                departamento = vale_data.get('Departamento', '-')
                descripcion = vale_data.get('Descripcion', '-')
            else:  # Datos de BD (ya procesados)
                no_vale = vale_data.get('noVale', '-')
                tipo = vale_data.get('tipo', '-')
                total = vale_data.get('total', '-')
                proveedor = vale_data.get('proveedor', '-')
                fecha = vale_data.get('fechaVale', '-')
                referencia = vale_data.get('referencia', '-')
                departamento = vale_data.get('departamento', '-')
                descripcion = vale_data.get('descripcion', '-')
            
            # Actualizar los labels
            self.vale_no_label.config(text=f"No Vale: {no_vale}")
            self.vale_tipo_label.config(text=f"Tipo: {tipo}")
            
            # Formatear total si es numérico
            if total and total != '-':
                if isinstance(total, (int, float)):
                    total_text = f"${total:,.2f}"
                else:
                    total_text = f"${total}" if not str(total).startswith('$') else str(total)
            else:
                total_text = "-"
            self.vale_total_label.config(text=f"Total: {total_text}")
            
            self.vale_proveedor_label.config(text=f"Proveedor: {proveedor}")
            self.vale_fecha_label.config(text=f"Fecha: {fecha}")
            self.vale_referencia_label.config(text=f"Referencia: {referencia}")
            self.vale_departamento_label.config(text=f"Departamento: {departamento}")
            
            # Actualizar descripción en el label
            if descripcion and descripcion != '-':
                # Limitar la longitud si es muy larga
                if len(descripcion) > 200:
                    descripcion_mostrar = descripcion[:200] + "..."
                else:
                    descripcion_mostrar = descripcion
                self.vale_descripcion_label.config(text=f"Descripción: {descripcion_mostrar}")
            else:
                self.vale_descripcion_label.config(text="Descripción: Sin información disponible")
            
        except Exception as e:
            self.logger.error(f"Error actualizando información de vale: {e}")
            self._clear_vale_info()
    
    def _clear_vale_info(self):
        """Limpia toda la información del vale"""
        try:
            self.vale_no_label.config(text="No Vale: -")
            self.vale_tipo_label.config(text="Tipo: -")
            self.vale_total_label.config(text="Total: -")
            self.vale_proveedor_label.config(text="Proveedor: -")
            self.vale_fecha_label.config(text="Fecha: -")
            self.vale_referencia_label.config(text="Referencia: -")
            self.vale_departamento_label.config(text="Departamento: -")
            self.vale_descripcion_label.config(text="Descripción: Sin información disponible")
        except Exception as e:
            self.logger.error(f"Error limpiando información de vale: {e}")
    
    def update_orden_compra_info(self, orden_data: Dict[str, Any]):
        """
        Actualiza la información de la orden de compra
        
        Args:
            orden_data: Diccionario con los datos de la orden de compra
        """
        try:
            importe = orden_data.get('importe', '-')
            iva = orden_data.get('iva', '-')
            importe_letras = orden_data.get('importe_letras', '-')
            cuenta_mayor = orden_data.get('cuenta_mayor', '-')
            banco_codigo = orden_data.get('banco_codigo', '-')
            
            # Formatear importes si son numéricos
            if isinstance(importe, (int, float)):
                importe = f"${importe:,.2f}"
            if isinstance(iva, (int, float)):
                iva = f"${iva:,.2f}"
            
            self.orden_importe_label.config(text=f"Importe: {importe}")
            self.orden_iva_label.config(text=f"IVA: {iva}")
            self.orden_letras_label.config(text=f"Importe en Letras: {importe_letras}")
            self.orden_cuenta_label.config(text=f"Cuenta Mayor: {cuenta_mayor}")
            self.orden_banco_label.config(text=f"Banco Código: {banco_codigo}")
            
        except Exception as e:
            self.logger.error(f"Error actualizando información de orden de compra: {e}")
    
    def update_factura_info(self, factura_data: Dict[str, Any]):
        """
        Actualiza la información básica de la factura en los paneles disponibles
        
        Args:
            factura_data: Diccionario con los datos de la factura
        """
        try:
            # Verificar que factura_data no sea None
            if not factura_data:
                factura_data = {}
                
            # Actualizar información en el panel de vale si hay datos
            vale_info = {
                'no_vale': factura_data.get('no_vale', '-'),
                'tipo': factura_data.get('tipo', '-'),
                'folio_factura': factura_data.get('folio', '-')
            }
            self.update_vale_info(vale_info)
            
            # Actualizar información de orden de compra si hay datos
            orden_info = {
                'importe': factura_data.get('total', '-'),
                'iva': factura_data.get('iva_trasladado', '-'),
                'importe_letras': '-',
                'cuenta_mayor': '-',
                'banco_codigo': '-'
            }
            self.update_orden_compra_info(orden_info)
            
        except Exception as e:
            self.logger.error(f"Error actualizando información de factura: {e}")
    
    def update_conceptos_info(self, conceptos_data: List[Dict[str, Any]]):
        """
        Actualiza la información de conceptos (no se muestra en los 3 paneles actuales)
        Mantener compatibilidad con la interfaz existente
        
        Args:
            conceptos_data: Lista de diccionarios con los conceptos
        """
        # Los conceptos no se muestran en estos 3 paneles básicos
        # Se mantiene el método para compatibilidad pero no hace nada
        pass
    
    def update_estadisticas(self, all_facturas: List[Dict[str, Any]], filtered_facturas: List[Dict[str, Any]]):
        """
        Actualiza las estadísticas (no se muestran en los 3 paneles actuales)
        Mantener compatibilidad con la interfaz existente
        
        Args:
            all_facturas: Lista de todas las facturas
            filtered_facturas: Lista de facturas filtradas
        """
        # Las estadísticas no se muestran en estos 3 paneles básicos
        # Se mantiene el método para compatibilidad pero no hace nada
        pass
    
    def clear_all_info(self):
        """Limpia toda la información de los paneles"""
        try:
            # Limpiar panel de proveedor
            self.proveedor_codigo_label.config(text="Código: -")
            self.proveedor_nombre_label.config(text="Nombre: -")
            self.proveedor_rfc_label.config(text="RFC: -")
            self.proveedor_email_label.config(text="Email: -")
            
            # Limpiar panel de vale
            self.vale_no_label.config(text="No Vale: -")
            self.vale_tipo_label.config(text="Tipo: -")
            self.vale_total_label.config(text="Total: -")
            self.vale_proveedor_label.config(text="Proveedor: -")
            self.vale_fecha_label.config(text="Fecha: -")
            self.vale_referencia_label.config(text="Referencia: -")
            self.vale_departamento_label.config(text="Departamento: -")
            self.vale_descripcion_label.config(text="Descripción: Sin información disponible")
            
            # Limpiar panel de orden de compra
            self.orden_importe_label.config(text="Importe: -")
            self.orden_iva_label.config(text="IVA: -")
            self.orden_letras_label.config(text="Importe en Letras: -")
            self.orden_cuenta_label.config(text="Cuenta Mayor: -")
            self.orden_banco_label.config(text="Banco Código: -")
            
        except Exception as e:
            self.logger.error(f"Error limpiando información de paneles: {e}")
    
    def update_display(self):
        """Actualiza la visualización del frame"""
        # Método para futuras actualizaciones si es necesario
        pass
