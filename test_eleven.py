import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    api_key = os.getenv('ELEVENLABS_API_KEY')
    print(f"ElevenLabs API Key found: {'Yes' if api_key else 'No'}")
    if api_key:
        print(f"API Key starts with: {api_key[:10]}...")
    else:
        raise ValueError("No ElevenLabs API key found in environment")
    
    # Import ElevenLabs after we confirm we have the key
    from shortGPT.audio.eleven_voice_module import ElevenLabsVoiceModule
    
    # Initialize with the API key and a valid voice name
    voice = ElevenLabsVoiceModule(api_key=api_key, voiceName="Sarah")
    print("\nVoice module initialized successfully")
    
    # Generate test audio with output file
    print("Generating test audio...")
    output_file = "test_audio.mp3"
    success = voice.generate_voice("This is a test of the ElevenLabs API.", output_file)
    
    if success:
        print(f"Audio generated successfully and saved to {output_file}")
    else:
        print("Audio generation failed")

except Exception as e:
    print(f"Error: {str(e)}")
    if hasattr(e, 'response'):
        print(f"Response status: {e.response.status_code}")
        print(f"Response text: {e.response.text}")