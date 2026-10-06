"""Integradores explícitos para problemas escalares x'=f(t,x)."""
import math
from numbers import Real
import numpy as np


def _real_finito(valor, nombre):
    if isinstance(valor, (bool, np.bool_)) or not isinstance(valor, Real):
        raise ValueError(f"{nombre} debe ser un número real finito")
    valor = float(valor)
    if not math.isfinite(valor):
        raise ValueError(f"{nombre} debe ser finito")
    return valor


def _integrar(f, x0, t0, tf, h, mejorado):
    if not callable(f):
        raise ValueError("f debe ser una función callable f(t,x)")
    x0, t0, tf, h = [_real_finito(v, n) for v, n in
                       [(x0, 'x0'), (t0, 't0'), (tf, 'tf'), (h, 'h')]]
    if h <= 0 or tf < t0:
        raise ValueError("Se requiere h > 0 y tf >= t0")
    if tf == t0:
        return np.array([t0]), np.array([x0]), 0
    intervalo = tf - t0
    cociente = intervalo / h
    if not math.isfinite(cociente) or cociente > 10_000_000:
        raise ValueError("Malla demasiado grande: máximo 10 millones de pasos")
    # Evita un paso espurio si el cociente está a unos ulps de un entero.
    entero = round(cociente)
    if entero >= 1 and abs(cociente - entero) <= 8 * math.ulp(cociente):
        n = entero
    else:
        n = math.ceil(cociente)
    t = t0 + h * np.arange(n + 1, dtype=float)
    t[-1] = tf
    if np.any(np.diff(t) <= 0):
        raise ValueError("h no permite avanzar el tiempo en precisión float64")
    x = np.empty(n + 1)
    x[0] = x0
    for i in range(n):
        dt = t[i + 1] - t[i]
        pendiente = _real_finito(f(t[i], x[i]), 'f(t,x)')
        pred = _real_finito(x[i] + dt * pendiente, 'predicción')
        if mejorado:
            final = _real_finito(f(t[i + 1], pred), 'f(t+dt,pred)')
            x[i + 1] = _real_finito(x[i] + dt * (pendiente / 2 + final / 2), 'x siguiente')
        else:
            x[i + 1] = pred
    return t, x, n


def euler(f, x0, t0, tf, h):
    """Euler: x[n+1]=x[n]+dt*f(t[n],x[n]).

    Recibe función escalar f(t,x), estado inicial y tiempos reales finitos;
    exige h>0 y tf>=t0. Devuelve (tiempos, estados, número de pasos).
    Incluye el punto inicial, termina en tf y ajusta el último dt.
    No recorta estados negativos. Errores de entrada: ValueError.
    Protección de recursos: máximo 10 millones de pasos.
    """
    return _integrar(f, x0, t0, tf, h, False)


def euler_mejorado(f, x0, t0, tf, h):
    """Predictor Euler y corrección mediante el promedio de dos pendientes (Heun).

    Usa dt real también en predictor, corrector y tiempo de segunda etapa.
    Mismas entradas, salida, validaciones y límites que euler.
    Dos evaluaciones de f por paso; ninguna si tf=t0.
    """
    return _integrar(f, x0, t0, tf, h, True)
