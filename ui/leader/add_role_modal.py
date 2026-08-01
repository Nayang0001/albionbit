import discord


class EmojiSelectionView(discord.ui.View):

    def __init__(self, aventura, parent_view):
        super().__init__(timeout=300)
        self.aventura = aventura
        self.parent_view = parent_view

    @discord.ui.button(label="⚔️", style=discord.ButtonStyle.secondary)
    async def espada(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddRoleModal(self.aventura, self.parent_view, "⚔️"))

    @discord.ui.button(label="❤️", style=discord.ButtonStyle.secondary)
    async def corazon(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddRoleModal(self.aventura, self.parent_view, "❤️"))

    @discord.ui.button(label="🛡️", style=discord.ButtonStyle.secondary)
    async def escudo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddRoleModal(self.aventura, self.parent_view, "🛡️"))

    @discord.ui.button(label="🎵", style=discord.ButtonStyle.secondary)
    async def musica(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddRoleModal(self.aventura, self.parent_view, "🎵"))

    @discord.ui.button(label="🔥", style=discord.ButtonStyle.secondary)
    async def fuego(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddRoleModal(self.aventura, self.parent_view, "🔥"))

    @discord.ui.button(label="⭐", style=discord.ButtonStyle.secondary)
    async def estrella(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddRoleModal(self.aventura, self.parent_view, "⭐"))


class AddRoleModal(discord.ui.Modal, title="Agregar Nuevo Rol"):

    nombre = discord.ui.TextInput(
        label="Nombre del Rol",
        placeholder="Ej: DPS Melee, Holy, Tank",
        required=True,
        max_length=50
    )

    categoria = discord.ui.TextInput(
        label="Categoría",
        placeholder="Ej: DPS, Tank, Healer, Support",
        required=True,
        max_length=30
    )

    cantidad = discord.ui.TextInput(
        label="Cantidad de plazas",
        placeholder="Ej: 4",
        required=True
    )

    def __init__(self, aventura, parent_view, emoji=""):
        super().__init__()
        self.aventura = aventura
        self.parent_view = parent_view
        self.emoji_seleccionado = emoji

    async def on_submit(self, interaction: discord.Interaction):
        try:
            cantidad = int(self.cantidad.value)
            if cantidad < 1:
                raise ValueError
        except ValueError:
            await interaction.response.send_message("❌ La cantidad debe ser un número mayor a 0.", ephemeral=True)
            return

        if not self.emoji_seleccionado:
            await interaction.response.send_message("❌ Debes seleccionar un emoji antes de continuar.", ephemeral=True)
            return

        self.aventura.agregar_rol(
            nombre=self.nombre.value.strip(),
            categoria=self.categoria.value.strip(),
            emoji=self.emoji_seleccionado,
            cantidad=cantidad
        )

        try:
            await self.parent_view.actualizar_embed()
        except Exception:
            pass

        await interaction.response.send_message(
            f"✅ Rol **{self.emoji_seleccionado} {self.nombre.value}** añadido correctamente.",
            ephemeral=True
        )
