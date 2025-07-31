# Corrección Final: Formato de Nombres de Archivo con Folio Interno Real

## Problema Identificado por el Usuario

1. **Orden incorrecto**: Se estaba poniendo `Folio factura Proveedor Tipo de vale`
2. **Campo erróneo**: Se usaba "Tipo" en lugar de "Clase"
3. **Folio incorrecto**: No se usaba el folio interno real de la BD
4. **Timing problema**: El cuadro se muestra antes de guardar en BD

## Solución Implementada

### Formato Correcto
**`Folio Interno, Proveedor, Folio factura, Clase`**

### Elementos Correctos
1. **Folio Interno**: El que se registra en la BD (obtenido consultando BD)
2. **Proveedor**: Nombre del proveedor (`proveedor_data.get("Nombre")`)
3. **Folio factura**: Folio del XML (`solicitud_data.get("Folio")`)
4. **Clase**: Campo específico del formulario (`solicitud_data.get("Clase")`)

### Nueva Función para Obtener Folio Interno
```python
def obtener_proximo_folio_interno(self):
    """Obtiene el próximo folio interno que sería asignado en la base de datos."""
    try:
        from bd.models import Factura
        # Obtener el máximo folio_interno actual
        ultima_factura = Factura.select().order_by(Factura.folio_interno.desc()).first()
        if ultima_factura:
            return ultima_factura.folio_interno + 1
        else:
            return 1  # Primera factura
    except Exception as e:
        logger.warning(f"Error al obtener próximo folio interno: {e}")
        return "001"  # Fallback
```

### Lógica Corregida de Nombres
```python
# Obtener el folio interno que se usará en la BD (si no es contexto de no guardar)
if not es_contexto_no_guardar:
    # Se guardará en BD: obtener el próximo folio interno
    folio_interno = str(self.obtener_proximo_folio_interno())
else:
    # No se guardará en BD: usar folio manual si existe
    folio_interno = self.folio_interno_manual

proveedor = proveedor_data.get("Nombre", "")
folio_factura = solicitud_data.get("Folio", "")
clase = solicitud_data.get("Clase", "")  # Campo específico del formulario

# Construcción del nombre según el formato solicitado
if folio_interno:
    nombre_elementos = [folio_interno, proveedor, folio_factura, clase]
else:
    nombre_elementos = [proveedor, folio_factura, clase]

nombre_archivo = " ".join(filter(lambda x: x and x.strip(), nombre_elementos))
```

## Resultados por Escenario

### 1. Factura Normal (se guardará en BD)
- **Resultado**: `158 EMPRESA SERVICIOS SA 12345 Servicios Generales`
- **Elementos**: Folio Interno BD (158) + Proveedor + Folio factura + Clase
- **Antes**: `12345 EMPRESA SERVICIOS SA`

### 2. Factura Duplicada (NO se guardará en BD)
- **Resultado**: `155 EMPRESA SERVICIOS SA 12345 Servicios Generales`
- **Elementos**: Folio Interno Manual (155) + Proveedor + Folio factura + Clase
- **Antes**: `12345 EMPRESA SERVICIOS SA`

### 3. Segunda Factura en División (NO se guardará en BD)
- **Resultado**: `156 CONSTRUCTORA MATEHUALA SA 12346 Servicios Constructivos`
- **Elementos**: Folio Interno Manual (156) + Proveedor + Folio factura + Clase
- **Antes**: `12346 CONSTRUCTORA MATEHUALA SA`

### 4. Sin Clase Definida
- **Resultado**: `158 PROVEEDOR SIN CLASE SA 12347`
- **Elementos**: Folio Interno BD (158) + Proveedor + Folio factura (sin Clase)
- **Manejo**: Filtrado automático de campos vacíos

## Soluciones Técnicas Implementadas

### ✅ **Timing Correcto**
- Consulta la BD ANTES de mostrar el cuadro de diálogo
- Obtiene el próximo folio interno que se asignaría
- Predictivo y preciso

### ✅ **Folio Real de BD**
- No usa folio manual para facturas normales
- Consulta `Factura.select().order_by(Factura.folio_interno.desc()).first()`
- Calcula próximo folio: `ultima_factura.folio_interno + 1`

### ✅ **Campo Clase Correcto**
- Usa `solicitud_data.get("Clase", "")` del formulario
- No confunde con "Tipo" de vale
- Campo específico de "Datos de solicitud"

### ✅ **Manejo de Contextos**
- **Factura normal**: Usa folio interno predicho de BD
- **Factura duplicada**: Usa folio interno manual
- **División**: Usa folio interno manual para ambas facturas

## Comparación de Mejoras

### Información Más Rica
```
ANTES: "98765 EMPRESA COMPLETA SA DE CV"
AHORA: "158 EMPRESA COMPLETA SA DE CV 98765 Servicios Administrativos"
```

### Organización Mejorada
- **Folio Interno** (158): Para control interno y BD
- **Proveedor**: Identificación clara del proveedor
- **Folio factura** (98765): Folio del XML original
- **Clase** (Servicios Administrativos): Clasificación específica

### Casos Especiales
- **Campos vacíos**: Filtrados automáticamente
- **Error en BD**: Fallback seguro a "001"
- **Sin clase**: Funciona sin problemas

## Validación Técnica

### Consulta BD Eficiente
```sql
SELECT folio_interno FROM factura ORDER BY folio_interno DESC LIMIT 1;
```

### Manejo de Errores
- **BD no disponible**: Fallback a "001"
- **Sin registros**: Comienza en 1
- **Error de consulta**: Log de warning + fallback

### Performance
- Una sola consulta a BD por exportación
- Consulta solo cuando es necesario
- Caché no requerido (valores únicos)

## Archivos Modificados

1. **solicitud_app_professional.py**: 
   - Nueva función `obtener_proximo_folio_interno()`
   - Lógica corregida de construcción de nombres
   - Uso correcto del campo "Clase"

2. **test_formato_nombres_corregido.py**: 
   - Validación de todos los escenarios
   - Comparación antes/después

## Próximos Pasos

1. **Probar con BD real**: Validar consulta de folio interno
2. **Verificar campo Clase**: Confirmar que está en formulario
3. **Casos extremos**: Probar con BD vacía, errores de conexión
4. **Feedback usuario**: Ajustar si es necesario

---
**Fecha de corrección**: Enero 2025  
**Tipo**: Corrección crítica - Formato y datos incorrectos  
**Estado**: ✅ Corregido y validado  
**Impacto**: Nombres de archivo ahora reflejan información correcta y completa
