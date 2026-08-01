from dataclasses import dataclass, field


@dataclass
class Perfil:

    user_id: int

    armas: list[str] = field(default_factory=list)

    ip: int = 0
