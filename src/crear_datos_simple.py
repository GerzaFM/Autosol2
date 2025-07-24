#!/usr/bin/env python3
"""
Script simple para crear datos de prueba.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from bd.models import db, Proveedor, Factura, Reparto
    from decimal import Decimal
    
    print("🔌 Conectando a la base de datos...")
    db.connect(reuse_if_open=True)
    
    print("📋 Creando tablas...")
    db.create_tables([Proveedor, Factura, Reparto], safe=True)
    
    print("🧹 Limpiando datos existentes...")
    # Limpiar datos existentes en orden correcto (respetando foreign keys)
    Reparto.delete().execute()
    Factura.delete().execute() 
    Proveedor.delete().execute()
    
    print("📝 Creando proveedor...")
    # Crear proveedor especificando ID manualmente
    proveedor = Proveedor.create(
        id=1,  # Especificar ID manualmente
        nombre="ROSAURA GUTIERREZ DUARTE",
        rfc="GUDR51052879A",
        telefono="444-123-4567",
        email="test@proveedor.com",
        nombre_contacto="Rosaura Gutiérrez"
    )
    print(f"✅ Proveedor creado con ID: {proveedor.id}")
    
    print("📝 Creando factura...")
    # Crear factura especificando folio_interno
    factura = Factura.create(
        folio_interno=1,  # Especificar ID manualmente
        serie=100,
        folio=123,
        fecha="2025-01-15",
        tipo="GA",  # COMBUSTIBLES Y LUBRICANTES
        nombre_emisor=proveedor.nombre,
        rfc_emisor=proveedor.rfc,
        nombre_receptor="TCM MATEHUALA",
        rfc_receptor="TMM860630PH1",
        subtotal=Decimal("1000.00"),
        iva_trasladado=Decimal("160.00"),
        total=Decimal("1160.00"),
        comentario="Factura de prueba",
        proveedor=proveedor
    )
    print(f"✅ Factura creada con ID: {factura.folio_interno}")
    
    print("📝 Creando reparto...")
    # Crear reparto especificando ID
    reparto = Reparto.create(
        id=1,  # Especificar ID manualmente
        comercial=Decimal("30.00"),
        fleet=Decimal("25.00"), 
        seminuevos=Decimal("15.00"),
        refacciones=Decimal("20.00"),
        servicio=Decimal("5.00"),
        hyp=Decimal("5.00"),
        administracion=Decimal("0.00"),
        factura=factura
    )
    print(f"✅ Reparto creado con ID: {reparto.id}")
    
    print("🔍 Verificando datos...")
    # Verificar que los datos se crearon correctamente
    proveedor_test = Proveedor.get_or_none(Proveedor.rfc == "GUDR51052879A")
    if proveedor_test:
        print(f"✅ Proveedor verificado: {proveedor_test.nombre}")
        
        # Buscar última factura
        ultima_factura = (Factura
                        .select()
                        .where(Factura.proveedor == proveedor_test)
                        .order_by(Factura.folio_interno.desc())
                        .first())
        
        if ultima_factura:
            print(f"✅ Factura verificada: {ultima_factura.serie}-{ultima_factura.folio}, Tipo: {ultima_factura.tipo}")
            
            # Buscar reparto
            ultimo_reparto = Reparto.get_or_none(Reparto.factura == ultima_factura)
            if ultimo_reparto:
                print(f"✅ Reparto verificado: Comer={ultimo_reparto.comercial}, Fleet={ultimo_reparto.fleet}, Servicio={ultimo_reparto.servicio}")
                print("🎉 ¡Datos de prueba creados exitosamente!")
            else:
                print("❌ No se encontró reparto")
        else:
            print("❌ No se encontró factura")
    else:
        print("❌ No se encontró proveedor")
        
    db.close()
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
