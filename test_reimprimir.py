"""
Script para verificar el formato de datos que se usará en reimprimir.
"""
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.bd.models import Factura, Proveedor, Concepto, Vale, Reparto, db

def probar_formato_reimprimir():
    """Prueba el formato de datos para reimprimir."""
    try:
        db.connect()
        
        # Obtener la primera factura
        factura = Factura.select().first()
        if not factura:
            print("No hay facturas en la base de datos")
            return
        
        print("=== DATOS PARA REIMPRIMIR (FORMATO SOLICITUD_APP_PROFESSIONAL) ===")
        
        # Obtener datos relacionados
        proveedor = factura.proveedor
        conceptos = list(factura.conceptos)
        
        # Obtener vale asociado si existe
        vale = None
        try:
            vale = Vale.get(Vale.factura == factura.folio_interno)
        except:
            pass
        
        # Obtener reparto asociado si existe
        reparto = None
        try:
            reparto = Reparto.get(Reparto.factura == factura)
        except:
            pass
        
        # Generar el diccionario de datos exactamente como en solicitud_app_professional
        datos_formulario = {
            "TIPO DE VALE": factura.tipo or "",
            "C A N T I D A D": "\n".join([str(concepto.cantidad) for concepto in conceptos]),
            "C O M E N T A R I O S": factura.comentario or "",
            "Nombre de Empresa": proveedor.nombre if proveedor else "",
            "RFC": proveedor.rfc if proveedor else "",
            "Teléfono": proveedor.telefono if proveedor else "",
            "Correo": proveedor.email if proveedor else "",
            "Nombre Contacto": proveedor.nombre_contacto if proveedor else "",
            "Menudeo": str(reparto.comercial) if reparto and reparto.comercial else "",
            "Seminuevos": str(reparto.seminuevos) if reparto and reparto.seminuevos else "",
            "Flotas": str(reparto.fleet) if reparto and reparto.fleet else "",
            "Administración": str(reparto.administracion) if reparto and reparto.administracion else "",
            "Refacciones": str(reparto.refacciones) if reparto and reparto.refacciones else "",
            "Servicio": str(reparto.servicio) if reparto and reparto.servicio else "",
            "HYP": str(reparto.hyp) if reparto and reparto.hyp else "",
            "DESCRIPCIÓN": "\n".join([concepto.descripcion for concepto in conceptos]),
            "PRECIO UNITARIO": "\n".join([f"${concepto.precio_unitario:,.2f}" for concepto in conceptos]),
            "TOTAL": "\n".join([f"${concepto.total:,.2f}" for concepto in conceptos]),
            "FECHA GERENTE DE ÁREA": "",
            "FECHA GERENTE ADMINISTRATIVO": "",
            "FECHA DE AUTORIZACIÓN GG O DIRECTOR DE MARCA": "",
            "SUBTOTAL": f"${factura.subtotal:,.2f}" if factura.subtotal else "",
            "IVA": f"${factura.iva_trasladado:,.2f}" if factura.iva_trasladado else "",
            "TOTAL, SUMATORIA": f"${factura.total:,.2f}" if factura.total else "",
            "FECHA CREACIÓN SOLICITUD": factura.fecha.strftime('%d/%m/%Y') if hasattr(factura.fecha, 'strftime') else str(factura.fecha),
            "FOLIO": str(factura.folio_interno),
            "RETENCIÓN": f"${(factura.ret_iva or 0) + (factura.ret_isr or 0):,.2f}" if factura.ret_iva or factura.ret_isr else "",
            "Departamento": ""
        }
        
        # Mostrar el diccionario
        print("\nDICCIONARIO DE DATOS:")
        for clave, valor in datos_formulario.items():
            print(f'"{clave}": "{valor}"')
        
        print(f"\n✅ Formato compatible con solicitud_app_professional")
        print(f"Reparto encontrado: {'Sí' if reparto else 'No'}")
        print(f"Vale encontrado: {'Sí' if vale else 'No'}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if not db.is_closed():
            db.close()

if __name__ == "__main__":
    probar_formato_reimprimir()
