import pdfplumber
import re
from typing import Dict, Optional
import os

class PDFDataExtractor:
    """
    Extractor de datos específicos de documentos PDF tipo vale/documento corporativo.
    """
    
    def __init__(self):
        # Patrones de expresiones regulares SIMPLIFICADOS para mejor rendimiento
        self.patterns = {
            'nombre': [
                # Patrón específico para PyPDF2 que evita "Tipo deVale"
                r'Proveedor:\s*([A-Z][A-Z\s]+?)(?:\s*Tipo\s*de|$)',
                r'Nombre:\s*([A-Z][A-Z\s]+?)(?:\s*Domicilio|\s*Tipo|\s*$)',
                r'NOMBRE:\s*([A-Z][A-Z\s]+?)(?:\s*DOMICILIO|\s*TIPO|\s*$)',
                # Fallback para nombres con terminaciones corporativas
                r'([A-Z][A-Z\s&]+(?:SA|S\.A\.|DE\s*CV|SADECV))\b',
            ],
            'numero': [
                # Patrones simples para números de vale
                r'Número:\s*(V\d+)',
                r'(V\d{6})',
                r'\b(V\d+)\b'
            ],
            'referencia': [
                # Patrones simples para referencia
                r'Referencia:\s*(\d+)',
                r'REFERENCIA:\s*(\d+)',
                r'referencia[:\s]*(\d+)'
            ],
            'fecha': [
                # Patrones simples para fechas
                r'Fecha:\s*(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{1,2}-\d{1,2}-\d{4})'
            ],
            'cuenta': [
                # Patrones simples para cuenta
                r'Cuenta:\s*(\d+)',
                r'CUENTA:\s*(\d+)',
                r'\b(\d{5})\b'
            ],
            'departamento': [
                # Patrones simples para departamento
                r'Departamento:\s*(\d+[A-Z]+)',
                r'DEPARTAMENTO:\s*(\d+[A-Z]+)',
                r'(\d+[A-Z]{3,})'
            ],
            'sucursal': [
                # Patrones simples para sucursal
                r'Sucursal:\s*(\d+[A-Z]+)',
                r'SUCURSAL:\s*(\d+[A-Z]+)',
                r'(\d{1,2}[A-Z]{3,})'
            ],
            'marca': [
                # Patrones simples para marca
                r'Marca:\s*(\d+-[A-Z]+)',
                r'MARCA:\s*(\d+-[A-Z]+)',
                r'(\d+\s*-\s*[A-Z]+)'
            ],
            'responsable': [
                # Patrones simples para responsable
                r'Responsable:\s*(\d+)',
                r'RESPONSABLE:\s*(\d+)',
                r'\b(\d{6})\b'
            ],
            'tipo_de_vale': [
                # Patrones simples para tipo de vale
                r'TipodeVale:\s*([A-Z]+)',
                r'TIPODEVALE:\s*([A-Z]+)',
                r'Tipo\s*de\s*Vale:\s*([A-Z\s]+)'
            ],
            'no_documento': [
                # Patrones simples para no documento
                r'NºDocumento:\s*([0-9-]+)',
                r'N[ºo]Documento:\s*([0-9A-Za-z-]+)',
                r'No\s*Documento:\s*([0-9A-Za-z-]+)'
            ],
            'total': [
                # Patrones simples para total
                r'ValorVale:\s*([0-9,]+\.[0-9]{2})',
                r'TOTAL[:\s]*\$?\s*([0-9,]+\.?[0-9]*)',
                r'Total[:\s]*\$?\s*([0-9,]+\.?[0-9]*)',
                r'([0-9]{1,3}(?:,[0-9]{3})*\.[0-9]{2})'
            ],
            'descripcion': [
                # Patrones SIMPLIFICADOS para descripción
                r'Descripción:\s*([A-Z\s,()]+)',
                r'DESCRIPCIÓN:\s*([A-Z\s,()]+)',
                r'Descripcion:\s*([A-Z\s,()]+)',
                r'DESCRIPCION:\s*([A-Z\s,()]+)',
                # Patrones específicos comunes
                r'(MARKETING\s+[A-Z\s,()]+)',
                r'(IMPRESORA\s+[A-Z\s,]+)',
                r'(HERRAMIENTAS\s+[A-Z\s]+)',
                r'([A-Z]{3,}\s+[A-Z\s]+)',
                r'(MAGNA|PREMIUM|DIESEL|GASOLINA)',
            ]
        }
    
    def debug_text_extraction(self, pdf_path: str) -> str:
        """
        Función de depuración para ver el texto extraído del PDF.
        """
        text = self.extract_text_from_pdf(pdf_path)
        print("\n" + "="*60)
        print("TEXTO EXTRAÍDO DEL PDF (PARA DEPURACIÓN)")
        print("="*60)
        print(text[:1000] + "..." if len(text) > 1000 else text)
        print("="*60)
        return text
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extrae todo el texto de un archivo PDF.
        Usa pdfplumber que funciona mejor con los patrones existentes.
        """
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error al leer el PDF: {e}")
            return ""
        
        return text
    
    def extract_text_from_pdf_with_spaces(self, pdf_path: str) -> str:
        """
        Extrae texto usando PyPDF2 para preservar espacios originales.
        Usado para campos específicos donde los espacios son importantes.
        """
        text = ""
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error al leer el PDF con PyPDF2: {e}")
            return ""
        
        return text
    
    def post_process_field(self, field_name: str, value: str) -> str:
        """
        Post-procesa un campo extraído para limpiarlo y formatearlo correctamente.
        """
        if not value:
            return value
        
        # Limpia espacios excesivos
        value = re.sub(r'\s+', ' ', value).strip()
        
        # Post-procesamiento específico por campo
        if field_name == 'nombre':
            # Mantener el nombre tal como viene del PDF, sin agregar espacios artificiales
            # Solo remover texto irrelevante como "Domicilio"
            value = re.sub(r'\s+(Domicilio|DOMICILIO).*$', '', value)
            # NO agregamos espacios automáticamente - el nombre se mantiene como viene del PDF
            # La comparación sin espacios se hará en provider_matcher.py si es necesario
            
        elif field_name == 'descripcion':
            # Mantener la descripción tal como viene del PDF
            # NO agregar espacios automáticamente - preservar el texto original
            pass
            
        elif field_name == 'departamento':
            # Agrega espacio entre número y texto: "6ADMINISTRACION" -> "6 ADMINISTRACION"
            value = re.sub(r'(\d+)([A-Z])', r'\1 \2', value)
            
        elif field_name == 'sucursal':
            # Agrega espacios: "15NISSANMATEHUALA" -> "15 NISSAN MATEHUALA"
            value = re.sub(r'(\d+)([A-Z])', r'\1 \2', value)
            value = re.sub(r'NISSAN([A-Z])', r'NISSAN \1', value)
            
        elif field_name == 'marca':
            # Agrega espacio después del guión: "2-NISSAN" -> "2 - NISSAN"
            value = re.sub(r'(\d+)-([A-Z])', r'\1 - \2', value)
            
        elif field_name == 'tipo_de_vale':
            # Extrae solo la abreviatura del tipo de vale
            # Busca patrones comunes de abreviaturas seguidas de palabras completas
            
            # Primero intenta encontrar patrones específicos conocidos
            if value.startswith('CECOMPRA'):
                value = 'CE'
            elif value.startswith('GAVALE') or value.startswith('GA'):
                value = 'GA'  # Gasolina
            elif value.startswith('AVALE') or value.startswith('AL'):
                value = 'AL'  # Alimentación
            elif value.startswith('VTRANSPORTE') or value.startswith('VT'):
                value = 'VT'  # Vales de transporte
            elif value.startswith('CICONSUMIBLES') or value.startswith('CI'):
                value = 'CI'  # Consumibles
            elif value.startswith('SETSERVICIO') or value.startswith('SET'):
                value = 'SET'  # Servicios externos
            else:
                # Si no coincide con patrones conocidos, busca abreviatura simple
                # Buscar abreviaturas de 1-3 caracteres seguidas de palabras
                # Patrón para detectar abreviatura seguida de palabra completa
                match = re.match(r'^([A-Z]{1,3})(?:[A-Z][a-z]|[A-Z]{4,})', value)
                if match:
                    value = match.group(1)
                elif len(value) >= 3 and value[:2].isupper():
                    # Si los primeros 2 caracteres son mayúsculas, usar esos
                    value = value[:2]
                elif len(value) >= 2 and value[:1].isupper():
                    # Si solo el primer carácter es mayúscula, usar solo ese
                    value = value[:1]
                else:
                    # Último recurso: toma hasta 3 caracteres si todo está en mayúsculas
                    if value.isupper() and len(value) > 3:
                        value = value[:3]
        
        return value

    def extract_field(self, text_or_path: str, field_name: str) -> Optional[str]:
        """
        Extrae un campo específico del texto usando los patrones definidos.
        Para ciertos campos usa PyPDF2 para preservar espacios.
        """
        if field_name not in self.patterns:
            return None
        
        # Determinar si es una ruta de archivo o texto
        is_file_path = os.path.isfile(text_or_path) if os.path.exists(text_or_path) else False
        
        # Para campos donde los espacios son importantes, usar PyPDF2
        if field_name in ['nombre', 'descripcion'] and is_file_path:
            # Intentar primero con texto de PyPDF2
            pypdf2_text = self.extract_text_from_pdf_with_spaces(text_or_path)
            if pypdf2_text:
                # Tratamiento especial para descripción que puede ser multilínea
                if field_name == 'descripcion':
                    result = self.extract_multiline_description(pypdf2_text)
                    if result:
                        return self.post_process_field(field_name, result)
                
                # Buscar en el texto de PyPDF2 (SIMPLIFICADO)
                for pattern in self.patterns[field_name]:
                    match = re.search(pattern, pypdf2_text, re.IGNORECASE)
                    if match:
                        result = match.group(1).strip()
                        result = re.sub(r'\s+', ' ', result)
                        result = self.post_process_field(field_name, result)
                        return result
        
        # Usar el texto normal de pdfplumber para otros campos o como fallback
        if is_file_path:
            current_text = self.extract_text_from_pdf(text_or_path)
        else:
            current_text = text_or_path
        
        # Intenta cada patrón para el campo (SIMPLIFICADO)
        for pattern in self.patterns[field_name]:
            match = re.search(pattern, current_text, re.IGNORECASE)
            if match:
                # Limpia el resultado
                result = match.group(1).strip()
                # Remueve espacios excesivos
                result = re.sub(r'\s+', ' ', result)
                # Aplica post-procesamiento específico
                result = self.post_process_field(field_name, result)
                return result
        
        return None
    
    def extract_all_data(self, pdf_path: str, debug: bool = False) -> Dict[str, Optional[str]]:
        """
        Extrae todos los campos especificados del PDF.
        """
        # Verifica si el archivo existe
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"El archivo {pdf_path} no existe")
        
        # Extrae el texto del PDF
        if debug:
            text = self.debug_text_extraction(pdf_path)
        else:
            text = self.extract_text_from_pdf(pdf_path)
        
        if not text:
            print("No se pudo extraer texto del PDF")
            return {}
        
        # Diccionario para almacenar los resultados
        data = {}
        
        # Lista de campos a extraer
        fields = [
            'nombre', 'numero', 'referencia', 'fecha', 'cuenta', 'departamento', 
            'sucursal', 'marca', 'responsable', 'tipo_de_vale', 
            'no_documento', 'total', 'descripcion'
        ]
        
        # Extrae cada campo
        for field in fields:
            # Para campos que necesitan PyPDF2, pasar la ruta del archivo
            if field in ['nombre', 'descripcion']:
                extracted_value = self.extract_field(pdf_path, field)
            else:
                # Para otros campos, usar el texto ya extraído
                extracted_value = self.extract_field(text, field)
            
            field_name = field.replace('_', ' ').title()
            data[field_name] = extracted_value
            
            # Modo debug: muestra qué se encontró para cada campo
            if debug:
                print(f"Campo '{field_name}': {extracted_value if extracted_value else '[No encontrado]'}")
        
        return data
    
    def print_extracted_data(self, data: Dict[str, Optional[str]]):
        """
        Imprime los datos extraídos de forma organizada.
        """
        print("\n" + "="*50)
        print("DATOS EXTRAÍDOS DEL DOCUMENTO")
        print("="*50)
        
        for key, value in data.items():
            if value:
                print(f"{key:15}: {value}")
            else:
                print(f"{key:15}: [No encontrado]")
        
        print("="*50)
    
    def extract_multiline_description(self, text: str) -> Optional[str]:
        """
        Extrae descripción que puede estar en múltiples líneas usando PyPDF2.
        """
        lines = text.split('\n')
        
        # Encontrar la línea que contiene "Descripción:"
        for i, line in enumerate(lines):
            if 'Descripción:' in line:
                # Buscar las líneas siguientes que contienen la descripción
                description_lines = []
                j = i + 1
                
                while j < len(lines):
                    current_line = lines[j].strip()
                    
                    # Si la línea contiene palabras de descripción, incluirla
                    if (current_line and 
                        any(keyword in current_line.upper() for keyword in 
                            ['MARKETING', 'EXPERIENCIA', 'EMBAJADORES', 'AMENIDADES', 
                             'CONTRATO', 'IMPRESORA', 'HERRAMIENTAS', 'MAGNA', 'DIESEL',
                             'PREMIUM', 'GASOLINA']) and
                        not current_line.startswith('TOTAL:') and
                        not re.match(r'^\d+', current_line)):
                        
                        description_lines.append(current_line)
                        j += 1
                    else:
                        break
                
                if description_lines:
                    # Unir las líneas
                    full_description = ' '.join(description_lines)
                    # Correcciones específicas para casos conocidos
                    full_description = full_description.replace('DEEXPERIENCIA', 'DE EXPERIENCIA')
                    full_description = full_description.replace('DEACUERDO', 'DE ACUERDO') 
                    full_description = full_description.replace('ACONTRATO', 'A CONTRATO')
                    # Normalizar espacios múltiples sin agregar espacios innecesarios
                    full_description = re.sub(r'\s+', ' ', full_description)
                    return full_description.strip()
        
        return None

def main():
    """
    Función principal para demostrar el uso del extractor.
    """
    extractor = PDFDataExtractor()
    
    # Solicita la ruta del archivo PDF
    pdf_path = input("Ingresa la ruta completa del archivo PDF: ").strip()
    
    # Remueve comillas si las hay
    pdf_path = pdf_path.strip('"\'')
    
    try:
        # Extrae los datos
        data = extractor.extract_all_data(pdf_path)
        
        # Muestra los resultados
        extractor.print_extracted_data(data)
        
        # También devuelve el diccionario para uso programático
        return data
        
    except Exception as e:
        print(f"Error: {e}")
        return {}

if __name__ == "__main__":
    main()
