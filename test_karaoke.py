#!/usr/bin/env python3
"""
Test script for karaoke maker functionality
"""

import subprocess
import sys

def test_audio_separator():
    """Test if audio-separator is available"""
    try:
        result = subprocess.run([sys.executable, '-c', 'import audio_separator; print("OK")'], 
                              capture_output=True, text=True)
        return result.returncode == 0 and "OK" in result.stdout
    except:
        return False

def test_karaoke_maker():
    """Test the karaoke maker with a single file"""
    if not test_audio_separator():
        print("❌ audio-separator not available")
        return False
    
    print("✅ audio-separator is available")
    
    # Test with a single file
    cmd = [
        sys.executable, 'karaoke_maker.py',
        '-i', 'Thriller [96kHz · 24bit]/04 - Thriller.flac',
        '-o', 'test_output/',
        '-t', 'instrumental',
        '-r', '1.0'
    ]
    
    print("🧪 Testing karaoke maker with Thriller.flac...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Karaoke maker test passed!")
        return True
    else:
        print("❌ Karaoke maker test failed:")
        print(result.stderr)
        return False

if __name__ == "__main__":
    print("🔧 Testing karaoke maker setup...")
    
    if test_audio_separator():
        print("✅ Dependencies are ready")
        test_karaoke_maker()
    else:
        print("❌ Dependencies not ready")
        print("Install audio-separator with: pipx install audio-separator")