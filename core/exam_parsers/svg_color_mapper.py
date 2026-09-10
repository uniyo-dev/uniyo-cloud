"""
UNIYO LMS - SVG Color Mapper for Print
Converts dark-themed SVGs to light-themed versions for printing.
Preserves brand colors (gold, purple, teal) while swapping
backgrounds and text colors for better print readability.
"""

import re
from typing import Dict


# ============================================
# COLOR MAPPING: DARK → LIGHT (Print-friendly)
# ============================================

DARK_TO_LIGHT_MAP = {
    # Dark backgrounds → Light/white
    '#111827': '#FFFFFF',      # Main SVG background
    '#0B0F19': '#FFFFFF',      # Very dark background
    '#1a2332': '#F1F5F9',      # Dark box → Light gray box
    '#1A2332': '#F1F5F9',      # Same with case
    '#0F172A': '#FFFFFF',      # Another dark bg
    
    # Light text → Dark text (for readability on white)
    '#f8fafc': '#0B0F19',      # Near-white text → Near-black text
    '#F8FAFC': '#0B0F19',
    '#ffffff': '#0B0F19',      # White text → Dark text (careful with this)
    '#FFFFFF': '#0B0F19',
    
    # Muted light colors → Darker muted
    '#94A3B8': '#475569',      # Light gray text → Dark gray text
    '#94a3b8': '#475569',
    '#CBD5E1': '#334155',
    '#cbd5e1': '#334155',
    '#E2E8F0': '#1E293B',
    '#e2e8f0': '#1E293B',
    
    # Light backgrounds in boxes
    '#F8FAFC': '#FFFFFF',      # Very light → pure white (only if bg)
    '#F1F5F9': '#FFFFFF',      # Light gray → white (only if bg)
}

# ============================================
# PRESERVE THESE COLORS (brand colors)
# ============================================
PRESERVE_COLORS = [
    # Brand purple
    '#6D28D9', '#6d28d9', '#7C3AED', '#7c3aed',
    '#4C1D95', '#4c1d95', '#8B5CF6', '#8b5cf6',
    '#A78BFA', '#a78bfa', '#C4B5FD', '#c4b5fd',
    
    # Gold/amber (diagram accent)
    '#F59E0B', '#f59e0b', '#FCD34D', '#fcd34d',
    '#D97706', '#d97706', '#FBBF24', '#fbbf24',
    '#B45309', '#b45309',
    
    # Teal/success (diagram accent)
    '#14B8A6', '#14b8a6', '#22C55E', '#22c55e',
    '#10B981', '#10b981', '#0D9488', '#0d9488',
    
    # Red/pink (diagram accent)
    '#EF4444', '#ef4444', '#EC4899', '#ec4899',
    '#DC2626', '#dc2626', '#F43F5E', '#f43f5e',
    
    # Blue/cyan (diagram accent)
    '#38BDF8', '#38bdf8', '#0EA5E9', '#0ea5e9',
    '#0284C7', '#0284c7', '#3B82F6', '#3b82f6',
]


def should_preserve_color(hex_color: str) -> bool:
    """Check if color should be preserved (not converted)"""
    color_upper = hex_color.upper()
    for preserve in PRESERVE_COLORS:
        if preserve.upper() == color_upper:
            return True
    return False


def convert_svg_to_light(svg_content: str) -> str:
    """
    Convert dark-themed SVG to light-themed for printing.
    
    Strategy:
    1. Replace dark background colors with white/light
    2. Replace light text colors with dark text
    3. Preserve brand/accent colors (gold, purple, teal, etc.)
    
    Args:
        svg_content: Original SVG string
    
    Returns:
        Modified SVG string for light theme
    """
    result = svg_content
    
    # Pattern to match hex colors in fill, stroke, style attributes
    # Matches: fill="#111827", stroke="#f8fafc", etc.
    hex_pattern = r'(fill|stroke|style|color)=(["\'])(#[0-9A-Fa-f]{3,6})\2'
    
    def replace_color(match):
        attr = match.group(1)
        quote = match.group(2)
        color = match.group(3)
        color_upper = color.upper()
        
        # Preserve brand colors
        if should_preserve_color(color):
            return match.group(0)
        
        # Look up in mapping (case-insensitive)
        for old, new in DARK_TO_LIGHT_MAP.items():
            if old.upper() == color_upper:
                return f'{attr}={quote}{new}{quote}'
        
        # Not in mapping - keep as is
        return match.group(0)
    
    result = re.sub(hex_pattern, replace_color, result)
    
    # Also handle colors inside style="fill: #XXXXXX; stroke: #XXXXXX"
    # Pattern: fill: #color or stroke: #color
    style_pattern = r'(fill|stroke|background)\s*:\s*(#[0-9A-Fa-f]{3,6})'
    
    def replace_style_color(match):
        prop = match.group(1)
        color = match.group(2)
        color_upper = color.upper()
        
        if should_preserve_color(color):
            return match.group(0)
        
        for old, new in DARK_TO_LIGHT_MAP.items():
            if old.upper() == color_upper:
                return f'{prop}: {new}'
        
        return match.group(0)
    
    result = re.sub(style_pattern, replace_color, result)
    
    return result


def convert_svg_variants(svg_content: str) -> Dict[str, str]:
    """
    Return both dark (original) and light (print) versions.
    
    Returns:
        {'dark': original_svg, 'light': modified_svg}
    """
    return {
        'dark': svg_content,
        'light': convert_svg_to_light(svg_content)
    }
