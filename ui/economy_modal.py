import discord

from services.leaderboard_service import LeaderboardService


class EconomyModal(discord.ui.Modal, title="Economía de la aventura"):

    total_loot = discord.ui.TextInput(
        label="Total de loot a dividir",
        placeholder="Ej: 100000",
        required=True,
        max_length=20
    )

    total_silver = discord.ui.TextInput(
        label="Total de silver a dividir",
        placeholder="Ej: 500000",
        required=True,
        max_length=20
    )

    def __init__(self, aventura):
        super().__init__()
        self.aventura = aventura

    async def on_submit(self, interaction: discord.Interaction):
        try:
            total_loot = float(self.total_loot.value.replace(',', '.'))
            total_silver = float(self.total_silver.value.replace(',', '.'))
        except ValueError:
            await interaction.response.send_message(
                "❌ Debes ingresar números válidos para el loot y el silver.",
                ephemeral=True
            )
            return

        participantes = self.aventura.total_jugadores()
        if participantes == 0:
            await interaction.response.send_message(
                "❌ No hay participantes registrados.",
                ephemeral=True
            )
            return

        loot_por_jugador = total_loot / participantes
        silver_por_jugador = total_silver / participantes

        self.aventura.loot_total = total_loot
        self.aventura.silver_total = total_silver

        LeaderboardService().registrar_resultado(
            self.aventura,
            total_loot,
            total_silver,
        )

        def _formatear_numero(valor):
            valor_float = float(valor)
            return f"{valor_float:,.0f}" if valor_float.is_integer() else f"{valor_float:,.2f}"

        reparto_individual = []
        for rol in self.aventura.roles.values():
            for jugador_id in rol.jugadores:
                miembro = interaction.guild.get_member(jugador_id) if interaction.guild else None
                nombre = miembro.mention if miembro else f"<@{jugador_id}>"
                reparto_individual.append(
                    f"• {nombre} — 💰 {_formatear_numero(loot_por_jugador)} | "
                    f"🪙 {_formatear_numero(silver_por_jugador)}"
                )

        mensaje = (
            "📊 Reparto de economía\n"
            f"👥 Participantes: {participantes}\n\n"
            "💰 Loot\n"
            f"• Total: {_formatear_numero(total_loot)}\n"
            f"• Por jugador: {_formatear_numero(loot_por_jugador)}\n\n"
            "🪙 Silver\n"
            f"• Total: {_formatear_numero(total_silver)}\n"
            f"• Por jugador: {_formatear_numero(silver_por_jugador)}\n\n"
            "👤 Reparto por participante\n"
            + "\n".join(reparto_individual)
        )

        await interaction.response.send_message(mensaje, ephemeral=False)
