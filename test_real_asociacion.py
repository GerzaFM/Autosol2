#!/usr/bin/env python3
"""
Script de prueba directo para probar la asociación en tiempo real
"""
import sys
import os

# Agregar paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

def test_asociacion_real():
    """Prueba la asociación con datos reales de la BD"""
    
    # Importar lo necesario
    from bd.models import Factura, Vale
    
    print("="*80)
    print("PRUEBA DE ASOCIACIÓN REAL CON DATOS DE BD")
    print("="*80)
    
    # Obtener facturas reales de la BD
    facturas_reales = []
    print("\n📋 FACTURAS DISPONIBLES EN BD:")
    for factura in Factura.select().limit(10):
        serie_folio = f"{factura.serie} {factura.folio}"
        facturas_reales.append({
            'folio_interno': str(factura.folio_interno),
            'serie_folio': serie_folio,
            'folio_xml': serie_folio,
            'serie': factura.serie,
            'folio': factura.folio,
            'tipo': factura.tipo
        })
        print(f"   - {serie_folio} (Serie: {factura.serie}, Folio: {factura.folio}, Tipo: {type(factura.folio)})")
    
    # Casos de prueba con datos que deberían coincidir
    vales_test = [
        {'noVale': 'TEST_5718', 'noDocumento': '5718'},      # Debería coincidir con OLEK 5718
        {'noVale': 'TEST_10604', 'noDocumento': '10604'},    # Debería coincidir con CC 10604
        {'noVale': 'TEST_17474', 'noDocumento': '17474'},    # Debería coincidir con F 17474
        {'noVale': 'TEST_NO_MATCH', 'noDocumento': '99999'}, # No debería coincidir
    ]
    
    # Importar funciones necesarias
    def normalizar_documento(doc):
        """Normaliza un documento para comparación: elimina espacios y guiones"""
        return str(doc).replace(' ', '').replace('-', '').strip()
    
    def buscar_factura_asociada_simple(no_documento, facturas_seleccionadas, nombre_vale=""):
        if not no_documento or not facturas_seleccionadas:
            return None, None
            
        doc_norm = normalizar_documento(no_documento)
        print(f"🔍 Buscando asociación para vale {nombre_vale}: No Documento '{no_documento}' (normalizado: '{doc_norm}')")
        
        for i, factura_data in enumerate(facturas_seleccionadas):
            try:
                # Obtener datos de la factura
                serie_folio = factura_data.get('serie_folio', '')
                serie = factura_data.get('serie', '')
                folio = factura_data.get('folio', '')
                
                # Convertir a strings
                serie_folio = str(serie_folio).strip() if serie_folio else ''
                serie = str(serie).strip() if serie else ''
                folio_str = str(folio).strip() if folio else ''
                
                print(f"   📋 Verificando factura: '{serie_folio}' - Serie: '{serie}', Folio: '{folio_str}' (tipo folio: {type(folio)})")
                
                # Coincidencia por folio exacto
                if folio_str and folio_str == no_documento:
                    print(f"   ✅ COINCIDENCIA POR FOLIO: '{folio_str}' = '{no_documento}'")
                    try:
                        if serie and folio_str.isdigit():
                            # Buscar en BD real
                            factura_encontrada = Factura.get((Factura.serie == serie) & (Factura.folio == int(folio_str)))
                            print(f"   🎯 FACTURA ENCONTRADA EN BD: {factura_encontrada.serie}-{factura_encontrada.folio}")
                            return factura_encontrada, "folio_exacto"
                        else:
                            print(f"   ❌ Datos inválidos: serie='{serie}', folio='{folio_str}', es_digito={folio_str.isdigit()}")
                    except Exception as e:
                        print(f"   ❌ Error buscando en BD: {e}")
                        continue
                
                # Coincidencia parcial
                serie_folio_norm = normalizar_documento(serie_folio)
                if doc_norm and (doc_norm in serie_folio_norm or serie_folio_norm in doc_norm):
                    print(f"   ✅ COINCIDENCIA PARCIAL: '{doc_norm}' <-> '{serie_folio_norm}'")
                    try:
                        if serie and folio_str and folio_str.isdigit():
                            factura_encontrada = Factura.get((Factura.serie == serie) & (Factura.folio == int(folio_str)))
                            print(f"   🎯 FACTURA ENCONTRADA EN BD: {factura_encontrada.serie}-{factura_encontrada.folio}")
                            return factura_encontrada, "parcial"
                        else:
                            print(f"   ❌ Datos inválidos para parcial: serie='{serie}', folio='{folio_str}', es_digito={folio_str.isdigit()}")
                    except Exception as e:
                        print(f"   ❌ Error buscando en BD: {e}")
                        continue
                
                print(f"   ❌ Sin coincidencia: '{no_documento}' vs '{serie_folio}'")
            
            except Exception as e:
                print(f"   ❌ Error procesando factura {i}: {e}")
                continue
        
        print(f"   ⚠️ No se encontró coincidencia para No Documento '{no_documento}'")
        return None, None
    
    print("\n🧪 PRUEBAS DE ASOCIACIÓN:")
    print("-"*80)
    
    for vale in vales_test:
        print(f"\n🔍 PRUEBA: {vale['noVale']} con No Documento '{vale['noDocumento']}'")
        factura_encontrada, tipo = buscar_factura_asociada_simple(
            vale['noDocumento'], 
            facturas_reales, 
            vale['noVale']
        )
        
        if factura_encontrada:
            print(f"   🎉 ÉXITO: ASOCIADO con {factura_encontrada.serie}-{factura_encontrada.folio} (tipo: {tipo})")
        else:
            print(f"   ❌ NO ASOCIADO")
        print("-"*80)

if __name__ == "__main__":
    test_asociacion_real()
