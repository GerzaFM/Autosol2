from bd.models import db, Proveedor, Factura, Concepto, Reparto, Vale, OrdenCompra, Banco, Usuario, RepartoFavorito

class DBManager:
    def __init__(self):
        db.connect(reuse_if_open=True)
        db.create_tables([Proveedor, Factura, Concepto, Reparto, Vale, OrdenCompra, Banco, Usuario, RepartoFavorito], safe=True)

    def guardar_formulario(self, data):
        # Verificar si la factura ya existe
        factura_existente = Factura.get_or_none(
            (Factura.serie == data.get("serie")) & 
            (Factura.folio == data.get("folio"))
        )
        
        if factura_existente:
            raise ValueError(f"La factura {data.get('serie')}-{data.get('folio')} ya está registrada en la base de datos")
        
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
            tipo=data.get("tipo", "VC"),  # Agregar campo tipo con valor por defecto
            clase=data.get("clase"),  # Agregar campo clase
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

        # Guardar reparto/prorrateo si existe (incluir campo servicio)
        if any(data.get(k) for k in ["p_comercial", "p_fleet", "p_seminuevos", "p_refacciones", "p_servicio", "p_hyp", "p_administracion"]):
            Reparto.create(
                comercial=data.get("p_comercial"),
                fleet=data.get("p_fleet"),
                seminuevos=data.get("p_seminuevos"),
                refacciones=data.get("p_refacciones"),
                servicio=data.get("p_servicio"),
                hyp=data.get("p_hyp"),
                administracion=data.get("p_administracion"),
                factura=factura
            )

        # Puedes agregar aquí la lógica para guardar vales, ordenes, etc. si lo necesitas

        return factura

    def cerrar(self):
        if not db.is_closed():
            db.close()
    
    def guardar_reparto_favorito(self, usuario_id, posicion, nombre, categorias):
        """Guarda un reparto como favorito para un usuario en una posición específica."""
        try:
            # Eliminar favorito existente en esa posición
            RepartoFavorito.delete().where(
                (RepartoFavorito.usuario == usuario_id) & 
                (RepartoFavorito.posicion == posicion)
            ).execute()
            
            # Crear nuevo favorito
            favorito = RepartoFavorito.create(
                usuario=usuario_id,
                nombre_personalizado=nombre,
                comercial=categorias.get("Comer", 0),
                fleet=categorias.get("Fleet", 0),
                seminuevos=categorias.get("Semis", 0),
                refacciones=categorias.get("Refa", 0),
                servicio=categorias.get("Serv", 0),
                hyp=categorias.get("HyP", 0),
                administracion=categorias.get("Admin", 0),
                posicion=posicion
            )
            return favorito
        except Exception as e:
            print(f"Error al guardar favorito: {e}")
            return None

    def obtener_favoritos_usuario(self, usuario_id):
        """Obtiene todos los favoritos de un usuario ordenados por posición."""
        return list(RepartoFavorito.select().where(
            RepartoFavorito.usuario == usuario_id
        ).order_by(RepartoFavorito.posicion))

    def obtener_favorito_por_posicion(self, usuario_id, posicion):
        """Obtiene un favorito específico por usuario y posición."""
        return RepartoFavorito.get_or_none(
            (RepartoFavorito.usuario == usuario_id) & 
            (RepartoFavorito.posicion == posicion)
        )
    
    def eliminar_factura(self, factura_id):
        """
        Elimina una factura y todos sus registros relacionados.
        
        Args:
            factura_id: folio_interno de la factura a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            # Buscar la factura
            factura = Factura.get_or_none(Factura.folio_interno == factura_id)
            if not factura:
                raise ValueError(f"No se encontró la factura con folio_interno {factura_id}")
            
            # Eliminar conceptos relacionados
            conceptos_eliminados = Concepto.delete().where(Concepto.factura == factura).execute()
            
            # Eliminar repartos relacionados (si existen)
            repartos_eliminados = Reparto.delete().where(Reparto.factura == factura).execute()
            
            # Eliminar vales relacionados (si existen)
            vales_eliminados = Vale.delete().where(Vale.factura == factura).execute()
            
            # Finalmente eliminar la factura
            factura.delete_instance()
            
            print(f"Factura {factura_id} eliminada correctamente:")
            print(f"  - Conceptos eliminados: {conceptos_eliminados}")
            print(f"  - Repartos eliminados: {repartos_eliminados}")
            print(f"  - Vales eliminados: {vales_eliminados}")
            
            return True
            
        except Exception as e:
            print(f"Error al eliminar factura {factura_id}: {e}")
            import traceback
            traceback.print_exc()
            return False