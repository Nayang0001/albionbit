import random

import discord


class RouletteModal(discord.ui.Modal, title="Ruleta de reparto"):
    premio = discord.ui.TextInput(
        label="¿Qué se repartirá?",
        placeholder="Ej.: 1 set 8.3 o 500,000 de silver",
        required=True,
        max_length=150,
    )

    def __init__(self, aventura):
        super().__init__()
        self.aventura = aventura

    async def on_submit(self, interaction: discord.Interaction):
        participantes = [
            jugador_id
            for rol in self.aventura.roles.values()
            for jugador_id in rol.jugadores
        ]
        if not participantes:
            await interaction.response.send_message("❌ No hay participantes para la ruleta.", ephemeral=True)
            return

        ganador_id = random.SystemRandom().choice(participantes)
        ganador = interaction.guild.get_member(ganador_id) if interaction.guild else None
        nombre_ganador = ganador.mention if ganador else f"<@{ganador_id}>"
        embed = discord.Embed(
            title="🎰 Ruleta de reparto",
            description=(
                f"**Premio:** {self.premio.value.strip()}\n"
                f"**Participantes:** {len(participantes)}\n\n"
                f"🏆 Ganador: {nombre_ganador}"
            ),
            color=0xF1C40F,
        )
        await interaction.response.send_message(embed=embed, ephemeral=False)
