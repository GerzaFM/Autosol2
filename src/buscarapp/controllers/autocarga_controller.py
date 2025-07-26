"""
Controlador para la funcionalidad de autocarga.
Maneja la integración entre el sistema de autocarga y la base de datos.
"""
import sys
import os
from typing import Dict, Any, List, Tuple, Optional
import logging
from datetime import datetime

# Agregar path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from ..utils.dialog_utils import DialogUtils
    from ..autocarga.autocarga import AutoCarga
    from ..autocarga.provider_matcher import ProviderMatcher
except ImportError:
    from utils.dialog_utils import DialogUtils
    from autocarga.autocarga import AutoCarga
    from autocarga.provider_matcher import ProviderMatcher


class AutocargaController:
    """Controlador que maneja la lógica de autocarga de facturas"""
    
    def __init__(self, bd_control=None, parent_widget=None):
        self.bd_control = bd_control
        self.parent_widget = parent_widget
        self.logger = logging.getLogger(__name__)
        self.dialog_utils = DialogUtils(parent_widget)
    
    def ejecutar_autocarga_con_configuracion(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Ejecuta la autocarga después de solicitar configuración al usuario.
        
        Returns:
            Tuple[bool, Dict]: (éxito, estadísticas)
        """
        try:
            # Mostrar diálogo de configuración
            config = self._mostrar_dialogo_configuracion()
            if not config:
                return False, {}
            
            # Crear instancia de AutoCarga
            autocarga = AutoCarga(
                ruta_carpeta=config['ruta_carpeta'],
                dias_atras=config['dias_atras']
            )
            
            # Mostrar progreso
            self._mostrar_mensaje_progreso("Iniciando autocarga...")
            
            # Ejecutar autocarga
            vales, ordenes = autocarga.ejecutar_autocarga()
            
            # Obtener estadísticas
            stats = autocarga.obtener_estadisticas()
            
            # Procesar resultados para llenar BD
            if self.bd_control:
                self._procesar_resultados_a_bd(vales, ordenes, stats)
            
            return True, stats
            
        except Exception as e:
            self.logger.error(f"Error en autocarga: {e}")
            self.dialog_utils.show_error("Error en Autocarga", f"Error durante la autocarga: {str(e)}")
            return False, {}
    
    def _mostrar_dialogo_configuracion(self) -> Optional[Dict[str, Any]]:
        """
        Muestra un diálogo para configurar la autocarga.
        
        Returns:
            Optional[Dict]: Configuración seleccionada o None si se cancela
        """
        import ttkbootstrap as ttk
        from tkinter import filedialog
        
        # Crear ventana de configuración
        config_window = ttk.Toplevel(self.parent_widget)
        config_window.title("Configuración de Autocarga")
        config_window.geometry("500x400")
        config_window.transient(self.parent_widget)
        config_window.grab_set()
        
        # Variables para almacenar la configuración
        config_result = {}
        
        # Frame principal
        main_frame = ttk.Frame(config_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título
        ttk.Label(
            main_frame,
            text="🚀 Configuración de Autocarga",
            font=("Segoe UI", 14, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Descripción
        desc_text = (
            "La autocarga buscará archivos PDF de vales y órdenes en la carpeta especificada "
            "y extraerá automáticamente los datos para llenar la base de datos."
        )
        ttk.Label(
            main_frame,
            text=desc_text,
            wraplength=450,
            justify="left"
        ).pack(pady=(0, 20))
        
        # Frame para ruta de carpeta
        ruta_frame = ttk.LabelFrame(main_frame, text="📂 Carpeta de Búsqueda", padding=10)
        ruta_frame.pack(fill="x", pady=(0, 15))
        
        ruta_var = ttk.StringVar(value=r"C:\QuiterWeb\cache")
        ruta_entry = ttk.Entry(ruta_frame, textvariable=ruta_var, width=50)
        ruta_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        def seleccionar_carpeta():
            carpeta = filedialog.askdirectory(
                title="Seleccionar carpeta de búsqueda",
                initialdir=ruta_var.get()
            )
            if carpeta:
                ruta_var.set(carpeta)
        
        ttk.Button(
            ruta_frame,
            text="Examinar...",
            bootstyle="outline-primary",
            command=seleccionar_carpeta
        ).pack(side="right")
        
        # Frame para período
        periodo_frame = ttk.LabelFrame(main_frame, text="📅 Período de Búsqueda", padding=10)
        periodo_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(periodo_frame, text="Buscar archivos modificados en los últimos:").pack(anchor="w")
        
        dias_var = ttk.IntVar(value=3)
        dias_frame = ttk.Frame(periodo_frame)
        dias_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Scale(
            dias_frame,
            from_=1,
            to=30,
            variable=dias_var,
            orient="horizontal"
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        dias_label = ttk.Label(dias_frame, text="3 días")
        dias_label.pack(side="right")
        
        def actualizar_dias_label(event=None):
            dias_label.config(text=f"{dias_var.get()} días")
        
        dias_var.trace('w', lambda *args: actualizar_dias_label())
        
        # Frame de opciones adicionales
        opciones_frame = ttk.LabelFrame(main_frame, text="⚙️ Opciones", padding=10)
        opciones_frame.pack(fill="x", pady=(0, 20))
        
        actualizar_proveedores_var = ttk.BooleanVar(value=True)
        ttk.Checkbutton(
            opciones_frame,
            text="Actualizar códigos de proveedores automáticamente",
            variable=actualizar_proveedores_var
        ).pack(anchor="w")
        
        crear_vale_automatico_var = ttk.BooleanVar(value=True)
        ttk.Checkbutton(
            opciones_frame,
            text="Crear registros de vales automáticamente",
            variable=crear_vale_automatico_var
        ).pack(anchor="w", pady=(5, 0))
        
        # Frame de botones
        botones_frame = ttk.Frame(main_frame)
        botones_frame.pack(fill="x", pady=(20, 0))
        
        resultado = [None]  # Lista para almacenar el resultado
        
        def aceptar():
            config_result.update({
                'ruta_carpeta': ruta_var.get(),
                'dias_atras': dias_var.get(),
                'actualizar_proveedores': actualizar_proveedores_var.get(),
                'crear_vale_automatico': crear_vale_automatico_var.get()
            })
            resultado[0] = config_result
            config_window.destroy()
        
        def cancelar():
            resultado[0] = None
            config_window.destroy()
        
        ttk.Button(
            botones_frame,
            text="Cancelar",
            bootstyle="outline-secondary",
            command=cancelar
        ).pack(side="right", padx=(10, 0))
        
        ttk.Button(
            botones_frame,
            text="Iniciar Autocarga",
            bootstyle="primary",
            command=aceptar
        ).pack(side="right")
        
        # Centrar ventana
        config_window.update_idletasks()
        x = config_window.master.winfo_x() + (config_window.master.winfo_width() // 2) - (config_window.winfo_width() // 2)
        y = config_window.master.winfo_y() + (config_window.master.winfo_height() // 2) - (config_window.winfo_height() // 2)
        config_window.geometry(f"+{x}+{y}")
        
        # Esperar hasta que se cierre la ventana
        config_window.wait_window()
        
        return resultado[0]
    
    def _mostrar_mensaje_progreso(self, mensaje: str):
        """Muestra un mensaje de progreso"""
        self.logger.info(mensaje)
    
    def _procesar_resultados_a_bd(self, vales: Dict, ordenes: Dict, stats: Dict):
        """
        Procesa los resultados de la autocarga para llenar la base de datos.
        
        Args:
            vales: Datos de vales extraídos
            ordenes: Datos de órdenes extraídas
            stats: Estadísticas del procesamiento
        """
        try:
            from bd.models import Factura, Proveedor, Vale, Concepto
            
            # Contadores para el reporte
            contadores = {
                'proveedores_actualizados': 0,
                'vales_creados': 0,
                'facturas_actualizadas': 0,
                'errores': 0
            }
            
            # Procesar vales
            for vale_id, vale_data in vales.items():
                try:
                    self._procesar_vale_individual(vale_data, contadores)
                except Exception as e:
                    self.logger.error(f"Error procesando vale {vale_id}: {e}")
                    contadores['errores'] += 1
            
            # Procesar órdenes
            for orden_id, orden_data in ordenes.items():
                try:
                    self._procesar_orden_individual(orden_data, contadores)
                except Exception as e:
                    self.logger.error(f"Error procesando orden {orden_id}: {e}")
                    contadores['errores'] += 1
            
            # Mostrar reporte final
            self._mostrar_reporte_procesamiento(stats, contadores)
            
        except Exception as e:
            self.logger.error(f"Error procesando resultados a BD: {e}")
            self.dialog_utils.show_error("Error procesando resultados", f"Error: {str(e)}")
    
    def _procesar_vale_individual(self, vale_data: Dict, contadores: Dict):
        """Procesa un vale individual para actualizar la BD"""
        from bd.models import Proveedor, Vale
        
        matcher = ProviderMatcher()
        
        # Buscar/actualizar proveedor
        proveedor, fue_actualizado = matcher.match_provider_from_vale_data(vale_data)
        
        if fue_actualizado:
            contadores['proveedores_actualizados'] += 1
        
        # Crear vale si no existe
        numero_vale = vale_data.get('Numero', '').replace('V', '')
        if numero_vale and proveedor:
            try:
                # Verificar si el vale ya existe
                vale_existente = Vale.get(Vale.noVale == numero_vale)
                self.logger.info(f"Vale {numero_vale} ya existe")
            except Vale.DoesNotExist:
                # Crear nuevo vale
                nuevo_vale = Vale.create(
                    noVale=numero_vale,
                    fechaVale=vale_data.get('Fecha', ''),
                    tipo=vale_data.get('TipodeVale', ''),
                    descripcion=f"Autocarga: {vale_data.get('Departamento', '')}",
                    total=vale_data.get('Total', 0),
                    proveedor=proveedor.id,
                    noDocumento=vale_data.get('NºDocumento', '')  # Agregar campo requerido
                )
                contadores['vales_creados'] += 1
                self.logger.info(f"Vale {numero_vale} creado automáticamente")
    
    def _procesar_orden_individual(self, orden_data: Dict, contadores: Dict):
        """Procesa una orden individual para actualizar la BD"""
        matcher = ProviderMatcher()
        
        # Buscar proveedor por nombre
        proveedor = matcher.match_provider_from_orden_data(orden_data)
        
        if proveedor:
            self.logger.info(f"Orden procesada para proveedor: {proveedor.nombre}")
        else:
            self.logger.warning(f"No se encontró proveedor para orden: {orden_data.get('Nombre', 'Sin nombre')}")
    
    def _mostrar_reporte_procesamiento(self, stats: Dict, contadores: Dict):
        """Muestra un reporte completo del procesamiento"""
        import ttkbootstrap as ttk
        
        # Crear ventana de reporte
        reporte_window = ttk.Toplevel(self.parent_widget)
        reporte_window.title("Reporte de Autocarga")
        reporte_window.geometry("600x500")
        reporte_window.transient(self.parent_widget)
        reporte_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(reporte_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título
        ttk.Label(
            main_frame,
            text="📊 Reporte de Autocarga Completada",
            font=("Segoe UI", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Crear texto del reporte
        reporte_text = ttk.Text(main_frame, wrap="word", height=20)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=reporte_text.yview)
        reporte_text.configure(yscrollcommand=scrollbar.set)
        
        # Contenido del reporte
        reporte_content = f"""
🚀 AUTOCARGA COMPLETADA
{"="*50}

📅 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📋 PROCESAMIENTO DE ARCHIVOS:
• Vales encontrados: {stats.get('vales_encontrados', 0)}
• Vales procesados exitosamente: {stats.get('vales_exitosos', 0)}
• Órdenes encontradas: {stats.get('ordenes_encontradas', 0)}
• Órdenes procesadas exitosamente: {stats.get('ordenes_exitosas', 0)}

🔍 COINCIDENCIAS DE PROVEEDORES:
"""
        
        if 'provider_matching' in stats:
            pm = stats['provider_matching']
            reporte_content += f"""• Vales con proveedor encontrado: {pm.get('vales_con_proveedor', 0)}
• Vales sin proveedor: {pm.get('vales_sin_proveedor', 0)}
• Órdenes con proveedor encontrado: {pm.get('ordenes_con_proveedor', 0)}
• Órdenes sin proveedor: {pm.get('ordenes_sin_proveedor', 0)}
"""
        
        reporte_content += f"""
🔄 ACTUALIZACIONES EN BASE DE DATOS:
• Proveedores actualizados con código: {contadores['proveedores_actualizados']}
• Vales creados automáticamente: {contadores['vales_creados']}
• Facturas actualizadas: {contadores['facturas_actualizadas']}
• Errores durante procesamiento: {contadores['errores']}

✅ PROCESO COMPLETADO EXITOSAMENTE

💡 PRÓXIMOS PASOS:
• Revisa los datos importados en la aplicación principal
• Verifica que los proveedores tengan los códigos correctos
• Confirma que los vales se han creado apropiadamente
"""
        
        reporte_text.insert("1.0", reporte_content)
        reporte_text.config(state="disabled")
        
        reporte_text.pack(side="left", fill="both", expand=True, padx=(0, 5))
        scrollbar.pack(side="right", fill="y")
        
        # Botón cerrar
        ttk.Button(
            main_frame,
            text="Cerrar",
            bootstyle="primary",
            command=reporte_window.destroy
        ).pack(pady=(20, 0))
        
        # Centrar ventana
        reporte_window.update_idletasks()
        x = reporte_window.master.winfo_x() + (reporte_window.master.winfo_width() // 2) - (reporte_window.winfo_width() // 2)
        y = reporte_window.master.winfo_y() + (reporte_window.master.winfo_height() // 2) - (reporte_window.winfo_height() // 2)
        reporte_window.geometry(f"+{x}+{y}")
