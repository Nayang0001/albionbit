import discord


class RemoveRoleView(discord.ui.View):

    def __init__(self, aventura, parent_view):
        super().__init__(timeout=60)
        self.aventura = aventura
        self.parent_view = parent_view

        # Crear opciones dinámicamente según los roles existentes
        options = []
        for rol in aventura.roles.values():
            options.append(
                discord.SelectOption(
                    label=rol.nombre,
                    emoji=rol.emoji,
                    description=f"{rol.cantidad} plazas"
                )
            )

        self.select = discord.ui.Select(
            placeholder="Selecciona el rol a eliminar",
            options=options
        )
        self.select.callback = self.callback
        self.add_item(self.select)

    async def callback(self, interaction: discord.Interaction):
        rol_nombre = self.select.values[0]

        # Verificar que el rol tenga 0 jugadores
        rol = self.aventura.obtener_rol(rol_nombre)
        if rol and len(rol.jugadores) > 0:
            await interaction.response.send_message(
                "❌ No puedes eliminar un rol que tiene jugadores inscritos.",
                ephemeral=True
            )
            return

        # Eliminar el rol
        if rol_nombre in self.aventura.roles:
            del self.aventura.roles[rol_nombre]

            await self.parent_view.actualizar_embed()

            await interaction.response.send_message(
                f"✅ Rol **{rol_nombre}** eliminado correctamente.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("❌ Rol no encontrado.", ephemeral=True)

        # Cerrar la vista
        self.stop()
