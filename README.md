# TikTok Video Text Overlay API (Python)

A Python-based REST API that adds TikTok-style text overlays to portrait videos. This project replaces the previous Node.js/FFmpeg implementation with a more reliable Python solution using MoviePy and Pillow.

## Features

- 🎥 **Video Processing**: Handles MP4, MOV, and AVI video formats
- 📝 **Text Overlays**: Three distinct text overlay styles matching TikTok aesthetics
- 🎨 **Smart Positioning**: Automatic text positioning with safe zone awareness
- 🔤 **Custom Font**: Uses Proxima Nova Semibold for professional typography
- ⚡ **Fast Processing**: Efficient video processing without FFmpeg dependencies
- 🛡️ **Error Handling**: Comprehensive error handling and file cleanup

## Text Overlay Styles

### Text 1 (Top Area)
- Black text on white rounded bubble background
- Font: Proxima Nova Semibold, 42px
- Position: Top safe zone (12% from top)

### Text 2 (Center Area)  
- White text with black stroke outline
- Font: Proxima Nova Semibold, 42px
- Position: Center of video

### Text 3 (Bottom Area)
- White text on red rounded bubble background
- Font: Proxima Nova Semibold, 42px  
- Position: Bottom safe zone (15% from bottom)

## Installation

### Prerequisites
- Python 3.8 or higher
- Linux/Ubuntu server (recommended)

### Setup

1. **Clone or download the project**
   ```bash
   cd /home/mussy/Documents/TikTok-video-text-overlay-API
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify font installation**
   The Proxima Nova Semibold font should already be downloaded in the `fonts/` directory.

4. **Create temp directory**
   ```bash
   mkdir -p temp
   ```

## Usage

### Start the Server

```bash
python main.py
```

The API will start on `http://localhost:3000` by default.

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Add Text Overlay
```bash
POST /add-text-overlay
Content-Type: multipart/form-data

Fields:
- video: Video file (MP4, MOV, AVI)
- texts: JSON array of exactly 3 strings
```

### Example Usage

#### Using curl
```bash
curl -X POST \
  -F "video=@your-video.mp4" \
  -F 'texts=["Health Tip of the Day", "Sleeping n@ked helps you stay cooler and sleep 10% better", "Send this to someone who needs to hear the truth"]' \
  http://localhost:3000/add-text-overlay \
  --output result.mp4
```

#### Using Python requests
```python
import requests

url = "http://localhost:3000/add-text-overlay"
files = {"video": open("your-video.mp4", "rb")}
data = {"texts": '["Text 1", "Text 2", "Text 3"]'}

response = requests.post(url, files=files, data=data)

if response.status_code == 200:
    with open("result.mp4", "wb") as f:
        f.write(response.content)
```

## Configuration

### Environment Variables
- `PORT`: Server port (default: 3000)
- `HOST`: Server host (default: 0.0.0.0)

### Video Specifications
- **Input Format**: MP4, MOV, AVI
- **Output Format**: MP4
- **Target Dimensions**: 720×1280 (portrait)
- **File Size Limit**: 50MB
- **Processing Timeout**: 5 minutes

## Project Structure

```
TikTok-video-text-overlay-API/
├── main.py                 # FastAPI application entry point
├── text_overlay.py         # Text overlay processing class
├── video_processor.py      # Video processing utilities
├── config.py              # Configuration settings
├── requirements.txt        # Python dependencies
├── fonts/                  # Font files directory
│   └── ProximaNova-Semibold.ttf
├── temp/                   # Temporary file storage
└── docs/                   # Documentation
    └── PRD.md             # Product Requirements Document
```

## Technical Details

### Core Technologies
- **FastAPI**: Modern Python web framework
- **MoviePy**: Video processing and manipulation
- **Pillow (PIL)**: Image processing and text rendering
- **NumPy**: Numerical operations for video arrays

### Key Improvements Over FFmpeg
1. **Better Control**: Fine-grained control over text positioning and styling
2. **Simplified Dependencies**: No FFmpeg binary installation required
3. **Improved Reliability**: Python libraries are more predictable than FFmpeg subprocess calls
4. **Enhanced Debugging**: Better error messages and debugging capabilities
5. **Resource Efficiency**: More efficient memory and CPU usage

### Text Processing Features
- **Auto-wrapping**: Intelligent word wrapping with safe zone awareness
- **Line Breaks**: Support for both explicit (`\n`) and automatic line breaks
- **Font Fallback**: Graceful fallback to system fonts if Proxima Nova fails to load
- **Combined Layout**: Smart positioning to prevent text overlap

## Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid file format, missing texts, wrong text count
- **413 Payload Too Large**: File exceeds 50MB limit
- **408 Request Timeout**: Processing takes longer than 5 minutes
- **500 Internal Server Error**: Processing failures, system errors

## Development

### Running in Development Mode
```bash
# Enable auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 3000
```

### Testing the Implementation
```bash
# Test with a sample video
python test_api.py
```

## Deployment

### Production Deployment
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:3000
```

### Docker Deployment
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 3000

CMD ["python", "main.py"]
```

## Performance Considerations

- **Concurrent Processing**: Limited to 2 parallel video processing tasks
- **Memory Management**: Automatic cleanup of temporary files
- **Video Size**: Optimized for videos up to 30 seconds
- **Resource Limits**: 50MB file size limit to prevent server overload

## Troubleshooting

### Common Issues

1. **Font Loading Errors**
   - Ensure `fonts/ProximaNova-Semibold.ttf` exists
   - Check file permissions
   - API will fallback to system fonts automatically

2. **Video Processing Failures**
   - Verify video file is not corrupted
   - Check video format is supported (MP4, MOV, AVI)
   - Ensure sufficient disk space in temp directory

3. **Memory Issues**
   - Reduce concurrent processing workers
   - Use smaller video files for testing
   - Monitor server resources

### Logs and Debugging
The application provides detailed console logging for:
- Video processing steps
- Text overlay generation
- Error conditions
- Performance metrics

## License

This project is developed for TikTok-style video processing applications.