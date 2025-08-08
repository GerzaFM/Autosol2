from bd.models import db, Proveedor, Factura, Concepto, Reparto, Vale, OrdenCompra, Banco, Usuario, RepartoFavorito
import os

class DBManager:
    def __init__(self):
        # Configurar la ruta absoluta a la base de datos
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        db_path = os.path.join(project_root, "facturas.db")
        
        # Reconectar con la ruta correcta
        if db.is_closed():
            db.init(db_path)
        
        db.connect(reuse_if_open=True)
        db.create_tables([Proveedor, Factura, Concepto, Reparto, Vale, OrdenCompra, Banco, Usuario, RepartoFavorito], safe=True)

    def guardar_formulario(self, data):
        try:
            with db.atomic():  # Usar transacción atómica
                # Preparar serie para la factura ANTES de validar duplicados
                serie_original = data.get("serie")
                
                # Si es la segunda factura dividida, agregar prefijo DIV-
                if data.get("es_segunda_factura_dividida", False):
                    serie_factura = f"DIV-{serie_original}"
                    print(f"📋 Segunda factura dividida detectada - Serie modificada: {serie_original} → {serie_factura}")
                else:
                    serie_factura = serie_original
                
                # Verificar si la factura ya existe (usando la serie ya modificada)
                factura_existente = Factura.get_or_none(
                    (Factura.serie == serie_factura) & 
                    (Factura.folio == data.get("folio"))
                )
                
                if factura_existente:
                    raise ValueError(f"La factura {serie_factura}-{data.get('folio')} ya está registrada en la base de datos")
                
                # BÚSQUEDA INTELIGENTE DE PROVEEDORES
                proveedor = None
                rfc_proveedor = data.get("rfc_proveedor", "").strip()
                nombre_proveedor = data.get("nombre_proveedor", "").strip()
                
                # PASO 1: Buscar por RFC exacto
                if rfc_proveedor:
                    proveedor = Proveedor.get_or_none(
                        Proveedor.rfc == rfc_proveedor
                    )
                    if proveedor:
                        print(f"✅ Proveedor encontrado por RFC: {proveedor.nombre}")
                
                # PASO 2: Si no encontró por RFC, búsqueda inteligente por nombre
                if not proveedor and nombre_proveedor:
                    def limpiar_nombre(nombre):
                        """Limpia nombre para comparación más flexible"""
                        if not nombre or nombre == "None":
                            return ""
                        # Convertir a mayúsculas y quitar caracteres especiales
                        import re
                        nombre_limpio = re.sub(r'[^A-Z0-9\s]', '', nombre.upper())
                        # Quitar palabras comunes
                        palabras_comunes = {'SA', 'DE', 'CV', 'SC', 'RL', 'SRL', 'SDERL', 'SADECV'}
                        palabras = [p for p in nombre_limpio.split() if p not in palabras_comunes]
                        return ' '.join(palabras).strip()
                    
                    def calcular_similitud(nombre1, nombre2):
                        """Calcula similitud entre nombres"""
                        nombre1_limpio = limpiar_nombre(nombre1)
                        nombre2_limpio = limpiar_nombre(nombre2)
                        
                        if not nombre1_limpio or not nombre2_limpio:
                            return 0
                        
                        # Buscar palabras en común
                        palabras1 = set(nombre1_limpio.split())
                        palabras2 = set(nombre2_limpio.split())
                        
                        if len(palabras1) == 0 or len(palabras2) == 0:
                            return 0
                        
                        # Calcular intersección
                        comunes = palabras1.intersection(palabras2)
                        total = palabras1.union(palabras2)
                        
                        if len(total) == 0:
                            return 0
                        
                        # Bonus si las primeras palabras coinciden
                        primera_palabra_coincide = (list(palabras1)[0] == list(palabras2)[0]) if len(palabras1) > 0 and len(palabras2) > 0 else False
                        
                        similitud_base = len(comunes) / len(total)
                        if primera_palabra_coincide:
                            similitud_base += 0.3  # Bonus por primera palabra
                        
                        return min(similitud_base, 1.0)
                    
                    # Buscar en todos los proveedores
                    mejor_proveedor = None
                    mejor_similitud = 0.0
                    
                    for prov_candidato in Proveedor.select():
                        # Comparar con nombre
                        if prov_candidato.nombre and prov_candidato.nombre != "None":
                            similitud = calcular_similitud(nombre_proveedor, prov_candidato.nombre)
                            if similitud > mejor_similitud and similitud >= 0.5:  # Mínimo 50% similitud
                                mejor_proveedor = prov_candidato
                                mejor_similitud = similitud
                        
                        # Comparar con nombre_en_quiter
                        if prov_candidato.nombre_en_quiter:
                            similitud = calcular_similitud(nombre_proveedor, prov_candidato.nombre_en_quiter)
                            if similitud > mejor_similitud and similitud >= 0.5:  # Mínimo 50% similitud
                                mejor_proveedor = prov_candidato
                                mejor_similitud = similitud
                    
                    if mejor_proveedor:
                        proveedor = mejor_proveedor
                        print(f"✅ Proveedor encontrado por similitud ({mejor_similitud:.2f}): {proveedor.nombre or proveedor.nombre_en_quiter}")
                
                # PASO 3: Actualizar datos del proveedor encontrado
                if proveedor:
                    # Actualizar campos con datos del formulario/XML
                    actualizado = False
                    
                    # Actualizar nombre con el del XML si viene
                    if nombre_proveedor and (not proveedor.nombre or proveedor.nombre == "None"):
                        proveedor.nombre = nombre_proveedor
                        actualizado = True
                        print(f"📝 Actualizando nombre: '{proveedor.nombre}'")
                    
                    # Actualizar RFC si no lo tenía
                    if rfc_proveedor and (not proveedor.rfc or proveedor.rfc == "None"):
                        proveedor.rfc = rfc_proveedor
                        actualizado = True
                        print(f"📝 Agregando RFC {rfc_proveedor} al proveedor")
                    
                    # Actualizar teléfono del formulario
                    if data.get("telefono_proveedor"):
                        proveedor.telefono = data.get("telefono_proveedor")
                        actualizado = True
                        print(f"📝 Actualizando teléfono: {proveedor.telefono}")
                    
                    # Actualizar email del formulario  
                    if data.get("email_proveedor"):
                        proveedor.email = data.get("email_proveedor")
                        actualizado = True
                        print(f"📝 Actualizando email: {proveedor.email}")
                    
                    # Actualizar contacto del formulario
                    if data.get("nombre_contacto_proveedor"):
                        proveedor.nombre_contacto = data.get("nombre_contacto_proveedor")
                        actualizado = True
                        print(f"📝 Actualizando contacto: {proveedor.nombre_contacto}")
                    
                    if actualizado:
                        proveedor.save()
                        print(f"📝 Datos del proveedor actualizados")
                
                # PASO 4: Si no existe, crear nuevo proveedor
                if not proveedor:
                    print(f"🆕 Creando nuevo proveedor: {nombre_proveedor}")
                    proveedor = Proveedor.create(
                        nombre=nombre_proveedor,
                        rfc=rfc_proveedor,
                        telefono=data.get("telefono_proveedor"),
                        email=data.get("email_proveedor"),
                        nombre_contacto=data.get("nombre_contacto_proveedor")
                    )

                # Guardar factura
                factura = Factura.create(
                    serie=serie_factura,
                    folio=data.get("folio"),
                    fecha=data.get("fecha"),
                    fecha_emision=data.get("fecha", data.get("fecha_emision")),  # Usar fecha como fallback
                    tipo=data.get("tipo", "VC"),  # Agregar campo tipo con valor por defecto
                    clase=data.get("clase"),  # Agregar campo clase
                    departamento=data.get("departamento"),  # Agregar campo departamento
                    cuenta_mayor=data.get("cuenta_mayor"),  # Agregar campo cuenta_mayor
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

                return factura
        except Exception as e:
            # Log del error para diagnóstico
            print(f"Error en guardar_formulario: {e}")
            raise

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
            vales_eliminados = Vale.delete().where(Vale.factura_id == factura).execute()
            
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

    def obtener_ultimo_vale(self):
        """
        Obtiene el último vale insertado en la base de datos.
        
        Returns:
            Vale: El último vale insertado o None si no hay vales
        """
        try:
            return Vale.select().order_by(Vale.id.desc()).first()
        except Exception as e:
            print(f"Error al obtener último vale: {e}")
            return None

# Alias para compatibilidad con código existente
BDControl = DBManager