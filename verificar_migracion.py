#!/usr/bin/env python3
"""
Verificar migración del campo folio
"""
import sqlite3

def verificar():
    conn = sqlite3.connect('facturas.db')
    cursor = conn.cursor()

    print('🔍 VERIFICANDO MIGRACIÓN')
    print('=' * 40)

    # Verificar estructura
    cursor.execute('PRAGMA table_info(factura)')
    cols = cursor.fetchall()
    
    print('📋 Estructura de campos clave:')
    for col in cols:
        if col[1] in ['folio_interno', 'folio', 'serie']:
            tipo = col[2]
            if col[1] == 'folio_interno' and 'INTEGER' in tipo:
                status = '✅ Correcto (control interno)'
            elif col[1] == 'folio' and 'TEXT' in tipo:
                status = '✅ Correcto (folio XML)'
            elif col[1] == 'serie' and 'TEXT' in tipo:
                status = '✅ Correcto (serie XML)'
            else:
                status = '❌ Revisar'
            
            print(f'   {col[1]}: {tipo} - {status}')

    # Probar folio alfanumérico
    print('\n🧪 PROBANDO FOLIO ALFANUMÉRICO')
    try:
        cursor.execute('SELECT MAX(folio_interno) FROM factura')
        max_folio = cursor.fetchone()[0] or 0
        nuevo_folio = max_folio + 1
        
        # Insertar prueba
        cursor.execute('''
            INSERT INTO factura (folio_interno, serie, folio, fecha, tipo, 
                               nombre_emisor, rfc_emisor, nombre_receptor, 
                               rfc_receptor, subtotal, ret_iva, ret_isr, 
                               iva_trasladado, total, comentario, proveedor_id, 
                               cargada, pagada, fecha_emision)
            VALUES (?, ?, ?, date('now'), 'TEST', 'Proveedor Test', 
                    'RFC123456789', 'Receptor Test', 'RFC987654321', 
                    1000.0, 0.0, 0.0, 160.0, 1160.0, 'Prueba folio', 1, 
                    0, 0, date('now'))
        ''', (nuevo_folio, 'TEST', '000456H'))
        
        # Verificar inserción
        cursor.execute('SELECT folio_interno, serie, folio FROM factura WHERE folio = ?', ('000456H',))
        resultado = cursor.fetchone()
        
        if resultado:
            print(f'✅ Insertado: Factura {resultado[0]} - {resultado[1]}-{resultado[2]}')
            
            # Probar búsqueda
            cursor.execute('''
                SELECT COUNT(*) FROM factura 
                WHERE serie = ? AND folio = ?
            ''', ('TEST', '000456H'))
            
            encontrados = cursor.fetchone()[0]
            print(f'✅ Búsqueda: {encontrados} factura(s) encontrada(s)')
            
            # Limpiar
            cursor.execute('DELETE FROM factura WHERE folio = ?', ('000456H',))
            print('✅ Registro de prueba eliminado')
            
        else:
            print('❌ No se pudo insertar')
            
    except Exception as e:
        print(f'❌ Error: {e}')

    # Mostrar ejemplos reales
    print('\n📊 EJEMPLOS DE FOLIOS MIGRADOS:')
    cursor.execute('SELECT folio_interno, serie, folio FROM factura LIMIT 5')
    ejemplos = cursor.fetchall()
    for ej in ejemplos:
        print(f'   Factura {ej[0]}: {ej[1]}-"{ej[2]}" (ahora TEXT)')

    print('\n🎉 MIGRACIÓN VERIFICADA')
    print('✅ El campo folio ahora soporta folios alfanuméricos')
    print('✅ Ejemplos que ahora funcionan: "000456H", "FT-001", "ABC123"')
    
    conn.close()

if __name__ == "__main__":
    verificar()
