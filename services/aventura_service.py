import re
import unicodedata
from database.models import Adventure


def normalizar_texto(texto):
    texto = unicodedata.normalize("NFKD", (texto or "").strip().lower())
    texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
    return re.sub(r"[^a-z0-9]+", "", texto)


def es_contenido_avalon(contenido):
    return normalizar_texto(contenido) in {
        "avalon",
        "avaloniana",
        "avaloniana6",
        "avaloniana61",
    }


class AdventureService:

    def __init__(self):

        # id de aventura -> Adventure
        self.aventuras = {}

        # leader_id -> id aventura
        self.lideres = {}

        # mensaje_id -> id aventura
        self.mensajes = {}

    def _normalizar_texto(self, texto):
        return normalizar_texto(texto)

    def _aplicar_roles_por_defecto(self, aventura):
        tipo = (aventura.tipo or "").strip().lower()
        contenido = self._normalizar_texto(aventura.contenido)

        if es_contenido_avalon(contenido):
            contenido = "avalon"

        mapping = {}
        if tipo == "pvp":
            mapping = {
                "gank": [("Stopper", 2), ("Healer", 1), ("DPS", 6)],
                "facciones": [("Clapper", 1), ("Healer", 1), ("Stopper", 1), ("Support", 1), ("DPS", 6)],
                "roaming": [("Tank", 1), ("Healer", 1), ("Stopper", 1), ("Support", 1), ("DPS", 6)],
                "smallscale": [("Tank", 1), ("Healer", 1), ("Stopper", 1), ("Support", 1), ("DPS", 6)],
                "pequenaescala": [("Tank", 1), ("Healer", 1), ("Stopper", 1), ("Support", 1), ("DPS", 6)],
            }
        elif tipo == "pve":
            mapping = {
                "grupales": [("Tank", 1), ("Healer", 1), ("Support", 1), ("DPS", 3)],
                "estaticas": [("Tank", 1), ("Healer", 1), ("Stopper", 1), ("Support", 1), ("DPS", 6)],
                "estatica": [("Tank", 1), ("Healer", 1), ("Stopper", 1), ("Support", 1), ("DPS", 6)],
                "avalon": [("Tank", 1), ("OFF", 1), ("COBRA/GA", 1), ("MAIN HEALER", 1), ("PARTY HEALER", 1), ("SC", 1), ("DPS", 4)],
            }

        for nombre, cantidad in mapping.get(contenido, []):
            aventura.agregar_rol(nombre=nombre, categoria=nombre, emoji="❔", cantidad=cantidad)

    def crear(
        self,
        guild_id,
        leader_id,
        tipo,
        contenido,
        descripcion,
        plantilla_roles=None
    ):

        aventura = Adventure(

            guild_id=guild_id,

            leader_id=leader_id,

            tipo=tipo,

            contenido=contenido,

            descripcion=descripcion

        )

        if plantilla_roles is not None:
            roles = plantilla_roles
        else:
            roles = []

        if roles:
            if isinstance(roles[0], str):
                from collections import Counter
                conteo = Counter(roles)
                for nombre, cantidad in conteo.items():
                    aventura.agregar_rol(
                        nombre=nombre,
                        categoria=nombre,
                        emoji="❔",
                        cantidad=cantidad
                    )
            elif isinstance(roles[0], dict):
                for rol in roles:
                    aventura.agregar_rol(
                        nombre=rol.get("nombre", "Rol"),
                        categoria=rol.get("categoria", "General"),
                        emoji=rol.get("emoji", "❔"),
                        cantidad=rol.get("cantidad", 1)
                    )
            else:
                for rol in roles:
                    try:
                        aventura.agregar_rol(
                            nombre=rol.nombre,
                            categoria=getattr(rol, "categoria", "General"),
                            emoji=getattr(rol, "emoji", "❔"),
                            cantidad=getattr(rol, "cantidad", 1)
                        )
                    except Exception:
                        pass

        if not aventura.roles:
            self._aplicar_roles_por_defecto(aventura)

        # Guardar aventura

        self.aventuras[aventura.id] = aventura

        self.lideres[leader_id] = aventura.id

        return aventura

    def registrar_mensaje(
        self,
        aventura,
        mensaje
    ):

        aventura.mensaje_id = mensaje.id
        aventura.canal_id = mensaje.channel.id

        self.mensajes[mensaje.id] = aventura.id

    def obtener(self, aventura_id):

        return self.aventuras.get(aventura_id)

    def obtener_por_lider(self, leader_id):

        aventura_id = self.lideres.get(leader_id)

        if aventura_id is None:
            return None

        return self.aventuras.get(aventura_id)

    def obtener_por_mensaje(self, mensaje_id):

        aventura_id = self.mensajes.get(mensaje_id)

        if aventura_id is None:
            return None

        return self.aventuras.get(aventura_id)

    def eliminar(self, aventura_id):

        aventura = self.aventuras.pop(

            aventura_id,

            None

        )

        if aventura is None:
            return

        self.lideres.pop(

            aventura.leader_id,

            None

        )

        if aventura.mensaje_id is not None:

            self.mensajes.pop(

                aventura.mensaje_id,

                None

            )

    def transferir_lider(self, aventura, new_leader_id: int) -> bool:
        """Transfer ownership of an Adventure to another user.

        Updates the `leader_id` on the Adventure and the internal leader index.
        Removes the new leader from sub_admins if present.
        """
        if aventura is None or new_leader_id <= 0:
            return False

        old_leader = aventura.leader_id
        if old_leader == new_leader_id:
            return False

        # Update mapping
        try:
            self.lideres.pop(old_leader, None)
        except Exception:
            pass

        aventura.leader_id = new_leader_id
        self.lideres[new_leader_id] = aventura.id

        # Ensure the new leader is not in sub_admins
        try:
            if new_leader_id in aventura.sub_admins:
                aventura.sub_admins.remove(new_leader_id)
        except Exception:
            pass

        return True


aventuras = AdventureService()
