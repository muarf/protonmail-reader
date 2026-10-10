import json
import os
from pathlib import Path


class State:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                with self.path.open("r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {"forwarded_ids": []}
        return {"forwarded_ids": []}

    @property
    def forwarded_ids(self) -> set[str]:
        ids = self._data.get("forwarded_ids", [])
        if not isinstance(ids, list):
            ids = []
        return set(str(x) for x in ids)

    def add(self, conv_id: str) -> None:
        ids = list(self.forwarded_ids)
        if conv_id not in ids:
            ids.append(conv_id)
        # keep a reasonable cap to avoid unbounded growth
        if len(ids) > 5000:
            ids = ids[-5000:]
        self._data["forwarded_ids"] = ids
        self._save()

    def _save(self) -> None:
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)
        tmp.replace(self.path)
