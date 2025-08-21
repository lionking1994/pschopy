#!/usr/bin/env python3
"""
Setup Script for PsychoPy Mood Induction + SART Study
Helps users set up the experiment environment and validate installation.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    """Print setup header"""
    print("=" * 70)
    print("PSYCHOPY MOOD INDUCTION + SART EXPERIMENT SETUP")
    print("=" * 70)
    print()

def check_python_version():
    """Check Python version compatibility"""
    print("Checking Python version...")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (compatible)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requires Python 3.8+)")
        return False

def install_requirements():
    """Install Python requirements"""
    print("\nInstalling Python requirements...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\nCreating directories...")
    
    base_dir = Path(__file__).parent
    directories = [
        base_dir / "stimuli" / "videos",
        base_dir / "stimuli" / "audio", 
        base_dir / "stimuli" / "velten_statements",
        base_dir / "data",
        base_dir / "data" / "backups",
        base_dir / "scripts",
        base_dir / "config"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}")
    
    return True

def create_placeholder_files():
    """Create placeholder files for missing stimuli"""
    print("\nChecking stimulus files...")
    
    base_dir = Path(__file__).parent
    
    # Check video files
    video_files = [
        "positive_clip1.mp4",
        "positive_clip2.mp4", 
        "negative_clip.mp4",
        "neutral_clip.mp4",
        "mood_repair.mp4"
    ]
    
    videos_dir = base_dir / "stimuli" / "videos"
    missing_videos = []
    
    for video_file in video_files:
        video_path = videos_dir / video_file
        if video_path.exists():
            print(f"✅ Video found: {video_file}")
        else:
            print(f"⚠️  Video missing: {video_file}")
            missing_videos.append(video_file)
    
    # Check audio files
    audio_files = [
        "positive_music.wav",
        "negative_music.wav"
    ]
    
    audio_dir = base_dir / "stimuli" / "audio"
    missing_audio = []
    
    for audio_file in audio_files:
        audio_path = audio_dir / audio_file
        if audio_path.exists():
            print(f"✅ Audio found: {audio_file}")
        else:
            print(f"⚠️  Audio missing: {audio_file}")
            missing_audio.append(audio_file)
    
    # Create README for stimulus files
    if missing_videos or missing_audio:
        readme_content = """# STIMULUS FILES NEEDED

## Video Files (place in stimuli/videos/):
"""
        for video in missing_videos:
            readme_content += f"- {video}\n"
        
        readme_content += """
## Audio Files (place in stimuli/audio/):
"""
        for audio in missing_audio:
            readme_content += f"- {audio}\n"
        
        readme_content += """
## Notes:
- Video files should be .mp4 format
- Audio files should be .wav format
- The experiment will show placeholders for missing video files
- Missing audio files will be skipped during Velten procedures
- All files are optional for testing purposes
"""
        
        readme_path = base_dir / "stimuli" / "STIMULUS_FILES_NEEDED.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print(f"✅ Created stimulus guide: {readme_path}")
    
    return True

def run_tests():
    """Run the test suite"""
    print("\nRunning test suite...")
    
    test_script = Path(__file__).parent / "scripts" / "test_experiment.py"
    
    if not test_script.exists():
        print("❌ Test script not found")
        return False
    
    try:
        result = subprocess.run([sys.executable, str(test_script)], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 70)
    print("SETUP COMPLETE!")
    print("=" * 70)
    print()
    print("NEXT STEPS:")
    print()
    print("1. ADD STIMULUS FILES:")
    print("   - Copy your video files (.mp4) to: stimuli/videos/")
    print("   - Copy your audio files (.wav) to: stimuli/audio/")
    print("   - See stimuli/STIMULUS_FILES_NEEDED.md for details")
    print()
    print("2. RUN THE EXPERIMENT:")
    print("   python main_experiment_fixed.py    # Recommended (fixed version)")
    print("   python main_experiment.py          # Original version")
    print()
    print("3. ANALYZE DATA:")
    print("   python scripts/data_analyzer.py --combine --data_dir data/")
    print()
    print("4. TEST COMPONENTS:")
    print("   python scripts/test_experiment.py  # Run full test suite")
    print("   python scripts/video_preloader.py  # Test video loading")
    print()
    print("SUPPORT:")
    print("   - Check README.md for detailed documentation")
    print("   - Contact: Nate Speert (nate.speert@my.viu.ca)")
    print()
    print("=" * 70)

def main():
    """Main setup function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Incompatible Python version")
        return False
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed: Could not install requirements")
        return False
    
    # Create directories
    if not create_directories():
        print("\n❌ Setup failed: Could not create directories")
        return False
    
    # Check stimulus files
    create_placeholder_files()
    
    # Run tests
    print("\n" + "=" * 70)
    print("RUNNING VALIDATION TESTS...")
    print("=" * 70)
    
    tests_passed = run_tests()
    
    if tests_passed:
        print("\n✅ All tests passed!")
    else:
        print("\n⚠️  Some tests failed, but setup is complete.")
        print("   You can still run the experiment - missing files will use placeholders.")
    
    # Print next steps
    print_next_steps()
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 