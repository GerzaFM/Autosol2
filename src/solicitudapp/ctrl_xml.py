import xml.etree.ElementTree as ET

class XMLFactura:
    """
    Clase para extraer datos relevantes de un CFDI 4.0 (SAT) en formato XML.
    """

    NAMESPACES = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}

    def __init__(self, ruta):
        self.ruta = ruta
        self.tree = None
        self.root = None

        # Inicializar atributos
        self.serie = ""
        self.folio = ""
        self.fecha_emision = ""
        self.subtotal = ""
        self.total = ""
        self.nombre_emisor = ""
        self.rfc_emisor = ""
        self.nombre_receptor = ""
        self.rfc_receptor = ""
        self.iva = ""
        self.iva_ret = ""
        self.isr_ret = ""
        self.conceptos = []

        self._cargar_xml()
        self._extraer_datos()

    def _cargar_xml(self):
        try:
            self.tree = ET.parse(self.ruta)
            self.root = self.tree.getroot()
        except Exception as e:
            raise ValueError(f"Error al cargar el archivo XML: {e}")

    def _extraer_datos(self):
        # Datos principales
        self.serie = self.root.attrib.get("Serie", "")
        self.folio = self.root.attrib.get("Folio", "")
        self.fecha_emision = self.root.attrib.get("Fecha", "")
        self.subtotal = self.root.attrib.get("SubTotal", "")
        self.total = self.root.attrib.get("Total", "")

        # Emisor
        emisor = self.root.find("cfdi:Emisor", self.NAMESPACES)
        if emisor is not None:
            self.nombre_emisor = emisor.attrib.get("Nombre", "")
            self.rfc_emisor = emisor.attrib.get("Rfc", "")

        # Receptor
        receptor = self.root.find("cfdi:Receptor", self.NAMESPACES)
        if receptor is not None:
            self.nombre_receptor = receptor.attrib.get("Nombre", "")
            self.rfc_receptor = receptor.attrib.get("Rfc", "")

        # Impuestos trasladados y retenidos
        impuestos = self.root.find("cfdi:Impuestos", self.NAMESPACES)
        self.iva = impuestos.attrib.get("TotalImpuestosTrasladados", "") if impuestos is not None else ""
        self.iva_ret = ""
        self.isr_ret = ""
        if impuestos is not None:
            retenciones = impuestos.find("cfdi:Retenciones", self.NAMESPACES)
            if retenciones is not None:
                for ret in retenciones.findall("cfdi:Retencion", self.NAMESPACES):
                    impuesto = ret.attrib.get("Impuesto", "")
                    importe = ret.attrib.get("Importe", "")
                    if impuesto == "002":  # IVA retenido
                        self.iva_ret = importe
                    elif impuesto == "001":  # ISR retenido
                        self.isr_ret = importe

        # Conceptos
        conceptos_factura = self.root.find("cfdi:Conceptos", self.NAMESPACES)
        if conceptos_factura is not None:
            for concepto in conceptos_factura.findall("cfdi:Concepto", self.NAMESPACES):
                cantidad = concepto.attrib.get("Cantidad", "")
                descripcion = concepto.attrib.get("Descripcion", "")
                precio_unitario = concepto.attrib.get("ValorUnitario", "")
                importe = concepto.attrib.get("Importe", "")
                self.conceptos.append((cantidad, descripcion, precio_unitario, importe))
        else:
            print("No se encontraron elementos cfdi:Conceptos")

    def get_datos_factura(self):
        """
        Devuelve un diccionario con los datos principales de la factura.
        """
        return {
            "serie": self.serie,
            "folio": self.folio,
            "fecha_emision": self.fecha_emision,
            "subtotal": self.subtotal,
            "total": self.total,
            "nombre_emisor": self.nombre_emisor,
            "rfc_emisor": self.rfc_emisor,
            "nombre_receptor": self.nombre_receptor,
            "rfc_receptor": self.rfc_receptor,
            "iva": self.iva,
            "iva_ret": self.iva_ret,
            "isr_ret": self.isr_ret,
            "conceptos": self.conceptos,
        }

if __name__ == "__main__":
    xml = XMLFactura("8954.xml")
    print(xml.get_datos_factura())