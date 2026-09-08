import os
import requests

# Set target directory paths matching your UNIYO structure
BASE_DIR = "/sdcard/UNIYO/static/certificates"
DIRS = {
    "borders": f"{BASE_DIR}/borders",
    "corners": f"{BASE_DIR}/corners",
    "dividers": f"{BASE_DIR}/dividers",
    "seals": f"{BASE_DIR}/seals",
    "ribbons": f"{BASE_DIR}/ribbons"
}

# Create folders if they don't exist
for folder in DIRS.values():
    os.makedirs(folder, exist_ok=True)

# Curated List of high-res, professional-grade certificate assets (transparent PNGs)
ASSET_URLS = {
    "borders": [
        # Double Thin Gold Luxury Frame Line
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Decorative_Border_-_Gold.svg/1024px-Decorative_Border_-_Gold.svg.png", "border_gold_luxury.png"),
        # Vintage Floral Frame (Classic Academic)
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Page_Border_-_Vintage_Floral_3.svg/1024px-Page_Border_-_Vintage_Floral_3.svg.png", "border_vintage_floral.png"),
        # Celtic Knot Frame (Exceptional detailed security style)
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Border_-_Celtic_Knot_Style_2.svg/1024px-Border_-_Celtic_Knot_Style_2.svg.png", "border_celtic_knot.png")
    ],
    "corners": [
        # Victorian Corner Swirl Ornament
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Victorian_Corner_Flourish.svg/1024px-Victorian_Corner_Flourish.svg.png", "corner_victorian_flourish.png"),
        # Baroque Corner Accent
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Decorative_Corner_-_Baroque.svg/1024px-Decorative_Corner_-_Baroque.svg.png", "corner_baroque.png"),
        # Ornate Renaissance Scroll
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Scroll_Corner_Design.svg/1024px-Scroll_Corner_Design.svg.png", "corner_renaissance.png")
    ],
    "dividers": [
        # Ornate Center Page Flourish
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Decorative_flourish_divider.svg/1024px-Decorative_flourish_divider.svg.png", "divider_floral_flourish.png"),
        # Gold Winged Royal Divider
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Fleuron_Divider_-_Gold.svg/1024px-Fleuron_Divider_-_Gold.svg.png", "divider_gold_fleuron.png")
    ],
    "seals": [
        # High-res Metallic Gold Starburst Seal
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Gold_seal.svg/1024px-Gold_seal.svg.png", "gold_foil_seal.png"),
        # Red Wax Seal Base
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Wax_seal.svg/1024px-Wax_seal.svg.png", "red_wax_seal.png")
    ],
    "ribbons": [
        # Official Red Ribbon Tail
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Red_ribbon_tails.svg/1024px-Red_ribbon_tails.svg.png", "red_ribbon_vector.png"),
        # Official Royal Blue Ribbon Tail
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Blue_ribbon_tails.svg/1024px-Blue_ribbon_tails.svg.png", "blue_ribbon_vector.png")
    ]
}

def download_file(url, filepath):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=15)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"   ✅ Saved: {os.path.basename(filepath)}")
        else:
            print(f"   ❌ HTTP Error {response.status_code} for {url}")
    except Exception as e:
        print(f"   ❌ Connection failed for {url}: {e}")

if __name__ == "__main__":
    print("⚜️ Starting UNIYO Luxury Certificate Asset Downloader...")
    for category, assets in ASSET_URLS.items():
        print(f"\n📂 Fetching Premium '{category.upper()}' Assets...")
        target_dir = DIRS[category]
        for url, filename in assets:
            dest_path = os.path.join(target_dir, filename)
            if not os.path.exists(dest_path):
                print(f" 📥 Downloading {filename}...")
                download_file(url, dest_path)
            else:
                print(f" ℹ️ Already exists: {filename}")
    print("\n👑 All requested high-res luxury design elements are now active!")