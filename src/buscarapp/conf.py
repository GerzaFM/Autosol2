import os

# Buscar el archivo PDF en diferentes ubicaciones posibles
def _encontrar_pdf_cheque():
    """Encuentra la ruta correcta del archivo PDF de cheque"""
    posibles_rutas = [
        "../../FormatosSolicitud/Cheque.pdf",  # Desde src/solicitudapp/
        "FormatosSolicitud/Cheque.pdf",        # Desde directorio raíz
        "../FormatosSolicitud/Cheque.pdf",     # Desde src/
    ]
    
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            return ruta
    
    # Si no encuentra ninguna, usar la ruta por defecto
    return "../../FormatosSolicitud/Cheuqe.pdf"

form_cheque = _encontrar_pdf_cheque()