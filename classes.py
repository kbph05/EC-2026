from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(eq=False)
class Node:
    name: str
    elevation: float
    enabled: bool
    edges: list[Edge] = field(default_factory=list)

@dataclass(eq=False)
class Edge:
    name: str
    weight: float
    src: Node
    dst: Node
