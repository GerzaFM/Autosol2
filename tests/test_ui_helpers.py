"""
Tests para las utilidades de UI y validación de geometría.
"""
import unittest
import sys
import os

# Agregar el directorio raíz al path para importar las utilidades
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

from app.utils.ui_helpers import (
    validate_geometry_string,
    parse_geometry_string,
    get_safe_window_size
)

class TestUIHelpers(unittest.TestCase):
    """Tests para las utilidades de UI."""
    
    def test_validate_geometry_string_valid(self):
        """Test para strings de geometría válidos."""
        valid_geometries = [
            "600x280",
            "1200x900",
            "400x300+100+50",
            "800x600-50-30",
            "1024x768+0+0"
        ]
        
        for geometry in valid_geometries:
            with self.subTest(geometry=geometry):
                self.assertTrue(
                    validate_geometry_string(geometry),
                    f"Geometría válida rechazada: {geometry}"
                )
    
    def test_validate_geometry_string_invalid(self):
        """Test para strings de geometría inválidos."""
        invalid_geometries = [
            "600x28git0",  # El error original
            "600x",
            "x280",
            "600280",
            "600x280x50",
            "",
            None,
            123,
            "abc×def",
            "600×280"  # Símbolo × en lugar de x
        ]
        
        for geometry in invalid_geometries:
            with self.subTest(geometry=geometry):
                self.assertFalse(
                    validate_geometry_string(geometry),
                    f"Geometría inválida aceptada: {geometry}"
                )
    
    def test_parse_geometry_string(self):
        """Test para el parseo de strings de geometría."""
        test_cases = [
            ("600x280", (600, 280, None, None)),
            ("1200x900+100+50", (1200, 900, 100, 50)),
            ("800x600-50-30", (800, 600, -50, -30)),
            ("invalid", None)
        ]
        
        for geometry, expected in test_cases:
            with self.subTest(geometry=geometry):
                result = parse_geometry_string(geometry)
                self.assertEqual(result, expected)
    
    def test_get_safe_window_size(self):
        """Test para obtener tamaños de ventana seguros."""
        # Test con clave válida
        size = get_safe_window_size("popup_favoritos")
        self.assertTrue(validate_geometry_string(size))
        
        # Test con clave inválida (debería retornar fallback)
        size = get_safe_window_size("nonexistent_key")
        self.assertEqual(size, "400x300")

class TestGeometryRegressions(unittest.TestCase):
    """Tests específicos para prevenir regresiones de errores de geometría."""
    
    def test_original_error_case(self):
        """Test específico para el error original '600x28git0'."""
        self.assertFalse(validate_geometry_string("600x28git0"))
        
        # Verificar que la versión corregida es válida
        self.assertTrue(validate_geometry_string("600x280"))
    
    def test_common_typos(self):
        """Test para errores tipográficos comunes."""
        typos = [
            "600x28git0",  # Error original
            "600x280o",    # 'o' en lugar de '0'
            "6OOx280",     # 'O' en lugar de '0'
            "600xl280",    # 'l' en lugar de '2'
            "600x 280",    # Espacio extra
            "600 x280",    # Espacio extra
        ]
        
        for typo in typos:
            with self.subTest(typo=typo):
                self.assertFalse(
                    validate_geometry_string(typo),
                    f"Error tipográfico no detectado: {typo}"
                )

if __name__ == "__main__":
    # Ejecutar los tests
    unittest.main(verbosity=2)
