from PyPDFForm import PdfWrapper
import sys
import os

# Manejar importaciones dependiendo del contexto
try:
    import solicitudapp.conf as conf
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    import solicitudapp.conf as conf

class FormPDF:
    """
    Clase para rellenar y guardar formularios PDF usando PyPDFForm.
    """

    def __init__(self):
        """
        Inicializa el formulario con la plantilla PDF.
        :param plantilla_pdf: Ruta al archivo PDF de la plantilla.
        """
        self.pdf = PdfWrapper(conf.form_solicitud_interna)

    def rellenar(self, datos, ruta_salida):
        """
        Rellena el formulario PDF con los datos y lo guarda en la ruta indicada.
        :param datos: Diccionario con los datos a rellenar en el PDF.
        :param ruta_salida: Ruta donde se guardará el PDF generado.
        """
        try:
            self.pdf.fill(datos)
            with open(ruta_salida, "wb") as output:
                output.write(self.pdf.read())
            print(f"PDF generado correctamente en: {ruta_salida}")
        except Exception as e:
            print(f"Error al generar el PDF: {e}")

if __name__ == "__main__":
    # Ejemplo de uso
    datos = {
        "campo1": "valor1",
        "campo2": "valor2"
    }
    form = FormPDF("Solicitud.pdf")
    form.rellenar(datos, "salida.pdf")