"""
MARK Lineage Tracker — Stub
Records the provenance chain for every golden record:
which sources contributed, which rules applied, what changed and when.
Full implementation: see mark/docs/lineage-architecture.md
"""
from __future__ import annotations
from datetime import datetime
from typing import Any


class LineageEvent:
    def __init__(self, record_id: str, action: str, detail: dict[str, Any]) -> None:
        self.record_id = record_id
        self.action = action
        self.detail = detail
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "action": self.action,
            "detail": self.detail,
            "timestamp": self.timestamp,
        }


class LineageTracker:
    """In-memory lineage log — replace with persistent store in production."""

    def __init__(self) -> None:
        self._log: list[LineageEvent] = []

    def record(self, record_id: str, action: str, detail: dict[str, Any]) -> None:
        self._log.append(LineageEvent(record_id, action, detail))

    def history(self, record_id: str) -> list[dict[str, Any]]:
        return [e.to_dict() for e in self._log if e.record_id == record_id]

    def full_log(self) -> list[dict[str, Any]]:
        return [e.to_dict() for e in self._log]
