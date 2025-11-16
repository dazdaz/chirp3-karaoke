#!/usr/bin/env python3.13
"""
Karaoke Maker - Python version using audio-separator
Create karaoke tracks with adjustable vocal reduction levels (0.0-1.0)
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path
import logging
import time
import signal
import tempfile
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KaraokeMaker:
    def __init__(self, vocal_reduction=0.7):
        self.vocal_reduction = vocal_reduction  # 0.0 = no reduction, 1.0 = full removal
        self.temp_dirs = []  # Track temporary directories for cleanup
        self.current_output_file = None
        self.setup_models()
        self.setup_signal_handlers()
        self.check_installation()
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful cleanup"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl-C and termination signals"""
        logger.info(f"\n🛑 Received signal {signum}, cleaning up...")
        self.cleanup()
        logger.info("👋 Goodbye!")
        sys.exit(0)
    
    def cleanup(self):
        """Clean up temporary files and directories"""
        for temp_dir in self.temp_dirs:
            try:
                if temp_dir.exists():
                    logger.info(f"🧹 Cleaning up temporary directory: {temp_dir}")
                    shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"⚠️  Could not clean up {temp_dir}: {e}")
        
        # Clean up any partial output files
        try:
            if hasattr(self, 'current_output_file') and self.current_output_file:
                if self.current_output_file.exists():
                    logger.info(f"🧹 Removing partial output file: {self.current_output_file}")
                    self.current_output_file.unlink()
        except Exception as e:
            logger.warning(f"⚠️  Could not clean up partial output file: {e}")
    
    def create_temp_dir(self):
        """Create a temporary directory and track it for cleanup"""
        temp_dir = Path(tempfile.mkdtemp(prefix="karaoke_maker_"))
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def setup_models(self):
        """Configure the models for different separation types"""
        # Default model for instrumental separation
        self.instrumental_model = "Demucs_v4_hybrid"
        # Model for vocal extraction
        self.vocal_model = "Kim_Vocal_2"
    
    def check_installation(self):
        """Check if audio-separator is properly installed"""
        try:
            from audio_separator.separator import Separator
            logger.info("Using audio-separator for high-quality vocal removal")
            self.separator = Separator()
            return True
        except ImportError as e:
            logger.error(f"audio-separator is required but not found: {e}")
            logger.error("Install with: pip install audio-separator")
            logger.error("Or install with: pip install --break-system-packages audio-separator")
            sys.exit(1)
    
    def check_ffmpeg(self):
        """Check if ffmpeg is available"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("ffmpeg available for basic vocal reduction")
                return True
        except FileNotFoundError:
            logger.error("ffmpeg not found. Install with: brew install ffmpeg")
            return False
    
    def process_instrumental(self, input_path, output_dir):
        """Process file(s) to create instrumental versions"""
        input_path = Path(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        try:
            if input_path.is_file():
                # Process single file
                self._process_single_instrumental(input_path, output_dir)
            elif input_path.is_dir():
                # Process all audio files in directory
                audio_files = list(input_path.glob("*.mp3")) + list(input_path.glob("*.flac")) + \
                             list(input_path.glob("*.MP3")) + list(input_path.glob("*.FLAC")) + \
                             list(input_path.glob("*.wav")) + list(input_path.glob("*.WAV"))
                
                if not audio_files:
                    logger.error(f"No audio files found in {input_path}")
                    return
                
                logger.info(f"Found {len(audio_files)} audio files to process")
                for i, audio_file in enumerate(audio_files, 1):
                    try:
                        logger.info(f"📁 Processing file {i}/{len(audio_files)}")
                        self._process_single_instrumental(audio_file, output_dir)
                    except KeyboardInterrupt:
                        logger.info(f"⏹️  Interrupted while processing {audio_file.name}")
                        logger.info(f"📊 Processed {i-1}/{len(audio_files)} files before interruption")
                        raise
            else:
                logger.error(f"Input path does not exist: {input_path}")
        except KeyboardInterrupt:
            logger.info("🛑 Instrumental processing interrupted by user")
            raise
    
    def _process_single_instrumental(self, input_file, output_dir):
        """Process a single file to create instrumental"""
        logger.info(f"Processing: {input_file.name}")
        self.current_output_file = None
        self._process_with_audio_separator(input_file, output_dir)
    
    def _process_with_audio_separator(self, input_file, output_dir):
        """Process using audio-separator for high quality"""
        try:
            # Configure separator for instrumental output
            self.separator.model_name = self.instrumental_model
            self.separator.output_dir = str(output_dir)
            self.separator.output_format = "FLAC"
            
            # Load the model
            logger.info(f"Loading model: {self.instrumental_model}")
            self.separator.load_model()
            
            # Apply vocal reduction if specified
            if self.vocal_reduction < 1.0:
                # For partial reduction, we'll need to mix the instrumental back with original
                # This is a limitation of audio-separator - it does full separation
                logger.info(f"Note: audio-separator performs full vocal removal. For partial reduction ({self.vocal_reduction:.0%}), consider post-processing.")
            
            # Separate the audio
            output_files = self.separator.separate(str(input_file))
            
            # The instrumental file is typically named with "_Instrumental" suffix
            for output_file in output_files:
                if "Instrumental" in output_file:
                    self.current_output_file = Path(output_file)
                    logger.info(f"✅ Created instrumental: {output_file}")
                    return
            
            logger.warning(f"No instrumental file found in output for {input_file.name}")
            
        except KeyboardInterrupt:
            logger.info("⏹️  Processing interrupted by user")
            raise
        except Exception as e:
            logger.error(f"Error processing {input_file.name}: {str(e)}")
            sys.exit(1)
        finally:
            self.current_output_file = None
    
    def process_reduced_vocals(self, input_path, output_dir):
        """Process file(s) to create reduced vocals versions"""
        input_path = Path(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        try:
            if input_path.is_file():
                # Process single file
                self._process_single_reduced_vocals(input_path, output_dir)
            elif input_path.is_dir():
                # Process all audio files in directory
                audio_files = list(input_path.glob("*.mp3")) + list(input_path.glob("*.flac")) + \
                             list(input_path.glob("*.MP3")) + list(input_path.glob("*.FLAC")) + \
                             list(input_path.glob("*.wav")) + list(input_path.glob("*.WAV"))
                
                if not audio_files:
                    logger.error(f"No audio files found in {input_path}")
                    return
                
                logger.info(f"Found {len(audio_files)} audio files to process")
                for i, audio_file in enumerate(audio_files, 1):
                    try:
                        logger.info(f"📁 Processing file {i}/{len(audio_files)}")
                        self._process_single_reduced_vocals(audio_file, output_dir)
                    except KeyboardInterrupt:
                        logger.info(f"⏹️  Interrupted while processing {audio_file.name}")
                        logger.info(f"📊 Processed {i-1}/{len(audio_files)} files before interruption")
                        raise
            else:
                logger.error(f"Input path does not exist: {input_path}")
        except KeyboardInterrupt:
            logger.info("🛑 Reduced vocals processing interrupted by user")
            raise
    
    def _process_single_reduced_vocals(self, input_file, output_dir):
        """Process a single file to create reduced vocals"""
        logger.info(f"Processing: {input_file.name}")
        self._process_reduced_vocals_with_audio_separator(input_file, output_dir)
    
    def _process_reduced_vocals_with_audio_separator(self, input_file, output_dir):
        """Process reduced vocals using audio-separator"""
        try:
            # First extract vocals
            self.separator.model_name = self.vocal_model
            self.separator.output_dir = str(output_dir)
            self.separator.output_format = "FLAC"
            
            # Load the model
            logger.info(f"Loading model: {self.vocal_model}")
            self.separator.load_model()
            
            vocal_files = self.separator.separate(str(input_file))
            
            # Find the vocal file
            vocal_file = None
            for file in vocal_files:
                if "Vocals" in file:
                    vocal_file = file
                    break
            
            if not vocal_file:
                logger.warning(f"No vocal file found for {input_file.name}")
                return
            
            # For reduced vocals, we could mix the vocal file back with the instrumental
            # at a reduced volume. For now, we'll output the vocals separately
            logger.info(f"✅ Extracted vocals for reduced processing: {vocal_file}")
            
            # Also create instrumental for mixing reference
            self.separator.model_name = self.instrumental_model
            logger.info(f"Loading model: {self.instrumental_model}")
            self.separator.load_model()
            instrumental_files = self.separator.separate(str(input_file))
            
            for file in instrumental_files:
                if "Instrumental" in file:
                    logger.info(f"✅ Created instrumental reference: {file}")
                    break
            
        except KeyboardInterrupt:
            logger.info("⏹️  Processing interrupted by user")
            raise
        except Exception as e:
            logger.error(f"Error processing {input_file.name}: {str(e)}")
            sys.exit(1)
    
    def copy_original_audio(self, input_path, output_dir):
        """Copy original audio files without processing when reduction is 0.0"""
        input_path = Path(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        try:
            if input_path.is_file():
                # Copy single file
                self._copy_single_file(input_path, output_dir)
            elif input_path.is_dir():
                # Copy all audio files in directory
                audio_files = list(input_path.glob("*.mp3")) + list(input_path.glob("*.flac")) + \
                             list(input_path.glob("*.MP3")) + list(input_path.glob("*.FLAC")) + \
                             list(input_path.glob("*.wav")) + list(input_path.glob("*.WAV"))
                
                if not audio_files:
                    logger.error(f"No audio files found in {input_path}")
                    return
                
                logger.info(f"Found {len(audio_files)} audio files to copy")
                for i, audio_file in enumerate(audio_files, 1):
                    try:
                        logger.info(f"📁 Copying file {i}/{len(audio_files)}")
                        self._copy_single_file(audio_file, output_dir)
                    except KeyboardInterrupt:
                        logger.info(f"⏹️  Interrupted while copying {audio_file.name}")
                        logger.info(f"📊 Copied {i-1}/{len(audio_files)} files before interruption")
                        raise
            else:
                logger.error(f"Input path does not exist: {input_path}")
        except KeyboardInterrupt:
            logger.info("🛑 Audio copying interrupted by user")
            raise
    
    def _copy_single_file(self, input_file, output_dir):
        """Copy a single file to the output directory"""
        try:
            import shutil
            output_file = output_dir / input_file.name
            shutil.copy2(input_file, output_file)
            logger.info(f"✅ Copied: {input_file.name}")
        except Exception as e:
            logger.error(f"Error copying {input_file.name}: {str(e)}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Create high-quality karaoke tracks using AI-powered vocal separation with audio-separator. "
                    "Process individual files or entire directories with adjustable vocal reduction levels.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i song.flac -o output/ -r 1.0    # Create pure instrumental
  %(prog)s -i album/ -o karaoke/ -r 0.8      # Heavy vocal reduction
  %(prog)s -i album/ -o karaoke/ -r 0.3      # Light vocal reduction
  %(prog)s -i "Beats [96kHz · 24bit]/" -o output/ -r 0.0  # Keep original audio

Vocal Reduction Levels:
  -r 1.0  - Full instrumental (remove all vocals for pure karaoke)
  -r 0.7  - Heavy reduction (karaoke with faint guide vocals)
  -r 0.5  - Moderate reduction (background vocals audible)
  -r 0.3  - Light reduction (practice with clear vocals)
  -r 0.0  - No reduction (original audio unchanged)

Note: audio-separator performs full separation. Partial reduction levels
create both vocal and instrumental tracks for post-processing/mixing.
        """)
    
    parser.add_argument("-i", "--input", required=True,
                       help="Input file or directory containing audio files. "
                            "Supports FLAC, MP3, and WAV formats. "
                            "Can be a single file or entire directory for batch processing.")
    
    parser.add_argument("-o", "--output", required=True,
                       help="Output directory where processed files will be saved. "
                            "Directory will be created if it doesn't exist.")
    
    parser.add_argument("-r", "--reduction", type=float, default=1.0,
                       help="Vocal reduction level (0.0-1.0, default: 1.0):\n"
                            "  1.0 = Full removal (pure instrumental)\n"
                            "  0.7 = Heavy reduction (karaoke with guide vocals)\n"
                            "  0.5 = Moderate reduction (background vocals)\n"
                            "  0.3 = Light reduction (practice vocals)\n"
                            "  0.0 = No reduction (original audio)\n"
                            "Note: audio-separator performs full separation. "
                            "For partial reduction, consider post-processing the outputs.")
    
    args = parser.parse_args()
    
    # Validate reduction level
    if not 0.0 <= args.reduction <= 1.0:
        logger.error("Reduction level must be between 0.0 and 1.0")
        sys.exit(1)
    
    # Create karaoke maker instance with specified reduction level
    karaoke_maker = KaraokeMaker(vocal_reduction=args.reduction)
    
    try:
        # Process based on reduction level
        if args.reduction >= 0.9:
            logger.info(f"🎵 Creating instrumental tracks (reduction: {args.reduction:.0%})...")
            karaoke_maker.process_instrumental(args.input, args.output)
            logger.info("✅ Instrumental processing completed!")
        elif args.reduction > 0.0:
            logger.info(f"🎤 Creating reduced vocals tracks (reduction: {args.reduction:.0%})...")
            karaoke_maker.process_reduced_vocals(args.input, args.output)
            logger.info("✅ Reduced vocals processing completed!")
        else:
            logger.info(f"🎶 Copying original audio files (no reduction: {args.reduction:.0%})...")
            karaoke_maker.copy_original_audio(args.input, args.output)
            logger.info("✅ Audio copying completed!")
        
        logger.info(f"📁 Output saved to: {args.output}")
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Processing interrupted by user")
        logger.info("🧹 Cleaning up temporary files...")
        karaoke_maker.cleanup()
        logger.info("👋 Goodbye!")
        sys.exit(130)  # Standard exit code for Ctrl-C
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        karaoke_maker.cleanup()
        sys.exit(1)
    finally:
        # Always cleanup on exit
        karaoke_maker.cleanup()

if __name__ == "__main__":
    main()
