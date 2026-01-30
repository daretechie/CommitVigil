from typing import Any

from arq import ArqRedis


class ApplicationState:
    """
    Typed Application State for CommitVigil.
    2026 Audit Remediation: Moves away from raw global dicts.
    """

    def __init__(self):
        self.redis: ArqRedis | None = None

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key, None)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


state = ApplicationState()
