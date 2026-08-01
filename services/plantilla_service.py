import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

PVP = BASE_DIR / "templates" / "pvp.json"
PVE = BASE_DIR / "templates" / "pve.json"
PVP_PRIVATE = BASE_DIR / "templates" / "pvp_private.json"
PVE_PRIVATE = BASE_DIR / "templates" / "pve_private.json"


class PlantillaService:

    def __init__(self):

        self.pvp = self._load_json(PVP)
        self.pve = self._load_json(PVE)
        self.pvp_private = self._load_json(PVP_PRIVATE)
        self.pve_private = self._load_json(PVE_PRIVATE)

    def _load_json(self, ruta):
        if not ruta.exists():
            return {}

        with open(ruta, encoding="utf8") as f:
            return json.load(f)

    def _write_json(self, ruta, data):
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with open(ruta, "w", encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def _normalizar_contenido(self, contenido):
        return (contenido or "").strip().lower()

    def _obtener_contenido_data(self, data, contenido):
        contenido_key = self._normalizar_contenido(contenido)
        if contenido_key in data:
            return data[contenido_key]

        for clave, valor in data.items():
            if str(clave).strip().lower() == contenido_key:
                return valor

        return {}

    def obtener(self, tipo, contenido):

        if tipo.lower() == "pvp":
            return self.pvp.get(contenido, [])

        return self.pve.get(contenido, [])

    def obtener_plantillas_usuario(self, tipo, contenido, user_id):
        user_id = str(user_id)

        if tipo.lower() == "pvp":
            data = self.pvp_private
        else:
            data = self.pve_private

        contenido_data = self._obtener_contenido_data(data, contenido)
        return contenido_data.get(user_id, {})

    def guardar(self, nombre, aventura, user_id):
        nombre = nombre.strip()
        if not nombre:
            return False, "El nombre de la plantilla no puede estar vacío."

        tipo = (aventura.tipo or "").strip().lower()
        if tipo == "pvp":
            destino = PVP_PRIVATE
            data = self.pvp_private
        else:
            destino = PVE_PRIVATE
            data = self.pve_private

        contenido = (aventura.contenido or "").strip()
        contenido_key = contenido.lower() if contenido else "personalizado"
        contenido_data = data.setdefault(contenido_key, {})
        if contenido_key not in data:
            data[contenido_key] = contenido_data
        user_templates = contenido_data.setdefault(str(user_id), {})

        if nombre in user_templates:
            return False, "Ya existe una plantilla con ese nombre para este contenido."

        roles = []
        for rol in aventura.roles.values():
            roles.extend([rol.nombre] * rol.cantidad)

        user_templates[nombre] = roles
        self._write_json(destino, data)

        return True, "Plantilla guardada correctamente."


plantillas = PlantillaService()
