# JLPT_SLIDE_DOWNLOADER_v9.py  ← Universal Script for ALL JLPT Levels
import os, cv2, imagehash, yt_dlp
from PIL import Image
import re
import unicodedata

# ----------------------------------------------------------------
# --- 🛑 CONFIGURATION: TIME OFFSETS 🛑 ---
# 
# Using the proven time offsets from your previous N4 setup.
SKIP_START_SECONDS = 35 
STOP_END_SECONDS = 15

# --- HASHING CONFIGURATION ---
POST_CHANGE_FRAME_DELAY = 10 
HASH_THRESHOLD = 8 
# ----------------------------------------------------------------

# --- Strict Path Sanitization Function ---
def create_safe_folder_name(title, max_length=80):
    """Ensures folder names are safe for all operating systems."""
    normalized = unicodedata.normalize('NFKD', title)
    ascii_only = normalized.encode('ascii', 'ignore').decode('ascii')
    safe_chars = re.sub(r'[^\w\s-]', '', ascii_only).strip()
    final_name = re.sub(r'[-\s]+', '_', safe_chars)
    return final_name[:max_length]
# ----------------------------------------

# --- DYNAMIC INPUTS ---

# 1. Get the JLPT Level from the user
while True:
    jlpt_level = input("\nEnter the JLPT Level (e.g., N5, N4, N3): ").strip().upper()
    if jlpt_level in ['N5', 'N4', 'N3', 'N2', 'N1']:
        break
    print("Invalid level. Please enter N5, N4, N3, N2, or N1.")

# 2. Get the Playlist URL from the user
url = input(f"\nPaste the {jlpt_level} playlist URL and press Enter:\n> ").strip()

# Set the dynamic output folder name
OUTPUT_FOLDER_NAME = f"{jlpt_level}_Slides"
print(f"Output folder will be: {OUTPUT_FOLDER_NAME}")

# --- YOUTUBE-DLP CONFIGURATION ---
ydl = yt_dlp.YoutubeDL({
    'format': 'best[height<=720][ext=mp4]', 
    'outtmpl': jlpt_level+'_running_one.mp4',
    'quiet': True,
    'no_warnings': True,
    'merge_output_format': 'mp4',
})

print("\nStarting — please wait...\n")
os.makedirs(OUTPUT_FOLDER_NAME, exist_ok=True)

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
    # Dynamic folder path construction
    folder = os.path.join(OUTPUT_FOLDER_NAME, f"{idx:02d}_{safe_title}")
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
    cap = cv2.VideoCapture(jlpt_level+"_running_one.mp4")
    
    # Get video metadata for time calculation
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    video_duration_seconds = frame_count / fps if fps > 0 else 0
    
    # Calculate start and end frame indices based on your fixed offsets
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
                hsh = imagehash.dhash(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                
                is_duplicate = any(hsh - old < HASH_THRESHOLD for old in seen[-20:])
                
                if not is_duplicate:
                    # Store the hash of the *detected* new slide (before saving)
                    seen.append(hsh)
                    saved += 1
                    
                    # Advance the frame position to skip the transition/blur
                    stable_frame_index = current_frame_index + POST_CHANGE_FRAME_DELAY
                    
                    # Ensure the advanced index is within the video
                    if stable_frame_index < frame_count:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, stable_frame_index)
                        ret, stable_frame = cap.read()
                        
                        frame_to_save = stable_frame if ret else frame 
                    else:
                        frame_to_save = frame
                        
                    # Save the stable frame
                    output_filepath = os.path.join(folder, f"{saved:03d}.jpg")
                    success = cv2.imwrite(output_filepath, frame_to_save, [cv2.IMWRITE_JPEG_QUALITY, 90])
                    
                    if success:
                        print(f"   saved {saved} (at frame {stable_frame_index})")
                    else:
                        print(f"   !!! FAILED to save slide {saved} at: {output_filepath}")
                        
            except Exception as frame_error:
                print(f"   !!! An error occurred while processing frame: {frame_error}")

    cap.release()
    
    if os.path.exists(jlpt_level+"_running_one.mp4"):
        os.remove(jlpt_level+"_running_one.mp4")
        
    print(f"   {saved} unique vocabulary slides saved\n")

print(f"FINISHED — ALL YOUR {jlpt_level} SLIDES ARE IN THE {OUTPUT_FOLDER_NAME} FOLDER")

try:
    os.startfile(OUTPUT_FOLDER_NAME)
except Exception:
    print(f"Could not automatically open the folder. Please check the '{OUTPUT_FOLDER_NAME}' folder manually.")
    
input("\nPress Enter to exit...")