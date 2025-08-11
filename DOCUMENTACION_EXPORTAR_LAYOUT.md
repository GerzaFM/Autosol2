# 📋 Funcionalidad de Exportar Layout - Documentación

## ✨ Nueva Funcionalidad Implementada

Se ha implementado completamente la funcionalidad **`on_exportar`** en la aplicación de cheques profesional con las siguientes características:

### 🎯 Funcionalidades Principales

#### 1. **Solicitud de Nombre de Layout**
- Al hacer clic en "Layout", se solicita al usuario un nombre para el nuevo layout
- Se proporciona un nombre por defecto: `"Layout YYYY-MM-DD"` (fecha de hoy)
- Validación de entrada: no se permite nombre vacío

#### 2. **Creación de Layout en Base de Datos**
- Se crea un nuevo registro en la tabla `layout` con:
  - Nombre proporcionado por el usuario
  - Fecha de hoy
  - Monto calculado automáticamente

#### 3. **Asignación de Cheques**
- Todos los cheques en `cargar_table` se asignan al nuevo layout
- Se actualiza la columna `layout` en la tabla `cheque`
- Se calcula y actualiza el monto total del layout

#### 4. **Limpieza de Interfaz**
- Se eliminan todos los ítems de `cargar_table` después del export
- La tabla queda lista para nuevos cheques

#### 5. **Actualización de Layout Table**
- Se refresca `layout_table` con todos los layouts del día actual
- Se muestra inmediatamente el layout recién creado

### 💾 Estructura de Base de Datos

#### Tabla `cheque` (actualizada)
```sql
id              INTEGER PRIMARY KEY
fecha           DATE
vale            VARCHAR(255)
folio           VARCHAR(255)
proveedor       VARCHAR(255)
monto           DECIMAL(10, 5)
banco           VARCHAR(255)
layout          INTEGER (FK a layout.id, nullable)
```

#### Tabla `layout`
```sql
id              INTEGER PRIMARY KEY
fecha           DATE
nombre          VARCHAR(255)
monto           DECIMAL(10, 5)
```

### 🔄 Flujo de Trabajo

1. **Buscar Cheques**: Usuario busca cheques usando filtros
2. **Agregar a Cargar**: Usuario selecciona cheques y los agrega a `cargar_table`
3. **Exportar Layout**: Usuario hace clic en "Layout"
   - Se solicita nombre del layout
   - Se crean registros en base de datos
   - Se limpian las tablas
   - Se actualiza la vista

### 📊 Funciones de Base de Datos Implementadas

#### `ChequeDatabase.create_layout(nombre, fecha, monto)`
- Crea un nuevo layout en la base de datos
- Retorna el ID del layout creado

#### `ChequeDatabase.assign_cheques_to_layout(layout_id, cheque_ids)`
- Asigna múltiples cheques a un layout específico
- Actualiza automáticamente el monto total del layout

#### `ChequeDatabase.search_layouts(filters)`
- Busca layouts aplicando filtros de fecha
- Usado para actualizar `layout_table`

### 🛠️ Componentes Técnicos

#### Imports Añadidos
```python
from datetime import date
from tkinter import simpledialog
```

#### Funciones Principales
- `on_exportar()`: Función principal de exportación
- `_refresh_layout_table()`: Actualiza la tabla de layouts

### ✅ Validaciones Implementadas

1. **Verificación de Contenido**: No se permite exportar si `cargar_table` está vacía
2. **Validación de Nombre**: Se requiere un nombre válido para el layout
3. **Manejo de Errores**: Todos los errores se manejan con mensajes informativos
4. **Logging**: Se registran todas las operaciones importantes

### 🧪 Pruebas Realizadas

- ✅ Creación de layouts
- ✅ Asignación de cheques a layouts
- ✅ Actualización de montos automática
- ✅ Búsqueda de layouts por fecha
- ✅ Integración completa con la aplicación

### 💡 Uso en la Aplicación

1. **Abrir aplicación de cheques** (standalone o desde main_app)
2. **Buscar cheques** usando los filtros disponibles
3. **Seleccionar cheques** en la tabla izquierda
4. **Agregar a cargar** usando el botón "Agregar"
5. **Crear layout** usando el botón "Layout"
6. **Proporcionar nombre** en el diálogo que aparece
7. **Verificar resultado** en la tabla de layouts inferior

### 🔮 Características Futuras Sugeridas

- [ ] Edición de layouts existentes
- [ ] Eliminación de layouts
- [ ] Exportación a PDF/Excel
- [ ] Filtros avanzados para layouts
- [ ] Reportes de layouts por rango de fechas

---

**✨ ¡La funcionalidad está completamente implementada y lista para usar!**
