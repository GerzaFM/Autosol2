# Mejora: Nuevo Formato de Nombres de Archivo al Exportar

## Cambio Solicitado
Cambiar el formato del nombre predeterminado en el cuadro de diálogo de guardado de:
- **Formato anterior**: `Folio Proveedor`
- **Formato nuevo**: `Folio Interno, Proveedor, Folio factura, Clase`

## Implementación

### Lógica Aplicada
```python
# Construir nombre de archivo con formato: Folio Interno, Proveedor, Folio factura, Clase
folio_interno = self.folio_interno_manual
proveedor = proveedor_data.get("Nombre", "")
folio_factura = solicitud_data.get("Folio", "")
clase = solicitud_data.get("Tipo", "")

# Si no hay folio interno manual, omitir ese campo para evitar duplicar el folio
if folio_interno:
    nombre_elementos = [folio_interno, proveedor, folio_factura, clase]
else:
    # Formato cuando no hay folio interno: Folio factura, Proveedor, Clase
    nombre_elementos = [folio_factura, proveedor, clase]

# Filtrar campos vacíos y construir nombre
nombre_archivo = ", ".join(filter(lambda x: x and x.strip(), nombre_elementos))
```

### Elementos del Nombre
1. **Folio Interno**: `self.folio_interno_manual` (solo cuando existe)
2. **Proveedor**: `proveedor_data.get("Nombre", "")`
3. **Folio Factura**: `solicitud_data.get("Folio", "")`
4. **Clase**: `solicitud_data.get("Tipo", "")`

## Resultados por Escenario

### 1. Factura Normal (sin folio interno manual)
- **Antes**: `12345 EMPRESA SERVICIOS SA`
- **Ahora**: `12345, EMPRESA SERVICIOS SA, SC Servicios`
- **Elementos**: Folio factura, Proveedor, Clase

### 2. Factura Duplicada (con folio interno manual)
- **Antes**: `12345 EMPRESA SERVICIOS SA`  
- **Ahora**: `155, EMPRESA SERVICIOS SA, 12345, SC Servicios`
- **Elementos**: Folio interno, Proveedor, Folio factura, Clase

### 3. Segunda Factura (VC) en División
- **Antes**: `12346 EMPRESA SERVICIOS SA`
- **Ahora**: `156, EMPRESA SERVICIOS SA, 12346, VC Servicios`
- **Elementos**: Folio interno, Proveedor, Folio factura, Clase

### 4. Datos Incompletos
- **Antes**: ` EMPRESA SERVICIOS SA` (con espacio al inicio)
- **Ahora**: `157, EMPRESA SERVICIOS SA, SC Servicios`
- **Mejora**: Filtrado de campos vacíos evita espacios innecesarios

### 5. Nombres Largos
- **Antes**: `98765 CONSTRUCTORA MATEHUALA SA DE CV`
- **Ahora**: `200, CONSTRUCTORA MATEHUALA SA DE CV, 98765, SC Servicios Constructivos`
- **Ventaja**: Información más completa y organizada

## Ventajas del Nuevo Formato

### ✅ **Información Más Completa**
- Incluye el tipo de vale (SC/VC Servicios)
- Diferencia entre folio interno y folio de factura
- Identificación clara del proveedor

### ✅ **Mejor Organización**
- Separación clara con comas
- Orden lógico de elementos
- Evita duplicación innecesaria de folios

### ✅ **Facilita la Búsqueda**
- Archivos organizables por folio interno
- Fácil identificación del tipo de vale
- Nombre del proveedor claramente visible

### ✅ **Casos Especiales Manejados**
- Facturas normales: formato optimizado sin duplicar folio
- Facturas duplicadas: incluye folio interno diferenciado
- División de facturas: identificación clara de SC vs VC

## Compatibilidad

### Facturas Existentes
- No afecta archivos ya generados
- Solo cambia el nombre sugerido en nuevas exportaciones

### Diferentes Tipos de Vale
- **SC (Servicios Constructivos)**: `Folio, Proveedor, Folio factura, SC Servicios`
- **VC (Vale Constructivo)**: `Folio, Proveedor, Folio factura, VC Servicios`
- **Otros tipos**: Se adaptará automáticamente

### Datos Faltantes
- Filtra campos vacíos automáticamente
- Mantiene formato consistente incluso con datos incompletos

## Casos de Uso Mejorados

### Archivo por Lotes
Antes:
```
12345 EMPRESA SERVICIOS SA.pdf
12346 EMPRESA SERVICIOS SA.pdf
```

Ahora:
```
155, EMPRESA SERVICIOS SA, 12345, SC Servicios.pdf
156, EMPRESA SERVICIOS SA, 12346, VC Servicios.pdf
```

### Búsqueda y Organización
- **Por folio interno**: Buscar "155"
- **Por proveedor**: Buscar "EMPRESA SERVICIOS"
- **Por tipo**: Buscar "SC Servicios" o "VC Servicios"
- **Por folio factura**: Buscar "12345"

## Archivos Modificados

1. **solicitud_app_professional.py**: Lógica principal del formato
2. **test_formato_nombres.py**: Script de validación y pruebas

## Próximos Pasos

1. **Probar con casos reales**: Validar que el formato funciona correctamente
2. **Verificar nombres largos**: Asegurar que Windows acepta los nombres generados
3. **Feedback del usuario**: Ajustar formato si es necesario

---
**Fecha de implementación**: Enero 2025  
**Tipo**: Mejora de UX - Nombres de archivo más informativos  
**Estado**: ✅ Implementado y probado  
**Impacto**: Mejor organización y búsqueda de archivos exportados
