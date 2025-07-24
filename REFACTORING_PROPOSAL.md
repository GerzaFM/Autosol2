"""
Propuesta de Refactorización para buscar_app.py

PROBLEMA ACTUAL:
- Archivo de 1800+ líneas que mezcla UI y lógica de negocio
- Difícil de mantener y probar
- Viola el principio de responsabilidad única

PROPUESTA DE SEPARACIÓN:

1. CONTROLLERS (Lógica de Negocio):
   - search_controller.py: Maneja la lógica de búsqueda y filtros
   - invoice_controller.py: Maneja operaciones CRUD de facturas
   - export_controller.py: Maneja exportación y reimpresión
   
2. MODELS (Datos y Estado):
   - search_models.py: Modelos para filtros y estado de búsqueda
   - table_models.py: Modelo para datos de la tabla
   
3. VIEWS (Interfaz Gráfica):
   - search_frame.py: Frame de controles de búsqueda
   - table_frame.py: Frame de la tabla de resultados
   - action_buttons_frame.py: Frame de botones de acción
   - info_panels_frame.py: Frame de paneles informativos
   - main_window.py: Ventana principal que coordina todo
   
4. UTILS (Utilidades):
   - format_utils.py: Funciones de formateo
   - dialog_utils.py: Utilidades para diálogos

BENEFICIOS:
✅ Código más modular y mantenible
✅ Easier testing (se pueden probar controllers independientemente)
✅ Mejor separación de responsabilidades
✅ Reutilización de componentes
✅ Menos acoplamiento entre UI y lógica
✅ Archivos más pequeños y enfocados

ESTRUCTURA PROPUESTA:
src/buscarapp/
├── __init__.py
├── main_window.py          # Ventana principal (coordinador)
├── controllers/
│   ├── __init__.py
│   ├── search_controller.py
│   ├── invoice_controller.py
│   └── export_controller.py
├── models/
│   ├── __init__.py
│   ├── search_models.py
│   └── table_models.py
├── views/
│   ├── __init__.py
│   ├── search_frame.py
│   ├── table_frame.py
│   ├── action_buttons_frame.py
│   └── info_panels_frame.py
├── utils/
│   ├── __init__.py
│   ├── format_utils.py
│   └── dialog_utils.py
└── search_components.py    # Existente

¿Te parece bien esta estructura? ¿Empezamos con la refactorización?
"""
