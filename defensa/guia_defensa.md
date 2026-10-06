# Guía de defensa oral

Estudiar junto al PDF, el notebook y las tablas CSV. Los números se calculan con Python; los ejemplos siguientes explican las operaciones, sin sustituir los experimentos. No presentar los escenarios como datos reales ni como predicciones de incidentes.

1. **¿Qué aproxima Euler?** Aproxima el estado al siguiente tiempo usando la pendiente en el estado actual: x siguiente = x actual + paso × tasa. Si x'=1, desde x=0 y h=.5 se obtiene .5: la pendiente constante coincide con el cambio real. Ver sección 2.2 y Tabla 1.
2. **¿Qué significa h?** Es cuánto tiempo avanza cada iteración. En [0,10], h=.1 produce 100 pasos y 101 puntos. No es una tasa de remediación. Ver metodología y Tabla 2.
3. **¿Por qué aparece error?** La pendiente real cambia y Euler conserva sólo la inicial durante el intervalo. Además hay redondeo binario. Para x'=1 no hay error de discretización; para x'=-x sí. Figuras 1 a 3.
4. **¿Qué cambia en Heun?** Calcula un predictor con Euler, evalúa la pendiente en el tiempo final y ese estado predicho, y promedia ambas pendientes. No es punto medio. Necesita dos llamadas a f por paso. Sección 2.2 y Tabla 3.
5. **¿Error final o máximo?** Final compara el último nodo. Máximo toma la mayor distancia en todos los nodos disponibles. Para h=1, Euler da cero desde t=1: su error final es pequeño porque exp(-10) es pequeño; el error máximo cerca del inicio es mucho mayor. Tabla 3: Heun tiene menor máximo pero mayor final con h=1.
6. **¿Pasos o puntos?** Cada paso transforma un estado en el siguiente. El estado inicial no requiere un paso. Diez pasos generan once puntos. Si tf=t0 hay un punto y cero pasos. Tabla 1 y tests.
7. **¿Qué es k?** Rapidez fraccional de remediación en unidades de tiempo inverso. kV es una tasa de salida que cambia con V. C tiene k=.7 y desciende antes que B (.3) y A (.1). No son equipos corregidos fijos por iteración. Tabla 5 y Figura 4.
8. **¿Un k alto prueba mayor capacidad?** Sólo en poblaciones comparables y con mediciones equivalentes. Automatización y recursos podrían aumentarlo; inventario incompleto puede aparentar mejoras. Aquí los parámetros fueron dados, no ajustados a datos. Sección 5.3.
9. **¿Qué es λ?** Equipos que pasan al conjunto vulnerable por unidad de tiempo. Puede representar incorporación o cambios del estado de equipos; no cuenta CVE directamente. λ=200 no significa 200 CVE publicadas. Tabla 7 y Figura 8.
10. **¿Cómo se obtiene el equilibrio?** Igualando entrada y salida: 0=λ-kV, entonces V*=λ/k. Con λ=100 y k=.3 es 333.333… equipos agregados. Como V0=1000 es mayor, disminuye hacia ese nivel. Si empezara por debajo, crecería; si empezara exactamente allí, sería constante. Sección 5.5.
11. **¿Se alcanza exactamente el equilibrio?** En los escenarios Euler con h=.1, la distancia se multiplica por .97 en cada paso. Después de 200 sigue siendo positiva. No confundir igualdad de números redondeados con igualdad matemática. Tabla 7.
12. **¿Por qué aparecen negativos?** Euler básico multiplica por 1-hk. Si hk=1.5 el factor es -.5: desde 1000 se obtiene -500, luego 250. No representa equipos reales. Se conserva para mostrar el problema de malla. Figura 9 y Tabla 8.
13. **¿Estabilidad equivale a sentido físico?** No. Con 1<hk<2 la magnitud disminuye y converge a cero, pero el signo alterna. Para hk=2 hay alternancia sin convergencia; para hk>2 crece la magnitud. Positividad requiere hk≤1; descenso gradual positivo exige hk<1. Sección 5.4.
14. **¿Siempre conviene bajar h?** No: aumenta pasos y evaluaciones; en el caso lineal no mejora necesariamente. Hay que fijar tolerancia y considerar incertidumbre del modelo. En el exponencial sí bajaron los errores en los pasos estudiados. A igual costo de 200 llamadas, comparar Euler h=.05 con Heun h=.1. Tablas 2 a 4 y sección 5.2.
15. **¿CVE y CVSS son lo mismo?** CVE identifica un problema divulgado. CVSS comunica severidad. Ninguno equivale automáticamente al riesgo particular de una organización; hay que sumar explotación activa, exposición, criticidad y controles. Sección 2.5.
16. **¿Qué es T1190?** Técnica ATT&CK de acceso inicial mediante debilidades de aplicaciones o sistemas expuestos. Ejemplo defensivo: aplicación web con un fallo sin corregir; probar, desplegar y verificar el parche reduce el tiempo de exposición a ese fallo. El modelo no estima ataques ni probabilidades. Sección 5.6.
17. **¿Qué limita el modelo?** Equipos tratados de forma homogénea, k y λ constantes, ausencia de población total, capacidad y retrasos, severidades distintas e inventario incompleto. Básico no incorpora entradas; extendido sí, como flujo constante. No hay calibración real. Sección 5.7.
18. **¿Cómo sabemos que el código funciona?** Se comprobaron fórmulas geométricas independientes, función dependiente de t, último paso ajustado, tiempos finales, conteo de llamadas, entradas inválidas y todas las combinaciones. El notebook se ejecuta con kernel nuevo. Ver registro de pruebas y matriz.

## Demostración corta

Abrir el notebook y señalar: caso lineal; fila h=1 de la comparación; tabla de 27 observaciones; clasificación de hk; equilibrio extendido. Ejecutar las pruebas desde la raíz con `python -m unittest discover -s tests -v`. Para explicar el último paso, mostrar f(t,x)=t en [0,1], h=.3: tiempos 0,.3,.6,.9,1 y cuatro pasos; Heun coincide con t²/2 en los nodos.

## Cierre sugerido

“Verificamos métodos iterativos y medimos sus errores y costos. La elección depende de la métrica y del paso; estabilidad no garantiza cantidades físicas. La remediación y aparición explican tendencias bajo supuestos, pero para decisiones reales se necesitan datos y un modelo más detallado”.
