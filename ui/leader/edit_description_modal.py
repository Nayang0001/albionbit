import discord

from services.embed_service import EmbedService


class EditDescriptionModal(discord.ui.Modal):

    descripcion = discord.ui.TextInput(
        label="Nueva descripción",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    def __init__(self, aventura, parent_view):

        super().__init__(title="Editar descripción")

        self.aventura = aventura
        self.parent_view = parent_view

        self.descripcion.default = aventura.descripcion

    async def on_submit(self, interaction: discord.Interaction):

        self.aventura.descripcion = self.descripcion.value

        embed = EmbedService.crear_aventura(
            self.aventura
        )

        await self.aventura.mensaje.edit(
            embed=embed,
            view=self.parent_view
        )

        await interaction.response.send_message(
            "✅ Descripción actualizada.",
            ephemeral=True
        )
