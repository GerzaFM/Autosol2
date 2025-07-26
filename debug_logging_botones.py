"""
Test con logging detallado para rastrear clicks de botones
"""
import sys
import os
import logging

# Configurar logging MUY detallado
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('debug_botones.log', mode='w')
    ]
)

# Agregar paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

def test_with_detailed_logging():
    """Test con logging súper detallado"""
    import ttkbootstrap as ttk
    
    root = ttk.Window("DEBUG - Logging Detallado de Botones", themename="litera")
    root.geometry("1000x700")
    
    try:
        logger = logging.getLogger("TEST_BOTONES")
        logger.info("🔍 INICIANDO TEST CON LOGGING DETALLADO")
        
        # Frame principal
        main_container = ttk.Frame(root, padding=10)
        main_container.pack(fill="both", expand=True)
        
        # Callbacks con logging súper detallado
        def _on_search(filters_dict):
            logger.info("🔍 ===== CALLBACK DE BÚSQUEDA EJECUTADO =====")
            logger.info(f"🔍 Filtros recibidos: {filters_dict}")
            print("🔍 BÚSQUEDA EJECUTADA EN CONSOLA")
            print(f"📋 Filtros: {filters_dict}")
            
        def _on_clear_search():
            logger.info("🧹 ===== CALLBACK DE LIMPIAR EJECUTADO =====")
            print("🧹 LIMPIAR EJECUTADO EN CONSOLA")
        
        # Crear SearchFrame
        logger.info("🏗️ Creando SearchFrame...")
        from buscarapp.views.search_frame import SearchFrame
        
        search_frame = SearchFrame(
            main_container,
            on_search_callback=_on_search,
            on_clear_callback=_on_clear_search
        )
        
        logger.info("✅ SearchFrame creado exitosamente")
        
        # Verificar comandos de botones
        if hasattr(search_frame, 'buscar_btn'):
            cmd = search_frame.buscar_btn['command']
            logger.info(f"📋 Comando del botón buscar: {cmd}")
            
        if hasattr(search_frame, 'limpiar_btn'):
            cmd = search_frame.limpiar_btn['command']
            logger.info(f"📋 Comando del botón limpiar: {cmd}")
        
        # Label de instrucciones muy visible
        instruction_frame = ttk.Frame(root, bootstyle="warning")
        instruction_frame.pack(side="bottom", fill="x", pady=10)
        
        ttk.Label(instruction_frame, 
                 text="🎯 PRESIONA LOS BOTONES DE BÚSQUEDA Y MIRA LA CONSOLA/LOG", 
                 font=("Arial", 12, "bold"),
                 bootstyle="warning").pack(pady=5)
        
        ttk.Label(instruction_frame, 
                 text="📝 Los logs se guardan en 'debug_botones.log'", 
                 font=("Arial", 10),
                 bootstyle="info").pack()
        
        logger.info("🎯 Aplicación lista - esperando interacción del usuario")
        print("\n" + "="*60)
        print("🎯 APLICACIÓN LISTA - PRESIONA LOS BOTONES DE BÚSQUEDA")
        print("📝 Logs se guardan en 'debug_botones.log'")
        print("="*60)
        
        root.mainloop()
        
        logger.info("🏁 Aplicación cerrada")
        
    except Exception as e:
        logger.error(f"❌ ERROR: {e}", exc_info=True)
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_detailed_logging()
