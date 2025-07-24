import dbm
import sys
import os

# Manejar importaciones para diferentes contextos de ejecución
try:
    # Intento 1: importación relativa desde el mismo directorio
    from . import form_control as pdf
    from .ctrl_xml import XMLFactura as Xml
except ImportError:
    try:
        # Intento 2: importación absoluta (cuando se ejecuta desde src/)
        import solicitudapp.form_control as pdf
        from solicitudapp.ctrl_xml import XMLFactura as Xml
    except ImportError:
        # Intento 3: agregar el path correcto si es necesario
        current_dir = os.path.dirname(__file__)
        parent_dir = os.path.dirname(current_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        import solicitudapp.form_control as pdf
        from solicitudapp.ctrl_xml import XMLFactura as Xml

# Importar el controlador de BD
try:
    from bd.bd_control import DBManager
except ImportError:
    # Si falla, intentar con ruta relativa
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from bd.bd_control import DBManager

class SolicitudLogica:
    def __init__(self):
        self.solicitudes = []

    def agregar_solicitud(self, rutas):
        self.solicitudes.clear()

        if not rutas:
            print("La ruta no ha podido ser cargada.")
            return
        
        for ruta in rutas:
            try:
                solicitud = Xml(ruta)
                self.solicitudes.append(solicitud)
            except ValueError as e:
                print(f"Error al procesar el archivo {ruta}: {e}")
                continue

    def get_solicitudes_restantes(self):
        return len(self.solicitudes)
    
    def get_solicitud(self):
        if self.solicitudes:
            return self.solicitudes[0]
        return None
    
    def delete_solicitud(self):
        if self.solicitudes:
            self.solicitudes.pop(0)

    def siguiente_solicitud(self):
        self.delete_solicitud()

        return self.get_solicitud()

    def rellenar_formulario(self, datos, ruta_salida):
        """
        Rellena el formulario PDF con los datos y lo guarda en la ruta indicada.
        :param datos: Diccionario con los datos a rellenar en el PDF.
        :param ruta_salida: Ruta donde se guardará el PDF generado.
        """
        form = pdf.FormPDF()
        form.rellenar(datos, ruta_salida)

    def guardar_solicitud(self, proveedor_data, solicitud_data, conceptos, totales, categorias, comentarios):
        dbm = DBManager()
        
        # Obtener la fecha de emisión del XML actual
        fecha_emision = ""
        solicitud_actual = self.get_solicitud()
        if solicitud_actual:
            fecha_emision = solicitud_actual.fecha_emision
        
        # Construye el diccionario 'data' como lo haces
        data = {
            # Datos del proveedor
            "nombre_proveedor": proveedor_data.get("nombre"),
            "rfc_proveedor": proveedor_data.get("rfc"),
            "telefono_proveedor": proveedor_data.get("telefono"),
            "email_proveedor": proveedor_data.get("email"),
            "nombre_contacto_proveedor": proveedor_data.get("nombre_contacto"),
            # Datos de la solicitud
            "serie": solicitud_data.get("serie"),
            "folio": solicitud_data.get("folio"),
            "fecha": solicitud_data.get("fecha"),
            "fecha_emision": fecha_emision,
            "tipo": solicitud_data.get("tipo"),
            "nombre_receptor": solicitud_data.get("nombre_receptor"),
            "rfc_receptor": solicitud_data.get("rfc_receptor"),
            "subtotal": totales.get("subtotal"),
            "iva_trasladado": totales.get("iva_trasladado"),
            "ret_iva": totales.get("ret_iva"),
            "ret_isr": totales.get("ret_isr"),
            "total": totales.get("total"),
            "comentario": comentarios.get("comentario"),
            # Datos de los conceptos
            "conceptos": [
                {
                    "descripcion": concepto.get("descripcion"),
                    "cantidad": concepto.get("cantidad"),
                    "unidad": concepto.get("unidad"),
                    "precio_unitario": concepto.get("precio_unitario"),
                    "importe": concepto.get("importe"),
                }
                for concepto in conceptos
            ],
            # Prorrateo y reparto
            "p_comercial": categorias.get("comercial"),
            "p_fleet": categorias.get("fleet"),
            "p_seminuevos": categorias.get("seminuevos"),
            "p_refacciones": categorias.get("refacciones"),
            "p_hyp": categorias.get("hyp"),
            "p_servicio": categorias.get("servicio"),
            "p_administracion": categorias.get("administracion"),
            # Comentarios adicionales
            "comentarios": comentarios.get("comentarios"),
        }

        factura = dbm.guardar_formulario(data)
        dbm.cerrar()
        return factura 
