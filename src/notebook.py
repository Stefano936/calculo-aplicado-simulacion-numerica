"""Construcción y ejecución del notebook con kernel nuevo."""
from pathlib import Path
import tempfile
import json
import sys
import nbformat as nbf
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager
from .experimentos import RAIZ


def crear_y_ejecutar(raiz=RAIZ):
    raiz=Path(raiz)
    md=nbf.v4.new_markdown_cell
    code=nbf.v4.new_code_cell
    celdas=[md('# Simulación numérica de sistemas dinámicos aplicada a ciberseguridad\n'
               'Stefano Francolino, Lucias Vazquez, Juan Andres Brignone y Agustin Karabajich · Cálculo Aplicado · Universidad Católica del Uruguay\n\n'
               'Ejecutar todas las celdas en orden. Los modelos son hipotéticos y el tiempo se expresa en unidades genéricas.'),
       md('## Métodos y contrato\nEuler usa la pendiente inicial; Heun predice el estado final y promedia dos pendientes. '
          'Ambos devuelven tiempos, aproximaciones y pasos, incluyen el punto inicial y ajustan el último paso. '
          'No se ocultan estados negativos.'),
       code("from pathlib import Path\nimport sys\nraiz = Path.cwd()\nif not (raiz / 'src').exists():\n    raiz = raiz.parent\nassert (raiz / 'src').exists(), 'Abrir desde la raíz del proyecto o notebooks/'\nsys.path.insert(0, str(raiz))\nfrom src.metodos import euler, euler_mejorado\nfrom src.experimentos import ejecutar\nfrom IPython.display import display, Image\nimport numpy as np\nimport pandas as pd\ndatos = ejecutar(raiz)\ndef figura(nombre):\n    display(Image(filename=str(raiz / 'resultados/figuras' / (nombre+'.png'))))"),
       code("t, x, pasos = euler_mejorado(lambda t,x: t, 0, 0, 1, .3)\ndisplay(pd.DataFrame({'t':t, 'Heun':x, 'referencia t²/2':t*t/2}))\nassert pasos == 4 and len(t) == pasos+1 and t[-1] == 1\nnp.testing.assert_allclose(x, t*t/2, atol=1e-14)"),
       md('## 1. Crecimiento lineal\n$x^{\\prime}=1$, $x(0)=0$, referencia $x=t$, intervalo [0,10]. '
          'Al ser constante la pendiente, Euler presenta error cero en los nodos de las tres mallas ejecutadas. Reducir el paso no garantiza mejorar este caso.'),
       code("display(datos['lineal'])\nfigura('lineal')"),
       md('## 2. Decrecimiento y error\n$x^{\\prime}=-x$, $x(0)=1$. '
          '$E_n=|x_n-e^{-t_n}|$. El error final usa el último nodo, mientras el máximo recorre todos. '
          'Con h=1 Euler toma cero desde el primer paso. Se comparan cinco pasos para el error.'),
       code("display(datos['error'])\nfigura('exponencial')\nfigura('errores')"),
       md('## 3. Euler frente a Heun\nHeun requiere dos evaluaciones por paso. '
          'Comparar ambas métricas: con h=1 Euler tiene menor error final, pero Heun menor máximo. '
          'La referencia final es muy pequeña, por eso el cero artificial puede quedar más cerca en ese punto.'),
       code("display(datos['comparacion'])\ndisplay(datos['convergencia'])\nc = datos['comparacion'].query('h == 1').set_index('metodo')\nassert c.loc['Euler','error_final'] < c.loc['Heun','error_final']\nassert c.loc['Euler','error_maximo'] > c.loc['Heun','error_maximo']"),
       md('## 4. Remediación de equipos vulnerables\n$V^{\\prime}=-kV$, $V_0=1000$, A: k=.1, B: .3, C: .7. '
          'k es rapidez fraccional, en tiempo inverso. Los decimales son cantidades agregadas, no fracciones de un equipo individual.'),
       code("display(datos['vulnerabilidades'])\ndisplay(datos['vulnerabilidades_resumen'])\nassert len(datos['vulnerabilidades']) == 27\nfigura('organizaciones')\nfor org in 'ABC':\n    figura('organizacion_'+org)"),
       md('## 5. Ecuación en diferencias\n$V_n=V_0(1-hk)^n$. '
          'Para 0<hk<1 hay descenso positivo; hk=1 anula el estado. '
          'Para 1<hk<2 alterna signo y converge en magnitud: estabilidad sin validez física. '
          'hk=2 alterna sin límite; hk>2 crece en magnitud.'),
       code("display(datos['regimenes'].pivot(index='n', columns='hk', values='valor'))\nfigura('regimenes')\nt,x,n = euler(lambda t,x:-1.5*x,1,0,5,1)\nnp.testing.assert_allclose(x,(-.5)**np.arange(n+1))\nprint('Valores negativos conservados:', x)"),
       md('## 6. Aparición\n$V^{\\prime}=\\lambda-.3V$, V0=1000, h=.1, [0,20]. '
          'El equilibrio $V^*=\\lambda/.3$ resulta del balance. Todas las condiciones iniciales están por encima del equilibrio, '
          'por lo que disminuyen hacia él. Aproximarse no equivale a alcanzarlo.'),
       code("display(datos['extendido'])\nfigura('extendido')\nfor lam in [0,50,100,200]:\n    eq = lam/.3\n    t,x,n = euler(lambda t,x:lam-.3*x,1000,0,20,.1)\n    np.testing.assert_allclose(x, eq+(1000-eq)*.97**np.arange(n+1), atol=2e-11)"),
       md('## Interpretación informática y alcance\nCVE identifica una vulnerabilidad; CVSS evalúa severidad; '
          'ATT&CK organiza comportamientos adversarios. T1190 se vincula con debilidades de aplicaciones expuestas. '
          'La remediación puede acortar exposición, pero el modelo no calcula incidentes ni probabilidades de ataque. '
          ''
          'Las tasas constantes, homogeneidad y falta de población total limitan la aplicación a organizaciones reales.'),
       md('## Verificación final\nLas pruebas utilizan fórmulas independientes, dependencia explícita de t, ajuste final y entradas inválidas.'),
       code("import unittest\nsuite = unittest.defaultTestLoader.discover(str(raiz/'tests'))\nresultado = unittest.TextTestRunner(verbosity=2).run(suite)\nassert resultado.wasSuccessful()\nprint('Completado: experimentos, tablas, figuras y pruebas.')")]
    nb=nbf.v4.new_notebook(cells=celdas,metadata={'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'}})
    destino=raiz/'notebooks/proyecto_calculo.ipynb'
    destino.parent.mkdir(exist_ok=True)
    # Especificación temporal: usa el mismo Python, sin registrar kernels globales.
    with tempfile.TemporaryDirectory(prefix='calculo-kernel-') as temporal:
        kernel=Path(temporal)/'calculo'
        kernel.mkdir()
        (kernel/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Python cálculo','language':'python'}),encoding='utf-8')
        km=KernelManager(kernel_name='calculo',kernel_spec_manager=KernelSpecManager(kernel_dirs=[temporal]))
        cliente=NotebookClient(nb,km=km,timeout=180,resources={'metadata':{'path':str(raiz)}},allow_errors=False)
        cliente.execute()
    nbf.write(nb,destino)
    return destino
