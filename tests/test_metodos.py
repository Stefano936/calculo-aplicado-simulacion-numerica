"""Comprobaciones independientes de fórmulas y contrato de los métodos."""
import unittest
import numpy as np
from src.metodos import euler, euler_mejorado
from src.metricas import indice_nodo


class Propiedades(unittest.TestCase):
    def test_predictor_corrector_distinto_del_punto_medio(self):
        # Oráculo racional para f=t² y nodos 0,3/10,6/10,9/10,1.
        # El punto medio da 653/2000 al final; no comparte este oráculo.
        t, x, n = euler_mejorado(lambda t, x: t*t, 0, 0, 1, .3)
        esperado = [0, 27/2000, 81/1000, 513/2000, 347/1000]
        np.testing.assert_allclose(x, esperado, rtol=0, atol=2e-15)
        self.assertEqual(n, 4)
        self.assertNotAlmostEqual(x[-1], 653/2000, places=10)

    def test_estado_predictor_y_pendientes(self):
        llamadas = []
        def f(t, x):
            llamadas.append((t, x))
            return t - x*x
        # Inicio (0,1), h=1/2: pendientes -1 y 1/4; predictor=1/2.
        # Corrección: 1 + (1/4)*(-1 + 1/4) = 13/16.
        _, x, _ = euler_mejorado(f, 1, 0, .5, .5)
        np.testing.assert_allclose(llamadas, [(0, 1), (.5, .5)])
        self.assertAlmostEqual(x[-1], 13/16)

    def test_lineal(self):
        for h in [1, .5, .1]:
            t, x, _ = euler(lambda t,x: 1, 0, 0, 10, h)
            np.testing.assert_allclose(x, t, atol=2e-13)

    def test_geometricas(self):
        for metodo in [euler, euler_mejorado]:
            for h in [1, .5, .1]:
                t,x,n = metodo(lambda t,x: -x, 1, 0, 10, h)
                factor = 1-h if metodo is euler else 1-h+h*h/2
                np.testing.assert_allclose(x, factor**np.arange(n+1), atol=1e-14)

    def test_vulnerabilidades(self):
        for k in [.1,.3,.7]:
            for h in [1,.5,.1]:
                t,x,n = euler(lambda t,x: -k*x, 1000, 0, 20, h)
                np.testing.assert_allclose(x,1000*(1-h*k)**np.arange(n+1),atol=2e-11)

    def test_dependencia_t_y_ultimo_paso(self):
        for metodo in [euler,euler_mejorado]:
            t,x,n = metodo(lambda t,x: t, 0, 0, 1, .3)
            np.testing.assert_allclose(t,[0,.3,.6,.9,1])
            if metodo is euler:
                self.assertAlmostEqual(x[-1],.36)
            else:
                np.testing.assert_allclose(x,t*t/2,atol=1e-14)
            self.assertEqual(n,4)

    def test_contrato(self):
        for metodo in [euler,euler_mejorado]:
            for args in [(2,2,2,.1),(2,3,3.2,1),(0,-2,1,.3),(1,0,10,.01)]:
                x0,t0,tf,h=args
                t,x,n=metodo(lambda t,x: 0,x0,t0,tf,h)
                self.assertEqual(len(t),n+1)
                self.assertEqual(len(x),len(t))
                self.assertEqual(t[-1],tf)
                self.assertEqual(x[0],x0)
                self.assertTrue(np.all(np.diff(t)>0))

    def test_invalidos(self):
        for metodo in [euler,euler_mejorado]:
            for args in [(0,0,1,0),(0,0,1,-1),(0,2,1,.1),
                         (np.nan,0,1,.1),(0,0,np.inf,.1),(0,0,1,np.nan),
                         ('a',0,1,.1),(0,0,1,True),(0,0,1,1e-10)]:
                with self.assertRaises(ValueError):
                    metodo(lambda t,x: x,*args)
            with self.assertRaises(ValueError):
                metodo(None,0,0,1,.1)
            with self.assertRaises(ValueError):
                metodo(lambda t,x: np.inf,0,0,1,.1)

    def test_evaluaciones(self):
        for metodo,multiplicador in [(euler,1),(euler_mejorado,2)]:
            llamadas=[]
            def f(t,x):
                llamadas.append(t)
                return -x
            t,x,n=metodo(f,1,0,1,.3)
            self.assertEqual(len(llamadas),multiplicador*n)
            llamadas.clear()
            metodo(f,1,0,0,.3)
            self.assertEqual(llamadas,[])

    def test_negativos_y_regimenes(self):
        for q in [.5,1,1.5,2,2.2]:
            t,x,n=euler(lambda t,x: -q*x,1,0,10,1)
            np.testing.assert_allclose(x,(1-q)**np.arange(n+1),atol=1e-13)
        self.assertLess(euler(lambda t,x:-1.5*x,1,0,1,1)[1][-1],0)

    def test_equilibrio_extendido(self):
        for lam in [0,50,100,200]:
            eq=lam/.3
            t,x,n=euler(lambda t,x:lam-.3*x,1000,0,20,.1)
            np.testing.assert_allclose(x,eq+(1000-eq)*.97**np.arange(n+1),atol=2e-11)
            self.assertTrue(np.all(np.diff(x)<0))
            self.assertGreater(x[-1],eq)
            _,constante,_=euler(lambda t,x:lam-.3*x,eq,0,20,.1)
            np.testing.assert_allclose(constante,eq,atol=1e-11)

    def test_nodos(self):
        t,_,_=euler(lambda t,x:0,0,0,20,.1)
        for objetivo in [5,10,15]:
            self.assertAlmostEqual(t[indice_nodo(t,objetivo)],objetivo)
        with self.assertRaises(ValueError):
            indice_nodo(t,5.05)

    def test_orden_convergencia(self):
        for metodo,orden in [(euler,1),(euler_mejorado,2)]:
            errores=[]
            for h in [.05,.025]:
                t,x,n=metodo(lambda t,x:-x,1,0,10,h)
                errores.append(np.max(np.abs(np.exp(-t)-x)))
            self.assertAlmostEqual(np.log2(errores[0]/errores[1]),orden,delta=.08)


if __name__=='__main__':
    unittest.main()
