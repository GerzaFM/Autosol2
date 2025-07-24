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
            conceptos = list(Concepto.select().where(Concepto.factura == factura.id))
            
            # Obtener vale (si existe)
            vale = None
            try:
                if factura.no_vale:
                    vale = Vale.select().where(Vale.no_vale == factura.no_vale).get()
            except Vale.DoesNotExist:
                pass
            
            # Obtener repartimientos (si existen)
            repartimientos = list(Reparto.select().where(Reparto.factura == factura.id))
            
            # Construir diccionario de detalles
            details = {
                'factura': {
                    'folio_interno': factura.folio_interno,
                    'tipo': factura.tipo,
                    'no_vale': factura.no_vale,
                    'fecha': factura.fecha.strftime('%Y-%m-%d') if factura.fecha else "",
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
                    'comentario': factura.comentario,
                    'uuid': factura.uuid,
                    'xml_path': factura.xml_path,
                    'pdf_path': factura.pdf_path
                },
                'proveedor': {
                    'id': factura.proveedor.id,
                    'nombre': factura.proveedor.nombre,
                    'rfc': factura.proveedor.rfc,
                    'telefono': factura.proveedor.telefono,
                    'email': factura.proveedor.email,
                    'nombre_contacto': factura.proveedor.nombre_contacto
                },
                'conceptos': [
                    {
                        'id': c.id,
                        'cantidad': float(c.cantidad) if c.cantidad else 0.0,
                        'unidad': c.unidad,
                        'descripcion': c.descripcion,
                        'valor_unitario': float(c.valor_unitario) if c.valor_unitario else 0.0,
                        'importe': float(c.importe) if c.importe else 0.0,
                        'clave_prodserv': c.clave_prodserv,
                        'clave_unidad': c.clave_unidad
                    }
                    for c in conceptos
                ],
                'vale': {
                    'no_vale': vale.no_vale,
                    'fecha_vale': vale.fecha_vale.strftime('%Y-%m-%d') if vale.fecha_vale else "",
                    'beneficiario': vale.beneficiario,
                    'comentario': vale.comentario,
                    'cargado': bool(vale.cargado),
                    'pagado': bool(vale.pagado)
                } if vale else None,
                'repartimientos': [
                    {
                        'id': r.id,
                        'cuenta': r.cuenta,
                        'debe': float(r.debe) if r.debe else 0.0,
                        'haber': float(r.haber) if r.haber else 0.0,
                        'referencia': r.referencia
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
                self.dialog_utils.show_warning("No se puede identificar la factura seleccionada")
                return False
            
            details = self.get_invoice_details(folio_interno)
            if not details:
                self.dialog_utils.show_warning("No se pudieron obtener los detalles de la factura")
                return False
            
            # Importar form_control
            try:
                from solicitudapp.form_control import FormPDF
            except ImportError:
                self.dialog_utils.show_error("No se pudo importar el módulo form_control")
                return False
            
            # Preparar datos para el formulario
            factura = details['factura']
            proveedor = details['proveedor']
            conceptos = details['conceptos']
            vale = details['vale']
            
            # Formatear datos según el formato esperado por FormPDF
            form_data = {
                'folio_interno': format_folio(factura['folio_interno']),
                'tipo_vale': format_tipo_vale(factura['tipo']),
                'no_vale': factura['no_vale'] or '',
                'fecha': factura['fecha'],
                'proveedor': proveedor['nombre'],
                'rfc_proveedor': proveedor['rfc'],
                'comentarios': self._format_comentarios_reimprimir(factura, conceptos),
                'subtotal': format_currency(factura['subtotal']),
                'iva': format_currency(factura['iva_trasladado']),
                'retencion_iva': format_currency(factura['ret_iva']),
                'retencion_isr': format_currency(factura['ret_isr']),
                'total': format_currency(factura['total'])
            }
            
            # Crear instancia de FormPDF y llenar
            form_pdf = FormPDF()
            
            # Solicitar archivo de destino
            output_path = self.dialog_utils.save_file_dialog(
                title="Guardar solicitud reimpresa",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")]
            )
            
            if not output_path:
                return False
            
            # Llenar y guardar el formulario
            success = form_pdf.llenar_formulario(form_data, output_path)
            
            if success:
                self.dialog_utils.show_info(f"Solicitud reimpresa guardada en:\n{output_path}")
                self.logger.info(f"Factura {folio_interno} reimpresa exitosamente")
                return True
            else:
                self.dialog_utils.show_error("Error al generar la solicitud")
                return False
                
        except Exception as e:
            self.logger.error(f"Error en reimprimir_factura: {e}")
            traceback.print_exc()
            self.dialog_utils.show_error(f"Error al reimprimir: {str(e)}")
            return False
    
    def _format_comentarios_reimprimir(self, factura: Dict[str, Any], conceptos: List[Dict[str, Any]]) -> str:
        """
        Formatea los comentarios para la reimpresión
        
        Args:
            factura: Datos de la factura
            conceptos: Lista de conceptos
            
        Returns:
            str: Comentarios formateados
        """
        comentarios = []
        
        # Agregar número de factura
        folio_factura = format_comentario_factura(factura.get('serie'), factura.get('folio'))
        if folio_factura:
            comentarios.append(f"FACTURA: {folio_factura}")
        
        # Agregar conceptos principales
        if conceptos:
            # Mostrar los primeros conceptos más importantes
            for i, concepto in enumerate(conceptos[:3]):  # Limitar a 3 conceptos
                desc = concepto.get('descripcion', '').strip()
                if desc:
                    # Limitar longitud del concepto
                    if len(desc) > 50:
                        desc = desc[:47] + "..."
                    comentarios.append(f"• {desc}")
            
            # Si hay más conceptos, indicarlo
            if len(conceptos) > 3:
                comentarios.append(f"... y {len(conceptos) - 3} conceptos más")
        
        # Agregar comentario adicional si existe
        comentario_adicional = factura.get('comentario', '').strip()
        if comentario_adicional:
            comentarios.append(f"OBSERVACIONES: {comentario_adicional}")
        
        return '\n'.join(comentarios)
    
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
                self.dialog_utils.show_warning("El archivo no existe o la ruta está vacía")
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
            self.dialog_utils.show_error(f"No se pudo abrir el archivo: {str(e)}")
            return False
