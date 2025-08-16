"""
FastAPI application for TikTok Video Text Overlay API
Python-based replacement for the Node.js/FFmpeg implementation
"""
import os
import json
import tempfile
import uuid
from pathlib import Path
from typing import List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from video_processor import VideoProcessor
from text_overlay import TikTokVideoTextOverlay
from config import (
    PORT, HOST, MAX_FILE_SIZE, ALLOWED_VIDEO_FORMATS, 
    TEMP_DIR, PROCESSING_TIMEOUT
)


# Initialize FastAPI app
app = FastAPI(
    title="TikTok Video Text Overlay API",
    description="Python-based API for adding TikTok-style text overlays to videos",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global processor instance
video_processor = VideoProcessor()

# Thread pool for video processing
thread_pool = ThreadPoolExecutor(max_workers=2)


def ensure_temp_dir():
    """Ensure temp directory exists"""
    os.makedirs(TEMP_DIR, exist_ok=True)


def cleanup_file(file_path: str):
    """Safely remove a file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Warning: Could not cleanup file {file_path}: {e}")


def validate_video_file(file: UploadFile) -> bool:
    """Validate uploaded video file"""
    if not file.content_type in ALLOWED_VIDEO_FORMATS:
        return False
    return True


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    ensure_temp_dir()
    print(f"🚀 TikTok Video Text Overlay API starting on {HOST}:{PORT}")
    print(f"📁 Temp directory: {TEMP_DIR}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    print("🛑 Shutting down TikTok Video Text Overlay API")
    
    # Clean up thread pool
    thread_pool.shutdown(wait=True)
    
    # Clean up temp directory
    try:
        for file in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except Exception as e:
        print(f"Warning: Could not clean up temp directory: {e}")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "TikTok Video Text Overlay API",
        "version": "1.0.0",
        "status": "OK",
        "endpoints": {
            "health": "GET /health",
            "add_text_overlay": "POST /add-text-overlay"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "OK",
        "service": "TikTok Video Text Overlay API",
        "version": "1.0.0"
    }


def process_video_sync(input_path: str, texts: List[str], output_path: str) -> bool:
    """Synchronous video processing function for thread pool"""
    try:
        return video_processor.process_video_with_text_overlays(
            input_path, texts, output_path
        )
    except Exception as e:
        print(f"Error in video processing: {e}")
        return False


@app.post("/add-text-overlay")
async def add_text_overlay(
    video: UploadFile = File(..., description="Video file (MP4, MOV, AVI)"),
    texts: str = Form(..., description="JSON array of 3 text strings")
):
    """
    Add text overlays to video
    
    Args:
        video: Video file upload
        texts: JSON string containing array of exactly 3 text strings
        
    Returns:
        Processed video file with text overlays
    """
    input_path = None
    output_path = None
    
    try:
        # Validate video file
        if not validate_video_file(video):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Only {', '.join(ALLOWED_VIDEO_FORMATS)} are allowed."
            )
        
        # Check file size
        content = await video.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Parse texts JSON
        try:
            texts_list = json.loads(texts)
            if not isinstance(texts_list, list) or len(texts_list) != 3:
                raise ValueError("Must be array of exactly 3 strings")
            
            # Ensure all texts are strings
            texts_list = [str(text) for text in texts_list]
            
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid texts format. Must be JSON array of exactly 3 strings. Error: {e}"
            )
        
        # Create temporary files
        unique_id = str(uuid.uuid4())
        input_filename = f"input_{unique_id}.{video.filename.split('.')[-1]}"
        output_filename = f"output_{unique_id}.mp4"
        
        input_path = os.path.join(TEMP_DIR, input_filename)
        output_path = os.path.join(TEMP_DIR, output_filename)
        
        # Save uploaded video to temp file
        with open(input_path, "wb") as f:
            f.write(content)
        
        print(f"📹 Processing video: {video.filename}")
        print(f"📝 Texts: {texts_list}")
        
        # Process video in thread pool with timeout
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(
            thread_pool, 
            process_video_sync, 
            input_path, 
            texts_list, 
            output_path
        )
        
        try:
            success = await asyncio.wait_for(future, timeout=PROCESSING_TIMEOUT)
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=408,
                detail="Video processing timed out. Please try with a shorter video."
            )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Video processing failed. Please check your video file and try again."
            )
        
        if not os.path.exists(output_path):
            raise HTTPException(
                status_code=500,
                detail="Processed video file was not created. Processing may have failed."
            )
        
        print(f"✅ Video processing completed: {output_path}")
        
        # Return processed video file
        def cleanup_files():
            """Cleanup function to run after response is sent"""
            cleanup_file(input_path)
            cleanup_file(output_path)
        
        # Schedule cleanup after response
        background_tasks = None
        try:
            from fastapi import BackgroundTasks
            background_tasks = BackgroundTasks()
            background_tasks.add_task(cleanup_files)
        except ImportError:
            # Fallback cleanup
            pass
        
        response = FileResponse(
            output_path,
            media_type="video/mp4",
            filename="video-with-overlay.mp4",
            background=background_tasks
        )
        
        # If BackgroundTasks not available, schedule cleanup manually
        if background_tasks is None:
            loop.call_later(10, cleanup_files)  # Cleanup after 10 seconds
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        cleanup_file(input_path)
        cleanup_file(output_path)
        raise
        
    except Exception as e:
        # Clean up files on error
        cleanup_file(input_path)
        cleanup_file(output_path)
        
        print(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/video-info")
async def get_video_info(video: UploadFile = File(...)):
    """
    Get information about an uploaded video file
    """
    input_path = None
    
    try:
        # Validate video file
        if not validate_video_file(video):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Only {', '.join(ALLOWED_VIDEO_FORMATS)} are allowed."
            )
        
        # Save to temporary file
        content = await video.read()
        unique_id = str(uuid.uuid4())
        input_filename = f"info_{unique_id}.{video.filename.split('.')[-1]}"
        input_path = os.path.join(TEMP_DIR, input_filename)
        
        with open(input_path, "wb") as f:
            f.write(content)
        
        # Get video info
        info = video_processor.get_video_info(input_path)
        
        if info is None:
            raise HTTPException(
                status_code=400,
                detail="Could not read video file information"
            )
        
        return {
            "filename": video.filename,
            "size_bytes": len(content),
            "duration_seconds": info["duration"],
            "width": info["width"],
            "height": info["height"],
            "fps": info["fps"],
            "has_audio": info["has_audio"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading video info: {str(e)}"
        )
    finally:
        cleanup_file(input_path)


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "message": f"Route {request.url.path} does not exist",
            "available_endpoints": [
                "GET /",
                "GET /health", 
                "POST /add-text-overlay",
                "GET /video-info"
            ]
        }
    )


@app.exception_handler(413)
async def payload_too_large_handler(request, exc):
    return JSONResponse(
        status_code=413,
        content={
            "error": "Payload too large",
            "message": f"File size exceeds maximum limit of {MAX_FILE_SIZE // (1024*1024)}MB"
        }
    )


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False,  # Set to True for development
        log_level="info"
    )