"""
Controlador para la lógica de exportación
"""
import os
import sys
import csv
import json
from typing import List, Dict, Any, Optional
import logging
import traceback

# Agregar path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from ..utils.dialog_utils import DialogUtils
    from ..utils.format_utils import format_currency
except ImportError:
    from utils.dialog_utils import DialogUtils
    from utils.format_utils import format_currency


class ExportController:
    """Controlador que maneja la lógica de exportación de datos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.dialog_utils = DialogUtils()
    
    def export_to_csv(self, data: List[Dict[str, Any]], default_filename: str = "facturas_export") -> bool:
        """
        Exporta datos a archivo CSV
        
        Args:
            data: Lista de diccionarios con los datos a exportar
            default_filename: Nombre por defecto del archivo
            
        Returns:
            bool: True si se exportó correctamente
        """
        try:
            if not data:
                self.dialog_utils.show_warning("No hay datos para exportar")
                return False
            
            # Solicitar archivo de destino
            output_path = self.dialog_utils.save_file_dialog(
                title="Exportar a CSV",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialname=f"{default_filename}.csv"
            )
            
            if not output_path:
                return False
            
            # Obtener las columnas del primer registro
            if not data:
                self.dialog_utils.show_warning("No hay datos para exportar")
                return False
            
            fieldnames = list(data[0].keys())
            
            # Escribir archivo CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in data:
                    # Formatear valores monetarios
                    formatted_row = {}
                    for key, value in row.items():
                        if key in ['total', 'subtotal', 'iva_trasladado', 'ret_iva', 'ret_isr'] and isinstance(value, (int, float)):
                            formatted_row[key] = format_currency(value)
                        else:
                            formatted_row[key] = str(value) if value is not None else ''
                    
                    writer.writerow(formatted_row)
            
            self.dialog_utils.show_info(f"Datos exportados a:\n{output_path}")
            self.logger.info(f"Exportación CSV exitosa: {len(data)} registros en {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error en exportación CSV: {e}")
            traceback.print_exc()
            self.dialog_utils.show_error(f"Error al exportar: {str(e)}")
            return False
    
    def export_to_excel(self, data: List[Dict[str, Any]], default_filename: str = "facturas_export") -> bool:
        """
        Exporta datos a archivo Excel
        
        Args:
            data: Lista de diccionarios con los datos a exportar
            default_filename: Nombre por defecto del archivo
            
        Returns:
            bool: True si se exportó correctamente
        """
        try:
            if not data:
                self.dialog_utils.show_warning("No hay datos para exportar")
                return False
            
            # Verificar si pandas está disponible
            try:
                import pandas as pd
            except ImportError:
                self.dialog_utils.show_error("Pandas no está instalado. Use exportación CSV como alternativa.")
                return False
            
            # Solicitar archivo de destino
            output_path = self.dialog_utils.save_file_dialog(
                title="Exportar a Excel",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialname=f"{default_filename}.xlsx"
            )
            
            if not output_path:
                return False
            
            # Crear DataFrame
            df = pd.DataFrame(data)
            
            # Formatear columnas monetarias
            monetary_columns = ['total', 'subtotal', 'iva_trasladado', 'ret_iva', 'ret_isr']
            for col in monetary_columns:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: float(x) if pd.notna(x) else 0.0)
            
            # Escribir a Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Facturas', index=False)
                
                # Formatear la hoja
                workbook = writer.book
                worksheet = writer.sheets['Facturas']
                
                # Ajustar ancho de columnas
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            self.dialog_utils.show_info(f"Datos exportados a:\n{output_path}")
            self.logger.info(f"Exportación Excel exitosa: {len(data)} registros en {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error en exportación Excel: {e}")
            traceback.print_exc()
            self.dialog_utils.show_error(f"Error al exportar: {str(e)}")
            return False
    
    def export_to_json(self, data: List[Dict[str, Any]], default_filename: str = "facturas_export") -> bool:
        """
        Exporta datos a archivo JSON
        
        Args:
            data: Lista de diccionarios con los datos a exportar
            default_filename: Nombre por defecto del archivo
            
        Returns:
            bool: True si se exportó correctamente
        """
        try:
            if not data:
                self.dialog_utils.show_warning("No hay datos para exportar")
                return False
            
            # Solicitar archivo de destino
            output_path = self.dialog_utils.save_file_dialog(
                title="Exportar a JSON",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialname=f"{default_filename}.json"
            )
            
            if not output_path:
                return False
            
            # Preparar datos para JSON (convertir valores numéricos)
            json_data = []
            for row in data:
                json_row = {}
                for key, value in row.items():
                    if isinstance(value, (int, float)):
                        json_row[key] = float(value)
                    else:
                        json_row[key] = str(value) if value is not None else None
                json_data.append(json_row)
            
            # Escribir archivo JSON
            with open(output_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(json_data, jsonfile, indent=2, ensure_ascii=False)
            
            self.dialog_utils.show_info(f"Datos exportados a:\n{output_path}")
            self.logger.info(f"Exportación JSON exitosa: {len(data)} registros en {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error en exportación JSON: {e}")
            traceback.print_exc()
            self.dialog_utils.show_error(f"Error al exportar: {str(e)}")
            return False
    
    def export_summary_report(self, data: List[Dict[str, Any]], default_filename: str = "resumen_facturas") -> bool:
        """
        Exporta un reporte de resumen en CSV
        
        Args:
            data: Lista de diccionarios con los datos
            default_filename: Nombre por defecto del archivo
            
        Returns:
            bool: True si se exportó correctamente
        """
        try:
            if not data:
                self.dialog_utils.show_warning("No hay datos para generar el resumen")
                return False
            
            # Calcular estadísticas
            total_facturas = len(data)
            total_monto = sum(float(row.get('total', 0)) for row in data)
            facturas_cargadas = sum(1 for row in data if row.get('cargada_bool', False))
            facturas_pagadas = sum(1 for row in data if row.get('pagada_bool', False))
            
            # Agrupar por tipo
            tipos = {}
            for row in data:
                tipo = row.get('tipo', 'Sin tipo')
                if tipo not in tipos:
                    tipos[tipo] = {'count': 0, 'total': 0.0}
                tipos[tipo]['count'] += 1
                tipos[tipo]['total'] += float(row.get('total', 0))
            
            # Agrupar por proveedor
            proveedores = {}
            for row in data:
                proveedor = row.get('nombre_emisor', 'Sin proveedor')
                if proveedor not in proveedores:
                    proveedores[proveedor] = {'count': 0, 'total': 0.0}
                proveedores[proveedor]['count'] += 1
                proveedores[proveedor]['total'] += float(row.get('total', 0))
            
            # Solicitar archivo de destino
            output_path = self.dialog_utils.save_file_dialog(
                title="Exportar Resumen",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialname=f"{default_filename}.csv"
            )
            
            if not output_path:
                return False
            
            # Escribir reporte
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Encabezado del reporte
                writer.writerow(['REPORTE DE RESUMEN DE FACTURAS'])
                writer.writerow([''])
                
                # Estadísticas generales
                writer.writerow(['ESTADISTICAS GENERALES'])
                writer.writerow(['Total de facturas:', total_facturas])
                writer.writerow(['Total monto:', format_currency(total_monto)])
                writer.writerow(['Facturas cargadas:', f"{facturas_cargadas} ({facturas_cargadas/total_facturas*100:.1f}%)"])
                writer.writerow(['Facturas pagadas:', f"{facturas_pagadas} ({facturas_pagadas/total_facturas*100:.1f}%)"])
                writer.writerow([''])
                
                # Resumen por tipo
                writer.writerow(['RESUMEN POR TIPO'])
                writer.writerow(['Tipo', 'Cantidad', 'Total'])
                for tipo, stats in sorted(tipos.items()):
                    writer.writerow([tipo, stats['count'], format_currency(stats['total'])])
                writer.writerow([''])
                
                # Resumen por proveedor (top 10)
                writer.writerow(['TOP 10 PROVEEDORES'])
                writer.writerow(['Proveedor', 'Cantidad', 'Total'])
                top_proveedores = sorted(proveedores.items(), key=lambda x: x[1]['total'], reverse=True)[:10]
                for proveedor, stats in top_proveedores:
                    writer.writerow([proveedor, stats['count'], format_currency(stats['total'])])
            
            self.dialog_utils.show_info(f"Reporte de resumen exportado a:\n{output_path}")
            self.logger.info(f"Reporte de resumen generado en {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generando reporte de resumen: {e}")
            traceback.print_exc()
            self.dialog_utils.show_error(f"Error al generar reporte: {str(e)}")
            return False
    
    def get_export_formats(self) -> List[str]:
        """
        Obtiene la lista de formatos de exportación disponibles
        
        Returns:
            List[str]: Lista de formatos disponibles
        """
        formats = ["CSV", "JSON"]
        
        # Verificar si pandas está disponible para Excel
        try:
            import pandas as pd
            formats.append("Excel")
        except ImportError:
            pass
        
        return formats
