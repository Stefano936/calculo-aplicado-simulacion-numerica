"""Cobertura y consistencia de las tablas producidas por los experimentos."""
import unittest
from pathlib import Path
import pandas as pd
import numpy as np

RAIZ=Path(__file__).resolve().parents[1]


class Cobertura(unittest.TestCase):
    def leer(self,nombre):
        return pd.read_csv(RAIZ/'resultados/tablas'/(nombre+'.csv'),float_precision='round_trip')

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
