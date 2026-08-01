import discord

from ui.selects.role_view import RoleView
from services.embed_service import EmbedService
from ui.leader.leader_view import LeaderView
from ui.economy_modal import EconomyModal
from services.leaderboard_service import LeaderboardService
from ui.share_permissions_view import SharePermissionsView
from ui.loot_delivery_view import LootDeliveryView
from ui.roulette_modal import RouletteModal


class AdventureView(discord.ui.View):

    def __init__(self, aventura):
        super().__init__(timeout=None)
        self.aventura = aventura

    def _es_lider(self, user_id: int) -> bool:
        return user_id == self.aventura.leader_id

    def _puede_editar(self, user) -> bool:
        user_id = getattr(user, "id", user)
        role_ids = [role.id for role in getattr(user, "roles", ())]
        return self.aventura.puede_editar(user_id, role_ids)

    def _aplicar_estado_panel(self) -> None:
        if hasattr(self, "unirme"):
            self.unirme.disabled = not self.aventura.abierta or self.aventura.finalizada
        if hasattr(self, "salir"):
            self.salir.disabled = not self.aventura.abierta or self.aventura.finalizada

    def _aplicar_permisos(self, user_id: int) -> None:
        # La vista es pública y compartida: no se deben mutar sus botones según
        # el último usuario que interactuó. Cada callback valida su permiso.
        return self._puede_editar(user_id)

    def _crear_mensaje_reping(self, guild) -> str:
        faltantes = [f"{rol.emoji} **{rol.nombre_mostrado}** ({rol.libres})"
                    for rol in self.aventura.roles.values() if rol.libres > 0]

        inscritos = []
        for rol in self.aventura.roles.values():
            for jugador_id in rol.jugadores:
                nombre = EmbedService._formatear_usuario(jugador_id, guild, mention=True)
                inscritos.append(f"• {nombre} → {rol.nombre_mostrado}")

        lider = EmbedService._formatear_usuario(self.aventura.leader_id, guild, mention=True)

        partes = [f"@everyone\n📢 Reping de {lider}"]

        if inscritos:
            partes.append("\n**Inscritos:**")
            partes.extend(inscritos)

        if not faltantes:
            partes.append("\n✅ La composición ya está completa.")
        else:
            partes.append("\n**Faltan los siguientes roles:**")
            partes.extend(faltantes)

        return "\n".join(partes)

    # =====================================
    # ACTUALIZAR EMBED
    # =====================================
    async def actualizar_embed(self):
        guild = None
        if hasattr(self.aventura, "mensaje") and self.aventura.mensaje:
            guild = getattr(self.aventura.mensaje, "guild", None)

        embed = EmbedService.crear_aventura(self.aventura, guild=guild)

        if hasattr(self.aventura, "mensaje") and self.aventura.mensaje:
            try:
                await self.aventura.mensaje.edit(embed=embed, view=self)
            except Exception:
                pass

    # =====================================
    # UNIRSE
    # =====================================
    @discord.ui.button(label="➕ Unirme", emoji="⚔️", style=discord.ButtonStyle.success, row=0)
    async def unirme(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._aplicar_permisos(interaction.user.id)

        if not self.aventura.abierta and interaction.user.id != self.aventura.leader_id:
            await interaction.response.send_message("🔒 La aventura está cerrada.", ephemeral=True)
            return

        if self.aventura.jugador_tiene_rol(interaction.user.id):
            await interaction.response.send_message("❌ Ya perteneces a esta aventura.", ephemeral=True)
            return

        await interaction.response.send_message(
            "Selecciona el rol que ocuparás.",
            view=RoleView(self.aventura, self),
            ephemeral=True
        )

    # =====================================
    # SALIR
    # =====================================
    @discord.ui.button(label="🚪 Salir", style=discord.ButtonStyle.danger, row=0)
    async def salir(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._aplicar_permisos(interaction.user.id)

        if not self.aventura.quitar_jugador(interaction.user.id):
            await interaction.response.send_message("❌ No perteneces a esta aventura.", ephemeral=True)
            return

        await self.actualizar_embed()
        await interaction.response.send_message("✅ Has salido de la aventura.", ephemeral=True)

    # =====================================
    # JUGADORES
    # =====================================
    @discord.ui.button(label="👥 Jugadores", style=discord.ButtonStyle.secondary, row=0)
    async def jugadores(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._aplicar_permisos(interaction.user.id)

        texto = ""
        guild = interaction.guild

        for rol in self.aventura.roles.values():
            texto += f"## {rol.emoji} {rol.nombre_mostrado}\n"
            if rol.jugadores:
                for jugador_id in rol.jugadores:
                    nombre = EmbedService._formatear_usuario(jugador_id, guild, mention=True)
                    texto += f"• {nombre}\n"
            else:
                texto += "❌ Libre\n"
            texto += "\n"

        embed = discord.Embed(title="👥 Jugadores inscritos", description=texto, color=0x3498DB)
        embed.set_footer(text=f"{self.aventura.total_jugadores()} / {self.aventura.plazas_totales()} jugadores")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =====================================
    # REPING
    # =====================================
    @discord.ui.button(label="📢 Reping", style=discord.ButtonStyle.primary, row=1)
    async def reping(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._aplicar_permisos(interaction.user.id)

        if interaction.user.id != self.aventura.leader_id:
            await interaction.response.send_message("❌ Solo el líder puede usar este botón.", ephemeral=True)
            return

        mensaje = self._crear_mensaje_reping(interaction.guild)

        await interaction.channel.send(
            mensaje,
            allowed_mentions=discord.AllowedMentions(users=True, everyone=True, roles=False)
        )
        await interaction.response.send_message("✅ Reping enviado.", ephemeral=True)

    # =====================================
    # CERRAR
    # =====================================
    @discord.ui.button(label="🔒 Cerrar", style=discord.ButtonStyle.secondary, row=1)
    async def cerrar(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._aplicar_permisos(interaction.user.id)

        if interaction.user.id != self.aventura.leader_id:
            await interaction.response.send_message("❌ Solo el líder puede cerrar la aventura.", ephemeral=True)
            return

        self.aventura.abierta = False
        self._aplicar_estado_panel()

        await self.actualizar_embed()
        await interaction.response.send_message("🔒 Inscripciones cerradas.", ephemeral=True)

    @discord.ui.button(label="🔓 Abrir", style=discord.ButtonStyle.success, row=1)
    async def abrir(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._aplicar_permisos(interaction.user.id)

        if interaction.user.id != self.aventura.leader_id:
            await interaction.response.send_message("❌ Solo el líder puede abrir la aventura.", ephemeral=True)
            return

        self.aventura.abierta = True
        self._aplicar_estado_panel()

        await self.actualizar_embed()
        await interaction.response.send_message("🔓 Inscripciones abiertas nuevamente.", ephemeral=True)

    # =====================================
    # FINALIZAR
    # =====================================
    @discord.ui.button(label="🏁 Finalizar", style=discord.ButtonStyle.danger, row=1)
    async def finalizar(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._aplicar_permisos(interaction.user.id)

        if interaction.user.id != self.aventura.leader_id:
            await interaction.response.send_message("❌ Solo el líder puede finalizar la aventura.", ephemeral=True)
            return

        self.aventura.abierta = False
        self.aventura.finalizada = True

        for item in self.children:
            if not isinstance(item, discord.ui.Button):
                continue

            if item is self.economia:
                item.disabled = True
                item.label = "🔒 Economía"
            elif item is self.reping:
                item.disabled = False
                item.label = "📢 Reping"
            elif item is self.unirme or item is self.salir:
                item.disabled = True
            elif item is self.jugadores:
                item.disabled = True
                item.label = "🔒 Jugadores"
            elif item is self.cerrar:
                item.disabled = True
                item.label = "🔒 Cerrar"
            elif item is self.abrir:
                item.disabled = True
                item.label = "🔒 Abrir"
            elif item is self.finalizar:
                item.disabled = True
                item.label = "🏁 Finalizada"
            elif item is self.editar:
                item.disabled = True
                item.label = "🔒 Editar"
            elif item is self.entrega_loot:
                item.disabled = True
                item.label = "🔒 Entrega"
            elif item is self.compartir_permisos:
                item.disabled = True
                item.label = "🔒 Compartir permisos"

        self._aplicar_estado_panel()

        embed = EmbedService.crear_aventura(self.aventura)
        embed.color = 0x808080

        if hasattr(self.aventura, "mensaje") and self.aventura.mensaje:
            await self.aventura.mensaje.edit(embed=embed, view=self)

        LeaderboardService().registrar_resultado(
            self.aventura,
            getattr(self.aventura, "loot_total", 0.0),
            getattr(self.aventura, "silver_total", 0.0),
        )

        await interaction.response.send_message("🏁 Aventura finalizada correctamente.", ephemeral=True)

    # =====================================
    # EDITAR (Panel del Líder)
    # =====================================
    @discord.ui.button(label="💰 Economía", style=discord.ButtonStyle.secondary, row=2)
    async def economia(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._aplicar_permisos(interaction.user.id)

        if not self._puede_editar(interaction.user):
            await interaction.response.send_message("❌ Solo el líder o un sub-admin puede usar la economía de la aventura.", ephemeral=True)
            return

        if self.aventura.total_jugadores() == 0:
            await interaction.response.send_message(
                "❌ No hay participantes anotados para dividir el loot.",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            EconomyModal(self.aventura)
        )

    @discord.ui.button(label="📦 Entrega", style=discord.ButtonStyle.secondary, row=2)
    async def entrega_loot(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._aplicar_permisos(interaction.user.id)

        if not self._puede_editar(interaction.user):
            await interaction.response.send_message("❌ Solo el líder o un sub-admin puede marcar entregas.", ephemeral=True)
            return

        await interaction.response.send_message(
            "Marca quién ya recibió el loot o sigue pendiente.",
            view=LootDeliveryView(self.aventura, self, interaction.guild),
            ephemeral=True,
        )

    @discord.ui.button(label="🔗 Compartir permisos", style=discord.ButtonStyle.primary, row=2)
    async def compartir_permisos(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._aplicar_permisos(interaction.user.id)

        if not self._es_lider(interaction.user.id):
            await interaction.response.send_message("❌ Solo quien creó la aventura puede compartir permisos.", ephemeral=True)
            return

        await interaction.response.send_message(
            "Selecciona a las personas que podrán editar esta aventura.",
            view=SharePermissionsView(self.aventura, self),
            ephemeral=True,
        )

    @discord.ui.button(label="⚙️ Editar", style=discord.ButtonStyle.primary, row=2)
    async def editar(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._aplicar_permisos(interaction.user.id)

        if not self._puede_editar(interaction.user):
            await interaction.response.send_message("❌ Solo el líder o un sub-admin pueden editar la aventura.", ephemeral=True)
            return

        embed = discord.Embed(
            title="⚙️ Panel del Líder",
            description="Selecciona una acción.",
            color=0xF39C12
        )

        await interaction.response.send_message(
            embed=embed,
            view=LeaderView(self.aventura, self),
            ephemeral=True
        )

    @discord.ui.button(label="🎲 Ruleta", style=discord.ButtonStyle.secondary, row=3)
    async def ruleta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self._es_lider(interaction.user.id):
            await interaction.response.send_message("❌ Solo quien creó la aventura puede iniciar la ruleta.", ephemeral=True)
            return
        await interaction.response.send_modal(RouletteModal(self.aventura))
