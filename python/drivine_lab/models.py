"""Optional Drivine object-manager models for the investigation graph.

Install with: pip install -e '.[drivine]'
"""

from __future__ import annotations

from typing import Annotated

try:
    from drivine import (
        GraphView,
        NodeFragment,
        NodeId,
        Relationship,
        Root,
    )
except ImportError as exc:  # pragma: no cover - optional extra
    raise ImportError(
        "drivine is not installed. Run: pip install -e '.[drivine]'"
    ) from exc


class Concept(NodeFragment, labels=["Concept"]):
    uuid: Annotated[str, NodeId()]
    title: str
    category: str
    summary: str
    detail: str


class DocChunk(NodeFragment, labels=["DocChunk"]):
    uuid: Annotated[str, NodeId()]
    topic: str
    instruction: str
    response: str


class ConceptBrief(GraphView):
    concept: Annotated[Concept, Root()]
    related: Annotated[list[Concept], Relationship("RELATES_TO")] = []
    examples: Annotated[list[DocChunk], Relationship("ILLUSTRATED_BY")] = []
