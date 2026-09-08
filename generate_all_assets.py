import os
import math
from PIL import Image, ImageDraw

BASE_DIR = "/sdcard/UNIYO/static/certificates"
DIRS = {
    "borders": f"{BASE_DIR}/borders",
    "corners": f"{BASE_DIR}/corners",
    "dividers": f"{BASE_DIR}/dividers",
    "seals": f"{BASE_DIR}/seals",
    "ribbons": f"{BASE_DIR}/ribbons"
}

for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

# Common Palette
GOLD_MAIN = (197, 160, 89, 255)    # #C5A059
GOLD_LIGHT = (226, 180, 80, 255)   # #E2B450
GOLD_DARK = (154, 105, 20, 255)    # #9A6914
RED_DEEP = (185, 28, 28, 255)      # #B91C1C
RED_DARK = (127, 29, 29, 255)      # #7F1D1D
BLUE_ROYAL = (30, 58, 138, 255)    # #1E3A8A
BLUE_DARK = (15, 23, 42, 255)      # #0F172A

# ==============================================================================
# 1. SEALS (Gold Starburst & Red Wax)
# ==============================================================================
def make_gold_seal():
    size = 1200
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2

    # 120-point serrated starburst
    outer_r, inner_r, num_pts = 560, 500, 120
    pts = []
    for i in range(num_pts * 2):
        angle = i * (math.pi / num_pts)
        r = outer_r if i % 2 == 0 else inner_r
        pts.append((cx + int(r * math.cos(angle)), cy + int(r * math.sin(angle))))
    
    draw.polygon(pts, fill=GOLD_MAIN)
    # Concentric inner rings
    draw.ellipse([cx - 450, cy - 450, cx + 450, cy + 450], outline=GOLD_DARK, width=14)
    draw.ellipse([cx - 425, cy - 425, cx + 425, cy + 425], outline=GOLD_LIGHT, width=6)
    draw.ellipse([cx - 380, cy - 380, cx + 380, cy + 380], outline=GOLD_DARK, width=8)

    # Beaded ring
    for i in range(60):
        a = i * (math.pi / 30)
        bx = cx + int(402 * math.cos(a))
        by = cy + int(402 * math.sin(a))
        draw.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=GOLD_LIGHT)

    img.save(f"{DIRS['seals']}/gold_foil_seal.png", "PNG")
    print("  ✅ Created seals/gold_foil_seal.png")

def make_wax_seal():
    size = 1000
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2

    # Irregular organic wax edge
    pts = []
    for i in range(72):
        angle = i * (math.pi / 36)
        r = 440 + 25 * math.sin(i * 1.5) + 10 * math.cos(i * 3)
        pts.append((cx + int(r * math.cos(angle)), cy + int(r * math.sin(angle))))
    draw.polygon(pts, fill=RED_DEEP)
    draw.ellipse([cx - 360, cy - 360, cx + 360, cy + 360], outline=RED_DARK, width=20)
    draw.ellipse([cx - 320, cy - 320, cx + 320, cy + 320], outline=RED_DEEP, width=10)

    img.save(f"{DIRS['seals']}/red_wax_seal.png", "PNG")
    print("  ✅ Created seals/red_wax_seal.png")

# ==============================================================================
# 2. CORNER ORNAMENTS (Victorian Filigree & Baroque)
# ==============================================================================
def make_corner_flourish(filename, style="victorian"):
    size = 600
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Frame lines
    draw.line([(30, 30), (30, 450)], fill=GOLD_MAIN, width=10)
    draw.line([(30, 30), (450, 30)], fill=GOLD_MAIN, width=10)
    draw.line([(55, 55), (55, 380)], fill=GOLD_LIGHT, width=5)
    draw.line([(55, 55), (380, 55)], fill=GOLD_LIGHT, width=5)

    # Spiral filigree curves
    for r in range(40, 240, 20):
        box = [30, 30, 30 + r * 2, 30 + r * 2]
        draw.arc(box, start=0, end=90, fill=GOLD_MAIN, width=6)

    # Diamond tips and decorative dots
    draw.polygon([(470, 30), (490, 20), (510, 30), (490, 40)], fill=GOLD_LIGHT)
    draw.polygon([(30, 470), (20, 490), (30, 510), (40, 490)], fill=GOLD_LIGHT)

    for offset in [(100, 100), (160, 160), (220, 220)]:
        draw.ellipse([offset[0]-8, offset[1]-8, offset[0]+8, offset[1]+8], fill=GOLD_DARK)

    img.save(f"{DIRS['corners']}/{filename}", "PNG")
    print(f"  ✅ Created corners/{filename}")

# ==============================================================================
# 3. DIVIDERS (Fleuron & Center Flourish)
# ==============================================================================
def make_divider(filename):
    w, h = 1600, 240
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = w // 2, h // 2

    # Horizontal tapered lines
    draw.line([(100, cy), (cx - 120, cy)], fill=GOLD_MAIN, width=6)
    draw.line([(cx + 120, cy), (w - 100, cy)], fill=GOLD_MAIN, width=6)
    draw.line([(250, cy - 10), (cx - 140, cy - 10)], fill=GOLD_LIGHT, width=3)
    draw.line([(cx + 140, cy - 10), (w - 250, cy - 10)], fill=GOLD_LIGHT, width=3)

    # Center diamond flourish
    draw.polygon([(cx, cy - 45), (cx + 50, cy), (cx, cy + 45), (cx - 50, cy)], fill=GOLD_MAIN)
    draw.polygon([(cx, cy - 25), (cx + 28, cy), (cx, cy + 25), (cx - 28, cy)], fill=GOLD_LIGHT)

    # Satellite dots & scrolls
    for sign in [-1, 1]:
        draw.ellipse([cx + sign * 75 - 10, cy - 10, cx + sign * 75 + 10, cy + 10], fill=GOLD_DARK)
        draw.ellipse([cx + sign * 105 - 6, cy - 6, cx + sign * 105 + 6, cy + 6], fill=GOLD_LIGHT)
        draw.ellipse([cx + sign * (w // 2 - 100) - 8, cy - 8, cx + sign * (w // 2 - 100) + 8, cy + 8], fill=GOLD_MAIN)

    img.save(f"{DIRS['dividers']}/{filename}", "PNG")
    print(f"  ✅ Created dividers/{filename}")

# ==============================================================================
# 4. RIBBONS (Dual Tail Red & Royal Blue)
# ==============================================================================
def make_ribbon(filename, main_color, dark_color):
    w, h = 600, 700
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Left ribbon tail with classic V-notch
    left_pts = [(180, 20), (280, 20), (220, 600), (140, 500), (80, 600)]
    draw.polygon(left_pts, fill=main_color)
    draw.line([(180, 20), (80, 600)], fill=dark_color, width=4)

    # Right ribbon tail with classic V-notch
    right_pts = [(320, 20), (420, 20), (520, 600), (460, 500), (380, 600)]
    draw.polygon(right_pts, fill=main_color)
    draw.line([(420, 20), (520, 600)], fill=dark_color, width=4)

    # Fold shadow
    draw.polygon([(260, 20), (340, 20), (300, 100)], fill=dark_color)

    img.save(f"{DIRS['ribbons']}/{filename}", "PNG")
    print(f"  ✅ Created ribbons/{filename}")

# ==============================================================================
# 5. BORDERS (Vintage Academic Frame)
# ==============================================================================
def make_border_frame(filename):
    w, h = 1920, 1080
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Outer border
    draw.rectangle([50, 50, w - 50, h - 50], outline=GOLD_MAIN, width=12)
    # Inner border
    draw.rectangle([80, 80, w - 80, h - 80], outline=GOLD_LIGHT, width=5)
    # Fine hairline
    draw.rectangle([105, 105, w - 105, h - 105], outline=GOLD_DARK, width=3)

    # Corner blocks
    corner_sz = 140
    for cx, cy in [(50, 50), (w - 50 - corner_sz, 50), 
                   (50, h - 50 - corner_sz), (w - 50 - corner_sz, h - 50 - corner_sz)]:
        draw.rectangle([cx, cy, cx + corner_sz, cy + corner_sz], outline=GOLD_MAIN, width=6)
        draw.ellipse([cx + 20, cy + 20, cx + corner_sz - 20, cy + corner_sz - 20], outline=GOLD_LIGHT, width=4)

    img.save(f"{DIRS['borders']}/{filename}", "PNG")
    print(f"  ✅ Created borders/{filename}")

# ==============================================================================
# EXECUTION
# ==============================================================================
if __name__ == "__main__":
    print("⚜️ Generating Local Ultra-HD Transparent Certificate Assets...\n")
    make_gold_seal()
    make_wax_seal()
    make_corner_flourish("corner_victorian_flourish.png")
    make_corner_flourish("corner_baroque.png")
    make_corner_flourish("corner_renaissance.png")
    make_divider("divider_floral_flourish.png")
    make_divider("divider_gold_fleuron.png")
    make_ribbon("red_ribbon_vector.png", RED_DEEP, RED_DARK)
    make_ribbon("blue_ribbon_vector.png", BLUE_ROYAL, BLUE_DARK)
    make_border_frame("border_gold_luxury.png")
    make_border_frame("border_vintage_floral.png")
    make_border_frame("border_celtic_knot.png")
    print("\n👑 All certificate assets have been generated in /sdcard/UNIYO/static/certificates/!")