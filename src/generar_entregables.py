"""Un comando para producir y verificar todos los entregables locales."""
import argparse
import io
import json
import unittest
import zipfile
from .experimentos import ejecutar, RAIZ
from .informe import recursos, compilar
from .notebook import crear_y_ejecutar
from .verificacion import auditar, matriz, manifiesto, archivos_entrega


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sin-pdf',action='store_true')
    parser.add_argument('--sin-notebook',action='store_true')
    parser.add_argument('--solo-pdf',action='store_true')
    args=parser.parse_args()
    if args.solo_pdf:
        compilar()
        print('PDF recompilado:',RAIZ/'informe/informe.pdf')
        return
    datos=ejecutar()
    recursos(datos)
    suite=unittest.defaultTestLoader.discover(str(RAIZ/'tests'))
    buffer=io.StringIO()
    resultado=unittest.TextTestRunner(stream=buffer,verbosity=2).run(suite)
    (RAIZ/'verificacion/pruebas.txt').write_text(buffer.getvalue(),encoding='utf-8')
    print(buffer.getvalue())
    if not resultado.wasSuccessful():
        raise RuntimeError('Hay pruebas fallidas')
    if not args.sin_notebook:
        print('Ejecutando notebook desde kernel nuevo...',flush=True)
        crear_y_ejecutar()
    if not args.sin_pdf:
        print('Compilando LaTeX con Biber...',flush=True)
        compilar()
    auditoria=auditar(con_pdf=not args.sin_pdf,con_notebook=not args.sin_notebook)
    matriz()
    manifiesto()
    if not args.sin_pdf and not args.sin_notebook:
        destino=RAIZ.parent/'proyecto_calculo.zip'
        with zipfile.ZipFile(destino,'w',zipfile.ZIP_DEFLATED) as archivo:
            for p in archivos_entrega():
                archivo.write(p,'proyecto_calculo/'+str(p.relative_to(RAIZ)).replace('\\','/'))
        print('ZIP:',destino)
    print(json.dumps(auditoria,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
