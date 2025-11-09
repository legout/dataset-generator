from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping, Optional


@dataclass(frozen=True)
class CatalogConfig:
    """Configuration for catalog metadata stores (sqlite or postgres)."""

    kind: str  # "sqlite" or "postgres"
    uri: str
    namespace: Optional[str] = None
    extras: Optional[Mapping[str, Any]] = None

    def as_dict(self) -> MutableMapping[str, Any]:
        data: MutableMapping[str, Any] = {"kind": self.kind, "uri": self.uri}
        if self.namespace is not None:
            data["namespace"] = self.namespace
        if self.extras:
            data.update(self.extras)
        return data
