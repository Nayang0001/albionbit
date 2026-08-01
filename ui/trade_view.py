import discord


class TradeContactView(discord.ui.View):
    def __init__(self, vendedor_id: int):
        super().__init__(timeout=None)
        self.vendedor_id = vendedor_id

    @discord.ui.button(label="Contactar vendedor", emoji="💬", style=discord.ButtonStyle.primary)
    async def contactar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"Contacta a <@{self.vendedor_id}> para acordar el intercambio dentro de Albion.",
            ephemeral=True,
        )
