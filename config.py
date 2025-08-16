"""
Configuration settings for TikTok Video Text Overlay API
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
FONTS_DIR = BASE_DIR / "fonts"
TEMP_DIR = BASE_DIR / "temp"

# Server configuration
PORT = int(os.getenv("PORT", 3000))
HOST = os.getenv("HOST", "0.0.0.0")

# File upload limits
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_VIDEO_FORMATS = ["video/mp4", "video/quicktime", "video/x-msvideo"]

# Video specifications
VIDEO_WIDTH = 720
VIDEO_HEIGHT = 1280

# Font configuration
FONT_FAMILY = "Proxima Nova Semibold"
FONT_PATH = FONTS_DIR / "ProximaNova-Semibold.ttf"

# Text overlay configurations
TEXT_CONFIGS = {
    "text1": {
        "fontSize": 42,
        "fontFamily": "Proxima Nova Semibold",
        "fontWeight": "normal",
        "textColor": "#131313",
        "bubbleColor": "#FFFFFF",
        "bubbleOpacity": 1,
        "bubblePadding": 20,
        "horizontalPadding": 26,
        "bubbleRadius": 13,
        "position": "top",
        "lineHeight": 0.75,
    },
    "text2": {
        "fontSize": 42,
        "fontFamily": "Proxima Nova Semibold",
        "fontWeight": "normal",
        "textColor": "#FFFFFF",
        "strokeColor": "#000000",
        "strokeWidth": 9,
        "position": "center",
        "lineHeight": 1.2,
    },
    "text3": {
        "fontSize": 46,
        "fontFamily": "Proxima Nova Semibold",
        "fontWeight": "normal",
        "textColor": "#FFFFFF",
        "bubbleColor": "#DB3643",
        "bubbleOpacity": 1,
        "bubblePadding": 33,
        "horizontalPadding": 26,
        "bubbleRadius": 7,
        "position": "bottom",
        "lineHeight": 0,
    },
}

# Safe zones for TikTok UI
SAFE_ZONES = {
    "top": 0.12,  # 12% from top
    "bottom": 0.85,  # 15% from bottom (85% of height)
}

# Processing timeouts
PROCESSING_TIMEOUT = 300  # 5 minutes