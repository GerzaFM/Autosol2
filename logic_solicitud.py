from ctrl_xml import XMLFactura as Xml
import form_control as pdf

class SolicitudLogica:
    def __init__(self):
        self.solicitudes = []

    def agregar_solicitud(self, rutas):
        self.solicitudes.clear()

        if not rutas:
            print("No se ha seleccionado ningún archivo XML.")
            return
        
        for ruta in rutas:
            try:
                solicitud = Xml(ruta)
                self.solicitudes.append(solicitud)
            except ValueError as e:
                print(f"Error al procesar el archivo {ruta}: {e}")
                continue

    def solicitudes_restantes(self):
        return len(self.solicitudes)

    def rellenar_formulario(self, datos, ruta_salida):
        """
        Rellena el formulario PDF con los datos y lo guarda en la ruta indicada.
        :param datos: Diccionario con los datos a rellenar en el PDF.
        :param ruta_salida: Ruta donde se guardará el PDF generado.
        """
        form = pdf.FormPDF()
        form.rellenar(datos, ruta_salida)