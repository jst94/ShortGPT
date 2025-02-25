import tkinter as tk
from tkinter import ttk
import os
from dotenv import load_dotenv
from shortGPT.database.content_database import ContentDatabase
from shortGPT.audio.eleven_voice_module import ElevenLabsVoiceModule
from shortGPT.config.languages import Language
from shortGPT.config.asset_db import AssetDatabase
from custom_engine import CustomFactsShortEngine
import threading

class ShortGPTGui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ShortGPT Video Creator")
        self.root.geometry("600x800")
        
        # Load environment variables
        load_dotenv()
        
        # Initialize content database
        self.content_db = ContentDatabase()
        
        # Initialize voice module with default voice
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        self.default_voice = "Sarah"
        self.voice_module = ElevenLabsVoiceModule(api_key=self.api_key, voiceName=self.default_voice)
        
        self.create_widgets()
    
    def create_widgets(self):
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="ShortGPT Video Creator", font=('Helvetica', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Script input
        ttk.Label(main_frame, text="Enter your script:", font=('Helvetica', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.script_text = tk.Text(main_frame, height=10, width=60, wrap=tk.WORD)
        self.script_text.grid(row=2, column=0, columnspan=2, pady=5, padx=5)
        self.script_text.insert('1.0', "Amazing fact: A day on Venus is longer than its year!")
        
        # Background video selection
        ttk.Label(main_frame, text="Background video:", font=('Helvetica', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.bg_video_var = tk.StringVar()
        self.bg_video_combo = ttk.Combobox(main_frame, textvariable=self.bg_video_var, width=40)
        self.bg_video_combo['values'] = self.get_background_videos()
        if self.bg_video_combo['values']:
            self.bg_video_combo.set(self.bg_video_combo['values'][0])
        self.bg_video_combo.grid(row=3, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Voice selection
        ttk.Label(main_frame, text="Voice:", font=('Helvetica', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.voice_var = tk.StringVar(value=self.default_voice)
        self.voice_combo = ttk.Combobox(main_frame, textvariable=self.voice_var, width=40)
        self.voice_combo['values'] = ['Sarah', 'Josh', 'Rachel', 'Adam']
        self.voice_combo.grid(row=4, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Language selection
        ttk.Label(main_frame, text="Language:", font=('Helvetica', 10, 'bold')).grid(row=5, column=0, sticky=tk.W, pady=5)
        self.lang_var = tk.StringVar(value=Language.ENGLISH.value)
        self.lang_combo = ttk.Combobox(main_frame, textvariable=self.lang_var, width=40)
        self.lang_combo['values'] = [lang.value for lang in Language]
        self.lang_combo.grid(row=5, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Progress
        self.progress_var = tk.StringVar(value="Ready to generate video...")
        status_label = ttk.Label(main_frame, textvariable=self.progress_var, font=('Helvetica', 10))
        status_label.grid(row=6, column=0, columnspan=2, pady=10)
        
        # Generate button
        style = ttk.Style()
        style.configure('Generate.TButton', font=('Helvetica', 10, 'bold'))
        self.generate_btn = ttk.Button(
            main_frame,
            text="Generate Video",
            style='Generate.TButton',
            command=self.generate_video
        )
        self.generate_btn.grid(row=7, column=0, columnspan=2, pady=10)
        
        # Progress log
        ttk.Label(main_frame, text="Progress Log:", font=('Helvetica', 10, 'bold')).grid(row=8, column=0, sticky=tk.W, pady=5)
        self.log_text = tk.Text(main_frame, height=15, width=60, wrap=tk.WORD, state='disabled')
        self.log_text.grid(row=9, column=0, columnspan=2, pady=5, padx=5)
        
        # Scrollbar for log
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=9, column=2, sticky=(tk.N, tk.S))
        self.log_text['yscrollcommand'] = scrollbar.set
    
    def get_background_videos(self):
        df = AssetDatabase.get_df()
        videos = df[df['type'] == 'background video']
        return videos['name'].tolist()
    
    def log(self, message):
        self.log_text.configure(state='normal')
        self.log_text.insert('end', f"{message}\n")
        self.log_text.see('end')
        self.log_text.configure(state='disabled')
        self.root.update()
    
    def generate_video(self):
        # Disable generate button
        self.generate_btn.configure(state='disabled')
        self.progress_var.set("Generating video...")
        
        # Start generation in a separate thread
        thread = threading.Thread(target=self._generate_video_thread)
        thread.daemon = True
        thread.start()
    
    def _generate_video_thread(self):
        try:
            # Get values from GUI
            script = self.script_text.get('1.0', 'end').strip()
            bg_video = self.bg_video_var.get()
            voice = self.voice_var.get()
            language = self.lang_var.get()
            
            self.log(f"Initializing with:")
            self.log(f"- Background video: {bg_video}")
            self.log(f"- Voice: {voice}")
            self.log(f"- Language: {language}")
            
            # Update voice module with selected voice
            self.voice_module = ElevenLabsVoiceModule(api_key=self.api_key, voiceName=voice)
            
            # Initialize engine
            engine = CustomFactsShortEngine(
                voiceModule=self.voice_module,
                facts_type="space",
                background_video_name=bg_video,
                background_music_name=None,
                short_id="",
                num_images=0,
                watermark=None,
                language=language
            )
            
            # Set script
            engine.set_script(script)
            
            # Generate content
            self.log("\nStarting video generation...")
            for step_num, step_info in engine.makeContent():
                self.log(f"\nStep {step_num}: {step_info}")
            
            # Copy to output directory
            if hasattr(engine, '_db_video_path') and engine._db_video_path:
                if not os.path.exists('output'):
                    os.makedirs('output')
                output_path = os.path.join('output', 'generated_short.mp4')
                import shutil
                shutil.copy2(engine._db_video_path, output_path)
                self.log(f"\nVideo saved to: {output_path}")
                self.progress_var.set("Video generation complete!")
            
        except Exception as e:
            self.log(f"\nError occurred: {str(e)}")
            self.progress_var.set("Error occurred during generation")
            
        finally:
            # Re-enable generate button
            self.generate_btn.configure(state='normal')
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ShortGPTGui()
    app.run()