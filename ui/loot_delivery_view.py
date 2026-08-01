import discord


class LootToggleButton(discord.ui.Button):
    def __init__(self, view, jugador_id, entregado, nombre):
        super().__init__(
            label=f"{'✅' if entregado else '❌'} {nombre}"[:80],
            style=discord.ButtonStyle.success if entregado else discord.ButtonStyle.secondary,
            custom_id=f"loot_toggle:{jugador_id}",
        )
        self.loot_view = view
        self.jugador_id = jugador_id

    async def callback(self, interaction: discord.Interaction):
        nuevo_estado = not self.loot_view.aventura.loot_entregado.get(self.jugador_id, False)
        self.loot_view.aventura.marcar_entrega(self.jugador_id, nuevo_estado)
        self.loot_view._build_buttons()
        if self.loot_view.parent_view is not None:
            await self.loot_view.parent_view.actualizar_embed()
        await interaction.response.edit_message(view=self.loot_view)


class LootDeliveryView(discord.ui.View):
    def __init__(self, aventura, parent_view=None, guild=None):
        super().__init__(timeout=180)
        self.aventura = aventura
        self.parent_view = parent_view
        self.guild = guild
        self._build_buttons()

    def _nombre_jugador(self, jugador_id):
        miembro = self.guild.get_member(jugador_id) if self.guild else None
        return (miembro.display_name or miembro.name) if miembro else f"Jugador {jugador_id}"

    def _build_buttons(self):
        self.clear_items()
        for rol in self.aventura.roles.values():
            for jugador_id in rol.jugadores:
                entregado = self.aventura.loot_entregado.get(jugador_id, False)
                self.add_item(LootToggleButton(self, jugador_id, entregado, self._nombre_jugador(jugador_id)))
        if not self.children:
            self.add_item(discord.ui.Button(label="No hay jugadores aún", disabled=True))
        self.add_item(LootRefreshButton(self))
        self.add_item(LootCloseButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.aventura.leader_id:
            return True
        await interaction.response.send_message(
            "❌ Solo quien creó la aventura puede marcar entregas.", ephemeral=True
        )
        return False


class LootRefreshButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Actualizar", style=discord.ButtonStyle.primary)
        self.loot_view = view

    async def callback(self, interaction: discord.Interaction):
        self.loot_view._build_buttons()
        await interaction.response.edit_message(view=self.loot_view)


class LootCloseButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Cerrar", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=None)
