"""
Video processing utilities using MoviePy
Replaces FFmpeg functionality with Python-based video processing
"""
import os
import tempfile
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
from moviepy import VideoFileClip, CompositeVideoClip, ImageClip
from PIL import Image
from text_overlay import TikTokVideoTextOverlay
from config import VIDEO_WIDTH, VIDEO_HEIGHT, PROCESSING_TIMEOUT


class VideoProcessor:
    """
    Video processing class that handles video loading, text overlay composition,
    and video output using MoviePy instead of FFmpeg
    """

    def __init__(self):
        self.text_overlay = TikTokVideoTextOverlay()
        self.temp_files = []

    def cleanup_temp_files(self):
        """Clean up temporary files created during processing"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"Warning: Could not clean up temporary file {temp_file}: {e}")
        self.temp_files.clear()

    def validate_video(self, video_path: str) -> bool:
        """
        Validate video file format and basic properties
        """
        try:
            with VideoFileClip(video_path) as clip:
                # Check if video has reasonable dimensions and duration
                if clip.duration is None or clip.duration <= 0:
                    return False
                if clip.w is None or clip.h is None:
                    return False
                return True
        except Exception as e:
            print(f"Video validation failed: {e}")
            return False

    def resize_video_to_portrait(self, video_clip: VideoFileClip) -> VideoFileClip:
        """
        Resize video to 720x1280 portrait format
        Maintains aspect ratio and crops/pads as needed
        """
        target_width = VIDEO_WIDTH
        target_height = VIDEO_HEIGHT
        target_ratio = target_width / target_height

        # Get original dimensions
        original_width = video_clip.w
        original_height = video_clip.h
        original_ratio = original_width / original_height

        if abs(original_ratio - target_ratio) < 0.01:
            # Aspect ratios are close enough, just resize
            return video_clip.resize((target_width, target_height))

        if original_ratio > target_ratio:
            # Video is wider, need to crop width
            new_width = int(original_height * target_ratio)
            x_offset = (original_width - new_width) // 2
            cropped = video_clip.crop(x1=x_offset, x2=x_offset + new_width)
            return cropped.resize((target_width, target_height))
        else:
            # Video is taller, need to crop height
            new_height = int(original_width / target_ratio)
            y_offset = (original_height - new_height) // 2
            cropped = video_clip.crop(y1=y_offset, y2=y_offset + new_height)
            return cropped.resize((target_width, target_height))

    def create_overlay_clips(self, overlay_images: List[Tuple[Image.Image, str]], duration: float) -> List[ImageClip]:
        """
        Create MoviePy ImageClips from overlay images
        """
        overlay_clips = []
        
        for overlay_image, temp_path in overlay_images:
            try:
                # Convert PIL Image to numpy array
                img_array = np.array(overlay_image)
                
                # Create ImageClip
                img_clip = ImageClip(img_array, duration=duration, transparent=True)
                overlay_clips.append(img_clip)
                
            except Exception as e:
                print(f"Error creating overlay clip from {temp_path}: {e}")
                continue
                
        return overlay_clips

    def process_video_with_text_overlays(
        self, 
        input_video_path: str, 
        texts: List[str], 
        output_video_path: str
    ) -> bool:
        """
        Main video processing function that adds text overlays to video
        
        Args:
            input_video_path: Path to input video file
            texts: List of 3 text strings for overlays
            output_video_path: Path where processed video will be saved
            
        Returns:
            bool: True if processing successful, False otherwise
        """
        video_clip = None
        
        try:
            # Validate input
            if not self.validate_video(input_video_path):
                print("❌ Video validation failed")
                return False

            if len(texts) != 3:
                print("❌ Must provide exactly 3 text strings")
                return False

            print(f"🔄 Loading video: {input_video_path}")
            
            # Load video
            video_clip = VideoFileClip(input_video_path)
            
            # Resize to portrait format if needed
            if video_clip.w != VIDEO_WIDTH or video_clip.h != VIDEO_HEIGHT:
                print(f"📐 Resizing video from {video_clip.w}x{video_clip.h} to {VIDEO_WIDTH}x{VIDEO_HEIGHT}")
                video_clip = self.resize_video_to_portrait(video_clip)

            # Generate text overlays
            print("📝 Generating text overlays...")
            overlay_images = self.text_overlay.generate_text_overlays(texts)
            
            if not overlay_images:
                print("⚠️ No text overlays generated")
                # If no overlays, just output the original video
                video_clip.write_videofile(
                    output_video_path,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile=f"{output_video_path}_temp_audio.m4a",
                    remove_temp=True
                )
                return True

            # Add temp files to cleanup list
            for _, temp_path in overlay_images:
                self.temp_files.append(temp_path)

            # Create overlay clips
            print("🎬 Creating overlay clips...")
            overlay_clips = self.create_overlay_clips(overlay_images, video_clip.duration)

            if not overlay_clips:
                print("⚠️ No overlay clips created, outputting original video")
                video_clip.write_videofile(
                    output_video_path,
                    codec='libx264',
                    audio_codec='aac'
                )
                return True

            # Composite video with overlays
            print("🎭 Compositing video with text overlays...")
            clips_to_composite = [video_clip] + overlay_clips
            final_video = CompositeVideoClip(clips_to_composite)

            # Write output video
            print(f"💾 Writing output video: {output_video_path}")
            final_video.write_videofile(
                output_video_path,
                codec='libx264',
                audio_codec='aac'
            )

            print("✅ Video processing completed successfully")
            return True

        except Exception as e:
            print(f"❌ Error processing video: {e}")
            return False

        finally:
            # Clean up video clip
            if video_clip:
                video_clip.close()
            
            # Clean up temporary files
            self.cleanup_temp_files()

    def get_video_info(self, video_path: str) -> Optional[dict]:
        """
        Get basic information about a video file
        """
        try:
            with VideoFileClip(video_path) as clip:
                return {
                    "duration": clip.duration,
                    "width": clip.w,
                    "height": clip.h,
                    "fps": clip.fps,
                    "has_audio": clip.audio is not None
                }
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None

    def extract_frame(self, video_path: str, time_seconds: float = 1.0) -> Optional[Image.Image]:
        """
        Extract a single frame from video for preview purposes
        """
        try:
            with VideoFileClip(video_path) as clip:
                if time_seconds > clip.duration:
                    time_seconds = clip.duration / 2
                
                # Get frame as numpy array
                frame_array = clip.get_frame(time_seconds)
                
                # Convert to PIL Image
                frame_image = Image.fromarray(frame_array)
                return frame_image
                
        except Exception as e:
            print(f"Error extracting frame: {e}")
            return None