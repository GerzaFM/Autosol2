#!/usr/bin/env python3
"""
Test completo del sistema actualizado:
1. Extracción de datos del PDF
2. Procesamiento de datos (extraer solo números)
3. Verificación de estructura BD
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.buscarapp.autocarga.extractor import PDFDataExtractor
from src.bd.models import db, Vale
from procesar_datos_vale import procesar_datos_vale

def test_sistema_actualizado():
    """
    Test completo del sistema desde extracción hasta base de datos.
    """
    print("🧪 TEST SISTEMA ACTUALIZADO - EXTRACCIÓN Y BD")
    print("=" * 60)
    
    # 1. EXTRACCIÓN DE DATOS
    print("1️⃣ EXTRAYENDO DATOS DEL PDF...")
    extractor = PDFDataExtractor()
    vale_path = "C:/QuiterWeb/cache/15gerzahin.flores_QRSVCMX_V152266_180646_CD.pdf"
    
    datos_raw = extractor.extract_all_data(vale_path, debug=False)
    print("✅ Datos extraídos exitosamente")
    
    # 2. PROCESAMIENTO DE DATOS
    print("\n2️⃣ PROCESANDO DATOS PARA BD...")
    datos_procesados = procesar_datos_vale(datos_raw)
    print("✅ Datos procesados exitosamente")
    
    # Mostrar comparación
    print("\n📊 COMPARACIÓN EXTRACCIÓN vs PROCESAMIENTO:")
    campos_numericos = ['Departamento', 'Sucursal', 'Marca', 'Responsable', 'Cuenta', 'Referencia']
    
    for campo in campos_numericos:
        original = datos_raw.get(campo, 'N/A')
        procesado_key = campo.lower() if campo != 'Departamento' else 'departamento'
        if procesado_key == 'cuenta':
            procesado_key = 'cuenta'
        elif procesado_key == 'referencia':
            procesado_key = 'referencia'
        
        procesado = datos_procesados.get(procesado_key, 'N/A')
        print(f"   {campo:12}: '{original}' → {procesado}")
    
    # 3. VERIFICACIÓN DE BD
    print("\n3️⃣ VERIFICANDO ESTRUCTURA BD...")
    try:
        db.connect()
        
        # Verificar estructura
        cursor = db.execute_sql("PRAGMA table_info(vale)")
        columnas = [row[1] for row in cursor.fetchall()]
        print(f"✅ Columnas en BD: {columnas}")
        
        # Verificar que la clave primaria es 'id'
        cursor = db.execute_sql("PRAGMA table_info(vale)")
        pk_info = [row for row in cursor.fetchall() if row[5] == 1]  # Primary key flag
        if pk_info and pk_info[0][1] == 'id':
            print("✅ Clave primaria 'id' confirmada")
        else:
            print("❌ Problema con clave primaria")
        
        # 4. SIMULACIÓN DE INSERCIÓN (sin insertar realmente)
        print("\n4️⃣ SIMULANDO INSERCIÓN EN BD...")
        
        # Verificar si el vale ya existe
        vale_existente = Vale.select().where(Vale.noVale == datos_procesados['noVale']).first()
        
        if vale_existente:
            print(f"⚠️  Vale {datos_procesados['noVale']} ya existe en BD (ID: {vale_existente.id})")
            print("   📋 Datos actuales en BD:")
            print(f"      Proveedor: {vale_existente.proveedor}")
            print(f"      Total: {vale_existente.total}")
            print(f"      Departamento: {vale_existente.departamento}")
            print(f"      Cuenta: {vale_existente.cuenta}")
        else:
            print(f"✅ Vale {datos_procesados['noVale']} listo para insertar")
            print("   📋 Datos a insertar:")
            for key, value in datos_procesados.items():
                if value is not None:
                    print(f"      {key}: {value}")
        
        print("\n🎉 TEST COMPLETO EXITOSO")
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        return False
    
    finally:
        if not db.is_closed():
            db.close()

def mostrar_mapeo_final():
    """
    Muestra el mapeo final de datos extractor → BD.
    """
    print("\n" + "=" * 60)
    print("🗺️  MAPEO FINAL EXTRACTOR → BASE DE DATOS")
    print("=" * 60)
    
    mapeo = [
        ("Extractor", "Valor Ejemplo", "Campo BD", "Tipo BD", "Procesamiento"),
        ("─" * 12, "─" * 15, "─" * 12, "─" * 8, "─" * 20),
        ("'Numero'", "V152266", "noVale", "CHAR", "Sin cambios"),
        ("'Nombre'", "SERVICIOS...", "proveedor", "CHAR", "Sin cambios"),
        ("'Total'", "12,837.49", "total", "CHAR", "Sin cambios"),
        ("'Descripcion'", "MARKETING...", "descripcion", "CHAR", "Sin cambios"),
        ("'Tipo De Vale'", "VCV", "tipo", "CHAR", "Sin cambios"),
        ("'No Documento'", "10455", "noDocumento", "CHAR", "Sin cambios"),
        ("'Fecha'", "18/07/2025", "fechaVale", "DATE", "String → Date"),
        ("'Referencia'", "8122661", "referencia", "INT", "String → Int"),
        ("'Cuenta'", "3221", "cuenta", "INT", "String → Int"),
        ("'Departamento'", "6 ADMIN...", "departamento", "INT", "Extraer número"),
        ("'Sucursal'", "15 NISSAN...", "sucursal", "INT", "Extraer número"),
        ("'Marca'", "2 - NISSAN", "marca", "INT", "Extraer número"),
        ("'Responsable'", "294379", "responsable", "INT", "String → Int"),
        ("─", "─", "id", "INT PK", "Autoincremental")
    ]
    
    for fila in mapeo:
        print(f"{fila[0]:15} {fila[1]:15} {fila[2]:15} {fila[3]:10} {fila[4]}")

if __name__ == "__main__":
    test_sistema_actualizado()
    mostrar_mapeo_final()
