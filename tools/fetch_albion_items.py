"""Descarga items.json formateado desde ao-bin-dumps y lo guarda en data/albion_items.json.

Uso:
    python tools/fetch_albion_items.py

El archivo resultante será usado por `services.albion_items.buscar_item_por_nombre`.
"""
from urllib.request import urlopen
from pathlib import Path
import shutil

URL = "https://raw.githubusercontent.com/ao-data/ao-bin-dumps/master/formatted/items.json"
OUT = Path("data/albion_items.json")
OUT.parent.mkdir(parents=True, exist_ok=True)

print("Descargando items.json desde ao-bin-dumps (puede pesar varios MB)...")
try:
    with urlopen(URL) as resp, OUT.open("wb") as out_f:
        shutil.copyfileobj(resp, out_f)
    print(f"Guardado en {OUT}")
except Exception as exc:
    print("Error al descargar:", exc)
    if OUT.exists():
        print("El archivo parcial fue guardado en", OUT)
    raise
