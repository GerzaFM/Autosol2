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
        Una fila por cheque: codigo_quiter, monto, banco
        """
        cheques = list(self.layout.cheques)  # backref='cheques' en el modelo

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Resumen Layout"

        # Encabezados
        ws.append(["codigo_quiter", "monto", "banco"])

        for cheque in cheques:
            facturas = list(cheque.facturas)
            if not facturas:
                continue
            proveedor = getattr(facturas[0], "proveedor", None)
            codigo_quiter = getattr(proveedor, "codigo_quiter", "") if proveedor else ""
            ws.append([
                codigo_quiter,
                float(cheque.monto),
                cheque.banco
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
