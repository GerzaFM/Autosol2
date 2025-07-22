#!/usr/bin/env python3
"""
Script para diagnosticar en detalle el problema del administrador de usuarios
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

def diagnosticar_admin_usuarios():
    """Diagnóstico completo del AdministradorUsuarios."""
    print("🔍 Diagnóstico completo del AdministradorUsuarios")
    print("=" * 60)
    
    # Crear ventana de prueba
    root = tb.Window(themename="darkly")
    root.title("Diagnóstico - Administrador Usuarios")
    root.geometry("1400x900")
    
    try:
        # Inicializar base de datos
        db_manager = DatabaseManager()
        print("✅ Base de datos inicializada")
        
        # Crear administrador de usuarios
        admin_usuarios = AdministradorUsuarios(root, db_manager)
        admin_usuarios.pack(fill=tb.BOTH, expand=True)
        
        # Inicializar datos
        admin_usuarios.inicializar()
        print("✅ AdministradorUsuarios inicializado")
        
        def diagnosticar_estructura():
            print("\n🔍 Diagnóstico de estructura de widgets:")
            
            # Verificar estructura principal
            print(f"1. main_frame existe: {hasattr(admin_usuarios, 'main_frame')}")
            print(f"2. form_frame existe: {hasattr(admin_usuarios, 'form_frame')}")
            
            if hasattr(admin_usuarios, 'form_frame'):
                print(f"3. form_frame empaquetado: {admin_usuarios.form_frame.winfo_ismapped()}")
                print(f"4. form_frame visible: {admin_usuarios.form_frame.winfo_viewable()}")
                print(f"5. form_frame hijos: {len(admin_usuarios.form_frame.winfo_children())}")
                
                # Listar hijos del form_frame
                print("6. Hijos del form_frame:")
                for i, child in enumerate(admin_usuarios.form_frame.winfo_children()):
                    print(f"   - Hijo {i}: {child} ({child.__class__.__name__})")
                    print(f"     Empaquetado: {child.winfo_ismapped()}")
                    print(f"     Visible: {child.winfo_viewable()}")
                    
                    # Si es un frame, mostrar sus hijos también
                    if hasattr(child, 'winfo_children'):
                        children = child.winfo_children()
                        if children:
                            print(f"     Tiene {len(children)} hijos:")
                            for j, grandchild in enumerate(children):
                                print(f"       - {j}: {grandchild.__class__.__name__}")
                                print(f"         Visible: {grandchild.winfo_viewable()}")
                                if hasattr(grandchild, 'get'):
                                    try:
                                        valor = grandchild.get()
                                        print(f"         Valor: '{valor}'")
                                    except:
                                        pass
            
            # Verificar campos específicos
            campos_esperados = [
                'entry_username', 'entry_nombre', 'entry_email', 'entry_password',
                'entry_empresa', 'entry_centro', 'entry_sucursal', 'entry_marca',
                'combo_permisos', 'combo_estado', 'btn_guardar', 'btn_cancelar'
            ]
            
            print("\n7. Verificación de campos específicos:")
            for campo in campos_esperados:
                existe = hasattr(admin_usuarios, campo)
                print(f"   - {campo}: {'✅' if existe else '❌'} existe")
                
                if existe:
                    widget = getattr(admin_usuarios, campo)
                    visible = widget.winfo_viewable()
                    mapped = widget.winfo_ismapped()
                    parent = widget.winfo_parent()
                    print(f"     {'✅' if visible else '❌'} visible, {'✅' if mapped else '❌'} mapped")
                    print(f"     Padre: {parent}")
        
        def simular_nuevo_usuario():
            print("\n🖱️ Simulando clic en 'Nuevo Usuario'...")
            admin_usuarios._nuevo_usuario()
            
            print("Estado después de _nuevo_usuario:")
            if hasattr(admin_usuarios, 'entry_username'):
                print(f"   - Username: '{admin_usuarios.entry_username.get()}'")
            if hasattr(admin_usuarios, 'entry_empresa'):
                print(f"   - Empresa: '{admin_usuarios.entry_empresa.get()}'")
            if hasattr(admin_usuarios, 'combo_permisos'):
                print(f"   - Permisos: '{admin_usuarios.combo_permisos.get()}'")
        
        def forzar_actualizacion():
            print("\n🔄 Forzando actualización de widgets...")
            try:
                root.update_idletasks()
                root.update()
                print("✅ Actualización completada")
            except Exception as e:
                print(f"❌ Error en actualización: {e}")
        
        # Crear botones de diagnóstico
        debug_frame = tb.Frame(root)
        debug_frame.pack(side=tb.BOTTOM, fill=tb.X, padx=10, pady=5)
        
        tb.Button(
            debug_frame,
            text="🔍 Diagnosticar Estructura",
            bootstyle="info",
            command=diagnosticar_estructura
        ).pack(side=tb.LEFT, padx=5)
        
        tb.Button(
            debug_frame,
            text="🖱️ Simular Nuevo Usuario",
            bootstyle="success",
            command=simular_nuevo_usuario
        ).pack(side=tb.LEFT, padx=5)
        
        tb.Button(
            debug_frame,
            text="🔄 Forzar Actualización",
            bootstyle="warning",
            command=forzar_actualizacion
        ).pack(side=tb.LEFT, padx=5)
        
        # Ejecutar diagnóstico inicial después de mostrar la ventana
        root.after(1000, diagnosticar_estructura)
        root.after(2000, simular_nuevo_usuario)
        root.after(3000, forzar_actualizacion)
        root.after(4000, diagnosticar_estructura)
        
        print("🚀 Iniciando ventana de diagnóstico...")
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnosticar_admin_usuarios()
