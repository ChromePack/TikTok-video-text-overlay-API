# PRD: TikTok-Style Video Text Overlay API (Python Implementation)

## Project Overview

A Python-based REST API that adds TikTok-style text overlays to portrait videos. The system accepts video uploads and applies three distinct styled text overlays at different positions, producing a processed video that closely matches modern social media aesthetics.

## Current Project Status

This project is migrating from a Node.js/FFmpeg implementation to a Python-based solution for improved reliability, performance, and reduced dependency complexity on Linux/Ubuntu servers.

## Technical Architecture

### Core Technology Stack

- **Framework**: FastAPI or Flask (Python web framework)
- **Video Processing**: MoviePy or OpenCV for video manipulation
- **Text Rendering**: Pillow (PIL) with custom font rendering
- **Image Composition**: Pillow for overlay creation and composition
- **Font**: Proxima Nova Semibold (downloaded from GitHub)

### Key Dependencies

```python
# Core framework
fastapi>=0.100.0
uvicorn[standard]>=0.23.0

# Video processing (replaces FFmpeg)
moviepy>=1.0.3
opencv-python>=4.8.0

# Image and text processing
Pillow>=10.0.0
numpy>=1.24.0

# File handling
python-multipart>=0.0.6
aiofiles>=23.0.0
```

### Video Processing Approach

Instead of FFmpeg, use Python libraries that provide better control and reliability:

- **MoviePy**: Primary video processing library for loading, manipulating, and saving videos
- **OpenCV**: Additional video processing capabilities if needed
- **Pillow**: Generate text overlay images with precise positioning and styling

## API Specification

### Endpoint

- **URL**: `POST /add-text-overlay`
- **Content-Type**: `multipart/form-data`

### Request Format

```json
{
  "video": "file upload (MP4, MOV, AVI)",
  "texts": ["Text 1", "Text 2", "Text 3"]
}
```

### Response

- **Success**: Returns processed MP4 video file
- **Error**: JSON error response with details

### Input Requirements

- **Video Format**: MP4, MOV, AVI
- **Video Dimensions**: 720×1280 portrait (9:16 aspect ratio)
- **File Size Limit**: 50MB
- **Text Array**: Exactly 3 strings

## Text Overlay Specifications

Based on the reference screenshot and existing implementation, create three distinct text styling approaches:

### Text 1 (Top Area)

- **Style**: Black text on white rounded bubble background
- **Font**: Proxima Nova Semibold, 42px
- **Text Color**: `#131313` (dark gray/black)
- **Background**: White (`#FFFFFF`) with full opacity
- **Bubble Padding**: 20px vertical, 26px horizontal
- **Border Radius**: 13px
- **Position**: Top safe zone (12% from top)
- **Line Height**: 0.75x font size

### Text 2 (Center Area)

- **Style**: White text with black stroke outline
- **Font**: Proxima Nova Semibold, 42px
- **Text Color**: `#FFFFFF` (white)
- **Stroke**: Black (`#000000`), 9px width
- **Position**: Center of video
- **Line Height**: 1.2x font size
- **Background**: None (transparent)

### Text 3 (Bottom Area)

- **Style**: White text on red rounded bubble background
- **Font**: Proxima Nova Semibold, 42px
- **Text Color**: `#FFFFFF` (white)
- **Background**: Red (`#eb4040`) with full opacity
- **Bubble Padding**: 26px vertical, 26px horizontal
- **Border Radius**: 13px
- **Position**: Bottom safe zone (15% from bottom)
- **Line Height**: -0.2x font size (tight spacing)

### Typography System

- **Font Family**: Proxima Nova Semibold
- **Font Weight**: 600 (Semibold)
- **Font Source**: https://github.com/cognitedata/file-explorer/raw/refs/heads/master/public/proxima-nova-cufonfonts/ProximaNova-Semibold.ttf
- **Text Alignment**: Center-aligned
- **Auto-wrapping**: Intelligent word wrapping with safe zone awareness

### Layout System

- **Safe Zones**: Avoid TikTok UI elements
  - Top: 12% margin from top
  - Bottom: 15% margin from bottom
  - Horizontal: 10% margins from sides when auto-wrapping
- **Text Positioning**: Combined layout ensuring all texts fit properly without overlap
- **Line Breaks**: Support both explicit (`\n`) and automatic word wrapping

## Implementation Approach

### Video Processing Pipeline

1. **Video Input**: Load video using MoviePy
2. **Text Overlay Generation**: Create overlay images using Pillow
3. **Composition**: Composite overlays onto video frames
4. **Audio Preservation**: Maintain original audio track
5. **Output**: Export as MP4 with original quality

### Text Rendering System

```python
class TikTokVideoTextOverlay:
    def __init__(self):
        # Initialize with configurations from reference project

    def generate_text_overlays(self, texts):
        # Create PNG overlays for each text style

    def create_bubble_text(self, text, style_config):
        # Generate bubble-style text overlays

    def create_stroke_text(self, text, style_config):
        # Generate stroke-style text overlays

    def process_video(self, video_path, texts, output_path):
        # Main video processing pipeline
```

### Font Management

- Download Proxima Nova Semibold TTF from GitHub
- Register font with Pillow's ImageFont
- Fallback to system fonts if download fails

## Performance Requirements

### Processing Specifications

- **Video Length**: Support up to 30 seconds efficiently
- **Processing Time**: Target <30 seconds for 10-second videos
- **Memory Usage**: Efficient frame-by-frame processing
- **Concurrent Requests**: Handle multiple requests with proper resource management

### Error Handling

- **400 Errors**: Missing files, invalid formats, wrong text count
- **500 Errors**: Processing failures, resource constraints
- **Cleanup**: Automatic temporary file removal
- **Timeout**: Graceful handling of long processing times

## File Structure

```
video-overlay-api/
├── main.py                 # FastAPI application entry point
├── text_overlay.py         # Text overlay processing class
├── video_processor.py      # Video processing utilities
├── fonts/                  # Font files directory
│   └── ProximaNova-Semibold.ttf
├── temp/                   # Temporary file storage
├── requirements.txt        # Python dependencies
└── config.py              # Configuration settings
```

## Migration Benefits

### Advantages Over FFmpeg Approach

1. **Better Control**: Fine-grained control over text positioning and styling
2. **Simplified Dependencies**: No FFmpeg binary installation required
3. **Improved Reliability**: Python libraries are more predictable than FFmpeg subprocess calls
4. **Enhanced Debugging**: Better error messages and debugging capabilities
5. **Resource Efficiency**: More efficient memory and CPU usage for text overlay operations

### Reference Implementation Compatibility

- Maintain exact visual output matching the reference screenshot
- Preserve text positioning algorithms from the Node.js Canvas implementation
- Keep all configuration parameters and styling options
- Ensure same API interface for seamless migration

## Development Notes

### Testing Strategy

- Test with various video formats and dimensions
- Validate text wrapping with different content lengths
- Verify overlay positioning accuracy
- Performance testing with typical video lengths

### Deployment Considerations

- Ubuntu/Linux server optimization
- Containerization with Docker
- Environment variable configuration
- Health check endpoints

This PRD provides a comprehensive foundation for implementing the Python-based TikTok video text overlay API while maintaining compatibility with existing requirements and improving upon the current FFmpeg-based approach.
