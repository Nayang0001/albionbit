import discord

from database.armas import obtener_armas_por_rol
from services.build_service import obtener_build
from ui.selects.weapon_select import WeaponSelect
from services.albion_items import buscar_item_por_nombre, obtener_url_sprite
from database.armas import mostrar_nombre_arma


class WeaponView(discord.ui.View):

    def __init__(

        self,

        aventura,

        rol,

        parent_view,

        user_id

    ):

        super().__init__(timeout=180)
        self.aventura = aventura
        self.rol = rol
        self.parent_view = parent_view
        self.user_id = user_id
        self.pagina = 0

        armas = obtener_armas_por_rol(rol, aventura.contenido)
        build_guardada = obtener_build(user_id, aventura.contenido, rol)
        if build_guardada and build_guardada not in armas:
            armas.insert(0, build_guardada)
        self.armas = list(dict.fromkeys(armas))
        self._renderizar()

    @property
    def _tamano_pagina(self):
        # Se reserva una opción para «Agregar mi build» si aún no hay una guardada.
        return 25 if obtener_build(self.user_id, self.aventura.contenido, self.rol) else 24

    def _renderizar(self):
        self.clear_items()
        inicio = self.pagina * self._tamano_pagina
        fin = inicio + self._tamano_pagina
        total_paginas = max(1, (len(self.armas) + self._tamano_pagina - 1) // self._tamano_pagina)
        self.add_item(WeaponSelect(
            self.aventura, self.rol, self.parent_view, self.user_id,
            armas=self.armas[inicio:fin],
        ))
        if total_paginas > 1:
            anterior = discord.ui.Button(label="◀ Anterior", style=discord.ButtonStyle.secondary, disabled=self.pagina == 0)
            siguiente = discord.ui.Button(label="Siguiente ▶", style=discord.ButtonStyle.secondary, disabled=self.pagina >= total_paginas - 1)

            async def ir_anterior(interaction):
                self.pagina -= 1
                self._renderizar()
                await interaction.response.edit_message(view=self)

            async def ir_siguiente(interaction):
                self.pagina += 1
                self._renderizar()
                await interaction.response.edit_message(view=self)

            anterior.callback = ir_anterior
            siguiente.callback = ir_siguiente
            self.add_item(anterior)
            self.add_item(siguiente)

        # Botón para previsualizar sprites de los items en la página actual
        if self.armas:
            ver_sprites_btn = discord.ui.Button(label="🔎 Ver sprites", style=discord.ButtonStyle.secondary)

            async def ver_sprites(interaction: discord.Interaction):
                inicio = self.pagina * self._tamano_pagina
                fin = inicio + self._tamano_pagina
                items = self.armas[inicio:fin]

                embeds = []
                for arma in items[:10]:
                    nombre = mostrar_nombre_arma(str(arma))
                    embed = discord.Embed(title=nombre, color=0x3498DB)
                    try:
                        item_id = buscar_item_por_nombre(arma)
                        sprite = obtener_url_sprite(item_id)
                        if sprite:
                            embed.set_thumbnail(url=sprite)
                    except Exception:
                        pass
                    embeds.append(embed)

                if not embeds:
                    await interaction.response.send_message("No hay sprites disponibles para los items listados.", ephemeral=True)
                    return

                await interaction.response.send_message(embeds=embeds, ephemeral=True)

            ver_sprites_btn.callback = ver_sprites
            self.add_item(ver_sprites_btn)
