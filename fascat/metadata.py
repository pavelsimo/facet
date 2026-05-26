from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Metadata = dict[str, object]
PmiKind = Literal[
    "dimension",
    "tolerance",
    "datum",
    "datum_target",
    "feature_control_frame",
    "note",
    "saved_view",
    "annotation_plane",
]


@dataclass(frozen=True)
class Tolerance:
    upper: float | None = None
    lower: float | None = None
    kind: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "upper": self.upper,
            "lower": self.lower,
            "kind": self.kind,
        }


@dataclass(frozen=True)
class PmiAnnotation:
    id: str
    kind: PmiKind
    text: str
    value: float | None = None
    unit: str | None = None
    tolerance: Tolerance | None = None
    applies_to: list[str] = field(default_factory=list)
    view: str | None = None
    plane: list[list[float]] | None = None
    source: Metadata = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "applies_to", list(self.applies_to))
        object.__setattr__(self, "source", dict(self.source))
        if self.plane is not None:
            object.__setattr__(self, "plane", [list(row) for row in self.plane])

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "id": self.id,
            "kind": self.kind,
            "type": self.kind,
            "text": self.text,
            "applies_to": list(self.applies_to),
            "appliesToPartIds": list(self.applies_to),
            "source": dict(self.source),
        }
        if self.value is not None:
            payload["value"] = self.value
        if self.unit is not None:
            payload["unit"] = self.unit
        if self.tolerance is not None:
            payload["tolerance"] = self.tolerance.to_dict()
        if self.view is not None:
            payload["view"] = self.view
        if self.plane is not None:
            payload["plane"] = [list(row) for row in self.plane]
        return payload
