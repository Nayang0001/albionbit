import discord


class ChangeTierModal(discord.ui.Modal, title="Cambiar Tier de la Aventura"):

    nuevo_tier = discord.ui.TextInput(
        label="Nuevo Tier",
        placeholder="Ej: 8, 7.1, 6.2",
        required=True,
        max_length=10
    )

    def __init__(self, aventura, parent_view):
        super().__init__()
        self.aventura = aventura
        self.parent_view = parent_view

        # Si ya tiene tier, lo mostramos como valor por defecto
        if hasattr(self.aventura, "tier") and self.aventura.tier:
            self.nuevo_tier.default = str(self.aventura.tier)

    async def on_submit(self, interaction: discord.Interaction):
        nuevo_tier = self.nuevo_tier.value.strip()

        # Guardar el tier en la aventura
        self.aventura.tier = nuevo_tier

        # Actualizar embed
        await self.parent_view.actualizar_embed()

        await interaction.response.send_message(
            f"✅ Tier cambiado a **{nuevo_tier}** correctamente.",
            ephemeral=True
        )
