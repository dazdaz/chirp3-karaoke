#!/usr/bin/env python3.13
"""
Karaoke Maker - Python version using audio-separator
Create karaoke tracks with full instrumental, guide vocals, or reduced vocals
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KaraokeMaker:
    def __init__(self, vocal_reduction=0.7):
        self.vocal_reduction = vocal_reduction  # 0.0 = no reduction, 1.0 = full removal
        self.setup_models()
        self.check_installation()
    
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
            for audio_file in audio_files:
                self._process_single_instrumental(audio_file, output_dir)
        else:
            logger.error(f"Input path does not exist: {input_path}")
    
    def _process_single_instrumental(self, input_file, output_dir):
        """Process a single file to create instrumental"""
        logger.info(f"Processing: {input_file.name}")
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
                    logger.info(f"✅ Created instrumental: {output_file}")
                    return
            
            logger.warning(f"No instrumental file found in output for {input_file.name}")
            
        except Exception as e:
            logger.error(f"Error processing {input_file.name}: {str(e)}")
            sys.exit(1)
    
    def process_reduced_vocals(self, input_path, output_dir):
        """Process file(s) to create reduced vocals versions"""
        input_path = Path(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
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
            for audio_file in audio_files:
                self._process_single_reduced_vocals(audio_file, output_dir)
        else:
            logger.error(f"Input path does not exist: {input_path}")
    
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
            
        except Exception as e:
            logger.error(f"Error processing {input_file.name}: {str(e)}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Create karaoke tracks using audio-separator")
    parser.add_argument("-i", "--input", required=True, help="Input file or directory")
    parser.add_argument("-o", "--output", required=True, help="Output directory")
    parser.add_argument("-t", "--type", choices=["instrumental", "reduced-vocals"], 
                       default="instrumental", help="Type of processing")
    parser.add_argument("-r", "--reduction", type=float, default=1.0,
                       help="Vocal reduction level (0.0=no reduction, 1.0=full removal, default=1.0)")
    
    args = parser.parse_args()
    
    # Validate reduction level
    if not 0.0 <= args.reduction <= 1.0:
        logger.error("Reduction level must be between 0.0 and 1.0")
        sys.exit(1)
    
    # Create karaoke maker instance with specified reduction level
    karaoke_maker = KaraokeMaker(vocal_reduction=args.reduction)
    
    # Process based on type
    if args.type == "instrumental":
        logger.info(f"🎵 Creating instrumental tracks (reduction: {args.reduction:.0%})...")
        karaoke_maker.process_instrumental(args.input, args.output)
        logger.info("✅ Instrumental processing completed!")
    else:
        logger.info(f"🎤 Creating reduced vocals tracks (reduction: {args.reduction:.0%})...")
        karaoke_maker.process_reduced_vocals(args.input, args.output)
        logger.info("✅ Reduced vocals processing completed!")
    
    logger.info(f"📁 Output saved to: {args.output}")

if __name__ == "__main__":
    main()