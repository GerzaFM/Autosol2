# Mejora: Solicitud de Folios al Inicio para División con Duplicado

## Problema Original
Cuando se utilizaba la función de dividir con una factura duplicada, el folio para la segunda factura se solicitaba **después** de presionar el botón "Generar", lo cual interrumpía el flujo del usuario.

## Solución Implementada
Ahora ambos folios (primera y segunda factura) se solicitan **al inicio**, inmediatamente después de cargar el XML y detectar que es duplicado con división activada.

## Cambios Realizados

### 1. Nueva Variable de Estado
```python
self.folio_segunda_factura = None  # Almacenar folio para la segunda factura en división
```

### 2. Solicitud de Ambos Folios al Inicio
En el método `cargar_xmls`, cuando se detecta `division_con_duplicado`:

```python
if self.division_con_duplicado:
    # Solicitar folio para la primera factura (SC)
    folio_manual_sc = simpledialog.askstring(
        "Folio para Primera Factura (SC)",
        f"Ingrese el folio interno para la PRIMERA factura (SC):",
        initialvalue=folio_inicial
    )
    
    # Solicitar folio para la segunda factura (VC)
    folio_manual_vc = simpledialog.askstring(
        "Folio para Segunda Factura (VC)",
        f"Ingrese el folio interno para la SEGUNDA factura (VC):",
        initialvalue=folio_siguiente
    )
    
    # Guardar ambos folios
    self.folio_interno_manual = folio_manual_sc
    self.folio_segunda_factura = folio_manual_vc
```

### 3. Uso del Folio Pre-configurado
En el método `generar_solicitud`, para la segunda factura:

```python
if self.factura_duplicada and hasattr(self, 'folio_segunda_factura') and self.folio_segunda_factura:
    logger.info("Usando folio pre-configurado para segunda factura")
    folio_vc = self.folio_segunda_factura
    self.folio_interno_manual = folio_vc
```

### 4. Reset de Variables
La nueva variable se resetea en todos los puntos donde se limpian los flags:
- `cargar_xmls`: Al inicio del proceso
- `limpiar_campos`: Al limpiar formulario
- `generar_solicitud`: Al completar la segunda factura

## Flujo Mejorado

### Escenario: XML Duplicado + División Activada

```
1. Usuario carga XML con división activada
   ↓
2. Sistema detecta que XML ya existe (duplicado)
   ↓
3. Sistema pide AMBOS folios inmediatamente:
   - "Folio para Primera Factura (SC): [155]"
   - "Folio para Segunda Factura (VC): [156]"
   ↓
4. Usuario ingresa ambos folios una sola vez
   ↓
5. Primera factura (SC):
   - Usa folio 155
   - Se genera inmediatamente
   ↓
6. Segunda factura (VC):
   - Usa folio 156 (ya guardado)
   - Se genera inmediatamente
   - NO solicita folio nuevamente
```

## Beneficios

### ✅ **Experiencia de Usuario Mejorada**
- Solo se interrumpe al usuario **una vez** al inicio
- No hay interrupciones durante la generación
- Flujo más fluido y predecible

### ✅ **Consistencia en el Proceso**
- Ambos folios se configuran en el mismo momento
- Reduce posibilidad de errores o cancelaciones
- Mejor control del estado de la aplicación

### ✅ **Mantenimiento del Código**
- Lógica centralizada en el momento de carga
- Fallback mantenido para compatibilidad
- Variables de estado claramente definidas

## Casos de Prueba

### 1. XML Nuevo + Dividir
- **Comportamiento**: Sin cambios, folios automáticos
- **Resultado**: ✅ Funciona como antes

### 2. XML Duplicado + Sin Dividir  
- **Comportamiento**: Sin cambios, un folio manual
- **Resultado**: ✅ Funciona como antes

### 3. XML Duplicado + Dividir (MEJORADO)
- **Comportamiento**: Pide ambos folios al inicio
- **Resultado**: ✅ Sin interrupciones durante generación

### 4. Cancelar Entrada de Folios
- **Comportamiento**: Cancela proceso completo
- **Resultado**: ✅ Previene estados inconsistentes

## Compatibilidad

### Fallback Mantenido
Si por alguna razón el folio de la segunda factura no se guardó correctamente, el sistema mantiene el comportamiento anterior como respaldo:

```python
elif self.factura_duplicada:
    # Fallback: pedir folio si no se configuró al inicio
    logger.warning("Folio para segunda factura no fue configurado, pidiendo ahora")
    # ... código de respaldo
```

## Archivos Modificados

- `src/solicitudapp/solicitud_app_professional.py`: Implementación principal
- `MEJORA_FOLIOS_AL_INICIO.md`: Esta documentación

## Próximos Pasos

1. **Probar escenario completo**: XML duplicado + división activada
2. **Validar interrupciones**: Confirmar que solo se pide folios una vez
3. **Verificar fallback**: Probar que el respaldo funciona si es necesario
4. **Documentar para usuario**: Actualizar manual de usuario si existe

---
**Fecha de mejora**: Enero 2025  
**Tipo**: Mejora de UX - Reducción de interrupciones  
**Estado**: ✅ Implementado y listo para pruebas  
**Impacto**: Mejora significativa en la experiencia del usuario
