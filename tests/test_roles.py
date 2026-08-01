import asyncio
import json
import unittest
from pathlib import Path
from types import SimpleNamespace

from database.models import Adventure, Rol, limpiar_roles_conocidos
from services.aventura_service import AdventureService
from services.embed_service import EmbedService
from ui.adventure_view import AdventureView
from ui.selects.role_select import RoleSelect


class RoleDisplayTests(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()
        asyncio.set_event_loop(None)

    async def _crear_vista(self, aventura):
        return AdventureView(aventura)

    def test_core_role_types_stay_in_english(self):
        aventura = Adventure()

        roles = [
            ("Tank", "Tank"),
            ("Healer", "Healer"),
            ("Support", "Support"),
            ("Puller", "Puller"),
            ("Clapper", "Clapper"),
            ("Stopper", "Stopper"),
            ("Holy", "Holy"),
            ("Nature", "Nature"),
            ("Pierce", "Pierce"),
            ("Agarre", "Agarre"),
            ("Prisma", "Prisma"),
        ]

        for nombre, esperado in roles:
            rol = aventura.agregar_rol(nombre=nombre, categoria=nombre, emoji="❔", cantidad=1)
            self.assertEqual(rol.nombre_mostrado, esperado)

    def test_unknown_roles_keep_their_name_and_get_an_emoji(self):
        aventura = Adventure()
        rol = aventura.agregar_rol(nombre="Flamígero", categoria="Flamígero", emoji="❔", cantidad=1)
        self.assertEqual(rol.nombre_mostrado, "Flamígero")
        self.assertNotEqual(rol.emoji, "❔")

    def test_role_select_options_use_unique_values(self):
        aventura = Adventure()
        aventura.roles = {
            "a": Rol(nombre="Holy", categoria="Holy", emoji="🔮", cantidad=1),
            "b": Rol(nombre="Holy", categoria="Holy", emoji="🔮", cantidad=1),
        }

        selector = RoleSelect(aventura, parent_view=None)
        valores = [opcion.value for opcion in selector.options]

        self.assertEqual(len(valores), len(set(valores)))

    def test_new_adventures_include_globally_registered_roles(self):
        limpiar_roles_conocidos()

        aventura = Adventure()
        aventura.agregar_rol(nombre="Shadow Caller", categoria="Shadow Caller", emoji="🧠", cantidad=1)

        servicio = AdventureService()
        nueva = servicio.crear(
            guild_id=1,
            leader_id=2,
            tipo="PvE",
            contenido="Facciones",
            descripcion="Test",
            plantilla_roles=[]
        )

        self.assertEqual(nueva.roles, {})

    def test_avalon_uses_the_default_6_1_composition(self):
        servicio = AdventureService()
        aventura = servicio.crear(1, 2, "PvE", "Avaloniana 6.1", "AVALONIANA 6.1")

        self.assertEqual(aventura.plazas_totales(), 10)
        self.assertEqual(aventura.roles["DPS"].cantidad, 4)
        self.assertTrue({"Tank", "OFF", "COBRA/GA", "MAIN HEALER", "PARTY HEALER", "SC"}.issubset(aventura.roles))

        embed = EmbedService.crear_aventura(aventura)
        self.assertTrue(any("Horario de Albion" in field.name for field in embed.fields))

    def test_permission_check_does_not_mutate_public_buttons(self):
        aventura = Adventure(leader_id=7)
        view = self.loop.run_until_complete(self._crear_vista(aventura))

        view._aplicar_permisos(99)

        self.assertFalse(view.editar.disabled)
        self.assertFalse(view.economia.disabled)

    def test_editor_role_grants_edit_permission(self):
        aventura = Adventure(leader_id=7)
        self.assertTrue(aventura.agregar_rol_editor(123))
        self.assertTrue(aventura.puede_editar(99, [123]))
        self.assertFalse(aventura.puede_editar(99, [456]))

    def test_edit_buttons_keep_their_labels_for_all_viewers(self):
        aventura = Adventure(leader_id=7)
        view = self.loop.run_until_complete(self._crear_vista(aventura))

        view._aplicar_permisos(99)

        self.assertEqual(view.entrega_loot.label, "📦 Entrega")
        self.assertEqual(view.compartir_permisos.label, "🔗 Compartir permisos")
        self.assertFalse(view.entrega_loot.disabled)
        self.assertFalse(view.compartir_permisos.disabled)

    def test_reping_message_mentions_everyone(self):
        aventura = Adventure(leader_id=7)
        aventura.agregar_rol(nombre="Tank", categoria="Tank", emoji="🛡️", cantidad=1)
        view = self.loop.run_until_complete(self._crear_vista(aventura))

        mensaje = view._crear_mensaje_reping(None)

        self.assertIn("@everyone", mensaje)

    def test_role_select_registers_directly_without_weapon_prompt(self):
        aventura = Adventure(leader_id=7)
        aventura.roles = {
            "DPS": Rol(nombre="DPS", categoria="DPS", emoji="⚔️", cantidad=1)
        }

        class DummyResponse:

            def __init__(self):
                self.kwargs = None

            async def send_message(self, **kwargs):
                self.kwargs = kwargs
                return None

        class DummyInteraction:

            def __init__(self, user_id):
                self.user = SimpleNamespace(id=user_id)
                self.response = DummyResponse()
                self.followup = DummyResponse()

        class DummyParentView:

            def __init__(self):
                self.updated = False

            async def actualizar_embed(self):
                self.updated = True

        parent_view = DummyParentView()
        selector = RoleSelect(aventura, parent_view=parent_view)
        selector._values = ["DPS::0"]
        interaction = DummyInteraction(99)

        self.loop.run_until_complete(selector.callback(interaction))

        self.assertTrue(parent_view.updated)
        self.assertTrue(aventura.jugador_tiene_rol(99))
        self.assertIsNone(interaction.response.kwargs.get("view"))
        self.assertIn("DPS", interaction.response.kwargs.get("content"))

    def test_registered_roles_are_persisted_to_disk(self):
        limpiar_roles_conocidos()

        aventura = Adventure()
        aventura.agregar_rol(nombre="Flamígero", categoria="Custom Role", emoji="🔥", cantidad=1)

        ruta = Path("data/roles_catalog.json")
        self.assertTrue(ruta.exists())

        datos = json.loads(ruta.read_text(encoding="utf-8"))
        self.assertIn("Flamígero", datos)
        self.assertEqual(datos["Flamígero"]["categoria"], "Custom Role")
        self.assertEqual(datos["Flamígero"]["emoji"], "🔥")


if __name__ == "__main__":
    unittest.main()
