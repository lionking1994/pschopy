#!/usr/bin/env python3
"""
Mac-optimized demo experiment launcher for PsychoPy - FIXED VERSION
This version forces demo mode configuration and includes comprehensive debugging.
"""

import sys
import os
import warnings
from pathlib import Path

print("🍎 Mac Demo Experiment - FIXED VERSION")
print("=" * 50)

# Suppress Mac-specific warnings that don't affect functionality
warnings.filterwarnings("ignore", message=".*Monitor specification not found.*")
warnings.filterwarnings("ignore", message=".*Couldn't measure a consistent frame rate.*")
warnings.filterwarnings("ignore", message=".*fillRGB parameter is deprecated.*")
warnings.filterwarnings("ignore", message=".*lineRGB parameter is deprecated.*")
warnings.filterwarnings("ignore", message=".*Font.*was requested. No similar font found.*")
warnings.filterwarnings("ignore", message=".*t of last frame was.*")
warnings.filterwarnings("ignore", message=".*Multiple dropped frames.*")
warnings.filterwarnings("ignore", message=".*Font Manager failed to load.*")
warnings.filterwarnings("ignore", message=".*Boolean HIDBuildMultiDeviceList.*")

# Mac-specific environment setup
if sys.platform == 'darwin':  # macOS
    print("🍎 macOS detected - applying Mac-specific optimizations...")
    
    # Set environment variables to reduce HID errors and improve audio
    os.environ['PSYCHOPY_DISABLE_HID_WARNINGS'] = '1'
    os.environ['PSYCHOPY_LOGGING_LEVEL'] = 'WARNING'
    
    # Audio configuration for Mac
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
    # Remove SDL audio driver constraints to allow proper audio
    if 'SDL_AUDIODRIVER' in os.environ:
        del os.environ['SDL_AUDIODRIVER']
    if 'SDL_AUDIO_DRIVER' in os.environ:
        del os.environ['SDL_AUDIO_DRIVER']
    
    # Suppress HID-related output
    import contextlib
    import io
    
    def suppress_hid_output():
        """Context manager to suppress HID error output"""
        return contextlib.redirect_stderr(io.StringIO())
    
    def suppress_all_warnings():
        """Context manager to suppress all warnings and HID output"""
        return contextlib.redirect_stderr(io.StringIO())

# Add config to path
config_dir = Path(__file__).parent / 'config'
sys.path.insert(0, str(config_dir))

print("📦 Importing configuration...")

# Import config FIRST
try:
    import experiment_config as config
    print("✅ Configuration imported successfully")
except Exception as e:
    print(f"❌ Failed to import configuration: {e}")
    sys.exit(1)

# Force demo mode configuration with detailed debugging
print("\n🔧 FORCING Demo Mode Configuration...")
print(f"   Working directory: {os.getcwd()}")
print(f"   Script location: {__file__}")
print(f"   Config file location: {config.__file__}")

# Show before state
print(f"\n📊 BEFORE configuration:")
print(f"   DEMO_MODE: {getattr(config, 'DEMO_MODE', 'NOT_SET')}")
print(f"   SART trials: {config.SART_PARAMS.get('trials_per_block', 'NOT_SET')}")

# FORCE demo mode settings
config.DEMO_MODE = True
config.SART_PARAMS['trials_per_block'] = 10

# Show after state
print(f"\n📊 AFTER configuration:")
print(f"   DEMO_MODE: {config.DEMO_MODE}")
print(f"   SART trials: {config.SART_PARAMS['trials_per_block']}")

# Verify settings
assert config.DEMO_MODE == True, "Demo mode STILL not enabled!"
assert config.SART_PARAMS['trials_per_block'] == 10, f"SART trials STILL not 10: {config.SART_PARAMS['trials_per_block']}"

print("\n🎯 DEMO MODE ENABLED (FORCED)")
print(f"   📊 SART trials per block: {config.SART_PARAMS['trials_per_block']} (reduced from 120)")
print(f"   📝 Velten statements: 3 per phase (reduced from 12)")
print(f"   ⏱️  Total estimated time: ~15-20 minutes")

# Check file paths
print(f"\n📁 File Path Debugging:")
print(f"   BASE_DIR: {config.BASE_DIR}")
print(f"   BASE_DIR exists: {config.BASE_DIR.exists()}")
print(f"   STIMULI_DIR: {config.STIMULI_DIR}")
print(f"   STIMULI_DIR exists: {config.STIMULI_DIR.exists()}")
print(f"   VIDEO_DIR: {config.VIDEO_DIR}")
print(f"   VIDEO_DIR exists: {config.VIDEO_DIR.exists()}")

if config.VIDEO_DIR.exists():
    print(f"   Files in videos directory:")
    try:
        video_files = list(config.VIDEO_DIR.glob("*"))
        for video_file in video_files:
            print(f"      - {video_file.name}")
    except Exception as e:
        print(f"      Error listing files: {e}")

print("\n📦 Importing main experiment class...")

# Now import main experiment AFTER configuration is forced
try:
    if sys.platform == 'darwin':
        with suppress_hid_output():
            from main_experiment import MoodSARTExperimentSimple
    else:
        from main_experiment import MoodSARTExperimentSimple
    print("✅ Main experiment class imported successfully")
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

def main():
    """Run the Mac-optimized demo experiment"""
    try:
        print("\n🚀 Starting Mac-optimized DEMO experiment...")
        
        # Final verification before starting
        print(f"🔍 Final configuration check:")
        print(f"   DEMO_MODE: {config.DEMO_MODE}")
        print(f"   SART trials: {config.SART_PARAMS['trials_per_block']}")
        
        # Create and run experiment with Mac-specific error handling
        if sys.platform == 'darwin':
            # Suppress HID output during initialization and experiment
            with suppress_all_warnings():
                experiment = MoodSARTExperimentSimple()
                print("✅ Experiment initialized successfully")
                experiment.run_experiment()
        else:
            experiment = MoodSARTExperimentSimple()
            print("✅ Experiment initialized successfully")
            experiment.run_experiment()
        
    except KeyboardInterrupt:
        print("\n⚠️  Experiment interrupted by user")
    except Exception as e:
        print(f"❌ Error running experiment: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🏁 Mac demo experiment completed")

if __name__ == "__main__":
    main()
