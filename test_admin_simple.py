#!/usr/bin/env python3
"""
Script para probar una versión simplificada del AdministradorUsuarios
"""

import sys
import os
from pathlib import Path

# Configurar rutas
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import ttkbootstrap as tb
from app.core.database import DatabaseManager

class AdministradorUsuariosSimple(tb.Frame):
    """Versión simplificada del administrador de usuarios para debug."""
    
    def __init__(self, parent, db_manager, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.db_manager = db_manager
        self.pack(fill=tb.BOTH, expand=True)
        
        self._crear_interfaz()
    
    def _crear_interfaz(self):
        """Crea la interfaz simplificada."""
        # Header
        header = tb.Frame(self, padding=10)
        header.pack(fill=tb.X)
        
        title = tb.Label(
            header,
            text="👥 Administrador de Usuarios",
            font=("Segoe UI", 20, "bold")
        )
        title.pack(anchor=tb.W)
        
        # Botón nuevo usuario
        btn_nuevo = tb.Button(
            header,
            text="➕ Nuevo Usuario",
            bootstyle="success",
            command=self._nuevo_usuario
        )
        btn_nuevo.pack(anchor=tb.W, pady=10)
        
        # Formulario
        self.form_frame = tb.LabelFrame(
            self,
            text="👤 Datos del Usuario",
            padding=15
        )
        self.form_frame.pack(fill=tb.X, padx=10, pady=10)
        
        # Crear campos del formulario directamente
        self._crear_campos_formulario()
        
        # Label de estado
        self.estado_label = tb.Label(
            self,
            text="Presiona 'Nuevo Usuario' para comenzar",
            font=("Segoe UI", 10),
            bootstyle="inverse-secondary"
        )
        self.estado_label.pack(pady=10)
    
    def _crear_campos_formulario(self):
        """Crea los campos del formulario de forma simple."""
        # Fila 1
        fila1 = tb.Frame(self.form_frame)
        fila1.pack(fill=tb.X, pady=5)
        
        # Username
        username_frame = tb.Frame(fila1)
        username_frame.pack(side=tb.LEFT, fill=tb.X, expand=True, padx=(0, 10))
        tb.Label(username_frame, text="Username:").pack(anchor=tb.W)
        self.entry_username = tb.Entry(username_frame)
        self.entry_username.pack(fill=tb.X)
        
        # Nombre
        nombre_frame = tb.Frame(fila1)
        nombre_frame.pack(side=tb.LEFT, fill=tb.X, expand=True, padx=(0, 10))
        tb.Label(nombre_frame, text="Nombre:").pack(anchor=tb.W)
        self.entry_nombre = tb.Entry(nombre_frame)
        self.entry_nombre.pack(fill=tb.X)
        
        # Email
        email_frame = tb.Frame(fila1)
        email_frame.pack(side=tb.LEFT, fill=tb.X, expand=True)
        tb.Label(email_frame, text="Email:").pack(anchor=tb.W)
        self.entry_email = tb.Entry(email_frame)
        self.entry_email.pack(fill=tb.X)
        
        # Fila 2
        fila2 = tb.Frame(self.form_frame)
        fila2.pack(fill=tb.X, pady=5)
        
        # Password
        pass_frame = tb.Frame(fila2)
        pass_frame.pack(side=tb.LEFT, fill=tb.X, expand=True, padx=(0, 10))
        tb.Label(pass_frame, text="Contraseña:").pack(anchor=tb.W)
        self.entry_password = tb.Entry(pass_frame, show="*")
        self.entry_password.pack(fill=tb.X)
        
        # Empresa
        empresa_frame = tb.Frame(fila2)
        empresa_frame.pack(side=tb.LEFT, fill=tb.X, expand=True, padx=(0, 10))
        tb.Label(empresa_frame, text="Empresa:").pack(anchor=tb.W)
        self.entry_empresa = tb.Entry(empresa_frame)
        self.entry_empresa.pack(fill=tb.X)
        
        # Permisos
        permisos_frame = tb.Frame(fila2)
        permisos_frame.pack(side=tb.LEFT, fill=tb.X, expand=True)
        tb.Label(permisos_frame, text="Permisos:").pack(anchor=tb.W)
        self.combo_permisos = tb.Combobox(
            permisos_frame,
            values=["Administrador", "Usuario", "Supervisor"],
            state="readonly"
        )
        self.combo_permisos.pack(fill=tb.X)
        
        # Botones
        btn_frame = tb.Frame(self.form_frame)
        btn_frame.pack(fill=tb.X, pady=10)
        
        self.btn_guardar = tb.Button(
            btn_frame,
            text="💾 Guardar",
            bootstyle="success",
            command=self._guardar_usuario
        )
        self.btn_guardar.pack(side=tb.LEFT, padx=(0, 10))
        
        self.btn_limpiar = tb.Button(
            btn_frame,
            text="🧹 Limpiar",
            bootstyle="warning",
            command=self._limpiar_formulario
        )
        self.btn_limpiar.pack(side=tb.LEFT)
    
    def _nuevo_usuario(self):
        """Inicia el proceso de nuevo usuario."""
        self._limpiar_formulario()
        self.combo_permisos.set("Usuario")
        self.entry_empresa.insert(0, "1")
        self.entry_username.focus()
        self.estado_label.config(text="Creando nuevo usuario - Complete los campos")
        
        # Debug: verificar visibilidad
        print("🔍 Estado después de _nuevo_usuario:")
        widgets = [
            ("Username", self.entry_username),
            ("Nombre", self.entry_nombre),
            ("Email", self.entry_email),
            ("Password", self.entry_password),
            ("Empresa", self.entry_empresa),
            ("Permisos", self.combo_permisos)
        ]
        
        for nombre, widget in widgets:
            visible = widget.winfo_viewable()
            mapped = widget.winfo_ismapped()
            print(f"   - {nombre}: {'✅' if visible else '❌'} visible, {'✅' if mapped else '❌'} mapped")
    
    def _limpiar_formulario(self):
        """Limpia el formulario."""
        self.entry_username.delete(0, tb.END)
        self.entry_nombre.delete(0, tb.END)
        self.entry_email.delete(0, tb.END)
        self.entry_password.delete(0, tb.END)
        self.entry_empresa.delete(0, tb.END)
        self.combo_permisos.set("")
    
    def _guardar_usuario(self):
        """Guarda el usuario."""
        username = self.entry_username.get()
        nombre = self.entry_nombre.get()
        email = self.entry_email.get()
        
        if not username or not nombre:
            from tkinter import messagebox
            messagebox.showerror("Error", "Username y Nombre son obligatorios")
            return
        
        print(f"💾 Guardando usuario: {username} - {nombre} - {email}")
        self.estado_label.config(text=f"Usuario '{username}' guardado exitosamente")

def main():
    """Función principal."""
    print("🧪 Probando AdministradorUsuarios Simplificado...")
    
    root = tb.Window(themename="darkly")
    root.title("Test - Administrador Usuarios Simple")
    root.geometry("1200x600")
    
    try:
        db_manager = DatabaseManager()
        
        admin = AdministradorUsuariosSimple(root, db_manager)
        
        print("✅ AdministradorUsuarios simple creado")
        print("🚀 Abriendo ventana...")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
