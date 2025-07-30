#!/usr/bin/env python3
"""
Video Captioner with Word-Level Animated Captions
Transcribes video audio and adds kinetic typography captions with precise timing.
"""

import whisper
import json
from moviepy.editor import *
import numpy as np
from typing import List, Dict, Tuple
from PIL import Image, ImageDraw, ImageFont
import os

def transcribe_with_word_timestamps(video_path: str) -> List[Dict]:
    """
    Transcribe video audio using OpenAI Whisper with word-level timestamps.
    
    Args:
        video_path: Path to input video file
        
    Returns:
        List of word segments with start/end times and text
    """
    print("Loading Whisper model...")
    model = whisper.load_model("base")
    
    print("Transcribing audio...")
    result = model.transcribe(video_path, word_timestamps=True)
    
    word_segments = []
    for segment in result["segments"]:
        if "words" in segment:
            for word in segment["words"]:
                word_segments.append({
                    "text": word["word"].strip(),
                    "start": word["start"],
                    "end": word["end"]
                })
    
    print(f"Extracted {len(word_segments)} words with timestamps")
    return word_segments

def create_text_image(text: str, font_size: int, width: int, height: int, is_highlight: bool = False) -> np.ndarray:
    """Create text image using PIL with bold font and styling."""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Convert to uppercase
    text = text.upper()
    
    # Try to load bold fonts (Impact-style)
    font = None
    bold_fonts = ["impact.ttf", "arial-bold.ttf", "arialbd.ttf", "calibrib.ttf"]
    
    for font_name in bold_fonts:
        try:
            font = ImageFont.truetype(font_name, font_size)
            break
        except:
            continue
    
    if font is None:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # Get text size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center text
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw thick black stroke/outline (increased thickness)
    stroke_width = 4
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, 255))
    
    # All text is yellow #FAFD07, brighter for highlights
    text_color = (255, 255, 0, 255) if is_highlight else (250, 253, 7, 255)  # Bright yellow or #FAFD07
    
    # Draw main text
    draw.text((x, y), text, font=font, fill=text_color)
    
    return np.array(img)

def create_word_caption_clips(transcript_segments: List[Dict], video_size: Tuple[int, int], highlight_words: List[str] = None) -> List[ImageClip]:
    """
    Create animated text clips for each word with kinetic typography effects.
    
    Args:
        transcript_segments: List of word segments with timing
        video_size: (width, height) of the video
        highlight_words: List of words to highlight in yellow
        
    Returns:
        List of ImageClip objects with animations
    """
    caption_clips = []
    width, height = video_size
    
    # Text styling - larger font for impact (25% bigger)
    font_size = min(int(width // 9.6), 125)  # 25% increase from width//12
    
    # Position for captions (center)
    caption_y = int(height * 0.5)
    
    # Group words into lines (fewer words per line for vertical video)
    lines = []
    current_line = []
    words_per_line = 2  # Reduced for better readability in vertical format
    
    if highlight_words is None:
        highlight_words = []
    
    # Convert highlight words to uppercase for comparison
    highlight_words = [word.upper() for word in highlight_words]
    
    for i, word_data in enumerate(transcript_segments):
        current_line.append(word_data)
        
        if len(current_line) >= words_per_line or i == len(transcript_segments) - 1:
            lines.append(current_line)
            current_line = []
    
    # Create clips for each word - keep all at center position
    for word_data in transcript_segments:
        # Check if word should be highlighted
        is_highlight = word_data["text"].upper().strip() in highlight_words
        
        # Create text image
        text_img = create_text_image(
            word_data["text"], 
            font_size, 
            width, 
            int(font_size * 1.5), 
            is_highlight
        )
        
        # Create image clip - all positioned at center
        img_clip = ImageClip(text_img, transparent=True)
        img_clip = img_clip.set_start(word_data["start"]).set_duration(word_data["end"] - word_data["start"])
        img_clip = img_clip.set_position((0, caption_y))  # Fixed center position
        
        # Add fade-in effect
        img_clip = img_clip.crossfadein(0.1)
        
        caption_clips.append(img_clip)
    
    return caption_clips

def compose_final_video_with_captions(video_path: str, caption_clips: List[ImageClip], output_path: str):
    """
    Compose the final video with hardcoded captions.
    
    Args:
        video_path: Path to input video
        caption_clips: List of caption text clips
        output_path: Path for output video
    """
    print("Loading video...")
    video = VideoFileClip(video_path)
    
    print("Compositing captions...")
    # Combine video with all caption clips
    final_video = CompositeVideoClip([video] + caption_clips)
    
    print(f"Rendering final video to {output_path}...")
    final_video.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True,
        fps=video.fps
    )
    
    # Clean up
    video.close()
    final_video.close()
    print("Video rendering complete!")

def main():
    """Main function to process video with captions."""
    input_video = "stitched_output.mp4"
    output_video = "captioned_output.mp4"
    
    # Define words to highlight in yellow (customize as needed)
    highlight_words = ["amazing", "incredible", "wow", "perfect", "awesome", "fantastic"]
    
    try:
        # Step 1: Transcribe with word timestamps
        word_segments = transcribe_with_word_timestamps(input_video)
        
        # Get video dimensions for responsive text sizing
        temp_video = VideoFileClip(input_video)
        video_size = (temp_video.w, temp_video.h)
        temp_video.close()
        
        # Step 2: Create caption clips with highlighting
        caption_clips = create_word_caption_clips(word_segments, video_size, highlight_words)
        
        # Step 3: Compose final video
        compose_final_video_with_captions(input_video, caption_clips, output_video)
        
        print(f"Successfully created captioned video: {output_video}")
        
    except FileNotFoundError:
        print(f"Error: Input video '{input_video}' not found!")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()