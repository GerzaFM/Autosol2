#!/usr/bin/env python3
"""
Script para probar el método rellenar_datos_proveedor_anterior
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'solicitudapp'))

try:
    from bd.models import Proveedor, Factura, Reparto
    from solicitudapp.config.app_config import AppConfig
    
    # Simular el método rellenar_datos_proveedor_anterior
    def test_rellenar_datos_proveedor_anterior(rfc_proveedor):
        """Simular el método para ver qué está pasando"""
        print(f"🔍 Buscando proveedor con RFC: {rfc_proveedor}")
        
        try:
            proveedor = Proveedor.get(Proveedor.rfc == rfc_proveedor)
            print(f"✅ Proveedor encontrado: {proveedor.nombre}")
            
            # Buscar la última factura
            ultima_factura = (Factura
                            .select()
                            .where(Factura.proveedor == proveedor)
                            .order_by(Factura.folio_interno.desc())
                            .first())
            
            if ultima_factura:
                print(f"✅ Última factura encontrada: {ultima_factura.serie}-{ultima_factura.folio}")
                print(f"   Tipo: {ultima_factura.tipo}")
                
                # Verificar si el tipo existe en TIPO_VALE
                tipo_encontrado = None
                for clave, descripcion in AppConfig.TIPO_VALE.items():
                    if clave == ultima_factura.tipo:
                        tipo_encontrado = f"{clave} - {descripcion}"
                        break
                
                if tipo_encontrado:
                    print(f"✅ Tipo mapeado: {tipo_encontrado}")
                else:
                    print(f"❌ Tipo '{ultima_factura.tipo}' no encontrado en TIPO_VALE")
                
                # Buscar el reparto
                ultimo_reparto = Reparto.get_or_none(Reparto.factura == ultima_factura)
                if ultimo_reparto:
                    print(f"✅ Reparto encontrado:")
                    print(f"   Comercial: {ultimo_reparto.comercial}")
                    print(f"   Fleet: {ultimo_reparto.fleet}")
                    print(f"   Seminuevos: {ultimo_reparto.seminuevos}")
                    print(f"   Refacciones: {ultimo_reparto.refacciones}")
                    print(f"   HyP: {ultimo_reparto.hyp}")
                    print(f"   Administración: {ultimo_reparto.administracion}")
                    
                    # Simular los datos que se enviarían
                    datos_rellenado = {
                        'tipo': tipo_encontrado if tipo_encontrado else ultima_factura.tipo,
                        'comercial': str(ultimo_reparto.comercial),
                        'fleet': str(ultimo_reparto.fleet),
                        'seminuevos': str(ultimo_reparto.seminuevos),
                        'refacciones': str(ultimo_reparto.refacciones),
                        'hyp': str(ultimo_reparto.hyp),
                        'administracion': str(ultimo_reparto.administracion)
                    }
                    
                    print(f"\n📦 Datos que se rellenarían:")
                    for campo, valor in datos_rellenado.items():
                        print(f"   {campo}: {valor}")
                    
                    return datos_rellenado
                else:
                    print("❌ No se encontró reparto para la última factura")
                    return None
            else:
                print("❌ No se encontró ninguna factura para este proveedor")
                return None
                
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    # Probar con el RFC de los datos de prueba
    print("🧪 Probando método de relleno de datos...")
    resultado = test_rellenar_datos_proveedor_anterior("XAXX010101000")
    
    if resultado:
        print("\n✅ El método funciona correctamente")
    else:
        print("\n❌ El método tiene problemas")
        
except Exception as e:
    print(f"❌ Error en imports: {e}")
    import traceback
    traceback.print_exc()
