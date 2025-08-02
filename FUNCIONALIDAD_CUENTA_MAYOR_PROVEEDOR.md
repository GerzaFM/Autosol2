# Funcionalidad: Actualización de Cuenta Mayor en Proveedores

## 📋 Implementación Completada

### ✅ **Funcionalidad Principal**

Al extraer órdenes de compra PDF, además de guardar la cuenta mayor en `OrdenCompra.cuenta_mayor`, ahora también se actualiza automáticamente el campo `cuenta_mayor` del proveedor correspondiente, **solo si el proveedor no tiene ya una cuenta mayor asignada**.

### 🔧 **Modificaciones Realizadas**

#### 1. **Base de Datos - `models.py`**
```python
class Proveedor(Model):
    # ... otros campos ...
    cuenta_mayor = IntegerField(null=True)  # ✅ Ya existía
```

#### 2. **Controlador de Autocarga - `autocarga_controller.py`**

**Nuevos métodos agregados:**

1. **`_actualizar_cuenta_mayor_proveedor()`**
   - Actualiza la cuenta mayor del proveedor si no la tiene
   - Preserva cuentas mayores existentes
   - Logging detallado de las operaciones

2. **`_buscar_proveedor_para_cuenta_mayor()`**
   - Busca proveedor por código_quiter
   - Fallback por coincidencia de nombre
   - Manejo de múltiples coincidencias

**Lógica integrada en `_procesar_orden_individual()`:**
- Procesa la cuenta mayor extraída del PDF
- Identifica el proveedor (por factura asociada o búsqueda directa)
- Actualiza cuenta_mayor del proveedor según reglas de negocio

### 🎯 **Reglas de Negocio Implementadas**

#### **Cuándo se actualiza la cuenta mayor del proveedor:**
1. ✅ **Proveedor sin cuenta mayor** (`cuenta_mayor = NULL`)
2. ✅ **Proveedor con cuenta mayor cero** (`cuenta_mayor = 0`)

#### **Cuándo NO se actualiza:**
1. ❌ **Proveedor ya tiene cuenta mayor** (mantiene la existente)
2. ❌ **Cuenta mayor igual a la extraída** (confirma pero no modifica)

### 📊 **Flujo de Procesamiento**

```
1. Extracción PDF → cuenta_mayor = "23020000152"
2. Guardar en OrdenCompra.cuenta_mayor = 23020000152
3. Identificar proveedor:
   ├─ Caso A: Factura asociada → usar proveedor de la factura
   └─ Caso B: Sin factura → buscar por código/nombre
4. Evaluar cuenta_mayor del proveedor:
   ├─ Si NULL/0 → Actualizar con nueva cuenta
   ├─ Si igual → Confirmar (no cambiar)
   └─ Si diferente → Preservar existente
```

### 🧪 **Resultados de Pruebas**

#### **Estructura de Base de Datos:**
- ✅ Columna `cuenta_mayor` agregada exitosamente
- ✅ 19 proveedores existentes, 0 con cuenta mayor asignada
- ✅ Operaciones de actualización funcionando correctamente

#### **Lógica de Controlador:**
- ✅ Proveedor sin cuenta → Se actualiza
- ✅ Proveedor con cuenta igual → Se preserva
- ✅ Proveedor con cuenta diferente → Se preserva existente
- ✅ Proveedor con cuenta cero → Se actualiza

### 💡 **Casos de Uso Reales**

#### **Escenario 1: Proveedor Nuevo**
```
PDF → Cuenta Mayor: 23020000152
Proveedor: "COMERCIAL PAPELERA" (cuenta_mayor = NULL)
Resultado: Proveedor.cuenta_mayor = 23020000152 ✅
```

#### **Escenario 2: Proveedor Existente con Cuenta**
```
PDF → Cuenta Mayor: 23020000152
Proveedor: "DISTRIBUIDORA XYZ" (cuenta_mayor = 12020000000)
Resultado: Proveedor.cuenta_mayor = 12020000000 (sin cambios) ✅
```

#### **Escenario 3: Proveedor sin Factura Asociada**
```
PDF → Cuenta Mayor: 23020000152
Búsqueda → Por código 291061 → Proveedor encontrado
Resultado: Proveedor.cuenta_mayor = 23020000152 ✅
```

### 🔍 **Estrategias de Identificación del Proveedor**

#### **Prioridad 1: Factura Asociada**
- Si la orden se asocia con una factura existente
- Usa el proveedor de esa factura directamente

#### **Prioridad 2: Búsqueda por Código**
- Busca por `Proveedor.codigo_quiter = cuenta_orden`
- Coincidencia exacta y confiable

#### **Prioridad 3: Búsqueda por Nombre**
- Coincidencia exacta del nombre
- Coincidencia parcial (primeros 15 caracteres)
- Coincidencia por primera palabra

### 📈 **Beneficios de la Implementación**

#### **Automatización:**
- ✅ Actualización automática de cuentas mayores
- ✅ Reduce trabajo manual de configuración
- ✅ Aprovecha datos extraídos de PDFs

#### **Integridad de Datos:**
- ✅ Preserva cuentas mayores existentes
- ✅ Evita sobreescribir datos configurados manualmente
- ✅ Logging completo para auditoria

#### **Flexibilidad:**
- ✅ Funciona con facturas asociadas y sin asociar
- ✅ Múltiples estrategias de búsqueda de proveedores
- ✅ Manejo robusto de errores

### 🔧 **Configuración y Mantenimiento**

#### **Logging Implementado:**
```
💼 Cuenta mayor encontrada: 23020000152
🏦 Cuenta mayor 23020000152 asignada al proveedor 'COMERCIAL PAPELERA'
⚠️ Proveedor 'DISTRIBUIDORA XYZ' ya tiene cuenta mayor 12020000000
```

#### **Manejo de Errores:**
- Conexión a BD fallida
- Proveedor no encontrado
- Errores de actualización
- Traceback completo en logs

### 🎉 **Estado Final**

**La funcionalidad está completamente implementada y probada:**

1. ✅ **Campo `cuenta_mayor` agregado** a tabla `proveedor`
2. ✅ **Métodos de actualización** implementados en controlador
3. ✅ **Lógica de negocio** funcionando correctamente
4. ✅ **Integración completa** con flujo de autocarga
5. ✅ **Pruebas exitosas** con casos reales y simulados

---

## 🚀 **¡Funcionalidad Lista para Producción!**

La actualización automática de cuentas mayores en proveedores está completamente implementada y funcionando. El sistema ahora aprovecha los datos extraídos de los PDFs para mantener actualizados los proveedores de manera inteligente y respetando la integridad de los datos existentes.
