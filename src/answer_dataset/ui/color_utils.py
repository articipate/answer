"""Extract dominant color from logo."""

from pathlib import Path
from typing import Tuple
import sys
from collections import Counter

try:
    from PIL import Image
    HAS_PIL = True
except Exception:
    HAS_PIL = False


def get_logo_path():
    candidates = [
        Path(__file__).parent.parent.parent.parent / "logos" / "Answer_Logo.png",
        Path(__file__).parent / "resources" / "Answer_Logo.png",
        Path.cwd() / "logos" / "Answer_Logo.png",
        Path.cwd() / "Answer_Logo.png",
    ]
    if getattr(sys, 'frozen', False):
        candidates.append(Path(sys.executable).parent / "logos" / "Answer_Logo.png")
        candidates.append(Path(sys.executable).parent / "Answer_Logo.png")
    for p in candidates:
        if p.exists():
            return p
    return None


def get_dominant_color() -> Tuple[int, int, int]:
    if not HAS_PIL:
        return (13, 110, 253)
    logo = get_logo_path()
    if not logo:
        return (13, 110, 253)
    try:
        img = Image.open(logo).convert("RGBA")
        img = img.resize((128, 128))
        pixels = []
        for pixel in img.getdata():
            r, g, b, a = pixel
            if a < 100:
                continue
            if r < 20 and g < 20 and b < 20:
                continue
            if r > 240 and g > 240 and b > 240:
                continue
            pixels.append((r, g, b))
        if not pixels:
            return (13, 110, 253)
        counter = Counter(pixels)
        r, g, b = counter.most_common(1)[0][0]
        return (r, g, b)
    except Exception:
        return (13, 110, 253)


def rgb_to_hex(r, g, b) -> str:
    return f"#{max(0,min(255,r)):02x}{max(0,min(255,g)):02x}{max(0,min(255,b)):02x}"


DOMINANT_COLOR = get_dominant_color()
BUTTON_COLOR = rgb_to_hex(*DOMINANT_COLOR)
BUTTON_HOVER = rgb_to_hex(max(0, DOMINANT_COLOR[0]-20), max(0, DOMINANT_COLOR[1]-20), max(0, DOMINANT_COLOR[2]-20))
BUTTON_PRESSED = rgb_to_hex(max(0, DOMINANT_COLOR[0]-40), max(0, DOMINANT_COLOR[1]-40), max(0, DOMINANT_COLOR[2]-40))
BUTTON_TEXT = "#ffffff"
