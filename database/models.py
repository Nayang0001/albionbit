import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict
from uuid import uuid4

CATALOGO_ROLES_PATH = Path(__file__).resolve().parent.parent / "data" / "roles_catalog.json"

ROLES_CONOCIDOS: Dict[str, "Rol"] = {}


def _cargar_catalogo_roles() -> None:
    if not CATALOGO_ROLES_PATH.exists():
        return

    try:
        datos = json.loads(CATALOGO_ROLES_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return

    for nombre, info in datos.items():
        if not isinstance(info, dict):
            continue
        rol = Rol(
            nombre=nombre,
            categoria=info.get("categoria", nombre),
            emoji=info.get("emoji", "🎯"),
            cantidad=int(info.get("cantidad", 1) or 1),
        )
        ROLES_CONOCIDOS[nombre] = rol


def _guardar_catalogo_roles() -> None:
    CATALOGO_ROLES_PATH.parent.mkdir(parents=True, exist_ok=True)
    datos = {}
    for nombre, rol in sorted(ROLES_CONOCIDOS.items()):
        datos[nombre] = {
            "categoria": rol.categoria,
            "emoji": rol.emoji,
            "cantidad": rol.cantidad,
        }
    CATALOGO_ROLES_PATH.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


def limpiar_roles_conocidos() -> None:
    ROLES_CONOCIDOS.clear()
    _guardar_catalogo_roles()


def registrar_rol_global(nombre: str, categoria: str, emoji: str, cantidad: int=1):
    if not nombre:
        return None

    nombre_limpio = _normalizar_nombre_rol(nombre)
    if not nombre_limpio:
        return None

    categoria_limpia = (categoria or nombre_limpio).strip()
    emoji_final = emoji if emoji and str(emoji).strip() not in {"", "❔", "?"} else _emoji_por_rol(nombre_limpio)

    rol_existente = ROLES_CONOCIDOS.get(nombre_limpio)
    if rol_existente is not None:
        rol_existente.categoria = categoria_limpia or rol_existente.categoria
        if not rol_existente.emoji or rol_existente.emoji in {"❔", "?"}:
            rol_existente.emoji = emoji_final
        rol_existente.cantidad = max(rol_existente.cantidad, cantidad)
        _guardar_catalogo_roles()
        return rol_existente

    rol_nuevo = Rol(
        nombre=nombre_limpio,
        categoria=categoria_limpia or nombre_limpio,
        emoji=emoji_final,
        cantidad=cantidad,
    )
    ROLES_CONOCIDOS[nombre_limpio] = rol_nuevo
    _guardar_catalogo_roles()
    return rol_nuevo


def copiar_roles_conocidos_a_aventura(aventura) -> None:
    for nombre_rol, rol_global in ROLES_CONOCIDOS.items():
        if nombre_rol in aventura.roles:
            continue

        aventura.roles[nombre_rol] = Rol(
            nombre=rol_global.nombre,
            categoria=rol_global.categoria,
            emoji=rol_global.emoji,
            cantidad=rol_global.cantidad,
        )


def _normalizar_nombre_rol(nombre: str) -> str:
    if not nombre:
        return ""

    texto = nombre.strip().lower()
    mapeo = {
        "tank": "Tank",
        "tanque": "Tank",
        "healer": "Healer",
        "sanador": "Healer",
        "support": "Support",
        "apoyo": "Support",
        "dps": "DPS",
        "holy": "Holy",
        "sagrado": "Holy",
        "nature": "Nature",
        "naturaleza": "Nature",
        "puller": "Puller",
        "clapper": "Clapper",
        "stopper": "Stopper",
        "pierce": "Pierce",
        "perforador": "Pierce",
        "garra": "Agarre",
        "garras": "Agarre",
        "agarre": "Agarre",
        "prisma": "Prisma",
        "sc": "SC",
        "badon": "Badon",
    }

    return mapeo.get(texto, nombre.strip())


def _mostrar_nombre_rol(nombre: str) -> str:
    if not nombre:
        return ""

    texto = nombre.strip()
    mapeo = {
        "Tank": "Tank",
        "Tanque": "Tank",
        "Healer": "Healer",
        "Sanador": "Healer",
        "Support": "Support",
        "Apoyo": "Support",
        "DPS": "DPS",
        "Holy": "Holy",
        "Sagrado": "Holy",
        "Nature": "Nature",
        "Naturaleza": "Nature",
        "Puller": "Puller",
        "Clapper": "Clapper",
        "Stopper": "Stopper",
        "Pierce": "Pierce",
        "Perforador": "Pierce",
        "Agarre": "Agarre",
        "Garras": "Agarre",
        "Garra": "Agarre",
        "Prisma": "Prisma",
        "SC": "SC",
        "Flami": "Flami",
        "Flamígero": "Flamígero",
        "Badon": "Badon",
    }

    return mapeo.get(texto, texto)


def _emoji_por_rol(nombre: str) -> str:
    texto = _normalizar_nombre_rol(nombre)
    mapeo = {
        "Tank": "🛡️",
        "Healer": "❤️",
        "Support": "✨",
        "DPS": "⚔️",
        "Holy": "🔮",
        "Nature": "🌿",
        "Puller": "🧲",
        "Clapper": "🔨",
        "Stopper": "🚧",
        "Pierce": "🗡️",
        "Agarre": "🪓",
        "Prisma": "💎",
        "SC": "🧠",
        "Flami": "🔥",
        "Badon": "🏹",
    }

    return mapeo.get(texto, "🎯")


# =====================================================
# ROL
# =====================================================
@dataclass
class Rol:
    nombre: str
    categoria: str
    emoji: str

    cantidad: int = 1

    # jugador_id -> arma
    jugadores: Dict[int, str] = field(default_factory=dict)

    @property
    def libres(self):
        return self.cantidad - len(self.jugadores)

    @property
    def nombre_mostrado(self):
        texto = self.categoria.strip() if self.categoria and self.categoria.strip() else self.nombre
        return _mostrar_nombre_rol(texto)

    @property
    def lleno(self):
        return len(self.jugadores) >= self.cantidad


_cargar_catalogo_roles()


# =====================================================
# AVENTURA
# =====================================================
@dataclass
class Adventure:
    id: str = field(default_factory=lambda: str(uuid4()))

    guild_id: int = 0
    leader_id: int = 0

    tipo: str = ""
    contenido: str = ""
    descripcion: str = ""
    tier: str = ""  # ← AÑADIDO
    portal: str = ""  # ← AÑADIR ESTA LÍNEA
    roles: Dict[str, Rol] = field(default_factory=dict)
    loot: str = ""
    finalizada: bool = False
    loot_total: float = 0.0
    silver_total: float = 0.0
    sub_admins: list[int] = field(default_factory=list)
    editor_role_ids: list[int] = field(default_factory=list)
    loot_entregado: Dict[int, bool] = field(default_factory=dict)
    
    mensaje_id: int | None = None
    canal_id: int | None = None

    abierta: bool = True

    # =================================================
    def agregar_rol(
        self,
        nombre: str,
        categoria: str,
        emoji: str,
        cantidad: int=1
    ):
        nombre_limpio = _normalizar_nombre_rol(nombre)
        if not nombre_limpio:
            return None

        categoria_limpia = (categoria or nombre_limpio).strip()
        emoji_final = emoji if emoji and str(emoji).strip() not in {"", "❔", "?"} else _emoji_por_rol(nombre_limpio)

        registrar_rol_global(nombre_limpio, categoria_limpia, emoji_final, cantidad)

        if nombre_limpio in self.roles:
            self.roles[nombre_limpio].categoria = categoria_limpia or self.roles[nombre_limpio].categoria
            if not self.roles[nombre_limpio].emoji or self.roles[nombre_limpio].emoji in {"❔", "?"}:
                self.roles[nombre_limpio].emoji = emoji_final
            self.roles[nombre_limpio].cantidad = max(self.roles[nombre_limpio].cantidad, cantidad)
            return self.roles[nombre_limpio]

        self.roles[nombre_limpio] = Rol(
            nombre=nombre_limpio,
            categoria=categoria_limpia or nombre_limpio,
            emoji=emoji_final,
            cantidad=cantidad
        )
        return self.roles[nombre_limpio]

    # =================================================
    def obtener_rol(self, nombre: str):
        return self.roles.get(nombre)

    # =================================================
    def jugador_tiene_rol(self, jugador_id: int) -> bool:
        return self.obtener_rol_jugador(jugador_id) is not None

    # =================================================
    def obtener_rol_jugador(self, jugador_id: int):
        for rol in self.roles.values():
            if jugador_id in rol.jugadores:
                return rol
        return None

    # =================================================
    def obtener_arma_jugador(self, jugador_id: int):
        rol = self.obtener_rol_jugador(jugador_id)
        if rol is None:
            return None
        return rol.jugadores.get(jugador_id)

    # =================================================
    def agregar_jugador(self, rol_nombre: str, jugador_id: int, arma: str) -> bool:
        rol = self.obtener_rol(rol_nombre)
        if rol is None:
            return False
        if rol.lleno:
            return False
        if self.jugador_tiene_rol(jugador_id):
            return False

        rol.jugadores[jugador_id] = arma
        return True

    # =================================================
    def cambiar_arma(self, jugador_id: int, nueva_arma: str) -> bool:
        rol = self.obtener_rol_jugador(jugador_id)
        if rol is None:
            return False

        rol.jugadores[jugador_id] = nueva_arma
        return True

    # =================================================
    def quitar_jugador(self, jugador_id: int) -> bool:
        encontrado = False

        for rol in self.roles.values():
            if jugador_id in rol.jugadores:
                del rol.jugadores[jugador_id]
                encontrado = True

        return encontrado

    # =================================================
    def total_jugadores(self) -> int:
        return sum(len(rol.jugadores) for rol in self.roles.values())

    # =================================================
    def puede_editar(self, user_id: int, role_ids=None) -> bool:
        if user_id == self.leader_id or user_id in self.sub_admins:
            return True
        return bool(set(role_ids or ()) & set(self.editor_role_ids))

    # =================================================
    def agregar_editor(self, user_id: int) -> bool:
        if user_id <= 0:
            return False
        if user_id == self.leader_id or user_id in self.sub_admins:
            return False
        self.sub_admins.append(user_id)
        return True

    def agregar_rol_editor(self, role_id: int) -> bool:
        if role_id <= 0 or role_id in self.editor_role_ids:
            return False
        self.editor_role_ids.append(role_id)
        return True

    # =================================================
    def marcar_entrega(self, user_id: int, entregado: bool) -> None:
        if user_id <= 0:
            return
        self.loot_entregado[user_id] = bool(entregado)

    # =================================================
    def plazas_totales(self) -> int:
        return sum(rol.cantidad for rol in self.roles.values())

    # =================================================
    def plazas_libres(self) -> int:
        return self.plazas_totales() - self.total_jugadores()
