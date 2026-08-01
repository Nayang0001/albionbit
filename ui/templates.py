import re
import discord
from services.aventura_service import es_contenido_avalon
from services.plantilla_service import plantillas


class PlantillasButton(discord.ui.Button):

    def __init__(self, tipo):
        self.tipo = tipo
        super().__init__(label="📁 Mis plantillas", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Solo verás las plantillas privadas que guardaste como líder para {self.tipo}.",
            view=PlantillasContentView(self.tipo, interaction.user.id),
            ephemeral=True
        )


class PlantillasContentSelect(discord.ui.Select):

    def __init__(self, tipo):
        self.tipo = tipo

        if tipo == "PvP":
            opciones = [
                discord.SelectOption(label="Gank", emoji="🩸"),
                discord.SelectOption(label="Roaming", emoji="⚔️"),
                discord.SelectOption(label="Small Scale", emoji="🛡️"),
                discord.SelectOption(label="Facciones", emoji="🏳️"),
                discord.SelectOption(label="Roads", emoji="🛣️"),
                discord.SelectOption(label="Cristales", emoji="💎"),
                discord.SelectOption(label="Hellgate", emoji="🔥"),
                discord.SelectOption(label="Castillos", emoji="🏰"),
                discord.SelectOption(label="Outposts", emoji="📍"),
                discord.SelectOption(label="ZvZ", emoji="👑"),
                discord.SelectOption(label="Scrim", emoji="🥊"),
                discord.SelectOption(label="Arena", emoji="⚡"),
                discord.SelectOption(label="Personalizado", emoji="⚙️")
            ]
        else:
            opciones = [
                discord.SelectOption(label="Grupales", emoji="👥"),
                discord.SelectOption(label="Estáticas", emoji="🏛️"),
                discord.SelectOption(label="Avalon", emoji="✨"),
                discord.SelectOption(label="Buffo Avaloniano", emoji="🌟"),
                discord.SelectOption(label="HCE", emoji="💰"),
                discord.SelectOption(label="Roads PvE", emoji="🛣️"),
                discord.SelectOption(label="Dorados", emoji="🪙"),
                discord.SelectOption(label="Personalizado", emoji="⚙️")
            ]

        super().__init__(
            placeholder="Selecciona el contenido...",
            min_values=1,
            max_values=1,
            options=opciones
        )

    async def callback(self, interaction: discord.Interaction):
        contenido = self.values[0]
        await interaction.response.edit_message(
            content=f"Tus plantillas privadas de {self.tipo} > {contenido}",
            view=PlantillasListView(self.tipo, contenido, interaction.user.id),
            ephemeral=True
        )


class PlantillasContentView(discord.ui.View):

    def __init__(self, tipo, user_id):
        super().__init__(timeout=180)
        self.tipo = tipo
        self.user_id = user_id
        self.add_item(PlantillasContentSelect(tipo))


class PlantillasListView(discord.ui.View):

    def __init__(self, tipo, contenido, user_id):
        super().__init__(timeout=180)
        self.tipo = tipo
        self.contenido = contenido
        self.user_id = user_id

        plantillas_usuario = plantillas.obtener_plantillas_usuario(tipo, contenido, user_id)

        if not plantillas_usuario:
            self.add_item(discord.ui.Button(label="No tienes plantillas guardadas para este contenido", style=discord.ButtonStyle.secondary, disabled=True))
            return

        for nombre, roles in plantillas_usuario.items():
            self.add_item(PlantillaSelect(nombre, tipo, contenido, roles))


class PlantillaSelect(discord.ui.Button):

    def __init__(self, nombre, tipo, contenido, roles):
        self.nombre = nombre
        self.tipo = tipo
        self.contenido = contenido
        self.roles = roles
        super().__init__(label=nombre, style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(
            DiscordPlantillaModal(self.tipo, self.contenido, self.roles)
        )


class DiscordPlantillaModal(discord.ui.Modal, title="Usar plantilla privada"):

    descripcion = discord.ui.TextInput(
        label="Descripción de la aventura",
        style=discord.TextStyle.paragraph,
        placeholder="Escribe la descripción de la aventura...",
        required=True,
        max_length=1000
    )

    def __init__(self, tipo, contenido, roles):
        super().__init__()
        self.tipo = tipo
        self.contenido = contenido
        self.roles = roles

    async def on_submit(self, interaction: discord.Interaction):
        from services.aventura_service import aventuras
        from services.embed_service import EmbedService
        from ui.adventure_view import AdventureView

        aventura = aventuras.crear(
            guild_id=interaction.guild.id,
            leader_id=interaction.user.id,
            tipo=self.tipo,
            contenido=self.contenido,
            descripcion=self.descripcion.value,
            plantilla_roles=self.roles
        )

        view = AdventureView(aventura)
        embed = EmbedService.crear_aventura(aventura, guild=interaction.guild)
        mensaje = await interaction.channel.send(
            content="@everyone",
            embed=embed,
            view=view,
            allowed_mentions=discord.AllowedMentions(everyone=True),
        )
        aventura.mensaje_id = mensaje.id
        aventura.canal_id = mensaje.channel.id
        aventura.mensaje = mensaje

        confirmacion = discord.Embed(
            title="✅ Aventura creada con plantilla",
            description=(
                f"**Contenido:** {self.contenido}\n"
                f"**Tipo:** {self.tipo}\n\n"
                "La aventura fue creada usando tu plantilla privada."
            ),
            color=0x2ECC71
        )
        confirmacion.add_field(
            name="💡 Consejo para el líder",
            value=(
                "Puedes borrar los roles por defecto que aparezcan y agregar los que necesites "
                "para esta aventura desde el menú de edición del líder."
            ),
            inline=False,
        )
        confirmacion.set_footer(text="Albion Party Manager")

        await interaction.response.send_message(embed=confirmacion, ephemeral=True)
