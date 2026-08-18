import asyncio
import logging
import discord
from discord import app_commands
from discord.ext import commands

import aiohttp
from io import BytesIO
from PIL import Image
from urllib.parse import quote

from services.albion_service import AlbionService
from database.database import db

LOGGER = logging.getLogger("killboard")


class Killboard(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.albion = AlbionService()
        self._task = bot.loop.create_task(self._poll_loop())

    async def _poll_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                await self.check_all_tracked()
            except Exception:
                LOGGER.exception("Error en poll killboard")
            await asyncio.sleep(30)

    async def check_all_tracked(self):
        cur = db.cursor
        cur.execute("SELECT guild_id, channel_kills, channel_deaths, albion_guild_id FROM killboard_tracked")
        rows = cur.fetchall()
        if not rows:
            return

        events = await self.albion.fetch_events(limit=50)

        for row in rows:
            guild_id = row[0]
            channel_kills = row[1]
            channel_deaths = row[2]
            albion_guild_id = row[3]

            for ev in events:
                event_id = ev.get("EventId") or ev.get("Id") or ev.get("Id")
                if not event_id:
                    continue

                # skip if already processed
                cur.execute("SELECT 1 FROM killboard_events WHERE event_id=?", (event_id,))
                if cur.fetchone():
                    continue

                killer = ev.get("Killer") or {}
                victim = ev.get("Victim") or {}

                sent = False

                if killer and killer.get("GuildId") == albion_guild_id:
                    await self._send_event(channel_kills, ev, "kill", guild_id)
                    sent = True

                if victim and victim.get("GuildId") == albion_guild_id:
                    await self._send_event(channel_deaths, ev, "death", guild_id)
                    sent = True

                if sent:
                    cur.execute(
                        "INSERT OR IGNORE INTO killboard_events (event_id, guild_id, event_type) VALUES (?,?,?)",
                        (event_id, guild_id, 'kill' if killer.get("GuildId") == albion_guild_id else 'death'),
                    )
                    db.conn.commit()

    async def _send_event(self, channel_id, ev, ev_type: str, guild_id: int):
        if not channel_id:
            return

        channel = self.bot.get_channel(channel_id)
        if channel is None:
            try:
                channel = await self.bot.fetch_channel(channel_id)
            except Exception:
                return

        killer = ev.get("Killer") or {}
        victim = ev.get("Victim") or {}

        title = "Kill" if ev_type == "kill" else "Death"
        color = 0xC0392B if ev_type == "death" else 0x27AE60

        # Render a card image that resembles the sample and send it as a file with a minimal embed
        try:
            from services.killboard_renderer import render_kill_event
        except Exception:
            render_kill_event = None

        # helper to extract item ids from event participant
        def extract_item_ids(part):
            items = []
            for p in (part.get("Items") or part.get("Equipment") or []):
                if isinstance(p, dict):
                    item_id = p.get("Type") or p.get("ItemType") or p.get("TypeId") or p.get("Id")
                    if item_id:
                        items.append(item_id)
                elif isinstance(p, str):
                    items.append(p)
            return items[:9]

        k_item_ids = extract_item_ids(killer)
        v_item_ids = extract_item_ids(victim)
        loot_ids = []
        for l in (ev.get("Loot") or []):
            if isinstance(l, dict):
                lid = l.get("Type") or l.get("ItemType") or l.get("Id")
                if lid:
                    loot_ids.append(lid)
            elif isinstance(l, str):
                loot_ids.append(l)

        async def fetch_icon(session, item_id: str):
            try:
                # Use Albion render CDN
                url = f"https://render.albiononline.com/v1/item/{quote(item_id)}.png"
                async with session.get(url, timeout=15) as resp:
                    if resp.status != 200:
                        return None
                    data = await resp.read()
                    img = Image.open(BytesIO(data)).convert("RGBA")
                    return img
            except Exception:
                return None

        k_icons = []
        v_icons = []
        loot_icons = []

        if render_kill_event is not None:
            async with aiohttp.ClientSession() as session:
                tasks = [fetch_icon(session, iid) for iid in k_item_ids]
                k_icons = await asyncio.gather(*tasks, return_exceptions=True)
                k_icons = [i if isinstance(i, Image.Image) else None for i in k_icons]

                tasks = [fetch_icon(session, iid) for iid in v_item_ids]
                v_icons = await asyncio.gather(*tasks, return_exceptions=True)
                v_icons = [i if isinstance(i, Image.Image) else None for i in v_icons]

                tasks = [fetch_icon(session, iid) for iid in loot_ids[:10]]
                loot_icons = await asyncio.gather(*tasks, return_exceptions=True)
                loot_icons = [i if isinstance(i, Image.Image) else None for i in loot_icons]

            try:
                img_bytes = render_kill_event(ev, ev_type, k_icons=k_icons, v_icons=v_icons, loot_icons=loot_icons)
                file = discord.File(fp=img_bytes, filename="killcard.png")
                embed = discord.Embed(title=title, color=color)
                # Short info fields
                k_name = killer.get("Name") or "Desconocido"
                v_name = victim.get("Name") or "Desconocido"
                embed.add_field(name="Killer", value=k_name, inline=True)
                embed.add_field(name="Victim", value=v_name, inline=True)
                location = ev.get("Location") or ev.get("Zone") or ev.get("ZoneId") or "-"
                embed.set_footer(text=f"Mapa: {location} ? EventId: {ev.get('EventId') or ev.get('Id')}")
                await channel.send(embed=embed, file=file)
                return
            except Exception:
                LOGGER.exception("Error rendering killcard")

        # Fallback if renderer not available or failed
        embed = discord.Embed(title=f"{title}", color=color)
        # Players
        k_name = killer.get("Name") or "Desconocido"
        v_name = victim.get("Name") or "Desconocido"
        embed.add_field(name="Killer", value=k_name, inline=True)
        embed.add_field(name="Victim", value=v_name, inline=True)
        # Fame / silver
        fame = ev.get("KillerFame") or ev.get("VictimFame") or ev.get("Fame") or 0
        silver = ev.get("Silver") or 0
        embed.add_field(name="Fama", value=str(fame), inline=False)
        if silver:
            embed.add_field(name="Silver", value=str(silver), inline=True)
        location = ev.get("Location") or ev.get("Zone") or ev.get("ZoneId") or "-"
        embed.set_footer(text=f"Mapa: {location} ? EventId: {ev.get('EventId') or ev.get('Id')}")
        await channel.send(embed=embed)


class KillboardSetup(commands.GroupCog, group_name="killboard", group_description="Comandos para configurar el killboard"):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="track", description="Trackear kills/deaths de una guild de Albion")
    @app_commands.describe(albion_guild_id="ID de la guild en Albion (GuildId)", channel_kills="Canal para kills", channel_deaths="Canal para deaths (opcional)")
    async def track(self, interaction: discord.Interaction, albion_guild_id: str, channel_kills: discord.TextChannel, channel_deaths: discord.TextChannel | None=None):
        cur = db.cursor
        cur.execute(
            "INSERT OR REPLACE INTO killboard_tracked (guild_id, nombre, channel_kills, channel_deaths, albion_guild_id) VALUES (?,?,?,?,?)",
            (interaction.guild_id, interaction.guild.name, channel_kills.id, channel_deaths.id if channel_deaths else None, albion_guild_id),
        )
        db.conn.commit()
        await interaction.response.send_message("? Killboard configurado para esta guild.", ephemeral=True)

    @app_commands.command(name="untrack", description="Dejar de trackear eventos para esta guild")
    async def untrack(self, interaction: discord.Interaction):
        cur = db.cursor
        cur.execute("DELETE FROM killboard_tracked WHERE guild_id=?", (interaction.guild_id,))
        db.conn.commit()
        await interaction.response.send_message("? Killboard desactivado para esta guild.", ephemeral=True)

    @app_commands.command(name="status", description="Mostrar estado del killboard para este servidor")
    async def status(self, interaction: discord.Interaction):
        cur = db.cursor
        cur.execute("SELECT channel_kills, channel_deaths, albion_guild_id FROM killboard_tracked WHERE guild_id=?", (interaction.guild_id,))
        row = cur.fetchone()
        if not row:
            await interaction.response.send_message("? No hay killboard configurado para este servidor.", ephemeral=True)
            return

        channel_kills, channel_deaths, albion_guild_id = row[0], row[1], row[2]
        text = f"Guild Albion ID: {albion_guild_id}\nCanal kills: {channel_kills}\nCanal deaths: {channel_deaths}"
        await interaction.response.send_message(text, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Killboard(bot))
    await bot.add_cog(KillboardSetup(bot))
