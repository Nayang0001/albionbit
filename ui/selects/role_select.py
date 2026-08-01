import discord


class RoleSelect(discord.ui.Select):

    def __init__(

        self,

        aventura,

        parent_view

    ):

        self.aventura = aventura
        self.parent_view = parent_view

        opciones = []

        for index, rol in enumerate(aventura.roles.values()):

            texto = f"{rol.libres} libres"

            if rol.libres == 0:
                texto = "Completo"

            nombre_visible = rol.nombre_mostrado
            emoji_display = rol.emoji or "🎯"
            if not emoji_display or emoji_display in {"❔", "?"}:
                emoji_display = "🎯"

            descripcion_visible = texto

            opciones.append(

                discord.SelectOption(

                    label=nombre_visible,
                    value=f"{rol.nombre}::{index}",
                    emoji=emoji_display,
                    description=descripcion_visible

                )

            )

        super().__init__(

            placeholder="Selecciona tu rol",

            min_values=1,

            max_values=1,

            options=opciones

        )

    async def callback(

        self,

        interaction: discord.Interaction

    ):

        try:

            # No permitir dos roles

            if self.aventura.jugador_tiene_rol(

                interaction.user.id

            ):

                await interaction.response.send_message(

                    "❌ Ya perteneces a esta aventura.",

                    ephemeral=True

                )

                return

            if not self.values:
                await interaction.response.send_message(
                    "❌ No se seleccionó ningún rol.",
                    ephemeral=True
                )
                return

            rol = self.values[0]
            rol_key = rol.split("::", 1)[0] if "::" in rol else rol

            rol_obj = self.aventura.obtener_rol(rol_key)

            if rol_obj is None:
                rol_obj = next(
                    (
                        rol_item for rol_item in self.aventura.roles.values()
                        if rol_item.nombre == rol_key or rol_item.nombre_mostrado == rol_key or rol_item.categoria == rol_key
                    ),
                    None
                )

            if rol_obj is None:

                await interaction.response.send_message(

                    "Ese rol ya no existe.",

                    ephemeral=True

                )

                return

            if rol_obj.lleno:

                await interaction.response.send_message(

                    "❌ Ese rol ya está completo.",

                    ephemeral=True

                )

                return

            # El catálogo de armas se conserva, pero no participa en la
            # inscripción hasta que esta función sea reactivada.
            if not self.aventura.agregar_jugador(rol_obj.nombre, interaction.user.id, ""):
                await interaction.response.send_message(
                    "❌ No fue posible registrarte en ese rol.",
                    ephemeral=True,
                )
                return

            await self.parent_view.actualizar_embed()
            await interaction.response.send_message(
                content=f"✅ Te inscribiste como **{rol_obj.nombre_mostrado}**.",
                ephemeral=True,
            )

        except Exception as exc:
            await interaction.response.send_message(
                f"❌ Ocurrió un error al seleccionar el rol: {exc}",
                ephemeral=True
            )
