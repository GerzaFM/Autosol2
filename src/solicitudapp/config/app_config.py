"""
Configuración de la aplicación.
"""
from typing import Dict, List


class AppConfig:
    """Configuración centralizada de la aplicación."""
    
    # Opciones para comboboxes
    #TIPOS_SOLICITUD: List[str] = ["VC - VALE DE CONTROL", "GA - COMBUSTIBLES Y LUBRICANTES"]
    DEPARTAMENTOS: List[str] = ["ADMINISTRACIÓN", "VENTAS", "SERVICIO", "REFACCIONES", "HyP"]
    
    # Categorías
    CATEGORIAS: List[str] = ["Comer", "Fleet", "Semis", "Refa", "Serv", "HyP", "Admin"]
    
    # Configuración de UI
    WINDOW_SIZE: str = "1024x850"
    THEME: str = "darkly"
    
    # Límites
    MAX_CONCEPTOS_RECOMENDADOS: int = 8
    
    # Anchos de columnas en el TreeView
    COLUMN_WIDTHS: Dict[str, int] = {
        "Cantidad": 80,
        "Descripción": 400,
        "Precio": 80,
        "Total": 80
    }
    
    # Anchos de entrada para popup de conceptos
    POPUP_ENTRY_WIDTHS: Dict[str, int] = {
        "Cantidad": 8,
        "Descripción": 70,
        "Precio": 12,
        "Total": 12
    }
    
    # Mensajes de error
    ERROR_MESSAGES: Dict[str, str] = {
        "campos_obligatorios": "Todos los campos son obligatorios.",
        "numeros_invalidos": "Los campos Cantidad, Precio y Total deben ser números válidos.",
        "no_datos": "No hay datos de solicitud disponibles.",
        "demasiados_conceptos": "La lista de conceptos es demasiado larga.\n¿Prefiere usar un concepto general?",
        "proveedor_incompleto": "Los datos del proveedor están incompletos.",
        "sin_conceptos": "Debe agregar al menos un concepto."
    }
    
    # Valores por defecto
    DEFAULT_VALUES: Dict[str, str] = {
        "departamento": "ADMINISTRACIÓN",
        "tipo_solicitud": "VC - VALE DE CONTROL"  # Valor por defecto del diccionario TIPO_VALE
    }

    # Diccionario: abreviatura -> tipo de vale
    TIPO_VALE = {
        "AU": "ACONDICIONAMIENTO DE UNIDADES",
        "AF": "ACTIVO FIJO",
        "SA": "AGUA",
        "AGO": "AGUINALDO",
        "APR": "ANTICIPO A PROVEEDORES",
        "ALF": "ASESORIA, AUDITORIA Y FISCAL",
        "INS": "ATENCION A CLIENTES Y PROVEEDORES",
        "BLI": "BASES POR LICITACIONES",
        "CP": "CAPACITACION AL PERSONAL",
        "GA": "COMBUSTIBLES Y LUBRICANTES",
        "CDG": "COMISIONES DIRECTIVAS Y GERENCIALES",
        "CBA": "COMISIONES BANCARIAS",
        "CE": "COMPRA DE EQUIPO COMPUTO Y OFICINA",
        "CSN": "COMPRA DIRECTA DE UNIDAD SEMINUEVA",
        "CI": "CONSUMIBLES",
        "CIM": "COSTOS SOCIALES",
        "CS": "CUOTAS SINDICALES",
        "DEP": "DEPRECIACION Y AMORTIZACION",
        "DEV": "DEVOLUCION CLIENTE",
        "DIV": "DIVERSOS",
        "ENE": "ENERGIA ELECTRICA",
        "EC": "EVENTOS DE COLABORADORES",
        "EQ": "COMPRA DE EQUIPO Y HERRAMIENTA",
        "ES": "ESTUDIOS SOCIOECONOMICOS",
        "FE": "FLETES Y EMBARQUES",
        "GU": "GASOLINA PREVIA UNIDADES",
        "GV": "GASTOS DE VIAJE Y REPRESENTACION",
        "GFA": "GASTOS FIN DE AÑO",
        "GE": "GARANTIA EXTENDIDA",
        "HPP": "HONORARIOS PROFESIONALES",
        "IM": "IMPRESION",
        "IRN": "IMPUESTOS SOBRE REMUNERACIONES Y NOMINAS",
        "IFJ": "INDEMNIZACIONES/FINIQUITOS Y JUBILACIONES",
        "DAS": "INTERESES DAS",
        "ME": "MANTENIMIENTO DE EDIFICIO",
        "MEU": "MANTENIMIENTO EQUIPO Y UNIDADES DE CMPIA",
        "OSI": "ORDEN DE SERVICIO INTERNA",
        "OID": "OTROS IMPUESTOS Y DERECHOS",
        "ISAN": "PAGO DE ISAN",
        "ISR": "PAGO DE ISR",
        "IVA": "PAGO DE IVA",
        "RET": "PAGO DE RETENCIONES DE IVA, ISR y OTROS",
        "PA": "PAPELERIA Y ARTICULOS DE ESCRITORIO",
        "PM": "PAQUETERIA Y MENSAJERIA",
        "PR": "PERMISOS DE CIRCULACION VEHICULARES",
        "MM": "PROMOCION MERCANTIL",
        "PMT": "PROMOCION MERCANTIL TOMAS",
        "PRO": "PROVISIONES DIVERSAS",
        "GM": "PUBLICIDAD",
        "REI": "REBATE INTERNO",
        "RA": "RECARGOS Y ACTUALIZACIONES",
        "RE": "RENTAS DE EQUIPO",
        "RI": "RENTAS DE INMUEBLES",
        "RC": "REPARACIONES Y CONSTRUCCIONES A EDIFICIO",
        "SAN": "SEGUROS AUTOS NUEVOS",
        "SGM": "SEGUROS GASTOS MEDICOS MAYORES",
        "SE": "SEGUROS Y FIANZAS",
        "SAD": "SERVICIOS ADMINISTRATIVOS",
        "SET": "SERVICIOS EXTERNOS",
        "SL": "SOFTWARE Y LICENCIAS",
        "3": "SUBARRENDADO TOT SERVICIO",
        "7": "SUBARRENDADO TOT VERIFICACION",
        "4": "SUBARRENDADO TOT EXTERNO HYP",
        "5": "SUBARRENDADO TOT LAVADO",
        "SS": "SUELDOS Y SALARIOS DE EMPLEADOS",
        "SC": "SUSCRIPCIONES Y CUOTAS",
        "ST": "TELEFONO E INTERNET",
        "TU": "TRASLADO DE UNIDADES",
        "TV": "TRASLADO DE VALORES",
        "UN": "UNIFORMES Y ROPA DE TRABAJO",
        "AL": "UTILES DE ASEO Y ORNATO",
        "1": "VALE COMPRA AUTOS NUEVOS",
        "1R": "VALE COMPRA REFACCIONES",
        "2": "VALE COMPRA SEMINUEVOS",
        "VC": "VALE DE CONTROL",
        "VG": "VIGILANCIA"
    }
