import os

# Buscar el archivo PDF en diferentes ubicaciones posibles
def _encontrar_pdf_solicitud():
    """Encuentra la ruta correcta del archivo PDF de solicitud"""
    posibles_rutas = [
        "../../FormatosSolicitud/Solicitud.pdf",  # Desde src/solicitudapp/
        "FormatosSolicitud/Solicitud.pdf",        # Desde directorio raíz
        "../FormatosSolicitud/Solicitud.pdf",     # Desde src/
    ]
    
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            return ruta
    
    # Si no encuentra ninguna, usar la ruta por defecto
    return "../../FormatosSolicitud/Solicitud.pdf"

form_solicitud_interna = _encontrar_pdf_solicitud()