"""Generación reproducible de experimentos, figuras y notebook ejecutado."""
import argparse
import unittest
from .experimentos import ejecutar, RAIZ

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sin-notebook', action='store_true',
                        help='Generar resultados y ejecutar pruebas sin Jupyter')
    args = parser.parse_args()
    datos = ejecutar()
    suite = unittest.defaultTestLoader.discover(str(RAIZ / 'tests'))
    resultado = unittest.TextTestRunner(verbosity=2).run(suite)
    if not resultado.wasSuccessful():
        raise RuntimeError('Hay pruebas fallidas')
    if not args.sin_notebook:
        from .notebook import crear_y_ejecutar
        print('Ejecutando notebook desde un kernel nuevo...', flush=True)
        crear_y_ejecutar()
    print(f'Generadas {len(datos)} tablas en {RAIZ / "resultados/tablas"}')
    print(f'Figuras en {RAIZ / "resultados/figuras"}')

if __name__ == '__main__':
    main()
