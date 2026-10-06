# Revisión final de fondo, forma y código

La revisión usa las categorías de la rúbrica. No asigna nota, puntos ni ponderaciones. Se registran hallazgos reales y correcciones, además de las evidencias de verificación. No constituye una evaluación docente ni certifica que no pueda detectarse alguna mejora posterior.

## Fondo

- **Error grave detectado en borrador y resuelto:** una comparación de costo afirmaba que Heun h=.5 mejoraba el máximo de Euler h=.1. Los valores ejecutados contradicen esa afirmación (.022746 frente a .019201). Se sustituyó por una comparación válida a 200 evaluaciones: Heun h=.1 frente a Euler h=.05. La prueba `test_convergencia_y_costo` verifica la desigualdad usada en el informe.
- Se revisaron la derivación de Euler, la fórmula exacta de Heun, errores absolutos frente a diferencias con signo y la excepción h=1. Tablas 1-4 y fórmulas geométricas independientes sustentan los resultados.
- Se explican los cinco regímenes de hk, distinguiendo positividad, convergencia y frontera sin amortiguación. Se conservan valores negativos. Tabla 8 y Figura 9.
- Las nueve combinaciones de organizaciones y 27 observaciones requeridas están completas. Se interpreta k sin inventar datos y λ como equipos por unidad de tiempo. El equilibrio se obtiene por balance y los finales no se declaran iguales a él.
- CVE, CVSS y ATT&CK cumplen funciones diferentes. T1190 se explica con un ejemplo defensivo y sin inferir incidentes o probabilidades. Las siete preguntas de limitaciones tienen ubicación individual en la matriz.
- Las conclusiones se limitan a los hallazgos presentados y responden los objetivos. Las mejoras propuestas no se presentan como implementadas.

## Forma

- **Error leve detectado y resuelto:** una tabla corta de tres filas se separaba entre páginas. Las tablas cortas ahora son indivisibles; la tabla de 27 filas inicia una página y está completa en el cuerpo.
- **Imperfección detectada y resuelta:** el índice comenzaba bajo el resumen y continuaba en otra página. Se separó mediante salto automático y se recompiló para verificar su correspondencia.
- **Error leve detectado y resuelto:** la portada y la primera página numerada compartían un destino PDF `page.1`. Se desactivó el anclaje de página sólo durante la portada y se recompiló; el registro final comprueba que no haya identificadores duplicados.
- El resumen contiene 228 palabras según la auditoría. El informe presenta autor, institución, asignatura, siete secciones y bibliografía APA generada con biblatex-apa/Biber. No se inventaron docente, grupo ni fecha de entrega.
- Nueve figuras con pie único debajo; ocho tablas con título encima y notas de unidades. Referencias cruzadas automáticas. Se revisaron los márgenes, símbolos y todas las páginas renderizadas. Gráficas exportadas a 240 dpi y PDF vectorial, sin recortes observados.
- Correspondencia de ocho claves citadas con ocho entradas bibliográficas comprobada automáticamente. La primera pasada tenía referencias sin resolver; las pasadas posteriores con Biber las resolvieron. El registro final no contiene referencias indefinidas ni cajas desbordadas.
- Fuentes primarias registradas: matemáticas, NIST, CVE, FIRST, CISA y MITRE. La limitación de acceso directo a CISA está documentada: se verificó su descripción en resultados indexados oficiales, sin consultar filas específicas.

## Código

- **Error grave detectado y resuelto:** el generador inicial tenía una cadena Python mal escapada al construir macros LaTeX y no ejecutaba. Se corrigió y el proceso completo se ejecutó correctamente.
- **Error leve detectado y resuelto:** el detector de marcadores buscaba `TODO` sin límites y rechazaba palabras españolas normales. Se acotó a marcadores explícitos completos; la auditoría pasó.
- **Imperfección detectada y resuelta:** cadenas del notebook y tablas emitían advertencias por escapes matemáticos. Se corrigieron los escapes y la colocación tipográfica de primas en los títulos de tablas.
- 15 pruebas pasan: 11 de propiedades de métodos y 4 de cobertura y métricas experimentales. Incluyen contratos, validaciones, dependencia explícita de t, último paso, evaluaciones, signos, equilibrio y convergencia.
- Notebook construido y ejecutado con kernel temporal limpio: nueve celdas de código, cero salidas de error; vuelve a ejecutar las pruebas y muestra los resultados.
- Los CSV y las celdas LaTeX se compararon automáticamente. Una ejecución independiente en otra carpeta produjo nueve CSV de experimentos con SHA-256 idénticos; `reproduccion.json` registra la comparación.
- Organización por módulos, docstrings y nombres claros; sin fórmulas específicas dentro de los integradores. Costos contados con llamadas reales. Último paso usa el incremento real y no se recortan estados.
- `.gitignore` excluye credenciales, entornos, cachés y auxiliares. El ZIP incluye únicamente entregables y recursos; el manifiesto registra sus hashes. No se incluyen las dependencias instaladas ni los documentos ajenos usados como referencia.

## Herramientas y límites

El compilador integrado de Codex falló con `Unable to find standard directories for platform`. Se mantuvo el editor abierto y se utilizó MiKTeX instalado (`pdflatex` y Biber), que produjo el PDF final. El fallo del compilador integrado no impide la recompilación local con los comandos del README.

Jupyter emitió una advertencia de transporte TCP del kernel local. No hubo error de ejecución. La simulación no usa servicios de cálculo remotos.

No quedan entregables esenciales pendientes. Permanece la limitación de consulta directa de CISA ya indicada y el alcance hipotético sin calibración real. La revisión visual se registra en `revision_visual.json`; después de cualquier edición corresponde repetirla.
