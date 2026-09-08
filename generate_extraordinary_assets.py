import os
import math
from PIL import Image, ImageDraw

BASE_DIR = "/sdcard/UNIYO/static/certificates"
DIRS = {
    "borders": f"{BASE_DIR}/borders",
    "corners": f"{BASE_DIR}/corners",
    "dividers": f"{BASE_DIR}/dividers",
}

for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

GOLD_MAIN = (197, 160, 89, 255)    # #C5A059
GOLD_LIGHT = (226, 180, 80, 255)   # #E2B450
GOLD_DARK = (154, 105, 20, 255)    # #9A6914

# ==============================================================================
# 1. EXTRAORDINARY ORNATE CORNERS (Baroque Scrolls & Filigree Labyrinths)
# ==============================================================================
def make_ornate_corner(filename, style="baroque"):
    size = 700
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if style == "baroque":
        # Multi-layered ornate scrollwork
        for i in range(5):
            offset = i * 18
            draw.arc([40 + offset, 40 + offset, 500 - offset, 500 - offset], start=180, end=270, fill=GOLD_MAIN, width=8 - i)
        
        # Leaf and scroll flourishes
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x = 250 + int(180 * math.cos(rad))
            y = 250 + int(180 * math.sin(rad))
            draw.ellipse([x-12, y-12, x+12, y+12], fill=GOLD_LIGHT, outline=GOLD_DARK, width=2)

        # Inner anchor rosette
        draw.ellipse([120, 120, 220, 220], outline=GOLD_MAIN, width=6)
        draw.ellipse([150, 150, 190, 190], fill=GOLD_DARK)

    elif style == "renaissance_scroll":
        # Sweeping ribbon scrolls
        for r in range(80, 450, 35):
            draw.arc([50, 50, r, r], start=0, end=180, fill=GOLD_LIGHT, width=6)
            draw.arc([50, 50, r, r], start=90, end=270, fill=GOLD_DARK, width=4)

        # Diamond cluster at vertex
        draw.polygon([(50, 50), (90, 30), (130, 50), (90, 70)], fill=GOLD_MAIN)
        draw.polygon([(50, 50), (30, 90), (50, 130), (70, 90)], fill=GOLD_MAIN)

    img.save(f"{DIRS['corners']}/{filename}", "PNG")
    print(f"  ✨ Created extraordinary corner: {filename}")

# ==============================================================================
# 2. ROYALTY-GRADE BORDERS & FRAMES (Guilloché Rope & Imperial Filigree)
# ==============================================================================
def make_imperial_border(filename, style="imperial"):
    w, h = 1920, 1080
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if style == "imperial":
        # Triple classic frame with guilloche offset
        draw.rectangle([40, 40, w - 40, h - 40], outline=GOLD_DARK, width=8)
        draw.rectangle([55, 55, w - 55, h - 55], outline=GOLD_MAIN, width=14)
        draw.rectangle([75, 75, w - 75, h - 75], outline=GOLD_LIGHT, width=4)
        draw.rectangle([95, 95, w - 95, h - 95], outline=GOLD_DARK, width=2)

        # Midpoint crest diamonds on all 4 sides
        mid_w, mid_h = w // 2, h // 2
        d_sz = 30
        # Top crest
        draw.polygon([(mid_w, 25), (mid_w + d_sz, 55), (mid_w, 85), (mid_w - d_sz, 55)], fill=GOLD_LIGHT, outline=GOLD_DARK, width=3)
        # Bottom crest
        draw.polygon([(mid_w, h - 25), (mid_w + d_sz, h - 55), (mid_w, h - 85), (mid_w - d_sz, h - 55)], fill=GOLD_LIGHT, outline=GOLD_DARK, width=3)
        # Left crest
        draw.polygon([(25, mid_h), (55, mid_h + d_sz), (85, mid_h), (55, mid_h - d_sz)], fill=GOLD_LIGHT, outline=GOLD_DARK, width=3)
        # Right crest
        draw.polygon([(w - 25, mid_h), (w - 55, mid_h + d_sz), (w - 85, mid_h), (w - 55, mid_h - d_sz)], fill=GOLD_LIGHT, outline=GOLD_DARK, width=3)

    elif style == "rope_filigree":
        # Braided rope style border
        draw.rectangle([50, 50, w - 50, h - 50], outline=GOLD_MAIN, width=18)
        # Inner dashed shadow line for 3D depth effect
        for i in range(120, w - 120, 30):
            draw.line([(i, 70), (i + 15, 70)], fill=GOLD_DARK, width=6)
            draw.line([(i, h - 70), (i + 15, h - 70)], fill=GOLD_DARK, width=6)
        for j in range(120, h - 120, 30):
            draw.line([(70, j), (70, j + 15)], fill=GOLD_DARK, width=6)
            draw.line([(w - 70, j), (w - 70, j + 15)], fill=GOLD_DARK, width=6)

    img.save(f"{DIRS['borders']}/{filename}", "PNG")
    print(f"  ✨ Created imperial border: {filename}")

# ==============================================================================
# 3. LUXURY DIVIDERS (Baroque Winged Fleurons)
# ==============================================================================
def make_royal_divider(filename):
    w, h = 1600, 300
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = w // 2, h // 2

    # Ornate curved wings
    for x_dir in [-1, 1]:
        start_x = cx + x_dir * 60
        for i in range(5):
            end_x = start_x + x_dir * (120 + i * 35)
            draw.arc([min(start_x, end_x), cy - 40 - i*10, max(start_x, end_x), cy + 40 + i*10], 
                     start=0 if x_dir == 1 else 180, end=180 if x_dir == 1 else 360, 
                     fill=GOLD_MAIN if i % 2 == 0 else GOLD_LIGHT, width=5 - i//2)

    # Center royal crest gem
    draw.ellipse([cx - 45, cy - 45, cx + 45, cy + 45], fill=GOLD_DARK, outline=GOLD_LIGHT, width=5)
    draw.ellipse([cx - 25, cy - 25, cx + 25, cy + 25], fill=GOLD_MAIN)
    draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=GOLD_LIGHT)

    img.save(f"{DIRS['dividers']}/{filename}", "PNG")
    print(f"  ✨ Created royal divider: {filename}")

# ==============================================================================
# EXECUTION
# ==============================================================================
if __name__ == "__main__":
    print("👑 Generating Extraordinary & Unique Luxury Assets...\n")
    make_ornate_corner("corner_baroque_imperial.png", "baroque")
    make_ornate_corner("corner_renaissance_scroll.png", "renaissance_scroll")
    make_imperial_border("border_imperial_crest.png", "imperial")
    make_imperial_border("border_rope_filigree.png", "rope_filigree")
    make_royal_divider("divider_royal_crested.png")
    print("\n🚀 All extraordinary assets are successfully generated and saved!")