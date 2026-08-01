from services.aventura_service import aventuras


class AdventureManager:

    def __init__(self):

        self.activas = {}

    def registrar(self, aventura):

        self.activas[aventura.id] = aventura

    def obtener(self, adventure_id):

        return self.activas.get(adventure_id)

    def eliminar(self, adventure_id):

        self.activas.pop(adventure_id, None)


manager = AdventureManager()
