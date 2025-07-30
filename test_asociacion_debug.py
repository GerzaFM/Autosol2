#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento de la asociación de vales.
"""
import sys
import os

# Agregar paths necesarios
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

def test_asociacion():
    """Prueba la asociación de vales con facturas."""
    
    # Simular datos de facturas seleccionadas como los devuelve la aplicación
    facturas_seleccionadas = [
        {
            'folio_interno': '1',
            'serie_folio': 'CC 10604',
            'serie': 'CC',
            'folio': 10604,
            'tipo': 'Ingreso'
        },
        {
            'folio_interno': '2',
            'serie_folio': 'CC 10603',
            'serie': 'CC',
            'folio': 10603,
            'tipo': 'Ingreso'
        },
        {
            'folio_interno': '3',
            'serie_folio': 'OLEK 5718',
            'serie': 'OLEK',
            'folio': 5718,
            'tipo': 'Ingreso'
        },
        {
            'folio_interno': '4',
            'serie_folio': 'F 17474',
            'serie': 'F',
            'folio': 17474,
            'tipo': 'Ingreso'
        }
    ]
    
    # Simular vales con diferentes No Documento
    vales_test = [
        {'noVale': 'V153924', 'noDocumento': '5718'},     # Debería asociarse con OLEK 5718
        {'noVale': 'V153814', 'noDocumento': '369858470'}, # No debería asociarse
        {'noVale': 'V151284', 'noDocumento': 'VERSAJUL25'}, # No debería asociarse
        {'noVale': 'V150001', 'noDocumento': '10604'},    # Debería asociarse con CC 10604
        {'noVale': 'V150002', 'noDocumento': '17474'},    # Debería asociarse con F 17474
    ]
    
    # Función de normalización (copiada del controlador)
    def normalizar_documento(doc):
        """Normaliza un documento para comparación: elimina espacios y guiones"""
        return str(doc).replace(' ', '').replace('-', '').strip()
    
    # Función de búsqueda simplificada
    def buscar_factura_asociada_test(no_documento, facturas_seleccionadas, nombre_vale=""):
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
                
                print(f"   📋 Verificando factura: '{serie_folio}' - Serie: '{serie}', Folio: '{folio_str}'")
                
                # Normalizar para comparación
                serie_folio_norm = normalizar_documento(serie_folio)
                
                # 1. Coincidencia directa con serie_folio normalizado
                if serie_folio_norm == doc_norm:
                    print(f"   ✅ Coincidencia directa serie_folio: '{serie_folio}' ~ '{no_documento}'")
                    return factura_data, "serie_folio_exacto"
                
                # 2. Coincidencia solo con el folio
                if folio_str and folio_str == no_documento:
                    print(f"   ✅ Coincidencia por folio: folio '{folio_str}' = '{no_documento}'")
                    return factura_data, "folio_exacto"
                
                # 3. Coincidencia con serie
                if serie and serie == no_documento:
                    print(f"   ✅ Coincidencia por serie: serie '{serie}' = '{no_documento}'")
                    return factura_data, "serie_exacto"
                
                # 4. Coincidencia parcial
                if doc_norm and (doc_norm in serie_folio_norm or serie_folio_norm in doc_norm):
                    print(f"   ✅ Coincidencia parcial: '{doc_norm}' <-> '{serie_folio_norm}'")
                    return factura_data, "parcial"
                
                print(f"   ❌ Sin coincidencia: '{no_documento}' vs '{serie_folio}'")
            
            except Exception as e:
                print(f"   ❌ Error procesando factura {i}: {e}")
                continue
        
        print(f"   ⚠️ No se encontró coincidencia para No Documento '{no_documento}'")
        return None, None
    
    # Ejecutar pruebas
    print("="*80)
    print("PRUEBA DE ASOCIACIÓN DE VALES")
    print("="*80)
    
    print("\n📋 FACTURAS DISPONIBLES:")
    for factura in facturas_seleccionadas:
        print(f"   - {factura['serie_folio']} (Serie: {factura['serie']}, Folio: {factura['folio']})")
    
    print("\n🧪 PRUEBAS DE ASOCIACIÓN:")
    print("-"*50)
    
    for vale in vales_test:
        print(f"\n🔍 PRUEBA: {vale['noVale']} con No Documento '{vale['noDocumento']}'")
        resultado, tipo = buscar_factura_asociada_test(
            vale['noDocumento'], 
            facturas_seleccionadas, 
            vale['noVale']
        )
        
        if resultado:
            print(f"   ✅ ASOCIADO con {resultado['serie_folio']} (tipo: {tipo})")
        else:
            print(f"   ❌ NO ASOCIADO")
        print("-"*50)

if __name__ == "__main__":
    test_asociacion()
