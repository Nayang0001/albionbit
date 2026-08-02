import re
import asyncio
import logging
import aiohttp
import ast
import json
import discord
from discord import app_commands
from discord.ext import commands

from cogs.afk import AFK_GUILD_ID
from config import GROQ_API_KEY, GROQ_MODEL, GROQ_API_URL

logger = logging.getLogger(__name__)


def _build_system_prompt() -> str:
    return (
        "Eres Rey, el asistente oficial de Albion Party Manager para Albion Online. "
        "Responde siempre en español, de forma breve, precisa y centrada en datos reales del juego. "
        "Cuando te pregunten por builds T4.2 de healer, tank o dps, responde con nombres reales de ítems del juego como Hallowfall, Scholar Robe, Scholar Hood, Scholar Sandals, Bear Paws, Hunter Jacket, Hunter Hood, Hunter Shoes, Incubus Mace, Stone Shield, Guardian Armor, Guardian Helmet y Guardian Boots. "
        "Ejemplo de respuesta para una build T4.2 de healer: 'Build T4.2 Healer: Hallowfall, Scholar Robe, Scholar Hood, Scholar Sandals, Healing Potions'. "
        "Ejemplo de respuesta para una build T4.2 de DPS: 'Build T4.2 DPS: Bear Paws, Hunter Jacket, Hunter Hood, Hunter Shoes, Poison Pots'. "
        "No inventes ítems, roles ni nombres. Si no tienes una referencia fiable, responde que no tienes datos concretos del juego en este momento. "
        "No digas que eres ChatGPT, OpenAI, Grok, Claude ni un modelo genérico; actúa solo como Rey. "
        "No des opiniones personales ni consejos fuera del juego. Usa frases cortas y listas cuando sea posible."
    )


SYSTEM_PROMPT = {
    "role": "system",
    "content": _build_system_prompt(),
}

MAX_HISTORY_MESSAGES = 12
# Configure límites para respuestas concisas y evitar cortes
MAX_TOKENS = 300
MAX_RESPONSE_CHARS = 800
DISCORD_MAX_MESSAGE_LENGTH = 2000

BUILD_RESPONSES = {
    "healer": (
        "Build T4.2 Healer\n"
        "Arma: Hallowfall\n"
        "Armadura: Scholar Robe\n"
        "Casco: Scholar Hood\n"
        "Botas: Scholar Sandals\n"
        "Accesorios: Healing Potions, Tier 4 food y runas de regeneración."
    ),
    "tank": (
        "Build T4.2 Tank\n"
        "Arma: Incubus Mace\n"
        "Escudo: Stone Shield\n"
        "Armadura: Guardian Armor\n"
        "Casco: Guardian Helmet\n"
        "Botas: Guardian Boots\n"
        "Accesorios: Defense Potions, comida de tanque y runas de resistencia."
    ),
    "dps": (
        "Build T4.2 DPS\n"
        "Arma: Bear Paws\n"
        "Armadura: Hunter Jacket\n"
        "Casco: Hunter Hood\n"
        "Botas: Hunter Shoes\n"
        "Accesorios: Poison Pots, Tier 4 food y runas de daño."
    ),
}


class ReyChat(commands.Cog):

    @staticmethod
    def _build_system_prompt() -> str:
        return _build_system_prompt()

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.conversations: dict[str, list[dict[str, str]]] = {}
        self.api_key = GROQ_API_KEY
        self.session = aiohttp.ClientSession() if self.api_key else None

    def cog_unload(self):
        if self.session is not None and not self.session.closed:
            asyncio.create_task(self.session.close())

    def _clean_prompt(self, content: str) -> str:
        prompt = re.sub(r"(?i)\brey\b", "", content).strip()
        return prompt or "Hola"

    def _sanitize_answer(self, text: str) -> str:
        if not text:
            return ""

        text = text.strip()
        text = re.sub(
            r"(?i)\b(?:soy|i am)\s+(?:chatgpt|gpt[- ]?\d|openai|grok|claude)\b[^.?!]*[.?!]?",
            "Soy Rey.",
            text,
        )
        text = re.sub(r"(?i)\b(?:chatgpt|gpt[- ]?\d|openai|grok|claude)\b", "", text)
        text = re.sub(r"\s{2,}", " ", text).strip()
        return text or "Soy Rey."

    def _get_build_response(self, prompt: str) -> str | None:
        lower = prompt.lower()
        if "build" not in lower and "constru" not in lower:
            return None
        if not any(token in lower for token in ("t4.2", "t4 2", "tier 4.2", "t4")):
            return None

        if "healer" in lower or "heal" in lower or "sanador" in lower:
            return BUILD_RESPONSES["healer"]
        if "tank" in lower or "tanque" in lower:
            return BUILD_RESPONSES["tank"]
        if "dps" in lower or "daño" in lower or "damage" in lower:
            return BUILD_RESPONSES["dps"]
        return None

    def _get_conversation(self, channel_id: int) -> list[dict[str, str]]:
        conversation = self.conversations.get(channel_id)
        if conversation is None:
            conversation = [SYSTEM_PROMPT]
            self.conversations[channel_id] = conversation
        return conversation

    def _trim_conversation(self, channel_id: int) -> None:
        conversation = self.conversations.get(channel_id)
        if conversation and len(conversation) > MAX_HISTORY_MESSAGES + 1:
            self.conversations[channel_id] = [conversation[0]] + conversation[-MAX_HISTORY_MESSAGES:]

    async def _generate_response(self, messages: list[dict[str, str]]) -> str:
        if not self.api_key:
            raise RuntimeError("Falta la clave de la API para Groq.")

        return await self._generate_groq_response(messages)

    def _get_groq_error_hint(self, exc: Exception) -> str:
        text = str(exc).lower()
        if "api key" in text or "unauthorized" in text or "401" in text or "forbidden" in text:
            return "La clave de Groq no está autorizada o no se cargó correctamente. Revisa la variable GROQ_API_KEY."
        if "quota" in text or "429" in text:
            return "Groq rechazó la solicitud por cuota o límite. Intenta de nuevo más tarde."
        if "model" in text and "not found" in text:
            return "El modelo de Groq no está disponible. Revisa GROQ_MODEL."
        if isinstance(exc, aiohttp.ClientConnectorError):
            return "No se pudo conectar a Groq. Revisa la conexión de red."
        if isinstance(exc, asyncio.TimeoutError):
            return "La conexión con Groq tardó demasiado. Intenta de nuevo más tarde."
        return "Hubo un error al comunicarse con Groq. Revisa la configuración y la red."

    async def _post_groq_request(self, url: str, payload: dict, headers: dict) -> dict:
        async with self.session.post(url, json=payload, headers=headers, timeout=60) as response:
            body = await response.text()
            if response.status != 200:
                raise RuntimeError(f"Groq API {response.status}: {body}")
            return await response.json()

    async def _generate_groq_response(self, messages: list[dict[str, str]]) -> str:
        if self.session is None:
            raise RuntimeError("Falta la sesión HTTP para Groq.")

        url = GROQ_API_URL.format(model=GROQ_MODEL)
        payload = {
            "model": GROQ_MODEL,
            "messages": messages,
            "max_tokens": MAX_TOKENS,
            "temperature": 0.8,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            data = await self._post_groq_request(url, payload, headers)
        except RuntimeError as exc:
            if "model_not_found" in str(exc).lower() and GROQ_MODEL != "openai/gpt-oss-20b":
                logger.warning(
                    "Modelo Groq no encontrado (%s). Reintentando con openai/gpt-oss-20b.",
                    GROQ_MODEL,
                )
                payload["model"] = "openai/gpt-oss-20b"
                data = await self._post_groq_request(url, payload, headers)
            else:
                raise

        answer = None
        if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
            choice = data["choices"][0]
            if isinstance(choice, dict):
                message = choice.get("message")
                if isinstance(message, dict):
                    answer = message.get("content") or message.get("text")
                if answer is None:
                    answer = choice.get("text")
        if not answer:
            answer = self._unwrap_api_repr(data)
        if not answer:
            raise RuntimeError("No se pudo extraer una respuesta de la API de Groq.")

        # Normalize and unwrap any API reprs (dicts, lists, or stringified dicts)
        answer = self._unwrap_api_repr(answer)
        return answer.strip()

    def _unwrap_api_repr(self, answer: object) -> str:
        """Try to extract a human-readable assistant content from various API shapes.

        Accepts dict, list, or string representations and returns a cleaned string.
        """
        EXCLUDE_KEYS = {
            "reasoning",
            "debug",
            "logprobs",
            "id",
            "object",
            "model",
            "created",
            "usage",
            "type",
            "index",
            "finish_reason",
        }

        def recursive_find_text(obj):
            """Recursively search for the first non-empty string value in obj.

            Prefer keys like 'content', 'text', 'message', 'output', 'result', 'reply'.
            Skip keys in EXCLUDE_KEYS.
            """
            if obj is None:
                return None

            if isinstance(obj, str):
                s = obj.strip()
                return s or None

            if isinstance(obj, dict):
                # First try preferred keys at this level
                for key in ("content", "text", "message", "output", "result", "reply", "response"):
                    if key in obj and key not in EXCLUDE_KEYS:
                        val = obj[key]
                        if isinstance(val, str) and val.strip():
                            return val.strip()
                        # If it's a list or dict, recurse
                        found = recursive_find_text(val)
                        if found:
                            return found

                # Then scan other items (but avoid excluded keys)
                for k, v in obj.items():
                    if k in EXCLUDE_KEYS:
                        continue
                    found = recursive_find_text(v)
                    if found:
                        return found
                return None

            if isinstance(obj, list):
                for item in obj:
                    found = recursive_find_text(item)
                    if found:
                        return found
                return None

            # Fallback to string conversion
            try:
                s = str(obj).strip()
                return s or None
            except Exception:
                return None

        # If it's already structured, try recursive extraction
        extracted = recursive_find_text(answer)
        if extracted:
            return str(extracted)

        # If it's a string that looks like a dict/list repr, try to parse and extract
        if isinstance(answer, str):
            s = answer.strip()
            if not s:
                return ""

            # Try JSON first
            try:
                obj = json.loads(s)
            except Exception:
                # Try literal_eval for python reprs
                try:
                    obj = ast.literal_eval(s)
                except Exception:
                    obj = None

            if obj is not None:
                extracted = recursive_find_text(obj)
                if extracted:
                    return str(extracted)

            # As last resort, remove obvious whitespace and truncate long strings
            short = re.sub(r"\s{2,}", " ", s)
            if len(short) > 1000:
                short = short[:1000] + "..."
            return short

        return ""

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        content = message.content or ""
        if "rey" not in content.lower():
            await self.bot.process_commands(message)
            return

        if not self.api_key:
            await message.channel.send(
                "🤖 La IA no está configurada: falta la clave de Groq."
            )
            await self.bot.process_commands(message)
            return

        if not content.strip():
            await message.channel.send(
                "⚠️ No pude leer el texto de tu mensaje. Activa el Message Content Intent en Discord Developer Portal o usa `/rey`."
            )
            await self.bot.process_commands(message)
            return

        if content.strip().lower() == "rey":
            await message.channel.send(
                "🤖 Hola, soy Rey. Escribe tu pregunta o mensaje después de 'rey' y te respondo."
            )
            await self.bot.process_commands(message)
            return

        prompt = self._clean_prompt(content)
        local_answer = self._get_build_response(prompt)
        if local_answer is not None:
            answer = local_answer
            conversation = self._get_conversation(message.channel.id)
        else:
            conversation = self._get_conversation(message.channel.id)
            conversation.append({"role": "user", "content": prompt})

            try:
                answer = await self._generate_response(conversation)
            except Exception as exc:
                logger.exception("Error al generar respuesta de IA")
                hint = self._get_groq_error_hint(exc)
                await message.channel.send(f"⚠️ {hint}")
                await self.bot.process_commands(message)
                return

        answer = self._sanitize_answer(answer)
        # Shorten answer to a concise, game-accurate form to avoid truncation
        answer = self._shorten_answer(answer)
        conversation.append({"role": "assistant", "content": answer})
        self._trim_conversation(message.channel.id)

        await self._send_long_message(message.channel, answer)
        await self.bot.process_commands(message)

    @app_commands.guilds(discord.Object(id=AFK_GUILD_ID))
    @app_commands.command(name="rey", description="Habla con Rey, el asistente del clan")
    @app_commands.describe(prompt="Escribe tu pregunta o mensaje para Rey")
    async def rey(self, interaction: discord.Interaction, prompt: str):
        if not self.api_key:
            await interaction.response.send_message(
                "🤖 La IA no está configurada: falta la clave de Groq.", ephemeral=True
            )
            return

        local_answer = self._get_build_response(prompt)
        if local_answer is not None:
            answer = local_answer
            conversation = self._get_conversation(interaction.channel.id)
        else:
            conversation = self._get_conversation(interaction.channel.id)
            conversation.append({"role": "user", "content": prompt})

            try:
                answer = await self._generate_response(conversation)
            except Exception as exc:
                logger.exception("Error al generar respuesta de IA para slash command")
                hint = self._get_groq_error_hint(exc)
                await interaction.response.send_message(f"⚠️ {hint}", ephemeral=True)
                return

        answer = self._sanitize_answer(answer)
        answer = self._shorten_answer(answer)
        conversation.append({"role": "assistant", "content": answer})
        self._trim_conversation(interaction.channel.id)
        await self._send_long_message(interaction, answer)

    def _shorten_answer(self, text: str) -> str:
        if not text:
            return ""
        text = text.strip()
        # Si ya es corto, devolver tal cual
        if len(text) <= MAX_RESPONSE_CHARS:
            return text

        # Preferir cortar por líneas o espacios para no romper palabras
        cutoff = MAX_RESPONSE_CHARS
        # buscar el último salto de línea antes del corte
        nl = text.rfind('\n', 0, cutoff)
        if nl != -1 and nl > int(cutoff * 0.5):
            cut = nl
        else:
            sp = text.rfind(' ', 0, cutoff)
            cut = sp if sp != -1 and sp > int(cutoff * 0.5) else cutoff

        short = text[:cut].rstrip()
        # Añadir indicación breve de que está resumido
        return f"{short}... (resumido)"

    async def _send_long_message(self, destination, content: str):
        chunks = self._split_message(content)

        # If single short chunk, try sending as embed for better formatting
        if len(chunks) == 1:
            sent = await self._try_send_as_embed(destination, chunks[0])
            if sent:
                return

        if isinstance(destination, discord.Interaction):
            await destination.response.send_message(chunks[0])
            for chunk in chunks[1:]:
                await destination.followup.send(chunk)
            return

        if isinstance(destination, discord.abc.Messageable):
            for chunk in chunks:
                await destination.send(chunk)
            return

        raise TypeError("Destino de mensaje no soportado para envíos largos")

    def _split_message(self, content: str) -> list[str]:
        if len(content) <= DISCORD_MAX_MESSAGE_LENGTH:
            return [content]

        chunks: list[str] = []
        current = []
        current_len = 0

        for line in content.splitlines(keepends=True):
            if len(line) > DISCORD_MAX_MESSAGE_LENGTH:
                while line:
                    part = line[:DISCORD_MAX_MESSAGE_LENGTH - current_len]
                    if not part:
                        part = line[:DISCORD_MAX_MESSAGE_LENGTH]
                    current.append(part)
                    chunks.append("".join(current))
                    current = []
                    current_len = 0
                    line = line[len(part):]
                continue

            if current_len + len(line) > DISCORD_MAX_MESSAGE_LENGTH:
                chunks.append("".join(current))
                current = [line]
                current_len = len(line)
            else:
                current.append(line)
                current_len += len(line)

        if current:
            chunks.append("".join(current))

        return chunks

    async def _try_send_as_embed(self, destination, content: str) -> bool:
        # Try to unwrap API-like reprs first
        try:
            content = self._unwrap_api_repr(content)
        except Exception:
            pass

        # Heurística: solo crear embed si el contenido parece realmente estructurado como build
        keywords = ("arma", "armadura", "rol", "build", "casco", "botas", "arma:")
        lower = content.lower()
        if not any(k in lower for k in keywords):
            return False

        # Extraer pares clave: valor por línea
        fields = []
        title = None
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            if title is None and (line.startswith("#") or line.lower().startswith("build") or line.endswith("—") or line.endswith("-")):
                title = line.strip('# ').strip()
                continue
            if ':' in line:
                parts = line.split(':', 1)
                key = parts[0].strip().strip('*\n ')
                value = parts[1].strip()
                if key and value:
                    fields.append((key, value))
            elif line.startswith('-') or line.startswith('*'):
                # fallback: bullet items -> add to description
                if len(fields) < 1:
                    fields.append(("Info", line.lstrip('-* ').strip()))

        if not fields:
            return False

        # Require a strong structure before using embed formatting
        if len(fields) < 3 and title is None:
            return False

        embed = discord.Embed(color=0x3498DB)
        embed.title = title or "Rey — Build"
        desc_lines = []
        for i, (k, v) in enumerate(fields[:10]):
            # Add as field when not too long
            try:
                embed.add_field(name=k, value=v, inline=True)
            except Exception:
                desc_lines.append(f"**{k}**: {v}")

        if len(fields) > 10:
            remaining = fields[10:]
            desc_lines.extend(f"**{k}**: {v}" for k, v in remaining)

        if desc_lines:
            embed.description = "\n".join(desc_lines)[:1000]

        try:
            if isinstance(destination, discord.Interaction):
                await destination.response.send_message(embed=embed)
                return True
            if isinstance(destination, discord.abc.Messageable):
                await destination.send(embed=embed)
                return True
        except Exception:
            return False

        return False


async def setup(bot: commands.Bot):
    await bot.add_cog(ReyChat(bot))
