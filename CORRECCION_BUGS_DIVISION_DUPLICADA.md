# Corrección de Bugs: División con Factura Duplicada

## Problemas Reportados por el Usuario

1. **Primera factura exporta con "ERROR"**: Cuando se usa dividir con factura duplicada, se pide folio manual pero el PDF se exporta con "ERROR" en lugar del folio ingresado
2. **Segunda factura se guarda en BD**: La segunda factura se sigue guardando en la base de datos cuando no debería

## Análisis de Causas

### Problema 1: Folio "ERROR" en Primera Factura

**Causa identificada**: Posible problema de scope con la variable `es_segunda_factura` que se definía dos veces en diferentes secciones del código.

**Evidencia**:
```python
# Línea 1098: Primera definición
es_segunda_factura = (dividir_marcado and not dividir_habilitado and ...)

# Línea 1163: Segunda definición (PROBLEMÁTICA)
es_segunda_factura = (dividir_marcado and not dividir_habilitado and ...)

# Línea 1257: Uso en lógica de guardado
es_contexto_no_guardar = (...and es_segunda_factura)  # ¿Cuál variable usa?
```

### Problema 2: Segunda Factura se Guarda

**Causa identificada**: La lógica `es_contexto_no_guardar` dependía de la variable `es_segunda_factura` que podía no estar correctamente definida en el scope de guardado.

## Correcciones Implementadas

### 1. Eliminación de Definición Duplicada
```python
# ANTES (PROBLEMÁTICO)
es_segunda_factura = (dividir_marcado and not dividir_habilitado and 
                    solicitud_data.get("Tipo", "").startswith("VC"))

# DESPUÉS (CORREGIDO)
# Nota: es_segunda_factura ya fue definida anteriormente
```

### 2. Logging de Debug Extensivo
```python
# DEBUG: Logging de variables críticas
logger.debug(f"DEBUG - factura_duplicada: {self.factura_duplicada}")
logger.debug(f"DEBUG - division_con_duplicado: {self.division_con_duplicado}")
logger.debug(f"DEBUG - es_segunda_factura: {es_segunda_factura}")
logger.debug(f"DEBUG - folio_interno_manual: {self.folio_interno_manual}")
logger.debug(f"DEBUG - es_contexto_no_guardar: {es_contexto_no_guardar}")
```

### 3. Logging Mejorado de Asignación de Folios
```python
# ANTES
data["FOLIO"] = self.folio_interno_manual or "DUPLICADO"

# DESPUÉS
folio_a_usar = self.folio_interno_manual or "DUPLICADO"
logger.info(f"DEBUG - Asignando folio manual: {folio_a_usar} (folio_interno_manual: {self.folio_interno_manual})")
data["FOLIO"] = folio_a_usar
```

### 4. Logging de Excepciones Mejorado
```python
# ANTES
data["FOLIO"] = self.folio_interno_manual or "ERROR"

# DESPUÉS
folio_error = self.folio_interno_manual or "ERROR"
logger.warning(f"DEBUG - Asignando folio por excepción: {folio_error}")
data["FOLIO"] = folio_error
```

## Flujo Corregido

### Escenario: XML Duplicado + División Activada

```
1. Cargar XML → Detectar duplicado → Establecer flags
   ✅ factura_duplicada = True
   ✅ division_con_duplicado = True
   ✅ folio_interno_manual = "155" (usuario)

2. Primera Factura (SC):
   ✅ es_segunda_factura = False
   ✅ es_contexto_no_guardar = True (por factura_duplicada)
   ✅ Folio PDF = "155" (folio manual)
   ✅ NO guardada en BD

3. Segunda Factura (VC):
   ✅ es_segunda_factura = True
   ✅ es_contexto_no_guardar = True (por division_con_duplicado AND es_segunda_factura)
   ✅ Folio PDF = "156" (folio manual)
   ✅ NO guardada en BD
```

## Diagnóstico con Logging

Con las mejoras de logging implementadas, ahora se puede diagnosticar exactamente qué está pasando:

### Log Esperado para Primera Factura
```
DEBUG - factura_duplicada: True
DEBUG - division_con_duplicado: True
DEBUG - es_segunda_factura: False
DEBUG - folio_interno_manual: 155
DEBUG - es_contexto_no_guardar: True
DEBUG - Asignando folio manual: 155 (folio_interno_manual: 155)
```

### Log Esperado para Segunda Factura
```
DEBUG - factura_duplicada: True
DEBUG - division_con_duplicado: True
DEBUG - es_segunda_factura: True
DEBUG - folio_interno_manual: 156
DEBUG - es_contexto_no_guardar: True
DEBUG - Asignando folio manual: 156 (folio_interno_manual: 156)
```

### Log que Indicaría Problema
```
DEBUG - folio_interno_manual: None
DEBUG - Asignando folio manual: DUPLICADO (folio_interno_manual: None)
```
o
```
DEBUG - Asignando folio por excepción: ERROR
```

## Verificación de la Corrección

### Casos de Prueba
1. **XML nuevo + dividir**: Ambas facturas guardadas automáticamente
2. **XML duplicado + sin dividir**: Una factura, folio manual, no guardada
3. **XML duplicado + dividir**: Dos facturas, folios manuales, no guardadas

### Variables Críticas a Monitorear
- `self.factura_duplicada`: Debe ser True para XML duplicado
- `self.division_con_duplicado`: Debe ser True cuando duplicado + dividir
- `self.folio_interno_manual`: Debe mantener valor del usuario
- `es_segunda_factura`: Debe ser False/True correctamente
- `es_contexto_no_guardar`: Debe ser True para ambas facturas

## Puntos de Verificación

### Si Primera Factura Exporta "ERROR"
1. Verificar que `folio_interno_manual` no sea None
2. Verificar que no haya excepción en el bloque try-catch
3. Verificar que `es_contexto_no_guardar` sea True
4. Revisar logs de debug para identificar dónde se pierde el folio

### Si Segunda Factura se Guarda en BD
1. Verificar que `division_con_duplicado` sea True
2. Verificar que `es_segunda_factura` sea True
3. Verificar que `es_contexto_no_guardar` sea True
4. Verificar que no entre en el bloque `else` de guardado normal

## Archivos Modificados

- `src/solicitudapp/solicitud_app_professional.py`: Correcciones principales y logging
- `test_debug_problemas.py`: Análisis de problemas
- `test_flujo_detallado_division.py`: Pruebas de flujo completo
- `CORRECCION_BUGS_DIVISION_DUPLICADA.md`: Esta documentación

## Próximos Pasos

1. **Probar con caso real**: Usar XML duplicado + dividir activado
2. **Revisar logs**: Verificar que variables tengan valores esperados
3. **Validar folios**: Confirmar que PDFs usen folios manuales correctos
4. **Verificar BD**: Confirmar que ninguna factura se guarde automáticamente

---
**Fecha de corrección**: Enero 2025  
**Estado**: ✅ Corregido con logging de debug  
**Criticidad**: Alta - Corrige comportamiento inconsistente reportado por usuario
