"""Errores en los nodos, sin redondeo previo."""
import numpy as np


def errores(t, x, referencia):
    ref = np.asarray(referencia(t), dtype=float)
    diferencia = np.asarray(x) - ref
    absoluto = np.abs(diferencia)
    return ref, diferencia, absoluto


def resumen(t, x, pasos, referencia, evaluaciones):
    _, _, error = errores(t, x, referencia)
    return dict(pasos=pasos, puntos=len(t), valor_final=x[-1],
                error_final=error[-1], error_maximo=error.max(),
                evaluaciones=evaluaciones)


def indice_nodo(t, objetivo):
    """Busca un nodo con tolerancia absoluta; no usa igualdad float exacta."""
    indices = np.flatnonzero(np.isclose(t, objetivo, rtol=0, atol=1e-10))
    if len(indices) != 1:
        raise ValueError(f"El tiempo {objetivo} no corresponde a un único nodo")
    return int(indices[0])
