import discord

from services.aventura_service import aventuras, es_contenido_avalon
from services.embed_service import EmbedService
from ui.adventure_view import AdventureView


class DescriptionModal(discord.ui.Modal, title="Descripción de la aventura"):

    descripcion = discord.ui.TextInput(

        label="Descripción",

        style=discord.TextStyle.paragraph,

        placeholder=(
            "Ejemplo:\n"
            "ROAMING ZONA NEGRA\n"
            "Portal Martlock\n"
            "T7 Equivalente\n"
            "Comida .1\n"
            "Split Loot"
        ),

        required=True,

        max_length=1000

    )

    def __init__(self, tipo: str, contenido: str):

        super().__init__()

        self.tipo = tipo
        self.contenido = contenido

    async def on_submit(self, interaction: discord.Interaction):

        # Crear la aventura

        aventura = aventuras.crear(

            guild_id=interaction.guild.id,

            leader_id=interaction.user.id,

            tipo=self.tipo,

            contenido=self.contenido,

            descripcion=self.descripcion.value

        )

        # Crear la vista de la aventura

        view = AdventureView(aventura)

        # Crear el embed

        embed = EmbedService.crear_aventura(aventura, guild=interaction.guild)

        # Publicar el mensaje principal

        mensaje = await interaction.channel.send(

            content="@everyone",
            embed=embed,
            view=view,
            allowed_mentions=discord.AllowedMentions(everyone=True),

        )

        # Guardar información del mensaje

        aventura.mensaje_id = mensaje.id
        aventura.canal_id = mensaje.channel.id

        # Guardar el objeto mensaje para futuras actualizaciones
        # (servirá para editar el embed cuando alguien entre o salga)

        aventura.mensaje = mensaje

        # Confirmación para el líder

        confirmacion = discord.Embed(

            title="✅ Aventura creada",

            description=(

                f"**Contenido:** {self.contenido}\n"
                f"**Tipo:** {self.tipo}\n\n"

                "La aventura fue creada correctamente.\n"
                "Los jugadores ya pueden comenzar a unirse."

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

        confirmacion.set_footer(

            text="Albion Party Manager"

        )

        await interaction.response.send_message(

            embed=confirmacion,

            ephemeral=True

        )
