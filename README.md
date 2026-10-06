# Simulación numérica aplicada a ciberseguridad

Stefano Francolino · Cálculo Aplicado · Universidad Católica del Uruguay.

Entrega: informe en LaTeX y PDF, métodos Python, notebook ejecutado, datos completos, figuras y verificaciones. Repositorio público autorizado por el usuario: [Stefano936/calculo-aplicado-simulacion-numerica](https://github.com/Stefano936/calculo-aplicado-simulacion-numerica). Se conserva también la entrega local y ZIP. Los escenarios son hipotéticos.

## Instalación

Python **3.12.14** fue usado para esta entrega (Python 3.12 recomendado). Desde esta carpeta:

```console
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
```

LaTeX requiere TeX Live o MiKTeX con `pdflatex`, `biber`, `biblatex-apa`, `babel-spanish`, `lmodern`, `microtype`, `placeins`, `booktabs`, `longtable`, `caption`, `csquotes` y `hyperref`. No hay servicios pagos. MiKTeX puede requerir instalar paquetes faltantes; hacerlo antes de una ejecución desconectada.

## Reproducir todo

```console
python -m src.generar_entregables
```

Este comando genera experimentos, CSV, gráficas, recursos LaTeX, notebook desde un kernel limpio, pruebas, PDF con Biber y pasadas de referencias, auditoría y ZIP. Si falla alguna verificación detiene la entrega con un mensaje, sin inventar resultados. El ZIP aparece junto a esta carpeta y excluye entornos, auxiliares y cachés. Para regenerar sólo cálculos y recursos sin LaTeX ni notebook:

```console
python -m src.generar_entregables --sin-pdf --sin-notebook
```

## Comandos independientes

```console
python -m src.experimentos
python -m unittest discover -s tests -v
python -m src.generar_entregables --solo-pdf
```

Recompilación manual, desde `informe/`, con los recursos ya entregados:

```console
pdflatex -interaction=nonstopmode -halt-on-error informe.tex
biber informe
pdflatex -interaction=nonstopmode -halt-on-error informe.tex
pdflatex -interaction=nonstopmode -halt-on-error informe.tex
```

Las tablas se generan desde los mismos DataFrames que los CSV. No editar a mano `informe/generados/`: cualquier cambio de parámetros debe regenerarse por Python antes de compilar.

## Notebook

Abrir `notebooks/proyecto_calculo.ipynb` con Jupyter, VS Code u otro lector compatible. El notebook entregado incluye salidas. Para ejecución interactiva puede instalarse opcionalmente `jupyterlab` y ejecutar `jupyter lab`. Usar un kernel del entorno anterior y **Restart Kernel and Run All**. La primera celda busca la raíz del proyecto desde la raíz o desde `notebooks/`; no hay rutas personales ni estados ocultos. La ejecución automática no necesita JupyterLab y crea una especificación de kernel temporal con el Python activo.

## Organización

- `src/metodos.py`: Euler y Heun escalares, genéricos y documentados.
- `src/metricas.py`: errores y selección robusta de nodos.
- `src/experimentos.py`: única fuente de cálculos y escenarios.
- `src/visualizacion.py`: exportación PNG a 240 dpi y PDF vectorial.
- `src/informe.py`: tablas automáticas, macros numéricas y compilación.
- `src/notebook.py`: creación y ejecución del notebook.
- `src/generar_entregables.py`: proceso completo y ZIP.
- `src/verificacion.py`: cobertura, auditoría y hashes.
- `informe/informe.tex`, `informe.pdf`, `referencias.bib`: informe editable y final.
- `resultados/tablas/`: tablas resumidas y trayectorias completas con 17 cifras.
- `resultados/figuras/`: nueve figuras en PNG y PDF.
- `tests/`: propiedades matemáticas y cobertura experimental.
- `verificacion/`: matriz inicial/final, pruebas, compilación, revisión y manifiesto.
- `defensa/guia_defensa.md`: preguntas y ejemplos de defensa.

## Supuestos y límites

Tiempo en unidades genéricas; k en tiempo inverso; λ en equipos por unidad de tiempo. V es cantidad agregada o esperada. Tasas constantes, poblaciones hipotéticas sin calibración ni población total explícita. Para el modelo extendido se adoptó [0,20], h=.1. No se redondean ni recortan estados durante la simulación. Hay límite explícito de 10 millones de pasos y comprobación de avance temporal. Precisión numérica no implica capacidad para predecir ataques.

Las fuentes web se consultaron el 6 de octubre de 2026. El acceso directo a CISA falló; su descripción oficial de KEV se contrastó mediante resultados indexados del dominio oficial, y no se usaron filas individuales del catálogo. CVE se consultó mediante su FAQ oficial archivada. La matriz y `fuentes_consultadas.csv` registran estos detalles.

La revisión visual humana del PDF no se automatiza como juicio infalible: la entrega incluye un registro de inspección. Al cambiar contenido o parámetros, volver a revisar las páginas renderizadas, además de las pruebas automáticas.
