#!/usr/bin/env python3
"""
Script para crear datos de prueba completos con reparto.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from bd.models import Proveedor, Factura, Reparto
    from bd.bd_control import DBManager
    from decimal import Decimal
    
    print("🧹 Limpiando base de datos...")
    
    # Limpiar datos existentes
    Reparto.delete().execute()
    Factura.delete().execute()
    Proveedor.delete().execute()
    
    print("📝 Creando datos de prueba...")
    
    # Crear proveedor
    proveedor = Proveedor.create(
        nombre="ROSAURA GUTIERREZ DUARTE",
        rfc="GUDR51052879A",
        telefono="444-123-4567",
        email="test@proveedor.com",
        nombre_contacto="Rosaura Gutiérrez"
    )
    
    # Crear factura con tipo
    factura = Factura.create(
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
    
    # Crear reparto
    reparto = Reparto.create(
        comercial=Decimal("30.00"),
        fleet=Decimal("25.00"), 
        seminuevos=Decimal("15.00"),
        refacciones=Decimal("20.00"),
        hyp=Decimal("10.00"),
        administracion=Decimal("0.00"),
        factura=factura
    )
    
    print(f"✅ Datos creados:")
    print(f"   - Proveedor: {proveedor.nombre} ({proveedor.rfc})")
    print(f"   - Factura: {factura.serie}-{factura.folio} - Tipo: {factura.tipo}")
    print(f"   - Reparto: Comer={reparto.comercial}, Fleet={reparto.fleet}, Semis={reparto.seminuevos}")
    print(f"              Refa={reparto.refacciones}, HyP={reparto.hyp}, Admin={reparto.administracion}")
    
    # Probar búsqueda
    print("\n🔍 Probando búsqueda...")
    
    proveedor_encontrado = Proveedor.get_or_none(Proveedor.rfc == "GUDR51052879A")
    if proveedor_encontrado:
        print(f"✅ Proveedor encontrado: {proveedor_encontrado.nombre}")
        
        # Buscar última factura
        ultima_factura = (Factura
                        .select()
                        .where(Factura.proveedor == proveedor_encontrado)
                        .order_by(Factura.folio_interno.desc())
                        .first())
        
        if ultima_factura:
            print(f"✅ Última factura: {ultima_factura.serie}-{ultima_factura.folio}, Tipo: {ultima_factura.tipo}")
            
            # Buscar reparto
            ultimo_reparto = Reparto.get_or_none(Reparto.factura == ultima_factura)
            if ultimo_reparto:
                print(f"✅ Reparto encontrado: Comer={ultimo_reparto.comercial}, Fleet={ultimo_reparto.fleet}")
            else:
                print("❌ No se encontró reparto")
        else:
            print("❌ No se encontró factura")
    else:
        print("❌ No se encontró proveedor")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
