"""Cobertura y consistencia de las tablas producidas por los experimentos."""
import unittest
import numpy as np
import tempfile
from functools import lru_cache
from src.experimentos import ejecutar

@lru_cache(maxsize=1)
def resultados_frescos():
    """Genera datos nuevos sin depender de CSV ni dejar resultados locales."""
    with tempfile.TemporaryDirectory(prefix='calculo-pruebas-') as temporal:
        return ejecutar(temporal)


class Cobertura(unittest.TestCase):
    def leer(self,nombre):
        return resultados_frescos()[nombre]

    def test_parametros_obligatorios_independientes(self):
        """Valores literales de los modelos, independientes de la configuración."""
        df = self.leer('trayectorias')
        esperado = {
            'lineal': (0, 10, {('Euler', 1), ('Euler', .5), ('Euler', .1)}),
            'exponencial': (1, 10, {('Euler', h) for h in [1, .5, .1, .05, .01]}),
            'comparacion': (1, 10, {(m, h) for m in ['Euler', 'Heun'] for h in [1, .5, .1]}),
            'vulnerabilidades': (1000, 20, {('Euler', h) for h in [1, .5, .1]}),
            'extendido': (1000, 20, {('Euler', .1)}),
            'convergencia': (1, 10, {(m, h) for m in ['Euler', 'Heun'] for h in [.2, .1, .05, .025, .0125]}),
        }
        self.assertEqual(set(df.modelo), set(esperado))
        for modelo, (x0, tf, pares) in esperado.items():
            subconjunto = df[df.modelo == modelo]
            self.assertEqual(set(zip(subconjunto.metodo, subconjunto.h)), pares)
            claves = ['metodo', 'h']
            if modelo == 'vulnerabilidades':
                claves += ['organizacion', 'k']
                self.assertEqual(set(zip(subconjunto.organizacion, subconjunto.k)),
                                 {('A', .1), ('B', .3), ('C', .7)})
            if modelo == 'extendido':
                claves += ['lambda_tasa']
                self.assertEqual(set(subconjunto.lambda_tasa), {0, 50, 100, 200})
                self.assertEqual(set(subconjunto.k), {.3})
            for clave, serie in subconjunto.groupby(claves):
                with self.subTest(modelo=modelo, parametros=clave):
                    self.assertEqual(serie.t.iloc[0], 0)
                    self.assertEqual(serie.t.iloc[-1], tf)
                    self.assertEqual(serie.aproximacion.iloc[0], x0)
                    h = clave[1]
                    n = round(tf / h)
                    self.assertEqual(len(serie), n+1)
                    np.testing.assert_allclose(serie.t, np.arange(n+1)*h, atol=2e-14)
                    if modelo == 'lineal':
                        ref = serie.t
                    elif modelo == 'vulnerabilidades':
                        k = {'A': .1, 'B': .3, 'C': .7}[clave[2]]
                        ref = 1000*np.exp(-k*serie.t)
                        np.testing.assert_allclose(serie.aproximacion,
                            1000*(1-h*k)**np.arange(n+1), atol=2e-11)
                    elif modelo == 'extendido':
                        lam = clave[2]
                        eq = lam/.3
                        ref = eq+(1000-eq)*np.exp(-.3*serie.t)
                        np.testing.assert_allclose(serie.aproximacion,
                            eq+(1000-eq)*.97**np.arange(n+1), atol=2e-11)
                    else:
                        ref = np.exp(-serie.t)
                    np.testing.assert_allclose(serie.referencia, ref, atol=1e-12)
        consultas = self.leer('vulnerabilidades')
        self.assertEqual(set(zip(consultas.organizacion, consultas.k, consultas.h, consultas.t)),
            {(o,k,h,t) for o,k in [('A',.1),('B',.3),('C',.7)]
             for h in [1,.5,.1] for t in [5,10,15]})
        for fila in consultas.itertuples():
            self.assertAlmostEqual(fila.aproximacion,
                1000*(1-fila.h*fila.k)**round(fila.t/fila.h), places=10)

    def test_combinaciones(self):
        for nombre,cantidad in [('lineal',3),('error',5),('comparacion',6),('vulnerabilidades',27),('vulnerabilidades_resumen',9),('extendido',4),('convergencia',10)]:
            self.assertEqual(len(self.leer(nombre)),cantidad)
        df=self.leer('vulnerabilidades')
        esperado={(o,h,t) for o in 'ABC' for h in [1,.5,.1] for t in [5,10,15]}
        self.assertEqual(set(zip(df.organizacion,df.h,df.t)),esperado)

    def test_metricas_trayectorias(self):
        df=self.leer('trayectorias')
        np.testing.assert_allclose(df.error_absoluto,np.abs(df.aproximacion-df.referencia),atol=1e-12)
        np.testing.assert_allclose(df.diferencia_con_signo,df.aproximacion-df.referencia,atol=1e-12)
        for nombre in ['lineal','error','comparacion','vulnerabilidades_resumen','extendido','convergencia']:
            modelo={'error':'exponencial','vulnerabilidades_resumen':'vulnerabilidades'}.get(nombre,nombre)
            for _,fila in self.leer(nombre).iterrows():
                serie=df[(df.modelo==modelo)&(df.metodo==fila.metodo)&(df.h==fila.h)]
                if nombre=='vulnerabilidades_resumen':
                    serie=serie[serie.organizacion==fila.organizacion]
                if nombre=='extendido':
                    serie=serie[serie.lambda_tasa==fila.lambda_tasa]
                self.assertEqual(len(serie),fila.pasos+1)
                self.assertAlmostEqual(serie.aproximacion.iloc[-1],fila.valor_final,places=12)
                self.assertAlmostEqual(serie.error_absoluto.max(),fila.error_maximo,places=12)
                self.assertAlmostEqual(serie.error_absoluto.iloc[-1],fila.error_final,places=12)
                self.assertEqual(fila.evaluaciones,fila.pasos*(1 if fila.metodo=='Euler' else 2))

    def test_h_uno_metricas(self):
        df=self.leer('comparacion').query('h == 1').set_index('metodo')
        self.assertLess(df.loc['Euler','error_final'],df.loc['Heun','error_final'])
        self.assertGreater(df.loc['Euler','error_maximo'],df.loc['Heun','error_maximo'])

    def test_convergencia_y_costo(self):
        df=self.leer('error')
        self.assertTrue(np.all(np.diff(df.error_maximo)<0))
        self.assertTrue(np.all(np.diff(df.pasos)>0))
        e=self.leer('error').query('h == .05').iloc[0]
        h=self.leer('comparacion').query("h == .1 and metodo == 'Heun'").iloc[0]
        self.assertEqual(e.evaluaciones,h.evaluaciones)
        self.assertLess(h.error_maximo,e.error_maximo)
