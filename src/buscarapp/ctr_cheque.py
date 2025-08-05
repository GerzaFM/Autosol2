from cheque_form_control import FormPDF
from datetime import datetime
import sys
import os
from decimal import Decimal

# Agregar path para acceder a los modelos de BD
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from bd.models import Banco, OrdenCompra, Factura, Proveedor
    # Importar configuración para cuentas mayores
    sys.path.insert(0, os.path.join(parent_dir, '..', 'config'))
    from app_config import AppConfig
except ImportError:
    print("Error: No se pudieron importar los modelos de la base de datos")
    Banco = OrdenCompra = Factura = Proveedor = None
    AppConfig = None


def numero_a_letras(numero):
    """
    Convierte un número a letras en español con formato de centavos x/100
    
    Args:
        numero (float, int, str, Decimal): Número a convertir
    
    Returns:
        str: Número convertido a letras con formato "PESOS XX/100 MN"
    
    Ejemplo:
        numero_a_letras(1234.56) -> "MIL DOSCIENTOS TREINTA Y CUATRO PESOS 56/100 MN"
        numero_a_letras(100) -> "CIEN PESOS 00/100 MN"
        numero_a_letras(0.75) -> "CERO PESOS 75/100 MN"
    """
    try:
        # Convertir a Decimal para manejo preciso de decimales
        if isinstance(numero, str):
            # Limpiar string (remover comas, espacios, etc.)
            numero_limpio = numero.replace(',', '').replace(' ', '').strip()
            num = Decimal(numero_limpio)
        else:
            num = Decimal(str(numero))
        
        # Separar parte entera y centavos
        parte_entera = int(num)
        centavos = int((num - parte_entera) * 100)
        
        # Diccionarios para conversión
        unidades = ["", "UNO", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE"]
        especiales = ["DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISÉIS", 
                     "DIECISIETE", "DIECIOCHO", "DIECINUEVE"]
        decenas = ["", "", "VEINTE", "TREINTA", "CUARENTA", "CINCUENTA", "SESENTA", 
                  "SETENTA", "OCHENTA", "NOVENTA"]
        centenas = ["", "CIENTO", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS",
                   "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]
        
        def convertir_grupo(num):
            """Convierte un grupo de 3 dígitos a letras"""
            if num == 0:
                return ""
            
            resultado = ""
            
            # Centenas
            if num >= 100:
                if num == 100:
                    resultado += "CIEN"
                else:
                    resultado += centenas[num // 100]
                num %= 100
                if num > 0:
                    resultado += " "
            
            # Decenas y unidades
            if num >= 20:
                resultado += decenas[num // 10]
                num %= 10
                if num > 0:
                    resultado += " Y " + unidades[num]
            elif num >= 10:
                resultado += especiales[num - 10]
            elif num > 0:
                resultado += unidades[num]
            
            return resultado
        
        def numero_completo_a_letras(numero):
            """Convierte un número completo a letras"""
            if numero == 0:
                return "CERO"
            
            grupos = []
            nombres_grupos = ["", "MIL", "MILLONES", "MIL MILLONES"]
            grupo_idx = 0
            
            while numero > 0 and grupo_idx < len(nombres_grupos):
                grupo = numero % 1000
                if grupo > 0:
                    grupo_letras = convertir_grupo(grupo)
                    
                    if grupo_idx == 1:  # Miles
                        if grupo == 1:
                            grupos.append("MIL")
                        else:
                            grupos.append(grupo_letras + " MIL")
                    elif grupo_idx == 2:  # Millones
                        if grupo == 1:
                            grupos.append("UN MILLÓN")
                        else:
                            grupos.append(grupo_letras + " MILLONES")
                    elif grupo_idx == 3:  # Mil millones
                        grupos.append(grupo_letras + " MIL MILLONES")
                    else:  # Unidades
                        grupos.append(grupo_letras)
                
                numero //= 1000
                grupo_idx += 1
            
            return " ".join(reversed(grupos))
        
        # Convertir parte entera
        if parte_entera == 0:
            letras_enteras = "CERO"
        else:
            letras_enteras = numero_completo_a_letras(parte_entera)
        
        # Formato final con centavos
        centavos_str = f"{centavos:02d}"  # Asegurar 2 dígitos
        resultado = f"{letras_enteras} PESOS {centavos_str}/100 MN"
        
        return resultado
        
    except (ValueError, TypeError, Exception) as e:
        # En caso de error, devolver formato por defecto
        return f"ERROR EN CONVERSIÓN: {str(numero)} PESOS 00/100 MN"


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
        departamento = self.factura.get('departamento', '')  # Agregar departamento
        
        # Crear concepto: "Factura + número folio"
        concepto = f"Factura {folio_factura}" if folio_factura else "Factura"
        
        # Inicializar valores por defecto
        importe_letras = ""
        cuenta_banco = ""
        banco_cuenta_mayor = ""  # Variable para cuenta_mayor del banco
        proveedor_cuenta_mayor = ""  # Variable para cuenta_mayor del proveedor
        codigo_proveedor = ""  # Variable para codigo_quiter del proveedor
        codigo_banco = ""  # Variable para código del banco
        nombre_proveedor = ""  # Variable para nombre del proveedor
        nombre_banco = ""  # Variable para nombre del banco
        
        try:
            # Obtener datos de la orden de compra si existe
            if folio_interno and OrdenCompra:
                orden_compra = OrdenCompra.select().where(
                    OrdenCompra.factura == folio_interno
                ).first()
                
                if orden_compra:
                    importe_letras = orden_compra.importe_en_letras or ""
            
            # Si no hay importe en letras en la BD, generarlo automáticamente
            if not importe_letras and total_factura:
                importe_letras = self.convertir_numero_a_letras(total_factura)
            
            # Obtener cuenta_mayor y codigo_quiter del proveedor usando el RFC emisor
            if Proveedor and self.factura.get('rfc_emisor'):
                rfc_emisor = self.factura.get('rfc_emisor')
                
                proveedor_obj = Proveedor.select().where(
                    Proveedor.rfc == rfc_emisor
                ).first()
                
                if proveedor_obj:
                    if proveedor_obj.cuenta_mayor:
                        proveedor_cuenta_mayor = proveedor_obj.cuenta_mayor
                    if proveedor_obj.codigo_quiter:
                        codigo_proveedor = proveedor_obj.codigo_quiter
                    if proveedor_obj.nombre:
                        nombre_proveedor = proveedor_obj.nombre
            
            # Obtener datos del banco BTC23
            if Banco:
                banco_btc23 = Banco.select().where(
                    Banco.codigo == "BTC23"
                ).first()
                
                if banco_btc23:
                    cuenta_banco = banco_btc23.cuenta or ""
                    banco_cuenta_mayor = banco_btc23.cuenta_mayor or ""  # Obtener cuenta_mayor del banco
                    codigo_banco = banco_btc23.codigo or ""  # Obtener código del banco
                    nombre_banco = banco_btc23.nombre or ""  # Obtener nombre del banco
                    
        except Exception as e:
            print(f"Error accediendo a la base de datos: {e}")
            # Si hay error, generar importe en letras automáticamente
            if total_factura:
                importe_letras = self.convertir_numero_a_letras(total_factura)

        # Construir string de cuentas mayores con todas las cuentas necesarias
        cuentas_lista = []
        
        # Usar únicamente cuenta_mayor del proveedor (no de la factura)
        if proveedor_cuenta_mayor:
            cuentas_lista.append(str(proveedor_cuenta_mayor))
        
        # Agregar cuenta de banco si existe
        if banco_cuenta_mayor:
            cuentas_lista.append(str(banco_cuenta_mayor))
        
        # Agregar cuentas IVA desde configuración
        if AppConfig:
            iva_deber = AppConfig.CUENTAS_MAYORES.get('Iva_Deber', '')
            iva_haber = AppConfig.CUENTAS_MAYORES.get('Iva_Haber', '')
            
            if iva_deber:
                cuentas_lista.append(str(iva_deber))
            if iva_haber:
                cuentas_lista.append(str(iva_haber))
        
        # Construir string de subcuentas con códigos correspondientes
        subcuentas_lista = []
        
        # Subcuenta del proveedor: usar codigo_quiter del proveedor
        if proveedor_cuenta_mayor and codigo_proveedor:
            subcuentas_lista.append(str(codigo_proveedor))
        elif proveedor_cuenta_mayor:
            subcuentas_lista.append("")  # Placeholder si no hay código
        
        # Subcuenta del banco: usar código del banco
        if banco_cuenta_mayor and codigo_banco:
            subcuentas_lista.append(str(codigo_banco))
        elif banco_cuenta_mayor:
            subcuentas_lista.append("")  # Placeholder si no hay código
        
        # Subcuentas IVA: usar codigo_quiter del proveedor también
        if AppConfig:
            iva_deber = AppConfig.CUENTAS_MAYORES.get('Iva_Deber', '')
            iva_haber = AppConfig.CUENTAS_MAYORES.get('Iva_Haber', '')
            
            if iva_deber:
                subcuentas_lista.append(str(codigo_proveedor) if codigo_proveedor else "")
            if iva_haber:
                subcuentas_lista.append(str(codigo_proveedor) if codigo_proveedor else "")
        
        # Procesar cuentas: tomar primeros 4 dígitos y agregar 5 ceros
        cuentas_procesadas = []
        for cuenta in cuentas_lista:
            if len(cuenta) >= 4:
                primeros_4_digitos = cuenta[:4]  # Tomar primeros 4 dígitos
                cuenta_procesada = primeros_4_digitos + "00000"  # Agregar 5 ceros
                cuentas_procesadas.append(cuenta_procesada)
            else:
                # Si tiene menos de 4 dígitos, agregar ceros al inicio hasta tener 4, luego agregar 5 ceros
                cuenta_con_ceros = cuenta.zfill(4) + "00000"
                cuentas_procesadas.append(cuenta_con_ceros)
        
        # Procesar subcuentas: mantener valores originales sin transformaciones y limitar a 3
        subcuentas_procesadas = []
        for subcuenta in subcuentas_lista[:3]:  # Limitar a solo 3 subcuentas
            if subcuenta:
                subcuentas_procesadas.append(str(subcuenta))
            else:
                # Si no hay subcuenta, agregar string vacío
                subcuentas_procesadas.append("")
        
        # Unir todas las cuentas y subcuentas con saltos de línea (sin saltos al inicio)
        cuentas_mayores = "\n\n\n".join(cuentas_procesadas)
        subcuentas_mayores = "\n\n\n".join(subcuentas_procesadas)
        
        # Construir campo Nombre con nombres correspondientes
        nombres_lista = []
        
        # Nombre del proveedor
        if proveedor_cuenta_mayor and nombre_proveedor:
            nombres_lista.append(nombre_proveedor)
        elif proveedor_cuenta_mayor:
            nombres_lista.append("")  # Placeholder si no hay nombre
        
        # Nombre del banco
        if banco_cuenta_mayor and nombre_banco:
            nombres_lista.append(nombre_banco)
        elif banco_cuenta_mayor:
            nombres_lista.append("")  # Placeholder si no hay nombre
        
        # Nombres para cuentas IVA
        if AppConfig:
            iva_deber = AppConfig.CUENTAS_MAYORES.get('Iva_Deber', '')
            iva_haber = AppConfig.CUENTAS_MAYORES.get('Iva_Haber', '')
            
            if iva_deber:
                # Para IVA Deber: nombre_proveedor + "IVA ACREDITABLE"
                nombre_iva_deber = f"{nombre_proveedor}\nIVA ACREDITABLE" if nombre_proveedor else "IVA ACREDITABLE"
                nombres_lista.append(nombre_iva_deber)
            if iva_haber:
                # Para IVA Haber: "IVA PAGADO"
                nombres_lista.append("IVA PAGADO")
        
        # No limitar los nombres, incluir todos (especialmente la línea 4 con "IVA PAGADO")
        nombres_mayores = "\n\n\n".join(nombres_lista)
        
        return {
            "Fecha1_af_date": fecha_actual,
            "Orden": proveedor,
            "Moneda": importe_letras,
            "cuenta": cuenta_banco,
            "cheque": str(numero_vale),
            "Concepto": concepto,
            "area": departamento,  # Campo departamento
            "Costos": tipo_vale,
            "subcuenta": subcuentas_mayores,  # Campo subcuentas con códigos
            "Debe": "",
            "Haber": "",
            "Cuenta": cuentas_mayores,
            "Nombre": nombres_mayores,  # Campo nombres con proveedores, banco e IVA
            "Parcial": "",
            "Cantidad": str(total_factura)
        }
    
    def convertir_numero_a_letras(self, numero):
        """
        Método de conveniencia para convertir número a letras usando la función global
        
        Args:
            numero: Número a convertir
            
        Returns:
            str: Número convertido a letras con formato x/100
        """
        return numero_a_letras(numero)
    
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