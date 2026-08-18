import aiohttp
import logging

BASE = "https://gameinfo.albiononline.com/api/gameinfo"


class AlbionService:

    def __init__(self):
        self.logger = logging.getLogger("AlbionService")

    async def fetch_events(self, limit: int=50):
        url = f"{BASE}/events?limit={limit}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=20) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def get_event(self, event_id: str):
        url = f"{BASE}/events/{event_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=20) as resp:
                resp.raise_for_status()
                return await resp.json()
