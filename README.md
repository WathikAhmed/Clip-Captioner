# Video Captioner with Kinetic Typography

Automatically transcribes video audio and adds word-by-word animated captions with precise timing.

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install FFmpeg:**
   - **Windows:** Download from https://ffmpeg.org/download.html or use `winget install ffmpeg`
   - **macOS:** `brew install ffmpeg`
   - **Linux:** `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (CentOS/RHEL)

## Usage

1. Place your input video file as `stitched_output.mp4` in the same directory
2. Run the script:
```bash
python video_captioner.py
```
3. The captioned video will be saved as `captioned_output.mp4`

## Features

- **Word-level timing:** Uses OpenAI Whisper for precise word timestamps
- **Kinetic typography:** Pop-in animations and fade effects
- **Responsive design:** Automatically adjusts for vertical (9:16) videos
- **Auto line-breaking:** Handles long captions by breaking into multiple lines
- **Styled text:** White text with black outline for visibility
- **Hardcoded captions:** Renders directly onto video (not overlay)

## Script Structure

- `transcribe_with_word_timestamps()` - Extracts audio and generates word-level transcription
- `create_word_caption_clips()` - Creates animated text clips with kinetic effects
- `compose_final_video_with_captions()` - Combines video with captions and renders output

## Customization

Edit the script to modify:
- Font size and style (line 52-56)
- Text colors and effects (line 57-60)
- Caption positioning (line 63)
- Words per line (line 66)
- Animation effects (line 85-92)