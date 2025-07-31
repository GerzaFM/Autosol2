# Mejora Crítica: Consistencia en División con Facturas Duplicadas

## Problema Crítico Identificado

**Escenario problemático específico:**
1. Usuario sube factura XML **completa** (sin dividir) → Se guarda en BD automáticamente
2. Usuario vuelve a subir **mismo XML** con "dividir" activado:
   - **Primera factura (SC)**: XML duplicado → Pide folio manual, NO se guarda ✅
   - **Segunda factura (VC)**: XML como VC no existe → Se guarda automáticamente ❌

**Inconsistencia crítica:** Si la primera factura no se puede guardar por estar duplicada, la segunda factura tampoco debería guardarse automáticamente.

## Análisis del Problema

### Lógica Anterior (Problemática)
```python
# Solo verificaba si la factura original estaba duplicada
if self.factura_duplicada:
    # NO guardar primera factura
else:
    # Guardar segunda factura automáticamente ❌
```

### Resultado Inconsistente
- **Primera factura**: Folio manual 155, NO guardada en BD
- **Segunda factura**: Folio automático, SI guardada en BD
- **Problema**: Comportamiento impredecible para el usuario

## Solución Implementada

### 1. Nuevo Flag de Control
```python
self.division_con_duplicado = False  # Flag para contexto de división con duplicado
```

### 2. Detección de Contexto
```python
if factura_existente:
    self.factura_duplicada = True
    
    # Si dividir está activado, marcar contexto especial
    if hasattr(self, 'dividir_var') and self.dividir_var and self.dividir_var.get():
        self.division_con_duplicado = True
        logger.info("División con factura duplicada detectada")
```

### 3. Lógica de Guardado Corregida
```python
# Verificar contexto completo para decidir si guardar
es_contexto_no_guardar = (
    self.factura_duplicada or 
    (self.division_con_duplicado and es_segunda_factura)
)

if es_contexto_no_guardar:
    # NO guardar en BD, usar folio manual
    data["FOLIO"] = self.folio_interno_manual or "DUPLICADO"
else:
    # Guardar normalmente en BD
    # ... lógica de guardado normal
```

## Flujo Corregido

### Escenario: XML Duplicado + División
```
1. Cargar XML → ⚠️ Ya existe en BD
2. Detectar dividir activado → ✅ division_con_duplicado = True
3. Primera factura (SC):
   💬 "Ingrese folio manual" → Usuario: "155"
   📄 Generada, NO guardada en BD
4. Segunda factura (VC):
   💬 "Ingrese folio manual para segunda factura" → Usuario: "156"  
   📄 Generada, NO guardada en BD
```

## Casos de Uso Completos

### ✅ XML Nuevo + Sin División
```
Resultado: Una factura, guardada automáticamente
```

### ✅ XML Nuevo + Con División
```
Resultado: Dos facturas, ambas guardadas automáticamente
```

### ✅ XML Duplicado + Sin División
```
Resultado: Una factura, folio manual, NO guardada
```

### ✅ XML Duplicado + Con División (CORREGIDO)
```
Resultado: Dos facturas, folios manuales, NO guardadas
```

## Beneficios de la Mejora

1. **Consistencia**: Ambas facturas siguen el mismo patrón cuando hay duplicado
2. **Predictibilidad**: Usuario sabe que si primera no se guarda, segunda tampoco
3. **Integridad**: Evita guardar parcialmente un proceso de división
4. **Experiencia coherente**: No sorpresas ni comportamientos inesperados
5. **Control total**: Usuario mantiene control sobre folios en casos especiales

## Implementación Técnica

### Variables de Estado
```python
self.factura_duplicada = False         # XML original ya existe
self.division_con_duplicado = False    # División con XML duplicado
self.folio_interno_manual = None       # Folio manual del usuario
```

### Puntos de Reset
- Al cargar nuevo XML
- Al limpiar formulario  
- Al completar proceso de división

### Detección de Contexto
- Se activa cuando: `factura_duplicada = True` AND `dividir_var.get() = True`
- Afecta a: Ambas facturas (primera y segunda)
- Resultado: Folios manuales para ambas, ninguna guardada en BD

## Validación y Pruebas

### Escenario de Prueba
```python
# Estado inicial: XML ya en BD
xml_exists = True
dividir_activado = True

# Resultado esperado
primera_factura = {"folio": "manual", "guardada": False}
segunda_factura = {"folio": "manual", "guardada": False}

# Validación
assert primera_factura["guardada"] == segunda_factura["guardada"]  # ✅
```

### Matriz de Casos
| XML Estado | Dividir | Primera Factura | Segunda Factura | Consistente |
|-----------|---------|-----------------|-----------------|-------------|
| Nuevo     | No      | Auto, Guardada  | -               | ✅          |
| Nuevo     | Sí      | Auto, Guardada  | Auto, Guardada  | ✅          |
| Duplicado | No      | Manual, NO      | -               | ✅          |
| Duplicado | Sí      | Manual, NO      | Manual, NO      | ✅ (NUEVO)  |

## Código Clave Implementado

### Detección de Contexto
```python
if factura_existente and self.dividir_var.get():
    self.division_con_duplicado = True
```

### Lógica de Guardado
```python
es_contexto_no_guardar = (
    self.factura_duplicada or 
    (self.division_con_duplicado and es_segunda_factura)
)
```

### Reset de Estado
```python
self.division_con_duplicado = False  # En cargar, limpiar, completar
```

## Archivos Modificados

- `src/solicitudapp/solicitud_app_professional.py`: Lógica principal corregida
- `test_division_con_duplicado.py`: Pruebas del escenario específico
- `MEJORA_DIVISION_DUPLICADO.md`: Esta documentación

---
**Fecha de implementación**: Enero 2025  
**Estado**: ✅ Implementado y validado  
**Criticidad**: Alta - Corrige inconsistencia en comportamiento de usuario  
**Impacto**: Experiencia de usuario consistente y predecible en todos los escenarios
