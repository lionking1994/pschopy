#!/usr/bin/env python3
"""
Mac-optimized main experiment launcher for PsychoPy
Includes Mac-specific optimizations to reduce HID and timing warnings.
Automatically detects display configuration and applies responsive UI.
"""

import sys
import os
import warnings
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
warnings.filterwarnings("ignore", message=".*PsychHID-ERROR.*")
warnings.filterwarnings("ignore", message=".*PsychHID-INFO.*")
warnings.filterwarnings("ignore", message=".*PsychHID-WARNING.*")

# Suppress Tkinter theme debug output
warnings.filterwarnings("ignore", message=".*ThemeChanged.*")
warnings.filterwarnings("ignore", message=".*ttk::ThemeChanged.*")

# Suppress stderr output during tkinter operations
os.environ['TK_SILENCE_DEPRECATION'] = '1'

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

def setup_display_config():
    """Setup display configuration using automatic detection"""
    from display_config import get_layout_for_config
    
    print("🔍 Detecting display configuration...")
    
    # Always use auto-detection mode
    display_size = 'auto'
    
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

# Force FULL experiment mode configuration BEFORE importing main experiment
print("🔧 CONFIGURING FULL EXPERIMENT MODE")
print(f"   Script: {__file__}")
print(f"   Config module: {config.__file__}")
print(f"   Before: DEMO_MODE = {getattr(config, 'DEMO_MODE', 'NOT_SET')}")
print(f"   Before: SART trials = {config.SART_PARAMS.get('total_trials', 'NOT_SET')}")

# FORCE full experiment mode settings with absolute certainty
config.DEMO_MODE = False
config.SART_PARAMS['total_trials'] = 120  # Full experiment
config.SART_PARAMS['trials_per_step_min'] = 13
config.SART_PARAMS['trials_per_step_max'] = 17

# Double-check the assignment worked
print(f"   After: DEMO_MODE = {config.DEMO_MODE}")
print(f"   After: SART trials = {config.SART_PARAMS['total_trials']}")

# Verify settings with assertions
try:
    assert config.DEMO_MODE == False, f"DEMO_MODE is {config.DEMO_MODE}, should be False"
    assert config.SART_PARAMS['total_trials'] == 120, f"SART trials is {config.SART_PARAMS['total_trials']}, should be 120"
    print("✅ Configuration verification PASSED")
except AssertionError as e:
    print(f"❌ Configuration verification FAILED: {e}")
    sys.exit(1)

print("🎯 FULL EXPERIMENT MODE ENABLED")
print(f"   📊 SART trials total: {config.SART_PARAMS['total_trials']} in {config.SART_PARAMS['steps_per_block']} steps")
print(f"   📝 Velten statements: 25 per phase (full set)")
print(f"   ⏱️  Total estimated time: ~45-60 minutes")
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
    """Run the Mac-optimized main experiment with auto-detected display configuration"""
    try:
        print("🚀 Starting Mac-optimized FULL experiment...")
        print("🍎 Mac-specific optimizations enabled")
        
        # Setup display configuration with auto-detection
        layout_config = setup_display_config()
        
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
                print("\n🎯 FULL EXPERIMENT MODE ACTIVE:")
                print(f"   📊 SART blocks: {config.SART_PARAMS['total_trials']} trials total in {config.SART_PARAMS['steps_per_block']} steps")
                print(f"   📝 Velten statements: 25 per phase (full set)")
                print(f"   ⏱️  Velten duration: {config.TIMING['velten_statement_duration']}s per statement")
                print(f"   🧠 MW probes: After each of {config.SART_PARAMS['steps_per_block']} steps ({config.SART_PARAMS['trials_per_step_min']}-{config.SART_PARAMS['trials_per_step_max']} trials per step)")
                print(f"   📊 Mood ratings: Every 4 Velten statements")
                print(f"   🎬 Videos and mood induction phases: Full duration")
                print()
                
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
        print("🏁 Mac main experiment completed")

if __name__ == "__main__":
    main()

