"""
Configuración para desarrollo.
Sobrescribe algunas configuraciones para facilitar el desarrollo.
"""
from config.settings import config

# Configuración de desarrollo
config.log_level = "DEBUG"
config.ui.theme = "darkly"  # Tema oscuro para desarrollo

# Configuración de base de datos para desarrollo
config.database.path = str(config.database.path).replace(".db", "_dev.db")

print(f"Configuración de desarrollo cargada")
print(f"Base de datos: {config.database.path}")
print(f"Nivel de log: {config.log_level}")
