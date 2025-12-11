# n4_ULTIMATE_PERFECT.py  ← YOUR script + my filtering = PERFECTION
import os
import cv2
import yt_dlp
from PIL import Image
import imagehash
import re
import numpy as np

def english_folder(title):
    safe = re.sub(r'[^a-zA-Z0-9 ]', '_', title)
    safe = re.sub(r'\s+', '_', safe.strip())
    return safe[:80] or "Lesson"

def has_real_vocab_text(frame):
    """Skip intro/title slides with big images and little text"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    center = gray[int(h*0.2):int(h*0.8), int(w*0.2):int(w*0.8)]
    text_pixels = np.sum(center < 120)  # dark pixels = text
    total = center.size
    return text_pixels > total * 0.025  # at least 2.5% text → real vocab slide

url = input("\nPaste playlist URL:\n> ").strip()

ydl_opts = {
    'format': 'best[height<=720][ext=mp4]',
    'outtmpl': 'VIDEO.mp4',
    'quiet': True,
    'merge_output_format': 'mp4',
}

os.makedirs("N4_PERFECT", exist_ok=True)

with yt_dlp.YoutubeDL({'quiet': True}) as ydl_info:
    info = ydl_info.extract_info(url, download=False)
    videos = info['entries']

print(f"\n{len(videos)} videos — extracting ONLY real vocabulary slides...\n")

for i, video in enumerate(videos, 1):
    title = video['title']
    folder = f"N4_PERFECT/{i:02d}_{english_folder(title)}"
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
    interval = int(fps * 1.2)  # every ~1.2 seconds
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

        # NEW: Skip slides with almost no text (intro, thank you, big pictures)
        if not has_real_vocab_text(frame):
            continue

        # Crop center to ignore cursor/YouTube bar
        h, w = frame.shape[:2]
        crop = frame[int(h*0.15):int(h*0.85), int(w*0.15):int(w*0.85)]
        hsh = imagehash.average_hash(Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)))

        # Only save if it's different from last 12 slides
        if all(hsh - old >= 7 for old in seen[-12:]):
            seen.append(hsh)
            saved += 1
            path = os.path.join(folder, f"{saved:03d}.jpg")
            ok = cv2.imwrite(path, frame)
            print(f"   saved {saved} - real vocab slide" if ok else f"   FAILED {saved}")

    cap.release()
    if os.path.exists("VIDEO.mp4"):
        os.remove("VIDEO.mp4")

    print(f"   {saved} PERFECT vocabulary slides saved\n")

print("COMPLETELY DONE!")
print("Only real Japanese + Bangla vocabulary slides → N4_PERFECT folder")
os.startfile("N4_PERFECT")
input("\nPress Enter to exit...")