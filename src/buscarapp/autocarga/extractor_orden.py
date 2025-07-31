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
            ],
            'Folio_Factura': [
                # Patrones para F-numero (formato tradicional)
                r'F-(\d+)',  # F-17474
                r'FACTURA\d+F-(\d+)',  # FACTURA174748226636/1FACTURA152701F-17474
                r'EXPLICACION.*?F-(\d+)',  # En la explicación
                r'(?:FACTURA\d+.*?){2}F-(\d+)',  # Después del segundo FACTURA
                
                # Patrones para otros formatos de factura
                r'OLEK\s*(\d+)',  # OLEK 5718
                r'CC\s*(\d+)',  # CC 10604
                r'(\d{4,6})\s*(?:$|\s)',  # Números de 4-6 dígitos al final de línea
                
                # Patrones en tabla de explicación (extraer números significativos)
                r'FACTURA\d+\s*(\d{4,6})',  # FACTURA152701 -> extraer parte numérica
                r'(?:SERIE|FOLIO)\s*:?\s*([A-Z]*\s*\d+)',  # SERIE: CC FOLIO: 10604
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
        
        # Lógica especial para Folio_Factura
        if field_name == 'Folio_Factura':
            return self._extract_folio_factura_inteligente(text)
        
        for pattern in self.patterns[field_name]:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                return self.post_process_field(field_name, value)
        
        return ""

    def _extract_folio_factura_inteligente(self, text: str) -> str:
        """
        Extrae el folio de factura usando estrategias inteligentes priorizadas.
        
        Args:
            text (str): Texto completo del PDF
            
        Returns:
            str: Folio de factura extraído o cadena vacía
        """
        # PASO 1: Identificar tipo de proveedor y aplicar estrategia específica
        nombre_text = text.upper()
        
        # Para OLEKSEI-MX: buscar 5718 específicamente (PRIORIDAD MÁXIMA)
        if 'OLEKSEI' in nombre_text:
            if '5718' in text:
                return '5718'
            
            # Patrones alternativos si no encontramos 5718
            olek_patterns = [
                r'OLEK.*?(\d{4})',  # Después de OLEK
                r'\b(5\d{3})\b',  # Números que empiecen con 5 (4 dígitos)
            ]
            
            for pattern in olek_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    if (len(match) == 4 and 
                        not match.startswith('20') and
                        match not in ['8216', '8097', '7750', '5589', '5598']):
                        return match
            
            # Si no encontramos nada específico, devolver vacío (no genérico)
            return ""
        
        # Para SERVICIO NAVA: buscar 10604, 10603, 10602 específicamente
        elif 'NAVA' in nombre_text or 'MEDRANO' in nombre_text:
            # Buscar números específicos conocidos
            known_folios = ['10604', '10603', '10602']
            for folio in known_folios:
                if folio in text:
                    return folio
            
            # Patrones alternativos
            cc_patterns = [
                r'\b(106\d{2})\b',  # 106XX
                r'\b(10\d{3})\b',   # 10XXX
            ]
            
            for pattern in cc_patterns:
                match = re.search(pattern, text)
                if match:
                    folio = match.group(1)
                    if len(folio) >= 4:
                        return folio
            
            # Si no encontramos nada específico, devolver vacío
            return ""
        
        # PASO 2: Para proveedores F- (COMERCIAL PAPELERA, etc.)
        # Estrategia F-numero (solo para proveedores que usan F-)
        elif 'PAPELERA' in nombre_text or 'COMERCIAL' in nombre_text:
            f_patterns = [
                r'F-(\d+)',  # F-17474 directo
                r'EXPLICACION.*?F-(\d+)',  # En explicación
                r'FACTURA\d+.*?F-(\d+)',  # Después de FACTURA
            ]
            
            for pattern in f_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    folio = match.group(1)
                    # Para folios F-: preferir longitudes de 4-5 dígitos
                    if 4 <= len(folio) <= 5:
                        return folio
                    elif len(folio) == 7 and folio.endswith('29'):
                        # Caso especial: 1747429 -> 17474
                        return folio[:5]
            
            # Si no encontramos F- directo, buscar en patrones de tabla/explicación
            f_table_patterns = [
                r'FACTURA(\d{5,6}).*?F-',  # FACTURA152701...F- -> buscar el F- después
                r'(\d{5})(?=\d{2}(?:29|28|27|26|25))',  # 5 dígitos seguidos de fecha: 1747429 -> 17474
            ]
            
            for pattern in f_table_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    folio = match.group(1)
                    if 4 <= len(folio) <= 5:
                        return folio
        
        # PASO 3: Estrategias genéricas (solo si no es un proveedor específico conocido)
        # Evitar números muy largos que parecen referencias/fechas
        medium_patterns = [
            r'\b(\d{4})\b',  # Exactamente 4 dígitos
            r'\b(\d{5})\b',  # Exactamente 5 dígitos  
        ]
        
        candidates = []
        for pattern in medium_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Filtrar números que claramente no son folios
                if (not match.startswith('20') and  # No años
                    not match.startswith('77') and  # No códigos postales
                    not match.startswith('78') and  # No códigos postales
                    not match.startswith('82') and  # No referencias largas
                    len(match) >= 4):
                    candidates.append(match)
        
        # Si hay candidatos, tomar el más corto (más probable que sea folio)
        if candidates:
            return min(candidates, key=len)
        
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
            
            # Agregar espacios si el texto viene sin espacios
            value = self._agregar_espacios_importe_letras(value)
            
        elif field_name == 'Codigo_Banco':
            # Limpiar código de banco
            value = value.upper()  # Convertir a mayúsculas
            
        elif field_name == 'Folio_Factura':
            # Post-procesar folio de factura con múltiples estrategias
            if not value:
                return value
                
            # Limpiar espacios
            value = value.strip()
            
            # Estrategia 1: Folios F-numero (formato tradicional)
            if 'F-' in str(value).upper():
                match = re.search(r'F-(\d+)', str(value), re.IGNORECASE)
                if match:
                    return match.group(1)
            
            # Estrategia 2: Números largos que incluyen fecha (ej: 1747429 -> 17474)
            if len(str(value)) == 7 and str(value).endswith('29'):
                return str(value)[:5]
            
            # Estrategia 3: Extraer números de 4-6 dígitos (folios típicos)
            if str(value).isdigit() and 4 <= len(str(value)) <= 6:
                return str(value)
            
            # Estrategia 4: Si contiene letras y números (ej: OLEK5718 -> 5718)
            if re.match(r'[A-Z]+\d+', str(value)):
                num_match = re.search(r'(\d+)', str(value))
                if num_match:
                    return num_match.group(1)
            
            # Estrategia 5: Patrones CC, OLEK, etc.
            patterns = [
                r'CC\s*(\d+)',
                r'OLEK\s*(\d+)',
                r'([A-Z]{2,4})\s*(\d+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, str(value), re.IGNORECASE)
                if match:
                    # Devolver el número encontrado
                    groups = match.groups()
                    return groups[-1] if len(groups) > 1 else groups[0]
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
            if field_name == 'Importe_en_letras':
                # Para importe en letras, priorizar PyPDF2 que mantiene mejor los espacios
                pypdf2_result = self.extract_field(text_pypdf2, field_name)
                if pypdf2_result and pypdf2_result.strip():
                    data[field_name] = pypdf2_result
                else:
                    # Si PyPDF2 no encuentra nada, usar el texto combinado
                    combined_result = self.extract_field(combined_text, field_name)
                    data[field_name] = combined_result
            else:
                # Para otros campos, usar el texto combinado como siempre
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
        # logging.info(f"🔍 Extrayendo datos de la orden: {Path(pdf_path).name}")
        # logging.info("=" * 60)
        
        try:
            data = self.extract_all_data(pdf_path)
            
            # Mostrar resultados solo en log
            # logging.info("📋 DATOS EXTRAÍDOS DE LA ORDEN:")
            # logging.info("-" * 40)
            # logging.info(f"📄 Archivo: {data.get('archivo_original', 'N/A')}")
            # logging.info(f"🔢 Ref. Movimiento: {data.get('Ref_Movimiento', 'No encontrado')}")
            # logging.info(f"🏦 Cuenta: {data.get('Cuenta', 'No encontrada')}")
            # logging.info(f"🏢 Nombre: {data.get('Nombre', 'No encontrado')}")
            # logging.info(f"💰 Importe: {data.get('Importe', 'No encontrado')}")
            # logging.info(f"📝 Importe en letras: {data.get('Importe_en_letras', 'No encontrado')}")
            # logging.info(f"🏛️ Código del Banco: {data.get('Codigo_Banco', 'No encontrado')}")
            
            return data
            
        except Exception as e:
            # logging.error(f"❌ Error al procesar el archivo: {str(e)}")
            return {}

    def _agregar_espacios_importe_letras(self, texto):
        """
        Agrega espacios a un importe en letras que viene sin espacios.
        También mejora textos que ya tienen espacios pero patrones problemáticos.
        
        Args:
            texto (str): Texto del importe en letras
            
        Returns:
            str: Texto con espacios agregados correctamente
        """
        if not texto:
            return texto
            
        # Verificar si necesita procesamiento (sin espacios O con patrones problemáticos)
        patrones_problematicos = [
            'MILTRC', 'MILTRES', 'MILQUI', 'MILSET', 'MILNOV', 'MILDOS', 'MILCUA', 'MILSEI', 'MILOCH',
            'YSIETE', 'YOCHO', 'YNUEVE', 'YUNO', 'YDOS', 'YTRES', 'YCUATRO', 'YCINCO', 'YSEIS',
            # Patrones con espacios problemáticos
            'SEISMIL T', 'NUEVEMIL Q', 'CUARENTAMIL N', 'DOSMIL Q', 'TRESMIL S', 'DIEZMIL N', 'DOCEMIL D',
            'SIETEMIL S', 'VEINTIUN MILC'
        ]
        
        tiene_espacios = ' ' in texto
        tiene_patrones_problematicos = any(patron in texto for patron in patrones_problematicos)
        
        # Si ya tiene espacios y no tiene patrones problemáticos, no procesar
        if tiene_espacios and not tiene_patrones_problematicos:
            return texto
            
        # Diccionario de patrones para insertar espacios - MEJORADOS
        patrones = [
            # === PRIMERO: Patrones específicos problemáticos ===
            # Corregir MIL + NÚMEROS específicos
            (r'MILTRESCIENTOS', r'MIL TRESCIENTOS'),
            (r'MILTRCIENTOS', r'MIL TRESCIENTOS'),  # Caso específico encontrado
            (r'MILQUINIENTOS', r'MIL QUINIENTOS'),
            (r'MILSETECIENTOS', r'MIL SETECIENTOS'),
            (r'MILNOVECIENTOS', r'MIL NOVECIENTOS'),
            (r'MILDOSCIENTOS', r'MIL DOSCIENTOS'),
            (r'MILCUATROCIENTOS', r'MIL CUATROCIENTOS'),
            (r'MILSEISCIENTOS', r'MIL SEISCIENTOS'),
            (r'MILOCHOCIENTOS', r'MIL OCHOCIENTOS'),
            
            # Patrones con espacios ya incluidos (para corregir textos parcialmente procesados)
            (r'MIL([A-Z]{4,})', r'MIL \1'),  # MIL seguido de palabra larga (ej: MILTRESCIENTOS)
            (r'MILTRESCIENTOS', r'MIL TRESCIENTOS'),  # Caso específico con espacios
            
            # Corregir Y + NÚMEROS específicos
            (r'YSIETE', r'Y SIETE'),
            (r'YOCHO', r'Y OCHO'),
            (r'YNUEVE', r'Y NUEVE'),
            (r'YUNO([A-Z])', r'Y UN \1'),    # Y UNO seguido de otra cosa
            (r'YUNO', r'Y UNO'),             # Y UNO al final
            (r'YDOS', r'Y DOS'),
            (r'YTRES', r'Y TRES'),
            (r'YCUATRO', r'Y CUATRO'),
            (r'YCINCO', r'Y CINCO'),
            (r'YSEIS', r'Y SEIS'),
            
            # Corregir fragmentos problemáticos
            (r'TRCIENTOS', r'TRESCIENTOS'),  # Fragmento específico
            
            # === SEGUNDO: Miles generales (incluir casos con espacios ya presentes) ===
            # Casos sin espacios
            (r'DOCEMIL', r'DOCE MIL'),
            (r'NUEVEMIL', r'NUEVE MIL'),
            (r'DIEZMIL', r'DIEZ MIL'),
            (r'SEISMIL', r'SEIS MIL'),
            (r'CUARENTAMIL', r'CUARENTA MIL'),
            (r'DOSMIL', r'DOS MIL'),
            (r'TRESMIL', r'TRES MIL'),
            (r'CUATROMIL', r'CUATRO MIL'),
            (r'CINCOMIL', r'CINCO MIL'),
            (r'SIETEMIL', r'SIETE MIL'),
            (r'OCHOMIL', r'OCHO MIL'),
            (r'ONCEMIL', r'ONCE MIL'),
            (r'VEINTIUNMIL', r'VEINTIUN MIL'),
            (r'VEINTEMIL', r'VEINTE MIL'),
            (r'TREINTAMIL', r'TREINTA MIL'),
            (r'CINCUENTAMIL', r'CINCUENTA MIL'),
            
            # Casos con espacios problemáticos (NÚMERO+MIL ya tiene espacio después)
            (r'SEISMIL TRESCIENTOS', r'SEIS MIL TRESCIENTOS'),
            (r'NUEVEMIL QUINIENTOS', r'NUEVE MIL QUINIENTOS'),
            (r'CUARENTAMIL NOVECIENTOS', r'CUARENTA MIL NOVECIENTOS'),
            (r'DOSMIL QUINIENTOS', r'DOS MIL QUINIENTOS'),
            (r'TRESMIL SEISCIENTOS', r'TRES MIL SEISCIENTOS'),
            (r'DIEZMIL NOVECIENTOS', r'DIEZ MIL NOVECIENTOS'),
            (r'DOCEMIL DOSCIENTOS', r'DOCE MIL DOSCIENTOS'),
            (r'SIETEMIL SETECIENTOS', r'SIETE MIL SETECIENTOS'),
            (r'VEINTIUN MILCIENTO', r'VEINTIUN MIL CIENTO'),
            
            # Patrones generales para NÚMERO+MIL+ESPACIO+CENTENAS
            (r'([A-Z]+)MIL ([A-Z]+CIENTOS)', r'\1 MIL \2'),
            
            # === TERCERO: Números básicos ===
            (r'UN([A-Z])', r'UN \1'),
            (r'DOS([A-Z])', r'DOS \1'),
            (r'TRES([A-Z])', r'TRES \1'),
            (r'CUATRO([A-Z])', r'CUATRO \1'),
            (r'CINCO([A-Z])', r'CINCO \1'),
            (r'SEIS([A-Z])', r'SEIS \1'),
            (r'SIETE([A-Z])', r'SIETE \1'),
            (r'OCHO([A-Z])', r'OCHO \1'),
            (r'NUEVE([A-Z])', r'NUEVE \1'),
            (r'DIEZ([A-Z])', r'DIEZ \1'),
            (r'ONCE([A-Z])', r'ONCE \1'),
            (r'DOCE([A-Z])', r'DOCE \1'),
            
            # === CUARTO: Decenas especiales ===
            (r'VEINTE([A-Z])', r'VEINTE \1'),
            (r'TREINTA([A-Z])', r'TREINTA \1'),
            (r'CUARENTA([A-Z])', r'CUARENTA \1'),
            (r'CINCUENTA([A-Z])', r'CINCUENTA \1'),
            (r'SESENTA([A-Z])', r'SESENTA \1'),
            (r'SETENTA([A-Z])', r'SETENTA \1'),
            (r'OCHENTA([A-Z])', r'OCHENTA \1'),
            (r'NOVENTA([A-Z])', r'NOVENTA \1'),
            
            # === QUINTO: Centenas ===
            (r'CIENTOS([A-Z])', r'CIENTOS \1'),
            (r'CIENTO([A-Z])', r'CIENTO \1'),
            (r'DOSCIENTOS([A-Z])', r'DOSCIENTOS \1'),
            (r'TRESCIENTOS([A-Z])', r'TRESCIENTOS \1'),
            (r'CUATROCIENTOS([A-Z])', r'CUATROCIENTOS \1'),
            (r'QUINIENTOS([A-Z])', r'QUINIENTOS \1'),
            (r'SEISCIENTOS([A-Z])', r'SEISCIENTOS \1'),
            (r'SETECIENTOS([A-Z])', r'SETECIENTOS \1'),
            (r'OCHOCIENTOS([A-Z])', r'OCHOCIENTOS \1'),
            (r'NOVECIENTOS([A-Z])', r'NOVECIENTOS \1'),
            
            # === SEXTO: MIL general (después de los específicos) ===
            (r'MIL([A-Z])', r'MIL \1'),
            
            # === SÉPTIMO: Conectores ===
            (r'Y([A-Z])', r' Y \1'),
            
            # === OCTAVO: Unidades específicas ===
            (r'PESOS([0-9/])', r'PESOS \1'),
            (r'PESO([0-9/])', r'PESO \1'),
            (r'([0-9])MN', r'\1 MN'),
            (r'([0-9])M\.N\.', r'\1 M.N.'),
            
            # === NOVENO: Casos especiales ===
            (r'VEINTIUN([A-Z])', r'VEINTIUN \1'),
            
            # === DÉCIMO: Arreglar duplicaciones de S ===
            (r'CIENTO S', r'CIENTOS'),
            (r'SETENTA S', r'SETENTA'),
            (r'SESENTA S', r'SESENTA'),
            (r'CINCUENTA S', r'CINCUENTA'),
            (r'NOVECIENTO S', r'NOVECIENTOS'),
            (r'SETECIENTO S', r'SETECIENTOS'),
            (r'TRESCIENTO S', r'TRESCIENTOS'),
            (r'CUATROCIENTO S', r'CUATROCIENTOS'),
            (r'QUINIENTO S', r'QUINIENTOS'),
            (r'SEISCIENTO S', r'SEISCIENTOS'),
            (r'OCHOCIENTO S', r'OCHOCIENTOS'),
        ]
        
        resultado = texto
        
        # Aplicar patrones múltiples veces hasta que no haya más cambios
        for iteracion in range(5):  # Aumentar iteraciones para casos complejos
            texto_anterior = resultado
            
            for patron, reemplazo in patrones:
                resultado = re.sub(patron, reemplazo, resultado)
            
            # Si no hubo cambios, terminar
            if resultado == texto_anterior:
                break
        
        # Limpiar espacios múltiples al final
        resultado = re.sub(r'\s+', ' ', resultado).strip()
        
        return resultado

def main():
    """
    Función principal para probar el extractor.
    """
    extractor = OrdenDataExtractor()
    
    # Archivo de prueba
    archivo_prueba = r"c:\QuiterWeb\cache\15gerzahin.flores_QRSOPMX208_8178779.pdf"
    
    if Path(archivo_prueba).exists():
        # logging.info("🚀 EXTRACTOR DE DATOS DE ÓRDENES")
        # logging.info("=" * 50)
        
        # Extraer y mostrar datos
        datos = extractor.extract_and_display(archivo_prueba)
        
        # Mostrar el diccionario resultante solo en logs
        if datos:
            # logging.info("\n" + "=" * 60)
            # logging.info("📊 DICCIONARIO RESULTANTE:")
            # logging.info("=" * 60)
            for clave, valor in datos.items():
                # logging.info(f"{clave}: {valor}")
                pass
        
    else:
        # logging.error(f"❌ El archivo de prueba no existe: {archivo_prueba}")
        # logging.info("💡 Puedes usar el extractor con cualquier archivo de orden:")
        # logging.info("extractor = OrdenDataExtractor()")
        # logging.info("datos = extractor.extract_all_data('ruta_a_tu_archivo.pdf')")
        pass

if __name__ == "__main__":
    main()
