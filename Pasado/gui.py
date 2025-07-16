import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from datetime import datetime
from xml_control import XML
from src.solicitudapp.form_control import Form
from comun import tipos_vale
from bd import Bd

class Main(tk.Tk):
    def __init__(self):
        super().__init__()
        # Tipos de vale, esta guardado en el archivo "comun.py" en un diccionario
        # Se llaman al inicio para ser desplegados en un ttk.Combobox
        self.vales_nombres = [f"{clave} - {valor}" for clave, valor in tipos_vale.items()]
        self.vales_nombres.sort()

        # Base de datos que guarda proveedores y su ultima factura ingresada al igual que sus datos de contaco
        self.bd = Bd()
        self.cola_xml = []

        # Se inicializa la Interfaz grafica
        self.config_window()
    
    def config_window(self):
        self.title("Nueva solicitud interna")
        w, h = 700, 605

        # Centrar ventana
        pantall_ancho = self.winfo_screenwidth()
        pantall_largo = self.winfo_screenheight()
        x = int((pantall_ancho/2)-(w/2))
        y = int((pantall_largo/2)-(h/2))

        self.geometry(f"{w}x{h}+{x}+{y}")

        # Cada frame vive en su propio metodo para facilitar acceso a cada elemento en la gui
        self.frame_datos()
        self.frame_conceptos()
        self.frame_totales()
        self.frame_comentarios()
        self.frame_acciones()

        ###-----------------------------------------------------------------------------###
        ###----------------------- Métodos de la Interfaz Grafica-----------------------###
        ###-----------------------------------------------------------------------------###

    def frame_datos(self):
        self.frm_datos = ttk.Frame(self)
        self.frm_datos.pack(side=tk.TOP, fill='both', expand=False)

        # Frame con los datos del receptor

        self.frm_receptor = ttk.LabelFrame(self.frm_datos, text="DATOS DE PROVEEDOR", padding=10)
        self.frm_receptor.pack(side=tk.LEFT, fill='both', expand=True)

        ttk.Label(self.frm_receptor, text="Nombre:").grid(row=0, column=0)
        self.entry_nombre = ttk.Entry(self.frm_receptor, width=40)
        self.entry_nombre.grid(row=0, column=1)

        ttk.Label(self.frm_receptor, text="Rfc:").grid(row=1, column=0)
        self.entry_rfc = ttk.Entry(self.frm_receptor, width=40)
        self.entry_rfc.grid(row=1, column=1)

        ttk.Label(self.frm_receptor, text="Telefono:").grid(row=2, column=0)
        self.entry_telefono = ttk.Entry(self.frm_receptor, width=40)
        self.entry_telefono.grid(row=2, column=1)

        ttk.Label(self.frm_receptor, text="Correo:").grid(row=3, column=0)
        self.entry_correo = ttk.Entry(self.frm_receptor, width=40)
        self.entry_correo.grid(row=3, column=1)

        ttk.Label(self.frm_receptor, text="Nombre de contacto:").grid(row=4, column=0)
        self.entry_contacto = ttk.Entry(self.frm_receptor, width=40)
        self.entry_contacto.grid(row=4, column=1)

        # Frame con los datos 

        self.frm_sol = ttk.LabelFrame(self.frm_datos, text="DATOS DE LA SOLICITUD", padding=10)
        self.frm_sol.pack(side=tk.RIGHT, fill='both', expand=True)

        ttk.Label(self.frm_sol, text="Fecha").grid(row=0, column=0)
        self.entry_fecha = ttk.Entry(self.frm_sol)
        self.entry_fecha.grid(row=0, column=1)

        ttk.Label(self.frm_sol, text="Folio").grid(row=1, column=0)
        self.entry_folio = ttk.Entry(self.frm_sol)
        self.entry_folio.grid(row=1, column=1)

        ttk.Label(self.frm_sol, text="Tipo").grid(row=2, column=0)
        self.entry_tipo = ttk.Combobox(self.frm_sol, values=self.vales_nombres)
        #self.entry_tipo = ttk.Entry(self.frm_sol)
        self.entry_tipo.grid(row=2, column=1)
        self.entry_tipo.bind("<FocusOut>", self.validar_entrada)
        self.entry_tipo.bind("<Return>", self.validar_entrada)

        ttk.Label(self.frm_sol, text="Departamento").grid(row=3, column=0)
        self.entry_departamento = ttk.Entry(self.frm_sol)
        self.entry_departamento.grid(row=3, column=1)
        self.entry_departamento.insert(0, "ADMINISTRACIÓN")

        ttk.Label(self.frm_sol, text="Factura").grid(row=4, column=0)
        self.entry_folio_factura = ttk.Entry(self.frm_sol)
        #self.entry_folio_factura.config(state="readonly")
        self.entry_folio_factura.grid(row=4, column=1)

    def frame_conceptos(self):
        self.frm_conceptos = ttk.Frame(self, padding=10)
        self.frm_conceptos.pack(side=tk.TOP, fill='both', expand=False)

        columnas = ("Cantidad", "Descripcion", "Precio", "Total")
        self.lst_conceptos = ttk.Treeview(self.frm_conceptos, columns=columnas, show="headings", height=5)

        for columna in columnas:
            self.lst_conceptos.heading(columna, text=columna)
            self.lst_conceptos.column(columna, anchor=tk.W, width=30)

        self.lst_conceptos.column("Descripcion", width=400)

        self.lst_conceptos.pack(fill='both', expand=True)

    def frame_totales(self):
        self.frm_ttl = ttk.Frame(self, padding=10)
        self.frm_ttl.pack(side=tk.TOP, fill='both', expand=False)

        # Porcentajes

        self.frm_porcentajes = ttk.Frame(self.frm_ttl, padding=10)
        self.frm_porcentajes.pack(side=tk.LEFT, fill='both', expand=False)

        ttk.Label(self.frm_porcentajes, text="Comercial").grid(row=0, column=0)
        self.entry_comercial = ttk.Entry(self.frm_porcentajes, width=10)
        self.entry_comercial.grid(row=0, column=1)

        ttk.Label(self.frm_porcentajes, text="Fleet Solutions").grid(row=1, column=0)
        self.entry_fleet = ttk.Entry(self.frm_porcentajes, width=10)
        self.entry_fleet.grid(row=1, column=1)

        ttk.Label(self.frm_porcentajes, text="Seminuevos").grid(row=2, column=0)
        self.entry_seminuevos = ttk.Entry(self.frm_porcentajes, width=10)
        self.entry_seminuevos.grid(row=2, column=1)

        ttk.Label(self.frm_porcentajes, text="Refacciones").grid(row=3, column=0)
        self.entry_refacciones = ttk.Entry(self.frm_porcentajes, width=10)
        self.entry_refacciones.grid(row=3, column=1)

        ttk.Label(self.frm_porcentajes, text="Servicio").grid(row=0, column=2)
        self.entry_servicio = ttk.Entry(self.frm_porcentajes, width=10)
        self.entry_servicio.grid(row=0, column=3)

        ttk.Label(self.frm_porcentajes, text="HYP").grid(row=1, column=2)
        self.entry_hyp = ttk.Entry(self.frm_porcentajes, width=10)
        self.entry_hyp.grid(row=1, column=3)

        ttk.Label(self.frm_porcentajes, text="Administración").grid(row=2, column=2)
        self.entry_admin = ttk.Entry(self.frm_porcentajes, width=10)
        self.entry_admin.grid(row=2, column=3)

        self.btn_limpiar_prorrateo = ttk.Button(self.frm_porcentajes, text="Limpiar", command=self.borrar_prorrateo)
        self.btn_limpiar_prorrateo.grid(row=4, column=3)

        # Total conceptos

        self.frm_total = ttk.Frame(self.frm_ttl, padding=10)
        self.frm_total.pack(side=tk.RIGHT, fill='both', expand=False)

        ttk.Label(self.frm_total, text="Subtotal").grid(row=0, column=0)
        self.entry_subtotal = ttk.Entry(self.frm_total, width=15, justify='right')
        self.entry_subtotal.grid(row=0, column=1)

        ttk.Label(self.frm_total, text="Retención").grid(row=1, column=0)
        self.entry_retencion = ttk.Entry(self.frm_total, width=15, justify='right')
        self.entry_retencion.grid(row=1, column=1)

        ttk.Label(self.frm_total, text="Iva").grid(row=2, column=0)
        self.entry_iva = ttk.Entry(self.frm_total, width=15, justify='right')
        self.entry_iva.grid(row=2, column=1)

        ttk.Label(self.frm_total, text="TOTAL").grid(row=3, column=0)
        self.entry_total = ttk.Entry(self.frm_total, width=15, justify='right')
        self.entry_total.grid(row=3, column=1)

    def frame_comentarios(self):
        self.frm_comentarios = ttk.LabelFrame(self, padding=10, text="Comentarios")
        self.frm_comentarios.pack(side=tk.TOP, fill='both', expand=False)

        self.txtb_comentarios = tk.Text(self.frm_comentarios, height=5)
        self.txtb_comentarios.pack()

    def frame_acciones(self):
        self.frm_acciones = ttk.Frame(self, padding=10)
        self.frm_acciones.pack(side=tk.BOTTOM, fill='both', expand=False)

        ttk.Label(self.frm_acciones, text="Facturas restates: ").pack(side=tk.LEFT)
        self.lbl_restantes = ttk.Label(self.frm_acciones, text=len(self.cola_xml))
        self.lbl_restantes.pack(side=tk.LEFT)

        self.btn_generar = ttk.Button(self.frm_acciones, text="Generar", command=self.generar)
        self.btn_generar.pack(side=tk.RIGHT)
 
        self.btn_cargar = ttk.Button(self.frm_acciones, text="Cargar XML", command=self.cargar_xml)
        self.btn_cargar.pack(side=tk.RIGHT)

    ###-----------------------------------------------------------------------------###
    ###-----------------------------------------------------------------------------###
    ###-----------------------------------------------------------------------------###

    def fecha(self):
        fecha_actual = datetime.now()
        return  fecha_actual.strftime("%d/%m/%y")
    
    def validar_entrada(self, event=None):
        # Este metodo es para el combobox del tipo de vale, sirve para poder escribir
        # La abreviatura y que el nombre completo se escriba automaticamente
        if self.entry_tipo.focus_get():
            tipo = self.entry_tipo.get().upper()

            if tipo in self.vales_nombres:
                return

            vales_value = list(tipos_vale.keys())
            if tipo not in vales_value:
                self.entry_tipo.delete(0, tk.END)
            else:
                self.entry_tipo.set(f"{tipo} - {tipos_vale[tipo]}")

            if event.keysym == 'Return':
                self.entry_departamento.focus_set()
            
    def borrar_prorrateo(self):
        # La accion del boton limpiar, borra el contenido en los campos de prorrateo
        # Nota: Guardar entrys en lista y borrar con ciclo for
        self.entry_comercial.delete(0, tk.END)
        self.entry_fleet.delete(0, tk.END)
        self.entry_seminuevos.delete(0, tk.END)
        self.entry_refacciones.delete(0, tk.END)
        self.entry_servicio.delete(0, tk.END)
        self.entry_hyp.delete(0, tk.END)
        self.entry_admin.delete(0, tk.END)

    def borrar_campos(self):
        # Borra todos los campos para donde se puede escribir
        self.entry_fecha.delete(0, tk.END)
        self.entry_nombre.delete(0, tk.END)
        self.entry_rfc.delete(0, tk.END)
        self.entry_folio_factura.delete(0, tk.END)
        self.entry_folio.delete(0,tk.END)
        self.entry_subtotal.delete(0, tk.END)
        self.entry_iva.delete(0, tk.END)
        self.entry_total.delete(0, tk.END)
        self.txtb_comentarios.delete("1.0", tk.END)

        self.entry_telefono.delete(0, tk.END)
        self.entry_correo.delete(0, tk.END)
        self.entry_contacto.delete(0, tk.END)
        self.entry_tipo.delete(0, tk.END)

        self.borrar_prorrateo()

        for item in self.lst_conceptos.get_children():
            self.lst_conceptos.delete(item)
        
        self.cantidades = ""
        self.descripciones = ""
        self.unitarios = ""
        self.totales = ""

    def cargar_xml(self):
        try:
            # Al cargar nuevos XML se borra la cola anterior
            self.cola_xml.clear()

            # Cuadro de dialogo para seleccionar los xml
            ruta = filedialog.askopenfilenames(
                title="Selecciona los archivos XML",
                filetypes=[("Archivos XML", "*.xml")]
            )

            # Si el usuario clickea en cancelar se sale de la función
            if not ruta:
                print("No se selecciono ningun archivo")
                return
            
            # Obtenemos las rutas de los XML y con ellas creamos objetos que contendran
            # La información de la factura, y las guardamos en la lista cola_xml
            # Para procesar varios XML con una sola carga
            for r in ruta:
                self.cola_xml.append(XML(r))

            # En la esquina inferior hay un label que indica las facturas restantes a ser procesadas
            # Lo actualizamos
            self.lbl_restantes.config(text=len(self.cola_xml))

            # Rellenamos los campos de la gui con la inforamcion de los objetos guardados en cola_xml
            self.rellenar_formulario(self.cola_xml[-1])

        except FileNotFoundError:
            print("Archivo no encontrado. Por favor, selecciona un archivo válido.")
        except Exception as e:
            print(f"Ocurrió un error al cargar el archivo XML: {e}")

    def rellenar_formulario(self, xml):

        # Borramos todos los campos para no duplicar datos al momento de rellenarlos
        self.borrar_campos()

        # Los objetos XML tienen los datos de cada factura asi que de ahi los obtenemos
        # Y rellenamos los campos correspondientes
        self.entry_fecha.insert(0, self.fecha())

        self.entry_nombre.insert(0, xml.nombre_emisor)
        self.entry_rfc.insert(0, xml.rfc_emisor)
        self.entry_folio_factura.insert(0, xml.folio)
        self.entry_subtotal.insert(0, xml.subtotal)
        self.entry_iva.insert(0, xml.iva)
        self.entry_total.insert(0, xml.total)
        self.txtb_comentarios.insert("1.0", f"Factura {xml.serie} {xml.folio}")
        
        self.cantidades = ""
        self.descripciones = ""
        self.unitarios = ""
        self.totales = ""

        for concepto in xml.conceptos:
            self.lst_conceptos.insert("", tk.END, values=concepto)

            self.cantidades += concepto[0]
            self.descripciones += concepto[1] + "\n"
            self.unitarios += concepto[2] + "\n"
            self.totales += concepto[3] + "\n"

        # Comprueba si el proveedor ya esta registrado en la BD y saca correo, telefono
        telefono = str(self.bd.obtener_dato(xml.rfc_emisor, 'telefono') or '')
        correo = str(self.bd.obtener_dato(xml.rfc_emisor, 'correo') or '')
        contacto = str(self.bd.obtener_dato(xml.rfc_emisor, 'contacto') or '')
        tipo_vale = str(self.bd.obtener_dato(xml.rfc_emisor, 'tipo') or '')
        p_comercial = str(self.bd.obtener_dato(xml.rfc_emisor, 'p_comercial') or '')
        p_fleet = str(self.bd.obtener_dato(xml.rfc_emisor, 'p_fleet') or '')
        p_seminuevos = str(self.bd.obtener_dato(xml.rfc_emisor, 'p_seminuevos') or '')
        p_refacciones = str(self.bd.obtener_dato(xml.rfc_emisor, 'p_refacciones') or '')
        p_servicio = str(self.bd.obtener_dato(xml.rfc_emisor, 'p_servicio') or '')
        p_hyp = str(self.bd.obtener_dato(xml.rfc_emisor, 'p_hyp') or '')
        p_admin = str(self.bd.obtener_dato(xml.rfc_emisor, 'p_admin') or '')

        # Inserta los datos en los campos de entrada
        self.entry_telefono.insert(0, telefono)
        self.entry_correo.insert(0, correo)
        self.entry_contacto.insert(0, contacto)
        self.entry_tipo.insert(0, tipo_vale)
        self.entry_comercial.insert(0, p_comercial)
        self.entry_fleet.insert(0, p_fleet)
        self.entry_seminuevos.insert(0, p_seminuevos)
        self.entry_refacciones.insert(0, p_refacciones)
        self.entry_servicio.insert(0, p_servicio)
        self.entry_hyp.insert(0, p_hyp)
        self.entry_admin.insert(0, p_admin)
        
    def generar(self):
        try:
            if not self.entry_rfc.get():
                print("Formulario sin rellenar")
                return
            
            folio = self.entry_folio.get()
            nombre = self.entry_nombre.get()
            factura = self.entry_folio_factura.get()

            ruta = filedialog.asksaveasfilename(
                title="Generar solicitud interna",
                filetypes=[("PDF", "*.pdf")],
                initialfile=f"{folio} {nombre} {factura}"
            )

            if not ruta:
                print("Exportacion cancelada")
                return 

            if not ruta.endswith(".pdf"):
                ruta += ".pdf"

            data = {
                "TIPO DE VALE": self.entry_tipo.get(),
                "C A N T I D A D": self.cantidades,
                "C O M E N T A R I O S": self.txtb_comentarios.get("1.0", tk.END),
                "Nombre de Empresa": self.entry_nombre.get(), 
                "RFC": self.entry_rfc.get(), 
                "Teléfono": self.entry_telefono.get(), 
                "Correo": self.entry_correo.get(), 
                "Nombre Contacto": self.entry_contacto.get(),
                "Menudeo": self.entry_comercial.get(), 
                "Seminuevos": self.entry_seminuevos.get(), 
                "Flotas": self.entry_fleet.get(),
                "Administración": self.entry_admin.get(),
                "Refacciones": self.entry_refacciones.get(),
                "Servicio": self.entry_servicio.get(),
                "HYP": self.entry_hyp.get(),
                "DESCRIPCIÓN": self.descripciones,
                "PRECIO UNITARIO": self.unitarios, 
                "TOTAL": self.totales,
                "FECHA GERENTE DE ÁREA": "", 
                "FECHA GERENTE ADMINISTRATIVO": "", 
                "FECHA DE AUTORIZACIÓN GG O DIRECTOR DE MARCA": "", 
                "SUBTOTAL": self.entry_subtotal.get(), 
                "IVA": self.entry_iva.get(), 
                "TOTAL, SUMATORIA": self.entry_total.get(), 
                "FECHA CREACIÓN SOLICITUD": self.entry_fecha.get(), 
                "FOLIO": self.entry_folio.get(), 
                "RETENCIÓN": self.entry_retencion.get(), 
                "Departamento": self.entry_departamento.get(),
                "folio_factura": folio
            }

            form = Form()
            form.rellenar(data, ruta)

            self.bd.insertar_o_actualizar(data)

            self.cola_xml.pop()
            self.lbl_restantes.config(text=len(self.cola_xml))

            if len(self.cola_xml):
                self.rellenar_formulario(self.cola_xml[-1])
            else:
                self.borrar_campos()

            #os.startfile(ruta)

        except FileNotFoundError:
            print("No se pudo abrir el cuadro de diálogo.")
        except Exception as e:
            print(f"Ocurrió un error al intentar guardar el archivo: {e}")


if __name__ == "__main__":
    root = Main()
    root.mainloop()