"""Catálogo de armas mostrado por el bot.

Los valores guardados y las etiquetas se mantienen en español para que el
reping, la inscripción y las builds hablen el mismo idioma.
"""

from dataclasses import dataclass


TRADUCCIONES = {
    "Bear Paws": "Patas de oso", "Bloodletter": "Sangrador",
    "Deathgivers": "Concedemuertes", "Double Daggers": "Doble daga",
    "Claws": "Garras", "Whispering Bow": "Arco susurrante",
    "Longbow": "Arco largo", "Bow of Badon": "Arco de Badon",
    "Siegebow": "Arco de asedio", "Carving Sword": "Espada de talla",
    "Galatine Pair": "Par de Galatinas", "Bridled Fury": "Furia domada",
    "Realmbreaker": "Rompe reinos", "Spirit Hunter": "Cazador de espíritus",
    "Battle Bracers": "Brazales de batalla", "Spiked Gauntlets": "Guanteletes de púas",
    "Mace": "Maza", "Heavy Mace": "Maza pesada", "Incubus Mace": "Maza Íncubo",
    "Morning Star": "Estrella de la mañana", "Camlann Mace": "Maza de Camlann",
    "Great Hammer": "Gran martillo", "Polehammer": "Martillo largo",
    "Hammer": "Martillo de una mano", "Grovekeeper": "Guarda bosques",
    "Hand of Justice": "Mano de la justicia", "Grailseeker": "Busca grial",
    "Double Bladed Staff": "Bastón de doble hoja", "Staff of Balance": "Bastón de equilibrio",
    "Holy Staff": "Bastón sagrado", "Great Holy Staff": "Gran bastón sagrado",
    "Lifetouch Staff": "Bastón de toque de vida", "Fallen Staff": "Bastón caído",
    "Redemption Staff": "Bastón de redención", "Hallowfall": "Hallowfall",
    "Nature Staff": "Bastón de naturaleza", "Blight Staff": "Bastón de la plaga",
    "Rampant Staff": "Bastón rampante", "Ironroot Staff": "Bastón enraizado",
    "Forgebark Staff": "Forja corteza", "Arcane Staff": "Bastón arcano",
    "Great Arcane Staff": "Gran bastón arcano", "Enigmatic Staff": "Bastón enigmático",
    "Occult Staff": "Bastón oculto", "Malevolent Locus": "Locus malévolo",
    "Frost Staff": "Bastón de escarcha", "Great Frost Staff": "Gran bastón de escarcha",
    "Icicle Staff": "Carámbanos", "Permafrost Prism": "Prisma de permafrost",
    "Cursed Staff": "Bastón maldito", "Lifecurse Staff": "Maldición de vida",
    "Damnation Staff": "Bastón de condenación", "Shadowcaller": "Invocador oscuro",
    "Fire Staff": "Bastón de fuego", "Blazing Staff": "Bastón flamígero",
    "Dawnsong": "Canción del alba", "Lightcaller": "Invocador de luz",
    "Primal Staff": "Bastón primigenio", "Weeping Repeater": "Repetidora de desconsuelo",
    "Mistpiercer": "Perfora nieblas", "Badon": "Badon",
}


FAMILIAS = {
    "Espadas": ["Espada ancha", "Claymore", "Espadas dobles", "Hoja Clarent", "Espada de talla", "Par de Galatinas", "Hacedor de reyes", "Hoja infinita"],
    "Hachas": ["Hacha de batalla", "Gran hacha", "Alabarda", "Invocacuervos", "Guadaña infernal", "Patas de oso", "Rompe reinos", "Segadora de cristal"],
    "Mazas": ["Maza", "Maza pesada", "Estrella de la mañana", "Maza de lecho", "Maza Íncubo", "Maza de Camlann", "Guardianes del juramento", "Monarca de tormenta"],
    "Martillos": ["Martillo de una mano", "Martillo largo", "Gran martillo", "Martillo de tumba", "Martillos de forja", "Guarda bosques", "Mano de la justicia", "Martillo de rayo verdadero"],
    "Guantes de guerra": ["Guantes de luchador", "Brazales de batalla", "Guanteletes de púas", "Mutiladores ursinos", "Manos infernales", "Cestos de golpe de cuervo", "Puños de Avalon", "Brazales de pulso de fuerza"],
    "Ballestas": ["Ballesta", "Ballesta pesada", "Ballesta ligera", "Repetidora de desconsuelo", "Lanzavirotes", "Arco de asedio", "Modelador de energía", "Explosores arcoluz"],
    "Arcos": ["Arco", "Arco de guerra", "Arco largo", "Arco susurrante", "Arco de lamentos", "Arco de Badon", "Perfora nieblas", "Arco caminacielos"],
    "Dagas": ["Daga", "Doble daga", "Garras", "Sangrador", "Colmillo demoníaco", "Concedemuertes", "Furia domada", "Asesinos gemelos"],
    "Lanzas": ["Lanza", "Pica", "Guja", "Lanza de garza", "Cazador de espíritus", "Lanza de trinidad", "Rompealbas", "Guja de grieta"],
    "Bastones de combate": ["Bastón de combate", "Bastón acorazado", "Bastón de doble hoja", "Bastón de monje negro", "Guadaña de alma", "Bastón de equilibrio", "Busca grial", "Hoja gemela fantasma"],
    "Bastones cambiaformas": ["Bastón merodeador", "Bastón enraizado", "Bastón primigenio", "Bastón luna de sangre", "Bastón infernal", "Runa terrestre", "Invocador de luz", "Bastón mirada fija"],
    "Bastones de naturaleza": ["Bastón de naturaleza", "Gran bastón de naturaleza", "Bastón salvaje", "Bastón druídico", "Bastón de la plaga", "Bastón rampante", "Bastón raíz de hierro", "Forja corteza"],
    "Bastones de fuego": ["Bastón de fuego", "Gran bastón de fuego", "Bastón infernal", "Bastón de fuego salvaje", "Bastón de azufre", "Bastón flamígero", "Canción del alba", "Bastón caminallamas"],
    "Bastones sagrados": ["Bastón sagrado", "Gran bastón sagrado", "Bastón divino", "Bastón toque de vida", "Bastón caído", "Bastón de redención", "Hallowfall", "Bastón exaltado"],
    "Bastones arcanos": ["Bastón arcano", "Gran bastón arcano", "Bastón enigmático", "Bastón de brujería", "Bastón oculto", "Locus malévolo", "Víspera", "Bastón astral"],
    "Bastones de escarcha": ["Bastón de escarcha", "Gran bastón de escarcha", "Bastón glacial", "Bastón de escarcha blanca", "Carámbanos", "Prisma de permafrost", "Aullido helado", "Bastón ártico"],
    "Bastones malditos": ["Bastón maldito", "Gran bastón maldito", "Bastón demoníaco", "Maldición de vida", "Cráneo maldito", "Bastón de condenación", "Invocador oscuro", "Invocador putrefacto"],
}


def _unir(*familias):
    return [arma for familia in familias for arma in FAMILIAS[familia]]


# Cada arma del catálogo está disponible en al menos un rol; las familias se
# repiten cuando un arma tiene un uso táctico válido en más de uno.
ARMAS_POR_ROL = {
    "Tank": _unir("Mazas", "Martillos"),
    "Healer": _unir("Bastones sagrados", "Bastones de naturaleza"),
    "Support": _unir("Bastones arcanos"),
    "Stopper": _unir("Mazas", "Martillos", "Bastones de combate", "Bastones de escarcha"),
    "Clapper": _unir("Espadas", "Hachas", "Guantes de guerra", "Ballestas"),
    "DPS": _unir("Espadas", "Hachas", "Guantes de guerra", "Ballestas", "Arcos", "Dagas", "Lanzas", "Bastones cambiaformas", "Bastones de fuego", "Bastones de escarcha", "Bastones malditos"),
    "Puller": _unir("Bastones de combate"),
    "Agarre": _unir("Bastones de combate", "Mazas"),
    "Pierce": _unir("Arcos", "Ballestas", "Lanzas"),
    "Prisma": _unir("Bastones de escarcha"),
}

ALIAS_ROLES = {
    "Tanque": "Tank", "Sanador": "Healer", "Sagrado": "Healer",
    "Naturaleza": "Healer", "Apoyo": "Support", "Perforador": "Pierce",
}


def mostrar_nombre_arma(nombre: str) -> str:
    if not nombre:
        return ""
    texto = nombre.strip()
    return TRADUCCIONES.get(texto, texto)


def obtener_armas_por_rol(rol: str, contenido: str | None = None) -> list[str]:
    rol_normalizado = ALIAS_ROLES.get((rol or "").strip(), (rol or "").strip())
    armas = ARMAS_POR_ROL.get(rol_normalizado)
    if armas:
        return list(armas)
    return list(ARMAS_POR_ROL["DPS"])


@dataclass
class Weapon:
    nombre: str
    categoria: str
    icono: str


WEAPONS = [Weapon(nombre, categoria, "⚔️") for categoria, armas in ARMAS_POR_ROL.items() for nombre in armas]
