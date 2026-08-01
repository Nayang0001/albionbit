import discord
from ui.leader.change_loot_modal import ChangeLootModal
from ui.leader.change_portal_modal import ChangePortalModal
from ui.leader.change_tier_modal import ChangeTierModal
from ui.leader.edit_description_modal import EditDescriptionModal
from ui.leader.add_role_modal import AddRoleModal, EmojiSelectionView
from ui.leader.remove_role_view import RemoveRoleView
from ui.leader.save_template_modal import SaveTemplateModal


class LeaderView(discord.ui.View):

    def __init__(self, aventura, parent_view):
        super().__init__(timeout=300)
        self.aventura = aventura
        self.parent_view = parent_view

    @discord.ui.select(
        placeholder="Selecciona una acción",
        options=[
            discord.SelectOption(label="Agregar Rol", emoji="➕", description="Añadir un nuevo rol"),
            discord.SelectOption(label="Eliminar Rol", emoji="➖", description="Eliminar un rol existente"),
            discord.SelectOption(label="Editar Descripción", emoji="✏️", description="Modificar la descripción"),
            discord.SelectOption(label="Cambiar Tier", emoji="🛡️", description="Cambiar el Tier requerido"),
            discord.SelectOption(label="Cambiar Portal", emoji="📍", description="Modificar el portal"),
            discord.SelectOption(label="Cambiar Loot", emoji="💰", description="Modificar el tipo de loot"),
            discord.SelectOption(label="Guardar Plantilla", emoji="💾", description="Guardar esta composición"),
        ]
    )
    async def menu(self, interaction: discord.Interaction, select: discord.ui.Select):
        opcion = select.values[0]

        # ==================== EDITAR DESCRIPCIÓN ====================
        if opcion == "Editar Descripción":
            await interaction.response.send_modal(
                EditDescriptionModal(self.aventura, self.parent_view)
            )
            return

        # ==================== AGREGAR ROL ====================
        if opcion == "Agregar Rol":
            await interaction.response.send_message(
                "Selecciona un emoji para el rol:",
                view=EmojiSelectionView(self.aventura, self.parent_view),
                ephemeral=True
            )
            return

        # ==================== ELIMINAR ROL ====================
        if opcion == "Eliminar Rol":
            if not self.aventura.roles:
                await interaction.response.send_message(
                    "❌ No hay roles para eliminar.",
                    ephemeral=True
                )
                return

            await interaction.response.send_message(
                "Selecciona el rol que deseas eliminar:",
                view=RemoveRoleView(self.aventura, self.parent_view),
                ephemeral=True
            )
            return

        # ==================== CAMBIAR TIER ====================
        if opcion == "Cambiar Tier":
            await interaction.response.send_modal(
                ChangeTierModal(self.aventura, self.parent_view)
            )
            return

        # ==================== CAMBIAR PORTAL ====================
        if opcion == "Cambiar Portal":
            await interaction.response.send_modal(
                ChangePortalModal(self.aventura, self.parent_view)
            )
            return

        # ==================== CAMBIAR LOOT ====================
        if opcion == "Cambiar Loot":
            await interaction.response.send_modal(
                ChangeLootModal(self.aventura, self.parent_view)
            )
            return

        # ==================== GUARDAR PLANTILLA ====================
        if opcion == "Guardar Plantilla":
            await interaction.response.send_modal(
                SaveTemplateModal(self.aventura, self.parent_view)
            )
            return

        # ==================== OTRAS OPCIONES (pendientes) ====================
        await interaction.response.send_message(
            "🚧 Esta función estará disponible muy pronto.",
            ephemeral=True
        )
