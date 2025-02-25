import os
import yt_dlp
from shortGPT.config.asset_db import AssetDatabase, AssetType

def download_youtube_video(url, output_path):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': False,
        'no_warnings': True,
        'merge_output_format': 'mp4'
    }
    
    print("Available formats:")
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get('formats', [])
        for f in formats:
            print(f"Format {f.get('format_id', 'N/A')}: {f.get('ext', 'N/A')} - {f.get('height', 'N/A')}p")
    
    print("\nDownloading video...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_path

try:
    # Create public directory if it doesn't exist
    if not os.path.exists('public'):
        os.makedirs('public')
    
    # Download Minecraft jumping circuit video
    video_url = "https://www.youtube.com/watch?v=Pt5_GSKIWQM"
    output_path = "public/minecraft_background.mp4"
    
    print(f"Downloading video from {video_url}...")
    downloaded_path = download_youtube_video(video_url, output_path)
    print(f"Video downloaded to {downloaded_path}")
    
    # Add to asset database
    AssetDatabase.add_local_asset(
        "minecraft_background", 
        AssetType.BACKGROUND_VIDEO, 
        downloaded_path
    )
    print("Added video to asset database")
    
    # Print available assets
    print("\nAvailable assets in database:")
    print(AssetDatabase.get_df())
    
except Exception as e:
    print(f"Error occurred: {str(e)}")
    if hasattr(e, 'stderr'):
        print(f"Error details: {e.stderr}")