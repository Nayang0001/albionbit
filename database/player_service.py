from database.player_repository import player_repository


class PlayerService:

    def registrar(

        self,

        usuario

    ):

        jugador = player_repository.obtener(

            usuario.id

        )

        if jugador is None:

            player_repository.crear(

                usuario.id,

                usuario.display_name

            )

        else:

            player_repository.cambiar_nombre(

                usuario.id,

                usuario.display_name

            )


players = PlayerService()
