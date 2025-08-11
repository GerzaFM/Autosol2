#!/usr/bin/env python3
"""
Script de prueba para verificar la integración de cheque_app_professional
con main_app sin problemas de imports.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_cheque_standalone():
    """Prueba que cheque_app_professional funcione standalone"""
    try:
        print("🔍 Probando cheque_app_professional standalone...")
        from src.chequeapp.cheque_app_professional import ChequeAppProfessional
        print("✅ Import standalone exitoso")
        return True
    except Exception as e:
        print(f"❌ Error en import standalone: {e}")
        return False

def test_cheque_from_main_app():
    """Prueba que cheque_app_professional funcione desde main_app"""
    try:
        print("🔍 Probando cheque_app_professional desde main_app context...")
        from app.ui.views.cheques_view import ChequesView
        print("✅ Import desde main_app exitoso")
        return True
    except Exception as e:
        print(f"❌ Error en import desde main_app: {e}")
        return False

def test_database_connection():
    """Prueba la conexión a base de datos de cheques"""
    try:
        print("🔍 Probando conexión a base de datos de cheques...")
        from src.chequeapp.cheque_database import ChequeDatabase
        db = ChequeDatabase()
        print("✅ Conexión a base de datos exitosa")
        return True
    except Exception as e:
        print(f"❌ Error en conexión a base de datos: {e}")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("=" * 60)
    print("🧪 PRUEBAS DE INTEGRACIÓN - CHEQUE APP PROFESSIONAL")
    print("=" * 60)
    
    tests = [
        test_cheque_standalone,
        test_cheque_from_main_app,
        test_database_connection
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Error ejecutando prueba {test.__name__}: {e}")
            results.append(False)
            print()
    
    print("=" * 60)
    print("📋 RESULTADOS:")
    print(f"✅ Pruebas exitosas: {sum(results)}")
    print(f"❌ Pruebas fallidas: {len(results) - sum(results)}")
    
    if all(results):
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✨ cheque_app_professional está correctamente integrado")
    else:
        print("⚠️  Algunas pruebas fallaron - revisar errores arriba")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
