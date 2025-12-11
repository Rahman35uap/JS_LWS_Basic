import os
import subprocess
import unicodedata
import re
import shutil
import json

# --- CONFIGURATION ---
PITCH_SHIFT_SEMITONES = -6.7 
OUTPUT_ROOT_FOLDER = "Male_Voice_Videos" 

# --- CRITICAL PATHS (Confirmed Working) ---
# 1. FFmpeg Path
FFMPEG_PATH = r"C:\Program Files (x86)\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe" 
# 2. Path to the new external executable (MUST be in the same folder as this script)
YTDLP_EXTERNAL_PATH = r".\yt-dlp.exe" # Relative path to the downloaded yt-dlp.exe
# -------------------------------------------

# Calculate the speed factor for FFmpeg's 'atempo' filter
PITCH_FACTOR = 2.0 ** (PITCH_SHIFT_SEMITONES / 12.0)
TEMPO_CORRECTION = 1.0 / PITCH_FACTOR

# --- PATH AND FILENAME SANITIZATION ---
def create_safe_filename(title, jlpt_level, max_length=120):
    normalized = unicodedata.normalize('NFKD', title)
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

# --- 1. Get Playlist Information using the external yt-dlp.exe ---

print("Fetching playlist information...")
try:
    # Use external yt-dlp.exe to get JSON info
    info_process = subprocess.run(
        [
            YTDLP_EXTERNAL_PATH, 
            '--flat-playlist', # Only list entries
            '--dump-json',     # Output in JSON format
            url
        ], 
        capture_output=True, 
        text=True, 
        check=True
    )
    # The output is a series of JSON objects, one per video
    videos = []
    for line in info_process.stdout.strip().split('\n'):
        try:
            video_info = json.loads(line)
            if video_info.get('id'): # Check for a valid video entry
                videos.append(video_info)
        except json.JSONDecodeError:
            continue
            
    if not videos:
        print("Error: Could not extract any valid video entries from the playlist.")
        exit()
except subprocess.CalledProcessError as e:
    print(f"An error occurred while fetching playlist info (yt-dlp external call failed): {e.stderr}")
    exit()
except Exception as e:
    print(f"An unexpected error occurred during info extraction: {e}")
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

    # --- A. Download and Merge Original Audio/Video using the external yt-dlp.exe ---
    print("  1. Downloading best available combined video and audio stream...")
    
    try:
        subprocess.run(
            [
                YTDLP_EXTERNAL_PATH,
                # --- FORCING SOLVER DOWNLOAD IS THE KEY FIX ---
                '--remote-components', 'ejs:github', 
                '--ffmpeg-location', FFMPEG_PATH, # Tell yt-dlp where FFmpeg is
                '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]', 
                '-o', temp_video_download,
                '--merge-output-format', 'mp4',
                '--quiet', # Keep the output clean
                video_url
            ], 
            check=True
        )
        if not os.path.exists(temp_video_download) or os.path.getsize(temp_video_download) == 0:
             print("  !!! Download failed or resulted in an empty file. Skipping.")
             continue
    except subprocess.CalledProcessError as e:
        print(f"  !!! Download failed (yt-dlp external call): {e}. Skipping.")
        continue

    # --- B. Pitch Shift Audio using FFmpeg Path ---
    print(f"  2. Shifting pitch by {PITCH_SHIFT_SEMITONES} semitones using FFmpeg...")
    try:
        audio_filter = f"asetrate=44100*{PITCH_FACTOR},atempo={TEMPO_CORRECTION}"

        subprocess.run(
            [
                FFMPEG_PATH, 
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
                FFMPEG_PATH, 
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

try:
    os.startfile(OUTPUT_ROOT_FOLDER)
except Exception:
    print(f"Could not automatically open the folder. Please check the '{OUTPUT_ROOT_FOLDER}' folder manually.")