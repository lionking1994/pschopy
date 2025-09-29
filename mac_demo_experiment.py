#!/usr/bin/env python3
"""
Mac-optimized demo experiment launcher for PsychoPy
Includes Mac-specific optimizations to reduce HID and timing warnings.
Features responsive UI with display size selection for different screen configurations.
"""

import sys
import os
import warnings
import argparse
from pathlib import Path

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
    
    def suppress_all_warnings():
        """Context manager to suppress all warnings and HID output"""
        return contextlib.redirect_stderr(io.StringIO())

# Add config to path
sys.path.append(str(Path(__file__).parent / 'config'))

def setup_display_config(display_size=None):
    """Setup display configuration based on user selection"""
    from display_config import get_layout_for_config, print_available_configs
    
    # Detect actual screen size (with fallback for missing tkinter)
    try:
        import tkinter as tk
        root = tk.Tk()
        actual_width = root.winfo_screenwidth()
        actual_height = root.winfo_screenheight()
        root.destroy()
    except ImportError:
        # tkinter not available in PsychoPy environment - use display_config.py fallback
        actual_width, actual_height = None, None
    except Exception as e:
        # Screen detection failed - use display_config.py fallback
        actual_width, actual_height = None, None
    
    if display_size is None:
        # Interactive selection
        print("\n🖥️  Select Display Configuration:")
        print("=" * 50)
        print("📱 Small Displays:")
        print("  1. tiny     - Tiny Display (1024x768)")
        print("  2. compact  - Compact Display (1280x720)")
        print("  3. small    - Small Display (1366x768)")
        print()
        print("🖥️  Standard Displays:")
        print("  4. standard - Standard Display (1440x900)")
        print("  5. medium   - Medium Display (1600x900)")
        print("  6. wide     - Wide Display (1680x1050)")
        print()
        print("🖥️  Large Displays:")
        print("  7. large    - Large Display (1920x1080)")
        print("  8. tall     - Tall Display (1920x1200)")
        print("  9. retina   - Retina Display (2880x1800)")
        print()
        print("🖥️  High-Resolution Displays:")
        print(" 10. xlarge   - Extra Large Display (2560x1440)")
        print(" 11. ultrawide- Ultrawide Display (3440x1440)")
        print(" 12. 4k       - 4K Display (3840x2160)")
        print()
        print(" 13. auto     - Auto-detect Display Size")
        print()
        
        # Create mapping for numeric choices
        choice_map = {
            '1': 'tiny', '2': 'compact', '3': 'small', '4': 'standard',
            '5': 'medium', '6': 'wide', '7': 'large', '8': 'tall',
            '9': 'retina', '10': 'xlarge', '11': 'ultrawide', '12': '4k',
            '13': 'auto'
        }
        
        while True:
            try:
                choice = input("Enter your choice (1-13) or display name: ").strip()
                
                if choice in choice_map:
                    display_size = choice_map[choice]
                    break
                elif choice in ['tiny', 'compact', 'small', 'standard', 'medium', 'wide', 
                              'large', 'tall', 'retina', 'xlarge', 'ultrawide', '4k', 'auto']:
                    display_size = choice
                    break
                else:
                    print("❌ Invalid choice. Please enter a number (1-13) or display name.")
                    continue
            except KeyboardInterrupt:
                print("\n👋 Setup cancelled by user")
                sys.exit(0)
            except Exception as e:
                print(f"❌ Input error: {e}")
                continue
    
    # Get layout configuration
    layout_config = get_layout_for_config(display_size)
    
    print(f"\n🎯 Selected Configuration: {layout_config['name']}")
    print(f"   📏 Resolution: {layout_config['size'][0]}x{layout_config['size'][1]}")
    print(f"   🖥️  Mode: {'Fullscreen' if layout_config['fullscr'] else 'Windowed'}")
    print(f"   🎬 Video quality: {layout_config['video_quality']['rating']}")
    print()
    
    return layout_config

# Clear any cached modules to ensure fresh import
import sys
if 'experiment_config' in sys.modules:
    del sys.modules['experiment_config']
if 'config.experiment_config' in sys.modules:
    del sys.modules['config.experiment_config']

# Import and configure experiment config FIRST
from config import experiment_config as config

# Force demo mode configuration BEFORE importing main experiment
print("🔧 CONFIGURING DEMO MODE - FORCED OVERRIDE")
print(f"   Script: {__file__}")
print(f"   Config module: {config.__file__}")
print(f"   Before: DEMO_MODE = {getattr(config, 'DEMO_MODE', 'NOT_SET')}")
print(f"   Before: SART trials = {config.SART_PARAMS.get('total_trials', 'NOT_SET')}")

# FORCE demo mode settings with absolute certainty
config.DEMO_MODE = True
config.SART_PARAMS['total_trials'] = 40  # 8 steps x 5 trials each
config.SART_PARAMS['trials_per_step_min'] = 5
config.SART_PARAMS['trials_per_step_max'] = 5

# Double-check the assignment worked
print(f"   After: DEMO_MODE = {config.DEMO_MODE}")
print(f"   After: SART trials = {config.SART_PARAMS['total_trials']}")

# Verify settings with assertions
try:
    assert config.DEMO_MODE == True, f"DEMO_MODE is {config.DEMO_MODE}, should be True"
    assert config.SART_PARAMS['total_trials'] == 40, f"SART trials is {config.SART_PARAMS['total_trials']}, should be 40"
    print("✅ Configuration verification PASSED")
except AssertionError as e:
    print(f"❌ Configuration verification FAILED: {e}")
    sys.exit(1)

print("🎯 DEMO MODE ENABLED (FORCED)")
print(f"   📊 SART trials total: {config.SART_PARAMS['total_trials']} in {config.SART_PARAMS['steps_per_block']} steps (reduced from 120)")
print(f"   📝 Velten statements: 3 per phase (reduced from 12)")
print(f"   ⏱️  Total estimated time: ~15-20 minutes")
print("=" * 60)

# Force the config module in sys.modules so main_experiment gets our modified version
sys.modules['experiment_config'] = config
sys.modules['config.experiment_config'] = config

# Now import main experiment class AFTER configuration is set
print("📦 Importing main experiment class...")
print(f"   Forcing config module in sys.modules...")

# Clear main_experiment from cache if it exists
if 'main_experiment' in sys.modules:
    del sys.modules['main_experiment']
    print("   Cleared main_experiment from cache")

try:
    if sys.platform == 'darwin':
        with suppress_hid_output():
            from main_experiment import MoodSARTExperimentSimple
    else:
        from main_experiment import MoodSARTExperimentSimple
    print("✅ Main experiment class imported successfully")
    
    # Verify the main experiment sees our config
    import main_experiment
    main_config = main_experiment.config
    print(f"   Main experiment config DEMO_MODE: {main_config.DEMO_MODE}")
    print(f"   Main experiment config SART trials: {main_config.SART_PARAMS['total_trials']}")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

def main():
    """Run the Mac-optimized demo experiment with responsive UI"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Mac-optimized Demo Experiment with Display Configuration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Display Configurations:
  tiny      - Tiny Display (1024x768)
  compact   - Compact Display (1280x720) 
  small     - Small Display (1366x768)
  standard  - Standard Display (1440x900)
  medium    - Medium Display (1600x900)
  wide      - Wide Display (1680x1050)
  large     - Large Display (1920x1080)
  tall      - Tall Display (1920x1200)
  retina    - Retina Display (2880x1800)
  xlarge    - Extra Large Display (2560x1440)
  ultrawide - Ultrawide Display (3440x1440)
  4k        - 4K Display (3840x2160)
  auto      - Auto-detect Display Size

Examples:
  python mac_demo_experiment.py --display auto
  python mac_demo_experiment.py --display large
  python mac_demo_experiment.py  # Interactive selection
        """
    )
    
    parser.add_argument('--display', type=str, default=None,
                        choices=['tiny', 'compact', 'small', 'standard', 'medium', 'wide', 
                                'large', 'tall', 'retina', 'xlarge', 'ultrawide', '4k', 'auto'],
                        help='Display configuration to use')
    
    args = parser.parse_args()
    
    try:
        print("🚀 Starting Mac-optimized DEMO experiment...")
        print("🍎 Mac-specific optimizations enabled")
        
        # Setup display configuration
        layout_config = setup_display_config(args.display)
        
        # Apply layout configuration to experiment config
        config.SCREEN_PARAMS['size'] = layout_config['size']
        config.SCREEN_PARAMS['fullscr'] = layout_config['fullscr']
        config.LAYOUT_CONFIG = layout_config
        
        # Update text styles with responsive sizing
        config.TEXT_STYLE['height'] = layout_config['text_height']
        config.TEXT_STYLE['wrapWidth'] = layout_config['text_wrap']
        config.TEXT_STYLE['pos'] = layout_config['text_pos']
        
        config.VELTEN_TEXT_STYLE['height'] = layout_config['velten_text_height']
        config.VELTEN_TEXT_STYLE['wrapWidth'] = layout_config['text_wrap']
        config.VELTEN_TEXT_STYLE['pos'] = (0, 0)  # Keep centered
        
        # Update SART cue positions and sizes
        config.CONDITION_CUES['inhibition']['pos'] = layout_config['cue_pos']
        config.CONDITION_CUES['inhibition']['radius'] = layout_config['cue_radius']
        config.CONDITION_CUES['non_inhibition']['pos'] = layout_config['cue_pos']
        config.CONDITION_CUES['non_inhibition']['radius'] = layout_config['cue_radius']
        
        # Configuration summary
        print(f"✅ Configuration applied: {config.SCREEN_PARAMS['size'][0]}x{config.SCREEN_PARAMS['size'][1]} ({'Fullscreen' if config.SCREEN_PARAMS['fullscr'] else 'Windowed'})")
        
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

