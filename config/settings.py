"""
Configuración principal de la aplicación.
"""
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List
from decouple import config as env_config, Csv

# =============================================================================
# CONFIGURACIÓN DE ENTORNO - CAMBIAR AQUÍ PARA ELEGIR BASE DE DATOS
# =============================================================================
# Opciones disponibles: 'test' o 'production'
ENVIRONMENT = 'test'  # Cambiar a 'production' para usar la base centralizada
# =============================================================================

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
APP_DIR = PROJECT_ROOT / "app"
CONFIG_DIR = PROJECT_ROOT / "config"
DATABASE_DIR = PROJECT_ROOT / "database"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
LOGS_DIR = PROJECT_ROOT / "logs"

# Crear directorios si no existen
for directory in [DATABASE_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

@dataclass
class DatabaseConfig:
    """Configuración de la base de datos con soporte para TEST y PRODUCTION."""
    # SQLite (desarrollo/fallback)
    sqlite_path: str = str(DATABASE_DIR / "facturas.db")
    backup_dir: str = str(DATABASE_DIR / "backups")
    
    # Configuración dinámica basada en ENVIRONMENT
    db_type: str = "postgresql"
    pg_host: str = ""
    pg_port: int = 5432
    pg_database: str = ""
    pg_user: str = ""
    pg_password: str = ""
    
    def __post_init__(self):
        """Configurar base de datos según el entorno elegido."""
        global ENVIRONMENT
        
        if ENVIRONMENT.lower() == 'test':
            # Configuración para TEST (tcm_matehuala local)
            self.pg_host = "localhost"
            self.pg_database = "tcm_matehuala"
            self.pg_user = "postgres"
            self.pg_password = "Nissan#2024"
            
        elif ENVIRONMENT.lower() == 'production':
            # Configuración para PRODUCTION (autoforms servidor)
            self.pg_host = "10.90.101.51"
            self.pg_database = "autoforms"
            self.pg_user = "sistemas"
            self.pg_password = "Postgresql#495"
            
        else:
            raise ValueError(f"ENVIRONMENT debe ser 'test' o 'production', recibido: {ENVIRONMENT}")
        
        # Intentar leer desde variables de entorno (opcional)
        try:
            from decouple import config as env_config
            self.db_type = env_config('DB_TYPE', default=self.db_type)
            self.pg_host = env_config('DB_HOST', default=self.pg_host)
            self.pg_port = env_config('DB_PORT', default=self.pg_port, cast=int)
            self.pg_database = env_config('DB_NAME', default=self.pg_database)
            self.pg_user = env_config('DB_USER', default=self.pg_user)
            self.pg_password = env_config('DB_PASSWORD', default=self.pg_password)
        except ImportError:
            # python-decouple no disponible, usar valores configurados
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
    theme: str = "cosmo"
    window_size: str = "1200x900"
    #1200x768
    min_window_size: tuple = (800, 600)
    sidebar_width_expanded: int = 200
    sidebar_width_collapsed: int = 60

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
