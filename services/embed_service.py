import discord
from datetime import datetime, timezone


class EmbedService:

    @staticmethod
    def _formatear_usuario(user_id, guild=None, mention=False):
        if guild is not None:
            member = guild.get_member(user_id)
            if member is not None:
                if mention:
                    return member.mention
                return member.display_name or member.name
        if mention:
            return f"<@{user_id}>"
        return f"Usuario {user_id}"

    @staticmethod
    def crear_aventura(aventura, guild=None):

        color = 0xF1C40F
        title = f"⚔️ {aventura.contenido.upper()}"
        description = aventura.descripcion

        if not aventura.abierta:
            color = 0x808080
            title = f"⚔️ {aventura.contenido.upper()} (FINALIZADA)"
            description = f"{aventura.descripcion}\n\n🔒 Esta aventura ya fue finalizada."

        embed = discord.Embed(

            title=title,

            description=description,

            color=color

        )

        embed.add_field(

            name="👑 Líder",

            value=EmbedService._formatear_usuario(aventura.leader_id, guild, mention=True),

            inline=False

        )

        now_utc = datetime.now(timezone.utc)
        timestamp = int(now_utc.timestamp())
        embed.add_field(
            name="🕒 Horario de Albion Online",
            value=(
                f"**UTC:** {now_utc:%H:%M} UTC\n"
                f"**Tu hora local:** <t:{timestamp}:t>\n"
                f"Actualizado: <t:{timestamp}:R>"
            ),
            inline=False,
        )

        # ==========================
        # ROLES
        # ==========================

        for rol in aventura.roles.values():

            texto = ""

            if rol.jugadores:

                for jugador_id in rol.jugadores:
                    texto += (
                        # El estado del panel representa la plaza ocupada, no
                        # la entrega de loot (que se gestiona en su propio panel).
                        f"✅ {EmbedService._formatear_usuario(jugador_id, guild, mention=True)}\n"
                    )

            libres = rol.libres

            for _ in range(libres):

                texto += "❌ Libre\n\n"

            embed.add_field(

                name=f"{rol.emoji} {rol.nombre_mostrado} ({len(rol.jugadores)}/{rol.cantidad})",

                value=texto,

                inline=False

            )

        # ==========================
        # PIE
        # ==========================

        embed.set_footer(

            text=(
                f"{aventura.total_jugadores()} / "
                f"{aventura.plazas_totales()} jugadores"
            )

        )

        return embed
