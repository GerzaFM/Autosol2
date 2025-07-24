#!/usr/bin/env python3
"""
Script para probar específicamente el formulario de nuevo usuario
"""

import sys
import os
from pathlib import Path

# Configurar rutas
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import ttkbootstrap as tb
from app.ui.views.user_admin import AdministradorUsuarios
from app.core.database import DatabaseManager

def probar_formulario_usuario():
    """Prueba el formulario de usuario de forma aislada."""
    print("🧪 Probando formulario de usuario...")
    
    # Crear ventana de prueba
    root = tb.Window(themename="darkly")
    root.title("Test - Formulario Usuario")
    root.geometry("1200x800")
    
    try:
        # Inicializar gestor de base de datos
        db_manager = DatabaseManager()
        print("✅ Base de datos inicializada")
        
        # Crear administrador de usuarios
        admin_usuarios = AdministradorUsuarios(root, db_manager)
        admin_usuarios.pack(fill=tb.BOTH, expand=True)
        
        # Inicializar datos
        admin_usuarios.inicializar()
        print("✅ AdministradorUsuarios inicializado")
        
        # Simular clic en "Nuevo Usuario"
        print("🖱️ Simulando clic en 'Nuevo Usuario'...")
        admin_usuarios._nuevo_usuario()
        
        # Verificar que las entradas estén visibles
        print("\n🔍 Verificando widgets del formulario:")
        widgets_formulario = [
            ("Username", admin_usuarios.entry_username),
            ("Nombre", admin_usuarios.entry_nombre),
            ("Email", admin_usuarios.entry_email),
            ("Password", admin_usuarios.entry_password),
            ("Empresa", admin_usuarios.entry_empresa),
            ("Centro", admin_usuarios.entry_centro),
            ("Sucursal", admin_usuarios.entry_sucursal),
            ("Marca", admin_usuarios.entry_marca),
            ("Permisos", admin_usuarios.combo_permisos),
            ("Estado", admin_usuarios.combo_estado),
        ]
        
        for nombre, widget in widgets_formulario:
            try:
                # Verificar si el widget existe y está visible
                visible = widget.winfo_viewable()
                mapped = widget.winfo_ismapped()
                parent = widget.winfo_parent()
                print(f"   - {nombre}: {'✅' if visible else '❌'} visible, {'✅' if mapped else '❌'} mapped, parent: {parent}")
                
                # Intentar obtener valor actual
                if hasattr(widget, 'get'):
                    valor = widget.get()
                    print(f"     Valor actual: '{valor}'")
                    
            except Exception as e:
                print(f"   - {nombre}: ❌ Error: {e}")
        
        print(f"\n📋 Estado del formulario:")
        print(f"   - Modo edición: {admin_usuarios.modo_edicion}")
        print(f"   - Usuario seleccionado: {admin_usuarios.selected_user}")
        print(f"   - Info label: {admin_usuarios.info_label.cget('text')}")
        
        # Ejecutar la ventana
        print("\n🚀 Iniciando ventana de prueba...")
        print("💡 Presiona el botón 'Nuevo Usuario' y verifica que aparezcan los campos")
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    probar_formulario_usuario()
