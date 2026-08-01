import discord


class ChangeLootModal(discord.ui.Modal, title="Cambiar Tipo de Loot"):

    nuevo_loot = discord.ui.TextInput(
        label="Tipo de Loot",
        placeholder="Ej: Plata, Fame, Equipo T8, Artefactos, Mounts",
        required=True,
        max_length=100
    )

    def __init__(self, aventura, parent_view):
        super().__init__()
        self.aventura = aventura
        self.parent_view = parent_view

        if hasattr(self.aventura, "loot") and self.aventura.loot:
            self.nuevo_loot.default = self.aventura.loot

    async def on_submit(self, interaction: discord.Interaction):
        nuevo_loot = self.nuevo_loot.value.strip()

        self.aventura.loot = nuevo_loot

        await self.parent_view.actualizar_embed()

        await interaction.response.send_message(
            f"✅ Tipo de Loot cambiado a **{nuevo_loot}**.",
            ephemeral=True
        )
