import cv2
import json
from shortGPT.config.asset_db import AssetDatabase

def print_video_info(video_path):
    print(f"\nChecking video file: {video_path}")
    
    # Try with OpenCV
    print("\nUsing OpenCV:")
    cap = cv2.VideoCapture(video_path)
    if cap.isOpened():
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count/fps
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"Duration: {duration:.2f} seconds")
        print(f"FPS: {fps}")
        print(f"Frame count: {frame_count}")
        print(f"Resolution: {width}x{height}")
    else:
        print(f"Failed to open video file: {video_path}")
    cap.release()

    # Print asset database entry
    print("\nAsset Database entry:")
    df = AssetDatabase.get_df()
    entry = df[df['link'] == video_path]
    print(json.dumps(entry.to_dict('records'), indent=2))

# Get the background video path
print("Available background videos:")
df = AssetDatabase.get_df()
video_entries = df[df['type'] == 'background video']
print(video_entries)

for _, row in video_entries.iterrows():
    if 'local' in row['source']:
        print(f"\nAnalyzing local video: {row['name']}")
        print_video_info(row['link'])