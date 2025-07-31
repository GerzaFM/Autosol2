# 📋 INSTRUCCIONES: Funcionalidad DIVIDIR en Solicitud de Compra

## 🎯 ¿Qué hace la funcionalidad "Dividir"?

La funcionalidad **DIVIDIR** permite crear automáticamente dos facturas idénticas con la mitad de los valores en cada una:

1. **Primera factura**: Se guarda con el tipo original y valores divididos por 2
2. **Segunda factura**: Se guarda automáticamente como "VC - VALE DE CONTROL" con valores divididos por 2

## 🔧 Cómo usar la funcionalidad

### Paso 1: Llenar el formulario normalmente
- Complete todos los datos del proveedor
- Agregue los conceptos necesarios
- Los totales se calcularán automáticamente

### Paso 2: Activar la función dividir
- ✅ **Marque la casilla "Dividir"** antes de generar
- La casilla solo estará disponible cuando el formulario esté completo

### Paso 3: Generar documento
- Haga clic en **"Generar"**
- Seleccione dónde guardar el PDF

## ⚡ ¿Qué sucede automáticamente?

### Al marcar "Dividir" y generar:

1. **Se dividen todos los totales por 2:**
   - Subtotal ÷ 2
   - Retenciones ÷ 2  
   - IVA ÷ 2
   - Total ÷ 2

2. **Se guarda PRIMERA factura en la base de datos:**
   - Tipo: El que seleccionó originalmente
   - Valores: Divididos por 2
   - Folio interno: Se asigna automáticamente

3. **Se genera el PDF de la primera factura**

4. **Se cambia automáticamente el tipo a "VC - VALE DE CONTROL"**

5. **Se guarda SEGUNDA factura en la base de datos:**
   - Tipo: "VC - VALE DE CONTROL"
   - Valores: Divididos por 2
   - Folio interno: Se asigna automáticamente (diferente al anterior)

6. **La casilla "Dividir" se deshabilita**

### Después de dividir:
- Los campos quedan llenos con los valores divididos
- El tipo cambia a "VC - VALE DE CONTROL"
- Al generar nuevamente, se crea el PDF de la segunda factura (VC)

## ✅ Beneficios

- **Automatización completa**: No necesita dividir manualmente los valores
- **Consistencia**: Ambas facturas suman exactamente el total original
- **Trazabilidad**: Cada factura tiene su propio folio_interno en la base de datos
- **Control**: Se evitan errores de cálculo manual

## 🚨 Puntos importantes

1. **La funcionalidad solo funciona UNA VEZ por formulario**
   - Una vez dividido, debe llenar un nuevo formulario para dividir otra factura

2. **Ambas facturas se guardan en la base de datos**
   - Primera: Con tipo original
   - Segunda: Como "VC - VALE DE CONTROL"

3. **Los valores se dividen exactamente por 2**
   - Si hay decimales, se redondea a 2 decimales

4. **Si hay error al guardar la segunda factura (VC)**
   - Se muestra un mensaje de error
   - La primera factura ya está guardada y es válida

## 🔍 Verificación

Para verificar que todo funcionó correctamente:

1. **Revise los logs de la aplicación**
   - Verá mensajes como: "Primera factura guardada con folio_interno: X"
   - Y: "Segunda factura (VC) guardada con folio_interno: Y"

2. **Consulte la base de datos**
   - Busque las dos facturas por el folio_interno asignado
   - Verifique que los totales de ambas sumen el valor original

## 🛠️ Solución de problemas

### Problema: "ERROR" en el folio
**Causa**: Error al guardar en la base de datos
**Solución**: Revise los logs para ver el error específico

### Problema: La casilla "Dividir" no aparece
**Causa**: Formulario incompleto
**Solución**: Complete todos los campos requeridos

### Problema: Solo se guarda una factura
**Causa**: Error en la segunda factura (VC)
**Solución**: La primera factura ya está guardada, revise los logs para el error específico

---

## 📊 Ejemplo práctico

### Factura original:
- Subtotal: $1,000.00
- IVA: $160.00
- Total: $1,160.00

### Al marcar "Dividir":

**Primera factura guardada:**
- Tipo: "SC - SOLICITUD DE COMPRA"
- Subtotal: $500.00
- IVA: $80.00
- Total: $580.00
- Folio interno: 123

**Segunda factura guardada:**
- Tipo: "VC - VALE DE CONTROL"
- Subtotal: $500.00
- IVA: $80.00
- Total: $580.00
- Folio interno: 124

**Suma: $580.00 + $580.00 = $1,160.00 ✅**
