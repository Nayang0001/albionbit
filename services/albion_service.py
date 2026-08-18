import asyncio
import aiohttp
import logging

# Servidores de Albion
SERVERS = {
    "europe": "https://gameinfo.albiononline.com/api/gameinfo",
    "americas": "https://gameinfo-ams.albiononline.com/api/gameinfo",
    "asia": "https://gameinfo-sgp.albiononline.com/api/gameinfo"
}

DEFAULT_SERVER = "europe"


class AlbionService:

    def __init__(self, server: str=DEFAULT_SERVER):
        self.logger = logging.getLogger("AlbionService")
        self.server = server.lower()
        if self.server not in SERVERS:
            self.logger.warning(f"Servidor '{server}' desconocido, usando 'europe'")
            self.server = "europe"
        self.base_url = SERVERS[self.server]
        self.logger.info(f"AlbionService inicializado para servidor: {self.server}")

    async def fetch_events(self, limit: int=50):
        url = f"{self.base_url}/events?limit={limit}"
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
        url = f"{self.base_url}/events/{event_id}"
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as resp:
                    resp.raise_for_status()
                    return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            self.logger.warning("No se pudo obtener el detalle del evento %s: %s", event_id, exc)
            return None
