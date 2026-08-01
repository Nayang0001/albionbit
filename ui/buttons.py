import discord

from ui.selects import ContenidoSelect
from ui.templates import PlantillasButton

PVE_CHANNEL_ID = 1526061241783554180
PVP_CHANNEL_ID = 1527460174044860547


class TipoContenidoView(discord.ui.View):

    def __init__(self, channel_id=None):
        super().__init__(timeout=300)

        if channel_id == PVE_CHANNEL_ID:
            self.add_item(self._crear_boton_pve())
        elif channel_id == PVP_CHANNEL_ID:
            self.add_item(self._crear_boton_pvp())
        else:
            self.add_item(self._crear_boton_pve())
            self.add_item(self._crear_boton_pvp())

    def _crear_boton_pve(self):
        return discord.ui.Button(
            label="🟢 PvE",
            style=discord.ButtonStyle.success,
            custom_id="tipo_pve"
        )

    def _crear_boton_pvp(self):
        return discord.ui.Button(
            label="🔴 PvP",
            style=discord.ButtonStyle.danger,
            custom_id="tipo_pvp"
        )

    async def _handle_pve(self, interaction: discord.Interaction):
        view = discord.ui.View()
        view.add_item(ContenidoSelect("PvE"))
        view.add_item(PlantillasButton("PvE"))

        await interaction.response.edit_message(
            content=None,
            embed=discord.Embed(
                title="🟢 Contenido PvE",
                description="Selecciona el contenido o revisa tus plantillas privadas como líder.",
                color=0x2ECC71
            ),
            view=view
        )

    async def _handle_pvp(self, interaction: discord.Interaction):
        view = discord.ui.View()
        view.add_item(ContenidoSelect("PvP"))
        view.add_item(PlantillasButton("PvP"))

        await interaction.response.edit_message(
            content=None,
            embed=discord.Embed(
                title="🔴 Contenido PvP",
                description="Selecciona el contenido o revisa tus plantillas privadas como líder.",
                color=0xE74C3C
            ),
            view=view
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.data and interaction.data.get("custom_id") == "tipo_pve":
            await self._handle_pve(interaction)
            return False
        if interaction.data and interaction.data.get("custom_id") == "tipo_pvp":
            await self._handle_pvp(interaction)
            return False
        return True
