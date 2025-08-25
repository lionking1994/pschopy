#!/usr/bin/env python3
"""
Mac-optimized demo experiment launcher for PsychoPy
Includes Mac-specific optimizations to reduce HID and timing warnings.
"""

import sys
import os
import warnings

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
    
    # Redirect stderr temporarily to capture HID errors
    original_stderr = sys.stderr
    
    def suppress_hid_output():
        """Context manager to suppress HID error output"""
        return contextlib.redirect_stderr(io.StringIO())

# Import and configure experiment
from config import experiment_config as config

# Enable demo mode and configure reduced parameters
config.DEMO_MODE = True

# Reduce SART trials for demo mode
config.SART_PARAMS['trials_per_block'] = 10  # Reduced from 120

print("🎯 DEMO MODE ENABLED")
print(f"   📊 SART trials per block: {config.SART_PARAMS['trials_per_block']} (reduced from 120)")
print(f"   📝 Velten statements: 3 per phase (reduced from 12)")
print(f"   ⏱️  Total estimated time: ~15-20 minutes")
print()

# Import main experiment class
try:
    if sys.platform == 'darwin':
        with suppress_hid_output():
            from main_experiment import MoodSARTExperimentSimple
    else:
        from main_experiment import MoodSARTExperimentSimple
except Exception as e:
    print(f"Import error: {e}")
    sys.exit(1)

def main():
    """Run the Mac-optimized demo experiment"""
    try:
        print("🚀 Starting Mac-optimized DEMO experiment...")
        
        # Create and run experiment with Mac-specific error handling
        if sys.platform == 'darwin':
            # Suppress HID output during initialization
            with suppress_hid_output():
                experiment = MoodSARTExperimentSimple()
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

