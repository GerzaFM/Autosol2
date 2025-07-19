#!/usr/bin/env python3
"""
Script de prueba para verificar la función de generar sin ejecutar la UI completa.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    # Importar módulos necesarios
    from solicitudapp.logic_solicitud import SolicitudLogica
    from solicitudapp.form_control import FormPDF
    from bd.bd_control import DBManager
    
    print("✅ Importaciones exitosas")
    
    # Datos de prueba
    proveedor_data = {
        "nombre": "Proveedor de Prueba",
        "rfc": "XAXX010101000",
        "telefono": "444-123-4567",
        "email": "test@test.com",
        "nombre_contacto": "Juan Pérez"
    }
    
    solicitud_data = {
        "serie": "A",
        "folio": "001",
        "fecha": "2025-01-17",
        "tipo": "VC",  # Usar clave del diccionario TIPO_VALE
        "nombre_receptor": "TCM MATEHUALA",
        "rfc_receptor": "TMM860630PH1"
    }
    
    conceptos_data = [{
        "descripcion": "Producto de prueba",
        "cantidad": "1",
        "unidad": "PZ",
        "precio_unitario": "100.00",
        "importe": "100.00"
    }]
    
    totales_data = {
        "subtotal": "100.00",
        "iva_trasladado": "16.00",
        "ret_iva": "0.00",
        "ret_isr": "0.00",
        "total": "116.00"
    }
    
    categorias_data = {
        "comercial": "100",
        "fleet": "0",
        "seminuevos": "0",
        "refacciones": "0",
        "servicios": "0",
        "hyp": "0",
        "administracion": "0"
    }
    
    comentarios_data = {
        "comentario": "Prueba de generación"
    }
    
    # Probar guardar solicitud
    try:
        logica = SolicitudLogica()
        factura = logica.guardar_solicitud(
            proveedor_data, solicitud_data, conceptos_data,
            totales_data, categorias_data, comentarios_data
        )
        print(f"✅ Factura guardada exitosamente con ID: {factura.folio_interno}")
    except Exception as e:
        print(f"❌ Error al guardar factura: {e}")
    
    # Probar rellenar formulario
    try:
        form_data = {
            "TIPO DE VALE": "VC - VALE DE CONTROL",  # Usar formato completo para el PDF
            "C A N T I D A D": "1",
            "C O M E N T A R I O S": "Prueba",
            "Nombre de Empresa": "Proveedor de Prueba",
            "RFC": "XAXX010101000",
            "FOLIO": "123",
            "SUBTOTAL": "100.00",
            "IVA": "16.00",
            "TOTAL, SUMATORIA": "116.00"
        }
        
        # Solo probar sin generar archivo
        form = FormPDF()
        print("✅ FormPDF inicializado correctamente")
        
    except Exception as e:
        print(f"❌ Error con FormPDF: {e}")
        
except ImportError as e:
    print(f"❌ Error de importación: {e}")
except Exception as e:
    print(f"❌ Error general: {e}")
