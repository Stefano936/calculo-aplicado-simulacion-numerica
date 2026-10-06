"""Convierte resultados numéricos en recursos LaTeX y compila el informe."""
import json
import platform
import shutil
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
from .experimentos import RAIZ


def numero(valor, entero=False):
    if pd.isna(valor):
        return '--'
    if isinstance(valor, str):
        return valor.replace('_', r'\_')
    if entero:
        return str(int(valor))
    if valor == 0:
        return '0'
    if abs(valor) < .001:
        mantisa, exp = f'{valor:.5e}'.split('e')
        return '$' + mantisa + r'\times 10^{' + str(int(exp)) + '}$'
    return f'{valor:.6f}'.rstrip('0').rstrip('.')


def recursos(datos, raiz=RAIZ):
    carpeta = Path(raiz) / 'informe/generados'
    carpeta.mkdir(parents=True, exist_ok=True)
    definiciones = [
      ('lineal','Euler para crecimiento lineal en $[0,10]$, referencia $x=t$.',
       [('h','$h$'),('pasos','Pasos'),('puntos','Puntos'),('valor_final','$x_N$'),('error_final','$E_f$'),('error_maximo','$E_{\\max}$')]),
      ('error','Euler para $x^{\\prime}=-x$ en $[0,10]$: errores absolutos y costo.',
       [('h','$h$'),('pasos','Pasos'),('valor_final','$x_N$'),('error_final','$E_f$'),('error_maximo','$E_{\\max}$'),('evaluaciones','Eval. $f$')]),
      ('comparacion','Euler y Heun para $x^{\\prime}=-x$, $x_0=1$, en $[0,10]$.',
       [('metodo','Método'),('h','$h$'),('valor_final','$x_N$'),('error_final','$E_f$'),('pasos','Pasos'),('error_maximo','$E_{\\max}$'),('evaluaciones','Eval. $f$')]),
      ('convergencia','Refinamiento para $x^{\\prime}=-x$ en $[0,10]$: error máximo y orden observado.',
       [('metodo','Método'),('h','$h$'),('error_maximo','$E_{\\max}$'),('evaluaciones','Eval. $f$'),('orden_observado','$p_{\\mathrm{obs}}$')]),
      ('vulnerabilidades','Equipos vulnerables: todas las organizaciones, pasos y tiempos requeridos.',
       [('organizacion','Org.'),('k','$k$'),('h','$h$'),('t','$t$'),('aproximacion','Aprox.'),('referencia','Referencia'),('error_absoluto','Error absoluto')]),
      ('vulnerabilidades_resumen','Resumen de remediación en $[0,20]$, $V_0=1000$, referencia $1000e^{-kt}$.',
       [('organizacion','Org.'),('k','$k$'),('h','$h$'),('pasos','Pasos'),('valor_final','$V_N$'),('error_final','$E_f$'),('error_maximo','$E_{\\max}$')]),
      ('extendido','Euler para $V^{\\prime}=\\lambda-0,3V$, $h=0,1$, en $[0,20]$.',
       [('lambda_tasa','$\\lambda$'),('valor_inicial','$V_0$'),('valor_final','$V_N$'),('equilibrio','$V^*$'),('distancia_equilibrio','$|V_N-V^*|$'),('pasos','Pasos')])
    ]
    auditoria = {}
    for nombre,titulo,columnas in definiciones:
        df=datos[nombre]
        label=nombre.replace('_','')
        larga = nombre == 'vulnerabilidades'
        texto=[r'\clearpage' if larga else '',r'\begingroup\small\setlength{\tabcolsep}{4pt}',
               r'\begin{longtable}{'+'l'*len(columnas)+'}' if larga else r'\begin{table}[H]\centering',
               r'\caption{'+titulo+r'}\label{tab:'+label+r'}\\',r'\toprule',
               ' & '.join(c[1] for c in columnas)+r'\\',r'\midrule\endfirsthead',
               r'\multicolumn{'+str(len(columnas))+r'}{l}{\small Tabla \thetable{} (continuación)}\\',
               r'\toprule',' & '.join(c[1] for c in columnas)+r'\\',r'\midrule\endhead',
               r'\bottomrule\endfoot']
        celdas=[]
        for _,fila in df.iterrows():
            valores=[numero(fila[k],k in ['pasos','puntos','evaluaciones','t','lambda_tasa','valor_inicial']) for k,_ in columnas]
            texto.append(' & '.join(valores)+r'\\')
            celdas.append(valores)
        texto += [r'\end{longtable}',r'\endgroup']
        if not larga:
            # Tablas cortas indivisibles: evita separar tres filas entre páginas.
            encabezado=' & '.join(c[1] for c in columnas)+r'\\'
            texto=[r'\begin{table}[H]\centering\small\setlength{\tabcolsep}{4pt}',
                   r'\caption{'+titulo+r'}\label{tab:'+label+r'}',
                   r'\begin{tabular}{'+'l'*len(columnas)+'}',r'\toprule',encabezado,r'\midrule']
            texto += [' & '.join(v)+r'\\' for v in celdas]
            texto += [r'\bottomrule\end{tabular}',r'\end{table}']
        if nombre.startswith('vulnerabilidades'):
            texto.append(r'{\footnotesize Nota. $t,h$: unidades de tiempo; $k$: tiempo inverso. Cantidades y errores: equipos agregados.}')
        elif nombre=='extendido':
            texto.append(r'{\footnotesize Nota. $\lambda$: equipos por unidad de tiempo; $V$: equipos agregados. Evaluaciones de $f$: 200 por escenario.}')
        else:
            texto.append(r'{\footnotesize Nota. $h$: unidades de tiempo. $x$ y errores sin unidad definida. Eval. $f$: llamadas a la función; valores sin redondeo previo.}')
        (carpeta/(nombre+'.tex')).write_text('\n'.join(texto)+'\n',encoding='utf-8')
        auditoria[nombre]={'columnas':[k for k,_ in columnas],'celdas':celdas}
    clasificacion=[
      ['0<hk<1','Positivo; decrece','Disminuye','0','Asintótica; sí'],
      ['hk=1','Cero desde n=1','Se anula','0','Asintótica; extinción artificial'],
      ['1<hk<2','Alternante','Disminuye','0','Asintótica; no'],
      ['hk=2','Alternante','Constante','No existe','Frontera; no'],
      ['hk>2','Alternante','Crece sin cota','No existe','Inestable; no']]
    pd.DataFrame(clasificacion,columns=['regimen','signo_monotonia','magnitud','limite','estabilidad_sentido']).to_csv(Path(raiz)/'resultados/tablas/clasificacion.csv',index=False)
    texto=r'''\begin{table}[htbp]\centering\small
\caption{Clasificación de $V_n=V_0(1-hk)^n$ para $V_0,h,k>0$.}\label{tab:clasificacion}
\begin{tabular}{p{1.7cm}p{2.5cm}p{2.2cm}p{1.5cm}p{4.3cm}}
\toprule Régimen & Signo y monotonía & Magnitud & Límite & Estabilidad; sentido físico\\\midrule
'''
    for fila in clasificacion:
        texto+=' & '.join(['$'+fila[0]+'$']+fila[1:])+r'\\'+'\n'
    texto+=r'''\bottomrule\end{tabular}
\par\smallskip\footnotesize Nota. En regímenes alternantes no hay monotonía de $V_n$. ``Frontera'' indica magnitud acotada sin amortiguación.
\end{table}'''
    (carpeta/'clasificacion.tex').write_text(texto,encoding='utf-8')
    def fila(nombre,**filtros):
        df=datos[nombre]
        for k,v in filtros.items():
            df=df[df[k]==v]
        return df.iloc[0]
    macros={
      'ErrorEulerUno':fila('error',h=1).error_maximo,
      'ErrorEulerPequeno':fila('error',h=.01).error_maximo,
      'ErrorHeunUno':fila('comparacion',metodo='Heun',h=1).error_maximo,
      'ErrorHeunMedio':fila('comparacion',metodo='Heun',h=.5).error_maximo,
      'ErrorEulerDecima':fila('error',h=.1).error_maximo,
      'ErrorHeunDecima':fila('comparacion',metodo='Heun',h=.1).error_maximo,
      'ErrorEulerMediaDecima':fila('error',h=.05).error_maximo,
      'BcincoEuler':fila('vulnerabilidades',organizacion='B',h=1,t=5).aproximacion,
      'BcincoRef':fila('vulnerabilidades',organizacion='B',h=1,t=5).referencia,
      'BcincoError':fila('vulnerabilidades',organizacion='B',h=1,t=5).error_absoluto,
      'ExtendidoFinal':fila('extendido',lambda_tasa=200).valor_final,
      'ExtendidoEquilibrio':fila('extendido',lambda_tasa=200).equilibrio,
      'ExtendidoDistancia':fila('extendido',lambda_tasa=200).distancia_equilibrio,
      'VersionPython':platform.python_version(),'VersionNumpy':np.__version__,
      'VersionPandas':pd.__version__,'VersionMatplotlib':matplotlib.__version__}
    (carpeta/'valores.tex').write_text('\n'.join('\\newcommand{\\'+k+'}{'+numero(v)+'}' for k,v in macros.items()),encoding='utf-8')
    (Path(raiz)/'verificacion/tablas_latex.json').write_text(json.dumps(auditoria,ensure_ascii=False,indent=2),encoding='utf-8')


def compilar(raiz=RAIZ):
    """Compila en carpeta temporal externa al ZIP; exporta sólo PDF final."""
    raiz=Path(raiz)
    for cmd in ['pdflatex','biber']:
        if not shutil.which(cmd):
            raise RuntimeError(f'No está disponible {cmd}; instalar TeX Live o MiKTeX con biblatex-apa')
    # Directorio oculto excluido al empaquetar; necesario para auxiliares.
    build=raiz/'.build'
    build.mkdir(exist_ok=True)
    directorio=raiz/'informe'
    latex=['pdflatex','-interaction=nonstopmode','-halt-on-error',f'-output-directory={build}', 'informe.tex']
    comandos=[latex,['biber',f'--input-directory={build}',f'--output-directory={build}','informe'],latex,latex]
    registros=[]
    for comando in comandos:
        proceso=subprocess.run(comando,cwd=directorio,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
        registros.append('\n'.join(linea.rstrip() for linea in proceso.stdout.splitlines()))
        if proceso.returncode:
            (raiz/'verificacion/compilacion.txt').write_text('\n'.join(registros),encoding='utf-8')
            raise RuntimeError('Falló la compilación; ver verificacion/compilacion.txt')
    log=(build/'informe.log').read_text(encoding='utf-8',errors='replace')
    problemas=[linea for linea in log.splitlines() if any(s in linea for s in ['Overfull','undefined','Please (re)run','Rerun to get','destination with the same identifier'])]
    (raiz/'verificacion/compilacion.txt').write_text('\n'.join(registros),encoding='utf-8')
    if problemas:
        raise RuntimeError('Revisar LaTeX: '+'; '.join(problemas))
    shutil.copy2(build/'informe.pdf',directorio/'informe.pdf')
