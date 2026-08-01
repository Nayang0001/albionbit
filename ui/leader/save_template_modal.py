import discord

from services.plantilla_service import plantillas


class SaveTemplateModal(discord.ui.Modal, title="Guardar como Plantilla"):

    nombre_plantilla = discord.ui.TextInput(
        label="Nombre de la Plantilla",
        placeholder="Ej: Roaming ZvZ, Gank Martlock, HCE T8",
        required=True,
        max_length=80
    )

    def __init__(self, aventura, parent_view):
        super().__init__()
        self.aventura = aventura
        self.parent_view = parent_view

    async def on_submit(self, interaction: discord.Interaction):
        nombre = self.nombre_plantilla.value.strip()

        if not nombre:
            await interaction.response.send_message("❌ Debes poner un nombre a la plantilla.", ephemeral=True)
            return

        ok, mensaje = plantillas.guardar(nombre, self.aventura, interaction.user.id)
        if not ok:
            await interaction.response.send_message(f"❌ {mensaje}", ephemeral=True)
            return

        await interaction.response.send_message(
            f"✅ Plantilla **{nombre}** guardada correctamente.",
            ephemeral=True
        )
