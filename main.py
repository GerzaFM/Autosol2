import ttkbootstrap as tb
from ttkbootstrap.constants import *
from gui_solicitud import SolicitudApp

class FormularioMaestroDesign(tb.Window):

    def __init__(self):
        super().__init__(themename="darkly")
        self.title('Python GUI')
        self.geometry("1024x850")
        self.resizable(True, True)
        self.sidebar_expanded = True
        self.paneles()
        self.controles_barra_superior()
        self.controles_menu_lateral()
        self.controles_cuerpo()

    def paneles(self):        
        self.barra_superior = tb.Frame(self, bootstyle="secondary", height=50)
        self.barra_superior.pack(side=TOP, fill='x')

        self.sidebar_width_expanded = 180
        self.sidebar_width_collapsed = 60
        self.menu_lateral = tb.Frame(self, bootstyle="dark", width=self.sidebar_width_expanded)
        self.menu_lateral.pack(side=LEFT, fill='y', expand=False) 

        self.cuerpo_principal = tb.Frame(self, bootstyle="dark")
        self.cuerpo_principal.pack(side=RIGHT, fill='both', expand=True)

    def controles_barra_superior(self):
        self.labelTitulo = tb.Label(self.barra_superior, text="TCM Matehuala", font=("Segoe UI", 15, "bold"), bootstyle="inverse-secondary")
        self.labelTitulo.pack(side=LEFT, padx=10, pady=10)

        self.labelInfo = tb.Label(self.barra_superior, text="Administración", font=("Segoe UI", 10), bootstyle="inverse-secondary")
        self.labelInfo.pack(side=RIGHT, padx=10, pady=10)
    
    def controles_menu_lateral(self):

        # Botón de colapsar/expandir en la parte superior del menú lateral
        self.buttonMenuLateral = tb.Button(
            self.menu_lateral, text="≡", width=3, bootstyle="secondary", command=self.toggle_panel
        )
        self.buttonMenuLateral.pack(side=TOP, padx=5, pady=10, anchor='w')

        # Botones principales (arriba)
        self.buttons_info_top = [
            ("Nueva", "📄"),
            ("Buscar", "🔍"),
            ("Pago", "💵"),
        ]
        # Botones inferiores (abajo)
        self.buttons_info_bottom = [
            ("Config", "⚙️"),
            ("Cuenta", "👤"),
        ]
        self.menu_buttons = []

        # Botones superiores
        for text, icon in self.buttons_info_top:
            btn = tb.Button(
                self.menu_lateral,
                text=f"{icon}   {text}",
                bootstyle="dark",
                width=20,
                command=lambda t=text: self.on_menu_click(t)
            )
            btn.pack(side=TOP, fill="x", pady=2)
            self.bind_hover_events(btn)
            self.menu_buttons.append((btn, icon, text))

        # Espaciador para empujar los botones de abajo
        self.spacer = tb.Label(self.menu_lateral, text="", bootstyle="dark")
        self.spacer.pack(side=TOP, fill="both", expand=True)

        # Botones inferiores
        for text, icon in self.buttons_info_bottom:
            btn = tb.Button(
                self.menu_lateral,
                text=f"{icon}   {text}",
                bootstyle="dark",
                width=20,
                command=lambda t=text: self.on_menu_click(t)
            )
            btn.pack(side=BOTTOM, fill="x", pady=2)
            self.bind_hover_events(btn)
            self.menu_buttons.append((btn, icon, text))

        self.set_sidebar_state(self.sidebar_expanded)

    def controles_cuerpo(self):
        label = tb.Label(self.cuerpo_principal, text="Cuerpo principal", font=("Segoe UI", 14), bootstyle="inverse-dark")
        label.place(x=0, y=0, relwidth=1, relheight=1)

    def bind_hover_events(self, button):
        button.bind("<Enter>", lambda event: button.config(bootstyle="success"))
        button.bind("<Leave>", lambda event: button.config(bootstyle="dark"))

    def toggle_panel(self):
        self.sidebar_expanded = not self.sidebar_expanded
        self.set_sidebar_state(self.sidebar_expanded)

    def set_sidebar_state(self, expanded):
        if expanded:
            self.menu_lateral.config(width=self.sidebar_width_expanded)
            for btn, icon, text in self.menu_buttons:
                btn.config(text=f"{icon}   {text:<21}", width=20)
        else:
            self.menu_lateral.config(width=self.sidebar_width_collapsed)
            for btn, icon, text in self.menu_buttons:
                btn.config(text=icon, width=4)
        self.menu_lateral.update_idletasks()

    def on_menu_click(self, name):
        self.toggle_panel()  # Colapsa el panel al hacer clic en un botón
        # Limpia el cuerpo principal antes de cargar un nuevo contenido

        for widget in self.cuerpo_principal.winfo_children():
            widget.destroy()
        if name == "Nueva":
            # Embebe la ventana de SolicitudApp en el frame cuerpo_principal
            solicitud = SolicitudApp(master=self.cuerpo_principal)
            solicitud.pack(fill="both", expand=True)
        else:
            tb.Label(
                self.cuerpo_principal,
                text=f"Seleccionado: {name}",
                font=("Segoe UI", 18),
                bootstyle="inverse-dark"
            ).pack(pady=40)

if __name__ == "__main__":
    app = FormularioMaestroDesign()
    app.mainloop()