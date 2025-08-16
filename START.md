# TikTok Video Text Overlay API - Quick Start

## 🚀 How to Run the API

### Prerequisites
- Python 3.8+ installed
- Required dependencies

### 1. Install Dependencies
```bash
pip3 install --break-system-packages fastapi uvicorn moviepy pillow numpy python-multipart requests
```

### 2. Start the Server
```bash
cd /home/mussy/Documents/TikTok-video-text-overlay-API
python3 main.py
```

The API will start on: **http://localhost:3000**

### 3. API Endpoints
- **Health Check**: `GET /health`
- **Text Overlay**: `POST /add-text-overlay`

## 📬 Postman/cURL Usage

### cURL Command for Postman:
```bash
curl --location 'http://localhost:3000/add-text-overlay' \
--form 'video=@"/path/to/your/video.mp4"' \
--form 'texts="[\"Health Tip of the Day\", \"Sleeping n@ked helps you stay cooler and sleep 10% better\", \"Send this to someone who needs to hear the truth\"]"'
```

### Postman Setup:
1. **Method**: POST
2. **URL**: `http://localhost:3000/add-text-overlay`
3. **Body**: form-data
   - Key: `video` | Type: File | Value: Select your MP4/MOV/AVI file
   - Key: `texts` | Type: Text | Value: `["Text 1", "Text 2", "Text 3"]`

### Response:
- **Success**: Returns processed MP4 video file
- **Error**: JSON error message

## 📝 Text Format
The `texts` parameter must be a JSON array of exactly 3 strings:
```json
["Top text", "Center text", "Bottom text"]
```

## 🎬 Supported Formats
- **Input**: MP4, MOV, AVI (max 50MB)
- **Output**: MP4 with text overlays
- **Dimensions**: Optimized for 720x1280 (portrait)