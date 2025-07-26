"""
Script de prueba para la comparación de nombres mejorada
"""

# Simular la lógica de normalización y comparación
def normalize_name(name):
    if not name:
        return ""
    
    # Convertir a mayúsculas y quitar espacios
    normalized = name.upper().replace(" ", "")
    
    # Quitar caracteres especiales comunes
    normalized = normalized.replace(".", "").replace(",", "").replace("-", "")
    normalized = normalized.replace("&", "").replace("/", "").replace("\\", "")
    
    return normalized

# Datos de prueba
nombres_pdf = ['SERVICIONAVAMEDRANOSADECV', 'SERVICIOSGLOBALESELYTSADECV', 'CYBERPUERTASADECV']
nombres_bd = ['SERVICIO NAVA MEDRANO', 'SERVICIOS GLOBALES ELYT', 'CYBERPUERTA SA DE CV']

print('Prueba de lógica de comparación mejorada:')
print('=' * 60)

for nombre_pdf in nombres_pdf:
    print(f'\n🔍 Buscando: {nombre_pdf}')
    normalized_target = normalize_name(nombre_pdf)
    print(f'   Normalizado: {normalized_target}')
    
    encontrado = False
    for nombre_bd in nombres_bd:
        normalized_db = normalize_name(nombre_bd)
        print(f'   Comparando con: {nombre_bd} -> {normalized_db}')
        
        # Comparación exacta
        if normalized_db == normalized_target:
            print(f'   ✅ Coincidencia exacta: {nombre_bd}')
            encontrado = True
            break
        
        # Comparación sin SADECV al final
        if normalized_target.endswith('SADECV'):
            target_sin_sadecv = normalized_target[:-6]  # Quitar "SADECV"
            print(f'   🔄 Probando sin SADECV: {target_sin_sadecv} vs {normalized_db}')
            if normalized_db == target_sin_sadecv:
                print(f'   ✅ Coincidencia sin SADECV: {nombre_bd}')
                encontrado = True
                break
    
    if not encontrado:
        print('   ❌ No encontrado')

print('\n' + '=' * 60)
print('Análisis detallado:')

for i, (pdf, bd) in enumerate(zip(nombres_pdf, nombres_bd)):
    pdf_norm = normalize_name(pdf)
    bd_norm = normalize_name(bd)
    pdf_sin_sadecv = pdf_norm[:-6] if pdf_norm.endswith('SADECV') else pdf_norm
    
    print(f'\n{i+1}. {pdf} vs {bd}')
    print(f'   PDF normalizado: {pdf_norm}')
    print(f'   BD normalizado:  {bd_norm}')
    print(f'   PDF sin SADECV:  {pdf_sin_sadecv}')
    print(f'   Coincide exacto: {pdf_norm == bd_norm}')
    print(f'   Coincide sin SADECV: {pdf_sin_sadecv == bd_norm}')
