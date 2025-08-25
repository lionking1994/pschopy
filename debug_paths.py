#!/usr/bin/env python3
"""
Debug script to check path resolution on Mac
Run this to see what paths are being calculated and what files exist.
"""

import os
import sys
from pathlib import Path

print("🔍 Path Debugging Script")
print("=" * 50)

print(f"Current working directory: {os.getcwd()}")
print(f"Script location (__file__): {__file__ if '__file__' in globals() else 'Not available'}")
print(f"Python executable: {sys.executable}")
print(f"Platform: {sys.platform}")

# Check if we're in the right directory
cwd = Path(os.getcwd())
print(f"\n📁 Directory structure check:")
print(f"   Current dir: {cwd}")
print(f"   Current dir exists: {cwd.exists()}")

# Look for key directories
key_dirs = ['config', 'stimuli', 'data', 'scripts']
for dir_name in key_dirs:
    dir_path = cwd / dir_name
    exists = dir_path.exists()
    print(f"   {dir_name}/ exists: {exists}")
    if exists and dir_name == 'stimuli':
        # Check stimuli subdirectories
        stimuli_subdirs = ['videos', 'audio', 'velten_statements']
        for subdir in stimuli_subdirs:
            subdir_path = dir_path / subdir
            subdir_exists = subdir_path.exists()
            print(f"      {subdir}/ exists: {subdir_exists}")
            if subdir_exists and subdir == 'videos':
                # List video files
                try:
                    video_files = list(subdir_path.glob("*.mp4"))
                    print(f"         Video files found: {len(video_files)}")
                    for video_file in video_files:
                        size_mb = video_file.stat().st_size / (1024*1024)
                        print(f"         - {video_file.name} ({size_mb:.1f} MB)")
                except Exception as e:
                    print(f"         Error listing videos: {e}")
            elif subdir_exists and subdir == 'audio':
                # List audio files
                try:
                    audio_files = list(subdir_path.glob("*.wav"))
                    print(f"         Audio files found: {len(audio_files)}")
                    for audio_file in audio_files:
                        size_kb = audio_file.stat().st_size / 1024
                        print(f"         - {audio_file.name} ({size_kb:.1f} KB)")
                except Exception as e:
                    print(f"         Error listing audio: {e}")

# Test config import
print(f"\n⚙️ Config import test:")
try:
    sys.path.append(str(cwd / 'config'))
    import experiment_config as config
    print(f"   ✅ Config imported successfully")
    print(f"   BASE_DIR from config: {config.BASE_DIR}")
    print(f"   STIMULI_DIR from config: {config.STIMULI_DIR}")
    print(f"   VIDEO_DIR from config: {config.VIDEO_DIR}")
    
    # Test specific video file paths
    print(f"\n🎬 Video file path test:")
    for video_key, video_path in config.VIDEO_FILES.items():
        exists = video_path.exists()
        status = "✅" if exists else "❌"
        print(f"   {status} {video_key}: {video_path}")
        
except Exception as e:
    print(f"   ❌ Config import failed: {e}")

print(f"\n" + "=" * 50)
print("Debug complete. Share this output to help diagnose the issue.")
