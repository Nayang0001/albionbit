from database.profile_model import Perfil


class PerfilService:

    def __init__(self):

        self.perfiles = {}

    def obtener(self, user_id):

        if user_id not in self.perfiles:

            self.perfiles[user_id] = Perfil(user_id)

        return self.perfiles[user_id]

    def agregar_arma(

        self,

        user_id,

        arma

    ):

        perfil = self.obtener(user_id)

        if arma not in perfil.armas:

            perfil.armas.append(arma)

    def quitar_arma(

        self,

        user_id,

        arma

    ):

        perfil = self.obtener(user_id)

        if arma in perfil.armas:

            perfil.armas.remove(arma)


perfiles = PerfilService()
