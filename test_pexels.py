import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    api_key = os.getenv('PEXELS_API_KEY')
    print(f"Pexels API Key found: {'Yes' if api_key else 'No'}")
    if api_key:
        print(f"API Key starts with: {api_key[:10]}...")
    else:
        raise ValueError("No Pexels API key found in environment")
    
    # Import Pexels functions after we confirm we have the key
    from shortGPT.api_utils.pexels_api import search_videos, getBestVideo
    
    # Try to search for a video
    print("\nSearching for test video...")
    search_term = "nature"
    results = search_videos(search_term)
    
    if results and 'videos' in results and len(results['videos']) > 0:
        video = results['videos'][0]
        print(f"\nFound video:")
        print(f"Title: {video.get('user', {}).get('name', 'No title')}")
        print(f"Duration: {video.get('duration', 'Unknown')} seconds")
        print(f"URL: {video.get('url', 'No URL')}")
        
        # Try to get best video
        print("\nTrying to get best video URL...")
        best_url = getBestVideo(search_term)
        if best_url:
            print(f"Best video URL: {best_url}")
        else:
            print("No best video found")
    else:
        print("No videos found")

except Exception as e:
    print(f"Error: {str(e)}")
    if hasattr(e, 'response'):
        print(f"Response status: {e.response.status_code}")
        print(f"Response text: {e.response.text}")