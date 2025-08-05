# Funcionalidad de Cheques Múltiples

## Descripción
La aplicación ahora soporta la generación de cheques consolidando múltiples facturas del mismo proveedor en un solo documento de cheque. Esta funcionalidad permite agilizar el proceso de pago cuando se tienen varias facturas de un mismo proveedor.

## Características Principales

### ✅ Consolidación Automática
- **Suma de Totales**: Se suman automáticamente los importes de todas las facturas seleccionadas
- **Suma de IVAs**: Se consolida el IVA trasladado de todas las facturas
- **Concepto Múltiple**: Se genera un concepto que incluye todos los folios de las facturas
- **Campo Costos**: Muestra todos los números de vale involucrados en formato "Vales V001, V002, V003"

### ✅ Validaciones de Seguridad
- **Mismo Proveedor**: Verifica que todas las facturas sean del mismo proveedor
- **Totales Válidos**: Valida que todas las facturas tengan importes válidos
- **RFC Consistente**: Utiliza el RFC del proveedor para obtener información bancaria

### ✅ Información Detallada
- **Resumen Completo**: Muestra estadísticas del cheque consolidado
- **Lista de Vales**: Incluye todos los números de vale en el archivo
- **Lista de Folios**: Muestra todos los folios consolidados

## Campos del Cheque

### Campo Costos
El campo **Costos** se comporta de manera diferente según el tipo de cheque:

#### Cheque Individual
- **Formato**: `Vale V001`
- **Contenido**: Muestra el número del vale individual de la factura

#### Cheque Múltiple  
- **Formato**: `Vales V001, V002, V003`
- **Contenido**: Muestra todos los números de vale involucrados separados por comas
- **Ejemplo**: Si consolida 3 facturas con vales V1001, V1002, V1003, mostrará: `Vales V1001, V1002, V1003`

### Campo Concepto
- **Individual**: `Factura F001`
- **Múltiple**: `Facturas F001, F002, F003`

### Campos Consolidados
- **Cantidad**: Suma total de todas las facturas
- **Debe/Haber**: Importes consolidados con IVA si aplica
- **Moneda**: Conversión a letras del total consolidado

## Cómo Usar

### Paso 1: Seleccionar Facturas
1. En la tabla de resultados, seleccione múltiples facturas usando `Ctrl + Click`
2. **Importante**: Todas las facturas deben ser del mismo proveedor
3. Las facturas deben tener importes válidos (mayor a 0)

### Paso 2: Generar Cheque
1. Haga clic en el botón **"Cheque"**
2. Si hay múltiples facturas seleccionadas, se activará el modo múltiple
3. El sistema validará automáticamente:
   - Mismo proveedor en todas las facturas
   - Importes válidos en todas las facturas

### Paso 3: Guardar Archivo
1. Se abrirá un diálogo para guardar el archivo PDF
2. El nombre sugerido incluirá:
   - Todos los números de vale
   - Nombre del proveedor
   - Todos los folios
   - Clase/Tipo de factura

### Paso 4: Confirmación
- Se mostrará un resumen detallado con:
  - Número de facturas consolidadas
  - Total consolidado
  - IVA consolidado
  - Lista de vales y folios

## Ejemplos de Uso

### Caso 1: 3 Facturas del Mismo Proveedor
```
Facturas seleccionadas:
- Vale V001, Factura F001, Total: $1,000.00, IVA: $160.00
- Vale V002, Factura F002, Total: $1,500.00, IVA: $240.00  
- Vale V003, Factura F003, Total: $750.00, IVA: $120.00

Resultado:
- Cheque consolidado por: $3,250.00
- IVA total: $520.00
- Concepto: "Facturas F001, F002, F003"
- Campo Costos: "Vales V001, V002, V003"
- Archivo: "V001 V002 V003 PROVEEDOR SA F001 F002 F003 Servicios.pdf"
```

### Caso 2: Error - Proveedores Diferentes
```
Si selecciona facturas de proveedores diferentes:
❌ "Los elementos seleccionados deben ser del mismo proveedor"
   Se mostrará la lista de facturas por proveedor
```

## Tecnología Implementada

### Clases Principales
- **`Cheque.crear_multiple(facturas, ruta)`**: Método de clase para crear cheques múltiples
- **`_consolidar_facturas(facturas)`**: Consolida múltiples facturas en una sola
- **`generar_multiple_cheques(facturas)`**: Genera el cheque con datos consolidados

### Proceso de Consolidación
1. **Validación**: Verifica que la lista de facturas no esté vacía
2. **Factura Base**: Usa la primera factura como plantilla
3. **Suma de Importes**: Consolida totales e IVAs
4. **Recopilación de Folios**: Crea lista de todos los folios
5. **Recopilación de Vales**: Crea lista de todos los números de vale
6. **Concepto Dinámico**: Genera concepto basado en número de facturas
7. **Campo Costos**: Genera campo con todos los vales involucrados
8. **Formulario**: Actualiza el formulario con datos consolidados

### Validaciones Implementadas
- ✅ Lista de facturas no vacía
- ✅ Mismo proveedor en todas las facturas
- ✅ Importes válidos (> 0) en todas las facturas
- ✅ Datos de proveedor consistentes (RFC, nombre)

## Logs y Debugging

### Información Registrada
```
[INFO] Iniciando generación de cheque múltiple para 3 facturas del proveedor: PROVEEDOR SA
[INFO] Cheque múltiple generado exitosamente: ruta.pdf - 3 facturas consolidadas - Total: $3,250.00
```

### Errores Comunes
```
[ERROR] Error de validación en cheque múltiple: La lista de facturas no puede estar vacía
[ERROR] Error generando cheque múltiple en: ruta.pdf
[WARNING] Proveedores diferentes detectados en la selección
```

## Archivos Modificados

### `buscar_app_refactored.py`
- **`_on_cheque()`**: Actualizada para soportar múltiples facturas
- **Validaciones**: Agregadas verificaciones de proveedor y totales
- **Manejo de Errores**: Mejorado con logging detallado

### `ctr_cheque.py`
- **`crear_multiple()`**: Método de clase para crear cheques múltiples
- **`_consolidar_facturas()`**: Lógica de consolidación de facturas
- **`generar_multiple_cheques()`**: Generación de cheques consolidados

## Próximas Mejoras

### 🔄 Funcionalidades Planificadas
- [ ] Soporte para diferentes monedas
- [ ] Plantillas personalizables para cheques múltiples
- [ ] Exportación a Excel con desglose de facturas
- [ ] Vista previa antes de generar el PDF
- [ ] Historial de cheques múltiples generados

### 🚀 Optimizaciones
- [ ] Cache de datos de proveedores para mejor rendimiento
- [ ] Generación asíncrona para lotes grandes
- [ ] Validación en tiempo real durante la selección

## Soporte Técnico

Si experimenta problemas con la funcionalidad de cheques múltiples:

1. **Verifique** que todas las facturas sean del mismo proveedor
2. **Confirme** que todas las facturas tengan importes válidos
3. **Revise** los logs de la aplicación para errores específicos
4. **Pruebe** primero con un número pequeño de facturas (2-3)

La funcionalidad ha sido probada exitosamente con hasta 10 facturas simultáneas del mismo proveedor.
