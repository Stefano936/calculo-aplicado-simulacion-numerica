"""Simulaciones y exportación reproducible de CSV y figuras."""
from pathlib import Path
import numpy as np
import pandas as pd
from .metodos import euler, euler_mejorado
from .metricas import resumen, errores, indice_nodo
from .visualizacion import plt, guardar

RAIZ = Path(__file__).resolve().parents[1]
METODOS = {'Euler': euler, 'Heun': euler_mejorado}


def ejecutar(raiz=RAIZ):
    """Ejecuta todos los escenarios y exporta resultados deterministas."""
    raiz = Path(raiz)
    tablas, figuras = raiz / 'resultados/tablas', raiz / 'resultados/figuras'
    tablas.mkdir(parents=True, exist_ok=True)
    figuras.mkdir(parents=True, exist_ok=True)
    datos, trayectorias = {}, []

    def simular(modelo, metodo, h, f, x0, tf, ref, **parametros):
        contador = [0]
        def contada(t, x):
            contador[0] += 1
            return f(t, x)
        t, x, n = METODOS[metodo](contada, x0, 0, tf, h)
        r, d, err = errores(t, x, ref)
        serie = pd.DataFrame(dict(t=t, aproximacion=x, referencia=r,
                                  diferencia_con_signo=d, error_absoluto=err))
        serie['modelo'], serie['metodo'], serie['h'] = modelo, metodo, h
        for clave, valor in parametros.items():
            serie[clave] = valor
        trayectorias.append(serie)
        return t, x, dict(metodo=metodo, h=h, **parametros,
                          **resumen(t, x, n, ref, contador[0]))

    _lineal(simular, datos, figuras)
    _exponencial(simular, datos, figuras)
    _comparacion(simular, datos, figuras)
    _vulnerabilidades(simular, datos, figuras)
    _extendido(simular, datos, figuras)
    _regimenes(simular, datos, figuras)
    _convergencia(simular, datos, figuras)
    datos['trayectorias'] = pd.concat(trayectorias, ignore_index=True)
    for nombre, df in datos.items():
        df.to_csv(tablas / (nombre + '.csv'), index=False, float_format='%.17g')
    return datos


def _lineal(simular, datos, figuras):
    """Genera el experimento lineal y sus salidas."""
    filas = []
    fig, ax = plt.subplots()
    ax.plot([0, 10], [0, 10], 'k--', label='Referencia x=t', zorder=5)
    for h in [1, .5, .1]:
        t, x, fila = simular('lineal', 'Euler', h, lambda t, x: 1., 0, 10, lambda t: t)
        filas.append(fila)
        ax.plot(t, x, label=f'Euler h={h:g}', alpha=.7)
    ax.set_ylabel('x (sin unidad definida)')
    guardar(fig, figuras, 'lineal')
    datos['lineal'] = pd.DataFrame(filas)



def _exponencial(simular, datos, figuras):
    """Genera el experimento exponencial y sus salidas."""
    filas = []
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.7))
    fe, ejes_error = plt.subplots(1, 2, figsize=(9, 3.7))
    ref = lambda t: np.exp(-t)
    for ax in axs:
        tt = np.linspace(0, 10, 2001)
        ax.plot(tt, ref(tt), 'k--', label='Referencia exp(-t)')
        ax.set_ylabel('x (sin unidad definida)')
    for h in [1, .5, .1, .05, .01]:
        t, x, fila = simular('exponencial', 'Euler', h, lambda t, x: -x, 1, 10, ref)
        filas.append(fila)
        error = np.abs(ref(t) - x)
        ejes_error[0].plot(t, error, label=f'h={h:g}')
        positivos = error > 0
        ejes_error[1].semilogy(t[positivos], error[positivos], label=f'h={h:g}')
        if h != .05:
            for ax in axs:
                ax.plot(t, x, label=f'Euler h={h:g}')
    axs[1].set_xlim(0, 2)
    for ax in ejes_error:
        ax.set_ylabel(r'Error absoluto $E_n$')
    guardar(fig, figuras, 'exponencial')
    guardar(fe, figuras, 'errores')
    datos['error'] = pd.DataFrame(filas)



def _comparacion(simular, datos, figuras):
    """Genera el experimento comparacion y sus salidas."""
    ref = lambda t: np.exp(-t)
    filas = []
    for metodo in METODOS:
        for h in [1, .5, .1]:
            _, _, fila = simular('comparacion', metodo, h, lambda t, x: -x, 1, 10, ref)
            filas.append(fila)
    datos['comparacion'] = pd.DataFrame(filas)



def _vulnerabilidades(simular, datos, figuras):
    """Genera el experimento vulnerabilidades y sus salidas."""
    filas, resumenes = [], []
    fg, ag = plt.subplots()
    for org, k in [('A', .1), ('B', .3), ('C', .7)]:
        fig, ax = plt.subplots()
        ref = lambda t, k=k: 1000 * np.exp(-k * t)
        tt = np.linspace(0, 20, 2001)
        ax.plot(tt, ref(tt), 'k--', label=f'Referencia k={k:g}')
        for h in [1, .5, .1]:
            t, x, fila = simular('vulnerabilidades', 'Euler', h,
                                lambda t, x, k=k: -k*x, 1000, 20, ref,
                                organizacion=org, k=k)
            resumenes.append(fila)
            ax.plot(t, x, label=f'Euler h={h:g}')
            if h == 1:
                ag.plot(t, x, label=f'{org}: k={k:g}, h=1')
            for tiempo in [5, 10, 15]:
                i = indice_nodo(t, tiempo)
                referencia = ref(t[i])
                filas.append(dict(organizacion=org, k=k, h=h, t=tiempo,
                                  aproximacion=x[i], referencia=referencia,
                                  error_absoluto=abs(referencia-x[i])))
        ax.set_ylabel('V (equipos, cantidad agregada)')
        guardar(fig, figuras, 'organizacion_' + org)
    ag.set_ylabel('V (equipos, cantidad agregada)')
    guardar(fg, figuras, 'organizaciones')
    datos['vulnerabilidades'] = pd.DataFrame(filas)
    datos['vulnerabilidades_resumen'] = pd.DataFrame(resumenes)



def _extendido(simular, datos, figuras):
    """Genera el experimento extendido y sus salidas."""
    filas = []
    fig, ax = plt.subplots()
    for lam in [0, 50, 100, 200]:
        equilibrio = lam / .3
        # Referencia continua complementaria; no genera los estados Euler.
        ref = lambda t, eq=equilibrio: eq + (1000-eq)*np.exp(-.3*t)
        t, x, fila = simular('extendido', 'Euler', .1,
                            lambda t, x, l=lam: l-.3*x, 1000, 20, ref,
                            lambda_tasa=lam, k=.3)
        fila.update(valor_inicial=1000, equilibrio=equilibrio,
                    distancia_equilibrio=abs(x[-1]-equilibrio))
        filas.append(fila)
        trayectoria, = ax.plot(t, x, label=f'Euler, λ={lam}')
        etiqueta_equilibrio = f'{equilibrio:.2f}'.rstrip('0').rstrip('.')
        ax.axhline(equilibrio, color=trayectoria.get_color(), linestyle='--',
                   label=f'V* (λ={lam}) = {etiqueta_equilibrio}')
    ax.set_ylabel('V (equipos, cantidad agregada)')
    guardar(fig, figuras, 'extendido', leyenda_fuera=True)
    datos['extendido'] = pd.DataFrame(filas)



def _regimenes(simular, datos, figuras):
    """Genera el experimento regimenes y sus salidas."""
    filas = []
    fig, ax = plt.subplots()
    for q in [.5, 1, 1.5, 2, 2.2]:
        t, x, n = euler(lambda t, x, q=q: -q*x, 1, 0, 10, 1)
        ax.plot(t, x, 'o-', markersize=3, label=f'hk={q:g}')
        filas.extend(dict(hk=q, n=int(ti), valor=xi) for ti, xi in zip(t, x))
    ax.set_ylabel('V / V0 (adimensional)')
    guardar(fig, figuras, 'regimenes')
    datos['regimenes'] = pd.DataFrame(filas)



def _convergencia(simular, datos, figuras):
    """Genera el experimento convergencia y sus salidas."""
    filas = []
    for metodo in METODOS:
        previo = None
        for h in [.2, .1, .05, .025, .0125]:
            _, _, fila = simular('convergencia', metodo, h,
                                 lambda t, x: -x, 1, 10, lambda t: np.exp(-t))
            fila['orden_observado'] = np.nan if previo is None else np.log2(previo/fila['error_maximo'])
            previo = fila['error_maximo']
            filas.append(fila)
    datos['convergencia'] = pd.DataFrame(filas)


if __name__ == '__main__':
    resultados = ejecutar()
    print(resultados['comparacion'].to_string(index=False))
