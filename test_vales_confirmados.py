#!/usr/bin/env python3
"""
Test específico solo para documentos que confirmamos que son vales.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.buscarapp.autocarga.autocarga import AutoCarga

def test_vales_confirmados():
    """
    Prueba solo con documentos que sabemos que son vales válidos.
    """
    print("🎯 PRUEBA ESPECÍFICA - SOLO VALES CONFIRMADOS")
    print("=" * 60)
    
    # Documentos que sabemos que son vales
    vales_confirmados = [
        "15gerzahin.flores_QRSVCMX_V152266_180646_CD.pdf"  # Este vale que acabamos de verificar
    ]
    
    autocarga = AutoCarga()
    
    for vale_file in vales_confirmados:
        pdf_path = os.path.join("Pruebas", vale_file)
        
        if os.path.exists(pdf_path):
            print(f"📄 Procesando: {vale_file}")
            # Procesar solo este archivo
            autocarga.procesar_directorio("Pruebas", filtro_archivo=vale_file)
        else:
            print(f"❌ No se encontró: {vale_file}")

if __name__ == "__main__":
    test_vales_confirmados()
