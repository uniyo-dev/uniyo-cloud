from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import time

ROOT = Path("/sdcard/UNIYO/static/certificates")

ASSETS = {
    "icons": {
        "certificate.svg":
            "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/certificate.svg",
        "award.svg":
            "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/award.svg",
        "medal.svg":
            "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/medal.svg",
        "star.svg":
            "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/star.svg",
        "shield.svg":
            "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/shield-halved.svg",
    },

    "dividers": {
        "divider_fleuron.svg":
            "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/diamond.svg",
        "divider_star.svg":
            "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/star-of-life.svg",
    },

    "seals": {
        "seal_certificate.svg":
            "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/certificate.svg",
        "seal_award.svg":
            "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/award.svg",
    },

    "corners": {
        "corner_diamond.svg":
            "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/diamond.svg",
        "corner_sparkle.svg":
            "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/sparkles.svg",
    },
}


def download(url, destination, retries=3):
    headers = {
        "User-Agent": "UNIYO-Certificate-Asset-Downloader/1.0",
        "Accept": "image/svg+xml,text/plain,*/*",
    }

    for attempt in range(1, retries + 1):
        try:
            request = Request(url, headers=headers)

            with urlopen(request, timeout=30) as response:
                status = response.status
                data = response.read()

            if status != 200:
                raise RuntimeError(f"HTTP {status}")

            if not data:
                raise RuntimeError("empty response")

            # Prevent saving an HTML error page as an SVG
            beginning = data[:300].lower()
            if b"<html" in beginning or b"<!doctype" in beginning:
                raise RuntimeError("server returned HTML instead of an asset")

            destination.write_bytes(data)
            return True, f"downloaded ({len(data)} bytes)"

        except HTTPError as error:
            message = f"HTTP {error.code}"
            if error.code == 429:
                time.sleep(5 * attempt)
            else:
                time.sleep(2)

        except (URLError, TimeoutError, RuntimeError) as error:
            message = str(error)
            time.sleep(2)

        except Exception as error:
            message = str(error)
            time.sleep(2)

    return False, message


def main():
    success = 0
    skipped = 0
    failed = 0

    print("UNIYO safe certificate asset downloader")
    print(f"Target: {ROOT}")
    print("-" * 60)

    for category, files in ASSETS.items():
        directory = ROOT / category
        directory.mkdir(parents=True, exist_ok=True)

        print(f"\n[{category.upper()}]")

        for filename, url in files.items():
            destination = directory / filename

            if destination.exists() and destination.stat().st_size > 0:
                print(f"SKIP     {filename}")
                skipped += 1
                continue

            ok, message = download(url, destination)

            if ok:
                print(f"OK       {filename} - {message}")
                success += 1
            else:
                print(f"FAILED   {filename} - {message}")
                if destination.exists():
                    destination.unlink()
                failed += 1

    print("\n" + "-" * 60)
    print(f"Downloaded: {success}")
    print(f"Skipped:    {skipped}")
    print(f"Failed:     {failed}")

    if failed:
        print("\nSome remote assets failed.")
        print("Your locally generated ornaments are still usable.")
    else:
        print("\nAll remote assets downloaded successfully.")


if __name__ == "__main__":
    main()