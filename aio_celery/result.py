from __future__ import annotations

import asyncio
import json
import time
from typing import TYPE_CHECKING, Any, Dict, cast

from .exceptions import TimeoutError

if TYPE_CHECKING:
    from .app import Celery


class AsyncResult:
    def __init__(
        self,
        id: str,  # noqa: A002
        *,
        app: Celery,
    ) -> None:
        self.id = id
        self._cache = None
        self.app = app

    def __repr__(self) -> str:
        return f"<{type(self).__name__}: {self.id}>"

    async def _get_task_meta(self) -> dict[str, Any]:
        if self.app.result_backend is None:
            msg = "No result backend is configured."
            raise RuntimeError(msg)
        if self._cache is None:
            value = await self.app.result_backend.get(f"celery-task-meta-{self.id}")
            if value is None:
                return {"result": None, "status": "PENDING"}
            self._cache = json.loads(value)
        return cast(Dict[str, Any], self._cache)

    @property
    async def meta(self) -> Dict[str, Any]:
        return (await self._get_task_meta())

    @property
    async def result(self) -> Any:
        return (await self._get_task_meta())["result"]

    @property
    async def state(self) -> str:
        return str((await self._get_task_meta())["status"])


    @property
    async def data(self) -> str:
        return (await self._get_task_meta())["data"]

    async def get(self, timeout: float | None = None, interval: float = 0.5) -> Any:
        """Wait until task is ready, and return its result."""
        value = await self._get_task_meta()
        start = time.monotonic()
        while value == {"result": None, "status": "PENDING"}:
            await asyncio.sleep(interval)
            if timeout is not None and (time.monotonic() - start) > timeout:
                msg = "The operation timed out."
                raise TimeoutError(msg)
            value = await self._get_task_meta()
        return value["result"]

    async def revoke(self):
        return await self.app.cancel_task(self.id)




