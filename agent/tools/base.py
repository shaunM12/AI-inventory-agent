from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Tool:
    name: str
    definition: dict[str, Any]
    run: Callable[[dict[str, Any]], Any]
    inventory_display: bool = False
    inventory_mutation: bool = False
