#!/usr/bin/env python3
"""
Script para analizar dependencias del proyecto Autosol2
"""

import os
import re
import ast
from pathlib import Path
from collections import defaultdict

def extract_imports_from_file(file_path):
    """Extrae imports de un archivo Python"""
    imports = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parsear el AST para extraer imports
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
        except SyntaxError:
            # Si hay error de sintaxis, usar regex como fallback
            import_patterns = [
                r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
                r'^from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import',
            ]
            
            for line in content.split('\n'):
                line = line.strip()
                for pattern in import_patterns:
                    match = re.match(pattern, line)
                    if match:
                        imports.add(match.group(1))
                        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
    
    return imports

def scan_project():
    """Escanea todo el proyecto en busca de dependencias"""
    project_root = Path(__file__).parent
    all_imports = defaultdict(list)
    
    # Buscar todos los archivos .py
    for py_file in project_root.rglob("*.py"):
        if "__pycache__" not in str(py_file):
            imports = extract_imports_from_file(py_file)
            for imp in imports:
                all_imports[imp].append(str(py_file.relative_to(project_root)))
    
    return all_imports

def categorize_imports(all_imports):
    """Categoriza las dependencias"""
    
    # Módulos de la librería estándar de Python
    stdlib_modules = {
        'sys', 'os', 're', 'json', 'csv', 'xml', 'datetime', 'pathlib', 
        'logging', 'threading', 'multiprocessing', 'subprocess', 'shutil',
        'tempfile', 'glob', 'uuid', 'hashlib', 'base64', 'urllib', 'http',
        'ssl', 'socket', 'collections', 'itertools', 'functools', 'operator',
        'math', 'random', 'statistics', 'decimal', 'fractions', 'cmath',
        'typing', 'dataclasses', 'enum', 'contextlib', 'weakref', 'copy',
        'pickle', 'copyreg', 'shelve', 'marshal', 'dbm', 'sqlite3', 'zlib',
        'gzip', 'bz2', 'lzma', 'zipfile', 'tarfile'
    }
    
    # Módulos internos del proyecto
    internal_modules = {
        'src', 'app', 'config', 'services', 'solicitudapp', 'buscarapp', 
        'chequeapp', 'proveedoresapp', 'mainapp', 'logapp', 'useradminapp',
        'bd'
    }
    
    # Mapeo de imports a paquetes PyPI
    pypi_mapping = {
        'ttkbootstrap': 'ttkbootstrap>=1.10.1',
        'tkinter': None,  # Viene con Python
        'peewee': 'peewee>=3.17.0',
        'psycopg2': 'psycopg2-binary>=2.9.0',
        'decouple': 'python-decouple>=3.6',
        'PyPDFForm': 'PyPDFForm>=3.4.0',
        'PyPDF2': 'PyPDF2>=3.0.1',
        'pdfplumber': 'pdfplumber>=0.11.0',
        'reportlab': 'reportlab>=4.0.0',
        'openpyxl': 'openpyxl>=3.1.0',
        'pandas': 'pandas>=2.3.0',
        'numpy': 'numpy>=2.3.0',
        'PIL': 'Pillow>=10.4.0',
        'Pillow': 'Pillow>=10.4.0',
        'pypdfium2': 'pypdfium2>=4.30.0',
        'lxml': 'lxml>=4.9.0',
        'dateutil': 'python-dateutil>=2.9.0',
        'pytz': 'pytz>=2025.2',
        'tzdata': 'tzdata>=2025.2',
        'cryptography': 'cryptography>=45.0.0',
        'charset_normalizer': 'charset-normalizer>=3.4.0',
        'cffi': 'cffi>=1.17.0',
        'pycparser': 'pycparser>=2.22',
        'six': 'six>=1.17.0',
        'pdfminer': 'pdfminer.six>=20250506',
    }
    
    external_deps = set()
    stdlib_used = set()
    internal_used = set()
    unknown = set()
    
    for module, files in all_imports.items():
        if module in stdlib_modules:
            stdlib_used.add(module)
        elif module in internal_modules:
            internal_used.add(module)
        elif module in pypi_mapping:
            if pypi_mapping[module]:
                external_deps.add(pypi_mapping[module])
        else:
            unknown.add(module)
    
    return {
        'external': sorted(external_deps),
        'stdlib': sorted(stdlib_used),
        'internal': sorted(internal_used),
        'unknown': sorted(unknown)
    }

if __name__ == "__main__":
    print("🔍 Analizando dependencias del proyecto Autosol2...")
    
    all_imports = scan_project()
    categorized = categorize_imports(all_imports)
    
    print(f"\n📊 RESUMEN:")
    print(f"  • Dependencias externas: {len(categorized['external'])}")
    print(f"  • Módulos estándar: {len(categorized['stdlib'])}")
    print(f"  • Módulos internos: {len(categorized['internal'])}")
    print(f"  • Desconocidos: {len(categorized['unknown'])}")
    
    print(f"\n📦 DEPENDENCIAS EXTERNAS (PyPI):")
    for dep in categorized['external']:
        print(f"  {dep}")
    
    print(f"\n🐍 MÓDULOS ESTÁNDAR DE PYTHON:")
    for mod in categorized['stdlib']:
        print(f"  {mod}")
    
    if categorized['unknown']:
        print(f"\n❓ MÓDULOS DESCONOCIDOS/REVISAR:")
        for mod in categorized['unknown']:
            files = all_imports.get(mod, [])
            print(f"  {mod} -> {files[:3]}")  # Solo mostrar primeros 3 archivos
    
    print(f"\n✅ Análisis completado!")
