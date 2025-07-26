#!/usr/bin/env python3
"""
Test integrado completo del sistema de AutoCarga:
1. Extracción de datos del PDF
2. Procesamiento de datos  
3. Inserción en base de datos
4. Actualización del frame de información
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.buscarapp.autocarga.extractor import PDFDataExtractor
from src.buscarapp.utils.procesar_datos_vale import procesar_datos_vale
from src.bd.models import db, Vale
from src.bd.bd_control import BDControl

def test_integracion_completa():
    """
    Test de integración completa del sistema AutoCarga.
    """
    print("🧪 TEST INTEGRACIÓN COMPLETA - AUTOCARGA")
    print("=" * 60)
    
    # 1. EXTRACCIÓN DE DATOS
    print("1️⃣ EXTRAYENDO DATOS DEL PDF...")
    extractor = PDFDataExtractor()
    vale_path = "C:/QuiterWeb/cache/15gerzahin.flores_QRSVCMX_V152266_180646_CD.pdf"
    
    if not os.path.exists(vale_path):
        print(f"❌ Archivo no encontrado: {vale_path}")
        return False
    
    datos_raw = extractor.extract_all_data(vale_path, debug=False)
    print("✅ Datos extraídos exitosamente")
    print(f"   📊 {len(datos_raw)} campos extraídos")
    
    # 2. PROCESAMIENTO DE DATOS
    print("\n2️⃣ PROCESANDO DATOS PARA BD...")
    datos_procesados = procesar_datos_vale(datos_raw)
    print("✅ Datos procesados exitosamente")
    
    # Mostrar datos procesados clave
    print("   📋 Datos procesados clave:")
    campos_clave = ['noVale', 'proveedor', 'total', 'departamento', 'referencia']
    for campo in campos_clave:
        valor = datos_procesados.get(campo, 'N/A')
        print(f"      {campo:12}: {valor}")
    
    # 3. VERIFICACIÓN DE BASE DE DATOS
    print("\n3️⃣ VERIFICANDO BD...")
    try:
        db.connect()
        
        # Verificar estructura de tabla
        cursor = db.execute_sql("PRAGMA table_info(vale)")
        columnas = [row[1] for row in cursor.fetchall()]
        print(f"✅ Tabla 'vale' verificada: {len(columnas)} columnas")
        
        # 4. SIMULACIÓN DE INSERCIÓN
        print("\n4️⃣ SIMULANDO INSERCIÓN EN BD...")
        
        # Verificar si el vale ya existe
        try:
            vale_existente = Vale.get(Vale.noVale == datos_procesados['noVale'])
            print(f"⚠️  Vale {datos_procesados['noVale']} ya existe en BD (ID: {vale_existente.id})")
            
            # Mostrar datos existentes para comparar
            print("   📋 Datos actuales en BD:")
            print(f"      ID: {vale_existente.id}")
            print(f"      Proveedor: {vale_existente.proveedor}")
            print(f"      Total: {vale_existente.total}")
            print(f"      Descripción: {vale_existente.descripcion[:50]}...")
            
            usar_existente = True
            
        except Vale.DoesNotExist:
            print(f"✅ Vale {datos_procesados['noVale']} no existe - sería insertado")
            usar_existente = False
            
            # Mostrar datos que se insertarían
            print("   📋 Datos a insertar:")
            for key, value in datos_procesados.items():
                if value is not None:
                    valor_mostrar = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                    print(f"      {key:15}: {valor_mostrar}")
        
        # 5. TEST DE BD_CONTROL
        print("\n5️⃣ TESTING BD_CONTROL...")
        bd_control = BDControl()
        
        if usar_existente:
            # Usar vale existente para test
            ultimo_vale = vale_existente
        else:
            # Para el test, insertemos temporalmente el vale
            print("   📝 Insertando vale para test...")
            ultimo_vale = Vale.create(**datos_procesados)
            print(f"✅ Vale insertado con ID: {ultimo_vale.id}")
        
        # Test obtener_ultimo_vale
        ultimo_vale_obtenido = bd_control.obtener_ultimo_vale()
        if ultimo_vale_obtenido:
            print(f"✅ obtener_ultimo_vale() funciona - ID: {ultimo_vale_obtenido.id}")
            
            # 6. SIMULACIÓN DE ACTUALIZACIÓN DE UI
            print("\n6️⃣ SIMULANDO ACTUALIZACIÓN DE UI...")
            
            # Formato de datos para el frame de información
            vale_data_ui = {
                'noVale': ultimo_vale_obtenido.noVale,
                'tipo': ultimo_vale_obtenido.tipo,
                'total': ultimo_vale_obtenido.total,
                'proveedor': ultimo_vale_obtenido.proveedor,
                'fechaVale': ultimo_vale_obtenido.fechaVale,
                'referencia': ultimo_vale_obtenido.referencia,
                'departamento': ultimo_vale_obtenido.departamento,
                'descripcion': ultimo_vale_obtenido.descripcion
            }
            
            print("✅ Datos formateados para UI:")
            for key, value in vale_data_ui.items():
                valor_mostrar = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                print(f"      {key:15}: {valor_mostrar}")
        else:
            print("❌ obtener_ultimo_vale() no funcionó")
        
        # Limpiar si insertamos un vale temporal
        if not usar_existente:
            ultimo_vale.delete_instance()
            print("   🧹 Vale temporal eliminado")
        
        print("\n🎉 TEST INTEGRACIÓN COMPLETA EXITOSO")
        return True
        
    except Exception as e:
        print(f"❌ Error en test de integración: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if not db.is_closed():
            db.close()

def mostrar_flujo_completo():
    """
    Muestra el flujo completo del sistema AutoCarga.
    """
    print("\n" + "=" * 60)
    print("🔄 FLUJO COMPLETO DEL SISTEMA AUTOCARGA")
    print("=" * 60)
    
    flujo = [
        ("1. Usuario presiona", "Botón 'AutoCarga' en la UI"),
        ("2. Sistema muestra", "Diálogo de configuración"),
        ("3. Usuario configura", "Carpeta y parámetros de búsqueda"),
        ("4. AutoCarga busca", "Archivos PDF de vales en C:/QuiterWeb/cache"),
        ("5. PDFDataExtractor", "Extrae datos de cada PDF encontrado"),
        ("6. procesar_datos_vale()", "Convierte datos al formato de BD"),
        ("7. AutocargaController", "Inserta vales en base de datos"),
        ("8. BD actualizada", "Nuevos registros en tabla 'vale'"),
        ("9. UI actualizada", "Frame inferior muestra último vale"),
        ("10. Usuario ve", "Información completa del vale procesado")
    ]
    
    for paso, descripcion in flujo:
        print(f"{paso:25} → {descripcion}")
    
    print("\n" + "=" * 60)
    print("📊 CAMPOS PROCESADOS EN CADA VALE:")
    print("=" * 60)
    
    campos = [
        ("noVale", "V152266", "Número único del vale"),
        ("proveedor", "SERVICIOS GLOBALES...", "Nombre del proveedor"),
        ("total", "12,837.49", "Monto total"),
        ("descripcion", "MARKETING DE EXPERIENCIA...", "Descripción del servicio"),
        ("referencia", "8122661", "Número de referencia"),
        ("departamento", "6", "Código de departamento"),
        ("fechaVale", "2025-07-18", "Fecha del vale"),
        ("tipo", "VCV", "Tipo de vale"),
        ("cuenta", "3221", "Número de cuenta")
    ]
    
    for campo, ejemplo, descripcion in campos:
        print(f"{campo:15} | {ejemplo:20} | {descripcion}")

if __name__ == "__main__":
    success = test_integracion_completa()
    if success:
        mostrar_flujo_completo()
