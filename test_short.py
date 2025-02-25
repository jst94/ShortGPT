import os
import shutil
from dotenv import load_dotenv
from shortGPT.database.content_database import ContentDatabase
from shortGPT.audio.eleven_voice_module import ElevenLabsVoiceModule
from shortGPT.config.languages import Language
from shortGPT.config.asset_db import AssetDatabase
from custom_engine import CustomFactsShortEngine

# Load environment variables
load_dotenv()

# Super short script about black holes
SAMPLE_SCRIPT = """Amazing fact: A black hole the size of a penny would weigh as much as Earth!"""

def create_output_dir():
    """Create output directory if it doesn't exist"""
    if not os.path.exists('output'):
        os.makedirs('output')

try:
    # Create output directory
    create_output_dir()
    
    # Initialize content database
    print("Initializing content database...")
    content_db = ContentDatabase()
    
    # Setup voice module
    api_key = os.getenv('ELEVENLABS_API_KEY')
    print("Initializing ElevenLabs voice module...")
    voice_module = ElevenLabsVoiceModule(api_key=api_key, voiceName="Sarah")
    
    # Print available assets
    print("\nAvailable assets in database:")
    print(AssetDatabase.get_df())
    
    print("\nInitializing CustomFactsShortEngine...")
    engine = CustomFactsShortEngine(
        voiceModule=voice_module,
        facts_type="space",  # Type of facts
        background_video_name="minecraft_background",  # Use our downloaded video
        background_music_name=None,  # No background music
        short_id="",  # Let it generate a new ID
        num_images=0,  # Disable images to simplify the process
        watermark=None,  # No watermark
        language=Language.ENGLISH
    )
    
    # Set the pre-written script
    engine.set_script(SAMPLE_SCRIPT)
    
    print("\nGenerating short video about black holes...")
    # Generate content
    for step_num, step_info in engine.makeContent():
        print(f"\nStep {step_num}: {step_info}")
    
    # Copy the rendered video to the output directory
    if hasattr(engine, '_db_video_path') and engine._db_video_path:
        output_path = os.path.join('output', 'black_hole_facts_short.mp4')
        shutil.copy2(engine._db_video_path, output_path)
        print(f"\nVideo saved to: {output_path}")
    else:
        print("\nWarning: Video path not found in engine attributes")
        # Try to find the video in the last used assets directory
        last_dir = sorted(os.listdir('.editing_assets/facts_shorts_assets/'))[-1]
        video_path = f".editing_assets/facts_shorts_assets/{last_dir}/rendered_video.mp4"
        if os.path.exists(video_path):
            output_path = os.path.join('output', 'black_hole_facts_short.mp4')
            shutil.copy2(video_path, output_path)
            print(f"\nVideo found and saved to: {output_path}")
        
except Exception as e:
    print(f"\nError occurred: {str(e)}")
    if hasattr(e, 'response'):
        print(f"Response status: {e.response.status_code}")
        print(f"Response text: {e.response.text}")