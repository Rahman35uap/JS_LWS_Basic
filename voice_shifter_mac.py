import os
import subprocess
import unicodedata
import re
import shutil
import json
import sys

# --- SCRIPT CONFIGURATION ---
# Set the desired pitch shift. -7.1 is used as it was in your input.
PITCH_SHIFT_SEMITONES = -7.1 
OUTPUT_ROOT_FOLDER = "Male_Voice_Videos" 

# --- CRITICAL PATHS (MAC/HOMEBREW VERSION) ---
# Homebrew ensures ffmpeg and yt-dlp are in the system PATH.
# We do NOT need to hardcode paths like the Windows version.
# We call the executable names directly.
FFMPEG_COMMAND = "ffmpeg"
YTDLP_COMMAND = "yt-dlp"
# ---------------------------------------------

# Calculate the speed factor for FFmpeg's 'atempo' filter
PITCH_FACTOR = 2.0 ** (PITCH_SHIFT_SEMITONES / 12.0)
TEMPO_CORRECTION = 1.0 / PITCH_FACTOR

# --- PATH AND FILENAME SANITIZATION ---
def create_safe_filename(title, jlpt_level, max_length=120):
    """Generates a safe filename including the dynamic JLPT level."""
    # This logic is universal and remains the same
    normalized = unicodedata.normalize('NFKD', title)
    # macOS file systems handle special characters better, but we keep this for safety
    ascii_only = normalized.encode('ascii', 'ignore').decode('ascii')
    safe_chars = re.sub(r'[^\w\s-]', '', ascii_only).strip()
    
    clean_title = re.sub(r'[-\s]+', '_', safe_chars)
    clean_title = re.sub(r'(JLPT[_ ]*[Nn]\d+)', '', clean_title, flags=re.IGNORECASE).strip('_')
    
    final_name = f"JLPT_{jlpt_level}_{clean_title}"
    
    return final_name[:max_length]

# --- DYNAMIC INPUTS ---
url = input("\nPaste the YouTube Playlist URL:\n> ").strip()
jlpt_level = input("Enter the JLPT Level (e.g., N5, N4, N3):\n> ").strip().upper()

print(f"Output folder will be: {OUTPUT_ROOT_FOLDER}")
print(f"Processing videos for JLPT Level: {jlpt_level}")

os.makedirs(OUTPUT_ROOT_FOLDER, exist_ok=True)
print("\nStarting — please wait...\n")

# --- 1. Get Playlist Information using the external yt-dlp command ---

print("Fetching playlist information...")
try:
    # Call yt-dlp command directly (relies on it being in the PATH)
    info_process = subprocess.run(
        [
            YTDLP_COMMAND, 
            '--flat-playlist',
            '--dump-json',
            url
        ], 
        capture_output=True, 
        text=True, 
        check=True
    )
    videos = []
    for line in info_process.stdout.strip().split('\n'):
        try:
            video_info = json.loads(line)
            if video_info.get('id'):
                videos.append(video_info)
        except json.JSONDecodeError:
            continue
            
    if not videos:
        print("Error: Could not extract any valid video entries from the playlist.")
        exit()
except subprocess.CalledProcessError as e:
    print(f"An error occurred while fetching playlist info (yt-dlp external call failed). Ensure yt-dlp is installed via Homebrew and in your PATH.")
    print(f"Details: {e.stderr}")
    exit()

# --- 2. Loop through each video in the playlist ---
for idx, video in enumerate(videos, 1):
    
    video_url = video.get('url')
    title = video.get('title', f"Unknown_Title_{video.get('id')}")

    safe_title = create_safe_filename(title, jlpt_level)
    final_video_path = os.path.join(OUTPUT_ROOT_FOLDER, f"{idx:02d}_{safe_title}_MALE.mp4")
    
    temp_video_download = os.path.join(OUTPUT_ROOT_FOLDER, "temp_video_original.mp4")
    temp_audio_pitched = os.path.join(OUTPUT_ROOT_FOLDER, "temp_pitched.mp3")

    print(f"\n[{idx:02d}/{len(videos)}] Processing: {title}")
    
    if os.path.exists(final_video_path):
        print(f"  -> Skipping. Final video already exists at: {final_video_path}")
        continue

    # --- A. Download and Merge Original Audio/Video using the external yt-dlp command ---
    print("  1. Downloading best available combined video and audio stream...")
    
    try:
        subprocess.run(
            [
                YTDLP_COMMAND,
                '--remote-components', 'ejs:github', 
                # FFMPEG_COMMAND is found via PATH, no explicit --ffmpeg-location needed
                '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]', 
                '-o', temp_video_download,
                '--merge-output-format', 'mp4',
                '--quiet', 
                video_url
            ], 
            check=True
        )
        if not os.path.exists(temp_video_download) or os.path.getsize(temp_video_download) == 0:
             print("  !!! Download failed or resulted in an empty file. Skipping.")
             continue
    except subprocess.CalledProcessError as e:
        print(f"  !!! Download failed (yt-dlp external call failed): {e}. Skipping.")
        continue

    # --- B. Pitch Shift Audio using FFmpeg command ---
    print(f"  2. Shifting pitch by {PITCH_SHIFT_SEMITONES} semitones and adding 'কর্কশ' roughness...")
    try:
        # 1. Pitch Shift and Speed Correction
        pitch_speed_filter = f"asetrate=44100*{PITCH_FACTOR},atempo={TEMPO_CORRECTION}"
        
        # 2. Roughness/Distortion Filter ("কর্কশ") - Using Compand for aggressive sound shaping
        roughness_filter = "compand=attacks=0:points=-80/-80|-10/-10|0/0:soft-knee=10"
        
        # Combine all filters
        audio_filter = f"{pitch_speed_filter},{roughness_filter}"

        subprocess.run(
            [
                FFMPEG_COMMAND, 
                '-i', temp_video_download,  
                '-af', audio_filter, 
                '-vn',                   
                '-c:a', 'libmp3lame',    
                '-b:a', '192k',
                '-loglevel', 'error', 
                '-y',
                temp_audio_pitched
            ], 
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"  !!! Failed to pitch shift audio with FFmpeg: {e}. Skipping.")
        if os.path.exists(temp_video_download): os.remove(temp_video_download) 
        if os.path.exists(temp_audio_pitched): os.remove(temp_audio_pitched) 
        continue

    # --- C. Final Merge (Video + Pitched Audio) ---
    print("  3. Merging video with the new male-pitched audio...")
    try:
        subprocess.run(
            [
                FFMPEG_COMMAND, 
                '-i', temp_video_download,  
                '-i', temp_audio_pitched,   
                '-c:v', 'copy',          
                '-c:a', 'aac',           
                '-map', '0:v:0',         
                '-map', '1:a:0',         
                '-loglevel', 'error', 
                '-y',                    
                final_video_path
            ], 
            check=True
        )
        print(f"  ✅ SUCCESS! File saved to: {final_video_path}")
    except subprocess.CalledProcessError as e:
        print(f"  !!! Failed to perform final merge: {e}")
        continue
    
    # --- D. Cleanup All Temporary Files ---
    try:
        if os.path.exists(temp_video_download): os.remove(temp_video_download)
        if os.path.exists(temp_audio_pitched): os.remove(temp_audio_pitched)
    except Exception as e:
        print(f"  !!! WARNING: Failed to clean up temporary files: {e}")


print(f"\nFINISHED — ALL VIDEOS WITH MODIFIED AUDIO ARE IN THE '{OUTPUT_ROOT_FOLDER}' FOLDER")

# macOS command to open the folder
try:
    subprocess.run(["open", OUTPUT_ROOT_FOLDER], check=True)
except Exception:
    print(f"Could not automatically open the folder. Please check the '{OUTPUT_ROOT_FOLDER}' folder manually.")