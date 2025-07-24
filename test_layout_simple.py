#!/usr/bin/env python3
"""
Script mínimo para probar solo el layout del formulario
"""

import sys
import os
from pathlib import Path

# Configurar rutas
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import ttkbootstrap as tb

def probar_layout_simple():
    """Prueba el layout con widgets simples para verificar visibilidad."""
    print("🧪 Probando layout simple...")
    
    # Crear ventana de prueba
    root = tb.Window(themename="darkly")
    root.title("Test - Layout Simple")
    root.geometry("1000x600")
    
    # Frame principal
    main_frame = tb.Frame(root, padding=20)
    main_frame.pack(fill=tb.BOTH, expand=True)
    
    # Frame del formulario
    form_frame = tb.LabelFrame(
        main_frame,
        text="👤 Datos del Usuario",
        padding=15
    )
    form_frame.pack(fill=tb.X, pady=(10, 0))
    
    # Primera fila: Username, Nombre, Email
    primera_fila = tb.Frame(form_frame)
    primera_fila.pack(fill=tb.X, pady=(0, 10))
    
    # Columna 1: Username
    col1_frame = tb.Frame(primera_fila)
    col1_frame.pack(side=tb.LEFT, fill=tb.X, expand=True, padx=(0, 10))
    lbl_username = tb.Label(col1_frame, text="Username:")
    lbl_username.pack(anchor=tb.W)
    entry_username = tb.Entry(col1_frame, width=20)
    entry_username.pack(fill=tb.X)
    
    # Columna 2: Nombre
    col2_frame = tb.Frame(primera_fila)
    col2_frame.pack(side=tb.LEFT, fill=tb.X, expand=True, padx=(0, 10))
    lbl_nombre = tb.Label(col2_frame, text="Nombre Completo:")
    lbl_nombre.pack(anchor=tb.W)
    entry_nombre = tb.Entry(col2_frame, width=25)
    entry_nombre.pack(fill=tb.X)
    
    # Columna 3: Email
    col3_frame = tb.Frame(primera_fila)
    col3_frame.pack(side=tb.LEFT, fill=tb.X, expand=True)
    lbl_email = tb.Label(col3_frame, text="Email:")
    lbl_email.pack(anchor=tb.W)
    entry_email = tb.Entry(col3_frame, width=25)
    entry_email.pack(fill=tb.X)
    
    # Botones de prueba
    btn_frame = tb.Frame(form_frame)
    btn_frame.pack(fill=tb.X, pady=10)
    
    def probar_widgets():
        print("🔍 Probando visibilidad de widgets:")
        widgets = [
            ("Username", entry_username),
            ("Nombre", entry_nombre), 
            ("Email", entry_email)
        ]
        
        for nombre, widget in widgets:
            visible = widget.winfo_viewable()
            mapped = widget.winfo_ismapped()
            print(f"   - {nombre}: {'✅' if visible else '❌'} visible, {'✅' if mapped else '❌'} mapped")
        
        # Agregar texto de prueba
        entry_username.delete(0, tb.END)
        entry_username.insert(0, "test_user")
        entry_nombre.delete(0, tb.END)
        entry_nombre.insert(0, "Usuario de Prueba")
        entry_email.delete(0, tb.END)
        entry_email.insert(0, "test@example.com")
        
        print("✅ Widgets llenados con datos de prueba")
    
    btn_probar = tb.Button(
        btn_frame,
        text="🧪 Probar Widgets",
        bootstyle="success",
        command=probar_widgets
    )
    btn_probar.pack(side=tb.LEFT, padx=(0, 10))
    
    print("✅ Layout creado exitosamente")
    print("🚀 Abriendo ventana...")
    
    # Ejecutar después de mostrar la ventana
    root.after(1000, probar_widgets)
    
    root.mainloop()

if __name__ == "__main__":
    probar_layout_simple()
