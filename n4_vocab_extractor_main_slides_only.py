# SAVE_MY_N4_v7.py  ← Switching to dHash for Text Sensitivity
import os, cv2, imagehash, yt_dlp
from PIL import Image
import re
import unicodedata

# ----------------------------------------------------------------
# --- 🛑 CONFIGURATION: YOUR TIME OFFSETS 🛑 ---
# 
# First X seconds to skip (Welcome/Title screens)
SKIP_START_SECONDS = 35 

# Last Y seconds to skip (Thank You/End Screen)
STOP_END_SECONDS = 15

# --- CRITICAL FIX: DEDUPLICATION HASH ALGORITHM ---
# Switched to dHash (Difference Hash) for higher sensitivity to text changes.
# dHash is more reliable for screenshots where only small areas change.
# Threshold is kept moderately low (8) for dHash, which is very sensitive.
HASH_THRESHOLD = 8 
# ----------------------------------------------------------------

# --- Strict Path Sanitization Function (Kept for path safety) ---
def create_safe_folder_name(title, max_length=80):
    """Ensures folder names are safe for all operating systems."""
    normalized = unicodedata.normalize('NFKD', title)
    ascii_only = normalized.encode('ascii', 'ignore').decode('ascii')
    safe_chars = re.sub(r'[^\w\s-]', '', ascii_only).strip()
    final_name = re.sub(r'[-\s]+', '_', safe_chars)
    return final_name[:max_length]
# ----------------------------------------

url = input("\nPaste your N4 playlist URL and press Enter:\n> ").strip()

ydl = yt_dlp.YoutubeDL({
    'format': 'best[height<=720][ext=mp4]', 
    'outtmpl': 'CURRENT_VIDEO.mp4',
    'quiet': True,
    'no_warnings': True,
    'merge_output_format': 'mp4',
})

print("\nStarting — please wait...\n")
os.makedirs("N4_Slides", exist_ok=True)

# 1. Get the playlist information
try:
    with yt_dlp.YoutubeDL({'quiet': True}) as info_ydl:
        playlist_info = info_ydl.extract_info(url, download=False)
        videos = playlist_info.get('entries', [])
        
    if not videos:
        print("Error: Could not extract video entries from the playlist URL.")
        input("\nPress Enter to exit...")
        exit()

except Exception as e:
    print(f"An error occurred while fetching playlist info: {e}")
    input("\nPress Enter to exit...")
    exit()

# 2. Loop through each video in the playlist
for idx, video in enumerate(videos, 1):
    if video is None:
        print(f"[{idx:02d}/{len(videos)}] Skipping an invalid video entry.")
        continue

    safe_title = create_safe_folder_name(video['title'])
    folder = os.path.join("N4_Slides", f"{idx:02d}_{safe_title}")
    os.makedirs(folder, exist_ok=True)
    
    print(f"[{idx:02d}/{len(videos)}] {video['title']}")
    print(f"   -> Saving slides to: {folder}")

    # Download the video
    try:
        ydl.download([video['webpage_url']])
    except Exception as e:
        print(f"   !!! FAILED to download video {idx}: {e}")
        continue

    # 3. Extract and filter slides
    cap = cv2.VideoCapture("CURRENT_VIDEO.mp4")
    
    # Get video metadata for time calculation
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    video_duration_seconds = frame_count / fps if fps > 0 else 0
    
    # Calculate start and end frame indices based on your offsets
    start_frame = int(SKIP_START_SECONDS * fps)
    end_frame = int((video_duration_seconds - STOP_END_SECONDS) * fps)
    
    saved = 0
    seen = [] 

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        current_frame_index = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

        # 1. Time-Based Filtering (skips intro/outro)
        if current_frame_index < start_frame:
            continue
        
        if current_frame_index > end_frame and end_frame > 0:
            break 
        
        # 2. Deduplication Check (captures only unique slides in the middle)
        if current_frame_index % 20 == 1: 
            try:
                # --- CRITICAL CHANGE: Using dHash for text sensitivity ---
                hsh = imagehash.dhash(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                
                is_duplicate = any(hsh - old < HASH_THRESHOLD for old in seen[-20:])
                
                if not is_duplicate:
                    seen.append(hsh)
                    saved += 1
                    
                    output_filepath = os.path.join(folder, f"{saved:03d}.jpg")
                    success = cv2.imwrite(output_filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                    
                    if success:
                        print(f"   saved {saved}")
                    else:
                        print(f"   !!! FAILED to save slide {saved} at: {output_filepath}")
                        
            except Exception as frame_error:
                print(f"   !!! An error occurred while processing frame: {frame_error}")
                break

    cap.release()
    
    if os.path.exists("CURRENT_VIDEO.mp4"):
        os.remove("CURRENT_VIDEO.mp4")
        
    print(f"   {saved} unique vocabulary slides saved\n")

print("FINISHED — ALL YOUR N4 SLIDES ARE IN THE N4_Slides FOLDER")

try:
    os.startfile("N4_Slides")
except Exception:
    print("Could not automatically open the folder. Please check the 'N4_Slides' folder manually.")
    
input("\nPress Enter to exit...")