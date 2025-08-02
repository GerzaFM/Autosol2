# Funcionalidad Botón Cheque - BuscarApp

## Nueva Funcionalidad Implementada

Se ha agregado un botón **"Cheque"** al frame de botones de acción de la aplicación BuscarApp refactorizada.

## Ubicación
- **Frame**: `ActionButtonsFrame` 
- **Posición**: A la derecha de todos los demás botones
- **Estilo**: Bootstrap `success` (verde)

## Funcionalidad

### Comportamiento con UN elemento seleccionado:
1. Obtiene los datos del elemento seleccionado
2. Extrae: `no_vale`, `proveedor`, `folio_factura`, `clase`
3. Limpia los caracteres especiales para nombres de archivo
4. Genera nombre sugerido: `{no_vale}_{proveedor}_{folio_factura}_{clase}.pdf`
5. Muestra diálogo para guardar documento
6. Guarda la ruta en variable `ruta_exportacion`

### Comportamiento con MÚLTIPLES elementos seleccionados:
1. Verifica que todos los elementos sean del mismo proveedor
2. Si no son del mismo proveedor, muestra error y termina
3. Si son del mismo proveedor:
   - Extrae todos los `no_vale` y `folio_factura`
   - Usa el `proveedor` y `clase` del primer elemento
   - Genera nombre: `{vale1}_{vale2}_{proveedor}_{folio1}_{folio2}_{clase}.pdf`
   - Muestra diálogo para guardar documento
   - Guarda la ruta en variable `ruta_exportacion`

## Archivos Modificados

### 1. `views/action_buttons_frame.py`
- ✅ Agregado parámetro `on_cheque_callback` al constructor
- ✅ Agregado botón "Cheque" con estilo success
- ✅ Agregado método `_on_cheque_clicked()`
- ✅ Incluido botón en lista de botones que requieren selección

### 2. `buscar_app_refactored.py`
- ✅ Agregada importación `from tkinter import filedialog`
- ✅ Agregado callback `on_cheque_callback=self._on_cheque` en inicialización
- ✅ Implementado método `_on_cheque()` con toda la lógica
- ✅ Implementado método `_limpiar_nombre_archivo()` para sanear nombres

## Métodos Implementados

### `_on_cheque(self)`
Método principal que maneja el evento del botón Cheque:
- Obtiene elementos seleccionados usando `get_selected_data_multiple()`
- Valida que haya selección
- Maneja caso de 1 elemento vs múltiples elementos
- Valida proveedores en caso de múltiples elementos
- Genera nombres de archivo sugeridos
- Muestra diálogo de guardar archivo
- Maneja errores con logging

### `_limpiar_nombre_archivo(self, nombre: str) -> str`
Utilidad que limpia strings para usar como nombres de archivo:
- Reemplaza caracteres inválidos: `<>:"/\|?*`
- Reemplaza espacios por guiones bajos
- Limita longitud a 50 caracteres
- Maneja casos de strings vacíos

## Formato de Nombres Generados

### Un elemento:
```
{no_vale}_{proveedor}_{folio_factura}_{clase}.pdf
```
**Ejemplo**: `V123_ACME_Corp_A001-001_SERVICIOS.pdf`

### Múltiples elementos:
```
{vale1}_{vale2}_{proveedor}_{folio1}_{folio2}_{clase}.pdf
```
**Ejemplo**: `V123_V124_ACME_Corp_A001-001_A001-002_SERVICIOS.pdf`

## Validaciones Implementadas

1. **Sin selección**: Muestra advertencia si no hay elementos seleccionados
2. **Proveedores diferentes**: En múltiples elementos, valida que sean del mismo proveedor
3. **Caracteres inválidos**: Limpia automáticamente caracteres no válidos en nombres
4. **Strings vacíos**: Reemplaza campos vacíos con texto por defecto
5. **Manejo de errores**: Try-catch con logging detallado

## Cómo Probar

1. Ejecutar la aplicación BuscarApp refactorizada
2. Realizar una búsqueda para tener elementos en la tabla
3. Seleccionar uno o varios elementos (Ctrl+Click para múltiples)
4. Hacer clic en el botón "Cheque" (verde, a la derecha)
5. Verificar que aparece el diálogo para guardar archivo
6. Verificar que el nombre sugerido tiene el formato correcto
7. Seleccionar ubicación y confirmar
8. Verificar en logs que se guarda la `ruta_exportacion`

## Script de Prueba

Ejecutar: `python src/buscarapp/test_cheque_button.py`

## Estado Actual

✅ **Completamente Implementado**
- Botón agregado y funcional
- Lógica de 1 elemento implementada
- Lógica de múltiples elementos implementada
- Validación de proveedores implementada
- Limpieza de nombres de archivo implementada
- Manejo de errores implementado
- Logging detallado implementado

🔄 **Próximos pasos (opcionales)**
- Generar documento PDF real en la ruta seleccionada
- Agregar templates para diferentes tipos de cheque
- Integrar con sistema de firmas digitales
- Agregar preview del documento antes de guardar

## Variables de Estado

La variable `ruta_exportacion` contiene la ruta completa del archivo seleccionado por el usuario y está disponible dentro del método `_on_cheque()` para futuras implementaciones de generación de documentos.
