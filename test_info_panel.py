#!/usr/bin/env python3
"""
Test rápido del frame de información de vale (solo UI, sin insertar en BD).
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_info_panel():
    """
    Test rápido del panel de información de vale.
    """
    print("🧪 TEST PANEL DE INFORMACIÓN - VALE")
    print("=" * 50)
    
    try:
        import ttkbootstrap as ttk
        from src.buscarapp.views.info_panels_frame import InfoPanelsFrame
        
        # Crear ventana de test
        root = ttk.Window(themename="flatly")
        root.title("Test Panel Información Vale")
        root.geometry("800x400")
        
        # Crear frame de información
        info_frame = InfoPanelsFrame(root)
        
        # Datos de ejemplo para mostrar
        vale_data_ejemplo = {
            'noVale': 'V152266',
            'tipo': 'VCV',
            'total': '12,837.49',
            'proveedor': 'SERVICIOS GLOBALES ELYT SADECV',
            'fechaVale': '2025-07-18',
            'referencia': '8122661',
            'departamento': '6',
            'descripcion': 'MARKETING DE EXPERIENCIA (INCLUYE EMBAJADORES DE EXPERIENCIA MAS AMENIDADES) DE ACUERDO A CONTRATO C-23'
        }
        
        # Crear botón para probar la actualización
        def actualizar_info():
            info_frame.update_vale_info(vale_data_ejemplo)
            print("✅ Información del vale actualizada")
        
        def limpiar_info():
            info_frame._clear_vale_info()
            print("🧹 Información del vale limpiada")
        
        # Frame de botones de test
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=10)
        
        ttk.Button(
            button_frame,
            text="Mostrar Vale de Ejemplo",
            command=actualizar_info,
            bootstyle="primary"
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Limpiar Información",
            command=limpiar_info,
            bootstyle="secondary"
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Cerrar",
            command=root.destroy,
            bootstyle="danger"
        ).pack(side="left", padx=5)
        
        print("✅ Ventana de test creada")
        print("📋 Datos de ejemplo cargados:")
        for key, value in vale_data_ejemplo.items():
            valor_mostrar = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            print(f"   {key:15}: {valor_mostrar}")
        
        print("\n🎯 Usa los botones para probar la funcionalidad")
        print("   - 'Mostrar Vale de Ejemplo': Carga datos en el panel")
        print("   - 'Limpiar Información': Limpia todos los campos")
        print("   - 'Cerrar': Cierra la ventana de test")
        
        # Mostrar los datos automáticamente al inicio
        actualizar_info()
        
        # Iniciar la aplicación
        root.mainloop()
        
        print("✅ Test de panel completado")
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("   Verifica que ttkbootstrap esté instalado")
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_info_panel()
