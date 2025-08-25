import ttkbootstrap as tb
from ttkbootstrap.constants import *

class TreeFrame:
    def __init__(self, master):
        self.master = master
        self.frame = tb.Frame(master)
        self.frame.pack(side=TOP, fill=BOTH, expand=True, padx=30, pady=10)

        c_smallest = 5
        c_small = 10
        c_medium = 50
        c_large = 150

        self.column_names = (
            ("id", c_smallest),
            ("codigo", c_small),
            ("nombre", c_large),
            ("nombre_en_quiter", c_large),
            ("rfc", c_small),
            ("telefono", c_small),
            ("email", c_small),
            ("nombre_contacto", c_medium)
        )

        # Diccionario para rastrear el estado de ordenamiento de cada columna
        self.sort_reverse = {}
        
        self.button_add = None
        self.button_remove = None
        self.button_modify = None
        self.button_show = None

        self.treeview = None
        self.create_tree()

    def create_tree(self):
        self.treeview = tb.Treeview(self.frame, show="headings", selectmode="browse")
        self.treeview.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Extraer solo los nombres de las columnas (sin los tamaños)
        column_names_only = [col for col, size in self.column_names]
        self.treeview["columns"] = column_names_only

        for col, size in self.column_names:
            # Inicializar el estado de ordenamiento para cada columna
            self.sort_reverse[col] = False
            self.treeview.heading(col, text=col.replace("_", " ").title(),
                                  command=lambda c=col: self.sort_by_column(c))
            self.treeview.column(col, width=size, anchor="w")

        scrollbar = tb.Scrollbar(self.frame, orient=VERTICAL, command=self.treeview.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.treeview.config(yscroll=scrollbar.set)

    def sort_by_column(self, col):
        """Ordena los datos del treeview por la columna especificada."""
        try:
            # Obtener todos los elementos del treeview
            data = [(self.treeview.set(k, col), k) for k in self.treeview.get_children("")]
            
            # Determinar si es ordenamiento numérico o de texto
            is_numeric = False
            if col in ['id', 'codigo']:
                is_numeric = True
            
            # Función de ordenamiento personalizada
            def sort_key(item):
                value = item[0]
                if value is None or value == '':
                    return '' if not is_numeric else 0
                
                if is_numeric:
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        return 0
                else:
                    return str(value).lower()
            
            # Alternar dirección de ordenamiento
            reverse = self.sort_reverse[col]
            data.sort(key=sort_key, reverse=reverse)
            
            # Reordenar elementos en el treeview
            for index, (val, k) in enumerate(data):
                self.treeview.move(k, '', index)
            
            # Alternar el estado para el próximo ordenamiento
            self.sort_reverse[col] = not reverse
            
            # Actualizar el indicador visual en el encabezado
            sort_indicator = " ↓" if reverse else " ↑"
            column_title = col.replace("_", " ").title()
            
            # Limpiar indicadores de otras columnas
            for other_col, _ in self.column_names:
                if other_col != col:
                    other_title = other_col.replace("_", " ").title()
                    self.treeview.heading(other_col, text=other_title)
            
            # Establecer indicador en la columna actual
            self.treeview.heading(col, text=column_title + sort_indicator)
            
        except Exception as e:
            print(f"Error ordenando por columna {col}: {e}")
