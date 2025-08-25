#!/usr/bin/env python3
"""
Simple script to check video file paths and existence
Run this to see what's wrong with the video loading
"""

import os
import sys
from pathlib import Path

print("🎬 Video File Checker")
print("=" * 40)

# Get current directory
cwd = Path(os.getcwd())
print(f"Current directory: {cwd}")

# Check for stimuli directory
stimuli_dir = cwd / "stimuli"
print(f"Stimuli directory: {stimuli_dir}")
print(f"Stimuli exists: {stimuli_dir.exists()}")

if stimuli_dir.exists():
    # Check videos directory
    videos_dir = stimuli_dir / "videos"
    print(f"Videos directory: {videos_dir}")
    print(f"Videos exists: {videos_dir.exists()}")
    
    if videos_dir.exists():
        print(f"\n📁 Files in videos directory:")
        try:
            all_files = list(videos_dir.glob("*"))
            if all_files:
                for file_path in sorted(all_files):
                    if file_path.is_file():
                        size_mb = file_path.stat().st_size / (1024*1024)
                        print(f"   ✅ {file_path.name} ({size_mb:.1f} MB)")
                    else:
                        print(f"   📁 {file_path.name}/ (directory)")
            else:
                print("   ❌ No files found in videos directory")
        except Exception as e:
            print(f"   ❌ Error listing files: {e}")
    
    # Check audio directory too
    audio_dir = stimuli_dir / "audio"
    print(f"\n🎵 Audio directory: {audio_dir}")
    print(f"Audio exists: {audio_dir.exists()}")
    
    if audio_dir.exists():
        print(f"📁 Files in audio directory:")
        try:
            audio_files = list(audio_dir.glob("*.wav"))
            if audio_files:
                for file_path in sorted(audio_files):
                    size_kb = file_path.stat().st_size / 1024
                    print(f"   ✅ {file_path.name} ({size_kb:.1f} KB)")
            else:
                print("   ❌ No .wav files found in audio directory")
        except Exception as e:
            print(f"   ❌ Error listing audio files: {e}")

# Expected video files
expected_videos = [
    'positive_clip.mp4',
    'positive_clip2.mp4', 
    'negative_clip.mp4',
    'negative_clip2.mp4',
    'neutral_clip.mp4',
    'repair_clip.mp4',
    'repair_clip_animal.mp4'
]

print(f"\n🔍 Expected video files:")
videos_dir = stimuli_dir / "videos"
for video_name in expected_videos:
    video_path = videos_dir / video_name
    exists = video_path.exists()
    status = "✅" if exists else "❌"
    print(f"   {status} {video_name}")
    if exists:
        size_mb = video_path.stat().st_size / (1024*1024)
        print(f"      Size: {size_mb:.1f} MB")
        print(f"      Full path: {video_path}")

print(f"\n🔍 Expected audio files:")
audio_dir = stimuli_dir / "audio"
expected_audio = ['positive_music.wav', 'negative_music.wav']
for audio_name in expected_audio:
    audio_path = audio_dir / audio_name
    exists = audio_path.exists()
    status = "✅" if exists else "❌"
    print(f"   {status} {audio_name}")
    if exists:
        size_kb = audio_path.stat().st_size / 1024
        print(f"      Size: {size_kb:.1f} KB")
        print(f"      Full path: {audio_path}")

print(f"\n" + "=" * 40)
print("Check complete. If files show as missing, either:")
print("1. The files don't exist and need to be added")
print("2. The filenames don't match what's expected")
print("3. There's a permissions or path issue")
