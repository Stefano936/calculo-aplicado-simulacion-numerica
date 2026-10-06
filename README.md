# Simulación numérica de sistemas dinámicos

Implementa Euler y el predictor-corrector con predicción Euler y promedio de
pendientes (denominado Heun en este proyecto). Simula crecimiento lineal,
decrecimiento exponencial, remediación de equipos vulnerables y aparición de
equipos vulnerables. Compara errores finales y máximos, pasos y evaluaciones.
Los escenarios son hipotéticos y utilizan unidades de tiempo genéricas.

## Instalación

Se requiere Python 3.12. Se verificó con Python 3.12.14.

```console
git clone https://github.com/Stefano936/calculo-aplicado-simulacion-numerica.git
cd calculo-aplicado-simulacion-numerica
python -m venv .venv
```

Activación en Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activación en Linux o macOS:

```sh
source .venv/bin/activate
```

Instalación para experimentos y pruebas:

```console
python -m pip install -r requirements.txt
```

Para ejecutar y abrir el notebook, instalar además:

```console
python -m pip install -r requirements-notebook.txt
```

Si PowerShell impide activar el entorno, usar directamente
`.\.venv\Scripts\python.exe` en lugar de `python` en los comandos siguientes.

## Ejecución

Desde la raíz del repositorio:

```console
python -m src.experimentos
python -m unittest discover -s tests -v
```

Los experimentos generan nueve CSV en `resultados/tablas/` y nueve figuras,
cada una en PNG de 240 dpi y PDF vectorial, en `resultados/figuras/`.
Estas carpetas se regeneran y están excluidas de Git. Cada ejecución
sobrescribe los resultados con los mismos nombres.

Para generar resultados, ejecutar pruebas y recrear el notebook desde un kernel nuevo:

```console
python -m src.generar_entregables
```

Sin dependencias de notebook:

```console
python -m src.generar_entregables --sin-notebook
```

Para abrir el notebook:

```console
python -m jupyterlab notebooks/proyecto_calculo.ipynb
```

Ejecutar todas las celdas en orden. El notebook importa los módulos del proyecto
y regenera las tablas y figuras; no necesita resultados preexistentes.

## Organización y verificaciones

- `src/metodos.py`: integradores escalares, validaciones y último paso ajustado.
- `src/metricas.py`: errores, resumen y consultas de nodos tolerantes al punto flotante.
- `src/experimentos.py`: experimentos separados y exportación de datos sin redondeo previo.
- `src/visualizacion.py`: configuración y exportación de figuras.
- `src/notebook.py`: creación y ejecución del notebook.
- `tests/`: fórmulas independientes, contratos, convergencia y parámetros de experimentos.

Las pruebas generan datos en una carpeta temporal, por lo que funcionan también
en un clon sin CSV. Los valores esperados de condiciones iniciales, intervalos,
pasos, organizaciones, tasas y tiempos se declaran independientemente del código
de producción. La prueba con `f(t,x)=t²` diferencia el predictor-corrector del
punto medio y comprueba el último paso ajustado. No se recortan estados negativos.
