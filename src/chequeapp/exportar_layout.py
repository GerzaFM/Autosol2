import openpyxl
import os


class LayoutExporter:
    def __init__(self, layout):
        """
        layout: instancia del modelo Layout (por ejemplo, un objeto de Peewee)
        """
        self.layout = layout

    def exportar_layout_excel(self, ruta_archivo=None):
        """
        Exporta los cheques relacionados con este layout a Excel.
        Una fila por cheque: alias, nombre, importe, descripcion, referencia
        """
        cheques = list(self.layout.cheques)  # backref='cheques' en el modelo

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Resumen Layout"

        # Encabezados
        ws.append(["Alias", "Nombre", "Importe", "Descripcion", "Referencia"])

        for cheque in cheques:
            # Extraer datos del cheque usando la misma lógica que show_layout_content
            codigo = cheque.proveedor.codigo_quiter if cheque.proveedor else ''
            nombre = cheque.proveedor.nombre if cheque.proveedor else ''
            importe_float = float(cheque.monto) if cheque.monto else 0.0
            vale = cheque.vale or ''
            folio = cheque.folio or ''
            
            # Obtener descripciones de los vales
            descripcion_conceptos = ""
            for factura in cheque.facturas:
                # Si la factura tiene un vale asociado
                if hasattr(factura, "vale") and factura.vale:
                    try:
                        # Obtener el primer (y único) vale de la consulta
                        vale_obj = factura.vale.first()
                        
                        if vale_obj and hasattr(vale_obj, "descripcion") and vale_obj.descripcion:
                            descripcion_conceptos += f"{vale_obj.descripcion} "
                    except Exception as e:
                        pass  # Silenciar errores aquí
            
            descripcion_conceptos = descripcion_conceptos.strip()
            
            # Crear referencia: tomar solo el primer vale (antes del espacio) sin la "V"
            if vale:
                primer_vale = vale.split()[0]  # Obtener solo el primer vale antes del espacio
                referencia = primer_vale[1:] if len(primer_vale) > 1 else primer_vale
            else:
                referencia = ""
            
            # Crear descripción completa: vale + folio + conceptos de los vales
            descripcion = f"{vale} "
            if folio:
                descripcion += f"F-{folio} "
            if descripcion_conceptos:  # Si hay descripciones de vales, agregarlas
                descripcion += f"{descripcion_conceptos}"
            
            descripcion = descripcion.strip()
            
            ws.append([
                codigo,           # Alias
                nombre,           # Nombre (Proveedor)
                importe_float,    # Importe como float
                descripcion,      # Descripción completa con conceptos
                referencia        # Referencia
            ])
 
        # Guardar archivo en la carpeta 'reportes'
        if not ruta_archivo:
            from datetime import datetime
            nombre = f"Layout_{self.layout.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            carpeta_reportes = os.path.join(os.getcwd(), "reportes")
            os.makedirs(carpeta_reportes, exist_ok=True)
            ruta_archivo = os.path.join(carpeta_reportes, nombre)
        wb.save(ruta_archivo)
        print(f"Archivo Excel exportado: {ruta_archivo}")
        return ruta_archivo
