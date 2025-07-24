# Aplicación de Búsqueda de Facturas - Refactorizada

## Descripción
Esta es la versión refactorizada de la aplicación de búsqueda de facturas, que implementa una arquitectura MVC (Model-View-Controller) para mejorar la mantenibilidad, escalabilidad y organización del código.

## Estructura del Proyecto

```
src/buscarapp/
├── buscar_app.py                 # Archivo original (monolítico)
├── buscar_app_refactored.py      # Nueva aplicación refactorizada
├── controllers/                  # Controladores (Lógica de negocio)
│   ├── __init__.py
│   ├── search_controller.py      # Controlador de búsqueda
│   ├── invoice_controller.py     # Controlador de facturas
│   └── export_controller.py      # Controlador de exportación
├── models/                       # Modelos de datos
│   ├── __init__.py
│   ├── search_models.py          # Modelos para búsqueda
│   └── table_models.py           # Modelos para tabla
├── views/                        # Componentes de interfaz
│   ├── __init__.py
│   ├── search_frame.py           # Frame de búsqueda
│   ├── table_frame.py            # Frame de tabla
│   ├── action_buttons_frame.py   # Frame de botones
│   └── info_panels_frame.py      # Paneles de información
└── utils/                        # Utilidades
    ├── __init__.py
    ├── format_utils.py           # Funciones de formateo
    └── dialog_utils.py           # Utilidades de diálogos
```

## Características Principales

### ✅ Arquitectura MVC
- **Modelo**: Gestión de datos y estado de la aplicación
- **Vista**: Componentes de interfaz gráfica separados y reutilizables  
- **Controlador**: Lógica de negocio y coordinación entre modelo y vista

### ✅ Separación de Responsabilidades
- **SearchController**: Maneja filtros y búsquedas
- **InvoiceController**: Gestiona operaciones de facturas (incluye Reimprimir)
- **ExportController**: Controla exportaciones en múltiples formatos
- **Componentes de Vista**: Cada frame es independiente y reutilizable

### ✅ Funcionalidades Preservadas
- ✅ Botón **Reimprimir** completamente funcional
- ✅ Formato tipo de vale como "clave - valor"
- ✅ Comentarios de facturas con serie y folio correctos
- ✅ Todas las operaciones CRUD de facturas
- ✅ Filtros de búsqueda avanzados
- ✅ Exportación de datos
- ✅ Gestión de estados (cargada/pagada)

### ✅ Mejoras Técnicas
- **Mantenibilidad**: Código organizado en módulos pequeños y específicos
- **Testabilidad**: Cada componente puede probarse independientemente
- **Reutilización**: Componentes pueden usarse en otras partes del sistema
- **Escalabilidad**: Fácil agregar nuevas funcionalidades
- **Logging**: Sistema de logging integrado para debugging

## Uso

### Ejecutar la Aplicación Refactorizada
```python
# Desde el directorio del proyecto
python -m src.buscarapp.buscar_app_refactored

# O directamente
python src/buscarapp/buscar_app_refactored.py
```

### Comparación con Aplicación Original
```python
# Aplicación original (monolítica)
python src/buscarapp/buscar_app.py

# Aplicación refactorizada (MVC)
python src/buscarapp/buscar_app_refactored.py
```

## Componentes Principales

### 1. SearchFrame
- Controles de filtros de búsqueda
- Fechas, tipos, proveedores, estados
- Búsqueda por texto
- Callbacks para eventos de búsqueda

### 2. TableFrame  
- Tabla de resultados con scroll
- Selección y eventos de doble click
- Colores alternados y estados visuales
- Actualización dinámica de datos

### 3. ActionButtonsFrame
- Botones de acción: Autocarga, Reimprimir, Toggle estados
- Apertura de archivos XML/PDF
- Exportación de datos
- Estados habilitado/deshabilitado dinámicos

### 4. InfoPanelsFrame
- Paneles de información detallada
- Tabs para: Factura, Conceptos, Proveedor, Vale, Estadísticas
- Actualización automática con selección

### 5. Controladores
- **SearchController**: Filtros, búsquedas, estado
- **InvoiceController**: Operaciones de facturas, archivos, estados
- **ExportController**: CSV, Excel, JSON, reportes

## Funcionalidad Reimprimir

La funcionalidad de reimprimir está completamente implementada en `InvoiceController`:

```python
# Uso del botón Reimprimir
def _on_reimprimir(self, selected_data):
    success = self.invoice_controller.reimprimir_factura(selected_data)
    # Genera PDF usando form_control.py con datos de BD
```

**Características:**
- ✅ Usa `form_control.py` para generar PDF
- ✅ Obtiene datos completos de la base de datos
- ✅ Formato tipo vale: "I - Ingreso", "E - Egreso", etc.
- ✅ Comentarios incluyen serie y folio de factura
- ✅ Manejo de errores y validaciones
- ✅ Interfaz de guardado de archivos

## Base de Datos

La aplicación soporta tanto datos reales como de ejemplo:

- **Con BD Real**: Todas las funcionalidades activas
- **Sin BD**: Datos de ejemplo para demostración
- **Detección Automática**: La app detecta y se adapta automáticamente

## Logging

Sistema de logging integrado para facilitar debugging:

```python
# Los logs aparecen en consola y pueden configurarse
logging.basicConfig(level=logging.INFO)
```

## Migración desde Aplicación Original

El refactoring preserva **toda** la funcionalidad existente:

1. **Búsquedas**: Mismos filtros y comportamiento
2. **Reimprimir**: Funcionalidad completa preservada  
3. **Estados**: Toggle de cargada/pagada funcional
4. **Exportación**: Múltiples formatos disponibles
5. **UI**: Interfaz mejorada pero familiar

## Ventajas del Refactoring

### Antes (buscar_app.py)
- ❌ 1800+ líneas en un solo archivo
- ❌ Lógica mezclada con interfaz
- ❌ Difícil de mantener y probar
- ❌ Acoplamiento alto entre componentes

### Después (buscar_app_refactored.py)
- ✅ Arquitectura modular MVC
- ✅ Responsabilidades separadas
- ✅ Fácil mantenimiento y testing  
- ✅ Componentes reutilizables
- ✅ Código autodocumentado

## Próximos Pasos

1. **Testing**: Implementar pruebas unitarias para cada controlador
2. **Documentación**: Expandir documentación de APIs
3. **Configuración**: Sistema de configuración externalizada
4. **Performance**: Optimizaciones de carga de datos
5. **UI/UX**: Mejoras adicionales de interfaz

## Conclusión

Esta refactorización transforma un archivo monolítico de 1800+ líneas en una aplicación bien estructurada, mantenible y escalable, preservando toda la funcionalidad existente incluida la función **Reimprimir** solicitada.
