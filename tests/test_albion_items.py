import unittest

from database.armas import FAMILIAS
from services.albion_items import buscar_item_por_nombre, obtener_url_sprite


class AlbionItemsTests(unittest.TestCase):
    def test_resuelve_nombres_oficiales_en_espanol(self):
        self.assertEqual(buscar_item_por_nombre("Ballesta"), "T4_2H_CROSSBOW")
        self.assertEqual(buscar_item_por_nombre("Ballesta pesada"), "T4_2H_CROSSBOWLARGE")

    def test_generates_sprite_url(self):
        url = obtener_url_sprite("T4_2H_CROSSBOW")
        self.assertIn("T4_2H_CROSSBOW", url)

    def test_todas_las_armas_del_catalogo_resuelven_un_sprite(self):
        armas = [arma for familia in FAMILIAS.values() for arma in familia]
        faltantes = [arma for arma in armas if not buscar_item_por_nombre(arma)]
        self.assertEqual(faltantes, [])
