from urllib.parse import quote
from pathlib import Path
import json
from typing import Optional
import unicodedata

CACHE_FILE = Path("data/albion_items.json")

# Memoria cache cargada una sola vez para evitar relecturas pesadas del JSON
_ITEMS_CACHE: Optional[list] = None
_ITEMS_INDEX: Optional[dict] = None
_ITEMS_TOKEN_INDEX: Optional[dict] = None

# Nombres del catálogo propio cuyo texto en español no coincide literalmente
# con la localización oficial de Albion.  Así se conserva el icono exacto y no
# se depende de una coincidencia aproximada.
CATALOG_WEAPON_IDS = {
    "espadas dobles": "T4_2H_DUALSWORD", "hacedor de reyes": "T4_2H_CLAYMORE_AVALON",
    "hacha de batalla": "T4_MAIN_AXE", "invocacuervos": "T4_2H_SCYTHE_HELL",
    "segadora de cristal": "T4_2H_SCYTHE_CRYSTAL", "guardianes del juramento": "T4_2H_DUALMACE_AVALON",
    "monarca de tormenta": "T4_MAIN_MACE_CRYSTAL", "martillo de tumba": "T4_2H_HAMMER_UNDEAD",
    "martillo de rayo verdadero": "T4_2H_HAMMER_CRYSTAL", "guantes de luchador": "T4_2H_KNUCKLES_SET1",
    "mutiladores ursinos": "T4_2H_KNUCKLES_KEEPER", "cestos de golpe de cuervo": "T4_2H_KNUCKLES_MORGANA",
    "brazales de pulso de fuerza": "T4_2H_KNUCKLES_AVALON", "lanzavirotes": "T4_2H_DUALCROSSBOW_HELL",
    "explosores arcoluz": "T4_2H_DUALCROSSBOW_CRYSTAL", "arco de lamentos": "T4_2H_BOW_HELL",
    "arco caminacielos": "T4_2H_BOW_CRYSTAL", "doble daga": "T4_2H_DAGGERPAIR",
    "asesinos gemelos": "T4_2H_DAGGERPAIR_CRYSTAL", "cazador de espiritus": "T4_2H_HARPOON_HELL",
    "rompealbas": "T4_MAIN_SPEAR_LANCE_AVALON", "guja de grieta": "T4_2H_GLAIVE_CRYSTAL",
    "baston de combate": "T4_2H_QUARTERSTAFF", "baston acorazado": "T4_2H_IRONCLADEDSTAFF",
    "guadana de alma": "T4_2H_TWINSCYTHE_HELL", "hoja gemela fantasma": "T4_2H_DOUBLEBLADEDSTAFF_CRYSTAL",
    "baston merodeador": "T4_2H_SHAPESHIFTER_SET1", "baston luna de sangre": "T4_2H_SHAPESHIFTER_MORGANA",
    "runa terrestre": "T4_2H_SHAPESHIFTER_KEEPER", "baston mirada fija": "T4_2H_SHAPESHIFTER_CRYSTAL",
    "gran baston de naturaleza": "T4_2H_NATURESTAFF", "baston druidico": "T4_MAIN_NATURESTAFF_KEEPER",
    "baston raiz de hierro": "T4_MAIN_NATURESTAFF_AVALON", "gran baston de fuego": "T4_2H_FIRESTAFF",
    "baston de fuego salvaje": "T4_MAIN_FIRESTAFF_KEEPER", "baston caminallamas": "T4_MAIN_FIRESTAFF_CRYSTAL",
    "baston toque de vida": "T4_MAIN_HOLYSTAFF_MORGANA", "vispera": "T4_2H_ARCANE_RINGPAIR_AVALON",
    "baston de escarcha blanca": "T4_MAIN_FROSTSTAFF_KEEPER", "aullido helado": "T4_MAIN_FROSTSTAFF_AVALON",
    "craneo maldito": "T4_2H_SKULLORB_HELL", "invocador putrefacto": "T4_MAIN_CURSEDSTAFF_CRYSTAL",
}


def _normalize(text: str) -> str:
    """Normaliza nombres para compararlos sin depender de mayúsculas o tildes."""
    decomposed = unicodedata.normalize("NFKD", str(text or ""))
    return "".join(char for char in decomposed if not unicodedata.combining(char)).strip().casefold()


def obtener_url_sprite(item_id: str | None) -> Optional[str]:
    """Genera la URL del icono oficial de un objeto de Albion.

    El identificador puede incluir encantamiento, por ejemplo ``T6_BAG@2``.
    """
    item_id = (item_id or "").strip()
    if not item_id:
        return None
    return f"https://render.albiononline.com/v1/item/{quote(item_id, safe='@_')}.png?size=217"


def _load_items_cache() -> Optional[list]:
    global _ITEMS_CACHE, _ITEMS_INDEX, _ITEMS_TOKEN_INDEX
    if _ITEMS_CACHE is not None:
        return _ITEMS_CACHE

    if not CACHE_FILE.exists():
        return None
    try:
        with CACHE_FILE.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
            if isinstance(data, list):
                _ITEMS_CACHE = data
                # build simple exact name index for fast lookups
                index = {}
                token_index = {}
                for it in data:
                    if not isinstance(it, dict):
                        continue
                    unique = it.get("UniqueName") or it.get("uniqueName")
                    # collect potential labels
                    labels = set()
                    if it.get("Name"):
                        labels.add(str(it.get("Name")).strip())
                    loc = it.get("LocalizedNames") or {}
                    if isinstance(loc, dict):
                        # El catálogo contiene traducciones oficiales, incluido ES-ES.
                        labels.update(str(value).strip() for value in loc.values() if value)
                    if unique:
                        labels.add(str(unique).strip())
                    for lbl in labels:
                        try:
                            key = _normalize(lbl)
                            if key and key not in index:
                                index[key] = unique
                            if key and unique:
                                for token in set(key.split()):
                                    token_index.setdefault(token, []).append((key, str(unique)))
                        except Exception:
                            continue
                _ITEMS_INDEX = index
                _ITEMS_TOKEN_INDEX = token_index
                return _ITEMS_CACHE
    except Exception:
        return None
    return None


def buscar_item_por_nombre(name: str) -> Optional[str]:
    """Busca un `UniqueName` de Albion que mejor coincida con `name`.

    Requiere tener descargado `data/albion_items.json` con la lista de objetos
    (por ejemplo desde https://github.com/ao-data/ao-bin-dumps formatted/items.json).
    Si no hay cache disponible, devuelve ``None`` y el llamador debe manejarlo.
    """
    if not name:
        return None
    catalog_item_id = CATALOG_WEAPON_IDS.get(_normalize(name))
    if catalog_item_id:
        return catalog_item_id
    items = _load_items_cache()
    if not items:
        return None

    needle = _normalize(name)

    # 1) Fast exact lookup via index
    if _ITEMS_INDEX and needle in _ITEMS_INDEX:
        return _ITEMS_INDEX.get(needle)

    # 1b) Try mapping from Spanish display names using database translations
    try:
        from database.armas import TRADUCCIONES
        # reverse mapping: spanish -> english
        for eng, spa in TRADUCCIONES.items():
            if _normalize(spa) == needle:
                # try exact lookup by english name
                key = _normalize(eng)
                if _ITEMS_INDEX and key in _ITEMS_INDEX:
                    return _ITEMS_INDEX.get(key)
                # also try english as substring fallback
                needle = key
                break
    except Exception:
        pass

    # 2) Fall back to a ranked substring scan.  A simple "first match" can
    # select an artefact component instead of the actual weapon (for example,
    # a generic crossbow), because those objects occur earlier in items.json.
    matches: list[tuple[tuple[int, int, int], str]] = []
    needle_tokens = needle.split()
    candidates = []
    if _ITEMS_TOKEN_INDEX and needle_tokens:
        # Usar el término menos frecuente conserva la búsqueda flexible, pero
        # evita recorrer cientos de miles de objetos en cada interacción.
        candidates = min(
            (_ITEMS_TOKEN_INDEX.get(token, []) for token in needle_tokens),
            key=len,
            default=[],
        )

    for normalized_label, item_id in candidates:
        if needle not in normalized_label:
            continue
        normalized_id = _normalize(item_id)
        # Prefer an equipable tier-4 item.  It gives a consistent base icon
        # and filters crafting components, skins, etc.
        non_equipment = int(any(token in normalized_id for token in (
            "artefact", "token", "skin", "quest", "journal",
        )))
        tier_penalty = 0 if item_id.startswith("T4_") else 1
        extra_words = max(0, len(normalized_label.split()) - len(needle_tokens))
        matches.append(((non_equipment, tier_penalty, extra_words), item_id))

    if matches:
        matches.sort(key=lambda match: match[0])
        return matches[0][1]
    return None
