import ttkbootstrap as tb
from ttkbootstrap.constants import *
import datetime

class SolicitudApp(tb.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self._build_ui()
        self.limpiar_todo()

    def _build_ui(self):
        # Frame superior
        frame_sup = tb.Frame(self)
        frame_sup.pack(fill=X, padx=15, pady=10)

        # Proveedor
        frame_prov = tb.Labelframe(frame_sup, text="Datos de proveedor", width=350)
        frame_prov.pack_propagate(False)
        frame_prov.pack(side=LEFT, fill=Y, expand=False, padx=(0,10), pady=0)
        for i, text in enumerate(["Nombre", "RFC", "Teléfono", "Correo", "Contacto"]):
            tb.Label(frame_prov, text=text+":").grid(row=i, column=0, sticky=E, padx=5, pady=4)
            tb.Entry(frame_prov, width=56, bootstyle="dark").grid(row=i, column=1, padx=5, pady=4)

        # Solicitud (alineado a la derecha)
        frame_sol = tb.Labelframe(frame_sup, text="Datos de la solicitud", width=320)
        frame_sol.pack_propagate(False)
        frame_sol.pack(side=RIGHT, fill=Y, expand=False, padx=(10,0), pady=0)
        for i, text in enumerate(["Fecha", "Clase", "Tipo", "Depa", "Folio"]):
            tb.Label(frame_sol, text=text+":").grid(row=i, column=0, sticky=E, padx=5, pady=4)
            if text == "Tipo":
                tb.Combobox(frame_sol, values=["Compra", "Servicio"], width=22, bootstyle="dark").grid(row=i, column=1, padx=5, pady=4, sticky=E)
            elif text == "Fecha":
                # Entrada de fecha con valor por defecto de hoy
                self.fecha_var = tb.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
                tb.DateEntry(
                    frame_sol,
                    width=19,
                    bootstyle="dark",
                    startdate=datetime.date.today()
                ).grid(row=i, column=1, padx=5, pady=4, sticky=E)
            else:
                tb.Entry(frame_sol, width=24, bootstyle="dark").grid(row=i, column=1, padx=5, pady=4, sticky=E)

        # Tabla productos/servicios
        frame_tabla = tb.Frame(self)
        frame_tabla.pack(fill=BOTH, expand=True, padx=15, pady=10)
        cols = ("Cantidad", "Descripción", "Precio", "Total")
        tree = tb.Treeview(frame_tabla, columns=cols, show="headings", height=6, bootstyle="dark")
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120 if col != "Descripción" else 340, anchor=W)
        tree.pack(fill=BOTH, expand=True)

        # Botones tabla
        frame_btn_tabla = tb.Frame(frame_tabla)
        frame_btn_tabla.pack(fill=X, padx=15, pady=10)
        btn_width = 6
        tb.Button(frame_btn_tabla, text="➕",  width=btn_width, command=self.place_holder).pack(side=RIGHT, padx=(0,5))
        tb.Button(frame_btn_tabla, text="➖ ", width=btn_width, command=self.place_holder).pack(side=RIGHT, padx=(0,5))
        tb.Button(frame_btn_tabla, text="✏️",  width=btn_width, command=self.place_holder).pack(side=RIGHT, padx=(0,5))
        
        # Frame inferior
        frame_inf = tb.Frame(self)
        frame_inf.pack(fill=X, padx=15, pady=10)

        # Categorías
        frame_cat = tb.Labelframe(frame_inf, text="Categorías", width=500)
        frame_cat.pack_propagate(False)
        frame_cat.pack(side=LEFT, fill=Y, expand=False, padx=(0,10))

        cat_labels = ["Comer", "Fleet", "Semis", "Refa", "Serv", "HyP", "Admin"]
        for col, text in enumerate(cat_labels):
            tb.Label(frame_cat, text=text).grid(row=0, column=col, padx=8, pady=(0,0), sticky="nw")
            tb.Entry(frame_cat, width=5, bootstyle="dark").grid(row=1, column=col, padx=8, pady=(0,0), sticky="new")

        # Frame para botones a la derecha de frame_cat
        frame_cat_btns = tb.Frame(frame_cat)
        frame_cat_btns.grid(row=0, column=len(cat_labels)+1, rowspan=3, padx=(16,0), pady=(0,6), sticky="ns")
        tb.Button(
            frame_cat_btns,
            text="Limpiar",
            bootstyle="warning",
            width=12
        ).pack(pady=(0,8), fill="x", padx=(0,5))
        tb.Button(
            frame_cat_btns,
            text="Guardar",
            bootstyle="warning",
            width=12
        ).pack(pady=(0,8), fill="x", padx=(0,5))

        # Frame Favoritos en la parte inferior de frame_cat (no es Labelframe)
        frame_fav = tb.Frame(frame_cat)
        frame_fav.grid(row=3, column=0, columnspan=len(cat_labels)+1, padx=8, pady=(10,0), sticky="ew")
        for i in range(5):
            tb.Button(
                frame_fav,
                text=f"Favorito {i+1}",
                bootstyle="info",
                width=10
            ).grid(row=0, column=i, padx=4, pady=6, sticky="s")
        frame_cat.grid_rowconfigure(3, weight=1)

        # Totales
        frame_tot = tb.Labelframe(frame_inf, text="Totales", width=320)
        frame_tot.pack_propagate(False)
        frame_tot.pack(side=RIGHT, fill=Y, expand=False, padx=(10,0))
        for i, text in enumerate(["Subtotal", "Ret", "IVA", "TOTAL"]):
            tb.Label(frame_tot, text=text).grid(row=i, column=0, sticky=E, padx=5, pady=4)
            tb.Entry(frame_tot, width=24, bootstyle="dark").grid(row=i, column=1, padx=5, pady=4)
        frame_tot.pack_propagate(False)

        # Comentarios
        tb.Label(self, text="Comentarios").pack(anchor=W, padx=18, pady=(10,0))
        comentarios = tb.Text(self, height=3)
        comentarios.pack(fill=X, padx=15, pady=5, expand=True)

        # Barra inferior
        frame_barra = tb.Frame(self)
        frame_barra.pack(fill=X, side=BOTTOM, padx=15, pady=10)
        tb.Label(frame_barra, text="Facturas restantes: 0").pack(side=LEFT, padx=2)
        tb.Button(frame_barra, text="Generar", bootstyle="success").pack(side=RIGHT, padx=5)
        tb.Button(frame_barra, text="Cargar XML", bootstyle="dark", command=self.cargar_xml).pack(side=RIGHT, padx=5)

        # Checkbox "Dividir" junto al botón "Cargar XML"
        self.dividir_var = tb.BooleanVar()
        tb.Checkbutton(
            frame_barra,
            text="Dividir",
            variable=self.dividir_var,
            bootstyle="dark"
        ).pack(side=RIGHT, padx=5)

    def limpiar_todo(self):
        # Borra todos los campos de entrada
        def limpiar_widget(widget):
            # Borrar Entry
            if isinstance(widget, tb.Entry):
                widget.delete(0, 'end')
            
            for child in widget.winfo_children():
                limpiar_widget(child)


    def place_holder(self):
        pass

    def cargar_xml(self):
        self.limpiar_todo()

    def limpiar_todo(self):
        """
        Borra el contenido de todos los Entry y Text hijos de este frame.
        """
        def limpiar_widget(widget):
            # Borra Entry
            if isinstance(widget, tb.Entry):
                widget.delete(0, "end")
            # Borra Text
            elif widget.winfo_class() == "Text":
                widget.delete("1.0", "end")
            # Busca recursivamente en los hijos
            for child in widget.winfo_children():
                limpiar_widget(child)

        limpiar_widget(self)

if __name__ == "__main__":

    app = SolicitudApp()
    app.mainloop()