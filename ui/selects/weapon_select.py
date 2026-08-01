import discord

from database.armas import mostrar_nombre_arma, obtener_armas_por_rol
from services.build_service import guardar_build, obtener_build
from services.albion_items import buscar_item_por_nombre, obtener_url_sprite


class BuildModal(discord.ui.Modal, title="Agregar mi build"):

    arma = discord.ui.TextInput(
        label="Nombre de la build",
        placeholder="Ej: Bear Paws, Hallowfall, Incubus Mace",
        required=True,
        max_length=80
    )

    def __init__(self, aventura, rol, parent_view, user_id):
        super().__init__()
        self.aventura = aventura
        self.rol = rol
        self.parent_view = parent_view
        self.user_id = user_id

    async def on_submit(self, interaction: discord.Interaction):
        nombre_build = self.arma.value.strip()
        if not nombre_build:
            await interaction.response.send_message("❌ Debes ingresar un nombre de build.", ephemeral=True)
            return

        guardar_build(self.user_id, self.aventura.contenido, self.rol, nombre_build, categoria=self.rol)

        await interaction.response.send_message(
            f"✅ Build guardada para **{self.rol}** en **{self.aventura.contenido}**.",
            ephemeral=True
        )


class WeaponSelect(discord.ui.Select):

    def __init__(

        self,

        aventura,

        rol,

        parent_view,

        user_id,

        armas=None,

        permitir_build_personalizada=True,

    ):

        self.aventura = aventura
        self.rol = rol
        self.parent_view = parent_view
        self.user_id = user_id

        opciones = []

        if armas is None:
            armas = obtener_armas_por_rol(rol, aventura.contenido)[:24]

        build_guardada = obtener_build(user_id, aventura.contenido, rol)

        if not armas:
            armas = ["Sin armas configuradas"]

        armas_unicas = []
        valores_vistos = set()
        for arma in armas:
            valor = str(arma).strip()
            if not valor or valor in valores_vistos:
                continue
            valores_vistos.add(valor)
            armas_unicas.append(valor)

        for arma in armas_unicas:
            nombre_mostrado = mostrar_nombre_arma(str(arma))
            valor = str(arma)
            opciones.append(
                discord.SelectOption(label=nombre_mostrado, value=valor)
            )

        if permitir_build_personalizada and build_guardada is None:
            opciones.append(discord.SelectOption(label="➕ Agregar mi build", value="__ADD_BUILD__"))

        super().__init__(

            placeholder=f"Selecciona el arma para {rol}",

            min_values=1,

            max_values=1,

            options=opciones

        )

    async def callback(

        self,

        interaction: discord.Interaction

    ):

        try:

            # ¿La aventura sigue abierta?

            if not self.aventura.abierta:

                await interaction.response.send_message(

                    "❌ Esta aventura ya fue cerrada.",

                    ephemeral=True

                )

                return

            # Ya tiene un rol

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
                    "❌ No se seleccionó ninguna arma.",
                    ephemeral=True
                )
                return

            arma = self.values[0].split("::", 1)[0]

            if arma == "__ADD_BUILD__":
                await interaction.response.send_modal(BuildModal(self.aventura, self.rol, self.parent_view, self.user_id))
                return

            if arma == "Sin armas configuradas":

                await interaction.response.send_message(

                    "❌ Ese rol todavía no tiene armas configuradas.",

                    ephemeral=True

                )

                return

            # Responder dentro de los tres segundos exigidos por Discord antes
            # de actualizar el panel o resolver el sprite del arma.
            await interaction.response.defer(ephemeral=True)

            guardar_build(interaction.user.id, self.aventura.contenido, self.rol, arma, categoria=self.rol)

            registrado = self.aventura.agregar_jugador(

                self.rol,

                interaction.user.id,

                arma

            )

            if not registrado:

                await interaction.followup.send(

                    "❌ No fue posible registrarte en ese rol.",

                    ephemeral=True

                )

                return

            # Actualizar el embed principal

            await self.parent_view.actualizar_embed()

            embed = discord.Embed(

                title="✅ Inscripción completada",

                description=(
                    f"Has seleccionado **{mostrar_nombre_arma(arma)}**.\n\n"
                    f"**Rol:** {self.rol}\n"
                    f"**Arma:** {mostrar_nombre_arma(arma)}"

                ),

                color=0x2ECC71

            )

            embed.set_footer(

                text="Albion Party Manager"

            )

            # intentar resolver sprite del arma seleccionada (si el proyecto tiene cache)
            try:
                item_id = buscar_item_por_nombre(arma)
                sprite = obtener_url_sprite(item_id)
                if sprite:
                    # La imagen principal se muestra debajo del texto de confirmación.
                    embed.set_image(url=sprite)
            except Exception:
                pass

            await interaction.followup.send(
                embed=embed,
                ephemeral=True
            )

        except Exception as exc:
            if interaction.response.is_done():
                await interaction.followup.send(
                    f"❌ Ocurrió un error al completar la inscripción: {exc}",
                    ephemeral=True
                )
                return
            await interaction.response.send_message(
                f"❌ Ocurrió un error al completar la inscripción: {exc}",
                ephemeral=True
            )
