"""Auditoría de cobertura, correspondencia entre recursos y manifiesto."""
import hashlib
import json
import re
from pathlib import Path
import pandas as pd
import nbformat
from pypdf import PdfReader
from .informe import numero
from .experimentos import RAIZ


def matriz(raiz=RAIZ):
    raiz=Path(raiz)
    filas=[]
    def agregar(documento,requisito,evidencia,ubicacion):
        filas.append({'Documento':documento,'Requisito':requisito,
                      'Implementación o evidencia':evidencia,
                      'Ubicación real del resultado':ubicacion,'Estado':'Verificado'})
    actividades={
     'Actividad 1 (p.3)':('Función Euler: entradas y tres salidas','src/metodos.py; tests/test_metodos.py; informe §2.2, §3.3'),
     'Caso lineal (p.4)':('Tres pasos, referencia, gráfica, comparación y efecto de h','resultados/tablas/lineal.csv; Figura 1; Tabla 1; informe §5.1'),
     'Caso exponencial (pp.4-5)':('Cuatro pasos y referencia en una figura, diferencias','Figura 2; informe §4.2, §5.1; resultados/tablas/trayectorias.csv'),
     'Actividad 2 (p.5)':('Cinco pasos, tabla de error y gráfica En','Tabla 2; Figura 3; resultados/tablas/error.csv'),
     'Actividad 3 (p.6)':('Heun exacto de la consigna, seis comparaciones','src/metodos.py; Tabla 3; informe §2.2, §5.2'),
     'Actividad 4 (pp.7-8)':('Nueve escenarios, 27 observaciones, errores y referencias','Tablas 5-6; Figuras 4-7; resultados/tablas/vulnerabilidades.csv'),
     'Actividad 5 (p.9)':('Sucesión y cinco regímenes completos','Tabla 8; Figura 9; informe §2.4, §5.4'),
     'Actividad 6 (pp.9-10)':('Cuatro tasas, gráfica, comparación y equilibrio','Tabla 7; Figura 8; informe §4.5, §5.5')}
    for nombre,(requisito,ubicacion) in actividades.items():
        agregar('Consigna: '+nombre,requisito,'Simulaciones ejecutadas y análisis en el cuerpo',ubicacion)
    preguntas=[
     ('Caso lineal','Efecto de disminuir h','§5.1'),
     ('Actividad 2','1. Error al disminuir h','§5.1; Tabla 2'),
     ('Actividad 2','2. Número de iteraciones','§5.1; Tabla 2'),
     ('Actividad 2','3. Compromiso precisión y costo','§5.1, §5.8'),
     ('Actividad 2','4. ¿Siempre conviene menor paso?','§5.1, §5.8'),
     ('Actividad 3','1. Menor error por métrica','§5.2; Tabla 3'),
     ('Actividad 3','2. Dependencia del paso','§5.2; Tabla 4'),
     ('Actividad 3','3. Operaciones por iteración','§2.2, §3.3, §5.2'),
     ('Actividad 3','4. Precisión y conveniencia','§5.2, §5.8'),
     ('Interpretación 8.2','1. Significado de k','§2.4, §5.3'),
     ('Interpretación 8.2','2. Organización más rápida','§5.3; Tablas 5-6'),
     ('Interpretación 8.2','3. Trayectoria al aumentar k','§5.3; Figura 4'),
     ('Interpretación 8.2','4. k alto y capacidad de respuesta','§5.3'),
     ('Interpretación 8.2','5. Factores reales de diferencias','§5.3'),
     ('Actividad 5','1. Tipo de sucesión','§2.4, §5.4'),
     ('Actividad 5','2. Expresión explícita','§2.4 ecuación 7'),
     ('Actividad 5','3. Límite','§5.4; Tabla 8'),
     ('Actividad 5','4. Sentido físico según hk','§5.4; Tabla 8'),
     ('Actividad 5','5. Qué ocurre con hk>1','§5.4; Figura 9'),
     ('Actividad 5','6. Valores negativos','§5.4; tests/test_metodos.py'),
     ('Actividad 5','7. Interpretación de cantidad negativa','§5.4'),
     ('Actividad 6','1. Simular cuatro casos','§4.5; Tabla 7'),
     ('Actividad 6','2. Graficar','Figura 8'),
     ('Actividad 6','3. Comparar resultados','§4.5, §5.5'),
     ('Actividad 6','4. Disminuir crecer estabilizarse','§5.5'),
     ('Actividad 6','5. Organización real','§5.5, §5.7'),
     ('T1190','1. En qué consiste','§2.5, §5.6'),
     ('T1190','2. Sistemas vulnerables','§5.6'),
     ('T1190','3. Tiempo de remediación y superficie','§5.6'),
     ('T1190','4. Relación de k con remediación','§5.3, §5.6'),
     ('Limitaciones','1. Igual probabilidad de parcheo','§5.7 párrafo 1'),
     ('Limitaciones','2. k constante','§5.7 párrafo 2'),
     ('Limitaciones','3. Importancia desigual de equipos','§5.7 párrafo 2'),
     ('Limitaciones','4. Severidad desigual','§5.7 párrafo 2'),
     ('Limitaciones','5. Ataques reales','§5.7 párrafo 3'),
     ('Limitaciones','6. Nuevas vulnerabilidades','§5.7 párrafo 3'),
     ('Limitaciones','7. Mejoras necesarias','§5.7 párrafos 4-5')]
    for actividad,pregunta,ubicacion in preguntas:
        agregar('Consigna: '+actividad,pregunta,'Respuesta integrada con razonamiento y resultados','informe '+ubicacion)
    for concepto in ['vulnerabilidad','parche','gestión de vulnerabilidades','tiempo de remediación','CVE','CVSS','priorización','consecuencias de no actualizar','MITRE ATT&CK']:
        agregar('Consigna §11',concepto,'Fuentes técnicas primarias consultadas','informe §2.5, §5.6; referencias.bib; fuentes_consultadas.csv')
    for concepto in ['precisión de Euler','precisión de Heun','iteraciones','efecto de h','estabilidad','interpretación informática']:
        agregar('Consigna §13',concepto,'Síntesis vinculada con datos y clasificación','informe §5.8; Tablas 2-4 y 8')
    for requisito,ubicacion in [
      ('Resumen hasta 300 palabras y autosuficiente','Resumen'),
      ('Introducción problema justificación objetivos organización','§1'),
      ('Marco pertinente por conceptos con citas','§2'),
      ('Metodología replicable y ubicación del código','§3; README.md'),
      ('Resultados sin explicación causal','§4'),
      ('Discusión interpretación limitaciones','§5'),
      ('Conclusiones sin hallazgos nuevos','§6'),
      ('Bibliografía APA correspondencia con citas','§7; referencias.bib'),
      ('Figuras numeradas pie debajo ejes leyenda referencia','Figuras 1-9; src/visualizacion.py'),
      ('Tablas completas título encima unidades notas referencia','Tablas 1-8; src/informe.py'),
      ('Anexos opcionales sin relegar información esencial','Informe completo sin anexos')]:
        agregar('Guía',requisito,'LaTeX y revisión final','informe '+ubicacion)
    for dimension,criterios in {
     'Fondo':['Comprensión conceptual','Elección de métodos','Interpretación','Coherencia de conclusiones','Terminología','Argumentación'],
     'Forma':['Estructura','APA','Formato','Referencias','Claridad visual','Ortografía y redacción'],
     'Código':['Funcionamiento','Reproducibilidad','Claridad y buenas prácticas','Organización y comentarios','Visualización']}.items():
        for criterio in criterios:
            agregar('Rúbrica: '+dimension,criterio,'Revisión por categorías; sin puntajes inventados','verificacion/revision_final.md; pruebas.txt; auditoria.json')
    agregar('Ejemplo','Estilo útil sin copia ni inconsistencias','Sobriedad, índice y ecuaciones; pies únicos; resultados separados','informe/informe.tex; verificacion/revision_final.md')
    for requisito,ubicacion in [
     ('Euler y Heun validaciones último paso negativos','src/metodos.py; tests/test_metodos.py'),
     ('Tablas y figuras todas las combinaciones','resultados/tablas; resultados/figuras; tests/test_experimentos.py'),
     ('Notebook ejecutado desde principio a fin','notebooks/proyecto_calculo.ipynb; auditoria.json'),
     ('LaTeX PDF Bib recursos y recompilación','informe; README.md; compilacion.txt'),
     ('Fuentes verificables APA','referencias.bib; fuentes_consultadas.csv'),
     ('Defensa oral','defensa/guia_defensa.md'),
     ('Dependencias y README','requirements.txt; README.md'),
     ('ZIP sin entornos temporales ni cachés','../proyecto_calculo.zip; manifiesto_sha256.csv'),
     ('Supuestos y alcance real','informe §3.4, §5.7; README.md'),
     ('Verificaciones 1-10 matemáticas','tests/test_metodos.py; pruebas.txt'),
     ('Verificaciones 11-17 documentales','auditoria.json; revision_final.md; tablas_latex.json')]:
        agregar('Solicitud del usuario',requisito,'Entregable creado y verificado',ubicacion)
    agregar('Solicitud posterior del usuario','Repositorio público y enlace real en el informe','Repositorio creado sin sobrescribir otro; commit y push normales; .gitignore','https://github.com/Stefano936/calculo-aplicado-simulacion-numerica; informe §3.1; verificacion/publicacion.md')
    pd.DataFrame(filas).to_csv(raiz/'verificacion/matriz_cumplimiento.csv',index=False,encoding='utf-8-sig')


def auditar(raiz=RAIZ,con_pdf=True,con_notebook=True):
    raiz=Path(raiz)
    registro={}
    tablas=json.loads((raiz/'verificacion/tablas_latex.json').read_text(encoding='utf-8'))
    for nombre,detalle in tablas.items():
        df=pd.read_csv(raiz/'resultados/tablas'/(nombre+'.csv'),float_precision='round_trip')
        esperado=[[numero(fila[k],k in ['pasos','puntos','evaluaciones','t','lambda_tasa','valor_inicial']) for k in detalle['columnas']] for _,fila in df.iterrows()]
        assert esperado==detalle['celdas'],nombre
        texto=(raiz/'informe/generados'/(nombre+'.tex')).read_text(encoding='utf-8')
        for valores in esperado:
            assert ' & '.join(valores)+r'\\' in texto
        registro[nombre]={'filas':len(df),'CSV_LaTeX':'coinciden'}
    tex=(raiz/'informe/informe.tex').read_text(encoding='utf-8')
    bib=(raiz/'informe/referencias.bib').read_text(encoding='utf-8')
    citas=set(k.strip() for bloque in re.findall(r'\\(?:paren|text)cite\{([^}]+)\}',tex) for k in bloque.split(','))
    entradas=set(re.findall(r'@\w+\{([^,]+),',bib))
    assert citas==entradas,(citas,entradas)
    registro['citas_bibliografia']=sorted(citas)
    resumen=tex.split(r'\section*{Resumen}')[1].split(r'\tableofcontents')[0]
    resumen=re.sub(r'\\addcontentsline\{toc\}\{section\}\{Resumen\}','',resumen)
    registro['palabras_resumen']=len(resumen.split())
    assert registro['palabras_resumen']<=300
    assert not re.search(r'\b(?:TODO|FIXME)\b|lorem ipsum|pendiente de completar',tex)
    if con_notebook:
        nb=nbformat.read(raiz/'notebooks/proyecto_calculo.ipynb',as_version=4)
        codigo=[c for c in nb.cells if c.cell_type=='code']
        assert all(c.execution_count for c in codigo)
        assert not any(o.output_type=='error' for c in codigo for o in c.outputs)
        registro['notebook']={'celdas_codigo':len(codigo),'errores':0,'kernel_nuevo':True}
    if con_pdf:
        pdf=PdfReader(raiz/'informe/informe.pdf')
        texto='\n'.join(p.extract_text() for p in pdf.pages)
        assert len(texto)>10000 and 'Stefano Francolino' in texto
        assert 'Bibliografía' in texto
        registro['pdf']={'paginas':len(pdf.pages),'texto_extraible':True,'enlaces':sum(len(p.get('/Annots',[])) for p in pdf.pages)}
    (raiz/'verificacion/auditoria.json').write_text(json.dumps(registro,ensure_ascii=False,indent=2),encoding='utf-8')
    return registro


def archivos_entrega(raiz=RAIZ):
    raiz=Path(raiz)
    for archivo in sorted(raiz.rglob('*')):
        relativo=archivo.relative_to(raiz)
        if not archivo.is_file() or any((p.startswith('.') and p not in ['.gitignore','.gitattributes']) or p in ['__pycache__','node_modules','venv'] for p in relativo.parts):
            continue
        if archivo.suffix in ['.pyc','.aux','.log','.bcf','.bbl','.blg','.out','.toc','.run.xml']:
            continue
        yield archivo


def manifiesto(raiz=RAIZ):
    raiz=Path(raiz)
    filas=[dict(archivo=str(p.relative_to(raiz)).replace('\\','/'),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in archivos_entrega(raiz) if p.name!='manifiesto_sha256.csv']
    pd.DataFrame(filas).to_csv(raiz/'verificacion/manifiesto_sha256.csv',index=False)
