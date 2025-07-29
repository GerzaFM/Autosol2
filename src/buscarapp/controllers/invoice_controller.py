"""
Controlador para la lógica de facturas
"""
import sys
import os
from typing import Dict, Any, Optional, List, Tuple
import logging
import traceback

# Agregar path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from ..utils.dialog_utils import DialogUtils
    from ..utils.format_utils import (
        format_folio, format_currency, format_comentario_factura, 
        format_tipo_vale
    )
except ImportError:
    from utils.dialog_utils import DialogUtils
    from utils.format_utils import (
        format_folio, format_currency, format_comentario_factura, 
        format_tipo_vale
    )


class InvoiceController:
    """Controlador que maneja la lógica de facturas"""
    
    def __init__(self, bd_control=None):
        self.bd_control = bd_control
        self.logger = logging.getLogger(__name__)
        self.dialog_utils = DialogUtils()
    
    def get_invoice_details(self, folio_interno: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles completos de una factura
        
        Args:
            folio_interno: Folio interno de la factura
            
        Returns:
            Dict con los detalles de la factura o None si no se encuentra
        """
        try:
            if not self.bd_control:
                self.logger.warning("Base de datos no disponible")
                return None
            
            from bd.models import Factura, Proveedor, Concepto, Vale, Reparto
            
            # Buscar la factura
            try:
                factura = (Factura
                          .select()
                          .join(Proveedor, on=(Factura.proveedor == Proveedor.id))
                          .where(Factura.folio_interno == folio_interno)
                          .get())
            except Factura.DoesNotExist:
                self.logger.warning(f"No se encontró la factura con folio interno: {folio_interno}")
                return None
            
            # Obtener conceptos
            conceptos = list(Concepto.select().where(Concepto.factura == factura.folio_interno))
            
            # Obtener vale (si existe)
            vale = None
            try:
                # Buscar vale directamente por factura_id
                vale = Vale.select().where(Vale.factura_id == factura.folio_interno).get()
            except Vale.DoesNotExist:
                self.logger.debug(f"No se encontró vale para la factura {folio_interno}")
                pass
            
            # Obtener repartimientos (si existen)
            repartimientos = list(Reparto.select().where(Reparto.factura == factura.folio_interno))
            
            # Construir diccionario de detalles
            details = {
                'factura': {
                    'folio_interno': factura.folio_interno,
                    'tipo': factura.tipo,
                    'no_vale': vale.noVale if vale else "",  # Obtener no_vale desde el vale relacionado
                    'fecha': factura.fecha if isinstance(factura.fecha, str) else factura.fecha.strftime('%Y-%m-%d') if factura.fecha else "",
                    'serie': factura.serie,
                    'folio': factura.folio,
                    'nombre_emisor': factura.nombre_emisor,
                    'rfc_emisor': factura.rfc_emisor,
                    'rfc_receptor': factura.rfc_receptor,
                    'nombre_receptor': factura.nombre_receptor,
                    'total': float(factura.total) if factura.total else 0.0,
                    'subtotal': float(factura.subtotal) if factura.subtotal else 0.0,
                    'iva_trasladado': float(factura.iva_trasladado) if factura.iva_trasladado else 0.0,
                    'ret_iva': float(factura.ret_iva) if factura.ret_iva else 0.0,
                    'ret_isr': float(factura.ret_isr) if factura.ret_isr else 0.0,
                    'clase': factura.clase,
                    'cargada': bool(factura.cargada),
                    'pagada': bool(factura.pagada),
                    'comentario': factura.comentario
                },
                'proveedor': {
                    'id': factura.proveedor.id,
                    'nombre': factura.proveedor.nombre,
                    'rfc': factura.proveedor.rfc,
                    'telefono': factura.proveedor.telefono,
                    'email': factura.proveedor.email,
                    'nombre_contacto': factura.proveedor.nombre_contacto,
                    'codigo': factura.proveedor.codigo_quiter  # Agregar código del proveedor
                },
                'conceptos': [
                    {
                        'id': c.id,
                        'cantidad': float(c.cantidad) if c.cantidad else 0.0,
                        'descripcion': c.descripcion,
                        'precio_unitario': float(c.precio_unitario) if c.precio_unitario else 0.0,  # Campo correcto
                        'total': float(c.total) if c.total else 0.0  # Campo correcto
                    }
                    for c in conceptos
                ],
                'vale': {
                    'noVale': vale.noVale,  # Campo correcto es noVale
                    'fechaVale': vale.fechaVale if isinstance(vale.fechaVale, str) else vale.fechaVale.strftime('%Y-%m-%d') if vale.fechaVale else "",  # Campo correcto es fechaVale
                    'tipo': vale.tipo,
                    'noDocumento': vale.noDocumento,
                    'descripcion': vale.descripcion,
                    'referencia': vale.referencia,
                    'total': vale.total,
                    'proveedor': vale.proveedor,
                    'departamento': vale.departamento,
                    'sucursal': vale.sucursal,
                    'marca': vale.marca,
                    'responsable': vale.responsable
                } if vale else None,
                'repartimientos': [
                    {
                        'id': r.id,
                        'comercial': float(r.comercial) if r.comercial else 0.0,
                        'fleet': float(r.fleet) if r.fleet else 0.0,
                        'seminuevos': float(r.seminuevos) if r.seminuevos else 0.0,
                        'refacciones': float(r.refacciones) if r.refacciones else 0.0,
                        'servicio': float(r.servicio) if r.servicio else 0.0,
                        'hyp': float(r.hyp) if r.hyp else 0.0,
                        'administracion': float(r.administracion) if r.administracion else 0.0
                    }
                    for r in repartimientos
                ]
            }
            
            return details
            
        except Exception as e:
            self.logger.error(f"Error obteniendo detalles de factura {folio_interno}: {e}")
            traceback.print_exc()
            return None
    
    def reimprimir_factura(self, selected_data: Dict[str, Any]) -> bool:
        """
        Reimprimir una factura usando form_control.py
        
        Args:
            selected_data: Datos de la factura seleccionada
            
        Returns:
            bool: True si se reimprimió correctamente
        """
        try:
            # Obtener detalles completos de la factura
            folio_interno = selected_data.get('folio_interno')
            if not folio_interno:
                self.dialog_utils.show_warning("Error de datos", "No se puede identificar la factura seleccionada")
                return False
            
            details = self.get_invoice_details(folio_interno)
            if not details:
                self.dialog_utils.show_warning("Error de datos", "No se pudieron obtener los detalles de la factura")
                return False
            
            # Importar form_control
            try:
                from solicitudapp.form_control import FormPDF
            except ImportError:
                self.dialog_utils.show_error("Error de importación", "No se pudo importar el módulo form_control")
                return False
            
            # Preparar datos para el formulario
            factura = details['factura']
            proveedor = details['proveedor']
            conceptos = details['conceptos']
            vale = details['vale']
            
            # Formatear datos según el formato esperado por FormPDF
            # Usar los mismos nombres de campos que en buscar_app.py
            
            # Formatear tipo de vale
            tipo_vale_formatted = ""
            if factura['tipo']:
                try:
                    from solicitudapp.config.app_config import AppConfig
                    if hasattr(AppConfig, 'TIPO_VALE') and factura['tipo'] in AppConfig.TIPO_VALE:
                        tipo_vale_formatted = f"{factura['tipo']} - {AppConfig.TIPO_VALE[factura['tipo']]}"
                    else:
                        tipo_vale_formatted = factura['tipo']
                except:
                    tipo_vale_formatted = factura['tipo']
            
            # Construir comentario con serie y folio de la factura
            serie_str = factura.get('serie') or ""
            folio_str = factura.get('folio') or ""
            
            if serie_str and folio_str:
                comentario_factura = f"Factura: {serie_str} {folio_str}"
            elif serie_str:
                comentario_factura = f"Factura: {serie_str}"
            elif folio_str:
                comentario_factura = f"Factura: {folio_str}"
            else:
                comentario_factura = "Factura:"
            
            # Obtener repartimientos si existen
            repartimientos = details.get('repartimientos', [])
            reparto = repartimientos[0] if repartimientos else {}
            
            form_data = {
                "TIPO DE VALE": tipo_vale_formatted,
                "C A N T I D A D": "\n".join([str(concepto['cantidad']) for concepto in conceptos]),
                "C O M E N T A R I O S": comentario_factura,
                "Nombre de Empresa": proveedor['nombre'],
                "RFC": proveedor['rfc'],
                "Teléfono": proveedor.get('telefono', ''),
                "Correo": proveedor.get('email', ''),
                "Nombre Contacto": proveedor.get('nombre_contacto', ''),
                "Menudeo": str(reparto.get('comercial', '')) if reparto.get('comercial') else "",
                "Seminuevos": str(reparto.get('seminuevos', '')) if reparto.get('seminuevos') else "",
                "Flotas": str(reparto.get('fleet', '')) if reparto.get('fleet') else "",
                "Administración": str(reparto.get('administracion', '')) if reparto.get('administracion') else "",
                "Refacciones": str(reparto.get('refacciones', '')) if reparto.get('refacciones') else "",
                "Servicio": str(reparto.get('servicio', '')) if reparto.get('servicio') else "",
                "HYP": str(reparto.get('hyp', '')) if reparto.get('hyp') else "",
                "DESCRIPCIÓN": "\n".join([concepto['descripcion'] for concepto in conceptos]),
                "PRECIO UNITARIO": "\n".join([f"${concepto['precio_unitario']:,.2f}" for concepto in conceptos]),
                "TOTAL": "\n".join([f"${concepto['total']:,.2f}" for concepto in conceptos]),
                "FECHA GERENTE DE ÁREA": "",
                "FECHA GERENTE ADMINISTRATIVO": "",
                "FECHA DE AUTORIZACIÓN GG O DIRECTOR DE MARCA": "",
                "SUBTOTAL": f"${factura['subtotal']:,.2f}" if factura['subtotal'] else "",
                "IVA": f"${factura['iva_trasladado']:,.2f}" if factura['iva_trasladado'] else "",
                "TOTAL, SUMATORIA": f"${factura['total']:,.2f}" if factura['total'] else "",
                "FECHA CREACIÓN SOLICITUD": factura['fecha'],
                "FOLIO": str(factura['folio_interno']),
                "RETENCIÓN": f"${(factura.get('ret_iva', 0) + factura.get('ret_isr', 0)):,.2f}" if factura.get('ret_iva') or factura.get('ret_isr') else "",
                "Departamento": ""
            }
            
            # Crear instancia de FormPDF y llenar
            form_pdf = FormPDF()
            
            # Solicitar archivo de destino
            output_path = self.dialog_utils.save_file_dialog(
                parent=None,
                title="Guardar solicitud reimpresa",
                default_filename="",
                file_types=[("PDF files", "*.pdf")]
            )
            
            if not output_path:
                return False
            
            # Llenar y guardar el formulario
            try:
                form_pdf.rellenar(form_data, output_path)
                success = True
            except Exception as form_error:
                self.logger.error(f"Error al llenar formulario: {form_error}")
                success = False
            
            if success:
                self.dialog_utils.show_info("Reimpresión exitosa", f"Solicitud reimpresa guardada en:\n{output_path}")
                self.logger.info(f"Factura {folio_interno} reimpresa exitosamente")
                return True
            else:
                self.dialog_utils.show_error("Error al generar", "Error al generar la solicitud")
                return False
                
        except Exception as e:
            self.logger.error(f"Error en reimprimir_factura: {e}")
            traceback.print_exc()
            self.dialog_utils.show_error("Error al reimprimir", f"Error al reimprimir: {str(e)}")
            return False
    
    def toggle_cargada_status(self, folio_interno: str) -> bool:
        """
        Cambia el estado de 'cargada' de una factura
        
        Args:
            folio_interno: Folio interno de la factura
            
        Returns:
            bool: True si se cambió correctamente
        """
        try:
            if not self.bd_control:
                self.logger.warning("Base de datos no disponible")
                return False
            
            from bd.models import Factura
            
            # Buscar la factura
            try:
                factura = Factura.get(Factura.folio_interno == folio_interno)
            except Factura.DoesNotExist:
                self.logger.warning(f"No se encontró la factura con folio interno: {folio_interno}")
                return False
            
            # Cambiar estado
            nuevo_estado = not factura.cargada
            factura.cargada = nuevo_estado
            factura.save()
            
            self.logger.info(f"Factura {folio_interno} - Estado 'cargada' cambiado a: {nuevo_estado}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cambiando estado de factura {folio_interno}: {e}")
            return False
    
    def toggle_pagada_status(self, folio_interno: str) -> bool:
        """
        Cambia el estado de 'pagada' de una factura
        
        Args:
            folio_interno: Folio interno de la factura
            
        Returns:
            bool: True si se cambió correctamente
        """
        try:
            if not self.bd_control:
                self.logger.warning("Base de datos no disponible")
                return False
            
            from bd.models import Factura
            
            # Buscar la factura
            try:
                factura = Factura.get(Factura.folio_interno == folio_interno)
            except Factura.DoesNotExist:
                self.logger.warning(f"No se encontró la factura con folio interno: {folio_interno}")
                return False
            
            # Cambiar estado
            nuevo_estado = not factura.pagada
            factura.pagada = nuevo_estado
            factura.save()
            
            self.logger.info(f"Factura {folio_interno} - Estado 'pagada' cambiado a: {nuevo_estado}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cambiando estado de factura {folio_interno}: {e}")
            return False
    
    def abrir_archivo(self, file_path: str) -> bool:
        """
        Abre un archivo con la aplicación predeterminada del sistema
        
        Args:
            file_path: Ruta del archivo a abrir
            
        Returns:
            bool: True si se abrió correctamente
        """
        try:
            if not file_path or not os.path.exists(file_path):
                self.dialog_utils.show_warning("Archivo no encontrado", "El archivo no existe o la ruta está vacía")
                return False
            
            import subprocess
            import platform
            
            # Abrir archivo según el sistema operativo
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', file_path])
            else:  # Linux
                subprocess.call(['xdg-open', file_path])
            
            self.logger.info(f"Archivo abierto: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error abriendo archivo {file_path}: {e}")
            self.dialog_utils.show_error("Error abriendo archivo", f"No se pudo abrir el archivo: {str(e)}")
            return False
