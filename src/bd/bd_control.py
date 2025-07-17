from bd.models import db, Proveedor, Factura, Concepto, Reparto, Vale, OrdenCompra, Banco, Usuario

class DBManager:
    def __init__(self):
        db.connect(reuse_if_open=True)
        db.create_tables([Proveedor, Factura, Concepto, Reparto, Vale, OrdenCompra, Banco, Usuario], safe=True)

    def guardar_formulario(self, proveedor_data, factura_data, conceptos_data, reparto_data=None, vales_data=None, ordenes_data=None):
        # Guardar proveedor (o recuperar si ya existe)
        proveedor, created = Proveedor.get_or_create(
            id=proveedor_data.get("id"),
            defaults={
                "nombre": proveedor_data.get("nombre"),
                "rfc": proveedor_data.get("rfc"),
                "telefono": proveedor_data.get("telefono"),
                "email": proveedor_data.get("email"),
                "nombre_contacto": proveedor_data.get("nombre_contacto"),
                "codigo_quiter": proveedor_data.get("codigo_quiter"),
            }
        )

        # Guardar factura
        factura = Factura.create(
            folio_interno=factura_data.get("folio_interno"),
            serie=factura_data.get("serie"),
            folio=factura_data.get("folio"),
            fecha=factura_data.get("fecha"),
            nombre_emisor=factura_data.get("nombre_emisor"),
            rfc_emisor=factura_data.get("rfc_emisor"),
            nombre_receptor=factura_data.get("nombre_receptor"),
            rfc_receoptor=factura_data.get("rfc_receoptor"),
            subtotal=factura_data.get("subtotal"),
            ret_iva=factura_data.get("ret_iva"),
            ret_isr=factura_data.get("ret_isr"),
            iva_trasladado=factura_data.get("iva_trasladado"),
            total=factura_data.get("total"),
            comentario=factura_data.get("comentario"),
            proveedor=proveedor
        )

        # Guardar conceptos
        for concepto in conceptos_data:
            Concepto.create(
                descripcion=concepto.get("descripcion"),
                cantidad=concepto.get("cantidad"),
                precio_unitario=concepto.get("precio_unitario"),
                total=concepto.get("total"),
                factura=factura
            )

        # Guardar reparto si existe
        if reparto_data:
            Reparto.create(
                comercial=reparto_data.get("comercial"),
                fleet=reparto_data.get("fleet"),
                seminuevos=reparto_data.get("seminuevos"),
                refacciones=reparto_data.get("refacciones"),
                hyp=reparto_data.get("hyp"),
                administracion=reparto_data.get("administracion"),
                factura=factura
            )

        # Guardar vales si existen
        if vales_data:
            for vale in vales_data:
                Vale.create(
                    noVale=vale.get("noVale"),
                    tipo=vale.get("tipo"),
                    noDocumento=vale.get("noDocumento"),
                    descripcion=vale.get("descripcion"),
                    referencia=vale.get("referencia"),
                    total=vale.get("total"),
                    fechaVale=vale.get("fechaVale"),
                    departameto=vale.get("departameto"),
                    sucursal=vale.get("sucursal"),
                    marca=vale.get("marca"),
                    responsable=vale.get("responsable"),
                    proveedor=vale.get("proveedor"),
                    factura=factura
                )

        # Guardar ordenes de compra si existen
        if ordenes_data:
            for orden in ordenes_data:
                OrdenCompra.create(
                    id=orden.get("id"),
                    factura=factura,
                    cuenta=orden.get("cuenta"),
                    nombre=orden.get("nombre"),
                    referencia=orden.get("referencia"),
                    fecha=orden.get("fecha"),
                    importe=orden.get("importe"),
                    importe_en_letras=orden.get("importe_en_letras"),
                    iva=orden.get("iva"),
                    cuenta_mayor=orden.get("cuenta_mayor")
                )

        return factura

    def cerrar(self):
        if not db.is_closed():
            db.close()