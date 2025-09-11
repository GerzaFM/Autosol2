"""
Script para crear releases automáticamente en GitHub.
"""
import subprocess
import sys
from pathlib import Path

# Agregar directorios al path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import config

def create_release():
    """Crea una nueva release en GitHub."""
    version = config.version
    tag_name = f"v{version}"
    release_name = f"Autoforms v{version}"
    
    print(f"🏷️ Creando release: {tag_name}")
    print(f"📝 Nombre: {release_name}")
    
    # Verificar si git está configurado
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Error: No es un repositorio git o git no está disponible")
            return False
    except FileNotFoundError:
        print("❌ Error: Git no está instalado")
        return False
    
    # Crear tag
    print("🔖 Creando tag...")
    result = subprocess.run(['git', 'tag', '-a', tag_name, '-m', release_name], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error creando tag: {result.stderr}")
        return False
    
    # Push tag
    print("🚀 Subiendo tag a GitHub...")
    result = subprocess.run(['git', 'push', 'origin', tag_name], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error subiendo tag: {result.stderr}")
        return False
    
    print("✅ Release creada exitosamente!")
    print(f"🌐 Revisa: https://github.com/GerzaFM/Autosol2/releases/tag/{tag_name}")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--confirm":
        create_release()
    else:
        print("⚠️ Este script creará una release en GitHub")
        print(f"🏷️ Tag: v{config.version}")
        print(f"📝 Nombre: Autoforms v{config.version}")
        print("")
        print("Para confirmar, ejecuta: python create_release.py --confirm")