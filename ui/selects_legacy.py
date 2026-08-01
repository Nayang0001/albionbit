import discord


class ContenidoSelect(discord.ui.Select):

    def __init__(self, tipo):

        self.tipo = tipo

        if tipo == "PvP":

            opciones = [

                discord.SelectOption(label="Gank", emoji="🩸"),

                discord.SelectOption(label="Roaming", emoji="⚔️"),

                discord.SelectOption(label="Small Scale", emoji="🛡️"),

                discord.SelectOption(label="Facciones", emoji="🏳️"),

                discord.SelectOption(label="Roads", emoji="🛣️"),

                discord.SelectOption(label="Hellgate", emoji="🔥"),

                discord.SelectOption(label="Cristales", emoji="💎"),

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

        from ui.modals import DescriptionModal

        await interaction.response.send_modal(

            DescriptionModal(

                self.tipo,

                self.values[0]

            )

        )
