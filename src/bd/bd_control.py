from bd.models import db, Proveedor, Factura, Concepto, Reparto, Vale, OrdenCompra, Banco, Usuario

class DBManager:
    def __init__(self):
        db.connect(reuse_if_open=True)
        db.create_tables([Proveedor, Factura, Concepto, Reparto, Vale, OrdenCompra, Banco, Usuario], safe=True)

    def guardar_formulario(self, data):
        # Guardar proveedor
        proveedor, _ = Proveedor.get_or_create(
            rfc=data.get("rfc_proveedor"),
            defaults={
                "nombre": data.get("nombre_proveedor"),
                "telefono": data.get("telefono_proveedor"),
                "email": data.get("email_proveedor"),
                "nombre_contacto": data.get("nombre_contacto_proveedor"),
            }
        )

        # Guardar factura
        factura = Factura.create(
            serie=data.get("serie"),
            folio=data.get("folio"),
            fecha=data.get("fecha"),
            nombre_emisor=data.get("nombre_proveedor"),
            rfc_emisor=data.get("rfc_proveedor"),
            nombre_receptor=data.get("nombre_receptor"),
            rfc_receptor=data.get("rfc_receptor"),
            subtotal=data.get("subtotal"),
            iva_trasladado=data.get("iva_trasladado"),
            ret_iva=data.get("ret_iva"),
            ret_isr=data.get("ret_isr"),
            total=data.get("total"),
            comentario=data.get("comentario"),
            proveedor=proveedor
        )

        # Guardar conceptos
        for concepto in data.get("conceptos", []):
            Concepto.create(
                descripcion=concepto.get("descripcion"),
                cantidad=concepto.get("cantidad"),
                precio_unitario=concepto.get("precio_unitario"),
                total=concepto.get("importe"),
                factura=factura
            )

        # Guardar reparto/prorrateo si existe
        if any(data.get(k) for k in ["p_comercial", "p_fleet", "p_seminuevos", "p_refacciones", "p_hyp", "p_administracion"]):
            Reparto.create(
                comercial=data.get("p_comercial"),
                fleet=data.get("p_fleet"),
                seminuevos=data.get("p_seminuevos"),
                refacciones=data.get("p_refacciones"),
                hyp=data.get("p_hyp"),
                administracion=data.get("p_administracion"),
                factura=factura
            )

        # Puedes agregar aquí la lógica para guardar vales, ordenes, etc. si lo necesitas

        return factura

    def cerrar(self):
        if not db.is_closed():
            db.close()