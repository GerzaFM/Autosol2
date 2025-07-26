"""
Extractor de datos para Órdenes (PDFs QRSOPMX208).
Extrae: Ref. Movimiento, Cuenta, Nombre, Importe, Importe en letras, y Código del banco.
"""

import PyPDF2
import pdfplumber
import re
from pathlib import Path

class OrdenDataExtractor:
    def __init__(self):
        """
        Inicializa el extractor de órdenes con los patrones de búsqueda.
        """
        # Patrones regex para extraer los datos de las órdenes
        self.patterns = {
            'Ref_Movimiento': [
                r'Ref\.Movimiento:\s*(\d+)',
                r'Referencia\s*Movimiento:\s*(\d+)',
                r'Ref\s*Movimiento\s*(\d+)',
                r'(?:Ref\.?\s*)?(?:de\s*)?Movimiento\s*:?\s*(\d+)',
            ],
            'Cuenta': [
                r'Cuenta:\s*(\d+)',
                r'Cta\.\s*(\d+)',
                r'Número\s*de\s*Cuenta\s*(\d+)',
                r'Cuenta\s*:?\s*(\d{4,6})',
            ],
            'Nombre': [
                r'Nombre:\s*([A-ZÁÉÍÓÚÜÑ]+(?:[A-ZÁÉÍÓÚÜÑ\s]*(?:S\.?A\.?(?:\s*DE\s*C\.?V\.?)?|S\.?C\.?|A\.?C\.?|S\.?R\.?L\.?))?)',
                r'Tercero:\s*Cuenta:\s*\d+\s*Nombre:\s*([A-ZÁÉÍÓÚÜÑ]+(?:[A-ZÁÉÍÓÚÜÑ\s]*(?:S\.?A\.?(?:\s*DE\s*C\.?V\.?)?|S\.?C\.?|A\.?C\.?|S\.?R\.?L\.?))?)',
                r'NOMBRECLIENTE.*?(\d+)\s+([A-ZÁÉÍÓÚÜÑ]+(?:[A-ZÁÉÍÓÚÜÑ\s]*(?:S\.?A\.?(?:\s*DE\s*C\.?V\.?)?|S\.?C\.?|A\.?C\.?|S\.?R\.?L\.?))?)',
            ],
            'Importe': [
                r'Importe:\s*([\d,]+\.?\d*)',
                r'Importe\s*\$?\s*([\d,]+\.?\d*)',
                r'(\d+,\d+\.\d+)\s+0\.00',  # Patrón específico de la tabla DEBE
                r'Monto\s*\$?\s*([\d,]+\.?\d*)',
            ],
            'Importe_en_letras': [
                r'Importeenletras:\s*([A-ZÁÉÍÓÚÜÑ\s]+(?:PESOS?|MN)[\d/\s]*(?:MN)?)',
                r'Importe\s*en\s*letras:\s*([A-ZÁÉÍÓÚÜÑ\s]+(?:PESOS?|MN)[\d/\s]*(?:MN)?)',
                r'Son\s*([A-ZÁÉÍÓÚÜÑ\s]+(?:PESOS?|MN)[\d/\s]*(?:MN)?)',
            ],
            'Codigo_Banco': [
                r'([A-Z]{2,4}\d{1,3})',  # Patrón general para códigos como BTC23
                r'TRANSFERENCIA([A-Z]{2,4}\d{1,3})',  # En la tabla
                r'(\w+)\s+BAJIOMATEHUALA',  # BTC23 en la tabla
                r'12020000000\s+([A-Z]+\d+)',  # Patrón específico de la tabla
            ]
        }

    def extract_text_with_pdfplumber(self, pdf_path: str) -> str:
        """
        Extrae texto del PDF usando pdfplumber para mejor precisión.
        
        Args:
            pdf_path (str): Ruta del archivo PDF
            
        Returns:
            str: Texto extraído del PDF
        """
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            print(f"Error al extraer texto con pdfplumber: {e}")
            return ""

    def extract_text_with_pypdf2(self, pdf_path: str) -> str:
        """
        Extrae texto del PDF usando PyPDF2 como método alternativo.
        
        Args:
            pdf_path (str): Ruta del archivo PDF
            
        Returns:
            str: Texto extraído del PDF
        """
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            print(f"Error al extraer texto con PyPDF2: {e}")
            return ""

    def extract_field(self, text: str, field_name: str) -> str:
        """
        Extrae un campo específico del texto usando patrones regex.
        
        Args:
            text (str): Texto del PDF
            field_name (str): Nombre del campo a extraer
            
        Returns:
            str: Valor extraído o cadena vacía si no se encuentra
        """
        if field_name not in self.patterns:
            return ""
        
        for pattern in self.patterns[field_name]:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                return self.post_process_field(field_name, value)
        
        return ""

    def post_process_field(self, field_name: str, value: str) -> str:
        """
        Post-procesa el valor extraído para limpieza y formato.
        
        Args:
            field_name (str): Nombre del campo
            value (str): Valor extraído
            
        Returns:
            str: Valor procesado
        """
        if not value:
            return ""
        
        # Limpieza general
        value = value.strip()
        
        # Post-procesamiento específico por campo
        if field_name == 'Nombre':
            # Limpiar nombres de empresas
            value = re.sub(r'\s+', ' ', value)  # Espacios múltiples
            value = value.upper()  # Convertir a mayúsculas
            
        elif field_name == 'Importe':
            # Limpiar formato de moneda
            value = re.sub(r'[,$]', '', value)  # Quitar comas y signos de peso
            value = value.replace(',', '')
            
        elif field_name == 'Importe_en_letras':
            # Limpiar importe en letras
            value = re.sub(r'\s+', ' ', value)  # Espacios múltiples
            value = value.upper()  # Convertir a mayúsculas
            
        elif field_name == 'Codigo_Banco':
            # Limpiar código de banco
            value = value.upper()  # Convertir a mayúsculas
            
        return value

    def extract_from_table(self, pdf_path: str) -> dict:
        """
        Extrae datos específicamente de las tablas del PDF.
        
        Args:
            pdf_path (str): Ruta del archivo PDF
            
        Returns:
            dict: Datos extraídos de las tablas
        """
        table_data = {}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    
                    for table in tables:
                        if not table:
                            continue
                            
                        # Buscar en la tabla principal de cuentas contables
                        for row in table:
                            if row and len(row) >= 4:
                                # Buscar la primera fila de datos (no el header)
                                # La estructura es: C.MAYOR, CTA., NOMBRECLIENTE, DEBE, HABER, TIPO, DESCRIPCION, EXPLICACION
                                if (row[0] and str(row[0]).isdigit() and 
                                    row[1] and str(row[1]).isdigit() and 
                                    row[2] and len(str(row[2])) > 5 and
                                    row[3] and re.match(r'[\d,]+\.\d+', str(row[3]))):
                                    
                                    # Tomar el nombre de la columna 2 (NOMBRECLIENTE)
                                    nombre_crudo = str(row[2]).strip()
                                    if not any(word in nombre_crudo.upper() for word in ['NOMBRECLIENTE', 'DEBE', 'HABER']):
                                        table_data['Nombre'] = nombre_crudo
                                    
                                    # Tomar el importe de la columna 3 (DEBE) - solo si no es 0.00
                                    importe = str(row[3]).strip()
                                    if importe != '0.00':
                                        table_data['Importe'] = importe
                                    
                                    # Solo tomar la primera fila válida
                                    break
                                
                                # Buscar código de banco - priorizar BTC23
                                if len(row) >= 2 and row[1]:
                                    banco_candidato = str(row[1]).strip()
                                    if banco_candidato.startswith('BTC'):
                                        table_data['Codigo_Banco'] = banco_candidato
                                    elif re.match(r'[A-Z]{2,4}\d{1,3}', banco_candidato) and 'Codigo_Banco' not in table_data:
                                        table_data['Codigo_Banco'] = banco_candidato
        
        except Exception as e:
            print(f"Error al extraer datos de tabla: {e}")
        
        return table_data

    def extract_all_data(self, pdf_path: str) -> dict:
        """
        Extrae todos los datos de la orden.
        
        Args:
            pdf_path (str): Ruta del archivo PDF
            
        Returns:
            dict: Diccionario con todos los datos extraídos
        """
        # Verificar que el archivo existe
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"El archivo {pdf_path} no existe")
        
        # Extraer texto usando ambos métodos
        text_pdfplumber = self.extract_text_with_pdfplumber(pdf_path)
        text_pypdf2 = self.extract_text_with_pypdf2(pdf_path)
        
        # Combinar textos para mayor cobertura
        combined_text = text_pdfplumber + "\n" + text_pypdf2
        
        # Extraer cada campo usando regex
        data = {}
        for field_name in self.patterns.keys():
            data[field_name] = self.extract_field(combined_text, field_name)
        
        # Extraer datos adicionales de las tablas
        table_data = self.extract_from_table(pdf_path)
        
        # Combinar datos de texto y tabla, dando prioridad a los datos de tabla cuando estén disponibles
        for key, value in table_data.items():
            if value and value.strip():  # Solo sobrescribir si el valor de la tabla no está vacío
                data[key] = value
        
        # Post-procesamiento específico para mejorar los datos
        self.improve_extracted_data(data, combined_text)
        
        # Agregar información adicional
        data['archivo_original'] = Path(pdf_path).name
        data['ruta_completa'] = pdf_path
        
        return data

    def improve_extracted_data(self, data: dict, text: str):
        """
        Mejora los datos extraídos con post-procesamiento específico.
        
        Args:
            data (dict): Datos extraídos
            text (str): Texto completo del PDF
        """
        # Extraer nombre directamente del texto estructurado (método principal)
        if not data.get('Nombre') or "FACTURA" in data.get('Nombre', '') or len(data.get('Nombre', '')) < 5:
            # Buscar el nombre después de "Nombre:" en la sección de tercero
            match = re.search(r'Nombre:\s*([A-ZÁÉÍÓÚÜÑ]+)', text)
            if match:
                nombre_crudo = match.group(1).strip()
                # Mantener el nombre tal como viene, sin forzar espacios
                data['Nombre'] = nombre_crudo
        
        # Extraer importe directamente del texto estructurado
        if not data.get('Importe') or data.get('Importe') == '0.00':
            # Buscar "Importe: X,XXX.XX"
            match = re.search(r'Importe:\s*([\d,]+\.\d+)', text)
            if match:
                data['Importe'] = match.group(1)
        
        # Extraer importe en letras del texto estructurado
        if not data.get('Importe_en_letras'):
            match = re.search(r'Importeenletras:\s*([A-ZÁÉÍÓÚÜÑ\d/\s]+MN)', text)
            if match:
                letras_crudo = match.group(1).strip()
                # Mantener el importe en letras tal como viene
                data['Importe_en_letras'] = letras_crudo
        
        # Verificar código de banco (priorizar BTC23 si está presente)
        if not data.get('Codigo_Banco'):
            # Buscar BTC23 específicamente primero
            if 'BTC23' in text:
                data['Codigo_Banco'] = 'BTC23'
            else:
                # Buscar cualquier otro código de banco
                match = re.search(r'([A-Z]{2,4}\d{1,3})', text)
                if match:
                    data['Codigo_Banco'] = match.group(1)
        elif data.get('Codigo_Banco') and 'BTC23' in text:
            # Si ya hay un código pero existe BTC23, priorizarlo
            data['Codigo_Banco'] = 'BTC23'
        
        return data

    def extract_and_display(self, pdf_path: str) -> dict:
        """
        Extrae datos y los muestra de forma organizada.
        
        Args:
            pdf_path (str): Ruta del archivo PDF
            
        Returns:
            dict: Diccionario con los datos extraídos
        """
        print(f"🔍 Extrayendo datos de la orden: {Path(pdf_path).name}")
        print("=" * 60)
        
        try:
            data = self.extract_all_data(pdf_path)
            
            # Mostrar resultados
            print("📋 DATOS EXTRAÍDOS DE LA ORDEN:")
            print("-" * 40)
            print(f"📄 Archivo: {data.get('archivo_original', 'N/A')}")
            print(f"🔢 Ref. Movimiento: {data.get('Ref_Movimiento', 'No encontrado')}")
            print(f"🏦 Cuenta: {data.get('Cuenta', 'No encontrada')}")
            print(f"🏢 Nombre: {data.get('Nombre', 'No encontrado')}")
            print(f"💰 Importe: {data.get('Importe', 'No encontrado')}")
            print(f"📝 Importe en letras: {data.get('Importe_en_letras', 'No encontrado')}")
            print(f"🏛️ Código del Banco: {data.get('Codigo_Banco', 'No encontrado')}")
            
            return data
            
        except Exception as e:
            print(f"❌ Error al procesar el archivo: {str(e)}")
            return {}

def main():
    """
    Función principal para probar el extractor.
    """
    extractor = OrdenDataExtractor()
    
    # Archivo de prueba
    archivo_prueba = r"c:\QuiterWeb\cache\15gerzahin.flores_QRSOPMX208_8178779.pdf"
    
    if Path(archivo_prueba).exists():
        print("🚀 EXTRACTOR DE DATOS DE ÓRDENES")
        print("=" * 50)
        
        # Extraer y mostrar datos
        datos = extractor.extract_and_display(archivo_prueba)
        
        # Mostrar el diccionario resultante
        if datos:
            print("\n" + "=" * 60)
            print("📊 DICCIONARIO RESULTANTE:")
            print("=" * 60)
            for clave, valor in datos.items():
                print(f"{clave}: {valor}")
        
    else:
        print(f"❌ El archivo de prueba no existe: {archivo_prueba}")
        print("💡 Puedes usar el extractor con cualquier archivo de orden:")
        print("extractor = OrdenDataExtractor()")
        print("datos = extractor.extract_all_data('ruta_a_tu_archivo.pdf')")

if __name__ == "__main__":
    main()
