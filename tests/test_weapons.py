import unittest

from database.armas import mostrar_nombre_arma, obtener_armas_por_rol


class WeaponDisplayTests(unittest.TestCase):

    def test_known_weapons_are_displayed_in_spanish(self):
        casos = {
            "Bear Paws": "Patas de oso",
            "Bloodletter": "Sangrador",
            "Deathgivers": "Concedemuertes",
            "Double Daggers": "Doble daga",
            "Spirit Hunter": "Cazador de espíritus",
            "Longbow": "Arco largo",
            "Heavy Mace": "Maza pesada",
            "Grailseeker": "Busca grial",
            "Holy Staff": "Bastón sagrado",
            "Great Holy Staff": "Gran bastón sagrado",
            "Blight Staff": "Bastón de la plaga",
            "Rampant Staff": "Bastón rampante",
            "Great Hammer": "Gran martillo",
            "Double Bladed Staff": "Bastón de doble hoja",
        }

        for original, esperado in casos.items():
            self.assertEqual(mostrar_nombre_arma(original), esperado)

    def test_unknown_weapons_keep_their_original_name(self):
        self.assertEqual(mostrar_nombre_arma("Arma nueva"), "Arma nueva")

    def test_common_content_roles_have_weapon_lists(self):
        armas = obtener_armas_por_rol("Tank", "Facciones")
        self.assertTrue(armas)
        self.assertIn("Maza pesada", armas)


if __name__ == "__main__":
    unittest.main()
