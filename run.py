#!/usr/bin/env python3
"""
Script de arranque simplificado para TCM Matehuala.
"""
import os
import sys
from pathlib import Path

# Asegurar que estamos en el directorio correcto
PROJECT_ROOT = Path(__file__).parent
os.chdir(PROJECT_ROOT)

# Ejecutar la aplicación principal
try:
    from main_app import main
    main()
except ImportError:
    print("Error: No se pudo importar la aplicación principal.")
    print("Asegúrese de que todas las dependencias estén instaladas:")
    print("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"Error al ejecutar la aplicación: {e}")
    sys.exit(1)
