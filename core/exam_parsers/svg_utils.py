"""
UNIYO LMS - SVG to Image Conversion
Converts inline SVG from exam HTML to images for ReportLab PDF
"""

from io import BytesIO
from typing import Optional
import base64

try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False
    print("⚠ cairosvg not available - SVG rendering disabled")


def svg_to_png_bytes(svg_content: str, output_width: int = 800) -> Optional[BytesIO]:
    """
    Convert SVG string to PNG bytes for embedding in ReportLab.
    
    Args:
        svg_content: SVG markup as string (must be complete <svg>...</svg>)
        output_width: Output width in pixels (height auto-calculated)
    
    Returns:
        BytesIO with PNG data, or None if conversion fails
    """
    if not CAIROSVG_AVAILABLE:
        return None
    
    try:
        png_data = cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            output_width=output_width
        )
        return BytesIO(png_data)
    except Exception as e:
        print(f"SVG conversion error: {e}")
        return None


def extract_svgs_from_html(html: str) -> list:
    """
    Extract all SVG elements from HTML.
    
    Returns:
        List of SVG strings (complete <svg>...</svg>)
    """
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html, 'html.parser')
    svgs = soup.find_all('svg')
    
    result = []
    for svg in svgs:
        # Get full SVG as string
        svg_str = str(svg)
        result.append(svg_str)
    
    return result


def extract_base64_images(html: str) -> list:
    """
    Extract all base64-encoded images from HTML.
    
    Returns:
        List of (alt_text, BytesIO) tuples
    """
    from bs4 import BeautifulSoup
    import re
    
    soup = BeautifulSoup(html, 'html.parser')
    result = []
    
    for img in soup.find_all('img'):
        src = img.get('src', '')
        alt = img.get('alt', 'Image')
        
        if src.startswith('data:image/'):
            try:
                # Format: data:image/png;base64,iVBOR...
                header, data = src.split(',', 1)
                img_bytes = base64.b64decode(data)
                result.append((alt, BytesIO(img_bytes)))
            except Exception as e:
                print(f"Base64 decode error: {e}")
    
    return result


def get_svg_dimensions(svg_content: str) -> tuple:
    """
    Extract width/height from SVG (in user units).
    
    Returns:
        (width, height) or (350, 200) as default
    """
    import re
    
    # Try width="350" height="200"
    w_match = re.search(r'width="(\d+)"', svg_content)
    h_match = re.search(r'height="(\d+)"', svg_content)
    
    if w_match and h_match:
        return int(w_match.group(1)), int(h_match.group(1))
    
    # Try viewBox="0 0 350 200"
    vb_match = re.search(r'viewBox="[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)"', svg_content)
    if vb_match:
        return int(float(vb_match.group(1))), int(float(vb_match.group(2)))
    
    return 350, 200  # Default
