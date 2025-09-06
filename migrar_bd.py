#!/usr/bin/env python3
"""
Script de migración de base de datos
Migra proveedores, usuarios y bancos de la base de datos actual a un servidor local
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Configurar logging sin emojis para compatibilidad Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'migracion_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Importar modelos y configuración
try:
    from src.bd.models import Proveedor, Usuario, Banco, db
    from config.settings import DatabaseConfig
    from peewee import PostgresqlDatabase, SqliteDatabase, DoesNotExist
except ImportError as e:
    logger.error(f"Error importando dependencias: {e}")
    sys.exit(1)

class MigradorBD:
    """Clase para manejar la migración de base de datos"""
    
    def __init__(self):
        self.db_origen = None
        self.db_destino = None
        self.estadisticas = {
            'proveedores': {'migrados': 0, 'errores': 0},
            'usuarios': {'migrados': 0, 'errores': 0},
            'bancos': {'migrados': 0, 'errores': 0}
        }
    
    def configurar_base_datos_origen(self):
        """Configura la conexión a la base de datos de origen (PostgreSQL tcm_matehuala)"""
        logger.info("Configurando base de datos ORIGEN: PostgreSQL tcm_matehuala...")
        
        try:
            self.db_origen = PostgresqlDatabase(
                database="tcm_matehuala",
                host="localhost",
                port=5432,
                user="postgres",
                password="Nissan#2024",
                autorollback=True
            )
            
            # Probar conexión
            self.db_origen.connect()
            
            # Verificar que las tablas existen
            cursor = self.db_origen.execute_sql("SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename IN ('proveedores', 'usuarios', 'bancos')")
            tablas = [row[0] for row in cursor.fetchall()]
            
            self.db_origen.close()
            
            logger.info(f"OK - Conectado a PostgreSQL ORIGEN: localhost/tcm_matehuala")
            logger.info(f"OK - Tablas encontradas: {', '.join(tablas)}")
            
            if not tablas:
                logger.warning("ADVERTENCIA - No se encontraron las tablas esperadas (proveedores, usuarios, bancos)")
                return None
                
            return "postgresql"
            
        except Exception as e:
            logger.error(f"ERROR - Error conectando a PostgreSQL ORIGEN: {e}")
            logger.error("   Verifique que PostgreSQL este corriendo y las credenciales sean correctas")
            return None
    
    def configurar_base_datos_destino(self):
        """Configura la conexión a la base de datos de destino (PostgreSQL autoforms)"""
        logger.info("Configurando base de datos DESTINO: PostgreSQL autoforms...")
        print("*** Configuracion de base de datos DESTINO ***")
        print("=" * 50)
        print("Servidor: 10.90.101.51")
        print("Base de datos: autoforms")
        print("Usuario: sistemas")
        print("Puerto: 5432")
        print("=" * 50)
        
        password = input("Ingrese la contraseña para el usuario 'sistemas': ").strip()
        
        if not password:
            logger.error("ERROR - La contraseña es obligatoria")
            return None
        
        try:
            self.db_destino = PostgresqlDatabase(
                database="autoforms",
                host="10.90.101.51",
                port=5432,
                user="sistemas",
                password=password,
                autorollback=True,
                autocommit=True
            )
            
            # Probar conexión
            logger.info("Probando conexión a servidor destino...")
            self.db_destino.connect()
            
            # Verificar permisos
            cursor = self.db_destino.execute_sql("SELECT current_user, current_database()")
            user_info = cursor.fetchone()
            
            self.db_destino.close()
            
            logger.info(f"OK - Conexión exitosa a PostgreSQL DESTINO: 10.90.101.51/autoforms")
            logger.info(f"OK - Usuario conectado: {user_info[0]}")
            logger.info(f"OK - Base de datos: {user_info[1]}")
            
            return "postgresql"
            
        except Exception as e:
            logger.error(f"ERROR - Error conectando a PostgreSQL DESTINO: {e}")
            logger.error("   Verifique la conectividad de red, credenciales y permisos")
            return None
    
    def crear_tablas_destino(self):
        """Crea las tablas en la base de datos destino"""
        logger.info("Creando tablas en base de datos destino...")
        
        # Cambiar la conexión de los modelos temporalmente
        modelos_originales_db = []
        for modelo in [Proveedor, Usuario, Banco]:
            modelos_originales_db.append(modelo._meta.database)
            modelo._meta.database = self.db_destino
        
        try:
            self.db_destino.connect()
            
            # Crear tablas
            self.db_destino.create_tables([Proveedor, Usuario, Banco], safe=True)
            logger.info("OK - Tablas creadas exitosamente")
            
            self.db_destino.close()
            
        except Exception as e:
            logger.error(f"ERROR - Error creando tablas: {e}")
            raise
        finally:
            # Restaurar conexiones originales
            for i, modelo in enumerate([Proveedor, Usuario, Banco]):
                modelo._meta.database = modelos_originales_db[i]
    
    def migrar_proveedores(self):
        """Migra todos los proveedores"""
        logger.info("Migrando proveedores...")
        
        try:
            # Configurar modelos para origen
            Proveedor._meta.database = self.db_origen
            self.db_origen.connect()
            
            proveedores_origen = list(Proveedor.select())
            total = len(proveedores_origen)
            logger.info(f"Encontrados {total} proveedores para migrar")
            
            self.db_origen.close()
            
            # Configurar modelos para destino
            Proveedor._meta.database = self.db_destino
            self.db_destino.connect()
            
            for i, proveedor in enumerate(proveedores_origen, 1):
                try:
                    # Crear nuevo proveedor en destino
                    Proveedor.create(
                        codigo_quiter=proveedor.codigo_quiter,
                        nombre=proveedor.nombre,
                        nombre_en_quiter=proveedor.nombre_en_quiter,
                        rfc=proveedor.rfc,
                        telefono=proveedor.telefono,
                        email=proveedor.email,
                        nombre_contacto=proveedor.nombre_contacto,
                        cuenta_mayor=proveedor.cuenta_mayor
                    )
                    
                    self.estadisticas['proveedores']['migrados'] += 1
                    
                    if i % 10 == 0:
                        logger.info(f"Progreso proveedores: {i}/{total}")
                        
                except Exception as e:
                    logger.error(f"ERROR - Error migrando proveedor {proveedor.id}: {e}")
                    self.estadisticas['proveedores']['errores'] += 1
            
            self.db_destino.close()
            logger.info(f"OK - Migración de proveedores completada: {self.estadisticas['proveedores']['migrados']} exitosos")
            
        except Exception as e:
            logger.error(f"ERROR - Error general migrando proveedores: {e}")
    
    def migrar_usuarios(self):
        """Migra todos los usuarios"""
        logger.info("Migrando usuarios...")
        
        try:
            # Configurar modelos para origen
            Usuario._meta.database = self.db_origen
            self.db_origen.connect()
            
            usuarios_origen = list(Usuario.select())
            total = len(usuarios_origen)
            logger.info(f"Encontrados {total} usuarios para migrar")
            
            self.db_origen.close()
            
            # Configurar modelos para destino
            Usuario._meta.database = self.db_destino
            self.db_destino.connect()
            
            for i, usuario in enumerate(usuarios_origen, 1):
                try:
                    # Crear nuevo usuario en destino
                    Usuario.create(
                        codigo=usuario.codigo,
                        nombre=usuario.nombre,
                        empresa=usuario.empresa,
                        centro=usuario.centro,
                        sucursal=usuario.sucursal,
                        marca=usuario.marca,
                        email=usuario.email,
                        permisos=usuario.permisos,
                        responsable=usuario.responsable,
                        username=usuario.username,
                        password=usuario.password
                    )
                    
                    self.estadisticas['usuarios']['migrados'] += 1
                    
                    if i % 10 == 0:
                        logger.info(f"Progreso usuarios: {i}/{total}")
                        
                except Exception as e:
                    logger.error(f"ERROR - Error migrando usuario {usuario.codigo}: {e}")
                    self.estadisticas['usuarios']['errores'] += 1
            
            self.db_destino.close()
            logger.info(f"OK - Migración de usuarios completada: {self.estadisticas['usuarios']['migrados']} exitosos")
            
        except Exception as e:
            logger.error(f"ERROR - Error general migrando usuarios: {e}")
    
    def migrar_bancos(self):
        """Migra todos los bancos"""
        logger.info("Migrando bancos...")
        
        try:
            # Configurar modelos para origen
            Banco._meta.database = self.db_origen
            self.db_origen.connect()
            
            bancos_origen = list(Banco.select())
            total = len(bancos_origen)
            logger.info(f"Encontrados {total} bancos para migrar")
            
            self.db_origen.close()
            
            # Configurar modelos para destino
            Banco._meta.database = self.db_destino
            self.db_destino.connect()
            
            for i, banco in enumerate(bancos_origen, 1):
                try:
                    # Crear nuevo banco en destino
                    Banco.create(
                        nombre=banco.nombre,
                        cuenta=banco.cuenta,
                        codigo=banco.codigo,
                        cuenta_mayor=banco.cuenta_mayor
                    )
                    
                    self.estadisticas['bancos']['migrados'] += 1
                    
                    logger.info(f"Progreso bancos: {i}/{total}")
                        
                except Exception as e:
                    logger.error(f"ERROR - Error migrando banco {banco.id}: {e}")
                    self.estadisticas['bancos']['errores'] += 1
            
            self.db_destino.close()
            logger.info(f"OK - Migración de bancos completada: {self.estadisticas['bancos']['migrados']} exitosos")
            
        except Exception as e:
            logger.error(f"ERROR - Error general migrando bancos: {e}")
    
    def mostrar_resumen(self):
        """Muestra el resumen final de la migración"""
        print("\n" + "="*60)
        print("*** RESUMEN DE MIGRACION ***")
        print("="*60)
        
        total_migrados = 0
        total_errores = 0
        
        for entidad, stats in self.estadisticas.items():
            migrados = stats['migrados']
            errores = stats['errores']
            total = migrados + errores
            
            total_migrados += migrados
            total_errores += errores
            
            print(f"* {entidad.capitalize()}:")
            print(f"   OK - Migrados: {migrados}")
            print(f"   ERROR - Errores: {errores}")
            print(f"   TOTAL - Procesados: {total}")
            
            if total > 0:
                exito_pct = (migrados / total) * 100
                print(f"   TASA - Exito: {exito_pct:.1f}%")
            print()
        
        print(f"*** TOTALES GENERALES ***")
        print(f"   OK - Total migrados: {total_migrados}")
        print(f"   ERROR - Total errores: {total_errores}")
        print(f"   TOTAL - Total procesados: {total_migrados + total_errores}")
        
        if (total_migrados + total_errores) > 0:
            exito_general = (total_migrados / (total_migrados + total_errores)) * 100
            print(f"   GENERAL - Tasa de éxito: {exito_general:.1f}%")
        
        print("="*60)
    
    def ejecutar_migracion(self):
        """Ejecuta todo el proceso de migración"""
        print("*** MIGRACION DE BASE DE DATOS ***")
        print("="*60)
        print("* ORIGEN:  PostgreSQL localhost/tcm_matehuala")
        print("* DESTINO: PostgreSQL 10.90.101.51/autoforms")
        print("="*60)
        print("Este script migrará:")
        print("• Proveedores")
        print("• Usuarios") 
        print("• Bancos")
        print("="*60)
        
        continuar = input("¿Desea continuar con la migración? (s/N): ").strip().lower()
        if continuar not in ['s', 'si', 'sí', 'y', 'yes']:
            logger.info("Migración cancelada por el usuario")
            return False
        
        # Paso 1: Configurar base de datos origen
        logger.info("PASO 1: Configurando conexión ORIGEN...")
        tipo_origen = self.configurar_base_datos_origen()
        if not tipo_origen:
            logger.error("ERROR - No se pudo configurar la base de datos origen")
            return False
        
        # Paso 2: Configurar base de datos destino
        logger.info("PASO 2: Configurando conexión DESTINO...")
        tipo_destino = self.configurar_base_datos_destino()
        if not tipo_destino:
            logger.error("ERROR - No se pudo configurar la base de datos destino")
            return False
        
        # Paso 3: Crear tablas en destino
        logger.info("PASO 3: Creando tablas en destino...")
        try:
            self.crear_tablas_destino()
        except Exception as e:
            logger.error(f"ERROR - Error creando tablas destino: {e}")
            return False
        
        # Paso 4: Ejecutar migraciones
        logger.info("PASO 4: Iniciando migración de datos...")
        self.migrar_proveedores()
        self.migrar_usuarios()
        self.migrar_bancos()
        
        # Paso 5: Mostrar resumen
        self.mostrar_resumen()
        
        return True

def main():
    """Función principal"""
    try:
        migrador = MigradorBD()
        exito = migrador.ejecutar_migracion()
        
        if exito:
            logger.info("*** Migración completada exitosamente ***")
        else:
            logger.error("ERROR - Migración falló o fue cancelada")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\nMigración cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"ERROR - Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
