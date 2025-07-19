#!/usr/bin/env python3
"""
Script de validación de código para TCM Matehuala.
Verifica problemas comunes y errores tipográficos en el código.
"""
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Colores para output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text: str, color: str):
    """Imprime texto con color."""
    print(f"{color}{text}{Colors.ENDC}")

def validate_geometry_strings(file_path: str) -> List[Tuple[int, str]]:
    """
    Valida strings de geometría en un archivo Python.
    
    Returns:
        Lista de tuplas (línea, problema_encontrado)
    """
    issues = []
    geometry_pattern = r'\.geometry\s*\(\s*["\']([^"\']+)["\']\s*\)'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(geometry_pattern, line)
            for match in matches:
                geometry = match.group(1)
                
                # Validación básica de formato
                # Permitir solo dimensiones o solo posición
                if not (re.match(r'^\d+x\d+([+-]\d+[+-]\d+)?$', geometry) or 
                       re.match(r'^[+-]\d+[+-]\d+$', geometry)):
                    issues.append((line_num, f"Geometría inválida: '{geometry}'"))
                
                # Verificar errores tipográficos comunes
                if 'git' in geometry.lower():
                    issues.append((line_num, f"Posible error tipográfico 'git' en geometría: '{geometry}'"))
                
                if re.search(r'[oO](?=\d|$)', geometry):
                    issues.append((line_num, f"Posible confusión O/0 en geometría: '{geometry}'"))
                
                if re.search(r'[lI](?=\d)', geometry):
                    issues.append((line_num, f"Posible confusión l/I/1 en geometría: '{geometry}'"))
                    
                if ' ' in geometry:
                    issues.append((line_num, f"Espacio en blanco en geometría: '{geometry}'"))
                    
    except Exception as e:
        issues.append((0, f"Error leyendo archivo: {e}"))
    
    return issues

def validate_import_statements(file_path: str) -> List[Tuple[int, str]]:
    """
    Valida declaraciones de importación.
    
    Returns:
        Lista de tuplas (línea, problema_encontrado)
    """
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Verificar imports relativos problemáticos
            if line.startswith('from .. import') or line.startswith('from ... import'):
                issues.append((line_num, "Import relativo complejo que puede causar problemas"))
            
            # Verificar imports circulares potenciales
            if 'import sys' in line and 'path.append' in lines[line_num:line_num+3]:
                issues.append((line_num, "Posible manipulación problemática de sys.path"))
                
    except Exception as e:
        issues.append((0, f"Error leyendo archivo: {e}"))
    
    return issues

def validate_string_literals(file_path: str) -> List[Tuple[int, str]]:
    """
    Valida strings literales buscando errores comunes.
    
    Returns:
        Lista de tuplas (línea, problema_encontrado)
    """
    issues = []
    
    # Patrones problemáticos comunes
    problematic_patterns = [
        (r'["\'][^"\']*\d+x\d*git\d*[^"\']*["\']', "Posible error tipográfico 'git' en geometría"),
        (r'["\'][^"\']*\d+x\d*[a-zA-Z]+\d*["\']', "String con formato de geometría posiblemente corrupto"),
        (r'["\'][^"\']*\d+×\d+["\']', "Símbolo × en lugar de x en dimensiones"),
    ]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            for pattern, description in problematic_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append((line_num, description))
                    
    except Exception as e:
        issues.append((0, f"Error leyendo archivo: {e}"))
    
    return issues

def validate_file(file_path: str) -> List[Tuple[int, str]]:
    """
    Valida un archivo Python completo.
    
    Returns:
        Lista de todos los problemas encontrados
    """
    all_issues = []
    
    all_issues.extend(validate_geometry_strings(file_path))
    all_issues.extend(validate_import_statements(file_path))
    all_issues.extend(validate_string_literals(file_path))
    
    return all_issues

def main():
    """Función principal del validador."""
    print_colored("🔍 TCM Matehuala - Validador de Código", Colors.BOLD + Colors.BLUE)
    print_colored("=" * 50, Colors.BLUE)
    
    # Directorios a validar
    directories_to_check = ['src', 'app', 'config']
    total_files = 0
    total_issues = 0
    
    for directory in directories_to_check:
        if not os.path.exists(directory):
            continue
            
        print_colored(f"\n📁 Validando directorio: {directory}", Colors.BOLD)
        
        # Buscar archivos Python
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    total_files += 1
                    
                    issues = validate_file(file_path)
                    
                    if issues:
                        total_issues += len(issues)
                        print_colored(f"\n⚠️  {file_path}", Colors.YELLOW)
                        
                        for line_num, issue in issues:
                            if line_num > 0:
                                print_colored(f"   Línea {line_num}: {issue}", Colors.RED)
                            else:
                                print_colored(f"   {issue}", Colors.RED)
                    else:
                        print_colored(f"✅ {file_path}", Colors.GREEN)
    
    # Resumen
    print_colored(f"\n" + "=" * 50, Colors.BLUE)
    print_colored(f"📊 Resumen de Validación", Colors.BOLD + Colors.BLUE)
    print_colored(f"Archivos revisados: {total_files}", Colors.BLUE)
    
    if total_issues == 0:
        print_colored(f"✅ Problemas encontrados: {total_issues}", Colors.GREEN)
        print_colored("🎉 ¡Código validado exitosamente!", Colors.BOLD + Colors.GREEN)
        return 0
    else:
        print_colored(f"⚠️  Problemas encontrados: {total_issues}", Colors.RED)
        print_colored("🔧 Revise los problemas reportados arriba", Colors.YELLOW)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
