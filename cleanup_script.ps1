# Script para limpiar archivos innecesarios del proyecto Autosol2
# EJECUTAR CON CUIDADO - Hacer backup primero

# Archivos de scripts/herramientas una vez
Remove-Item "fix_strip_errors.py" -Force -ErrorAction SilentlyContinue
Remove-Item "fusionar_hb.py" -Force -ErrorAction SilentlyContinue  
Remove-Item "fusionar_hb_sqlite.py" -Force -ErrorAction SilentlyContinue
Remove-Item "listar_archivos_pdf.py" -Force -ErrorAction SilentlyContinue

# GUI obsoleta
Remove-Item "gui_solicitud.py" -Force -ErrorAction SilentlyContinue

# Entry point duplicado (mantener main_app.py)
# Remove-Item "main.py" -Force -ErrorAction SilentlyContinue

# Archivos de migración/test
Remove-Item "src\migrar_agregar_codigo_vale.py" -Force -ErrorAction SilentlyContinue
Remove-Item "src\init_db.py" -Force -ErrorAction SilentlyContinue
Remove-Item "src\buscarapp\autocarga\main_autocarga.py" -Force -ErrorAction SilentlyContinue
Remove-Item "src\buscarapp\autocarga\test_autocarga.py" -Force -ErrorAction SilentlyContinue

# Documentación de desarrollo
Remove-Item "src\buscarapp\README_REFACTORING.md" -Force -ErrorAction SilentlyContinue
Remove-Item "src\buscarapp\autocarga\README.md" -Force -ErrorAction SilentlyContinue
Remove-Item "DOCUMENTACION_EXPORTAR_LAYOUT.md" -Force -ErrorAction SilentlyContinue

# Archivos de prueba/datos
Remove-Item "BD.txt" -Force -ErrorAction SilentlyContinue
Remove-Item "15gerzahin.flores_QRSOPMX208_8226744.pdf" -Force -ErrorAction SilentlyContinue
Remove-Item "Test_Autocarga" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "Pruebas" -Recurse -Force -ErrorAction SilentlyContinue

# Backups viejos (mantener solo los recientes)
Get-ChildItem "facturas.db_backup_*.db" | Sort-Object LastWriteTime -Descending | Select-Object -Skip 3 | Remove-Item -Force

Write-Host "✅ Limpieza completada. Archivos eliminados:"
Write-Host "   - Scripts de migración/herramientas"  
Write-Host "   - GUI obsoleta (gui_solicitud.py)"
Write-Host "   - Archivos de test y documentación"
Write-Host "   - Archivos de prueba"
Write-Host "   - Backups antiguos"
Write-Host ""
Write-Host "🚀 El proyecto ahora está más limpio y organizado"
