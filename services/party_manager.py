from services.aventura_service import aventuras


class PartyManager:

    def unirse(

        self,

        aventura_id,

        jugador_id,

        rol

    ):

        aventura = aventuras.obtener(

            aventura_id

        )

        if aventura is None:

            return False, "La aventura no existe."

        if not aventura.abierta:

            return False, "La aventura está cerrada."

        if aventura.jugador_tiene_rol(

            jugador_id

        ):

            return False, "Ya estás inscrito."

        if aventura.agregar_jugador(

            rol,

            jugador_id

        ):

            return True, "Te uniste correctamente."

        return False, "Ese rol ya está lleno."

    def salir(

        self,

        aventura_id,

        jugador_id

    ):

        aventura = aventuras.obtener(

            aventura_id

        )

        if aventura is None:

            return False

        return aventura.quitar_jugador(

            jugador_id

        )


party = PartyManager()
