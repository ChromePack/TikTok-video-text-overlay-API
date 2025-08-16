"""
TikTok-style text overlay processing class
Based on the reference Node.js Canvas implementation
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from config import TEXT_CONFIGS, VIDEO_WIDTH, VIDEO_HEIGHT, FONT_PATH, SAFE_ZONES


class TikTokVideoTextOverlay:
    """
    TikTok Text Overlay for Videos using Pillow
    Based on the image overlay implementation from the reference project
    """

    def __init__(self):
        self.config = {
            "width": VIDEO_WIDTH,
            "height": VIDEO_HEIGHT,
            "text1": TEXT_CONFIGS["text1"],
            "text2": TEXT_CONFIGS["text2"],
            "text3": TEXT_CONFIGS["text3"],
            "safeZones": SAFE_ZONES,
        }
        self.font_path = FONT_PATH
        self._setup_font()

    def _setup_font(self):
        """Setup font for text rendering"""
        try:
            # Test if font file exists and is valid
            if self.font_path.exists():
                test_font = ImageFont.truetype(str(self.font_path), 42)
                print(f"✅ Proxima Nova font loaded successfully: {self.font_path}")
            else:
                print(f"⚠️ Font file not found at {self.font_path}, using default font")
                self.font_path = None
        except Exception as e:
            print(f"⚠️ Error loading font: {e}, using default font")
            self.font_path = None

    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get font object with specified size"""
        try:
            if self.font_path and self.font_path.exists():
                return ImageFont.truetype(str(self.font_path), size)
            else:
                # Fallback to default font
                return ImageFont.load_default()
        except Exception:
            return ImageFont.load_default()

    def split_text_by_newlines(self, text: str) -> List[str]:
        """Split text by newlines for proper line breaking"""
        processed_text = text.replace("\\n", "\n")
        return [line for line in processed_text.split("\n") if line.strip()]

    def should_auto_wrap(self, text: str) -> bool:
        """Decide if we should auto-wrap (no explicit newlines)"""
        return not re.search(r"\n|\\n", text)

    def get_max_bubble_width_for_auto_mode(self) -> int:
        """Compute the maximum bubble width allowed when centered, obeying safe zones"""
        canvas_width = self.config["width"]  # 720
        center_x = canvas_width / 2  # 360
        right_boundary = canvas_width * 0.9  # 90% of width to avoid right edge
        left_boundary = canvas_width * 0.1  # 10% margin from left

        max_half_width_right = right_boundary - center_x
        max_half_width_left = center_x - left_boundary
        max_half_width = min(max_half_width_right, max_half_width_left)
        return int(max_half_width * 2)

    def auto_wrap_lines(self, text: str, text_config: Dict, font: ImageFont.FreeTypeFont) -> List[str]:
        """
        Auto-wrap text into lines without breaking words
        - Only used when no explicit newlines are provided
        - Enforces safe horizontal zone by limiting bubble width
        - Greedy word wrapping using font measurement
        """
        # Create a temporary image for text measurement
        temp_img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)

        # Normalize whitespace and treat multiple spaces as single separators
        normalized = re.sub(r"\\n", "\n", text)
        normalized = re.sub(r"\n", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()

        if not normalized:
            return []

        max_bubble_width = self.get_max_bubble_width_for_auto_mode()
        max_text_width = max(0, max_bubble_width - 2 * text_config.get("horizontalPadding", 22))

        words = normalized.split(" ")
        lines = []
        current_line = ""

        for word in words:
            candidate = f"{current_line} {word}" if current_line else word
            bbox = temp_draw.textbbox((0, 0), candidate, font=font)
            candidate_width = bbox[2] - bbox[0]

            if candidate_width <= max_text_width:
                current_line = candidate
                continue

            # Candidate would exceed available width
            if current_line:
                # Push current line and start a new one with the word
                lines.append(current_line)
                current_line = word
            else:
                # Single word longer than allowed width: place it on its own line (allowed to overflow)
                lines.append(word)
                current_line = ""

        if current_line:
            lines.append(current_line)

        return lines

    def calculate_text_metrics(self, text: str, text_config: Dict) -> Dict:
        """
        Calculate text dimensions and line breaks
        - Uses explicit newlines if provided by user
        - Falls back to auto word-wrapping when no newlines present
        """
        font = self._get_font(text_config["fontSize"])
        
        # Determine mode: explicit line breaks vs. auto-wrap
        has_explicit_breaks = re.search(r"\n|\\n", text)
        lines = (
            self.split_text_by_newlines(text)
            if has_explicit_breaks
            else self.auto_wrap_lines(text, text_config, font)
        )

        line_height = text_config["fontSize"] * text_config.get("lineHeight", 0.75)
        return {
            "lines": lines,
            "lineHeight": line_height,
            "totalHeight": len(lines) * line_height,
        }

    def draw_bubble(
        self,
        draw: ImageDraw.Draw,
        x: int,
        y: int,
        width: int,
        height: int,
        radius: int,
        color: str,
        opacity: float = 1,
    ):
        """Draw rounded rectangle bubble background"""
        # Convert color to RGBA
        if color.startswith("#"):
            color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
        
        alpha = int(255 * opacity)
        color_rgba = color + (alpha,) if len(color) == 3 else color

        # Draw rounded rectangle
        draw.rounded_rectangle(
            [x, y, x + width, y + height],
            radius=radius,
            fill=color_rgba
        )

    def create_text_overlay(self, text: str, text_config: Dict, overlay_index: int) -> Optional[Image.Image]:
        """Create text overlay image for a specific text with its styling"""
        if not text or not text.strip():
            return None

        # Create transparent canvas
        canvas = Image.new("RGBA", (self.config["width"], self.config["height"]), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        # Get font
        font = self._get_font(text_config["fontSize"])

        # Calculate text metrics and line breaks (auto-wrap or explicit)
        text_metrics = self.calculate_text_metrics(text, text_config)
        if not text_metrics["lines"]:
            return None

        # Calculate positioning
        line_height = text_metrics["lineHeight"]
        bubble_height = line_height + text_config.get("bubblePadding", 0) * 2
        gap_between_bubbles = -10 if text_config.get("bubbleColor") else 50  # Overlap for bubbles, gap for stroke text

        # Calculate starting Y position based on text position
        total_height = (
            len(text_metrics["lines"]) * bubble_height
            + (len(text_metrics["lines"]) - 1) * gap_between_bubbles
        )

        position = text_config.get("position", "center")
        if position == "top":
            start_y = self.config["height"] * self.config["safeZones"]["top"]
        elif position == "bottom":
            start_y = self.config["height"] * self.config["safeZones"]["bottom"] - total_height
        else:  # center
            start_y = (self.config["height"] - total_height) / 2

        # Draw each line
        for index, line in enumerate(text_metrics["lines"]):
            # Get text dimensions for this line
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            current_y = start_y + index * (bubble_height + gap_between_bubbles)

            # Draw bubble background if configured
            if text_config.get("bubbleColor"):
                bubble_width = line_width + text_config.get("horizontalPadding", 26) * 2
                bubble_x = (self.config["width"] - bubble_width) / 2

                self.draw_bubble(
                    draw,
                    int(bubble_x),
                    int(current_y),
                    int(bubble_width),
                    int(bubble_height),
                    text_config.get("bubbleRadius", 13),
                    text_config["bubbleColor"],
                    text_config.get("bubbleOpacity", 1),
                )

            # Calculate text position
            text_x = self.config["width"] / 2
            text_y = current_y + bubble_height / 2

            # Draw text with stroke if configured
            if text_config.get("strokeColor") and text_config.get("strokeWidth"):
                stroke_width = text_config["strokeWidth"]
                stroke_color = text_config["strokeColor"]
                
                # Convert stroke color
                if stroke_color.startswith("#"):
                    stroke_color = tuple(int(stroke_color[i:i+2], 16) for i in (1, 3, 5))

                # Draw stroke by drawing text multiple times offset
                for dx in range(-stroke_width, stroke_width + 1):
                    for dy in range(-stroke_width, stroke_width + 1):
                        if dx * dx + dy * dy <= stroke_width * stroke_width:
                            draw.text(
                                (text_x + dx, text_y + dy),
                                line,
                                font=font,
                                fill=stroke_color,
                                anchor="mm"
                            )

            # Draw main text
            text_color = text_config["textColor"]
            if text_color.startswith("#"):
                text_color = tuple(int(text_color[i:i+2], 16) for i in (1, 3, 5))

            draw.text(
                (text_x, text_y),
                line,
                font=font,
                fill=text_color,
                anchor="mm"
            )

        return canvas

    def calculate_combined_text_layout(self, texts: List[str]) -> List[Dict]:
        """Calculate combined height and positioning for all texts"""
        text_configs = [
            self.config["text1"],
            self.config["text2"],
            self.config["text3"],
        ]
        text_heights = []
        gap_between_texts = 70  # Gap between different text blocks

        # Calculate height for each text
        for i, text in enumerate(texts):
            if text and text.strip():
                text_config = text_configs[i]
                text_metrics = self.calculate_text_metrics(text, text_config)
                line_height = text_metrics["lineHeight"]
                bubble_height = line_height + text_config.get("bubblePadding", 0) * 2
                total_text_height = len(text_metrics["lines"]) * bubble_height

                text_heights.append({
                    "text": text,
                    "config": text_config,
                    "height": total_text_height,
                    "lines": text_metrics["lines"],
                    "lineHeight": line_height,
                    "bubbleHeight": bubble_height,
                })

        # Calculate total combined height
        total_height = (
            sum(text_info["height"] for text_info in text_heights)
            + (len(text_heights) - 1) * gap_between_texts
        )

        # Calculate starting Y position to center all texts
        start_y = (self.config["height"] - total_height) / 2

        # Calculate individual Y positions for each text
        current_y = start_y
        for text_info in text_heights:
            text_info["startY"] = current_y
            current_y += text_info["height"] + gap_between_texts

        return text_heights

    def create_text_overlay_with_position(
        self, text: str, text_config: Dict, start_y: float, text_info: Dict
    ) -> Optional[Image.Image]:
        """Create text overlay image for a specific text with custom positioning"""
        if not text or not text.strip():
            return None

        # Create transparent canvas
        canvas = Image.new("RGBA", (self.config["width"], self.config["height"]), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        # Get font
        font = self._get_font(text_config["fontSize"])

        # Draw each line
        for index, line in enumerate(text_info["lines"]):
            # Get text dimensions for this line
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            
            current_y = start_y + index * text_info["bubbleHeight"]

            # Draw bubble background if configured
            if text_config.get("bubbleColor"):
                bubble_width = line_width + text_config.get("horizontalPadding", 26) * 2
                bubble_x = (self.config["width"] - bubble_width) / 2

                self.draw_bubble(
                    draw,
                    int(bubble_x),
                    int(current_y),
                    int(bubble_width),
                    int(text_info["bubbleHeight"]),
                    text_config.get("bubbleRadius", 13),
                    text_config["bubbleColor"],
                    text_config.get("bubbleOpacity", 1),
                )

            # Calculate text position
            text_x = self.config["width"] / 2
            text_y = current_y + text_info["bubbleHeight"] / 2

            # Draw text with stroke if configured
            if text_config.get("strokeColor") and text_config.get("strokeWidth"):
                stroke_width = text_config["strokeWidth"]
                stroke_color = text_config["strokeColor"]
                
                # Convert stroke color
                if stroke_color.startswith("#"):
                    stroke_color = tuple(int(stroke_color[i:i+2], 16) for i in (1, 3, 5))

                # Draw stroke by drawing text multiple times offset
                for dx in range(-stroke_width, stroke_width + 1):
                    for dy in range(-stroke_width, stroke_width + 1):
                        if dx * dx + dy * dy <= stroke_width * stroke_width:
                            draw.text(
                                (text_x + dx, text_y + dy),
                                line,
                                font=font,
                                fill=stroke_color,
                                anchor="mm"
                            )

            # Draw main text
            text_color = text_config["textColor"]
            if text_color.startswith("#"):
                text_color = tuple(int(text_color[i:i+2], 16) for i in (1, 3, 5))

            draw.text(
                (text_x, text_y),
                line,
                font=font,
                fill=text_color,
                anchor="mm"
            )

        return canvas

    def generate_text_overlays(self, texts: List[str]) -> List[Tuple[Image.Image, str]]:
        """
        Generate all text overlay images with combined positioning
        Returns list of (overlay_image, temp_path) tuples
        """
        overlays = []

        # Calculate combined layout for all texts
        text_layouts = self.calculate_combined_text_layout(texts)

        # Generate overlay for each text with calculated positioning
        for index, text_info in enumerate(text_layouts):
            overlay = self.create_text_overlay_with_position(
                text_info["text"],
                text_info["config"],
                text_info["startY"],
                text_info
            )

            if overlay:
                # Save to temporary file
                temp_path = f"temp/overlay_{index + 1}_{hash(text_info['text']) % 10000}.png"
                os.makedirs("temp", exist_ok=True)
                overlay.save(temp_path)
                overlays.append((overlay, temp_path))

        return overlays