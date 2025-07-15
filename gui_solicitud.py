import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog
from logic_solicitud import SolicitudLogica
import datetime
import tkinter as tk  # Agrega esto al inicio si no lo tienes
import tkinter.messagebox as messagebox
from tkinter import simpledialog

class SolicitudApp(tb.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.solictudes_restantes = 0
        self.control = SolicitudLogica()
        self._build_ui()
        #self.limpiar_todo()

    def _build_ui(self):
        # Frame superior
        frame_sup = tb.Frame(self)
        frame_sup.pack(fill=X, padx=15, pady=10)

        # Proveedor
        frame_prov = tb.Labelframe(frame_sup, text="Datos de proveedor", width=350)
        frame_prov.pack_propagate(False)
        frame_prov.pack(side=LEFT, fill=Y, expand=False, padx=(0,10), pady=0)
        self.entries_prov = {}
        for i, text in enumerate(["Nombre", "RFC", "Teléfono", "Correo", "Contacto"]):
            tb.Label(frame_prov, text=text+":").grid(row=i, column=0, sticky=E, padx=5, pady=4)
            entry = tb.Entry(frame_prov, width=56, bootstyle="dark")
            entry.grid(row=i, column=1, padx=5, pady=4)
            self.entries_prov[text] = entry

        # Solicitud (alineado a la derecha)
        frame_sol = tb.Labelframe(frame_sup, text="Datos de la solicitud", width=320)
        frame_sol.pack_propagate(False)
        frame_sol.pack(side=RIGHT, fill=Y, expand=False, padx=(10,0), pady=0)
        self.entries_sol = {}
        for i, text in enumerate(["Fecha", "Clase", "Tipo", "Depa", "Folio"]):
            tb.Label(frame_sol, text=text+":").grid(row=i, column=0, sticky=E, padx=5, pady=4)
            if text == "Tipo":
                entry = tb.Combobox(frame_sol, values=["Compra", "Servicio"], width=22, bootstyle="dark")
                entry.grid(row=i, column=1, padx=5, pady=4, sticky=E)
            elif text == "Depa":
                entry = tb.Combobox(frame_sol, values=["Administración", "Ventas", "Servicio", "Refacciones", "HyP"], width=22, bootstyle="dark")
                entry.set("Administracion")  # Valor por defecto
                entry.grid(row=i, column=1, padx=5, pady=4, sticky=E)
            elif text == "Fecha":
                entry = tb.DateEntry(
                    frame_sol,
                    width=19,
                    bootstyle="dark",
                    startdate=datetime.date.today()
                )
                entry.grid(row=i, column=1, padx=5, pady=4, sticky=E)
            else:
                entry = tb.Entry(frame_sol, width=24, bootstyle="dark")
                entry.grid(row=i, column=1, padx=5, pady=4, sticky=E)
            self.entries_sol[text] = entry

        # Tabla productos/servicios
        frame_tabla = tb.Frame(self)
        frame_tabla.pack(fill=BOTH, expand=True, padx=15, pady=10)
        cols = ("Cantidad", "Descripción", "Precio", "Total")
        self.tree = tb.Treeview(frame_tabla, columns=cols, show="headings", height=6, bootstyle="dark")
        for col in cols:
            self.tree.heading(col, text=col)
            if col == "Cantidad":
                self.tree.column(col, width=80, anchor=W, stretch=False)
            elif col == "Descripción":
                self.tree.column(col, width=400, anchor=W, stretch=True)  # Esta columna se expande
            elif col == "Precio":
                self.tree.column(col, width=80, anchor=W, stretch=False)
            elif col == "Total":
                self.tree.column(col, width=80, anchor=W, stretch=False)
        self.tree.pack(fill=BOTH, expand=True)

        # Botones tabla
        frame_btn_tabla = tb.Frame(frame_tabla)
        frame_btn_tabla.pack(fill=X, padx=15, pady=10)
        btn_width = 6
        self.trebtn_agregar = tb.Button(
            frame_btn_tabla, text="➕", width=btn_width, command=self.agregar_concepto
        ).pack(side=RIGHT, padx=(0,5))
        self.trebtn_quitar = tb.Button(
            frame_btn_tabla,
            text="➖ ",
            width=btn_width,
            command=self.eliminar_concepto_seleccionado  # Cambia el comando aquí
        ).pack(side=RIGHT, padx=(0,5))
        self.trebtn_editar = tb.Button(
            frame_btn_tabla, text="✏️", width=btn_width, command=self.editar_concepto_seleccionado
        ).pack(side=RIGHT, padx=(0,5))
        
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

        # Frame Favoritos en la parte inferior de frame_cat
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
        self.entries_totales = {}
        for i, text in enumerate(["Subtotal", "Ret", "IVA", "TOTAL"]):
            tb.Label(frame_tot, text=text).grid(row=i, column=0, sticky=E, padx=5, pady=4)
            entry_tot = tb.Entry(frame_tot, width=24, bootstyle="dark")
            entry_tot.grid(row=i, column=1, padx=5, pady=4)
            self.entries_totales[text] = entry_tot
        frame_tot.pack_propagate(False)

        # Comentarios
        tb.Label(self, text="Comentarios").pack(anchor=W, padx=18, pady=(10,0))
        self.comentarios = tb.Text(self, height=3)
        self.comentarios.pack(fill=X, padx=15, pady=5, expand=True)

        # Barra inferior
        frame_barra = tb.Frame(self)
        frame_barra.pack(fill=X, side=BOTTOM, padx=15, pady=10)
        self.lbl_sol_rest = tb.Label(frame_barra, text=f"Solicitudes restantes: {self.solictudes_restantes}")
        self.lbl_sol_rest.pack(side=LEFT, padx=2)
        tb.Button(frame_barra, text="Generar", bootstyle="success", command=self.generar).pack(side=RIGHT, padx=5)
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
        rutas = filedialog.askopenfilenames(
            title="Selecciona los archivos XML",
            filetypes=[("Archivos XML", "*.xml")]
        )

        if not rutas:
            return
        
        self.limpiar_todo()
        self.control.agregar_solicitud(rutas)
        self.actualizar_solicitudes_restantes()

        self.rellenar_campo()

    def rellenar_campo(self):
        datos = self.control.get_solicitud()

        if not datos:
            return
        
        # Rellenar datos de proveedor
        self.entries_prov["Nombre"].insert(0, datos.nombre_emisor)
        self.entries_prov["RFC"].insert(0, datos.rfc_emisor)
        # Si tienes Teléfono, Correo, Contacto en el XML, agrégalos aquí

        # Rellenar datos de solicitud
        self.entries_sol["Folio"].insert(0, datos.folio)
        hoy = datetime.date.today()
        fecha_formateada = hoy.strftime("%d/%m/%Y")
        self.entries_sol["Fecha"].entry.delete(0, "end")
        self.entries_sol["Fecha"].entry.insert(0, fecha_formateada)
        # Si tienes Clase, Tipo, Depa en el XML, agrégalos aquí

        self.entries_totales["Subtotal"].insert(0, datos.subtotal)
        try:
            iva_ret = float(datos.iva_ret)
            isr_ret = float(datos.isr_ret)
            ret = str(iva_ret + isr_ret)
        except (ValueError, TypeError):
            ret = ""
        self.entries_totales["Ret"].insert(0, ret)
        self.entries_totales["IVA"].insert(0, datos.iva)
        self.entries_totales["TOTAL"].insert(0, datos.total)

        comentario = f"Factura: {datos.serie or ''} {datos.folio or ''}".strip()
        self.comentarios.delete("1.0", "end")
        self.comentarios.insert("1.0", comentario)

        self.rellenar_conceptos(datos.conceptos)

    def actualizar_solicitudes_restantes(self):
        self.solictudes_restantes = self.control.get_solicitudes_restantes()
        self.lbl_sol_rest.config(text=f"Solicitudes restantes: {self.solictudes_restantes}")

    def generar(self):
        pass

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

        self.lista_conceptos = []

    def rellenar_conceptos(self, conceptos):
        # Se limpia la tabla de conceptos
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Se instertan los concpetos en la tabla
        for concepto in conceptos:
            self.tree.insert("", "end", values=concepto)

        self.comprobar_numero_conceptos()

    def eliminar_concepto_seleccionado(self):
        """Elimina el concepto seleccionado en el Treeview."""
        selected = self.tree.selection()
        for item in selected:
            self.tree.delete(item)

    def popup_concepto(self, title, button_text, callback, valores_iniciales=None, entry_widths=None):
        """
        Muestra un formulario horizontal para agregar o editar un concepto.
        - title: Título de la ventana.
        - button_text: Texto del botón de acción.
        - callback: Función a llamar con los valores cuando se presiona el botón.
        - valores_iniciales: Lista de valores iniciales para los campos (opcional).
        - entry_widths: Diccionario con el ancho de cada campo (opcional).
        """
        popup = tk.Toplevel(self)
        popup.title(title)
        popup.geometry("720x120")
        popup.grab_set()

        labels = ["Cantidad", "Descripción", "Precio", "Total"]
        if entry_widths is None:
            entry_widths = {
                "Cantidad": 8,
                "Descripción": 70,
                "Precio": 12,
                "Total": 12
            }
        entries = {}

        for i, text in enumerate(labels):
            tk.Label(popup, text=text).grid(row=0, column=i, padx=10, pady=8, sticky="w")
            entry = tk.Entry(popup, width=entry_widths[text])
            entry.grid(row=1, column=i, padx=10, pady=8)
            if valores_iniciales and i < len(valores_iniciales):
                entry.insert(0, valores_iniciales[i])
            entries[text] = entry

        def on_ok():
            values = [entries[l].get() for l in labels]
            if not all(values):
                messagebox.showerror("Error", "Todos los campos son obligatorios.")
                return
            
            # Validar que Cantidad, Precio y Total sean números
            try:
                float(values[0])  # Cantidad
                float(values[2])  # Precio
                float(values[3])  # Total
            except ValueError:
                messagebox.showerror("Error", "Los campos Cantidad, Precio y Total deben ser números válidos.")
                return
            
            callback(values)
            popup.destroy()

        tk.Button(popup, text=button_text, command=on_ok).grid(row=2, column=0, columnspan=len(labels), pady=12)

    # Ahora puedes usar esta función para agregar o editar conceptos:

    def agregar_concepto(self):
        def insertar_concepto(values):
            self.tree.insert("", "end", values=values)
        self.popup_concepto("Agregar concepto", "Agregar", insertar_concepto)

    def editar_concepto_seleccionado(self):
        selected = self.tree.selection()
        if not selected:
            return
        item_id = selected[0]
        valores_actuales = self.tree.item(item_id, "values")
        def actualizar_concepto(values):
            self.tree.item(item_id, values=values)
        self.popup_concepto("Editar concepto", "Guardar", actualizar_concepto, valores_iniciales=valores_actuales)

    def comprobar_numero_conceptos(self):
        """
        Comprueba si hay más de 8 conceptos en la tabla.
        Si es así, muestra un popup preguntando si desea usar un concepto general.
        Si elige 'Sí', muestra un placeholder para el concepto general.
        """
        num_conceptos = len(self.tree.get_children())
        if num_conceptos > 8:
            respuesta = messagebox.askyesno(
                "Demasiados conceptos",
                "La lista de conceptos es demasiado larga.\n¿Prefiere usar un concepto general?"
            )
            if respuesta:
                self.agregar_concepto_general()

    def agregar_concepto_general(self):
        """
        Agrega un concepto general usando el formulario popup_concepto,
        con cantidad=1, precio=self.datos.subtotal y total=self.datos.total.
        """
        # Asegúrate de que self.datos existe y tiene los atributos necesarios
        descripcion = simpledialog.askstring(
            "Concepto general",
            "Escriba el concepto general que desea usar:"
        )
        if not descripcion:
            return
        
        datos = self.control.get_solicitud()
        if not datos:
            messagebox.showerror("Error", "No hay datos de solicitud disponibles.")
            return

        valores_iniciales = [
            "1",  # Cantidad
            descripcion,  # Descripción (lo que el usuario escribió)
            getattr(datos, "subtotal", ""),  # Precio
            getattr(datos, "total", "")      # Total
        ]

        def insertar_concepto(values):
            self.tree.insert("", "end", values=values)

        self.popup_concepto(
            "Agregar concepto general",
            "Agregar",
            insertar_concepto,
            valores_iniciales=valores_iniciales
        )
    

if __name__ == "__main__":

    app = tb.Window(themename="darkly")
    app.title("Solicitud de Compra")
    app.geometry("1024x850")
    frame = SolicitudApp(app)
    frame.pack(fill="both", expand=True)
    app.mainloop()