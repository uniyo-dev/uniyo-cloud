import os
import requests
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# ==============================================================================
# CONFIGURATION & DIRECTORY SETUP
# ==============================================================================
BASE_DIR = Path("/sdcard/UNIYO/static/certificates")
CATEGORIES = ["borders", "corners", "dividers", "seals", "ribbons", "icons", "medals"]

# Create directory structure
for cat in CATEGORIES:
    (BASE_DIR / cat).mkdir(parents=True, exist_ok=True)

# Browser-like headers to avoid being blocked by servers (Wikimedia/GitHub)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'
}

# ==============================================================================
# ASSET DATABASE (High-Quality Curated URLs)
# ==============================================================================
# Note: Using direct raw URLs from stable GitHub repos and Wikimedia direct file paths
ASSETS = {
    "borders": [
        ("https://raw.githubusercontent.com/Anisul-Islam/Academic-Certificate-Template/master/images/border.png", "border_academic_classic.png"),
        ("https://pixabay.com/get/g948386b896f6e5e8020610f7be6256f08170c0c09033320c7490082f45c911d735f4900d72045958276f7f2f65f0e74b_1280.png", "border_gold_lace.png"),
        ("https://upload.wikimedia.org/wikipedia/commons/d/d7/Decorative_Border_-_Gold.svg", "border_gold_vector.svg")
    ],
    "corners": [
        ("https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/clover.svg", "corner_clover_vector.svg"),
        ("https://www.transparentpng.com/download/gold/gold-corner-floral-design-png-6.png", "corner_gold_floral.png"),
        ("https://www.transparentpng.com/download/gold/gold-corner-element-png-15.png", "corner_luxury_scroll.png")
    ],
    "dividers": [
        ("https://raw.githubusercontent.com/google/material-design-icons/master/src/editor/format_line_spacing/any/24px.svg", "divider_minimal_line.svg"),
        ("https://www.transparentpng.com/download/gold/gold-divider-transparent-images-12.png", "divider_gold_royal.png"),
        ("https://www.transparentpng.com/download/floral/floral-divider-png-21.png", "divider_vintage_floral.png")
    ],
    "seals": [
        ("https://raw.githubusercontent.com/Anisul-Islam/Academic-Certificate-Template/master/images/seal.png", "seal_academic_red.png"),
        ("https://www.transparentpng.com/download/gold/gold-seal-transparent-image-5.png", "seal_gold_luxury.png"),
        ("https://www.transparentpng.com/download/gold/gold-seal-png-8.png", "seal_premium_star.png")
    ],
    "ribbons": [
        ("https://www.transparentpng.com/download/ribbon/blue-ribbon-transparent-images-5.png", "ribbon_royal_blue.png"),
        ("https://www.transparentpng.com/download/ribbon/gold-ribbon-transparent-background-12.png", "ribbon_gold_victory.png"),
        ("https://www.transparentpng.com/download/ribbon/red-ribbon-transparent-background-15.png", "ribbon_standard_red.png")
    ],
    "medals": [
        ("https://www.transparentpng.com/download/medal/gold-medal-transparent-images-10.png", "medal_gold_first.png"),
        ("https://www.transparentpng.com/download/medal/silver-medal-transparent-images-12.png", "medal_silver_second.png"),
        ("https://www.transparentpng.com/download/medal/bronze-medal-transparent-images-15.png", "medal_bronze_third.png")
    ],
    "icons": [
        ("https://raw.githubusercontent.com/google/material-design-icons/master/src/social/school/any/24px.svg", "icon_graduation_cap.svg"),
        ("https://raw.githubusercontent.com/google/material-design-icons/master/src/action/verified/any/24px.svg", "icon_verified_badge.svg"),
        ("https://raw.githubusercontent.com/google/material-design-icons/master/src/action/stars/any/24px.svg", "icon_star_premium.svg")
    ]
}

# ==============================================================================
# DOWNLOAD LOGIC
# ==============================================================================

def download_asset(category, url, filename):
    """Downloads a single file to the specified category folder."""
    target_path = BASE_DIR / category / filename
    
    if target_path.exists():
        print(f"  [SKIPPED] {filename} already exists.")
        return

    try:
        response = requests.get(url, headers=HEADERS, stream=True, timeout=20)
        if response.status_code == 200:
            with open(target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"  [SUCCESS] Downloaded {filename}")
        else:
            print(f"  [FAILED] HTTP {response.status_code} for {filename}")
    except Exception as e:
        print(f"  [ERROR] {filename}: {e}")

def main():
    print("⚜️ UNIYO - Ultimate Luxury Asset Downloader")
    print(f"📂 Target: {BASE_DIR}")
    print("-" * 50)

    # Flatten the download tasks for multithreading
    tasks = []
    for category, items in ASSETS.items():
        for url, filename in items:
            tasks.append((category, url, filename))

    # Download using 5 parallel threads for speed
    with ThreadPoolExecutor(max_workers=5) as executor:
        for task in tasks:
            executor.submit(download_asset, *task)

    print("-" * 50)
    print("✅ All extraordinary assets have been processed!")
    print(f"📍 Check your folders in: {BASE_DIR}")

if __name__ == "__main__":
    main()