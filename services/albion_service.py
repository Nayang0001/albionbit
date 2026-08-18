import asyncio
import aiohttp
import logging

BASE = "https://gameinfo.albiononline.com/api/gameinfo"


class AlbionService:

    def __init__(self):
        self.logger = logging.getLogger("AlbionService")

    async def fetch_events(self, limit: int=50):
        url = f"{BASE}/events?limit={limit}"
        timeout = aiohttp.ClientTimeout(total=15)

        for attempt in range(3):
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url) as resp:
                        resp.raise_for_status()
                        return await resp.json()
            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                if attempt == 2:
                    self.logger.warning("No se pudieron obtener eventos de Albion: %s", exc)
                    return []
                await asyncio.sleep(2 * (attempt + 1))

    async def get_event(self, event_id: str):
        url = f"{BASE}/events/{event_id}"
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as resp:
                    resp.raise_for_status()
                    return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            self.logger.warning("No se pudo obtener el detalle del evento %s: %s", event_id, exc)
            return None
