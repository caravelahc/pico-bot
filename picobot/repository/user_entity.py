from dataclasses import dataclass, field
from typing import Optional, Union


@dataclass
class UserEntity:
    t_user: dict[str, Union[str, int, bool]]
    state: str = field(default_factory=str)
    packs: set[str] = field(default_factory=set[str])
    def_pack: Optional[str] = None
