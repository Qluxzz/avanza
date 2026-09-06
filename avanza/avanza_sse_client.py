import asyncio
import json
import logging
from avanza import Avanza
from curl_cffi.requests import AsyncSession

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AvanzaSSEClient:
    def __init__(self, avanza: Avanza, sse_url: str, impersonate: str = "firefox"):
        self.session_cookie = avanza._session.cookies.get_dict()
        self.sse_url = sse_url
        self.running = False
        self.listeners = []
        self.last_event = None
        self.last_event_data = None
        self.last_event_id = None
        self.reconnect_delay = 5.0
        self.impersonate = impersonate

    def add_listener(self, callback):
        """Register async callback(id, event, data)."""
        self.listeners.append(callback)

    async def _emit(self, id, event, data):
        for cb in self.listeners:
            try:
                await cb(id, event, data)
            except Exception as e:
                LOGGER.exception("Listener error: %s", e)

    async def _listen(self):
        async with AsyncSession(impersonate=self.impersonate) as session:
            async with session.stream(
                "GET",
                self.sse_url,
                cookies=self.session_cookie,
            ) as resp:
                LOGGER.info("Connected to SSE stream: %s", self.sse_url)
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    # Decode and clean
                    text = line.decode("utf-8") if isinstance(line, bytes) else line
                    text = text.strip()
                    if not text:
                        continue
                    # Parse SSE fields
                    if text.startswith("event:"):
                        self.last_event = text.split(":", 1)[1].strip()
                        LOGGER.debug("Received event: %s", self.last_event)
                    elif text.startswith("data:"):
                        raw = text[len("data:") :].strip()
                        try:
                            self.last_event_data = json.loads(raw)
                        except json.JSONDecodeError:
                            self.last_event_data = raw
                        LOGGER.debug("Received event data: %s", self.last_event_data)
                    elif text.startswith("id:"):
                        self.last_event_id = text.split(":", 1)[1].strip()
                        LOGGER.debug("Received event ID: %s", self.last_event_id)
                    # Only emit when all the event, data, and id are ready
                    if self.last_event and self.last_event_id and self.last_event_data:
                        await self._emit(
                            self.last_event_id, self.last_event, self.last_event_data
                        )
                        self.last_event = None
                        self.last_event_id = None
                        self.last_event_data = None

    async def start(self):
        if self.running:
            return
        self.running = True
        while self.running:
            try:
                await self._listen()
            except asyncio.CancelledError:
                break
            except Exception as e:
                LOGGER.warning(
                    "SSE connection lost: %s, reconnecting in %.1fs",
                    e,
                    self.reconnect_delay,
                )
                await asyncio.sleep(self.reconnect_delay)

    async def stop(self):
        self.running = False
