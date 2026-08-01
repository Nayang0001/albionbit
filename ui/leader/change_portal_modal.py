import discord


class ChangePortalModal(discord.ui.Modal, title="Cambiar Portal / Zona"):

    nuevo_portal = discord.ui.TextInput(
        label="Nuevo Portal / Zona",
        placeholder="Ej: Martlock, Martlock Portal, Thetford, Lymhurst, Black Zone, Avalon",
        required=True,
        max_length=100
    )

    def __init__(self, aventura, parent_view):
        super().__init__()
        self.aventura = aventura
        self.parent_view = parent_view

        if hasattr(self.aventura, "portal") and self.aventura.portal:
            self.nuevo_portal.default = self.aventura.portal

    async def on_submit(self, interaction: discord.Interaction):
        nuevo_portal = self.nuevo_portal.value.strip()

        self.aventura.portal = nuevo_portal

        await self.parent_view.actualizar_embed()

        await interaction.response.send_message(
            f"✅ Portal / Zona cambiado a **{nuevo_portal}**.",
            ephemeral=True
        )
