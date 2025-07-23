"""
Ejemplo de uso del componente SearchEntry para diferentes tipos de búsqueda.
Muestra cómo usar el componente para buscar proveedores, tipos de vale, etc.
"""
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from search_components import SearchEntry

# Datos de ejemplo para tipos de vale
TIPOS_VALE_DATA = [
    {'codigo': 'AU', 'descripcion': 'ACONDICIONAMIENTO DE UNIDADES', 'categoria': 'Mantenimiento'},
    {'codigo': 'AF', 'descripcion': 'ACTIVO FIJO', 'categoria': 'Contabilidad'},
    {'codigo': 'SA', 'descripcion': 'AGUA', 'categoria': 'Servicios'},
    {'codigo': 'AGO', 'descripcion': 'AGUINALDO', 'categoria': 'Recursos Humanos'},
    {'codigo': 'APR', 'descripcion': 'ANTICIPO A PROVEEDORES', 'categoria': 'Finanzas'},
    {'codigo': 'ALF', 'descripcion': 'ASESORIA, AUDITORIA Y FISCAL', 'categoria': 'Consultoria'},
    {'codigo': 'INS', 'descripcion': 'ATENCION A CLIENTES Y PROVEEDORES', 'categoria': 'Servicios'},
    {'codigo': 'BLI', 'descripcion': 'BASES POR LICITACIONES', 'categoria': 'Administrativo'},
    {'codigo': 'CP', 'descripcion': 'CAPACITACION AL PERSONAL', 'categoria': 'Recursos Humanos'},
    {'codigo': 'GA', 'descripcion': 'COMBUSTIBLES Y LUBRICANTES', 'categoria': 'Operaciones'},
    {'codigo': 'CDG', 'descripcion': 'COMISIONES DIRECTIVAS Y GERENCIALES', 'categoria': 'Recursos Humanos'},
    {'codigo': 'CBA', 'descripcion': 'COMISIONES BANCARIAS', 'categoria': 'Finanzas'},
    {'codigo': 'CE', 'descripcion': 'COMPRA DE EQUIPO COMPUTO Y OFICINA', 'categoria': 'Tecnologia'},
]

# Datos de ejemplo para proveedores
PROVEEDORES_DATA = [
    {'id': 1, 'nombre': 'SOCIEDAD CONSTRUCTORA DUBLEX', 'rfc': 'SCD123456789', 'telefono': '555-1111', 'email': 'contacto@dublex.com'},
    {'id': 2, 'nombre': 'Materiales de Oficina S.A.', 'rfc': 'MOF987654321', 'telefono': '555-2222', 'email': 'ventas@materiales.com'},
    {'id': 3, 'nombre': 'Servicios Tecnológicos S.A.', 'rfc': 'STQ456789123', 'telefono': '555-3333', 'email': 'info@tecnologicos.com'},
    {'id': 4, 'nombre': 'Consultores Empresariales S.C.', 'rfc': 'CES321654987', 'telefono': '555-4444', 'email': 'consultas@empresariales.com'},
]

class SearchExampleApp(tb.Frame):
    """Aplicación de ejemplo para mostrar el uso de SearchEntry."""
    
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self._create_layout()
    
    def _create_layout(self):
        """Crea el layout de la aplicación."""
        main_frame = tb.Frame(self, padding=30)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Título
        title_label = tb.Label(
            main_frame,
            text="Ejemplos de Componente de Búsqueda",
            font=("Segoe UI", 16, "bold"),
            bootstyle="inverse-primary"
        )
        title_label.pack(pady=(0, 30))
        
        # Ejemplo 1: Búsqueda de Proveedores
        proveedor_frame = tb.LabelFrame(main_frame, text="Búsqueda de Proveedores", padding=20)
        proveedor_frame.pack(fill=X, pady=(0, 20))
        
        tb.Label(proveedor_frame, text="Proveedor:", font=("Segoe UI", 10)).pack(side=LEFT, padx=(0, 10))
        
        self.proveedor_search = SearchEntry(
            proveedor_frame,
            placeholder_text="Seleccionar proveedor...",
            search_title="Buscar Proveedor",
            items=PROVEEDORES_DATA,
            search_fields=['nombre', 'rfc'],
            display_columns=[
                {'key': 'nombre', 'title': 'Nombre', 'width': 250},
                {'key': 'rfc', 'title': 'RFC', 'width': 120},
                {'key': 'telefono', 'title': 'Teléfono', 'width': 100},
                {'key': 'email', 'title': 'Email', 'width': 180}
            ]
        )
        self.proveedor_search.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        tb.Button(
            proveedor_frame,
            text="Ver Selección",
            bootstyle="info-outline",
            command=self._show_proveedor_selection
        ).pack(side=RIGHT)
        
        # Ejemplo 2: Búsqueda de Tipos de Vale
        tipo_frame = tb.LabelFrame(main_frame, text="Búsqueda de Tipos de Vale", padding=20)
        tipo_frame.pack(fill=X, pady=(0, 20))
        
        tb.Label(tipo_frame, text="Tipo de Vale:", font=("Segoe UI", 10)).pack(side=LEFT, padx=(0, 10))
        
        self.tipo_search = SearchEntry(
            tipo_frame,
            placeholder_text="Seleccionar tipo de vale...",
            search_title="Buscar Tipo de Vale",
            items=TIPOS_VALE_DATA,
            search_fields=['codigo', 'descripcion', 'categoria'],
            display_columns=[
                {'key': 'codigo', 'title': 'Código', 'width': 80},
                {'key': 'descripcion', 'title': 'Descripción', 'width': 300},
                {'key': 'categoria', 'title': 'Categoría', 'width': 120}
            ]
        )
        self.tipo_search.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        tb.Button(
            tipo_frame,
            text="Ver Selección",
            bootstyle="info-outline",
            command=self._show_tipo_selection
        ).pack(side=RIGHT)
        
        # Frame para mostrar resultados
        self.results_frame = tb.LabelFrame(main_frame, text="Selecciones Actuales", padding=20)
        self.results_frame.pack(fill=BOTH, expand=True)
        
        self.results_text = tb.Text(
            self.results_frame,
            height=10,
            font=("Consolas", 10),
            state="disabled"
        )
        self.results_text.pack(fill=BOTH, expand=True)
        
        # Botones de acción
        buttons_frame = tb.Frame(main_frame)
        buttons_frame.pack(fill=X, pady=(20, 0))
        
        tb.Button(
            buttons_frame,
            text="Limpiar Todo",
            bootstyle="secondary-outline",
            command=self._clear_all
        ).pack(side=LEFT)
        
        tb.Button(
            buttons_frame,
            text="Mostrar Todas las Selecciones",
            bootstyle="primary",
            command=self._show_all_selections
        ).pack(side=RIGHT)
    
    def _show_proveedor_selection(self):
        """Muestra la selección de proveedor."""
        selected = self.proveedor_search.get_selected_item()
        if selected:
            message = f"Proveedor seleccionado:\n"
            message += f"  Nombre: {selected['nombre']}\n"
            message += f"  RFC: {selected['rfc']}\n"
            message += f"  Teléfono: {selected['telefono']}\n"
            message += f"  Email: {selected['email']}"
        else:
            message = "No hay proveedor seleccionado"
        
        tb.dialogs.Messagebox.show_info(
            title="Selección de Proveedor",
            message=message,
            parent=self
        )
    
    def _show_tipo_selection(self):
        """Muestra la selección de tipo de vale."""
        selected = self.tipo_search.get_selected_item()
        if selected:
            message = f"Tipo de Vale seleccionado:\n"
            message += f"  Código: {selected['codigo']}\n"
            message += f"  Descripción: {selected['descripcion']}\n"
            message += f"  Categoría: {selected['categoria']}"
        else:
            message = "No hay tipo de vale seleccionado"
        
        tb.dialogs.Messagebox.show_info(
            title="Selección de Tipo de Vale",
            message=message,
            parent=self
        )
    
    def _show_all_selections(self):
        """Muestra todas las selecciones en el área de texto."""
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, END)
        
        # Proveedor
        proveedor = self.proveedor_search.get_selected_item()
        self.results_text.insert(END, "=== SELECCIONES ACTUALES ===\n\n")
        
        if proveedor:
            self.results_text.insert(END, "PROVEEDOR:\n")
            self.results_text.insert(END, f"  ID: {proveedor['id']}\n")
            self.results_text.insert(END, f"  Nombre: {proveedor['nombre']}\n")
            self.results_text.insert(END, f"  RFC: {proveedor['rfc']}\n")
            self.results_text.insert(END, f"  Teléfono: {proveedor['telefono']}\n")
            self.results_text.insert(END, f"  Email: {proveedor['email']}\n\n")
        else:
            self.results_text.insert(END, "PROVEEDOR: No seleccionado\n\n")
        
        # Tipo de Vale
        tipo = self.tipo_search.get_selected_item()
        if tipo:
            self.results_text.insert(END, "TIPO DE VALE:\n")
            self.results_text.insert(END, f"  Código: {tipo['codigo']}\n")
            self.results_text.insert(END, f"  Descripción: {tipo['descripcion']}\n")
            self.results_text.insert(END, f"  Categoría: {tipo['categoria']}\n\n")
        else:
            self.results_text.insert(END, "TIPO DE VALE: No seleccionado\n\n")
        
        self.results_text.config(state="disabled")
    
    def _clear_all(self):
        """Limpia todas las selecciones."""
        self.proveedor_search.clear()
        self.tipo_search.clear()
        
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, END)
        self.results_text.insert(END, "Todas las selecciones han sido limpiadas.")
        self.results_text.config(state="disabled")


def main():
    """Función principal para ejecutar el ejemplo."""
    try:
        root = tb.Window(themename="cosmo")
        root.title("Ejemplo de Componente de Búsqueda")
        root.geometry("800x700")
        
        app = SearchExampleApp(root)
        app.pack(fill="both", expand=True)
        
        root.mainloop()
        
    except Exception as e:
        print(f"Error ejecutando aplicación: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
