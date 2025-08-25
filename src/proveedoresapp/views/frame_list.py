"""
TreeFrame - Componente de visualización tabular
===============================================

Marco que contiene una tabla (Treeview) para mostrar la lista de proveedores
con funcionalidades avanzadas de ordenamiento y selección.

Características:
- Tabla ordenable por cualquier columna (click en encabezados)
- Indicadores visuales de ordenamiento (↑ ↓)
- Scrollbar automático para listas grandes
- Selección de registros individuales
- Columnas redimensionables
- Ordenamiento inteligente (numérico vs alfabético)

Patrones implementados:
- State Pattern: Para estados de ordenamiento por columna
- Strategy Pattern: Para diferentes tipos de ordenamiento
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *

class TreeFrame:
    """
    Marco de visualización tabular para proveedores.
    
    Proporciona una tabla interactiva con capacidades avanzadas de ordenamiento,
    selección y visualización de datos de proveedores.
    
    Funcionalidades principales:
    - Ordenamiento bidireccional por cualquier columna
    - Persistencia del estado de ordenamiento
    - Indicadores visuales de dirección de ordenamiento
    - Manejo inteligente de tipos de datos (números vs texto)
    - Scrolling automático para datasets grandes
    
    Uso:
        tree = TreeFrame(parent_widget)
        tree.treeview.insert("", "end", values=("1", "ABC", "Proveedor"))
    """
    
    def __init__(self, master):
        """
        Inicializa el marco de tabla con configuración predeterminada.
        
        Args:
            master: Widget padre que contendrá este marco
        """
        self.master = master
        
        # Contenedor principal del componente
        self.frame = tb.Frame(master)
        self.frame.pack(side=TOP, fill=BOTH, expand=True, padx=30, pady=10)

        # Definir tamaños estándar para diferentes tipos de columnas
        c_smallest = 5      # Para IDs y datos muy cortos
        c_small = 10        # Para códigos y campos compactos
        c_medium = 50       # Para campos de longitud media
        c_large = 150       # Para nombres y texto largo

        # Configuración de columnas de la tabla
        # Formato: (nombre_campo, ancho_en_caracteres)
        self.column_names = (
            ("id", c_smallest),              # ID único del proveedor
            ("codigo", c_small),             # Código en sistema Quiter
            ("nombre", c_large),             # Nombre fiscal completo
            ("nombre_en_quiter", c_large),   # Nombre como aparece en Quiter
            ("rfc", c_small),                # RFC del proveedor
            ("telefono", c_small),           # Número telefónico
            ("email", c_small),              # Correo electrónico
            ("nombre_contacto", c_medium)    # Persona de contacto
        )

        # Diccionario para rastrear el estado de ordenamiento de cada columna
        # Key: nombre_columna, Value: bool (False=ascendente, True=descendente)
        self.sort_reverse = {}
        
        # Referencias a componentes que serán inicializados externamente
        # (Patrón de inyección de dependencias)
        self.button_add = None
        self.button_remove = None
        self.button_modify = None
        self.button_show = None

        # Widget Treeview principal
        self.treeview = None
        
        # Crear la interfaz visual
        self.create_tree()

    def create_tree(self):
        """
        Crea y configura el widget Treeview y sus componentes asociados.
        
        Inicializa:
        - Treeview con configuración de columnas
        - Headers con funcionalidad de ordenamiento
        - Scrollbar vertical automática
        - Event handlers para ordenamiento
        """
        # Crear Treeview sin mostrar el árbol (solo encabezados y filas)
        self.treeview = tb.Treeview(self.frame, show="headings", selectmode="browse")
        self.treeview.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Extraer solo los nombres de las columnas (sin los tamaños)
        column_names_only = [col for col, size in self.column_names]
        self.treeview["columns"] = column_names_only

        # Configurar cada columna con sus propiedades
        for col, size in self.column_names:
            # Inicializar el estado de ordenamiento (comenzar ascendente)
            self.sort_reverse[col] = False
            
            # Configurar encabezado con texto y comando de ordenamiento
            self.treeview.heading(
                col, 
                text=col.replace("_", " ").title(),  # Convertir "nombre_contacto" → "Nombre Contacto"
                command=lambda c=col: self.sort_by_column(c)  # Closure para capturar columna
            )
            
            # Configurar propiedades de la columna
            self.treeview.column(col, width=size, anchor="w")

        # Crear scrollbar vertical para listas grandes
        scrollbar = tb.Scrollbar(self.frame, orient=VERTICAL, command=self.treeview.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Conectar scrollbar con treeview
        self.treeview.config(yscroll=scrollbar.set)

    def sort_by_column(self, col):
        """
        Ordena los datos del treeview por la columna especificada.
        
        Implementa ordenamiento inteligente que:
        - Detecta el tipo de datos (numérico vs texto)
        - Alterna entre ascendente/descendente en clicks sucesivos
        - Muestra indicadores visuales de dirección
        - Maneja valores nulos/vacíos apropiadamente
        
        Args:
            col (str): Nombre de la columna por la cual ordenar
            
        Algoritmo:
        1. Obtener todos los elementos y sus valores para la columna
        2. Determinar tipo de ordenamiento (numérico/alfabético)
        3. Aplicar función de ordenamiento apropiada
        4. Reordenar elementos en el treeview
        5. Actualizar indicadores visuales
        6. Alternar estado para próximo click
        """
        try:
            # Obtener todos los elementos del treeview con sus valores
            data = [(self.treeview.set(k, col), k) for k in self.treeview.get_children("")]
            
            # Determinar si requiere ordenamiento numérico
            is_numeric = False
            if col in ['id', 'codigo']:  # Columnas que sabemos son numéricas
                is_numeric = True
            
            # Función de ordenamiento personalizada para manejo robusto
            def sort_key(item):
                """
                Genera clave de ordenamiento para un elemento.
                
                Maneja:
                - Valores None/vacíos
                - Conversión numérica con fallback
                - Normalización de texto (lowercase)
                
                Args:
                    item: Tupla (valor, id_elemento)
                    
                Returns:
                    Valor comparable para ordenamiento
                """
                value = item[0]
                
                # Manejar valores vacíos o None
                if value is None or value == '':
                    return '' if not is_numeric else 0
                
                if is_numeric:
                    # Intentar conversión numérica con fallback seguro
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        return 0  # Fallback para valores no numéricos
                else:
                    # Ordenamiento alfabético insensible a mayúsculas
                    return str(value).lower()
            
            # Obtener estado actual de ordenamiento para esta columna
            reverse = self.sort_reverse[col]
            
            # Aplicar ordenamiento con función personalizada
            data.sort(key=sort_key, reverse=reverse)
            
            # Reordenar elementos en el treeview según el nuevo orden
            for index, (val, k) in enumerate(data):
                self.treeview.move(k, '', index)
            
            # Alternar el estado para el próximo ordenamiento
            self.sort_reverse[col] = not reverse
            
            # Actualizar indicadores visuales en los encabezados
            self._update_sort_indicators(col, reverse)
            
        except Exception as e:
            # Log del error sin interrumpir la aplicación
            print(f"Error ordenando por columna {col}: {e}")

    def _update_sort_indicators(self, active_col, was_reverse):
        """
        Actualiza los indicadores visuales de ordenamiento en los encabezados.
        
        Comportamiento:
        - Limpia indicadores de otras columnas
        - Muestra ↑ o ↓ en la columna activa
        - Indica la dirección ACTUAL del ordenamiento
        
        Args:
            active_col (str): Columna que está siendo ordenada
            was_reverse (bool): Si el ordenamiento aplicado fue reverso
        """
        # Determinar símbolo indicador según la dirección aplicada
        sort_indicator = " ↓" if was_reverse else " ↑"
        column_title = active_col.replace("_", " ").title()
        
        # Limpiar indicadores de todas las columnas inactivas
        for other_col, _ in self.column_names:
            if other_col != active_col:
                # Restaurar título sin indicador
                other_title = other_col.replace("_", " ").title()
                self.treeview.heading(other_col, text=other_title)
        
        # Establecer indicador en la columna activa
        self.treeview.heading(active_col, text=column_title + sort_indicator)
