# Mejora: Manejo de Folios para Segunda Factura con XML Duplicado

## Problema Identificado

Cuando se cargaba un XML que ya existía en la base de datos y se tenía la función "dividir" activada:

1. **Primera factura (SC)**: Se le pedía al usuario un folio manual ✅
2. **Segunda factura (VC)**: Se generaba automáticamente un folio sin pedirle al usuario ❌

Esto causaba un **conflicto potencial** porque la segunda factura podría usar un folio que ya existiera en la base de datos.

## Solución Implementada

### Cambios en `solicitud_app_professional.py`

Se modificó la lógica en el método `generar()` para que cuando se detecta una segunda factura (VC) después de dividir, verifique si la factura original estaba duplicada:

```python
if es_segunda_factura:
    logger.info("Detectada segunda factura (VC) después de dividir")
    
    # Si la factura original estaba duplicada (XML ya existía), 
    # también pedir folio manual para la segunda factura
    if self.factura_duplicada:
        logger.info("Factura original estaba duplicada, pidiendo folio manual para segunda factura")
        
        # Pedir folio manual para la segunda factura
        folio_manual_segunda = simpledialog.askstring(
            "Folio para Segunda Factura (VC)",
            f"El XML original ya existía en la base de datos.\n\n"
            f"Ingrese el folio interno para la segunda factura (VC):",
            initialvalue=folio_inicial_segunda
        )
        
        # Manejar la respuesta del usuario...
    else:
        # Generar folio automático para la segunda factura (caso normal)
        # Lógica existente...
```

### Flujo Mejorado

#### Caso 1: XML Nuevo (sin duplicados)
```
1. Cargar XML → ✅ No existe en BD
2. Primera factura (SC) → ✅ Folio automático de BD
3. Segunda factura (VC) → ✅ Folio automático incrementado
```

#### Caso 2: XML Duplicado (ya existe)
```
1. Cargar XML → ⚠️ Ya existe en BD
   💬 "Ingrese folio para primera factura": Usuario ingresa "155"

2. Primera factura (SC) → 📄 Usar folio manual "155"
   
3. Segunda factura (VC) → 💬 "Ingrese folio para segunda factura (VC)"
   💬 Valor inicial sugerido: "155"
   👤 Usuario ingresa: "156"
   📄 Usar folio manual "156"
```

## Beneficios

1. **Consistencia**: Ambas facturas siguen el mismo patrón cuando el XML está duplicado
2. **Sin conflictos**: Evita folios duplicados en la base de datos
3. **Control del usuario**: El usuario decide qué folios usar en casos de duplicados
4. **Compatibilidad**: Mantiene el flujo normal para XMLs nuevos
5. **Experiencia coherente**: Comportamiento predecible en ambos casos

## Validación

### Pruebas Realizadas

1. **test_folio_segunda_factura.py**: Verifica la lógica de decisión de folios
2. **test_flujo_integral_xml_duplicado.py**: Simula el flujo completo desde cargar XML hasta generar ambas facturas

### Escenarios Cubiertos

✅ XML nuevo + dividir → Folios automáticos  
✅ XML duplicado + dividir → Folios manuales para ambas facturas  
✅ XML duplicado + sin dividir → Folio manual para única factura  
✅ XML nuevo + sin dividir → Folio automático para única factura  

## Impacto

- **Usuarios**: Experiencia más coherente y control sobre folios en casos de duplicados
- **Base de datos**: Eliminación de conflictos de folios duplicados
- **Código**: Lógica más robusta y mantenible
- **Compatibilidad**: Sin cambios en el flujo existente para casos normales

## Archivos Modificados

- `src/solicitudapp/solicitud_app_professional.py`: Lógica principal mejorada
- `test_folio_segunda_factura.py`: Pruebas unitarias de la lógica
- `test_flujo_integral_xml_duplicado.py`: Pruebas de integración del flujo completo
- `MEJORA_FOLIO_SEGUNDA_FACTURA.md`: Esta documentación

---
**Fecha de implementación**: Enero 2025  
**Estado**: ✅ Completado y probado
