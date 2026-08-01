import discord
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from discord.ext import commands, tasks
from discord import app_commands

from ui.buttons import TipoContenidoView
from ui.adventure_view import AdventureView
from services.embed_service import EmbedService
from services.aventura_service import aventuras
from services.leaderboard_service import LeaderboardService
from services.albion_items import obtener_url_sprite
from ui.trade_view import TradeContactView

PANELES_HORARIO_PATH = Path(__file__).resolve().parent.parent / "data" / "paneles_horario.json"


class Aventura(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._paneles_horario = self._cargar_paneles_horario()
        self.actualizar_horarios.start()

    def cog_unload(self):
        self.actualizar_horarios.cancel()

    @staticmethod
    def _cargar_paneles_horario() -> dict[int, int]:
        try:
            datos = json.loads(PANELES_HORARIO_PATH.read_text(encoding="utf-8"))
            return {int(mensaje_id): int(canal_id) for mensaje_id, canal_id in datos.items()}
        except (FileNotFoundError, json.JSONDecodeError, ValueError, TypeError):
            return {}

    def _guardar_paneles_horario(self) -> None:
        PANELES_HORARIO_PATH.parent.mkdir(parents=True, exist_ok=True)
        PANELES_HORARIO_PATH.write_text(
            json.dumps(self._paneles_horario, indent=2), encoding="utf-8"
        )

    @staticmethod
    def _crear_embed_horario() -> discord.Embed:
        """Crea el panel horario en formato de 12 horas con segundos y actualización continua."""
        ahora_utc = datetime.now(timezone.utc)
        zonas = (
            ("Albion Online / UTC", 0),
            ("Belice (UTC-6)", -6),
            ("Guatemala (UTC-6)", -6),
            ("El Salvador (UTC-6)", -6),
            ("Honduras (UTC-6)", -6),
            ("Nicaragua (UTC-6)", -6),
            ("Costa Rica (UTC-6)", -6),
            ("Panamá (UTC-5)", -5),
            ("México (UTC-6)", -6),
            ("República Dominicana (UTC-4)", -4),
        )
        lineas = [
            f"**{nombre}:** {ahora_utc.astimezone(timezone(timedelta(hours=desfase))):%I:%M:%S %p}"
            for nombre, desfase in zonas
        ]
        timestamp = int(ahora_utc.timestamp())
        embed = discord.Embed(
            title="🕒 Horario de Albion y Centroamérica",
            description="\n".join(lineas) + f"\n\nActualizado: <t:{timestamp}:R>",
            color=0x3498DB,
        )
        embed.set_footer(text="Actualización automática cada 5 segundos")
        return embed

    @tasks.loop(seconds=5)
    async def actualizar_horarios(self):
        """Mantiene actualizados los paneles creados con /horario."""
        se_elimino_panel = False
        for mensaje_id, canal_id in list(self._paneles_horario.items()):
            try:
                canal = self.bot.get_channel(canal_id) or await self.bot.fetch_channel(canal_id)
                mensaje = await canal.fetch_message(mensaje_id)
                await mensaje.edit(embed=self._crear_embed_horario())
            except (discord.NotFound, discord.Forbidden):
                self._paneles_horario.pop(mensaje_id, None)
                se_elimino_panel = True
            except discord.HTTPException:
                continue
        if se_elimino_panel:
            self._guardar_paneles_horario()

    @actualizar_horarios.before_loop
    async def antes_de_actualizar_horarios(self):
        await self.bot.wait_until_ready()

    @app_commands.command(
        name="horario",
        description="Publicar el horario de Albion, América y Centroamérica."
    )
    async def horario(self, interaction: discord.Interaction):
        """Publica un horario visible para todo el servidor."""
        await self._publicar_horario(interaction)

    async def _publicar_horario(self, interaction: discord.Interaction) -> None:
        """Publica un solo panel y lo registra para sus actualizaciones."""
        await interaction.response.send_message(embed=self._crear_embed_horario())
        mensaje = await interaction.original_response()
        self._paneles_horario[mensaje.id] = mensaje.channel.id
        self._guardar_paneles_horario()

    @app_commands.command(
        name="hora-albion",
        description="Ver la hora actual de Albion (UTC) y tu hora local."
    )
    async def hora_albion(self, interaction: discord.Interaction):
        # Compatibilidad con el comando anterior: ahora también crea el panel
        # persistente que actualiza sus segundos sin volver a ejecutarlo.
        await self._publicar_horario(interaction)

    @app_commands.command(
        name="aventura",
        description="Crear una aventura."
    )
    async def aventura(
        self,
        interaction: discord.Interaction
    ):

        embed = discord.Embed(

            title="⚔️ Albion Party Manager",

            description=(
                "Bienvenido al creador de aventuras.\n\n"
                "Selecciona primero el tipo de contenido que quieres crear."
            ),

            color=0xF1C40F

        )

        embed.add_field(

            name="🟢 PvE",

            value=(
                "• Grupales\n"
                "• Estáticas\n"
                "• Avalon\n"
                "• Buffo Avaloniano\n"
                "• HCE\n"
                "• Caminos PvE\n"
                "• Dorados\n"
                "• Personalizado"
            ),

            inline=False

        )

        embed.add_field(

            name="🔴 PvP",

            value=(
                "• Gank\n"
                "• Roaming\n"
                "• Pequeña Escala\n"
                "• Facciones\n"
                "• Caminos\n"
                "• Cristales de arena\n"
                "• Competitivo (Crystal)\n"
                "• Hellgate\n"
                "• Castillos\n"
                "• Puestos avanzados\n"
                "• ZvZ\n"
                "• Personalizado"
            ),

            inline=False

        )

        embed.set_footer(
            text="Albion Party Manager"
        )

        await interaction.response.send_message(

            embed=embed,

            view=TipoContenidoView(interaction.channel_id),

            ephemeral=True

        )

    @app_commands.command(name="comercio", description="Publicar una oferta de comercio de Albion.")
    @app_commands.describe(
        objeto="Nombre del objeto que ofreces o buscas",
        tipo="Ofrezco o busco",
        cantidad="Cantidad de objetos",
        precio="Precio o lo que pides a cambio",
        item_id="ID de Albion para mostrar su sprite; ej.: T6_BAG@2",
    )
    async def comercio(
        self,
        interaction: discord.Interaction,
        objeto: str,
        tipo: str,
        cantidad: int,
        precio: str,
        item_id: str | None=None,
    ):
        if cantidad < 1:
            await interaction.response.send_message("❌ La cantidad debe ser mayor que cero.", ephemeral=True)
            return
        tipo_normalizado = tipo.strip().lower()
        if tipo_normalizado not in {"ofrezco", "busco"}:
            await interaction.response.send_message("❌ En tipo escribe `ofrezco` o `busco`.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"🤝 Comercio: {tipo_normalizado.title()}",
            description=f"**{objeto.strip()}** × {cantidad}",
            color=0x3498DB,
        )
        embed.add_field(name="💰 Precio / intercambio", value=precio.strip(), inline=False)
        embed.set_footer(text=f"Publicado por {interaction.user.display_name}")
        # Si no se proporcionó item_id, intentar resolverlo desde el nombre (si se dispone de cache)
        if not item_id:
            try:
                from services.albion_items import buscar_item_por_nombre

                resolved = buscar_item_por_nombre(objeto)
                if resolved:
                    item_id = resolved
            except Exception:
                item_id = None

        sprite = obtener_url_sprite(item_id)
        if sprite:
            embed.set_thumbnail(url=sprite)
        await interaction.response.send_message(
            content=interaction.user.mention,
            embed=embed,
            view=TradeContactView(interaction.user.id),
            ephemeral=False,
        )

    @app_commands.command(
        name="leaderboard",
        description="Ver el ranking de líderes por aventuras, loot y silver"
    )
    async def leaderboard(self, interaction: discord.Interaction, tipo: str="Todos"):
        tipo_filtrado = None if str(tipo).strip().lower() in {"todos", "", "all"} else str(tipo).strip().upper()

        ranking = LeaderboardService().obtener_ranking(
            guild_id=interaction.guild.id,
            tipo=tipo_filtrado,
            limit=10,
        )

        if not ranking:
            await interaction.response.send_message("📊 Todavía no hay resultados registrados.", ephemeral=True)
            return

        def _formatear_numero(valor):
            valor_float = float(valor or 0)
            return f"{valor_float:,.0f}" if valor_float.is_integer() else f"{valor_float:,.2f}"

        lines = []
        for index, item in enumerate(ranking, start=1):
            user = interaction.guild.get_member(item["leader_id"])
            nombre = user.mention if user else f"<@{item['leader_id']}>"
            lines.append(
                f"{index}. {nombre} — Aventuras: {item['aventuras']:,} | Loot: {_formatear_numero(item['loot_total'])} | Silver: {_formatear_numero(item['silver_total'])}"
            )

        embed = discord.Embed(
            title="🏆 Leaderboard de líderes",
            description="\n".join(lines),
            color=0x2ECC71,
        )
        embed.set_footer(text=f"Tipo: {tipo if tipo else 'Todos'}")

        await interaction.response.send_message(embed=embed, ephemeral=False)

    async def publicar_aventura(

        self,

        interaction: discord.Interaction,

        tipo: str,

        contenido: str,

        descripcion: str

    ):

        aventura = aventuras.crear(

            guild_id=interaction.guild.id,

            leader_id=interaction.user.id,

            tipo=tipo,

            contenido=contenido,

            descripcion=descripcion

        )

        embed = EmbedService.crear_aventura(aventura, guild=interaction.guild)

        view = AdventureView(aventura)

        mensaje = await interaction.channel.send(

            content="@everyone",

            embed=embed,

            view=view,

            allowed_mentions=discord.AllowedMentions(everyone=True)

        )

        aventura.mensaje_id = mensaje.id
        aventura.canal_id = mensaje.channel.id
        aventura.mensaje = mensaje

        return aventura


async def setup(bot):

    await bot.add_cog(Aventura(bot))
