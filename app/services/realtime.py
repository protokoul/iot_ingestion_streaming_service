import asyncio
import json
import logging
from collections import defaultdict
from collections.abc import Iterable
from contextlib import suppress

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self._subscriptions: dict[str, set[WebSocket]] = defaultdict(set)
        self._expiry_tasks: dict[WebSocket, asyncio.Task] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, user_id: str, websocket: WebSocket, disconnect_at_epoch: int | None = None) -> None:
        await websocket.accept()
        async with self._lock:
            self._subscriptions[user_id].add(websocket)
        if disconnect_at_epoch is not None:
            self._expiry_tasks[websocket] = asyncio.create_task(self._disconnect_on_expiry(websocket, disconnect_at_epoch))

    async def register_ingest_socket(self, websocket: WebSocket, disconnect_at_epoch: int | None = None) -> None:
        await websocket.accept()
        if disconnect_at_epoch is not None:
            self._expiry_tasks[websocket] = asyncio.create_task(self._disconnect_on_expiry(websocket, disconnect_at_epoch))

    async def unsubscribe(self, websocket: WebSocket) -> None:
        async with self._lock:
            for user_id, sockets in list(self._subscriptions.items()):
                sockets.discard(websocket)
                if not sockets:
                    self._subscriptions.pop(user_id, None)
        task = self._expiry_tasks.pop(websocket, None)
        if task:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    async def broadcast(self, user_id: str, payload: dict) -> None:
        async with self._lock:
            sockets = list(self._subscriptions.get(user_id, set()))
        stale: list[WebSocket] = []
        for websocket in sockets:
            try:
                await websocket.send_json(payload)
            except Exception:
                stale.append(websocket)
        for websocket in stale:
            await self.unsubscribe(websocket)

    async def _disconnect_on_expiry(self, websocket: WebSocket, exp_epoch: int) -> None:
        now = int(asyncio.get_running_loop().time())
        # Convert wall-clock epoch to event-loop sleep approximately.
        import time
        delay = max(exp_epoch - int(time.time()), 0)
        await asyncio.sleep(delay)
        with suppress(Exception):
            await websocket.close(code=1008, reason="Token expired")
        await self.unsubscribe(websocket)


class RedisBroadcaster:
    def __init__(self, redis_client, channel_prefix: str, manager: ConnectionManager) -> None:
        self.redis = redis_client
        self.channel_prefix = channel_prefix
        self.manager = manager
        self._task: asyncio.Task | None = None

    async def publish(self, user_id: str, message: dict) -> None:
        channel = f"{self.channel_prefix}{user_id}"
        await self.redis.publish(channel, json.dumps(message))

    async def start(self) -> None:
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def _run(self) -> None:
        pubsub = self.redis.pubsub()
        pattern = f"{self.channel_prefix}*"
        await pubsub.psubscribe(pattern)
        logger.info("Redis subscriber listening on pattern %s", pattern)
        try:
            async for message in pubsub.listen():
                if message["type"] not in {"message", "pmessage"}:
                    continue
                data = json.loads(message["data"])
                user_id = data["data"]["user_id"]
                await self.manager.broadcast(user_id, data)
        finally:
            await pubsub.aclose()
