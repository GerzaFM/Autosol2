#!/usr/bin/env python3
"""
Migración simple: folio INTEGER → TEXT
"""
import sqlite3
from datetime import datetime

def migrar():
    # Backup
    print('🔄 Creando backup...')
    backup_path = f'facturas_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    source = sqlite3.connect('facturas.db')
    backup = sqlite3.connect(backup_path)
    source.backup(backup)
    source.close()
    backup.close()
    print(f'✅ Backup: {backup_path}')

    # Migración
    print('🔄 Migrando campo folio de INTEGER a TEXT...')
    conn = sqlite3.connect('facturas.db')
    cursor = conn.cursor()

    # Verificar estado actual
    cursor.execute('SELECT COUNT(*) FROM factura')
    total = cursor.fetchone()[0]
    print(f'📊 Registros: {total}')

    cursor.execute('SELECT folio_interno, serie, folio FROM factura LIMIT 3')
    ejemplos = cursor.fetchall()
    print('📋 Antes:')
    for ej in ejemplos:
        print(f'   {ej[0]}: {ej[1]}-{ej[2]} (int)')

    cursor.execute('BEGIN TRANSACTION')
    
    try:
        # Crear nueva tabla con folio como TEXT
        cursor.execute('''
            CREATE TABLE factura_new (
                folio_interno INTEGER PRIMARY KEY,
                serie TEXT,
                folio TEXT,
                fecha DATE,
                tipo TEXT,
                nombre_emisor TEXT,
                rfc_emisor TEXT,
                nombre_receptor TEXT,
                rfc_receptor TEXT,
                subtotal DECIMAL(10, 5),
                ret_iva DECIMAL(10, 5),
                ret_isr DECIMAL(10, 5),
                iva_trasladado DECIMAL(10, 5),
                total DECIMAL(10, 5),
                comentario TEXT,
                proveedor_id INTEGER,
                layout_id INTEGER,
                cargada BOOLEAN,
                pagada BOOLEAN,
                clase TEXT,
                fecha_emision DATE,
                departamento VARCHAR(255),
                cuenta_mayor INTEGER
            )
        ''')
        
        # Copiar datos (convirtiendo folio a texto)
        cursor.execute('''
            INSERT INTO factura_new 
            SELECT folio_interno, serie, CAST(folio AS TEXT), fecha, tipo, 
                   nombre_emisor, rfc_emisor, nombre_receptor, rfc_receptor, 
                   subtotal, ret_iva, ret_isr, iva_trasladado, total, 
                   comentario, proveedor_id, layout_id, cargada, pagada, 
                   clase, fecha_emision, departamento, cuenta_mayor
            FROM factura
        ''')
        
        # Verificar
        cursor.execute('SELECT COUNT(*) FROM factura_new')
        nuevos = cursor.fetchone()[0]
        if nuevos != total:
            raise Exception(f'Error en copia: {total} → {nuevos}')
        
        # Reemplazar
        cursor.execute('DROP TABLE factura')
        cursor.execute('ALTER TABLE factura_new RENAME TO factura')
        
        # Recrear índice
        cursor.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS ix_factura_proveedor_serie_folio 
            ON factura (proveedor_id, serie, folio)
        ''')
        
        cursor.execute('COMMIT')
        
        # Verificar resultado
        cursor.execute('PRAGMA table_info(factura)')
        cols = cursor.fetchall()
        folio_col = next((c for c in cols if c[1] == 'folio'), None)
        print(f'✅ Campo folio: {folio_col[2]}')
        
        cursor.execute('SELECT folio_interno, serie, folio FROM factura LIMIT 3')
        ejemplos_final = cursor.fetchall()
        print('📋 Después:')
        for ej in ejemplos_final:
            print(f'   {ej[0]}: {ej[1]}-"{ej[2]}" (text)')
        
        print('🎉 ¡MIGRACIÓN EXITOSA!')
        print('✅ Folios alfanuméricos como "000456H" ahora funcionan')
        
    except Exception as e:
        cursor.execute('ROLLBACK')
        print(f'❌ Error: {e}')
        
    conn.close()

if __name__ == "__main__":
    migrar()
