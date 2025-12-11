# n4_fixed.py  ← English folders + ALL slides saved (no missing)
import os
import cv2
import yt_dlp
from PIL import Image
import imagehash
import re

def english_folder(title):
    # Keep only English letters/numbers/spaces, replace others with _
    safe = re.sub(r'[^a-zA-Z0-9 ]', '_', title)
    safe = re.sub(r'\s+', '_', safe.strip())
    return safe[:80] or "Lesson"

url = input("\nPaste playlist URL:\n> ").strip()

ydl_opts = {
    'format': 'best[height<=720][ext=mp4]',
    'outtmpl': 'VIDEO.mp4',
    'quiet': True,
    'merge_output_format': 'mp4',
}

os.makedirs("N4_ENGLISH", exist_ok=True)

with yt_dlp.YoutubeDL({'quiet': True}) as ydl_info:
    info = ydl_info.extract_info(url, download=False)
    videos = info['entries']

print(f"\n{len(videos)} videos — starting...\n")

for i, video in enumerate(videos, 1):
    title = video['title']
    folder = f"N4_ENGLISH/{i:02d}_{english_folder(title)}"
    os.makedirs(folder, exist_ok=True)
    
    print(f"[{i:02d}/{len(videos)}] {title}")
    print(f"   → {folder}")

    try:
        yt_dlp.YoutubeDL(ydl_opts).download([video['webpage_url']])
    except:
        print("   Download failed")
        continue

    cap = cv2.VideoCapture("VIDEO.mp4")
    if not cap.isOpened():
        print("   Video open failed")
        continue

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    interval = int(fps * 1.0)  # Every 1 second
    saved = 0
    seen = []
    frame_no = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_no += 1
        if frame_no % interval != 0:
            continue

        # Crop to ignore UI/cursor
        h, w = frame.shape[:2]
        crop = frame[int(h*0.15):int(h*0.85), int(w*0.15):int(w*0.85)]
        hsh = imagehash.average_hash(Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)))

        if all(hsh - old >= 6 for old in seen[-10:]):  # Loose duplicate check
            seen.append(hsh)
            saved += 1
            path = os.path.join(folder, f"{saved:03d}.jpg")
            ok = cv2.imwrite(path, frame)
            print(f"   saved {saved}" if ok else f"   FAILED {saved}")

    cap.release()
    if os.path.exists("VIDEO.mp4"):
        os.remove("VIDEO.mp4")

    print(f"   {saved} slides\n")

print("DONE! Check N4_ENGLISH folder")
os.startfile("N4_ENGLISH")
input("Press Enter...")