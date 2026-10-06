"""Generación reproducible de experimentos, tablas, figuras y comprobaciones."""
import unittest
from .experimentos import ejecutar, RAIZ

def main():
    datos = ejecutar()
    suite = unittest.defaultTestLoader.discover(str(RAIZ / 'tests'))
    resultado = unittest.TextTestRunner(verbosity=2).run(suite)
    if not resultado.wasSuccessful():
        raise RuntimeError('Hay pruebas fallidas')
    print(f'Generadas {len(datos)} tablas en {RAIZ / "resultados/tablas"}')
    print(f'Figuras en {RAIZ / "resultados/figuras"}')

if __name__ == '__main__':
    main()
