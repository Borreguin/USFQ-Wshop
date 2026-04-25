import unittest

from Torres import ejecutar_torres_hanoi


class TestTorresHanoi(unittest.TestCase):
    def test_movimientos_minimos_y_estado_final(self):
        resultado = ejecutar_torres_hanoi(n_discos=4, mostrar_pasos=False)
        self.assertEqual(resultado["movimientos_reales"], 15)
        self.assertEqual(resultado["movimientos_teoricos"], 15)
        self.assertTrue(resultado["es_optimo"])
        self.assertTrue(resultado["solucion_correcta"])
        self.assertEqual(resultado["torres_final"]["A"], [])
        self.assertEqual(resultado["torres_final"]["B"], [])
        self.assertEqual(resultado["torres_final"]["C"], [4, 3, 2, 1])


if __name__ == "__main__":
    unittest.main()
