import pdfplumber
import re
from typing import Dict, Optional
import os

class PDFDataExtractor:
    """
    Extractor de datos específicos de documentos PDF tipo vale/documento corporativo.
    """
    
    def __init__(self):
        # Patrones de expresiones regulares mejorados para encontrar los datos
        self.patterns = {
            'nombre': [
                # Patrones para PyPDF2 (preserva espacios)
                r'Proveedor:\s*([A-Z\s]+?)(?=\s*(?:\d|\n|$))',
                r'([A-Z\s]+)\s*Nombre:',  # PyPDF2 a veces invierte el orden
                # Patrones originales para pdfplumber
                r'Nombre:\s*([A-Z]+(?:[A-Z\s]*[A-Z])*)',
                r'NOMBRE:\s*([A-Z]+(?:[A-Z\s]*[A-Z])*)',
                r'Nombre:\s*([A-Z]{2,}(?:[A-Z]*[A-Z])*)',
                # Fallback patterns
                r'([A-Z][A-Z\s&]+(?:SA|S\.A\.|DE|CV|S\.C\.|LTDA|INC|CORP)[A-Z\s]*)',
                r'Nombre[:\s]*([A-Za-z\s.&]+?)(?=\n|$|\s{3,})'
            ],
            'numero': [
                # Funciona bien: V152885
                r'Número:\s*(V\d+)',
                r'(V\d{6})',
                r'Número[:\s]*([0-9A-Za-z-]+?)(?=\n|$|\s{3,})',
                r'\b(V\d+)\b'
            ],
            'referencia': [
                # Basado en: "Número: V152885 Referencia: 8158095"
                r'Referencia:\s*(\d+)',
                r'REFERENCIA:\s*(\d+)',
                # Patrón específico para capturar después de "Referencia:"
                r'Número:\s*V\d+\s+Referencia:\s*(\d+)',
                # Patrón más general para referencias numéricas
                r'(?i)referencia[:\s]*(\d+)',
                # Fallback para números largos después de "Referencia"
                r'Referencia[:\s]*([0-9]+)'
            ],
            'fecha': [
                # Funciona bien: 23/07/2025
                r'Fecha:\s*(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{1,2}-\d{1,2}-\d{4})',
                r'Fecha[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})(?=\n|$|\s{3,})'
            ],
            'cuenta': [
                # Funciona bien: 60309
                r'Cuenta:\s*(\d+)',
                r'CUENTA:\s*(\d+)',
                r'(?i)cuenta[:\s]*(\d+)',
                r'\b(\d{5})\b'
            ],
            'departamento': [
                # Basado en el texto: "Departamento: 6ADMINISTRACION"
                r'Departamento:\s*(\d+[A-Z]+)',
                r'DEPARTAMENTO:\s*(\d+[A-Z]+)',
                # Patrón específico para capturar "6ADMINISTRACION" 
                r'Departamento:\s*(\d+[A-Z][A-Z]*)',
                r'(\d+\s*[A-Z]{3,})',
                # Fallback
                r'Departamento[:\s]*([0-9A-Za-z\s]+?)(?=\n|$|\s{3,})'
            ],
            'sucursal': [
                # Basado en el texto: "Sucursal: 15NISSANMATEHUALA"
                r'Sucursal:\s*(\d+[A-Z]+(?:[A-Z]*[A-Z])*)',
                r'SUCURSAL:\s*(\d+[A-Z]+(?:[A-Z]*[A-Z])*)',
                # Patrón específico para capturar "15NISSANMATEHUALA"
                r'Sucursal:\s*(\d+[A-Z][A-Z]*)',
                r'(\d{1,2}[A-Z]{3,}[A-Z]*)',
                # Fallback
                r'Sucursal[:\s]*([0-9A-Za-z\s]+?)(?=\n|$|\s{3,})'
            ],
            'marca': [
                # Basado en el texto: "Marca: 2-NISSAN"
                r'Marca:\s*(\d+-[A-Z]+)',
                r'MARCA:\s*(\d+-[A-Z]+)',
                # Patrón específico para capturar "2-NISSAN"
                r'Marca:\s*(\d+\-[A-Z][A-Z]*)',
                r'(\d+\s*-\s*[A-Z]+)',
                # Fallback
                r'Marca[:\s]*([0-9A-Za-z\s-]+?)(?=\n|$|\s{3,})'
            ],
            'responsable': [
                # Funciona bien: 294379
                r'Responsable:\s*(\d+)',
                r'RESPONSABLE:\s*(\d+)',
                r'Responsable[:\s]*(\d+)',
                r'\b(\d{6})\b'
            ],
            'tipo_de_vale': [
                # Basado en el texto: "TipodeVale: CECOMPRADEEQUIPOCOMPUTOYOFICINA"
                r'TipodeVale:\s*([A-Z]+)',
                r'TIPODEVALE:\s*([A-Z]+)',
                r'Tipo\s*de\s*Vale:\s*([A-Z\s]+)',
                r'TipodeVale:\s*([A-Z][A-Z]*)',
                # Fallback
                r'Tipo de Vale[:\s]*([A-Za-z\s]+?)(?=\n|$|\s{3,})'
            ],
            'no_documento': [
                # Basado en el texto: "NºDocumento: 6976073-1"
                r'NºDocumento:\s*([0-9-]+)',
                r'N[ºo]Documento:\s*([0-9A-Za-z-]+)',
                r'No\s*Documento:\s*([0-9A-Za-z-]+)',
                r'NºDocumento:\s*([0-9A-Za-z-]+)',
                # Fallback
                r'No Documento[:\s]*([0-9A-Za-z-]+?)(?=\n|$|\s{3,})'
            ],
            'total': [
                # Funciona bien: 3,132.77
                r'ValorVale:\s*([0-9,]+\.[0-9]{2})',
                r'TOTAL[:\s]*\$?\s*([0-9,]+\.?[0-9]*)',
                r'Total[:\s]*\$?\s*([0-9,]+\.?[0-9]*)',
                r'([0-9]{1,3}(?:,[0-9]{3})*\.[0-9]{2})',
                r'\$?\s*([0-9,]+\.[0-9]{2})(?=\s|$)'
            ],
            'descripcion': [
                # Patrones para PyPDF2 (preserva espacios) - Múltiples líneas
                r'Descripción:\s*\n([A-Z\s,()]+(?:\n[A-Z\s,()]+)*?)(?=\n\d|\n[A-Z]+:|$)',
                r'Descripción:\s*([A-Z\s,()]+(?:\n[A-Z\s,()]+)*?)(?=\n\d|\nTOTAL:)',
                # Patrón específico para descripciones largas en PyPDF2
                r'Descripción:\s*\n([A-Z\s,()]+)\n([A-Z\s,()]+)',
                # Patrones específicos para texto PyPDF2
                r'(MARKETING\s+[A-Z\s,()]+(?:\n[A-Z\s,()]+)*)',
                r'(IMPRESORA\s+[A-Z\s,]+)',
                r'(HERRAMIENTAS\s+[A-Z\s]+)',
                # Patrones originales para pdfplumber
                r'Descripción:\s*.*?\n(?:.*?\n)*(IMPRESORA[A-Z0-9,]+)\s+MATEHUALA',
                r'Descripción:\s*.*?\n(?:.*?\n)*(HERRAMIENTASDETRABAJO|HERRAMIENTAS\s*DE\s*TRABAJO)',
                r'Descripción:\s*.*?\n(?:.*?\n)*([A-Z][A-Z0-9,\s]+?)\s+MATEHUALA',
                r'Descripción:\s*.*?\n(?:.*?\n)*([A-Z]*HERRAMIENTAS[A-Z]*)',
                r'Descripción:\s*.*?\n(?:.*?\n)*([A-Z]+(?:DE)?[A-Z]+)\s+[A-Z]+',
                r'Descripción:\s*\n(?:\s*\n)*(?:[0-9-]+\s+[A-Z]+\s+[0-9%.\s]+\n)*([A-Z]+(?:DE)?[A-Z]+)',
                r'(?:DESCRIPCI[ÓO]N|D\s*E\s*S\s*C\s*R\s*I\s*P\s*C\s*I\s*[ÓO]\s*N).*?\n\s*([A-Z\s]+(?:\s+DE\s+)?[A-Z\s]*)\n',
                r'(?:DESCRIPCI[ÓO]N|D\s*E\s*S\s*C\s*R\s*I\s*P\s*C\s*I\s*[ÓO]\s*N).*?\n\s*([A-Z][A-Z\s]+)',
                r'[0-9.,]+\s*([A-Z]{3,})\s+[0-9]+\.?[0-9]*',
                r'[0-9.,]+\s*(MAGNA|PREMIUM|DIESEL|GASOLINA)\s+',
                r'Descripción:\s*(.+?)(?=\n[A-Z][a-z]*:|$)',
                r'DESCRIPCIÓN:\s*(.+?)(?=\n[A-Z][a-z]*:|$)',
                r'Descripcion:\s*(.+?)(?=\n[A-Z][a-z]*:|$)',
                r'DESCRIPCION:\s*(.+?)(?=\n[A-Z][a-z]*:|$)',
                r'Descripci[óo]n[:\s]*(.+?)(?=\n|$)'
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
            else:
                # Si no coincide con patrones conocidos, busca abreviatura de 1-3 caracteres
                # seguida de una palabra completa en mayúsculas
                match = re.search(r'^([A-Z]{1,3})(?=[A-Z]{4,})', value)
                if match:
                    value = match.group(1)
                else:
                    # Último recurso: toma los primeros 2 caracteres si todo está en mayúsculas
                    if value.isupper() and len(value) > 2:
                        value = value[:2]
        
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
                
                # Buscar en el texto de PyPDF2
                for pattern in self.patterns[field_name]:
                    match = re.search(pattern, pypdf2_text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
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
        
        # Intenta cada patrón para el campo
        for pattern in self.patterns[field_name]:
            match = re.search(pattern, current_text, re.IGNORECASE | re.MULTILINE)
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
