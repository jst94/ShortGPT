from shortGPT.engine.facts_short_engine import FactsShortEngine
import cv2
from shortGPT.config.asset_db import AssetDatabase
from shortGPT.config.languages import Language
from shortGPT.audio.audio_duration import get_asset_duration
from shortGPT.editing_utils.handle_videos import extract_random_clip_from_video
from shortGPT.editing_framework.editing_engine import (EditingEngine, EditingStep)
import os

class CustomFactsShortEngine(FactsShortEngine):
    def __init__(self, voiceModule, facts_type="", background_video_name="minecraft_background", 
                 background_music_name=None, short_id="", num_images=0, watermark=None, 
                 language=Language.ENGLISH):
        # Set basic attributes before parent init
        self._background_video_name = background_video_name
        self._background_music_name = background_music_name
        self._background_video_path = None
        self._background_video_duration = None
        self._script_override = None
        
        # Call parent's init
        super().__init__(
            voiceModule=voiceModule,
            facts_type=facts_type,
            background_video_name=background_video_name,
            background_music_name=background_music_name if background_music_name else "",
            short_id=short_id,
            num_images=num_images,
            watermark=watermark,
            language=language
        )
        
        # Initialize video properties after parent init
        if background_video_name:
            self._init_video_properties()

    def set_script(self, script):
        """Method to override the script generation"""
        self._script_override = script
        self._db_script = script

    def _generateScript(self):
        """Override script generation to use pre-written script if available"""
        if self._script_override:
            print("\nUsing pre-written script")
            self._db_script = self._script_override
            return
        
        # If no override, call parent's implementation
        super()._generateScript()

    def _init_video_properties(self):
        """Initialize video properties including duration"""
        # Get video path from asset database
        df = AssetDatabase.get_df()
        video_entry = df[df['name'] == self._background_video_name].iloc[0]
        video_path = video_entry['link']
        
        print(f"\nInitializing video properties for: {video_path}")
        
        # Get video duration using OpenCV
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Failed to open video file: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count/fps
        cap.release()
        
        # Set properties
        self._background_video_path = video_path
        self._background_video_duration = duration
        self._background_video_url = video_path  # Required by parent class
        
        print(f"Video duration: {duration:.2f} seconds")
        print(f"Video FPS: {fps}")
        print(f"Frame count: {frame_count}")

    def _chooseBackgroundVideo(self):
        """Override to use pre-initialized video properties"""
        print("\nUsing pre-initialized video properties:")
        print(f"Path: {self._background_video_path}")
        print(f"Duration: {self._background_video_duration}")

    def _chooseBackgroundMusic(self):
        """Override to make background music optional"""
        if not self._background_music_name:
            print("\nSkipping background music (not specified)")
            self._background_music_url = None
            return
        
        print(f"\nAttempting to use background music: {self._background_music_name}")
        self._background_music_url = AssetDatabase.get_asset_link(self._background_music_name)

    def _prepareBackgroundAssets(self):
        """Override to handle background assets properly"""
        print("\nPreparing background assets...")
        
        # Get voiceover duration if not already set
        if not hasattr(self, '_db_voiceover_duration') or not self._db_voiceover_duration:
            print("Getting voiceover duration...")
            self._db_voiceover_duration = get_asset_duration(self._db_audio_path, isVideo=False)[1]
            print(f"Voiceover duration: {self._db_voiceover_duration:.2f} seconds")
        
        # Extract random clip from background video
        if not hasattr(self, '_db_background_trimmed') or not self._db_background_trimmed:
            print("Preparing background video clip...")
            self._db_background_trimmed = extract_random_clip_from_video(
                self._background_video_path,  # Use local path instead of URL
                self._background_video_duration,
                self._db_voiceover_duration,
                self.dynamicAssetDir + "clipped_background.mp4"
            )
            print(f"Background clip prepared: {self._db_background_trimmed}")

    def _editAndRenderShort(self):
        """Override to handle video rendering properly"""
        outputPath = self.dynamicAssetDir + "rendered_video.mp4"
        
        if not os.path.exists(outputPath):
            print("\nStarting video rendering...")
            videoEditor = EditingEngine()
            
            # Add voiceover
            videoEditor.addEditingStep(
                EditingStep.ADD_VOICEOVER_AUDIO,
                {'url': self._db_audio_path}
            )

            # Add background video
            videoEditor.addEditingStep(
                EditingStep.CROP_1920x1080,
                {'url': self._db_background_trimmed}
            )

            # Add subscribe animation if available
            try:
                subscribe_url = AssetDatabase.get_asset_link('subscribe animation')
                videoEditor.addEditingStep(
                    EditingStep.ADD_SUBSCRIBE_ANIMATION,
                    {'url': subscribe_url}
                )
            except:
                print("Subscribe animation not found, skipping...")

            # Add watermark if specified
            if self._db_watermark:
                videoEditor.addEditingStep(
                    EditingStep.ADD_WATERMARK,
                    {'text': self._db_watermark}
                )

            # Add captions
            caption_type = (EditingStep.ADD_CAPTION_SHORT_ARABIC 
                          if self._db_language == Language.ARABIC.value 
                          else EditingStep.ADD_CAPTION_SHORT)
            
            for timing, text in self._db_timed_captions:
                videoEditor.addEditingStep(
                    caption_type,
                    {
                        'text': text.upper(),
                        'set_time_start': timing[0],
                        'set_time_end': timing[1]
                    }
                )

            print("\nVideo editing schema:")
            print(videoEditor.dumpEditingSchema())
            
            print("\nRendering final video...")
            videoEditor.renderVideo(
                outputPath,
                logger=self.logger if self.logger is not self.default_logger else None
            )

        self._db_video_path = outputPath