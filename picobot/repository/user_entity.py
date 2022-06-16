from dataclasses import dataclass, field
from typing import Dict, Optional, Set, Union


@dataclass
class UserEntity:
    t_user: Dict[str, Union[str, int, bool]]
    state: str = field(default_factory=str)
    packs: Set[str] = field(default_factory=set)
    def_pack: Optional[str] = None
