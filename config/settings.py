"""
Configuración principal de la aplicación.
"""
import os
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List
from decouple import config as env_config, Csv

# =============================================================================
# CONFIGURACIÓN DE ENTORNO - CAMBIAR AQUÍ PARA ELEGIR BASE DE DATOS
# =============================================================================
# Opciones disponibles: 'test' o 'production'
ENVIRONMENT = 'production'  # Cambiar a 'production' para usar la base centralizada
# =============================================================================

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
APP_DIR = PROJECT_ROOT / "app"
CONFIG_DIR = PROJECT_ROOT / "config"
DATABASE_DIR = PROJECT_ROOT / "database"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
LOGS_DIR = PROJECT_ROOT / "logs"

DBCONF_PATH = PROJECT_ROOT / ("connections_test.json" if ENVIRONMENT == "test" else "connections.json")

# Crear directorios si no existen
for directory in [DATABASE_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Función para cargar configuración JSON
def load_json_config():
    """Carga la configuración desde el archivo JSON correspondiente al entorno."""
    try:
        config_data = json.loads(DBCONF_PATH.read_text(encoding='utf-8'))
        return config_data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[WARNING] No se pudo cargar {DBCONF_PATH}: {e}")
        return {}

def write_version_to_json(version: str):
    """Escribe la versión actual en el archivo JSON de configuración."""
    try:
        # Cargar configuración actual
        if DBCONF_PATH.exists():
            config_data = json.loads(DBCONF_PATH.read_text(encoding='utf-8'))
        else:
            print(f"[WARNING] Archivo {DBCONF_PATH} no existe, creando configuración básica")
            config_data = {}
        
        # Agregar/actualizar versión
        config_data['version'] = version
        
        # Escribir de vuelta al archivo con formato legible
        DBCONF_PATH.write_text(
            json.dumps(config_data, indent=4, ensure_ascii=False),
            encoding='utf-8'
        )
        
        print(f"[CONFIG] Versión {version} escrita en {DBCONF_PATH}")
        return True
        
    except Exception as e:
        print(f"[ERROR] No se pudo escribir versión en {DBCONF_PATH}: {e}")
        return False

# Cargar configuración global
_json_config = load_json_config()

@dataclass
class DatabaseConfig:
    """Configuración de la base de datos PostgreSQL con soporte para TEST y PRODUCTION."""
    # Configuración dinámica basada en ENVIRONMENT
    db_type: str = "postgresql"
    pg_host: str = ""
    pg_port: int = 5432
    pg_database: str = ""
    pg_user: str = ""
    pg_password: str = ""

    config: Dict = None
    
    def __post_init__(self):
        """Configurar base de datos según el entorno elegido."""
        global ENVIRONMENT
        
        # Usar configuración JSON global cargada
        if _json_config:
            # Usar configuración del archivo JSON
            self.pg_host = _json_config.get('ip', '')
            self.pg_port = int(_json_config.get('port', 5432))
            self.pg_database = _json_config.get('dbname', '')
            self.pg_user = _json_config.get('user', '')
            self.pg_password = _json_config.get('password', '')
        else:
            print(f"[FALLBACK] Usando configuración por defecto para entorno: {ENVIRONMENT}")
        
        # Las variables de entorno pueden sobrescribir la configuración del archivo JSON
        try:
            from decouple import config as env_config
            self.db_type = env_config('DB_TYPE', default=self.db_type)
            self.pg_host = env_config('DB_HOST', default=self.pg_host)
            self.pg_port = env_config('DB_PORT', default=self.pg_port, cast=int)
            self.pg_database = env_config('DB_NAME', default=self.pg_database)
            self.pg_user = env_config('DB_USER', default=self.pg_user)
            self.pg_password = env_config('DB_PASSWORD', default=self.pg_password)
        except ImportError:
            # python-decouple no disponible, usar valores del archivo JSON
            pass
        
        # Log de configuración (sin mostrar contraseña)
        print(f"[CONFIG] Entorno: {ENVIRONMENT.upper()}")
        print(f"[CONFIG] Base de datos: {self.pg_host}:{self.pg_port}/{self.pg_database}")
        print(f"[CONFIG] Usuario: {self.pg_user}")
    
    def get_connection_info(self):
        """Retorna información de conexión para logging."""
        return {
            'environment': ENVIRONMENT,
            'host': self.pg_host,
            'port': self.pg_port,
            'database': self.pg_database,
            'user': self.pg_user
        }

@dataclass
class UIConfig:
    """Configuración de la interfaz de usuario."""
    theme: str = ""
    window_size: str = "1200x900"
    #1200x768
    min_window_size: tuple = (800, 600)
    sidebar_width_expanded: int = 200
    sidebar_width_collapsed: int = 60
    
    def __post_init__(self):
        """Configurar UI usando el archivo JSON."""
        # Cargar tema desde configuración JSON, con fallback a 'cosmo'
        self.theme = _json_config.get("theme", "cosmo")

@dataclass
class BusinessConfig:
    """Configuración de reglas de negocio."""
    max_conceptos_recomendados: int = 10
    categorias: List[str] = None
    tipos_vale: Dict[str, str] = None
    
    def __post_init__(self):
        if self.categorias is None:
            self.categorias = ["Comer", "Fleet", "Semis", "Refa", "Serv", "HyP", "Admin"]
        
        if self.tipos_vale is None:
            self.tipos_vale = {
                "VC": "VALE DE CONTROL",
                "VG": "VALE DE GASTOS",
                "VP": "VALE DE PEDIDO",
                "VS": "VALE DE SERVICIO"
            }

@dataclass
class AppConfig:
    """Configuración general de la aplicación."""
    app_name: str = "Autoforms"
    version: str = "0.3.3"
    author: str = "Gerzahin Flores Martinez"

    # Escribir en JSON la versión actual
    

    # Configuraciones específicas
    database: DatabaseConfig = None
    ui: UIConfig = None
    business: BusinessConfig = None
    
    # Configuración de logging
    log_level: str = "INFO"
    log_file: str = str(LOGS_DIR / "app.log")
    
    # GitHub repo para actualizaciones
    github_repo: str = "GerzaFM/Autosol2"
    
    # Valores por defecto
    default_values: Dict[str, str] = None
    
    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig()
        if self.ui is None:
            self.ui = UIConfig()
        if self.business is None:
            self.business = BusinessConfig()
        if self.default_values is None:
            self.default_values = {
                "tipo_solicitud": "VC - VALE DE CONTROL",
                "departamento": "ADMINISTRACION",
                "receptor_nombre": "TCM MATEHUALA",
                "receptor_rfc": "TMM860630PH1"
            }
        
        # Escribir versión actual en el archivo JSON
        write_version_to_json(self.version)

# Instancia global de configuración
config = AppConfig()

# Mensajes de error centralizados
ERROR_MESSAGES = {
    "sin_conceptos": "Debe agregar al menos un concepto.",
    "demasiados_conceptos": f"Hay más de {config.business.max_conceptos_recomendados} conceptos. ¿Desea crear un concepto general?",
    "no_datos": "No hay datos cargados para procesar.",
    "suma_categorias": "La suma de las categorías debe ser exactamente 100%.",
    "validacion_proveedor": "Los datos del proveedor son obligatorios.",
    "archivo_no_encontrado": "El archivo especificado no fue encontrado.",
    "error_base_datos": "Error al acceder a la base de datos.",
    "error_xml": "Error al procesar el archivo XML.",
    "error_pdf": "Error al generar el documento PDF."
}

# Configuraciones de columnas para la tabla
COLUMN_WIDTHS = {
    "Cantidad": 80,
    "Descripción": 300,
    "Precio": 120,
    "Total": 120
}

# Configuraciones de ventanas y popups
WINDOW_SIZES = {
    "main_window": "1200x900",
    "popup_favoritos": "600x280",
    "popup_concepto": "500x400",
    "popup_confirmacion": "400x200",
    "popup_error": "450x250"
}

# Configuraciones de UI adicionales
UI_CONSTANTS = {
    "sidebar_animation_duration": 200,
    "popup_center_offset": 50,
    "button_min_width": 120,
    "entry_standard_width": 200
}
