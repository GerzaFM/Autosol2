"""
Controlador para generar reportes PDF de cheques múltiples
"""
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os


class ReporteChequeMultiple:
    """
    Generador de reportes PDF para cheques con múltiples facturas
    """
    
    def __init__(self, facturas_data, ruta_pdf=None, info_cheque=None):
        """
        Inicializa el generador de reportes
        
        Args:
            facturas_data: Lista de diccionarios con datos de las facturas
            ruta_pdf: Ruta donde se guardará el PDF (opcional)
            info_cheque: Diccionario con información adicional del cheque (opcional)
        """
        self.facturas = facturas_data
        self.info_cheque = info_cheque or {}
        
        print(f"🔧 ReporteChequeMultiple - Inicializando con {len(facturas_data)} facturas")
        print(f"🔧 Ruta recibida: {ruta_pdf}")
        
        # Manejar la ruta del PDF de manera más específica
        if ruta_pdf is not None and ruta_pdf != "":
            self.ruta_pdf = ruta_pdf
            print(f"✅ Usando ruta proporcionada: {ruta_pdf}")
        else:
            self.ruta_pdf = self._generar_ruta_default()
            print(f"🔄 Usando ruta por defecto: {self.ruta_pdf}")
        
        self.styles = getSampleStyleSheet()
        self._crear_estilos_personalizados()
    
    def _generar_ruta_default(self):
        """
        Genera una ruta por defecto para el PDF
        
        Returns:
            str: Ruta del archivo PDF
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"reporte_cheque_multiple_{timestamp}.pdf"
        
        # Buscar carpeta de reportes de cheques múltiples
        # Primero intentar en el directorio del proyecto
        directorio_base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        directorio_reportes = os.path.join(directorio_base, "reportes", "cheques_multiples")
        
        # Si no existe, crear la estructura de directorios
        if not os.path.exists(directorio_reportes):
            os.makedirs(directorio_reportes, exist_ok=True)
        
        return os.path.join(directorio_reportes, nombre_archivo)
    
    def _crear_estilos_personalizados(self):
        """
        Crea estilos personalizados para el reporte
        """
        self.styles.add(ParagraphStyle(
            name='TituloReporte',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubtituloReporte',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=10,
            alignment=TA_LEFT,
            textColor=colors.darkgreen
        ))
        
        self.styles.add(ParagraphStyle(
            name='InfoGeneral',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=5,
            alignment=TA_LEFT
        ))
    
    def _formatear_moneda(self, valor):
        """
        Formatea un valor como moneda con símbolo de pesos
        
        Args:
            valor: Valor numérico a formatear
            
        Returns:
            str: Valor formateado como moneda
        """
        try:
            if valor is None or valor == '':
                return "$0.00"
            return f"${float(valor):,.2f}"
        except (ValueError, TypeError):
            return "$0.00"
    
    def _formatear_moneda_simple(self, valor):
        """
        Formatea un valor como moneda SIN símbolo de pesos (para el formato de tabla)
        
        Args:
            valor: Valor numérico a formatear
            
        Returns:
            str: Valor formateado sin símbolo de pesos
        """
        try:
            if valor is None or valor == '':
                return "$0"
            numero = float(valor)
            if numero == 0:
                return "$0"
            return f"${numero:,.0f}"  # Sin decimales, como en la imagen
        except (ValueError, TypeError):
            return "$0"
    
    def _crear_tabla_facturas(self):
        """
        Crea la tabla con el detalle de todas las facturas y totales
        Formato: Vale, Descripción, Folio, Importe, Iva, RetIva, RetIsr, Total
        
        Returns:
            Table: Tabla de reportlab con las facturas y fila de totales
        """
        # Encabezados de la tabla (igual al formato de la imagen)
        headers = [
            'Vale',
            'Descripción',
            'Folio',
            'Importe',
            'Iva',
            'RetIva',
            'RetIsr',
            'Total'
        ]
        
        # Crear filas de datos
        data = [headers]
        
        # Variables para totales
        importe_total = 0
        iva_total = 0
        ret_iva_total = 0
        ret_isr_total = 0
        total_general = 0
        
        for factura in self.facturas:
            # Obtener valores numéricos
            importe = float(factura.get('subtotal', 0) or 0)  # Importe = Subtotal
            iva = float(factura.get('iva_trasladado', 0) or 0)
            ret_iva = float(factura.get('ret_iva', 0) or 0)
            ret_isr = float(factura.get('ret_isr', 0) or 0)
            total = float(factura.get('total', 0) or 0)
            
            # Sumar a totales
            importe_total += importe
            iva_total += iva
            ret_iva_total += ret_iva
            ret_isr_total += ret_isr
            total_general += total
            
            # Obtener descripción de los conceptos (si está disponible)
            descripcion = factura.get('conceptos', '')
            if not descripcion:
                # Si no hay conceptos, usar nombre del emisor como descripción
                descripcion = str(factura.get('nombre_emisor', ''))[:30]
            else:
                # Tomar solo los primeros 30 caracteres de los conceptos
                descripcion = str(descripcion)[:30]
            
            fila = [
                str(factura.get('no_vale', '')),
                descripcion,
                str(factura.get('folio', '')),  # Solo folio, sin serie
                self._formatear_moneda_simple(importe),
                self._formatear_moneda_simple(iva),
                self._formatear_moneda_simple(ret_iva),
                self._formatear_moneda_simple(ret_isr),
                self._formatear_moneda_simple(total)
            ]
            data.append(fila)
        
        # Agregar fila de totales (igual al formato de la imagen)
        fila_totales = [
            '',  # Vale vacío
            '',  # Descripción vacía
            'Total',  # En la columna Folio
            self._formatear_moneda_simple(importe_total),
            self._formatear_moneda_simple(iva_total),
            self._formatear_moneda_simple(ret_iva_total),
            self._formatear_moneda_simple(ret_isr_total),
            self._formatear_moneda_simple(total_general)
        ]
        data.append(fila_totales)
        
        # Crear tabla con anchos ajustados al formato
        tabla = Table(data, colWidths=[
            1.5*cm, 3.5*cm, 1.5*cm, 2*cm, 1.5*cm, 1.5*cm, 1.5*cm, 2*cm
        ])
        
        # Aplicar estilos a la tabla (similar al formato de la imagen)
        num_filas = len(data)
        tabla.setStyle(TableStyle([
            # Estilo del encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            
            # Estilo del contenido (excepto última fila de totales)
            ('FONTNAME', (0, 1), (-1, num_filas-2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, num_filas-2), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            
            # Alineación de números a la derecha
            ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
            
            # Alineación de texto a la izquierda para descripción
            ('ALIGN', (1, 1), (1, num_filas-2), 'LEFT'),
            
            # Estilo especial para la fila de totales
            ('BACKGROUND', (0, num_filas-1), (-1, num_filas-1), colors.white),
            ('TEXTCOLOR', (0, num_filas-1), (-1, num_filas-1), colors.black),
            ('FONTNAME', (0, num_filas-1), (-1, num_filas-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, num_filas-1), (-1, num_filas-1), 9),
        ]))
        
        return tabla
    
    def generar_reporte(self):
        """
        Genera el reporte PDF completo
        
        Returns:
            str: Ruta del archivo PDF generado
        """
        print(f"📝 Generando reporte PDF en: {self.ruta_pdf}")
        
        # Verificar que el directorio existe
        directorio = os.path.dirname(self.ruta_pdf)
        if not os.path.exists(directorio):
            print(f"📁 Creando directorio: {directorio}")
            os.makedirs(directorio, exist_ok=True)
        
        # Crear el documento PDF
        doc = SimpleDocTemplate(
            self.ruta_pdf,
            pagesize=A4,
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Lista de elementos del reporte
        story = []
        
        # Obtener nombre del proveedor para el encabezado
        nombre_proveedor = "Proveedor No Especificado"
        if self.facturas and len(self.facturas) > 0:
            nombre_proveedor = self.facturas[0].get('nombre_emisor', 'Proveedor No Especificado')
        
        # Título con el nombre del proveedor (como en la imagen)
        titulo = Paragraph(nombre_proveedor, self.styles['TituloReporte'])
        story.append(titulo)
        story.append(Spacer(1, 0.5*cm))
        """"
        # Información adicional (opcional)
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        if self.info_cheque and 'numero_cheque' in self.info_cheque:
            info_cheque = Paragraph(f"<b>Cheque:</b> {self.info_cheque['numero_cheque']} - <b>Fecha:</b> {fecha_actual}", self.styles['InfoGeneral'])
            story.append(info_cheque)
            story.append(Spacer(1, 0.3*cm))
        """
        # Tabla de facturas con totales incluidos
        tabla_facturas = self._crear_tabla_facturas()
        story.append(tabla_facturas)

        """
        # Pie de página con información adicional
        story.append(Spacer(1, 1*cm))
        pie_info = Paragraph(
            f"<i>Reporte generado automáticamente por AutoSol2<br/>"
            f"Archivo: {os.path.basename(self.ruta_pdf)}</i>",
            self.styles['InfoGeneral']
        )
        story.append(pie_info)
        """
        
        # Generar el PDF
        try:
            print(f"🔄 Construyendo documento PDF...")
            doc.build(story)
            print(f"✅ PDF construido exitosamente")
            
            # Verificar que el archivo fue creado
            if os.path.exists(self.ruta_pdf):
                tamaño = os.path.getsize(self.ruta_pdf)
                print(f"📄 Archivo creado: {self.ruta_pdf} ({tamaño} bytes)")
            else:
                print(f"❌ ERROR: El archivo no fue creado en {self.ruta_pdf}")
                
        except Exception as e:
            print(f"❌ Error al construir PDF: {e}")
            raise
        
        return self.ruta_pdf
    
    def abrir_reporte(self):
        """
        Abre el reporte PDF generado con el visor predeterminado
        """
        try:
            if os.path.exists(self.ruta_pdf):
                os.startfile(self.ruta_pdf)
            else:
                print(f"Error: No se encontró el archivo {self.ruta_pdf}")
        except Exception as e:
            print(f"Error al abrir el reporte: {e}")


def generar_reporte_cheque_multiple(facturas_data, ruta_pdf=None, info_cheque=None, abrir_automaticamente=True):
    """
    Función de conveniencia para generar un reporte de cheque múltiple
    
    Args:
        facturas_data: Lista de diccionarios con datos de las facturas
        ruta_pdf: Ruta donde se guardará el PDF (opcional)
        info_cheque: Diccionario con información adicional del cheque (opcional)
        abrir_automaticamente: Si True, abre el PDF automáticamente
        
    Returns:
        str: Ruta del archivo PDF generado
    """
    reporte = ReporteChequeMultiple(facturas_data, ruta_pdf, info_cheque)
    ruta_generada = reporte.generar_reporte()
    
    if abrir_automaticamente:
        reporte.abrir_reporte()
    
    return ruta_generada


# Este archivo contiene el generador de reportes de cheques múltiples
    print(f"Relación de vales generada en: {ruta}")
