# Sistema AutoCarga Mejorado

Sistema unificado para extraer datos de PDFs de Vales y Órdenes, con comparación inteligente de proveedores.

## 🚀 Características Principales

### ✨ Extracción Inteligente
- **Mantiene nombres originales**: Los nombres se extraen con espacios tal como aparecen en el PDF
- **Comparación sin espacios**: Para encontrar coincidencias en BD, compara sin espacios ni caracteres especiales
- **Patrones mejorados**: Usa múltiples patrones regex para mayor precisión

### 🔍 Comparación de Proveedores
- **Por código QuiteR**: Busca primero por el campo "Cuenta" como codigo_quiter
- **Por nombre**: Si no encuentra por código, compara nombres normalizados
- **Actualización automática**: Asigna códigos QuiteR faltantes automáticamente

### 📊 Reportes Completos
- **Estadísticas detalladas**: Muestra éxito/fallo de extracciones y coincidencias
- **Archivos JSON**: Guarda todos los datos extraídos para procesamiento posterior
- **Reporte de coincidencias**: Lista proveedores encontrados/no encontrados

## 📁 Estructura de Archivos

```
autocarga/
├── autocarga.py           # Clase principal del sistema
├── extractor.py          # Extractor de Vales (QRSVCMX)
├── extractor_orden.py    # Extractor de Órdenes (QRSOPMX208)
├── provider_matcher.py   # Lógica de comparación de proveedores
├── lector_carpeta.py     # Búsqueda de archivos por fecha
├── main_autocarga.py     # Script principal para ejecutar
├── test_autocarga.py     # Script de pruebas
└── README.md             # Esta documentación
```

## 🎯 Uso Rápido

### Ejecutar el Sistema Completo
```bash
python main_autocarga.py
```

### Ejecutar Pruebas
```bash
python test_autocarga.py
```

### Uso Programático
```python
from autocarga import AutoCarga

# Crear instancia
autocarga = AutoCarga(
    ruta_carpeta=r"C:\QuiterWeb\cache",
    dias_atras=3
)

# Procesar archivos
vales, ordenes = autocarga.ejecutar_autocarga()

# Obtener estadísticas
stats = autocarga.obtener_estadisticas()

# Guardar resultados
autocarga.guardar_resultados("resultados")
```

## 📋 Datos Extraídos

### De Vales (QRSVCMX)
- **Nombre**: Nombre del proveedor (con espacios originales)
- **Número**: Número del vale (ej: V152885)
- **Fecha**: Fecha del vale
- **Cuenta**: Código QuiteR del proveedor
- **Departamento**: Departamento solicitante
- **Total**: Monto del vale

### De Órdenes (QRSOPMX208)
- **Nombre**: Nombre del proveedor
- **Ref_Movimiento**: Referencia del movimiento
- **Cuenta**: Número de cuenta
- **Importe**: Monto de la orden
- **Codigo_Banco**: Código del banco

## 🔧 Configuración

### Parámetros Principales
```python
AutoCarga(
    ruta_carpeta="C:\\QuiterWeb\\cache",  # Dónde buscar PDFs
    dias_atras=3                          # Días hacia atrás para buscar
)
```

### Patrones de Archivo
- **Vales**: Archivos que contengan "QRSVCMX"
- **Órdenes**: Archivos que contengan "QRSOPMX208"

## 📊 Ejemplo de Salida

```
🚀 SISTEMA DE AUTOCARGA - INICIO
============================================================
🔍 Buscando archivos en: C:\QuiterWeb\cache
📅 Archivos modificados en los últimos 3 días
------------------------------------------------------------
💳 Vales encontrados: 5
📋 Órdenes encontradas: 3

🚀 PROCESANDO VALES
========================================
📄 1/5 Procesando: archivo_vale_001.pdf
   ✅ Datos extraídos exitosamente
   🔢 Número: V152885
   🏢 Nombre: SERVICIOS GLOBALES ELYT
   💰 Total: 3,132.77

📊 RESUMEN VALES: 5/5 exitosos

🔍 REPORTE DE COINCIDENCIAS DE PROVEEDORES
============================================================
💳 VALES:
   ✅ Con proveedor encontrado: 4
   ❌ Sin proveedor: 1
📋 ÓRDENES:
   ✅ Con proveedor encontrado: 2
   ❌ Sin proveedor: 1
🔄 Proveedores actualizados con nuevo código: 2
```

## 🔄 Lógica de Comparación

### 1. Búsqueda por Código
```python
# Si el vale tiene "Cuenta", buscar proveedor por codigo_quiter
proveedor = buscar_por_codigo(vale.Cuenta)
```

### 2. Búsqueda por Nombre
```python
# Si no se encuentra por código, buscar por nombre normalizado
nombre_normalizado = "SERVICIOSGLOBALESELYT"  # Sin espacios
proveedor = buscar_por_nombre_normalizado(nombre_normalizado)
```

### 3. Actualización Automática
```python
# Si se encuentra por nombre pero no tiene código, asignarlo
if proveedor and not proveedor.codigo_quiter:
    proveedor.codigo_quiter = vale.Cuenta
    proveedor.save()
```

## ⚙️ Personalización

### Agregar Nuevos Patrones
Modifica los patrones en `extractor.py` o `extractor_orden.py`:

```python
self.patterns = {
    'nuevo_campo': [
        r'Patrón1:\s*([A-Z]+)',
        r'Patrón2:\s*([0-9]+)',
    ]
}
```

### Modificar Normalización
Ajusta la función `normalize_name()` en `provider_matcher.py`:

```python
def normalize_name(self, name: str) -> str:
    # Tu lógica personalizada aquí
    return name.upper().replace(" ", "")
```

## 🐛 Solución de Problemas

### Archivos No Encontrados
- Verifica que la ruta `ruta_carpeta` existe
- Confirma que hay archivos PDF con los patrones correctos
- Ajusta `dias_atras` para buscar en un período más amplio

### Proveedores No Coinciden
- Revisa los nombres extraídos vs. nombres en BD
- Ajusta la función `normalize_name()` si hay caracteres especiales
- Verifica que los códigos QuiteR no tengan conflictos

### Errores de Extracción
- Ejecuta `test_autocarga.py` para diagnóstico
- Revisa los patrones regex si cambia el formato de PDFs
- Habilita modo debug en extractores

## 📝 Logs y Debugging

El sistema incluye logging detallado. Para habilitar debug:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

autocarga = AutoCarga(...)
autocarga.ejecutar_autocarga()
```

## 🎯 Próximos Pasos

1. **Integrar con BD**: Usar los datos extraídos para crear/actualizar facturas
2. **Interfaz gráfica**: Crear UI para configurar y monitorear el proceso
3. **Notificaciones**: Alertas cuando se procesan nuevos archivos
4. **Validaciones**: Verificar consistencia de datos antes de guardar

---

**Nota**: Este sistema está diseñado para mantener la máxima compatibilidad con los datos existentes mientras mejora la precisión de la extracción y comparación.
