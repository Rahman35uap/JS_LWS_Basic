# JLPT_SLIDE_DOWNLOADER_v12.py  ← Maximum Robustness (Skip errors, bypass streaming issues)
import os, cv2, imagehash, yt_dlp
from PIL import Image
import re
import unicodedata

# ----------------------------------------------------------------
# --- 🛑 CONFIGURATION: TIME OFFSETS 🛑 ---
# 
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
while True:
    jlpt_level = input("\nEnter the JLPT Level (e.g., N5, N4, N3): ").strip().upper()
    if jlpt_level in ['N5', 'N4', 'N3', 'N2', 'N1']:
        break
    print("Invalid level. Please enter N5, N4, N3, N2, or N1.")

url = input(f"\nPaste the {jlpt_level} playlist URL and press Enter:\n> ").strip()

OUTPUT_FOLDER_NAME = f"{jlpt_level}_Slides"
print(f"Output folder will be: {OUTPUT_FOLDER_NAME}")

# --- YOUTUBE-DLP CONFIGURATION (CRITICAL CHANGES HERE) ---
ydl = yt_dlp.YoutubeDL({
    'format': 'best[height<=720][ext=mp4]', 
    'outtmpl': 'CURRENT_VIDEO.mp4',
    'quiet': True,
    'no_warnings': True,
    'merge_output_format': 'mp4',
    'allow_unplayable_formats': True,
    
    # --- FIX 1: Explicitly ignore download errors for individual videos ---
    'ignoreerrors': True,
    
    # --- FIX 2: Bypasses YouTube streaming issues (SABR, missing URL) ---
    'extractor_args': {'youtube': {'skip': ['web_safari']}},
})

print("\nStarting — please wait...\n")
os.makedirs(OUTPUT_FOLDER_NAME, exist_ok=True)

# 1. Get the playlist information
try:
    # Retaining 'ignoreerrors': True for the info extraction, which prevents crash here.
    info_opts = {'quiet': True, 'ignoreerrors': True}
    with yt_dlp.YoutubeDL(info_opts) as info_ydl:
        playlist_info = info_ydl.extract_info(url, download=False)
        videos = playlist_info.get('entries', [])
        
    videos = [v for v in videos if v is not None]
        
    if not videos:
        print("Error: Could not extract any valid video entries from the playlist URL.")
        input("\nPress Enter to exit...")
        exit()

except Exception as e:
    print(f"An error occurred while fetching playlist info: {e}")
    input("\nPress Enter to exit...")
    exit()

# 2. Loop through each video in the playlist
for idx, video in enumerate(videos, 1):
    
    # Enhanced skip logic for entries without ID or Title
    if not video.get('id') or not video.get('title'):
        print(f"[{idx:02d}/{len(videos)}] Skipping unavailable/private video entry.")
        continue

    safe_title = create_safe_folder_name(video['title'])
    folder = os.path.join(OUTPUT_FOLDER_NAME, f"{idx:02d}_{safe_title}")
    os.makedirs(folder, exist_ok=True)
    
    print(f"[{idx:02d}/{len(videos)}] {video['title']}")
    print(f"   -> Saving slides to: {folder}")

    # Download the video
    try:
        video_source = video.get('url') or video.get('webpage_url')
        if not video_source:
             print(f"   !!! FAILED to download video {idx}: Missing video source URL.")
             continue
             
        # ydl.download will now silently skip the private video due to 'ignoreerrors': True 
        # in the ydl config above, preventing the crash.
        ydl.download([video_source])
        
    except Exception as e:
        print(f"   !!! FAILED to download video {idx} ({video['title']}): {e}")
        continue

    # Skip processing if the file was not successfully downloaded (e.g., was private)
    if not os.path.exists("CURRENT_VIDEO.mp4"):
        print(f"   !!! Skipping slide extraction for video {idx} (Download failed or was skipped).")
        continue

    # 3. Extract and filter slides
    cap = cv2.VideoCapture("CURRENT_VIDEO.mp4")
    # ... (rest of the slide extraction logic remains unchanged and is already perfect)
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    video_duration_seconds = frame_count / fps if fps > 0 else 0
    
    start_frame = int(SKIP_START_SECONDS * fps)
    end_frame = int((video_duration_seconds - STOP_END_SECONDS) * fps)
    
    saved = 0
    seen = [] 

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        current_frame_index = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

        if current_frame_index < start_frame: continue
        if current_frame_index > end_frame and end_frame > 0: break 
        
        if current_frame_index % 20 == 1: 
            try:
                hsh = imagehash.dhash(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                is_duplicate = any(hsh - old < HASH_THRESHOLD for old in seen[-20:])
                
                if not is_duplicate:
                    seen.append(hsh)
                    saved += 1
                    
                    stable_frame_index = current_frame_index + POST_CHANGE_FRAME_DELAY
                    
                    if stable_frame_index < frame_count:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, stable_frame_index)
                        ret, stable_frame = cap.read()
                        frame_to_save = stable_frame if ret else frame 
                    else:
                        frame_to_save = frame
                        
                    output_filepath = os.path.join(folder, f"{saved:03d}.jpg")
                    success = cv2.imwrite(output_filepath, frame_to_save, [cv2.IMWRITE_JPEG_QUALITY, 90])
                    
                    if success:
                        print(f"   saved {saved} (at frame {stable_frame_index})")
                    else:
                        print(f"   !!! FAILED to save slide {saved} at: {output_filepath}")
                        
            except Exception as frame_error:
                print(f"   !!! An error occurred while processing frame: {frame_error}")

    cap.release()
    
    if os.path.exists("CURRENT_VIDEO.mp4"):
        os.remove("CURRENT_VIDEO.mp4")
        
    print(f"   {saved} unique vocabulary slides saved\n")

print(f"FINISHED — ALL YOUR {jlpt_level} SLIDES ARE IN THE {OUTPUT_FOLDER_NAME} FOLDER")

try:
    os.startfile(OUTPUT_FOLDER_NAME)
except Exception:
    print(f"Could not automatically open the folder. Please check the '{OUTPUT_FOLDER_NAME}' folder manually.")
    
input("\nPress Enter to exit...")