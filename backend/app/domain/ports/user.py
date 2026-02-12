from __future__ import annotations

import uuid
from typing import Protocol


class UserData(Protocol):
    id: uuid.UUID
    email: str
    password_hash: str


class UserPort(Protocol):
    async def get_by_email(self, email: str) -> UserData | None:
        ...

    async def create(self, email: str, password_hash: str) -> UserData:
        ...
