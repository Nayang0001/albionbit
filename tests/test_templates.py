import tempfile
import unittest
from pathlib import Path

from database.models import Adventure
from services import plantilla_service


class PlantillaServiceTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        plantilla_service.PVP_PRIVATE = Path(self.temp_dir.name) / "pvp_private.json"
        plantilla_service.PVE_PRIVATE = Path(self.temp_dir.name) / "pve_private.json"
        self.service = plantilla_service.PlantillaService()

    def test_guardar_y_recuperar_plantillas_en_personalizado(self):
        aventura = Adventure(tipo="PvE", contenido="Personalizado", descripcion="Test")
        aventura.agregar_rol(nombre="Pierce", categoria="Pierce", emoji="🗡️", cantidad=1)

        ok, _ = self.service.guardar("Mi plantilla", aventura, 123)
        self.assertTrue(ok)

        plantillas = self.service.obtener_plantillas_usuario("PvE", "personalizado", 123)
        self.assertIn("Mi plantilla", plantillas)


if __name__ == "__main__":
    unittest.main()
