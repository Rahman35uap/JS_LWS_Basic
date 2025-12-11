import os
import cv2
from pytubefix import Playlist, YouTube  # ← Changed this line
from PIL import Image
import imagehash

def is_new_slide(current_frame, previous_hashes, threshold=8):
    try:
        hash_obj = imagehash.phash(Image.fromarray(cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)))
        for old_hash in previous_hashes:
            if hash_obj - old_hash < threshold:
                return False, previous_hashes
        previous_hashes.append(hash_obj)
        return True, previous_hashes
    except:
        return True, previous_hashes  # If error, just save the frame

def process_playlist(playlist_url):
    try:
        playlist = Playlist(playlist_url)
        print(f"Found playlist: {playlist.title} ({len(playlist)} videos)")
    except Exception as e:
        print("Playlist error:", e)
        return

    os.makedirs("Japanese_N5_Slides_2", exist_ok=True)

    for idx, video_url in enumerate(playlist.video_urls, 1):
        for attempt in range(3):  # Retry up to 3 times
            try:
                yt = YouTube(video_url, use_oauth=False, allow_oauth_cache=True)
                safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in yt.title)[:60]
                folder = f"Japanese_N5_Slides_2/Lesson_{idx:02d}_{safe_title}"
                os.makedirs(folder, exist_ok=True)

                print(f"\n[{idx}/{len(playlist)}] Downloading: {yt.title}")
                stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                if not stream:
                    stream = yt.streams.get_highest_resolution()
                
                video_path = stream.download(filename="temp_video.mp4", timeout=300)

                cap = cv2.VideoCapture(video_path)
                fps = max(cap.get(cv2.CAP_PROP_FPS), 1)
                hashes = []
                count = 0

                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % int(fps) == 0:
                        is_new, hashes = is_new_slide(frame, hashes)
                        if is_new:
                            count += 1
                            cv2.imwrite(f"{folder}/slide_{count:03d}.png", frame)
                            print(f"  → Saved slide #{count}")

                cap.release()
                os.remove(video_path)
                print(f"Done → {count} slides saved in '{folder}'")
                break  # Success → next video

            except Exception as e:
                print(f"  Attempt {attempt+1} failed: {e}")
                if attempt == 2:
                    print(f"  Skipping this video after 3 tries")
                # Small delay before retry
                import time
                time.sleep(2)
                break

    print("\nALL DONE! Check the 'Japanese_N5_Slides_2' folder")

if __name__ == "__main__":
    url = input("\nPaste your N5 playlist URL: ").strip()
    process_playlist(url)