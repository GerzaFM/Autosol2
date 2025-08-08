#!/usr/bin/env python3
"""
Migración: Cambiar campo 'folio' de IntegerField a CharField en tabla Factura.

Esta migración:
1. Crea una nueva columna 'folio_new' como CharField
2. Copia todos los datos de 'folio' a 'folio_new' (convirtiendo int → string)
3. Elimina la columna antigua 'folio'
4. Renombra 'folio_new' a 'folio'
5. Actualiza el modelo

IMPORTANTE: Hacer backup de la base de datos antes de ejecutar.
"""

import sys
import os
import sqlite3
from datetime import datetime

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def hacer_backup():
    """Crear backup de la base de datos antes de la migración."""
    try:
        db_path = "facturas.db"
        backup_path = f"facturas_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        if not os.path.exists(db_path):
            print(f"❌ No se encontró la base de datos: {db_path}")
            return False
        
        # Usar sqlite3 para hacer backup
        source = sqlite3.connect(db_path)
        backup = sqlite3.connect(backup_path)
        
        source.backup(backup)
        
        source.close()
        backup.close()
        
        print(f"✅ Backup creado: {backup_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear backup: {e}")
        return False

def migrar_folio_a_charfield():
    """Ejecutar la migración del campo folio."""
    
    print("🔄 Iniciando migración: folio IntegerField → CharField")
    print("=" * 60)
    
    # 1. Crear backup
    print("1. Creando backup de la base de datos...")
    if not hacer_backup():
        print("❌ No se pudo crear backup. Migración cancelada.")
        return False
    
    try:
        # 2. Conectar a la base de datos
        print("2. Conectando a la base de datos...")
        conn = sqlite3.connect("facturas.db")
        cursor = conn.cursor()
        
        # 3. Verificar estructura actual
        print("3. Verificando estructura actual...")
        cursor.execute("PRAGMA table_info(factura)")
        columnas = cursor.fetchall()
        
        print("   Columnas actuales de la tabla 'factura':")
        for col in columnas:
            if col[1] == 'folio':
                print(f"   - {col[1]}: {col[2]} (esta será migrada)")
            else:
                print(f"   - {col[1]}: {col[2]}")
        
        # 4. Verificar que el campo folio existe y es INTEGER
        folio_column = next((col for col in columnas if col[1] == 'folio'), None)
        if not folio_column:
            print("❌ No se encontró la columna 'folio'")
            return False
        
        if 'INTEGER' not in folio_column[2].upper():
            print(f"⚠️  La columna 'folio' ya es de tipo {folio_column[2]}")
            respuesta = input("¿Continuar de todas formas? (s/n): ").lower()
            if respuesta != 's':
                return False
        
        # 5. Contar registros actuales
        cursor.execute("SELECT COUNT(*) FROM factura")
        total_registros = cursor.fetchone()[0]
        print(f"   📊 Total de registros a migrar: {total_registros}")
        
        if total_registros > 0:
            # Mostrar algunos ejemplos
            cursor.execute("SELECT folio_interno, serie, folio LIMIT 5")
            ejemplos = cursor.fetchall()
            print("   📋 Ejemplos de folios actuales:")
            for ej in ejemplos:
                print(f"      Factura {ej[0]}: Serie='{ej[1]}', Folio={ej[2]} ({type(ej[2]).__name__})")
        
        # 6. Confirmar migración
        print("\n❓ ¿Proceder con la migración?")
        print("   - Se cambiará el campo 'folio' de INTEGER a TEXT")
        print(f"   - Se migrarán {total_registros} registros")
        print("   - El backup ya fue creado")
        
        confirmacion = input("\n¿Continuar? (escriba 'SI' para confirmar): ")
        if confirmacion != 'SI':
            print("❌ Migración cancelada por el usuario")
            return False
        
        # 7. Iniciar transacción
        print("\n🔄 Ejecutando migración...")
        cursor.execute("BEGIN TRANSACTION")
        
        # 8. Crear nueva columna temporal
        print("   - Creando nueva columna 'folio_new' como TEXT...")
        cursor.execute("ALTER TABLE factura ADD COLUMN folio_new TEXT")
        
        # 9. Copiar datos convertidos
        print("   - Copiando datos convertidos...")
        cursor.execute("""
            UPDATE factura 
            SET folio_new = CAST(folio AS TEXT)
            WHERE folio IS NOT NULL
        """)
        
        # También copiar NULLs si los hay
        cursor.execute("""
            UPDATE factura 
            SET folio_new = NULL
            WHERE folio IS NULL
        """)
        
        # 10. Verificar que la copia fue exitosa
        cursor.execute("SELECT COUNT(*) FROM factura WHERE folio IS NOT NULL AND folio_new IS NULL")
        fallos_copia = cursor.fetchone()[0]
        
        if fallos_copia > 0:
            print(f"❌ Error: {fallos_copia} registros no se copiaron correctamente")
            cursor.execute("ROLLBACK")
            return False
        
        # 11. Crear nueva tabla sin la columna antigua
        print("   - Reestructurando tabla...")
        
        # Obtener definición de tabla actual (sin la columna folio antigua)
        cursor.execute("PRAGMA table_info(factura)")
        columnas = cursor.fetchall()
        
        # Construir nueva definición de tabla
        nueva_definicion = []
        columnas_a_copiar = []
        
        for col in columnas:
            col_name = col[1]
            col_type = col[2]
            col_notnull = col[3]
            col_default = col[4]
            col_pk = col[5]
            
            if col_name == 'folio':
                # Saltar la columna antigua
                continue
            elif col_name == 'folio_new':
                # Renombrar folio_new a folio y cambiar tipo
                definicion_col = "folio TEXT"
                if col_notnull:
                    definicion_col += " NOT NULL"
                if col_default is not None:
                    definicion_col += f" DEFAULT {col_default}"
                nueva_definicion.append(definicion_col)
                columnas_a_copiar.append("folio_new")
            else:
                # Mantener columna como está
                definicion_col = f"{col_name} {col_type}"
                if col_notnull:
                    definicion_col += " NOT NULL"
                if col_default is not None:
                    definicion_col += f" DEFAULT {col_default}"
                if col_pk:
                    definicion_col += " PRIMARY KEY"
                nueva_definicion.append(definicion_col)
                columnas_a_copiar.append(col_name)
        
        # Crear nueva tabla
        nueva_tabla_sql = f"""
        CREATE TABLE factura_new (
            {', '.join(nueva_definicion)}
        )
        """
        
        print("   - Creando tabla temporal...")
        cursor.execute(nueva_tabla_sql)
        
        # Copiar todos los datos a la nueva tabla
        columnas_select = [col if col != "folio_new" else "folio_new AS folio" for col in columnas_a_copiar]
        columnas_insert = [col if col != "folio_new" else "folio" for col in columnas_a_copiar]
        
        cursor.execute(f"""
            INSERT INTO factura_new ({', '.join(columnas_insert)})
            SELECT {', '.join(columnas_select)}
            FROM factura
        """)
        
        # Verificar que se copiaron todos los registros
        cursor.execute("SELECT COUNT(*) FROM factura_new")
        registros_nuevos = cursor.fetchone()[0]
        
        if registros_nuevos != total_registros:
            print(f"❌ Error: Se esperaban {total_registros} registros, pero se copiaron {registros_nuevos}")
            cursor.execute("ROLLBACK")
            return False
        
        # 12. Reemplazar tabla antigua con nueva
        print("   - Reemplazando tabla antigua...")
        cursor.execute("DROP TABLE factura")
        cursor.execute("ALTER TABLE factura_new RENAME TO factura")
        
        # 13. Recrear índices si existían
        print("   - Recreando índices...")
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS ix_factura_proveedor_serie_folio 
            ON factura (proveedor, serie, folio)
        """)
        
        # 14. Confirmar transacción
        cursor.execute("COMMIT")
        
        # 15. Verificar resultado final
        print("   - Verificando resultado...")
        cursor.execute("PRAGMA table_info(factura)")
        columnas_finales = cursor.fetchall()
        
        folio_final = next((col for col in columnas_finales if col[1] == 'folio'), None)
        if folio_final and 'TEXT' in folio_final[2]:
            print(f"   ✅ Campo 'folio' ahora es: {folio_final[2]}")
        else:
            print(f"   ⚠️  Campo 'folio': {folio_final}")
        
        # Mostrar algunos ejemplos migrados
        cursor.execute("SELECT folio_interno, serie, folio LIMIT 5")
        ejemplos_finales = cursor.fetchall()
        print("   📋 Ejemplos de folios migrados:")
        for ej in ejemplos_finales:
            print(f"      Factura {ej[0]}: Serie={ej[1]}, Folio='{ej[2]}' ({type(ej[2]).__name__})")
        
        conn.close()
        
        print("\n🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
        print("=" * 60)
        print("✅ El campo 'folio' ahora es CharField (TEXT)")
        print("✅ Todos los datos se migraron correctamente")
        print("✅ Los folios alfanuméricos ahora son compatibles")
        print("\n💡 Ahora puedes usar folios como: '000456H', 'FT-001', etc.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        try:
            cursor.execute("ROLLBACK")
            print("🔄 Transacción revertida")
        except:
            pass
        return False

def main():
    """Función principal."""
    print("🔧 MIGRACIÓN DE BASE DE DATOS")
    print("Cambiar campo 'folio' de IntegerField a CharField")
    print("=" * 60)
    
    # Verificar que existe la base de datos
    if not os.path.exists("facturas.db"):
        print("❌ No se encontró la base de datos 'facturas.db'")
        print("   Asegúrate de ejecutar este script desde el directorio raíz del proyecto")
        return
    
    # Ejecutar migración
    exito = migrar_folio_a_charfield()
    
    if exito:
        print("\n🎯 PRÓXIMOS PASOS:")
        print("1. Verificar que la aplicación funciona correctamente")
        print("2. Probar carga de XML con folios alfanuméricos")
        print("3. Si todo funciona bien, puedes eliminar el backup")
    else:
        print("\n💔 La migración falló")
        print("1. Revisa los errores arriba")
        print("2. La base de datos no fue modificada")
        print("3. El backup sigue disponible por seguridad")

if __name__ == "__main__":
    main()
