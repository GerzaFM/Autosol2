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
            ("nombre_contacto", c_medium),
            ("cuenta_mayor", c_large)
        )

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
            self.treeview.heading(col, text=col.replace("_", " ").title(),
                                  command=lambda c=col: self.sort_by_column(c, False))
            self.treeview.column(col, width=size, anchor="w")

        scrollbar = tb.Scrollbar(self.frame, orient=VERTICAL, command=self.treeview.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.treeview.config(yscroll=scrollbar.set)

    def clear(self):
        self.treeview.delete(*self.treeview.get_children())

    def fill_data(self, data):
        self.clear()
        for item in data:
            self.treeview.insert("", "end", values=item)

    def get_selection(self):
        selected_item = self.treeview.selection()
        if selected_item:
            return self.treeview.item(selected_item, "values")
        return None
    
    def get_selected_id(self):
        selected_item = self.treeview.selection()
        if selected_item:
            item_id = int(self.treeview.item(selected_item, "values")[0])
            return item_id
        return None

    def add_item(self, item):
        self.treeview.insert("", "end", values=item)

    def remove_selected(self):
        selected_item = self.treeview.selection()
        if selected_item:
            self.treeview.delete(selected_item)

    def modify_selected(self, new_values):
        selected_item = self.treeview.selection()
        if selected_item:
            self.treeview.item(selected_item, values=new_values)

    def sort_by_column(self, col, reverse):
        data = [(self.treeview.set(k, col), k) for k in self.treeview.get_children("")]
        try:
            data.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            data.sort(key=lambda t: t[0], reverse=reverse)
        for index, (val, k) in enumerate(data):
            self.treeview.move(k, '', index)
        # Cambia el sentido de orden para la próxima vez
        self.treeview.heading(col, command=lambda: self.sort_by_column(col, not reverse))
