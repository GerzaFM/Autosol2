"""
Controller - Controlador principal de la aplicación de proveedores
=================================================================

Implementa el patrón MVC como coordinador central entre la Vista y el Modelo.
Maneja toda la lógica de presentación y coordina las interacciones del usuario
con las operaciones de negocio y persistencia de datos.

Arquitectura MVC implementada:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Model       │    │   Controller    │    │      View       │
│ ProveedorModel  │◄──►│   Controller    │◄──►│ ProveedoreView  │
│ (Base de datos) │    │ (Lógica coord.) │    │ (Interfaz GUI)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘

Responsabilidades principales:
- Coordinación entre Vista y Modelo (patrón MVC)
- Gestión de eventos de interfaz de usuario
- Implementación de lógica de presentación
- Validación de datos de entrada
- Manejo de estados de la aplicación (edición, visualización)
- Filtrado y búsqueda en tiempo real
- Gestión de ciclo de vida de operaciones CRUD

Patrones implementados:
- MVC Pattern: Separación clara de responsabilidades
- Observer Pattern: Manejo de eventos de UI (bindings, traces)
- Command Pattern: Cada botón/evento ejecuta un comando específico
- Strategy Pattern: Diferentes estrategias de filtrado y búsqueda
"""

from proveedoresapp.views.main_view import ProveedoreView
from proveedoresapp.models.model import ProveedorModel
import tkinter.messagebox as msgbox


class Controller:
    """
    Controlador principal que coordina la interacción entre Vista y Modelo.
    
    Actúa como intermediario inteligente que:
    - Recibe eventos de la interfaz de usuario
    - Procesa y valida la información
    - Coordina operaciones con el modelo
    - Actualiza la vista con los resultados
    
    Manejo de estado:
    - self.proveedores: Cache local de datos para filtrado rápido
    - Estados de edición: Controla cuándo el formulario es editable
    - Selecciones: Rastrea qué proveedor está seleccionado
    
    Eventos manejados:
    - Búsqueda en tiempo real (KeyRelease)
    - Toggle de filtros (Variable trace)
    - Selecciones de tabla (TreeviewSelect)
    - Clicks en botones (Command bindings)
    
    Flujo típico de operación:
    1. Usuario interactúa con la vista
    2. Vista genera evento
    3. Controller captura evento
    4. Controller procesa y valida
    5. Controller opera sobre modelo si necesario
    6. Controller actualiza vista con resultado
    """
    
    def __init__(self, model: ProveedorModel, view: ProveedoreView):
        """
        Inicializa el controlador y configura todos los bindings de eventos.
        
        Args:
            model: Instancia del modelo de proveedores para operaciones de BD
            view: Instancia de la vista principal para operaciones de UI
            
        Configuración realizada:
        - Referencias a modelo y vista
        - Cache de datos en memoria para filtrado rápido
        - Bindings de eventos de todos los componentes de UI
        - Estado inicial de la aplicación
        - Carga inicial de datos
        
        El constructor establece una red completa de comunicación bidireccional
        entre todos los componentes de la aplicación, asegurando que cada
        interacción del usuario sea adecuadamente procesada y reflejada.
        """
        # === REFERENCIAS PRINCIPALES ===
        # Almacenar referencias a los componentes MVC
        self.model = model      # Modelo: acceso a base de datos y lógica de negocio
        self.view = view        # Vista: interfaz de usuario y presentación

        # === CACHE DE DATOS ===
        # Cache local para operaciones de filtrado rápido sin hits a BD
        # Se actualiza cuando se cargan/modifican datos desde la base
        self.proveedores = []

        # === CONFIGURACIÓN DE EVENTOS DE BÚSQUEDA ===
        
        # Convertir botón de búsqueda en botón de refresh/reload
        # Permitir al usuario recargar datos desde BD cuando sea necesario
        self.view.search_frame.button_search.config(command=self.refresh_proveedores)
        
        # Búsqueda en tiempo real mientras el usuario escribe
        # Observer Pattern: Vista notifica cambios, Controller responde
        self.view.search_frame.search_bar.bind('<KeyRelease>', self._on_search_keyrelease)
        
        # Responder a cambios en el toggle de "mostrar incompletos"
        # Variable trace para reactividad automática del filtro
        self.view.search_frame.incomplete_var.trace('w', self._on_incomplete_toggle)

        # === CONFIGURACIÓN DE EVENTOS DE BOTONES PRINCIPALES ===
        # Command Pattern: Cada botón ejecuta una acción específica del controlador
        
        self.view.button_add.config(command=self.add_proveedor)           # Crear nuevo proveedor
        self.view.button_delete.config(command=self.delete_proveedor)     # Eliminar proveedor seleccionado
        self.view.button_edit.config(command=self.edit_proveedor)         # Editar proveedor seleccionado
        self.view.button_combine.config(command=self.combine_proveedor)   # Combinar proveedores (placeholder)

        # === CONFIGURACIÓN DE EVENTOS DEL FORMULARIO ===
        # Botones específicos del formulario de datos
        self.view.button_cancel.config(command=self.cancel_proveedor)     # Cancelar edición/creación
        self.view.button_save.config(command=self.save_proveedor)         # Guardar datos del formulario

        # === CONFIGURACIÓN DE EVENTOS DE SELECCIÓN ===
        # Observer Pattern: Responder a selecciones en la tabla
        # Permite acciones contextuales basadas en el elemento seleccionado
        self.view.tree_frame.treeview.bind('<<TreeviewSelect>>', self.on_proveedor_select)

        # === ESTADO INICIAL DE LA APLICACIÓN ===
        
        # Comenzar en modo solo lectura (formulario deshabilitado)
        # Se habilitará contextualmente cuando el usuario elija crear/editar
        self.view.set_editable(False)

        # Cargar datos iniciales desde la base de datos
        # Poblar la cache local y mostrar datos en la interfaz
        self.load_proveedores()
        self.fill_list(self.proveedores)

    # === MANEJADORES DE EVENTOS DE SELECCIÓN ===
    
    def on_proveedor_select(self, event):
        """
        Maneja la selección de un proveedor en la tabla.
        
        Args:
            event: Evento de selección del TreeView
            
        Comportamiento actual: No action (placeholder)
        
        Decisión de diseño:
        - NO llenar automáticamente el formulario al seleccionar
        - El formulario solo se llena al presionar "Editar"
        - Esto previene ediciones accidentales
        - Mejora la experiencia de usuario (menos cambios inesperados)
        
        Posibles extensiones futuras:
        - Mostrar información adicional en panel de detalles
        - Habilitar/deshabilitar botones según selección
        - Validar permisos para editar el proveedor seleccionado
        """
        # Ya no llenamos automáticamente el formulario al seleccionar
        # Solo se llenará cuando se presione el botón "Editar"
        pass

    # === OPERACIONES DE CARGA Y ACTUALIZACIÓN DE DATOS ===
    
    def load_proveedores(self):
        """
        Carga todos los proveedores desde la base de datos al cache local.
        
        Actualiza self.proveedores con los datos más recientes de la BD.
        Esta operación es el punto de sincronización entre la aplicación
        y el almacenamiento persistente.
        
        Cuándo se ejecuta:
        - Inicio de la aplicación
        - Después de operaciones CRUD (crear, actualizar, eliminar)
        - Cuando el usuario hace refresh explícito
        - Después de operaciones que pueden afectar múltiples registros
        
        Postcondición:
        - self.proveedores contiene todos los registros actuales
        - Cache está sincronizado con base de datos
        - Listo para operaciones de filtrado rápido
        """
        self.proveedores = self.model.obtener_todos()

    def fill_list(self, proveedores):
        """
        Actualiza la tabla de la vista con una lista específica de proveedores.
        
        Args:
            proveedores: Lista de diccionarios con datos de proveedores
        
        Transforma los datos del modelo (diccionarios) al formato requerido
        por la vista (listas de valores) y actualiza la tabla visual.
        
        Proceso:
        1. Convierte diccionarios a listas ordenadas de valores
        2. Delega a la vista la actualización visual de la tabla
        3. Mantiene la abstracción entre formatos de datos
        
        Esta separación permite:
        - Filtrar datos sin afectar la base de datos
        - Mostrar subconjuntos de datos según criterios
        - Mantener performance al evitar consultas BD repetitivas
        """
        table_data = [list(proveedor.values()) for proveedor in proveedores]
        self.view.fill_list(table_data)

    # === SISTEMA DE FILTRADO Y BÚSQUEDA ===
    
    def _on_search_keyrelease(self, event):
        """
        Responde a eventos de teclado en el campo de búsqueda.
        
        Args:
            event: Evento KeyRelease del widget de búsqueda
            
        Implementa búsqueda en tiempo real: cada tecla presionada
        dispara inmediatamente una nueva filtración de los datos.
        
        Observer Pattern: El campo de búsqueda notifica cambios,
        el controlador responde aplicando filtros actualizados.
        
        Performance: Usa cache local para evitar consultas BD repetitivas.
        """
        self.apply_filters()

    def _on_incomplete_toggle(self, *args):
        """
        Responde a cambios en el toggle de "mostrar solo incompletos".
        
        Args:
            *args: Argumentos del trace de tkinter (variable, índice, modo)
            
        Se ejecuta automáticamente cuando el usuario cambia el estado
        del checkbox "Mostrar solo incompletos".
        
        Variable Trace Pattern: La variable se auto-observa y ejecuta
        este callback cuando cambia, manteniendo la vista actualizada
        sin intervención manual del usuario.
        """
        self.apply_filters()

    def apply_filters(self):
        """
        Aplica todos los filtros activos sobre el cache de datos.
        
        Sistema de filtros en cadena:
        1. Inicia con todos los proveedores (self.proveedores)
        2. Aplica filtro de incompletos si está activado
        3. Aplica filtro de búsqueda textual si hay query
        4. Actualiza la vista con resultados filtrados
        
        Filtros implementados:
        - Incompletos: Proveedores sin nombre O sin nombre_en_quiter
        - Búsqueda textual: Coincidencia en múltiples campos
        
        Strategy Pattern: Diferentes estrategias de filtrado se combinan
        en una pipeline flexible y extensible.
        
        Performance: Opera sobre cache en memoria, no sobre BD.
        """
        # Obtener parámetros de filtrado desde la vista
        query = self.view.search_frame.search_bar.get_search_text().strip().lower()
        show_incomplete = self.view.search_frame.incomplete_var.get()
        
        # === PIPELINE DE FILTRADO ===
        # Comenzar con todos los datos disponibles
        proveedores_filtrados = self.proveedores.copy()
        
        # FILTRO 1: Proveedores incompletos (si está activado)
        if show_incomplete:
            proveedores_filtrados = [
                proveedor for proveedor in proveedores_filtrados
                if self._is_proveedor_incomplete(proveedor)
            ]
        
        # FILTRO 2: Búsqueda textual (si hay query)
        if query:
            proveedores_con_busqueda = []
            for proveedor in proveedores_filtrados:
                # Campos incluidos en la búsqueda textual
                # Búsqueda multi-campo para máxima flexibilidad
                campos_busqueda = [
                    str(proveedor.get('nombre', '')).lower(),
                    str(proveedor.get('codigo_quiter', '')).lower(),
                    str(proveedor.get('rfc', '')).lower(),
                    str(proveedor.get('nombre_en_quiter', '')).lower(),
                    str(proveedor.get('email', '')).lower(),
                ]
                
                # Incluir si el query aparece en cualquiera de los campos
                # Búsqueda por substring (contiene) en lugar de exact match
                if any(query in campo for campo in campos_busqueda):
                    proveedores_con_busqueda.append(proveedor)
            
            proveedores_filtrados = proveedores_con_busqueda
        
        # === ACTUALIZACIÓN DE LA VISTA ===
        # Mostrar resultados filtrados en la tabla
        self.fill_list(proveedores_filtrados)

    def _is_proveedor_incomplete(self, proveedor):
        """
        Determina si un proveedor está incompleto según criterios de negocio.
        
        Args:
            proveedor: Diccionario con datos del proveedor
            
        Returns:
            bool: True si el proveedor está incompleto, False si está completo
            
        Criterios de incompletitud:
        - No tiene nombre (campo vacío o None)
        - No tiene nombre_en_quiter (campo vacío o None)
        
        Lógica de negocio: Un proveedor es útil solo si tiene ambos nombres
        definidos. Esta función encapsula esa regla para fácil mantenimiento
        y posible extensión futura con criterios adicionales.
        
        Extensibilidad: Fácil agregar más criterios (RFC, email, etc.)
        """
        nombre = proveedor.get('nombre', '').strip()
        nombre_en_quiter = proveedor.get('nombre_en_quiter', '').strip()
        
        # Es incompleto si no tiene nombre O no tiene nombre_en_quiter
        # Lógica OR: Falta cualquiera de los dos campos críticos
        return not nombre or not nombre_en_quiter

    # === OPERACIONES DE DATOS ===
    
    def refresh_proveedores(self):
        """
        Recarga todos los datos desde la base de datos y actualiza la vista.
        
        Operación de sincronización completa que:
        1. Limpia el campo de búsqueda (reset de UI)
        2. Recarga datos desde BD (actualiza cache)
        3. Reaplica filtros actuales (mantiene estado de filtros)
        
        Cuándo usarlo:
        - Usuario presiona botón "Refresh"
        - Después de operaciones que pueden afectar múltiples registros
        - Para sincronizar con cambios externos a la aplicación
        - Recuperación de errores de estado inconsistente
        
        Comportamiento inteligente:
        - Respeta el estado del toggle de incompletos
        - Limpia la búsqueda textual para mostrar resultados amplios
        - Mantiene selecciones si es posible
        """
        # Limpiar el searchbar (reset de UI)
        self.view.search_frame.search_bar.clear_search()
        # Recargar datos desde la base de datos
        self.load_proveedores()
        # Aplicar filtros actuales (respeta el toggle incompletos)
        self.apply_filters()

    def search_proveedor(self):
        """
        Realiza búsqueda usando el sistema de filtros integrado.
        
        DEPRECATED: Esta función es legacy y redirige a apply_filters().
        
        Mantenida por compatibilidad, pero la funcionalidad real
        está implementada en apply_filters() que se ejecuta automáticamente
        con la búsqueda en tiempo real.
        
        Futuro: Considerar eliminación en refactoring posterior.
        """
        self.apply_filters()
    
    # === OPERACIONES CRUD ===
    
    def add_proveedor(self):
        """
        Habilita el formulario para crear un nuevo proveedor.
        
        Transición de estado: Modo visualización → Modo creación
        
        Acciones realizadas:
        1. Limpiar formulario (remover datos previos)
        2. Habilitar edición de campos
        3. Establecer foco en primer campo para UX fluida
        
        Estado resultante:
        - Formulario limpio y editable
        - Usuario puede ingresar datos inmediatamente
        - Campos validarán al guardar
        - Botones Save/Cancel activos
        
        UX Pattern: Preparar interfaz para entrada de datos nueva
        """
        # Limpiar el formulario de cualquier dato previo
        self.view.clear_form()
        # Habilitar edición de todos los campos
        self.view.set_editable(True)
        # Foco en el primer campo para UX fluida
        if 'codigo' in self.view.entries:
            self.view.entries['codigo'].focus_set()

    def delete_proveedor(self):
        """
        Elimina el proveedor seleccionado con confirmación del usuario.
        
        Proceso de eliminación segura:
        1. Validar que hay selección activa
        2. Mostrar datos del proveedor a eliminar
        3. Solicitar confirmación explícita del usuario
        4. Ejecutar eliminación en base de datos
        5. Actualizar vista según resultado
        
        Protecciones implementadas:
        - Validación de selección antes de proceder
        - Confirmación explícita con datos del proveedor
        - Manejo de errores de BD con mensajes descriptivos
        - Actualización de vista solo si operación fue exitosa
        
        UX Consideraciones:
        - Operación irreversible claramente comunicada
        - Información suficiente para decisión informada
        - Feedback inmediato del resultado
        """
        # === VALIDACIÓN DE PRECONDICIONES ===
        selected_id = self.view.get_selected_id()
        if not selected_id:
            msgbox.showwarning("Advertencia", "Selecciona un proveedor para eliminar")
            return
        
        # === PREPARACIÓN DE INFORMACIÓN PARA CONFIRMACIÓN ===
        # Obtener información del proveedor para mostrar en confirmación
        selection = self.view.get_selection()
        proveedor_nombre = selection[2] if len(selection) > 2 else "Sin nombre"  # Asumiendo que el nombre está en la posición 2
        
        # === SOLICITUD DE CONFIRMACIÓN ===
        if msgbox.askyesno("Confirmar eliminación", 
                          f"¿Estás seguro de eliminar el proveedor:\n{proveedor_nombre}?"):
            
            # === EJECUCIÓN DE ELIMINACIÓN ===
            exito, mensaje = self.model.eliminar_proveedor(selected_id)
            
            if exito:
                # === POST-PROCESAMIENTO EXITOSO ===
                msgbox.showinfo("Éxito", mensaje)
                # Recargar la lista con datos actualizados
                self.load_proveedores()
                self.apply_filters()
                # Limpiar formulario (puede haber datos del proveedor eliminado)
                self.view.clear_form()
            else:
                # === MANEJO DE ERRORES ===
                msgbox.showerror("Error", f"No se pudo eliminar el proveedor:\n{mensaje}")

    def edit_proveedor(self):
        """
        Habilita la edición del proveedor seleccionado.
        
        Transición de estado: Modo visualización → Modo edición
        
        Flujo de edición:
        1. Validar que hay proveedor seleccionado
        2. Habilitar edición en formulario
        3. Cargar datos completos del proveedor
        4. Poblar formulario con datos actuales
        5. Usuario puede modificar y guardar
        
        Orden importante: Habilitar edición ANTES de llenar formulario
        para asegurar que los campos son editables cuando reciben datos.
        
        Manejo de errores:
        - Valida selección antes de proceder
        - Maneja casos de datos no encontrados en BD
        - Proporciona feedback claro en caso de error
        """
        # === VALIDACIÓN DE PRECONDICIONES ===
        selected_id = self.view.get_selected_id()
        if not selected_id:
            msgbox.showwarning("Advertencia", "Selecciona un proveedor para editar")
            return
        
        # === HABILITACIÓN DE EDICIÓN ===
        # CRÍTICO: Habilitar edición ANTES de llenar el formulario
        # Los campos deben ser editables para recibir datos correctamente
        self.view.set_editable(True)
        
        # === OBTENCIÓN DE DATOS COMPLETOS ===
        # Obtener datos completos del proveedor desde la base de datos
        # No confiar en los datos de la vista (pueden estar filtrados/parciales)
        proveedor_data = self.model.obtener_por_id(selected_id)
        if not proveedor_data:
            msgbox.showerror("Error", "No se pudo obtener la información del proveedor")
            return
        
        # === MAPEO Y POBLACIÓN DEL FORMULARIO ===
        # Mapear campos del modelo a campos del formulario
        # Manejar diferencias en nombres de campos entre capas
        form_data = {
            'codigo': str(proveedor_data.get('codigo_quiter', '')),
            'nombre': proveedor_data.get('nombre', ''),
            'email': proveedor_data.get('email', ''),
            'nombre_contacto': proveedor_data.get('nombre_contacto', ''),
            'rfc': proveedor_data.get('rfc', ''),
            'nombre_quiter': proveedor_data.get('nombre_en_quiter', ''),
            'telefono': proveedor_data.get('telefono', '')
        }
        
        # Llenar formulario con datos mapeados
        self.view.fill_form(form_data)

    def save_proveedor(self):
        """
        Guarda el proveedor actual (nuevo o editado) en la base de datos.
        
        Operación dual: Crear nuevo O actualizar existente
        
        Flujo de guardado:
        1. Obtener datos del formulario
        2. Validar datos básicos (campos requeridos)
        3. Mapear datos del formulario al formato del modelo
        4. Determinar si es creación o edición
        5. Ejecutar operación correspondiente en BD
        6. Actualizar vista según resultado
        7. Retornar al modo visualización si exitoso
        
        Validaciones implementadas:
        - Código es campo requerido
        - Datos son limpiados (strip whitespace)
        - Mapeo correcto entre capas
        
        Estados manejados:
        - selected_id existe → Edición de proveedor existente
        - selected_id None → Creación de nuevo proveedor
        """
        # === OBTENCIÓN Y VALIDACIÓN DE DATOS ===
        form_data = self.view.get_form_data()
        
        # Validación básica de campos requeridos
        if not form_data.get('codigo', '').strip():
            msgbox.showwarning("Advertencia", "El código es requerido")
            return
        
        # === PREPARACIÓN DE DATOS PARA EL MODELO ===
        # Mapear y limpiar datos del formulario al formato del modelo
        # Manejar diferencias en nombres de campos entre capas
        datos_proveedor = {
            'codigo_quiter': form_data.get('codigo', '').strip(),
            'nombre': form_data.get('nombre', '').strip(),
            'nombre_en_quiter': form_data.get('nombre_quiter', '').strip(),
            'rfc': form_data.get('rfc', '').strip(),
            'telefono': form_data.get('telefono', '').strip(),
            'email': form_data.get('email', '').strip(),
            'nombre_contacto': form_data.get('nombre_contacto', '').strip()
        }
        
        # === DETERMINACIÓN DE OPERACIÓN ===
        # Decidir si es creación o edición basado en selección actual
        selected_id = self.view.get_selected_id()
        
        if selected_id:
            # === EDICIÓN DE PROVEEDOR EXISTENTE ===
            exito, mensaje = self.model.actualizar_proveedor(selected_id, datos_proveedor)
        else:
            # === CREACIÓN DE NUEVO PROVEEDOR ===
            exito, mensaje, nuevo_id = self.model.crear_proveedor(datos_proveedor)
        
        # === POST-PROCESAMIENTO ===
        if exito:
            # === OPERACIÓN EXITOSA ===
            msgbox.showinfo("Éxito", mensaje)
            # Recargar datos para reflejar cambios
            self.load_proveedores()
            self.apply_filters()
            # Retornar al modo visualización
            self.view.clear_form()
            self.view.set_editable(False)
        else:
            # === MANEJO DE ERRORES ===
            msgbox.showerror("Error", f"No se pudo guardar el proveedor:\n{mensaje}")

    def cancel_proveedor(self):
        """
        Cancela la operación de edición/creación actual.
        
        Transición de estado: Modo edición → Modo visualización
        
        Acciones de cancelación:
        1. Limpiar formulario (descartar cambios no guardados)
        2. Deshabilitar edición (volver a modo solo lectura)
        3. No actualizar datos (cambios se pierden)
        
        UX Considerations:
        - Operación segura (no afecta datos persistidos)
        - Permite al usuario salir de edición sin comprometer datos
        - Formulario limpio listo para próxima operación
        
        Decisión de diseño: NO llenar automáticamente el formulario
        al cancelar, manteniendo estado limpio para próxima acción.
        """
        # Limpiar formulario (descartar cambios no guardados)
        self.view.clear_form()
        # Deshabilitar edición (volver a solo lectura)
        self.view.set_editable(False)
        # Ya no llenamos automáticamente el formulario al cancelar

    def combine_proveedor(self):
        """
        Combina proveedores duplicados (funcionalidad pendiente).
        
        PLACEHOLDER: Funcionalidad no implementada actualmente.
        
        Comportamiento actual:
        - Deshabilita edición del formulario
        - No realiza operación de combinación
        
        Funcionalidad futura prevista:
        - Detectar proveedores duplicados/similares
        - Permitir al usuario seleccionar múltiples proveedores
        - Fusionar información en un solo registro
        - Eliminar duplicados después de fusión
        - Mantener historial de cambios
        
        Consideraciones de implementación:
        - Algoritmos de detección de duplicados
        - UI para selección múltiple
        - Lógica de fusión de datos conflictivos
        - Validaciones de integridad referencial
        """
        self.view.set_editable(False)
        pass  # Funcionalidad no implementada

    def _on_search_keyrelease(self, event):
        """Búsqueda en tiempo real mientras el usuario escribe."""
        self.apply_filters()

    def _on_incomplete_toggle(self, *args):
        """Maneja el cambio del toggle de incompletos."""
        self.apply_filters()

    def apply_filters(self):
        """Aplica todos los filtros activos (búsqueda + incompletos)."""
        # Obtener el texto de búsqueda del searchbar
        query = self.view.search_frame.search_bar.get_search_text().strip().lower()
        # Obtener el estado del toggle incompletos
        show_incomplete = self.view.search_frame.incomplete_var.get()
        
        # Comenzar con todos los proveedores
        proveedores_filtrados = self.proveedores.copy()
        
        # Aplicar filtro de incompletos si está activado
        if show_incomplete:
            proveedores_filtrados = [
                proveedor for proveedor in proveedores_filtrados
                if self._is_proveedor_incomplete(proveedor)
            ]
        
        # Aplicar filtro de búsqueda si hay texto
        if query:
            proveedores_con_busqueda = []
            for proveedor in proveedores_filtrados:
                # Buscar en múltiples campos del proveedor
                campos_busqueda = [
                    str(proveedor.get('nombre', '')).lower(),
                    str(proveedor.get('codigo_quiter', '')).lower(),
                    str(proveedor.get('rfc', '')).lower(),
                    str(proveedor.get('nombre_en_quiter', '')).lower(),
                    str(proveedor.get('email', '')).lower(),
                ]
                
                # Si el query aparece en alguno de los campos, incluir el proveedor
                if any(query in campo for campo in campos_busqueda):
                    proveedores_con_busqueda.append(proveedor)
            
            proveedores_filtrados = proveedores_con_busqueda
        
        # Actualizar la lista con los resultados filtrados
        self.fill_list(proveedores_filtrados)

    def _is_proveedor_incomplete(self, proveedor):
        """Determina si un proveedor está incompleto (sin nombre o nombre_en_quiter)."""
        nombre = proveedor.get('nombre', '').strip()
        nombre_en_quiter = proveedor.get('nombre_en_quiter', '').strip()
        
        # Es incompleto si no tiene nombre O no tiene nombre_en_quiter
        return not nombre or not nombre_en_quiter

    def refresh_proveedores(self):
        """Recarga los proveedores desde la base de datos."""
        # Limpiar el searchbar
        self.view.search_frame.search_bar.clear_search()
        # Recargar datos desde la base de datos
        self.load_proveedores()
        # Aplicar filtros actuales (respeta el toggle incompletos)
        self.apply_filters()

    def search_proveedor(self):
        """Realiza búsqueda usando el nuevo sistema de filtros."""
        self.apply_filters()
    
    def add_proveedor(self):
        """Habilita el formulario para agregar un nuevo proveedor."""
        # Limpiar el formulario
        self.view.clear_form()
        # Habilitar edición
        self.view.set_editable(True)
        # Foco en el primer campo (código)
        if 'codigo' in self.view.entries:
            self.view.entries['codigo'].focus_set()

    def delete_proveedor(self):
        """Elimina el proveedor seleccionado."""
        selected_id = self.view.get_selected_id()
        if not selected_id:
            msgbox.showwarning("Advertencia", "Selecciona un proveedor para eliminar")
            return
        
        # Confirmar eliminación
        selection = self.view.get_selection()
        proveedor_nombre = selection[2] if len(selection) > 2 else "Sin nombre"  # Asumiendo que el nombre está en la posición 2
        
        if msgbox.askyesno("Confirmar eliminación", 
                          f"¿Estás seguro de eliminar el proveedor:\n{proveedor_nombre}?"):
            
            # Intentar eliminar
            exito, mensaje = self.model.eliminar_proveedor(selected_id)
            
            if exito:
                msgbox.showinfo("Éxito", mensaje)
                # Recargar la lista
                self.load_proveedores()
                self.apply_filters()
                # Limpiar formulario
                self.view.clear_form()
            else:
                msgbox.showerror("Error", f"No se pudo eliminar el proveedor:\n{mensaje}")

    def edit_proveedor(self):
        """Habilita la edición del proveedor seleccionado."""
        selected_id = self.view.get_selected_id()
        if not selected_id:
            msgbox.showwarning("Advertencia", "Selecciona un proveedor para editar")
            return
        
        # Habilitar edición PRIMERO
        self.view.set_editable(True)
        
        # Obtener datos completos del proveedor
        proveedor_data = self.model.obtener_por_id(selected_id)
        if not proveedor_data:
            msgbox.showerror("Error", "No se pudo obtener la información del proveedor")
            return
        
        # Llenar el formulario con los datos del proveedor
        form_data = {
            'codigo': str(proveedor_data.get('codigo_quiter', '')),
            'nombre': proveedor_data.get('nombre', ''),
            'email': proveedor_data.get('email', ''),
            'nombre_contacto': proveedor_data.get('nombre_contacto', ''),
            'rfc': proveedor_data.get('rfc', ''),
            'nombre_quiter': proveedor_data.get('nombre_en_quiter', ''),
            'telefono': proveedor_data.get('telefono', '')
        }
        
        self.view.fill_form(form_data)

    def save_proveedor(self):
        """Guarda el proveedor (nuevo o editado)."""
        # Obtener datos del formulario
        form_data = self.view.get_form_data()
        
        # Validar datos básicos
        if not form_data.get('codigo', '').strip():
            msgbox.showwarning("Advertencia", "El código es requerido")
            return
        
        # Preparar datos para el modelo (ajustar nombres de campos)
        datos_proveedor = {
            'codigo_quiter': form_data.get('codigo', '').strip(),
            'nombre': form_data.get('nombre', '').strip(),
            'nombre_en_quiter': form_data.get('nombre_quiter', '').strip(),
            'rfc': form_data.get('rfc', '').strip(),
            'telefono': form_data.get('telefono', '').strip(),
            'email': form_data.get('email', '').strip(),
            'nombre_contacto': form_data.get('nombre_contacto', '').strip()
        }
        
        # Determinar si es nuevo o edición
        selected_id = self.view.get_selected_id()
        
        if selected_id:
            # Edición de proveedor existente
            exito, mensaje = self.model.actualizar_proveedor(selected_id, datos_proveedor)
        else:
            # Nuevo proveedor
            exito, mensaje, nuevo_id = self.model.crear_proveedor(datos_proveedor)
        
        if exito:
            msgbox.showinfo("Éxito", mensaje)
            # Recargar la lista
            self.load_proveedores()
            self.apply_filters()
            # Limpiar formulario y deshabilitar edición
            self.view.clear_form()
            self.view.set_editable(False)
        else:
            msgbox.showerror("Error", f"No se pudo guardar el proveedor:\n{mensaje}")

    def cancel_proveedor(self):
        """Cancela la edición/creación y vuelve al modo de visualización."""
        self.view.clear_form()
        self.view.set_editable(False)
        # Ya no llenamos automáticamente el formulario al cancelar

    def combine_proveedor(self):
        self.view.set_editable(False)
        pass