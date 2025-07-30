#!/usr/bin/env python3
"""
Script para verificar cómo se ven los datos del to_dict()
"""
import sys
import os

# Agregar paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

def test_to_dict():
    """Verificar los datos del to_dict()"""
    
    from bd.models import Factura
    from buscarapp.models.search_models import FacturaData
    
    print("="*80)
    print("VERIFICACIÓN DE to_dict() DE FACTURAS")
    print("="*80)
    
    # Obtener una factura real
    factura_real = Factura.select().first()
    
    print(f"\n📋 FACTURA REAL DE BD:")
    print(f"   Serie: '{factura_real.serie}', Folio: {factura_real.folio}")
    
    # Crear FacturaData como lo hace el controlador
    factura_data = FacturaData(
        folio_interno=str(factura_real.folio_interno),
        tipo=factura_real.tipo,
        no_vale="",
        fecha="2025-07-30",
        folio_xml=f"{factura_real.serie or ''} {factura_real.folio or ''}".strip(),
        serie=factura_real.serie,
        folio=factura_real.folio,
        nombre_emisor=factura_real.nombre_emisor,
        rfc_emisor=factura_real.rfc_emisor,
        conceptos="",
        total=float(factura_real.total) if factura_real.total else 0.0,
        subtotal=float(factura_real.subtotal) if factura_real.subtotal else 0.0,
        iva_trasladado=float(factura_real.iva_trasladado) if factura_real.iva_trasladado else 0.0,
        ret_iva=float(factura_real.ret_iva) if factura_real.ret_iva else 0.0,
        ret_isr=float(factura_real.ret_isr) if factura_real.ret_isr else 0.0,
        clase=factura_real.clase,
        cargada=False,
        pagada=False,
        comentario=factura_real.comentario
    )
    
    print(f"\n📊 FACTURADATA OBJETO:")
    print(f"   serie: '{factura_data.serie}'")
    print(f"   folio: '{factura_data.folio}'")
    print(f"   serie_folio: '{factura_data.serie_folio}'")
    
    # Convertir a diccionario
    factura_dict = factura_data.to_dict()
    
    print(f"\n🔄 RESULTADO DE to_dict():")
    print(f"   serie: '{factura_dict.get('serie', 'NO_ENCONTRADO')}'")
    print(f"   folio: '{factura_dict.get('folio', 'NO_ENCONTRADO')}'")
    print(f"   serie_folio: '{factura_dict.get('serie_folio', 'NO_ENCONTRADO')}'")
    
    print(f"\n🧪 TIPOS DE DATOS:")
    print(f"   tipo serie: {type(factura_dict.get('serie'))}")
    print(f"   tipo folio: {type(factura_dict.get('folio'))}")
    
    print(f"\n📝 DICCIONARIO COMPLETO:")
    for key, value in factura_dict.items():
        if key in ['serie', 'folio', 'serie_folio', 'folio_xml']:
            print(f"   {key}: '{value}' (tipo: {type(value)})")

if __name__ == "__main__":
    test_to_dict()
