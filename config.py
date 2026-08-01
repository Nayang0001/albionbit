from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = (
    os.environ.get("DISCORD_TOKEN")
    or os.environ.get("TOKEN")
    or ""
).strip()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", os.environ.get("OPENAI_API_KEY", "")).strip()
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
GROQ_API_URL = os.environ.get(
    "GROQ_API_URL",
    "https://api.groq.com/openai/v1/chat/completions",
).strip()
