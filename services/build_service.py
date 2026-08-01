import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "user_builds.json"


def _cargar_datos():
    if not DATA_FILE.exists():
        return {}

    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _guardar_datos(datos):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8")


def guardar_build(user_id, contenido, rol, arma, categoria=None):
    datos = _cargar_datos()
    usuario = datos.setdefault(str(user_id), {})
    contenido_datos = usuario.setdefault(contenido, {})
    contenido_datos[rol] = {
        "arma": arma,
        "categoria": categoria or ""
    }
    _guardar_datos(datos)
    return arma


def obtener_build(user_id, contenido, rol):
    datos = _cargar_datos()
    datos_rol = datos.get(str(user_id), {}).get(contenido, {}).get(rol)
    if isinstance(datos_rol, dict):
        return datos_rol.get("arma")
    return datos_rol
