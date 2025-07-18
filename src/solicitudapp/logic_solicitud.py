import dbm
import solicitudapp.form_control as pdf

from solicitudapp.ctrl_xml import XMLFactura as Xml
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
            "p_administracion": categorias.get("administracion"),
            # Comentarios adicionales
            "comentarios": comentarios.get("comentarios"),
        }

        factura = dbm.guardar_formulario(data)
        dbm.cerrar()
        return factura 
