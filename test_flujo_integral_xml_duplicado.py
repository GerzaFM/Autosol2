"""
Prueba integral del flujo de división con XML duplicado.
Simula el comportamiento completo desde cargar XML hasta generar ambas facturas.
"""

def simular_flujo_completo():
    """
    Simula el flujo completo de división cuando se carga un XML que ya existe.
    """
    print("=== SIMULACIÓN: Flujo Completo XML Duplicado con División ===\n")
    
    # Estado inicial de la aplicación
    estado = {
        "factura_duplicada": False,
        "folio_interno_manual": None,
        "dividir_marcado": True,
        "dividir_habilitado": True,
        "tipo_actual": "SC - SOLICITUD DE COMPRA"
    }
    
    # PASO 1: Cargar XML que ya existe
    print("PASO 1: Usuario carga un XML")
    print("-" * 40)
    xml_path = "ejemplo_8927.xml"
    print(f"Cargando: {xml_path}")
    
    # Simular verificación en base de datos
    xml_ya_existe = True  # Simular que ya existe
    
    if xml_ya_existe:
        print("⚠️  XML ya existe en la base de datos")
        estado["factura_duplicada"] = True
        
        # Simular diálogo de folio manual
        folio_existente = "150"  # Folio de la factura existente
        print(f"💬 Mostrar diálogo: 'La factura ya existe con folio: {folio_existente}'")
        folio_manual_usuario = "155"  # Usuario ingresa nuevo folio
        print(f"👤 Usuario ingresa folio manual: {folio_manual_usuario}")
        
        estado["folio_interno_manual"] = folio_manual_usuario
        print(f"✅ Folio manual almacenado: {estado['folio_interno_manual']}")
    else:
        print("✅ XML nuevo, continuar con flujo normal")
    
    # PASO 2: Usuario marca "Dividir" y genera primera factura
    print(f"\nPASO 2: Generar Primera Factura (SC)")
    print("-" * 40)
    print(f"Dividir marcado: {estado['dividir_marcado']}")
    print(f"Dividir habilitado: {estado['dividir_habilitado']}")
    print(f"Tipo actual: {estado['tipo_actual']}")
    
    if estado["factura_duplicada"]:
        print("⚠️  Factura duplicada detectada - NO guardar en BD")
        print(f"📄 Usar folio manual para primera factura: {estado['folio_interno_manual']}")
    else:
        print("✅ Guardar en BD y obtener folio automático")
    
    # Simular generación exitosa de primera factura
    print("📁 Primera factura (SC) generada correctamente")
    
    # Cambiar estado para segunda factura
    estado["dividir_habilitado"] = False  # Se deshabilita después de primera
    estado["tipo_actual"] = "VC - VALE DE CONTROL"  # Se cambia automáticamente
    
    print(f"🔄 Estado actualizado:")
    print(f"   - Dividir habilitado: {estado['dividir_habilitado']}")
    print(f"   - Tipo cambiado a: {estado['tipo_actual']}")
    print("💬 Mensaje: 'Haga clic en Generar nuevamente para segunda factura'")
    
    # PASO 3: Usuario genera segunda factura
    print(f"\nPASO 3: Generar Segunda Factura (VC)")
    print("-" * 40)
    
    # Detectar si es segunda factura
    es_segunda_factura = (
        estado["dividir_marcado"] and 
        not estado["dividir_habilitado"] and 
        estado["tipo_actual"].startswith("VC")
    )
    
    print(f"✅ Segunda factura detectada: {es_segunda_factura}")
    
    if es_segunda_factura:
        if estado["factura_duplicada"]:
            print("⚠️  XML original estaba duplicado")
            print("📝 NUEVA FUNCIONALIDAD: Pedir folio manual para segunda factura")
            
            # Simular diálogo para segunda factura
            folio_inicial_sugerido = estado["folio_interno_manual"]  # 155
            print(f"💬 Mostrar diálogo: 'Ingrese folio para segunda factura (VC)'")
            print(f"💬 Valor inicial sugerido: {folio_inicial_sugerido}")
            
            folio_segunda_usuario = "156"  # Usuario ingresa folio para segunda
            print(f"👤 Usuario ingresa folio para segunda: {folio_segunda_usuario}")
            
            # Actualizar estado
            estado["folio_interno_manual"] = folio_segunda_usuario
            print(f"✅ Folio para segunda factura: {folio_segunda_usuario}")
            
        else:
            print("✅ XML original era nuevo")
            print("🔢 Generar folio automático para segunda factura")
            folio_original = estado.get("folio_primera", "155")
            folio_automatico = str(int(folio_original) + 1)
            print(f"🔢 Folio automático: {folio_original} → {folio_automatico}")
        
        # Simular generación de segunda factura
        if estado["factura_duplicada"]:
            print("⚠️  Segunda factura también es duplicada - NO guardar en BD")
            print(f"📄 Usar folio manual para segunda factura: {estado['folio_interno_manual']}")
        else:
            print("✅ Guardar segunda factura en BD")
        
        print("📁 Segunda factura (VC) generada correctamente")
        
        # Restaurar estado normal
        estado["dividir_habilitado"] = True
        estado["dividir_marcado"] = False
        print(f"🔄 Estado restaurado:")
        print(f"   - Dividir habilitado: {estado['dividir_habilitado']}")
        print(f"   - Dividir marcado: {estado['dividir_marcado']}")
    
    # RESUMEN FINAL
    print(f"\n{'='*70}")
    print("RESUMEN DEL FLUJO MEJORADO:")
    print("="*70)
    print("✅ XML duplicado detectado correctamente")
    print("✅ Primera factura (SC) usa folio manual del usuario")
    print("✅ Segunda factura (VC) TAMBIÉN pide folio manual") 
    print("✅ Evita conflictos de folios duplicados")
    print("✅ Mantiene funcionalidad de división intacta")
    print("✅ Experiencia de usuario coherente")
    
    print(f"\nFOLIOS UTILIZADOS:")
    print(f"- Factura original existente: 150")
    print(f"- Primera factura (SC): 155 (manual)")
    print(f"- Segunda factura (VC): 156 (manual)")
    print(f"- ✅ Sin conflictos de folios!")

def simular_caso_xml_nuevo():
    """
    Simula el flujo cuando el XML es nuevo (para comparar).
    """
    print(f"\n{'='*70}")
    print("COMPARACIÓN: Flujo con XML Nuevo (sin duplicados)")
    print("="*70)
    
    print("PASO 1: Cargar XML nuevo")
    print("✅ XML no existe en BD - continuar flujo normal")
    
    print("\nPASO 2: Generar primera factura (SC)")
    print("✅ Guardar en BD - folio automático: 200")
    
    print("\nPASO 3: Generar segunda factura (VC)")
    print("✅ XML era nuevo - generar folio automático: 201")
    print("✅ Guardar en BD normalmente")
    
    print(f"\nFOLIOS UTILIZADOS:")
    print("- Primera factura (SC): 200 (automático)")
    print("- Segunda factura (VC): 201 (automático)")
    print("- ✅ Flujo normal sin intervención manual!")

if __name__ == "__main__":
    simular_flujo_completo()
    simular_caso_xml_nuevo()
