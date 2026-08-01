import discord

from services.aventura_service import aventuras
from services.embed_service import EmbedService


class SharePermissionsView(discord.ui.View):
    """Permite al creador delegar edición a un miembro o a un rol del servidor."""

    def __init__(self, aventura, parent_view):
        super().__init__(timeout=180)
        self.aventura = aventura
        self.parent_view = parent_view

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.aventura.leader_id:
            return True
        await interaction.response.send_message(
            "❌ Solo quien creó la aventura puede gestionar permisos.", ephemeral=True
        )
        return False

    @discord.ui.select(
        cls=discord.ui.RoleSelect,
        placeholder="Añadir un rol del servidor (moderador, staff, reclutador...)",
        min_values=1,
        max_values=1,
    )
    async def seleccionar_rol(self, interaction: discord.Interaction, select: discord.ui.RoleSelect):
        rol = select.values[0]
        if rol.is_default():
            await interaction.response.send_message("❌ No se puede asignar @everyone como editor.", ephemeral=True)
            return
        if not self.aventura.agregar_rol_editor(rol.id):
            await interaction.response.send_message("❌ Ese rol ya tiene permisos de edición.", ephemeral=True)
            return
        await interaction.response.send_message(
            f"✅ El rol {rol.mention} ya puede editar esta aventura.", ephemeral=True
        )

    @discord.ui.select(
        cls=discord.ui.UserSelect,
        placeholder="O añade a una persona concreta",
        min_values=1,
        max_values=1,
    )
    async def seleccionar_usuario(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        usuario = select.values[0]
        if usuario.id == self.aventura.leader_id:
            await interaction.response.send_message("❌ El creador ya tiene permisos de edición.", ephemeral=True)
            return
        if not self.aventura.agregar_editor(usuario.id):
            await interaction.response.send_message("❌ Esa persona ya tiene permisos de edición.", ephemeral=True)
            return
        await interaction.response.send_message(
            f"✅ Se añadió a {usuario.mention} como sub-admin de la aventura.", ephemeral=True
        )

    @discord.ui.select(
        cls=discord.ui.UserSelect,
        placeholder="Transferir liderazgo a...",
        min_values=1,
        max_values=1,
    )
    async def transferir_lider_select(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        nuevo = select.values[0]
        if nuevo.id == self.aventura.leader_id:
            await interaction.response.send_message("❌ Esa persona ya es el líder.", ephemeral=True)
            return

        # Perform transfer via service to keep mappings in sync
        success = aventuras.transferir_lider(self.aventura, nuevo.id)
        if not success:
            await interaction.response.send_message("❌ No se pudo transferir el liderazgo.", ephemeral=True)
            return

        await interaction.response.send_message(f"✅ Liderazgo transferido a {nuevo.mention}.", ephemeral=True)
        # Actualizar el mensaje público de la aventura si existe
        try:
            embed = EmbedService.crear_aventura(self.aventura, guild=interaction.guild)
            channel = None
            if getattr(self.aventura, "mensaje", None) is not None:
                try:
                    await self.aventura.mensaje.edit(embed=embed)
                except Exception:
                    pass
            else:
                if getattr(self.aventura, "canal_id", None):
                    channel = interaction.guild.get_channel(self.aventura.canal_id)
                if channel is None and interaction.channel is not None:
                    channel = interaction.channel
                if channel is not None and getattr(self.aventura, "mensaje_id", None):
                    try:
                        mensaje = await channel.fetch_message(self.aventura.mensaje_id)
                        await mensaje.edit(embed=embed)
                    except Exception:
                        pass
        except Exception:
            # Si falla la actualización del embed, ignorar y continuar
            pass

        # Optionally notify the new leader via DM
        try:
            await nuevo.send(f"Has sido asignado líder de la aventura `{self.aventura.id}`.")
        except Exception:
            pass
