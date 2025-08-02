from cheque_form_control import FormPDF
from datetime import datetime
import sys
import os

# Agregar path para acceder a los modelos de BD
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from bd.models import Banco, OrdenCompra, Factura
except ImportError:
    print("Error: No se pudieron importar los modelos de la base de datos")
    Banco = OrdenCompra = Factura = None

class Cheque:
    def __init__(self, factura, ruta):
        """
        Inicializa el objeto Cheque con una factura y la ruta de exportación
        
        Args:
            factura: Diccionario con los datos de la factura
            ruta: Ruta donde se guardará el PDF del cheque
        """
        self.factura = factura
        self.ruta = ruta
        
        # Inicializar formulario con datos de la factura
        self.form_info = self._llenar_formulario_factura()
    
    def _llenar_formulario_factura(self):
        """
        Llena el formulario con los datos de una sola factura
        
        Returns:
            dict: Diccionario con los campos del formulario llenos
        """
        # Obtener fecha actual en formato dd/mm/aa
        fecha_actual = datetime.now().strftime("%d/%m/%y")
        
        # Extraer datos básicos de la factura
        proveedor = self.factura.get('nombre_emisor', '')
        numero_vale = self.factura.get('no_vale', '')
        folio_factura = self.factura.get('folio', '')
        tipo_vale = self.factura.get('clase', '')
        total_factura = self.factura.get('total', 0)
        folio_interno = self.factura.get('folio_interno')
        
        # Crear concepto: "Factura + número folio"
        concepto = f"Factura {folio_factura}" if folio_factura else "Factura"
        
        # Inicializar valores por defecto
        importe_letras = ""
        cuenta_banco = ""
        
        try:
            # Obtener datos de la orden de compra si existe
            if folio_interno and OrdenCompra:
                orden_compra = OrdenCompra.select().where(
                    OrdenCompra.factura == folio_interno
                ).first()
                
                if orden_compra:
                    importe_letras = orden_compra.importe_en_letras or ""
            
            # Obtener datos del banco BTC23
            if Banco:
                banco_btc23 = Banco.select().where(
                    Banco.codigo == "BTC23"
                ).first()
                
                if banco_btc23:
                    cuenta_banco = banco_btc23.cuenta or ""
                    
        except Exception as e:
            print(f"Error accediendo a la base de datos: {e}")
            # Los valores por defecto ya están establecidos
        
        return {
            "Fecha1_af_date": fecha_actual,
            "Orden": proveedor,
            "Moneda": importe_letras,
            "cuenta": cuenta_banco,
            "cheque": str(numero_vale),
            "Concepto": concepto,
            "area": "",
            "Costos": tipo_vale,
            "subcuenta": "",
            "Debe": "",
            "Haber": "",
            "Cuenta": cuenta_banco,  # Mismo valor que "cuenta"
            "Nombre": "",
            "Parcial": "",
            "Cantidad": str(total_factura),
        }
    
    def generar_cheque(self):
        """
        Genera el cheque PDF para una sola factura
        
        Returns:
            bool: True si se generó correctamente, False en caso contrario
        """
        try:
            # Crear instancia del formulario PDF
            form_pdf = FormPDF()
            
            # Llenar el formulario y guardarlo directamente
            form_pdf.rellenar(self.form_info, self.ruta)
            
            print(f"Cheque generado exitosamente en: {self.ruta}")
            return True
                
        except Exception as e:
            print(f"Error generando cheque: {str(e)}")
            return False

    def generar_multiple_cheques(self, facturas):
        """
        Método para generar cheques con múltiples facturas (a implementar después)
        
        Args:
            facturas: Lista de facturas para el cheque múltiple
        """
        pass

    def exportar(self):
        """
        Método de exportación principal que genera el cheque
        
        Returns:
            bool: True si se exportó correctamente, False en caso contrario
        """
        return self.generar_cheque()
    
    def get_datos_formulario(self):
        """
        Obtiene los datos del formulario para depuración
        
        Returns:
            dict: Diccionario con los datos del formulario
        """
        return self.form_info.copy()
    
    def actualizar_campo(self, campo, valor):
        """
        Actualiza un campo específico del formulario
        
        Args:
            campo: Nombre del campo a actualizar
            valor: Nuevo valor para el campo
        """
        if campo in self.form_info:
            self.form_info[campo] = valor
        else:
            print(f"Advertencia: Campo '{campo}' no existe en el formulario")