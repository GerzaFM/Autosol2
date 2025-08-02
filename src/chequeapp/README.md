# Aplicación de Gestión de Cheques

## Descripción
Aplicación completa para la gestión de cheques implementada con arquitectura MVC y componentes reutilizables siguiendo el patrón de "Views como Contenedores" utilizado en las otras aplicaciones del sistema.

## Características Implementadas

### ✅ Funcionalidades Completas
- **Gestión de Cheques**: Crear, editar, eliminar cheques
- **Filtros Avanzados**: Búsqueda por fecha, beneficiario, banco, estado, monto
- **Estados de Cheques**: PENDIENTE, COBRADO, CANCELADO
- **Tabla Interactiva**: Ordenamiento por columnas, selección múltiple
- **Exportación**: Exportar datos a CSV
- **Integración**: Completamente integrada en la aplicación principal

### ✅ Arquitectura MVC
- **Modelos**: `ChequeData`, `ChequeFilters`, `ChequeState`
- **Vistas**: Componentes modulares y reutilizables
- **Controladores**: `ChequeController` para lógica de negocio

### ✅ Componentes de Vista
- **`ChequeFilterFrame`**: Filtros específicos para cheques
- **`ChequeTableFrame`**: Tabla optimizada para datos de cheques
- **`ChequeActionFrame`**: Botones de acción contextual

## Estructura del Proyecto

```
src/chequeapp/
├── __init__.py                      # Módulo principal
├── cheque_app.py                    # Aplicación original (simplificada)
├── cheque_app_complete.py           # Aplicación completa
├── controllers/
│   ├── __init__.py
│   ├── search_controller.py         # Controlador de búsqueda original
│   └── cheque_controller.py         # Controlador principal de cheques
├── models/
│   ├── __init__.py
│   └── cheque_models.py             # Modelos de datos
└── views/
    ├── __init__.py
    ├── search_frame.py              # Frame de búsqueda original
    ├── table_frame.py               # Frame de tabla original
    ├── cheque_filter_frame.py       # Filtros específicos para cheques
    ├── cheque_table_frame.py        # Tabla específica para cheques
    └── cheque_action_frame.py       # Botones de acción
```

## Uso

### 1. Ejecutar Aplicación Independiente
```python
# Aplicación completa con todas las funcionalidades
python src/chequeapp/cheque_app_complete.py

# Aplicación simplificada (original)
python src/chequeapp/cheque_app.py
```

### 2. Integración en Aplicación Principal
```python
# La aplicación está integrada en el menú principal
# Acceder a través del botón "🏦 Cheques" en el sidebar
```

### 3. Uso Programático
```python
from chequeapp import ChequeAppComplete, ChequeController, ChequeData

# Usar el controlador
controller = ChequeController()

# Crear un nuevo cheque
cheque = ChequeData(
    numero_cheque="001234",
    beneficiario="Proveedor ABC",
    monto=Decimal('5000.00'),
    banco="BBVA Bancomer"
)
controller.create_cheque(cheque)

# Filtrar cheques
filters = {'estado': 'PENDIENTE', 'banco': 'BBVA'}
results = controller.apply_filters(filters)
```

## Funcionalidades Detalladas

### Filtros de Búsqueda
- **Rango de Fechas**: Fecha inicial y final
- **Número de Cheque**: Búsqueda por número exacto o parcial
- **Beneficiario**: Búsqueda por nombre del beneficiario
- **Banco**: Selección de banco específico
- **Estado**: PENDIENTE, COBRADO, CANCELADO
- **Rango de Monto**: Monto mínimo y máximo

### Acciones Disponibles
- **Nuevo**: Crear un nuevo cheque
- **Editar**: Modificar cheque existente
- **Eliminar**: Eliminar cheque (con confirmación)
- **Marcar Cobrado**: Cambiar estado a COBRADO
- **Marcar Cancelado**: Cambiar estado a CANCELADO
- **Imprimir**: Imprimir formato de cheque (placeholder)
- **Exportar**: Exportar datos filtrados a CSV

### Estados de Cheques
- **PENDIENTE**: Cheque emitido, pendiente de cobro
- **COBRADO**: Cheque cobrado exitosamente
- **CANCELADO**: Cheque cancelado por algún motivo

## Datos de Ejemplo
La aplicación incluye 5 cheques de ejemplo para demostración:
- Diferentes bancos (BBVA, Banamex, Santander, Banorte, HSBC)
- Diferentes estados (PENDIENTE, COBRADO, CANCELADO)
- Montos variables (desde $2,800 hasta $12,000)
- Fechas distribuidas en 2024

## Extensibilidad

### Agregar Nuevos Campos
```python
# En models/cheque_models.py
@dataclass
class ChequeData:
    # Agregar nuevos campos aquí
    nuevo_campo: str = ""
```

### Agregar Nuevos Filtros
```python
# En views/cheque_filter_frame.py
# Agregar widgets de filtro

# En controllers/cheque_controller.py
# Agregar lógica de filtrado
```

### Integrar con Base de Datos Real
```python
# En controllers/cheque_controller.py
# Reemplazar _load_sample_data() con carga desde BD
def load_cheques(self):
    # Implementar carga desde base de datos real
    pass
```

## Logging y Debugging
La aplicación incluye logging completo:
- Nivel INFO para operaciones normales
- Nivel ERROR para errores con stack traces
- Nivel DEBUG para información detallada

## Compatibilidad
- **Python**: 3.8+
- **TTKBootstrap**: Para interfaz moderna
- **Tkinter**: Biblioteca estándar de Python
- **Decimal**: Para manejo preciso de montos

## Estado del Proyecto
✅ **Completamente Implementado**
- Todas las funcionalidades básicas implementadas
- Integración con aplicación principal completa
- Arquitectura MVC completa
- Componentes reutilizables
- Datos de ejemplo funcionales

🔄 **Pendientes (Opcionales)**
- Formulario modal para crear/editar cheques
- Integración con base de datos real
- Funcionalidad de impresión real
- Reportes avanzados
- Validaciones adicionales

## Créditos
Desarrollado siguiendo los patrones arquitectónicos de `buscarapp` y `solicitudapp`, implementando la filosofía de "Views como Contenedores" para mantener consistencia en el sistema.
