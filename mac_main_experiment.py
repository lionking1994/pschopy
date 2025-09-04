#!/usr/bin/env python3
"""
Mac-optimized main experiment launcher for PsychoPy
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

# Mac-specific environment setup
if sys.platform == 'darwin':  # macOS
    print("🍎 macOS detected - applying Mac-specific optimizations...")
    
    # Set environment variables to reduce HID errors
    os.environ['PSYCHOPY_DISABLE_HID_WARNINGS'] = '1'
    os.environ['PSYCHOPY_LOGGING_LEVEL'] = 'WARNING'
    
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

# Ensure demo mode is disabled for main experiment
config.DEMO_MODE = False
print("🎯 FULL EXPERIMENT MODE")
print(f"   📊 SART trials total: {config.SART_PARAMS['total_trials']} (in {config.SART_PARAMS['steps_per_block']} steps)")
print(f"   📝 Velten statements: 12 per phase (full)")
print(f"   ⏱️  Total estimated time: ~45-60 minutes")
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
    """Run the Mac-optimized main experiment"""
    try:
        print("🚀 Starting Mac-optimized FULL experiment...")
        
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
        print("🏁 Mac main experiment completed")

if __name__ == "__main__":
    main()

