import discord

from ui.selects.role_select import RoleSelect


class RoleView(discord.ui.View):

    def __init__(

        self,

        aventura,

        parent_view

    ):

        super().__init__(timeout=120)

        self.add_item(

            RoleSelect(

                aventura,

                parent_view

            )

        )
