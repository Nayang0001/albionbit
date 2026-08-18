from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


def _load_font(size=18):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def render_kill_event(ev: dict, ev_type: str="kill", k_icons: list | None=None, v_icons: list | None=None, loot_icons: list | None=None) -> BytesIO:
    """Render a simple card-like image that resembles the example.

    Uses placeholder boxes for item icons and text from the event.
    Returns a BytesIO with PNG data.
    """
    width, height = 900, 680
    bg_color = (224, 200, 180)
    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # fonts
    title_font = _load_font(28)
    small_font = _load_font(16)
    mid_font = _load_font(20)

    # Title: killer vs victim
    killer = ev.get("Killer", {})
    victim = ev.get("Victim", {})
    k_name = killer.get("Name", "Desconocido")
    v_name = victim.get("Name", "Desconocido")

    title_text = f"{k_name}  —  {v_name}"
    draw.text((width // 2 - draw.textsize(title_text, font=title_font)[0] // 2, 18), title_text, fill=(60, 34, 20), font=title_font)

    # Left and right equipment grids (3x3)
    box_size = 84
    start_y = 70
    left_x = 40
    right_x = width - 40 - box_size * 3 - 16

    def draw_grid(x, y, items, icons=None):
        for r in range(3):
            for c in range(3):
                bx = x + c * (box_size + 8)
                by = y + r * (box_size + 8)
                draw.rectangle([bx, by, bx + box_size, by + box_size], fill=(200, 210, 220), outline=(120, 100, 80))
                # placeholder: if items list has an entry, draw its first letter
                idx = r * 3 + c
                if icons and idx < len(icons) and icons[idx] is not None:
                    try:
                        ic = icons[idx]
                        if isinstance(ic, Image.Image):
                            ic = ic.convert("RGBA")
                            ic = ic.resize((box_size - 8, box_size - 8), resample=Image.LANCZOS)
                            img.paste(ic, (bx + 4, by + 4), ic)
                            continue
                    except Exception:
                        pass
                if idx < len(items):
                    label = items[idx]
                    draw.text((bx + 8, by + 8), label[:12], fill=(20, 20, 20), font=small_font)

    # Extract simple item name lists from event participants (placeholders)
    k_items = []
    v_items = []
    # If event has participants with Equipment, try to fill
    for p in (killer.get("Items") or [])[:9]:
        k_items.append(str(p))
    for p in (victim.get("Items") or [])[:9]:
        v_items.append(str(p))

    draw_grid(left_x, start_y, k_items, icons=k_icons)
    draw_grid(right_x, start_y, v_items, icons=v_icons)

    # Central panel with fame, silver, killed badge and timestamp
    center_x = width // 2 - 120
    center_y = 140
    # Fame
    fame = ev.get("KillerFame") or ev.get("VictimFame") or ev.get("Fame") or 0
    silver = ev.get("Silver") or 0

    draw.text((center_x, center_y), f"Fama:\n{fame}", fill=(40, 30, 20), font=mid_font)
    draw.text((center_x + 120, center_y), f"Silver:\n{silver}", fill=(40, 30, 20), font=mid_font)

    # Killed badge
    badge_text = "KILLED" if ev_type == "kill" else "DEAD"
    bx = width // 2 - 60
    by = center_y + 80
    draw.ellipse([bx, by, bx + 120, by + 120], fill=(230, 210, 120), outline=(120, 90, 60))
    draw.text((bx + 22, by + 42), badge_text, fill=(80, 44, 20), font=mid_font)

    # Timestamp
    ts = ev.get("TimeStamp") or ev.get("Timestamp") or ev.get("TimeStampUtc") or ev.get("Time") or ""
    draw.text((width // 2 - 140, height - 80), str(ts), fill=(60, 40, 20), font=small_font)

    # Bottom row: loot placeholders
    loot = ev.get("Loot") or []
    loot_x = 40
    loot_y = height - 160
    for i in range(10):
        bx = loot_x + i * (box_size // 1)
        draw.rectangle([bx, loot_y, bx + 56, loot_y + 56], fill=(210, 220, 230), outline=(120, 100, 80))
        if loot_icons and i < len(loot_icons) and loot_icons[i] is not None:
            try:
                ic = loot_icons[i]
                if isinstance(ic, Image.Image):
                    ic = ic.convert("RGBA")
                    ic = ic.resize((52, 52), resample=Image.LANCZOS)
                    img.paste(ic, (bx + 2, loot_y + 2), ic)
                    continue
            except Exception:
                pass
        if i < len(loot):
            draw.text((bx + 6, loot_y + 6), str(loot[i])[:10], fill=(10, 10, 10), font=small_font)

    out = BytesIO()
    img.save(out, format="PNG")
    out.seek(0)
    return out
