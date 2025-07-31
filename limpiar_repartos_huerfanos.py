#!/usr/bin/env python3
"""
Script para limpiar repartos huérfanos que apuntan a facturas inexistentes
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bd.models import Factura, Reparto, db
from peewee import DoesNotExist

def limpiar_repartos_huerfanos():
    """Elimina repartos que apuntan a facturas inexistentes"""
    try:
        db.connect()
        print("Conectado a la base de datos")
        
        # Obtener todos los repartos
        repartos = Reparto.select()
        total_repartos = repartos.count()
        print(f"Total de repartos en la base de datos: {total_repartos}")
        
        huerfanos_encontrados = []
        validos = 0
        
        for reparto in repartos:
            try:
                # Intentar acceder a la factura
                factura = reparto.factura
                print(f"✓ Reparto {reparto.id} -> Factura {factura.folio_interno} (VÁLIDO)")
                validos += 1
            except DoesNotExist:
                print(f"✗ Reparto {reparto.id} -> Factura {reparto.factura_id} (HUÉRFANO)")
                huerfanos_encontrados.append(reparto)
        
        print(f"\nResumen:")
        print(f"- Repartos válidos: {validos}")
        print(f"- Repartos huérfanos: {len(huerfanos_encontrados)}")
        
        if huerfanos_encontrados:
            print(f"\nRepartos huérfanos a eliminar:")
            for reparto in huerfanos_encontrados:
                print(f"  - Reparto ID: {reparto.id}, Factura ID: {reparto.factura_id}")
            
            respuesta = input(f"\n¿Eliminar {len(huerfanos_encontrados)} repartos huérfanos? (s/N): ").strip().lower()
            
            if respuesta == 's':
                eliminados = 0
                for reparto in huerfanos_encontrados:
                    try:
                        reparto.delete_instance()
                        print(f"✓ Eliminado reparto {reparto.id}")
                        eliminados += 1
                    except Exception as e:
                        print(f"✗ Error eliminando reparto {reparto.id}: {e}")
                
                print(f"\nLimpieza completada:")
                print(f"- Repartos eliminados: {eliminados}")
                print(f"- Errores: {len(huerfanos_encontrados) - eliminados}")
                
                # Verificar que no quedan huérfanos
                print(f"\nVerificación post-limpieza:")
                repartos_restantes = Reparto.select()
                for reparto in repartos_restantes:
                    try:
                        factura = reparto.factura
                        print(f"✓ Reparto {reparto.id} -> Factura {factura.folio_interno}")
                    except DoesNotExist:
                        print(f"✗ ¡ADVERTENCIA! Reparto {reparto.id} sigue siendo huérfano")
            else:
                print("Limpieza cancelada por el usuario")
        else:
            print("\n✓ No se encontraron repartos huérfanos")
            
    except Exception as e:
        print(f"Error durante la limpieza: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if not db.is_closed():
            db.close()

if __name__ == "__main__":
    print("=== LIMPIEZA DE REPARTOS HUÉRFANOS ===")
    limpiar_repartos_huerfanos()
