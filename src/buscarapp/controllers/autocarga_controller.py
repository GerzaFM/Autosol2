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
    def _procesar_orden_individual(self, orden_data: Dict, contadores: Dict):
        """Procesa una orden individual para guardar en la BD y asociar con factura"""
        try:
            from bd.models import OrdenCompra, Factura, Proveedor
            from datetime import date
            
            self.logger.info(f"🔍 Procesando orden: {orden_data.get('archivo_original', 'Sin nombre')}")
            
            # Extraer datos de la orden
            ref_movimiento = orden_data.get('Ref_Movimiento', '')
            cuenta_str = orden_data.get('Cuenta', '')
            nombre = orden_data.get('Nombre', '')
            importe_str = orden_data.get('Importe', '0')
            importe_letras = orden_data.get('Importe_en_letras', '')
            codigo_banco = orden_data.get('Codigo_Banco', '')
            folio_factura = orden_data.get('Folio_Factura', '')
            archivo_original = orden_data.get('archivo_original', '')
            cuentas_mayores = orden_data.get('cuentas_mayores', None)
            
            # Validar datos esenciales
            if not ref_movimiento or not cuenta_str or not nombre:
                self.logger.warning(f"Orden incompleta - faltan datos esenciales: {orden_data}")
                contadores['errores'] = contadores.get('errores', 0) + 1
                return
                
            # Convertir tipos
            try:
                cuenta = int(cuenta_str) if cuenta_str.isdigit() else 0
                importe = float(importe_str.replace(',', '')) if importe_str else 0.0
            except (ValueError, AttributeError):
                self.logger.warning(f"Error convirtiendo datos numéricos para orden: {orden_data}")
                cuenta = 0
                importe = 0.0
                
            # Procesar cuentas mayores (ahora es un string directo)
            cuenta_mayor = None
            if cuentas_mayores:
                if isinstance(cuentas_mayores, str) and cuentas_mayores.isdigit():
                    cuenta_mayor = int(cuentas_mayores)
                elif isinstance(cuentas_mayores, int):
                    cuenta_mayor = cuentas_mayores
                elif isinstance(cuentas_mayores, (tuple, list)) and len(cuentas_mayores) > 0:
                    # Compatibilidad con formato anterior (por si acaso)
                    cuenta_mayor = int(cuentas_mayores[0]) if str(cuentas_mayores[0]).isdigit() else None
                    
            if cuenta_mayor:
                self.logger.info(f"💼 Cuenta mayor encontrada: {cuenta_mayor}")
            
            # Verificar si la orden ya existe (evitar duplicados)
            orden_existente = OrdenCompra.get_or_none(
                OrdenCompra.ref_movimiento == ref_movimiento,
                OrdenCompra.cuenta == cuenta
            )
            
            if orden_existente:
                self.logger.info(f"Orden ya existe: {ref_movimiento} - {cuenta}")
                return
            
            # Buscar asociación usando cuenta/fecha → vale → factura
            factura_asociada = None
            
            try:
                # Estrategia simplificada: cuenta (codigo_quiter) + proveedor + importe → factura
                orden_data = {
                    'cuenta': str(cuenta),
                    'fecha': None,  # No necesitamos fecha para esta estrategia
                    'importe_total': float(importe)
                }
                factura_asociada = self._buscar_factura_por_asociacion_inteligente(orden_data)
                
                if factura_asociada:
                    self.logger.info(f"✅ Factura encontrada por cuenta/proveedor: {factura_asociada.serie}-{factura_asociada.folio}")
                else:
                    self.logger.info(f"❌ No se encontró factura para cuenta {cuenta} y proveedor {nombre}")
                    
            except Exception as e:
                self.logger.error(f"Error en búsqueda de asociación: {e}")
            
            # Crear la orden en la BD
            nueva_orden = OrdenCompra.create(
                ref_movimiento=ref_movimiento,
                cuenta=cuenta,
                nombre=nombre,
                referencia=int(ref_movimiento) if ref_movimiento.isdigit() else 0,  # Campo requerido
                fecha=date.today(),  # Campo requerido
                importe=importe,
                importe_en_letras=importe_letras,
                codigo_banco=codigo_banco,
                folio_factura=folio_factura,
                archivo_original=archivo_original,
                fecha_procesamiento=date.today(),
                cuenta_mayor=cuenta_mayor,  # Agregar la cuenta mayor extraída del PDF
                factura=factura_asociada  # Asociar con la factura si se encontró
            )
            
            # Actualizar cuenta_mayor del proveedor y factura si no la tienen
            if cuenta_mayor:
                proveedor_para_actualizar = None
                
                # Caso 1: Hay factura asociada, usar su proveedor
                if factura_asociada and factura_asociada.proveedor:
                    proveedor_para_actualizar = factura_asociada.proveedor
                    self.logger.info(f"🔗 Usando proveedor de factura asociada: {proveedor_para_actualizar.nombre}")
                    
                    # Actualizar cuenta_mayor de la factura si no la tiene
                    if not factura_asociada.cuenta_mayor:
                        factura_asociada.cuenta_mayor = cuenta_mayor
                        factura_asociada.save()
                        self.logger.info(f"📄 Factura {factura_asociada.serie}-{factura_asociada.folio} actualizada con cuenta mayor: {cuenta_mayor}")
                    else:
                        self.logger.info(f"📄 Factura {factura_asociada.serie}-{factura_asociada.folio} ya tiene cuenta mayor: {factura_asociada.cuenta_mayor}")
                
                # Caso 2: No hay factura asociada, buscar proveedor por cuenta o nombre
                else:
                    proveedor_para_actualizar = self._buscar_proveedor_para_cuenta_mayor(cuenta, nombre)
                    if proveedor_para_actualizar:
                        self.logger.info(f"🔍 Proveedor encontrado por búsqueda: {proveedor_para_actualizar.nombre}")
                
                # Actualizar cuenta mayor del proveedor si encontramos uno
                if proveedor_para_actualizar:
                    self._actualizar_cuenta_mayor_proveedor(proveedor_para_actualizar, cuenta_mayor, nueva_orden.id)
                else:
                    self.logger.info(f"ℹ️ No se pudo determinar el proveedor para actualizar cuenta mayor {cuenta_mayor}")
            
            contadores['ordenes_creadas'] = contadores.get('ordenes_creadas', 0) + 1
            
            if factura_asociada:
                contadores['ordenes_asociadas'] = contadores.get('ordenes_asociadas', 0) + 1
                mensaje_cuenta_mayor = f" (Cuenta Mayor: {cuenta_mayor})" if cuenta_mayor else ""
                self.logger.info(f"✅ Orden creada y asociada: ID {nueva_orden.id} → Factura {factura_asociada.serie}-{factura_asociada.folio}{mensaje_cuenta_mayor}")
            else:
                contadores['ordenes_sin_asociar'] = contadores.get('ordenes_sin_asociar', 0) + 1
                mensaje_cuenta_mayor = f" (Cuenta Mayor: {cuenta_mayor})" if cuenta_mayor else ""
                self.logger.info(f"✅ Orden creada sin asociar: ID {nueva_orden.id}{mensaje_cuenta_mayor}")
                
        except Exception as e:
            self.logger.error(f"Error procesando orden individual: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            contadores['errores'] = contadores.get('errores', 0) + 1

    def _buscar_asociacion_cuenta_proveedor(self, cuenta: int, nombre_proveedor: str, importe: float, fecha_orden=None):
        """
        Busca asociación usando cuenta + proveedor + importe.
        
        Estrategia simplificada:
        1. Buscar vales por cuenta (y opcionalmente fecha)
        2. De esos vales, buscar facturas por proveedor + importe similar
        3. Devolver la mejor coincidencia
        
        Args:
            cuenta (int): Cuenta del proveedor
            nombre_proveedor (str): Nombre del proveedor  
            importe (float): Importe de la orden
            fecha_orden (date, optional): Fecha de la orden
            
        Returns:
            tuple: (Factura, Vale) o (None, None) si no hay coincidencia
        """
        try:
            from bd.models import Factura, Proveedor, Vale
        except ImportError:
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
            from src.bd.models import Factura, Proveedor, Vale
            
        self.logger.info(f"🔍 Búsqueda por cuenta/proveedor: cuenta={cuenta}, proveedor='{nombre_proveedor}', importe=${importe:,.2f}")
        
        # ESTRATEGIA 1: Buscar por proveedor + importe similar
        # Normalizar nombre del proveedor (quitar SADECV, espacios, etc.)
        nombre_limpio = nombre_proveedor.upper().replace('SADECV', '').replace('S.A.DE C.V.', '').replace('SADECV', '').strip()
        
        # Buscar proveedores similares
        proveedores_candidatos = Proveedor.select().where(
            (Proveedor.nombre.contains(nombre_limpio[:15])) |  # Primeros 15 caracteres
            (Proveedor.nombre.contains(nombre_limpio.split()[0])) |  # Primera palabra
            (Proveedor.cuenta == str(cuenta))  # Por cuenta
        )
        
        self.logger.info(f"  📋 Encontrados {proveedores_candidatos.count()} proveedores candidatos")
        
        mejor_factura = None
        mejor_vale = None
        mejor_puntuacion = 0
        
        for proveedor in proveedores_candidatos:
            self.logger.info(f"  🔍 Verificando proveedor: {proveedor.nombre}")
            
            # Buscar facturas de este proveedor con importe similar (±10%)
            tolerancia = importe * 0.1  # 10% de tolerancia
            facturas_proveedor = Factura.select().where(
                (Factura.proveedor == proveedor) &
                (Factura.total >= importe - tolerancia) &
                (Factura.total <= importe + tolerancia)
            )
            
            for factura in facturas_proveedor:
                diferencia_importe = abs(float(factura.total) - importe)
                
                # Calcular puntuación (menor diferencia = mejor puntuación)
                if diferencia_importe == 0:
                    puntuacion = 100  # Coincidencia exacta
                elif diferencia_importe < tolerancia:
                    puntuacion = 90 - (diferencia_importe / tolerancia * 20)  # 70-90 puntos
                else:
                    continue  # Fuera de tolerancia
                
                # Bonus por coincidencia de nombre
                if nombre_limpio[:10] in proveedor.nombre.upper():
                    puntuacion += 10
                    
                self.logger.info(f"    💰 Factura {factura.serie}-{factura.folio}: ${factura.total:,.2f} (dif: ${diferencia_importe:,.2f}, puntos: {puntuacion:.1f})")
                
                if puntuacion > mejor_puntuacion:
                    mejor_puntuacion = puntuacion
                    mejor_factura = factura
                    
                    # Buscar vale asociado a esta factura (opcional)
                    vale_asociado = Vale.get_or_none(Vale.factura == factura)
                    if vale_asociado:
                        mejor_vale = vale_asociado
                        puntuacion += 5  # Bonus por tener vale
                        self.logger.info(f"      📄 Vale asociado: {vale_asociado.numero}")
        
        # ESTRATEGIA 2: Si no hay coincidencia directa, buscar por cuenta en vales
        if not mejor_factura:
            self.logger.info(f"  🔄 Estrategia alternativa: buscar vales por cuenta {cuenta}")
            
            # Buscar vales que podrían corresponder a esta cuenta
            # (esto es más especulativo, pero puede ayudar)
            vales_cuenta = Vale.select().join(Factura).join(Proveedor).where(
                Proveedor.cuenta.contains(str(cuenta)[-4:])  # Últimos 4 dígitos de cuenta
            )
            
            for vale in vales_cuenta:
                if vale.factura:
                    diferencia_importe = abs(float(vale.factura.total) - importe)
                    if diferencia_importe < importe * 0.15:  # 15% de tolerancia más amplia
                        puntuacion = 60 - (diferencia_importe / (importe * 0.15) * 10)
                        
                        self.logger.info(f"    🎫 Vale {vale.numero} → Factura {vale.factura.serie}-{vale.factura.folio}: ${vale.factura.total:,.2f} (puntos: {puntuacion:.1f})")
                        
                        if puntuacion > mejor_puntuacion:
                            mejor_puntuacion = puntuacion
                            mejor_factura = vale.factura
                            mejor_vale = vale
        
        # Resultado final
        if mejor_factura:
            self.logger.info(f"✅ Mejor coincidencia: {mejor_factura.serie}-{mejor_factura.folio} (puntuación: {mejor_puntuacion:.1f})")
            return mejor_factura, mejor_vale
        else:
            self.logger.info(f"❌ No se encontró coincidencia para cuenta {cuenta} y proveedor '{nombre_proveedor}'")
            return None, None

    def _mostrar_reporte_procesamiento(self, stats: Dict, contadores: Dict, facturas_seleccionadas: List[Dict[str, Any]] = None):
        """Muestra un reporte completo del procesamiento"""
        if getattr(self, 'reporte_mostrado', False):
            self.logger.info("El reporte ya fue mostrado, se omite ventana adicional.")
            return
        self.reporte_mostrado = True
        import ttkbootstrap as ttk
        # Crear ventana de reporte
        reporte_window = ttk.Toplevel(self.parent_widget)
        reporte_window.title("Reporte de Autocarga")
        reporte_window.geometry("700x550")
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
        facturas_info = ""
        if facturas_seleccionadas:
            facturas_info = f"""
🎯 FACTURAS SELECCIONADAS PARA ASOCIACIÓN:
• Total de facturas seleccionadas: {len(facturas_seleccionadas)}
• Folios seleccionados: {', '.join([str(f.get('serie_folio', 'N/A')) for f in facturas_seleccionadas[:5]])}{'...' if len(facturas_seleccionadas) > 5 else ''}
"""
        reporte_content = f"""
🚀 AUTOCARGA COMPLETADA
{'='*50}

📅 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{facturas_info}
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
• Vales asociados a facturas: {contadores['vales_asociados']}
• Vales sin asociar: {contadores['vales_sin_asociar']}
• Órdenes de compra creadas: {contadores.get('ordenes_creadas', 0)}
• Órdenes asociadas a facturas: {contadores.get('ordenes_asociadas', 0)}
• Órdenes sin asociar: {contadores.get('ordenes_sin_asociar', 0)}
• Facturas actualizadas: {contadores['facturas_actualizadas']}
• Errores durante procesamiento: {contadores['errores']}

✅ PROCESO COMPLETADO EXITOSAMENTE

💡 PRÓXIMOS PASOS:
• Revisa los datos importados en la aplicación principal
• Verifica que los vales estén correctamente asociados a las facturas seleccionadas
• Los vales sin asociar requieren revisión manual del No Documento vs Folio
• Solo se consideraron las facturas que estaban seleccionadas en la tabla
• Confirma que los proveedores tengan los códigos correctos
"""
        # Frame contenedor para el área de texto con scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill="both", expand=True, pady=(0, 20))
        # Crear área de texto y scrollbar dentro de text_frame
        reporte_text = ttk.Text(text_frame, wrap="word", height=20)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=reporte_text.yview)
        reporte_text.configure(yscrollcommand=scrollbar.set)
        reporte_text.pack(side="left", fill="both", expand=True, padx=(0, 5))
        scrollbar.pack(side="right", fill="y")
        # Insertar contenido después de crear el widget
        reporte_text.insert("1.0", reporte_content)
        reporte_text.config(state="disabled")
        # Frame separado para el botón (siempre visible en la parte inferior)
        botones_frame = ttk.Frame(main_frame)
        botones_frame.pack(fill="x", pady=(0, 0))
        ttk.Button(
            botones_frame,
            text="Cerrar",
            bootstyle="primary",
            command=reporte_window.destroy
        ).pack(pady=10)
        # Centrar ventana
        reporte_window.update_idletasks()
        x = reporte_window.master.winfo_x() + (reporte_window.master.winfo_width() // 2) - (reporte_window.winfo_width() // 2)
        y = reporte_window.master.winfo_y() + (reporte_window.master.winfo_height() // 2) - (reporte_window.winfo_height() // 2)
        reporte_window.geometry(f"+{x}+{y}")
    def _mostrar_barra_progreso(self, total_archivos):
        import ttkbootstrap as ttk
        progreso_window = ttk.Toplevel(self.parent_widget)
        progreso_window.title("Procesando archivos PDF...")
        progreso_window.geometry("400x120")
        progreso_window.transient(self.parent_widget)
        progreso_window.grab_set()

        # Centrar ventana en pantalla
        progreso_window.update_idletasks()
        w = progreso_window.winfo_width()
        h = progreso_window.winfo_height()
        ws = progreso_window.winfo_screenwidth()
        hs = progreso_window.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        progreso_window.geometry(f"400x120+{x}+{y}")

        # Detectar tema actual
        theme = str(ttk.Style().theme)
        if 'dark' in theme.lower():
            fg_color = '#FFFFFF'
        else:
            fg_color = '#222222'

        label = ttk.Label(progreso_window, text="Procesando archivos PDF...", font=("Segoe UI", 12, "bold"), bootstyle="light")
        label.pack(pady=(20, 10))
        label.configure(foreground=fg_color)

        barra = ttk.Progressbar(progreso_window, maximum=total_archivos, length=350, bootstyle="info-striped")
        barra.pack(pady=(0, 10))

        progreso_window.update_idletasks()
        return progreso_window, barra
    """Controlador que maneja la lógica de autocarga de facturas"""
    
    def __init__(self, bd_control=None, parent_widget=None):
        self.bd_control = bd_control
        self.parent_widget = parent_widget
        self.logger = logging.getLogger(__name__)
        self.dialog_utils = DialogUtils(parent_widget)
        self.reporte_mostrado = False  # Flag para evitar reportes múltiples
    
    def ejecutar_autocarga_con_configuracion(self, facturas_seleccionadas: List[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Ejecuta la autocarga después de solicitar configuración al usuario.
        
        Args:
            facturas_seleccionadas: Lista de facturas seleccionadas para asociación
        
        Returns:
            Tuple[bool, Dict]: (éxito, estadísticas)
        """
        try:
            # DEBUG: Agregar logging para diagnosticar el problema
            self.logger.info(f"🔍 DIAGNÓSTICO AUTOCARGA - Facturas recibidas: {len(facturas_seleccionadas) if facturas_seleccionadas else 0}")
            if facturas_seleccionadas:
                for i, factura in enumerate(facturas_seleccionadas):
                    self.logger.info(f"   📋 Factura {i+1}: {factura}")
                    # DEBUG ADICIONAL: Verificar campos específicos
                    serie_folio = factura.get('serie_folio', 'NO_ENCONTRADO')
                    folio_interno = factura.get('folio_interno', 'NO_ENCONTRADO')
                    self.logger.info(f"      🔍 serie_folio: '{serie_folio}', folio_interno: '{folio_interno}'")
            
            # Mostrar diálogo de configuración
            config = self._mostrar_dialogo_configuracion()
            if not config:
                self.logger.info("❌ Autocarga cancelada por el usuario")
                return False, {}
            
            self.logger.info(f"⚙️ Configuración de autocarga: {config}")
            
            # Crear instancia de AutoCarga
            autocarga = AutoCarga(
                ruta_carpeta=config['ruta_carpeta'],
                dias_atras=config['dias_atras']
            )

            # Buscar archivos para saber el total
            lista_vales, lista_ordenes = autocarga.buscar_archivos()
            total_archivos = len(lista_vales) + len(lista_ordenes)

            import threading
            progreso_window, barra = (None, None)
            resultado = {'vales': None, 'ordenes': None}
            if total_archivos > 0:
                progreso_window, barra = self._mostrar_barra_progreso(total_archivos)

                def progress_callback(idx, total):
                    if barra:
                        barra.after(0, barra.config, {'value': idx})

                def procesamiento():
                    self._mostrar_mensaje_progreso("Iniciando autocarga...")
                    self.logger.info("🚀 Ejecutando autocarga...")
                    vales, ordenes = autocarga.ejecutar_autocarga(progress_callback=progress_callback)
                    resultado['vales'] = vales
                    resultado['ordenes'] = ordenes
                    if progreso_window:
                        progreso_window.after(0, progreso_window.destroy)

                hilo = threading.Thread(target=procesamiento)
                hilo.start()
                progreso_window.wait_window()
                vales, ordenes = resultado['vales'], resultado['ordenes']
            else:
                self._mostrar_mensaje_progreso("Iniciando autocarga...")
                self.logger.info("🚀 Ejecutando autocarga...")
                vales, ordenes = autocarga.ejecutar_autocarga()

            self.logger.info(f"📊 Autocarga ejecutada - Vales: {len(vales) if vales else 0}, Órdenes: {len(ordenes) if ordenes else 0}")
            
            # Obtener estadísticas
            stats = autocarga.obtener_estadisticas()
            self.logger.info(f"📈 Estadísticas autocarga: {stats}")
            
            # Procesar resultados para llenar BD
            if self.bd_control:
                self.logger.info("💾 Procesando resultados a base de datos...")
                self._procesar_resultados_a_bd(vales, ordenes, stats, facturas_seleccionadas)
            else:
                self.logger.warning("⚠️ Sin conexión a BD - No se procesarán resultados")
            
            return True, stats
            
        except Exception as e:
            self.logger.error(f"❌ Error en autocarga: {e}")
            import traceback
            self.logger.error(f"📍 Traceback completo: {traceback.format_exc()}")
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
        config_window.geometry("500x480")
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
        
        dias_var = ttk.IntVar(value=1)
        dias_frame = ttk.Frame(periodo_frame)
        dias_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Scale(
            dias_frame,
            from_=1,
            to=30,
            variable=dias_var,
            orient="horizontal"
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        dias_label = ttk.Label(dias_frame, text="1 día")
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
    
    def _procesar_resultados_a_bd(self, vales: Dict, ordenes: Dict, stats: Dict, facturas_seleccionadas: List[Dict[str, Any]] = None):
        """
        Procesa los resultados de la autocarga para llenar la base de datos.
        
        Args:
            vales: Datos de vales extraídos
            ordenes: Datos de órdenes extraídas
            stats: Estadísticas del procesamiento
            facturas_seleccionadas: Lista de facturas seleccionadas para asociación
        """
        try:
            from bd.models import Factura, Proveedor, Vale, Concepto
            
            # Contadores para el reporte
            contadores = {
                'proveedores_actualizados': 0,
                'vales_creados': 0,
                'vales_asociados': 0,
                'vales_sin_asociar': 0,
                'facturas_actualizadas': 0,
                'errores': 0
            }
            
            # Procesar vales
            for vale_id, vale_data in vales.items():
                try:
                    self._procesar_vale_individual(vale_data, contadores, facturas_seleccionadas)
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
            self._mostrar_reporte_procesamiento(stats, contadores, facturas_seleccionadas)
            
        except Exception as e:
            self.logger.error(f"Error procesando resultados a BD: {e}")
            self.dialog_utils.show_error("Error procesando resultados", f"Error: {str(e)}")
    
    def _actualizar_codigo_proveedor(self, datos_procesados: Dict[str, Any]):
        """
        Actualiza el código_quiter del proveedor si no lo tiene y el vale incluye código.
        
        Args:
            datos_procesados: Datos del vale procesados que incluyen proveedor y código
        """
        try:
            # Import del modelo Proveedor
            import sys
            src_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            sys.path.insert(0, src_path)
            from bd.models import Proveedor
            
            nombre_proveedor = datos_procesados.get('proveedor')
            codigo_vale = datos_procesados.get('codigo')
            
            # Solo proceder si tenemos tanto proveedor como código
            if not nombre_proveedor or not codigo_vale:
                return
            
            # Buscar el proveedor por nombre
            try:
                # Búsqueda exacta primero
                proveedor = Proveedor.get(Proveedor.nombre == nombre_proveedor)
            except Proveedor.DoesNotExist:
                # Búsqueda parcial si no hay coincidencia exacta
                try:
                    proveedor = Proveedor.get(Proveedor.nombre.contains(nombre_proveedor))
                except Proveedor.DoesNotExist:
                    # Búsqueda avanzada para casos como "MX SADECV" -> "OLEKSEI-MX SA DE CV"
                    try:
                        # Extraer palabras clave del nombre del vale
                        palabras_vale = nombre_proveedor.upper().split()
                        self.logger.debug(f"🔍 Palabras del vale: {palabras_vale}")
                        
                        # Buscar proveedor que contenga alguna de las palabras clave
                        proveedor_encontrado = None
                        for palabra in palabras_vale:
                            if len(palabra) >= 2:  # Solo palabras de 2+ caracteres
                                try:
                                    proveedor_candidato = Proveedor.get(Proveedor.nombre.contains(palabra))
                                    self.logger.debug(f"✅ Encontrado candidato '{proveedor_candidato.nombre}' con palabra '{palabra}'")
                                    proveedor_encontrado = proveedor_candidato
                                    break
                                except Proveedor.DoesNotExist:
                                    continue
                        
                        if proveedor_encontrado:
                            proveedor = proveedor_encontrado
                            self.logger.info(f"🔄 Coincidencia avanzada: Vale '{nombre_proveedor}' -> Proveedor '{proveedor.nombre}'")
                        else:
                            raise Proveedor.DoesNotExist()
                            
                    except Proveedor.DoesNotExist:
                        self.logger.debug(f"📋 Proveedor '{nombre_proveedor}' no encontrado en BD para actualizar código")
                        return
            
            # Verificar si el proveedor ya tiene código
            if proveedor.codigo_quiter is None or proveedor.codigo_quiter == '':
                # Actualizar el código del proveedor
                proveedor.codigo_quiter = codigo_vale
                proveedor.save()
                self.logger.info(f"🔄 Código '{codigo_vale}' agregado al proveedor '{proveedor.nombre}'")
            else:
                # El proveedor ya tiene código
                if str(proveedor.codigo_quiter) != str(codigo_vale):
                    self.logger.warning(f"⚠️ Proveedor '{proveedor.nombre}' ya tiene código '{proveedor.codigo_quiter}', pero vale tiene '{codigo_vale}'")
                else:
                    self.logger.debug(f"✅ Proveedor '{proveedor.nombre}' ya tiene el código correcto '{proveedor.codigo_quiter}'")
                    
        except Exception as e:
            self.logger.error(f"Error actualizando código del proveedor: {e}")
    
    def _procesar_vale_individual(self, vale_data: Dict, contadores: Dict, facturas_seleccionadas: List[Dict[str, Any]] = None):
        """Procesa un vale individual para actualizar la BD"""
        reporte_content = ""
        try:
            # Importar funciones de procesamiento
            try:
                from ..utils.procesar_datos_vale import procesar_datos_vale
            except ImportError:
                from utils.procesar_datos_vale import procesar_datos_vale

            import sys
            src_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            sys.path.insert(0, src_path)
            from bd.models import Vale, Factura

            def normalizar_documento(doc):
                """Normaliza un documento para comparación: elimina espacios y guiones"""
                return str(doc).replace(' ', '').replace('-', '').strip()

            def extraer_serie_folio(doc):
                """Extrae serie y folio de un documento en formato 'SERIE-FOLIO' o 'SERIE FOLIO'"""
                if '-' in doc:
                    partes = doc.split('-', 1)
                elif ' ' in doc:
                    partes = doc.split(' ', 1)
                else:
                    return None, None
                if len(partes) == 2:
                    return partes[0].strip(), partes[1].strip()
                return None, None

            def buscar_factura_asociada(no_documento, facturas_seleccionadas, nombre_vale=""):
                if not no_documento or not facturas_seleccionadas:
                    return None, None
                
                # Analizar el tipo de No Documento: ¿es "SERIE-FOLIO" o solo "FOLIO"?
                doc_serie, doc_folio = extraer_serie_folio(no_documento)
                doc_norm = normalizar_documento(no_documento)
                
                if doc_serie and doc_folio:
                    self.logger.debug(f"🔍 No Documento '{no_documento}' parece ser SERIE-FOLIO: serie='{doc_serie}', folio='{doc_folio}'")
                    es_serie_folio = True
                else:
                    self.logger.debug(f"🔍 No Documento '{no_documento}' parece ser solo FOLIO o formato desconocido")
                    es_serie_folio = False
                
                self.logger.debug(f"🔍 Buscando asociación para vale {nombre_vale}: No Documento '{no_documento}' (normalizado: '{doc_norm}')")
                self.logger.info(f"📊 DEBUGGING - Total facturas seleccionadas: {len(facturas_seleccionadas)}")
                
                for i, factura_data in enumerate(facturas_seleccionadas):
                    try:
                        # DEBUG: Mostrar datos completos de la factura
                        self.logger.debug(f"   🔍 FACTURA {i+1}: {factura_data}")
                        
                        # Obtener datos directamente del diccionario de factura
                        serie_folio = factura_data.get('serie_folio', '')
                        serie_original = factura_data.get('serie', '')
                        folio_original = factura_data.get('folio', '')
                        
                        # DEBUG: Mostrar valores RAW antes de procesamiento
                        self.logger.debug(f"   📋 Valores RAW: serie_folio='{serie_folio}', serie='{serie_original}', folio='{folio_original}'")
                        
                        # Si no tenemos serie y folio directamente, extraerlos del folio_xml
                        if not serie_original or not folio_original:
                            folio_xml = factura_data.get('folio_xml', '')
                            self.logger.debug(f"   🔄 Extrayendo de folio_xml: '{folio_xml}'")
                            if folio_xml and ' ' in folio_xml:
                                partes = folio_xml.split(' ', 1)
                                if len(partes) == 2:
                                    serie_original = partes[0].strip()
                                    try:
                                        folio_original = int(partes[1].strip())
                                    except ValueError:
                                        folio_original = partes[1].strip()
                                    self.logger.debug(f"   ✅ Extraído: serie='{serie_original}', folio='{folio_original}'")
                        
                        # Convertir a strings para evitar errores de tipo
                        serie_folio = str(serie_folio).strip() if serie_folio else ''
                        serie = str(serie_original).strip() if serie_original else ''
                        folio_str = str(folio_original).strip() if folio_original not in [None, ''] else ''
                        
                        # DEBUG: Mostrar valores procesados
                        self.logger.debug(f"   🎯 Valores PROCESADOS: serie_folio='{serie_folio}', serie='{serie}', folio_str='{folio_str}'")
                        
                        if not serie_folio:
                            self.logger.debug(f"   ⚠️ Saltando factura sin serie_folio")
                            continue
                        
                        self.logger.debug(f"   📋 Verificando factura: '{serie_folio}' - Serie: '{serie}', Folio: '{folio_str}'")
                        
                        # ===== CASO 1: No Documento es SERIE-FOLIO (ej: "A-123", "CFDI 456") =====
                        if es_serie_folio and doc_serie and doc_folio:
                            self.logger.debug(f"   🔍 CASO 1 - SERIE-FOLIO: Comparando doc_serie='{doc_serie}' con serie='{serie}' y doc_folio='{doc_folio}' con folio_str='{folio_str}'")
                            
                            # 1.1. Coincidencia exacta: serie y folio coinciden
                            if serie == doc_serie and folio_str == doc_folio:
                                self.logger.info(f"   ✅ Coincidencia exacta SERIE-FOLIO para vale {nombre_vale}: {doc_serie}-{doc_folio} = {serie}-{folio_str}")
                                try:
                                    if folio_str.isdigit():
                                        factura_asociada = Factura.get((Factura.serie == serie) & (Factura.folio == int(folio_str)))
                                        return factura_asociada, "serie_folio_exacto"
                                except Exception as e:
                                    self.logger.warning(f"   ❌ Error buscando factura en BD: {e}")
                                    continue
                            else:
                                self.logger.debug(f"   ❌ NO coincide exacto: serie '{serie}' != '{doc_serie}' O folio '{folio_str}' != '{doc_folio}'")
                            
                            # 1.2. Coincidencia normalizada: comparar serie_folio completo normalizado
                            serie_folio_norm = normalizar_documento(serie_folio)
                            self.logger.debug(f"   🔍 Comparando normalizado: '{serie_folio_norm}' vs '{doc_norm}'")
                            if serie_folio_norm == doc_norm:
                                self.logger.info(f"   ✅ Coincidencia normalizada SERIE-FOLIO para vale {nombre_vale}: '{serie_folio}' ~ '{no_documento}'")
                                try:
                                    if serie and folio_str and folio_str.isdigit():
                                        factura_asociada = Factura.get((Factura.serie == serie) & (Factura.folio == int(folio_str)))
                                        return factura_asociada, "serie_folio_normalizado"
                                except Exception as e:
                                    self.logger.warning(f"   ❌ Error buscando factura en BD: {e}")
                                    continue
                            else:
                                self.logger.debug(f"   ❌ NO coincide normalizado: '{serie_folio_norm}' != '{doc_norm}'")
                        
                        # ===== CASO 2: No Documento es solo FOLIO (ej: "123", "456") =====
                        else:
                            self.logger.debug(f"   🔍 CASO 2 - SOLO FOLIO: Comparando no_documento='{no_documento}' con folio_str='{folio_str}'")
                            
                            # 2.1. Coincidencia directa con folio
                            if folio_str and folio_str == no_documento:
                                self.logger.info(f"   ✅ Coincidencia exacta FOLIO para vale {nombre_vale}: folio '{folio_str}' = '{no_documento}'")
                                try:
                                    if folio_str.isdigit():
                                        # Buscar factura por folio (con o sin serie)
                                        if serie and serie.strip():
                                            # Caso: Factura con serie
                                            self.logger.debug(f"   🔍 Buscando en BD: serie='{serie}' AND folio={int(folio_str)}")
                                            factura_asociada = Factura.get((Factura.serie == serie) & (Factura.folio == int(folio_str)))
                                        else:
                                            # Caso: Factura sin serie (solo folio)
                                            self.logger.debug(f"   🔍 Buscando en BD: folio={int(folio_str)} (sin serie)")
                                            factura_asociada = Factura.get(Factura.folio == int(folio_str))
                                        
                                        self.logger.info(f"   🎯 FACTURA ENCONTRADA EN BD: {factura_asociada.serie}-{factura_asociada.folio}")
                                        return factura_asociada, "folio_exacto"
                                    else:
                                        self.logger.warning(f"   ❌ folio_str no es dígito: '{folio_str}'")
                                except Exception as e:
                                    self.logger.warning(f"   ❌ Error buscando factura en BD: {e}")
                                    self.logger.debug(f"   📍 Intentaba buscar: folio={int(folio_str) if folio_str.isdigit() else 'NO_DIGIT'}, serie='{serie}'")
                                    continue
                            else:
                                self.logger.debug(f"   ❌ NO coincide folio exacto: '{folio_str}' != '{no_documento}'")
                            
                            # 2.2. Coincidencia con serie_folio normalizado (por si el folio está dentro)
                            serie_folio_norm = normalizar_documento(serie_folio)
                            self.logger.debug(f"   🔍 Verificando si '{no_documento}' está en '{serie_folio_norm}' o termina con él")
                            if no_documento in serie_folio_norm or serie_folio_norm.endswith(no_documento):
                                self.logger.info(f"   ✅ Coincidencia FOLIO en serie_folio para vale {nombre_vale}: '{no_documento}' está en '{serie_folio}'")
                                try:
                                    if folio_str and folio_str.isdigit():
                                        # Buscar factura por folio (con o sin serie)
                                        if serie and serie.strip():
                                            # Caso: Factura con serie
                                            self.logger.debug(f"   🔍 Buscando en BD: serie='{serie}' AND folio={int(folio_str)}")
                                            factura_asociada = Factura.get((Factura.serie == serie) & (Factura.folio == int(folio_str)))
                                        else:
                                            # Caso: Factura sin serie (solo folio)
                                            self.logger.debug(f"   🔍 Buscando en BD: folio={int(folio_str)} (sin serie)")
                                            factura_asociada = Factura.get(Factura.folio == int(folio_str))
                                        
                                        self.logger.info(f"   🎯 FACTURA ENCONTRADA EN BD: {factura_asociada.serie}-{factura_asociada.folio}")
                                        return factura_asociada, "folio_en_serie_folio"
                                    else:
                                        self.logger.warning(f"   ❌ folio_str no es dígito: '{folio_str}'")
                                except Exception as e:
                                    self.logger.warning(f"   ❌ Error buscando factura en BD: {e}")
                                    self.logger.debug(f"   📍 Intentaba buscar: folio={int(folio_str) if folio_str.isdigit() else 'NO_DIGIT'}, serie='{serie}'")
                                    continue
                            else:
                                self.logger.debug(f"   ❌ NO está contenido: '{no_documento}' no está en '{serie_folio_norm}'")
                        
                        # ===== CASO 3: Coincidencias adicionales y fallback =====
                        
                        # 3.1. Coincidencia con serie (menos común, pero posible)
                        if serie and serie == no_documento:
                            self.logger.info(f"   ✅ Coincidencia por SERIE para vale {nombre_vale}: serie '{serie}' = '{no_documento}'")
                            try:
                                if folio_str and folio_str.isdigit():
                                    factura_asociada = Factura.get((Factura.serie == serie) & (Factura.folio == int(folio_str)))
                                    return factura_asociada, "serie_exacto"
                            except Exception as e:
                                self.logger.warning(f"   ❌ Error buscando factura en BD: {e}")
                                continue
                        
                        # 3.2. Coincidencia parcial general (último recurso)
                        serie_folio_norm = normalizar_documento(serie_folio)
                        if doc_norm and len(doc_norm) >= 3 and (doc_norm in serie_folio_norm or serie_folio_norm in doc_norm):
                            self.logger.info(f"   ✅ Coincidencia PARCIAL para vale {nombre_vale}: '{doc_norm}' <-> '{serie_folio_norm}'")
                            try:
                                if folio_str and folio_str.isdigit():
                                    # Buscar factura por folio (con o sin serie)
                                    if serie and serie.strip():
                                        # Caso: Factura con serie
                                        self.logger.debug(f"   🔍 Buscando en BD: serie='{serie}' AND folio={int(folio_str)}")
                                        factura_asociada = Factura.get((Factura.serie == serie) & (Factura.folio == int(folio_str)))
                                    else:
                                        # Caso: Factura sin serie (solo folio)
                                        self.logger.debug(f"   🔍 Buscando en BD: folio={int(folio_str)} (sin serie)")
                                        factura_asociada = Factura.get(Factura.folio == int(folio_str))
                                    
                                    self.logger.info(f"   🎯 FACTURA ENCONTrada EN BD: {factura_asociada.serie}-{factura_asociada.folio}")
                                    return factura_asociada, "parcial"
                                else:
                                    self.logger.warning(f"   ❌ folio_str no es dígito: '{folio_str}'")
                            except Exception as e:
                                self.logger.warning(f"   ❌ Error buscando factura en BD: {e}")
                                continue
                        
                        self.logger.debug(f"   ❌ Sin coincidencia: '{no_documento}' vs '{serie_folio}' (Serie: '{serie}', Folio: '{folio_str}')")
                    
                    except Exception as e:
                        self.logger.warning(f"   ❌ Error procesando factura {i}: {e}")
                        continue
                
                self.logger.info(f"   ⚠️ No se encontró coincidencia para No Documento '{no_documento}' entre {len(facturas_seleccionadas)} facturas")
                
                # DEBUG FINAL: Mostrar resumen de todas las facturas que se intentaron comparar
                self.logger.debug("📋 RESUMEN DE FACTURAS NO COINCIDENTES:")
                for i, factura_data in enumerate(facturas_seleccionadas):
                    serie_folio = str(factura_data.get('serie_folio', '')).strip()
                    serie = str(factura_data.get('serie', '')).strip()
                    folio = str(factura_data.get('folio', '')).strip()
                    self.logger.debug(f"   {i+1}. serie_folio='{serie_folio}', serie='{serie}', folio='{folio}'")
                
                return None, None

            datos_procesados = procesar_datos_vale(vale_data)
            try:
                vale_existente = Vale.get(Vale.noVale == datos_procesados['noVale'])
                self.logger.info(f"Vale {datos_procesados['noVale']} ya existe en BD")
                if facturas_seleccionadas and not vale_existente.factura:
                    self.logger.info(f"🔄 Vale {datos_procesados['noVale']} existe pero SIN ASOCIAR - intentando asociar con facturas seleccionadas")
                    no_documento = datos_procesados.get('noDocumento', '').strip()
                    factura_asociada, tipo_coincidencia = buscar_factura_asociada(no_documento, facturas_seleccionadas, datos_procesados['noVale'])
                    if factura_asociada:
                        try:
                            vale_existente.factura = factura_asociada
                            vale_existente.save()
                            contadores['vales_asociados'] += 1
                            self.logger.info(f"      ✅ Vale existente {datos_procesados['noVale']} ASOCIADO con {factura_asociada.serie}-{factura_asociada.folio}")
                        except Exception as e:
                            self.logger.error(f"      ❌ Error asociando vale existente: {e}")
                    else:
                        self.logger.info(f"      ⚠️ Vale existente {datos_procesados['noVale']} - No se encontró coincidencia con facturas seleccionadas")
                elif facturas_seleccionadas and vale_existente.factura:
                    self.logger.info(f"✅ Vale {datos_procesados['noVale']} ya existe y YA ESTÁ ASOCIADO con {vale_existente.factura.serie}-{vale_existente.factura.folio}")
                self._actualizar_codigo_proveedor(datos_procesados)
                return
            except Vale.DoesNotExist:
                pass
            no_documento = datos_procesados.get('noDocumento', '').strip()
            self.logger.debug(f"🔄 Procesando vale: {datos_procesados.get('noVale', 'SIN_NUMERO')}, No Documento: '{no_documento}'")
            factura_asociada, tipo_coincidencia = buscar_factura_asociada(no_documento, facturas_seleccionadas, datos_procesados['noVale'])
            if factura_asociada:
                self.logger.info(f"✅ Vale {datos_procesados['noVale']} será asociado con factura {factura_asociada.serie}-{factura_asociada.folio} (tipo: {tipo_coincidencia})")
            elif facturas_seleccionadas:
                self.logger.info(f"⚠️ Vale {datos_procesados['noVale']} - No Documento '{no_documento}' no coincide con ninguna factura seleccionada")
            else:
                self.logger.warning("No hay facturas seleccionadas para asociar vales")
            
            # Crear y guardar el vale
            try:
                # Actualizar proveedor con código si no lo tiene
                self._actualizar_codigo_proveedor(datos_procesados)
                
                # Crear el vale con los campos correctos del modelo
                nuevo_vale = Vale.create(
                    noVale=datos_procesados['noVale'],
                    tipo=datos_procesados.get('tipo', ''),
                    noDocumento=datos_procesados.get('noDocumento', ''),
                    descripcion=datos_procesados.get('descripcion', ''),
                    referencia=datos_procesados.get('referencia', 0),
                    total=datos_procesados.get('total', ''),
                    cuenta=datos_procesados.get('cuenta'),
                    fechaVale=datos_procesados.get('fechaVale'),
                    departamento=datos_procesados.get('departamento'),
                    sucursal=datos_procesados.get('sucursal'),
                    marca=datos_procesados.get('marca'),
                    responsable=datos_procesados.get('responsable'),
                    proveedor=datos_procesados.get('proveedor', ''),
                    codigo=datos_procesados.get('codigo', ''),
                    factura=factura_asociada  # Asociar con la factura encontrada (puede ser None)
                )
                
                if factura_asociada:
                    contadores['vales_asociados'] += 1
                    self.logger.info(f"✅ Vale {datos_procesados['noVale']} CREADO y ASOCIADO con factura {factura_asociada.serie}-{factura_asociada.folio}")
                else:
                    contadores['vales_sin_asociar'] += 1
                    self.logger.info(f"📝 Vale {datos_procesados['noVale']} CREADO sin asociar")
                
                contadores['vales_creados'] += 1
                
            except Exception as e:
                contadores['errores'] += 1
                self.logger.error(f"❌ Error creando vale {datos_procesados['noVale']}: {e}")
                
        except Exception as e:
            import traceback
            self.logger.error(f"❌ Error inesperado en _procesar_vale_individual: {e}")
            self.logger.error(traceback.format_exc())
            contadores['errores'] += 1

    def _buscar_factura_por_asociacion_inteligente(self, orden_data):
        """
        Busca facturas usando cuenta -> proveedor -> factura por importe
        Estrategia simplificada: cuenta=codigo_quiter, luego match por proveedor+importe
        """
        try:
            from bd.models import Factura, Proveedor
        except ImportError:
            from src.bd.models import Factura, Proveedor
            
        try:
            cuenta = orden_data.get('cuenta')
            fecha = orden_data.get('fecha')
            importe = orden_data.get('importe_total')
            
            if not cuenta or not importe:
                self.logger.info(f"❌ Faltan datos: cuenta={cuenta}, importe={importe}")
                return None
                
            # Buscar proveedor por codigo_quiter = cuenta
            proveedor = Proveedor.get_or_none(Proveedor.codigo_quiter == cuenta)
            if not proveedor:
                self.logger.info(f"❌ No se encontró proveedor con codigo_quiter: {cuenta}")
                return None
                
            self.logger.info(f"✅ Proveedor encontrado: {proveedor.nombre} (codigo_quiter: {cuenta})")
                
            # Buscar facturas del proveedor con el importe similar (tolerancia 5%)
            facturas = Factura.select().where(
                Factura.proveedor == proveedor,
                (Factura.total >= importe * 0.95) & (Factura.total <= importe * 1.05)
            )
            
            count = facturas.count()
            self.logger.info(f"🔍 Facturas encontradas con importe similar: {count}")
            
            if count == 1:
                factura = facturas.first()
                self.logger.info(f"✅ Factura única encontrada: {factura.serie}-{factura.folio} (${factura.total})")
                return factura
            elif count > 1:
                # Si hay múltiples, tomar la primera (podríamos usar fecha como criterio adicional)
                factura = facturas.first()
                self.logger.info(f"⚠️ Múltiples facturas encontradas, tomando la primera: {factura.serie}-{factura.folio}")
                return factura
            else:
                self.logger.info(f"❌ No se encontraron facturas del proveedor {proveedor.nombre} con importe ~${importe}")
                
        except Exception as e:
            self.logger.error(f"Error en asociación inteligente: {e}")
            
        return None

    def _actualizar_cuenta_mayor_proveedor(self, proveedor, cuenta_mayor, orden_id):
        """
        Actualiza la cuenta_mayor del proveedor si no la tiene asignada.
        
        Args:
            proveedor: Instancia del modelo Proveedor
            cuenta_mayor (int): Cuenta mayor extraída del PDF
            orden_id (int): ID de la orden de compra para logging
        """
        try:
            # Verificar si el proveedor ya tiene cuenta mayor
            if proveedor.cuenta_mayor is None or proveedor.cuenta_mayor == 0:
                # El proveedor no tiene cuenta mayor, asignar la nueva
                proveedor.cuenta_mayor = cuenta_mayor
                proveedor.save()
                
                self.logger.info(f"🏦 Cuenta mayor {cuenta_mayor} asignada al proveedor '{proveedor.nombre}' (desde orden ID: {orden_id})")
                
            else:
                # El proveedor ya tiene cuenta mayor
                if proveedor.cuenta_mayor == cuenta_mayor:
                    self.logger.info(f"✅ Proveedor '{proveedor.nombre}' ya tiene la cuenta mayor correcta: {cuenta_mayor}")
                else:
                    self.logger.warning(f"⚠️ Proveedor '{proveedor.nombre}' ya tiene cuenta mayor {proveedor.cuenta_mayor}, no se actualiza con {cuenta_mayor}")
                    
        except Exception as e:
            self.logger.error(f"❌ Error actualizando cuenta mayor del proveedor {proveedor.nombre}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")

    def _buscar_proveedor_para_cuenta_mayor(self, cuenta, nombre_proveedor):
        """
        Busca un proveedor para actualizar su cuenta mayor cuando no hay factura asociada.
        
        Args:
            cuenta (int): Código de cuenta del proveedor
            nombre_proveedor (str): Nombre del proveedor de la orden
            
        Returns:
            Proveedor: Instancia del proveedor encontrado o None
        """
        try:
            from bd.models import Proveedor
            
            # Estrategia 1: Buscar por codigo_quiter
            proveedor = Proveedor.get_or_none(Proveedor.codigo_quiter == cuenta)
            if proveedor:
                self.logger.info(f"✅ Proveedor encontrado por codigo_quiter {cuenta}: {proveedor.nombre}")
                return proveedor
            
            # Estrategia 2: Buscar por nombre (coincidencia parcial)
            nombre_limpio = nombre_proveedor.upper().replace('SADECV', '').replace('S.A.DE C.V.', '').strip()
            
            # Buscar coincidencia exacta primero
            proveedor = Proveedor.get_or_none(Proveedor.nombre == nombre_proveedor)
            if proveedor:
                self.logger.info(f"✅ Proveedor encontrado por nombre exacto: {proveedor.nombre}")
                return proveedor
            
            # Buscar coincidencia parcial
            proveedores_candidatos = Proveedor.select().where(
                (Proveedor.nombre.contains(nombre_limpio[:15])) |  # Primeros 15 caracteres
                (Proveedor.nombre.contains(nombre_limpio.split()[0]))  # Primera palabra
            )
            
            if proveedores_candidatos.count() == 1:
                proveedor = proveedores_candidatos.first()
                self.logger.info(f"✅ Proveedor encontrado por coincidencia parcial: {proveedor.nombre}")
                return proveedor
            elif proveedores_candidatos.count() > 1:
                # Si hay múltiples coincidencias, tomar el primero pero avisar
                proveedor = proveedores_candidatos.first()
                self.logger.warning(f"⚠️ Múltiples proveedores encontrados, tomando el primero: {proveedor.nombre}")
                return proveedor
            
            self.logger.info(f"❌ No se encontró proveedor para cuenta {cuenta} y nombre '{nombre_proveedor}'")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error buscando proveedor para cuenta mayor: {e}")
            return None
