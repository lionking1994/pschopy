#!/usr/bin/env python3
"""
Mac-optimized demo experiment launcher with resolution selection
Includes client's specific screen size (1496x967) as an option
"""

import sys
import os
import warnings
from pathlib import Path

# Create a custom stream that filters out RGB warnings
class FilteredStream:
    def __init__(self, stream):
        self.stream = stream
        
    def write(self, text):
        # Filter out RGB-related warnings and other repetitive warnings
        if any(x in str(text) for x in ['RGB parameter is deprecated', 'fillRGB', 'lineRGB',
                                         'Font b\'Helvetica Bold\' was requested']):
            return
        self.stream.write(text)
    
    def flush(self):
        self.stream.flush()
        
    def __getattr__(self, name):
        return getattr(self.stream, name)

# Replace stderr to filter warnings
sys.stderr = FilteredStream(sys.stderr)

# Suppress Mac-specific warnings that don't affect functionality
warnings.filterwarnings("ignore", message=".*Monitor specification not found.*")
warnings.filterwarnings("ignore", message=".*Couldn't measure a consistent frame rate.*")
warnings.filterwarnings("ignore", message=".*fillRGB parameter is deprecated.*")
warnings.filterwarnings("ignore", message=".*lineRGB parameter is deprecated.*")
warnings.filterwarnings("ignore", message=".*RGB parameter is deprecated.*")

# Override warning handler to completely suppress RGB warnings
original_showwarning = warnings.showwarning
def filtered_showwarning(message, category, filename, lineno, file=None, line=None):
    msg_str = str(message)
    if 'RGB parameter is deprecated' in msg_str or 'fillRGB' in msg_str or 'lineRGB' in msg_str:
        return  # Skip RGB warnings entirely
    original_showwarning(message, category, filename, lineno, file, line)
warnings.showwarning = filtered_showwarning
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
if sys.platform == 'darwin':
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
    """Setup display configuration with resolution selection"""
    from display_config import get_layout_for_config
    
    print("\n🖥️  Select Display Resolution:")
    print("=" * 50)
    print("📱 Recommended Options:")
    print("  1. client   - Client's Screen (1496x967) ⭐ RECOMMENDED")
    print("  2. auto     - Auto-detect Display Size")
    print()
    print("🖥️  Standard Resolutions:")
    print("  3. small    - Small Display (1366x768)")
    print("  4. standard - Standard Display (1440x900)")
    print("  5. medium   - Medium Display (1600x900)")
    print("  6. large    - Large Display (1920x1080)")
    print()
    print("🖥️  High-Resolution Displays:")
    print("  7. retina   - Retina Display (2880x1800)")
    print("  8. retina16 - MacBook Pro 16\" (3456x2234)")
    print("  9. 4k       - 4K Display (3840x2160)")
    print()
    
    # Create mapping for numeric choices
    choice_map = {
        '1': 'client', '2': 'auto', '3': 'small', '4': 'standard',
        '5': 'medium', '6': 'large', '7': 'retina', '8': 'retina16', '9': '4k'
    }
    
    while True:
        try:
            choice = input("Enter your choice (1-9) or press Enter for client size: ").strip()
            
            # Default to client size if Enter pressed
            if not choice:
                display_size = 'client'
                print("✅ Using client's screen size (1496x967)")
                break
            elif choice in choice_map:
                display_size = choice_map[choice]
                break
            elif choice in ['client', 'auto', 'small', 'standard', 'medium', 'large', 'retina', 'retina16', '4k']:
                display_size = choice
                break
            else:
                print("❌ Invalid choice. Please enter 1-9 or a valid display name.")
                continue
        except KeyboardInterrupt:
            print("\n👋 Setup cancelled by user")
            sys.exit(0)
        except (EOFError, OSError) as e:
            print(f"\n⚠️  Input not available: {e}")
            print("🔄 Automatically using client's screen size...")
            display_size = 'client'
            break
        except Exception as e:
            print(f"❌ Input error: {e}")
            print("🔄 Using client's screen size as fallback...")
            display_size = 'client'
            break
    
    # Special handling for client size
    if display_size == 'client':
        # Check actual screen size to determine if we should use windowed mode
        actual_width, actual_height = None, None
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            actual_width = root.winfo_screenwidth()
            actual_height = root.winfo_screenheight()
            root.destroy()
            print(f"   Detected actual screen: {actual_width}x{actual_height}")
        except:
            # If we can't detect, assume we need windowed mode
            actual_width, actual_height = 1920, 1080
            print(f"   Could not detect screen, assuming: {actual_width}x{actual_height}")
        
        # Use windowed mode if client size doesn't match actual screen
        client_width, client_height = 1496, 967
        use_fullscreen = (actual_width == client_width and actual_height == client_height)
        
        if not use_fullscreen:
            print(f"   ⚠️  Client size ({client_width}x{client_height}) differs from actual screen ({actual_width}x{actual_height})")
            print(f"   📱 Using WINDOWED mode to simulate client's display")
        else:
            print(f"   ✅ Client size matches actual screen - using fullscreen")
        
        # Create a custom configuration for client's screen
        layout_config = {
            'name': "Client's Screen (1496x967)",
            'size': [client_width, client_height],
            'fullscr': use_fullscreen,  # Only fullscreen if sizes match
            'description': 'Client-specific Mac resolution'
        }
        
        # Calculate responsive layout for client's screen
        from display_config import calculate_responsive_layout
        layout = calculate_responsive_layout(client_width, client_height)
        layout_config.update(layout)
        
        print(f"\n🎯 Selected Configuration: {layout_config['name']}")
        print(f"   📏 Resolution: {layout_config['size'][0]}x{layout_config['size'][1]}")
        print(f"   🖥️  Mode: {'Fullscreen' if layout_config['fullscr'] else 'Windowed'}")
        print(f"   📐 Text height: {layout_config['text_height']}px")
        print(f"   📐 Button size: {layout_config['button_width']}x{layout_config['button_height']}")
        print(f"   📐 SART cue: pos={layout_config['cue_pos']}, radius={layout_config['cue_radius']}")
    else:
        # Use standard configuration
        layout_config = get_layout_for_config(display_size)
        
        print(f"\n🎯 Selected Configuration: {layout_config['name']}")
        print(f"   📏 Resolution: {layout_config['size'][0]}x{layout_config['size'][1]}")
        print(f"   🖥️  Mode: {'Fullscreen' if layout_config['fullscr'] else 'Windowed'}")
        if 'video_quality' in layout_config:
            print(f"   🎬 Video quality: {layout_config['video_quality']['rating']}")
    
    print()
    return layout_config

# Clear any cached modules to ensure fresh import
import sys
if 'config.experiment_config' in sys.modules:
    del sys.modules['config.experiment_config']
if 'experiment_config' in sys.modules:
    del sys.modules['experiment_config']

# Import config FIRST before anything else
import config.experiment_config as config

# Path debugging for Mac
print("🔍 Path debugging:")
print(f"   __file__: {config.__file__}")
print(f"   BASE_DIR calculated: {config.BASE_DIR}")
print(f"   BASE_DIR absolute: {config.BASE_DIR.resolve()}")
print(f"   BASE_DIR exists: {config.BASE_DIR.exists()}")

# Check if OneDrive is being used
if 'OneDrive' in str(config.DATA_DIR):
    print(f"📁 OneDrive detected: Using {config.DATA_DIR} for data storage")
else:
    print(f"📁 Using local directory {config.DATA_DIR} for data storage")

print(f"   DATA_DIR: {config.DATA_DIR}")
print(f"   DATA_DIR exists: {config.DATA_DIR.exists()}")
print(f"   STIMULI_DIR: {config.STIMULI_DIR}")
print(f"   STIMULI_DIR exists: {config.STIMULI_DIR.exists()}")
print(f"   Videos dir exists: {config.STIMULI_DIR.joinpath('videos').exists()}")
print(f"   Audio dir exists: {config.STIMULI_DIR.joinpath('audio').exists()}")

# CRITICAL: Force demo mode configuration
print("\n🔧 CONFIGURING DEMO MODE - FORCED OVERRIDE")
print(f"   Script: {__file__}")
print(f"   Config module: {config.__file__}")
print(f"   Before: DEMO_MODE = {config.DEMO_MODE}")
print(f"   Before: SART trials = {config.SART_PARAMS['total_trials']}")

config.DEMO_MODE = True
config.SART_PARAMS['total_trials'] = 2  # Ultra-short: 2 trials, then 1 MW probe at end
config.SART_PARAMS['steps_per_block'] = 1  # Only 1 step per block
config.SART_PARAMS['trials_per_step_min'] = 2  # 2 trials per step
config.SART_PARAMS['trials_per_step_max'] = 2  # 2 trials per step

print(f"   After: DEMO_MODE = {config.DEMO_MODE}")
print(f"   After: SART trials = {config.SART_PARAMS['total_trials']}")

# Verify the configuration
if config.DEMO_MODE and config.SART_PARAMS['total_trials'] == 2:
    print("✅ Configuration verification PASSED")
else:
    print("❌ Configuration verification FAILED")
    print(f"   DEMO_MODE: {config.DEMO_MODE}")
    print(f"   SART trials: {config.SART_PARAMS['total_trials']}")
    sys.exit(1)

print("🎯 DEMO MODE ENABLED (FORCED)")
print(f"   📊 SART blocks: {config.SART_PARAMS['total_trials']} trials, then 1 MW probe at end")
print(f"   📝 Velten statements: 2 per phase (reduced from 12)")
print(f"   ⏱️  Total estimated time: ~5-10 minutes")
print("=" * 60)

# Import main experiment
print("📦 Importing main experiment class...")
print("   Forcing config module in sys.modules...")
sys.modules['config'] = config
sys.modules['experiment_config'] = config

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
    """Run the Mac-optimized demo experiment with resolution selection"""
    
    try:
        print("🚀 Starting Mac-optimized DEMO experiment with resolution selection...")
        print("🍎 Mac-specific optimizations enabled")
        
        # Setup display configuration with user selection
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
                print("\n🎯 DEMO MODE ACTIVE:")
                print(f"   📊 SART blocks: {config.SART_PARAMS['total_trials']} trials total in 8 steps (shortened)")
                print(f"   📝 Velten statements: 2 per phase (shortened from 12)")
                print(f"   ⏱️  Velten duration: {config.TIMING['velten_statement_duration']}s per statement (same as main)")
                print(f"   🧠 MW probes: 1 at the end of each SART block")
                print(f"   🎬 Videos and other phases: Same as main experiment")
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
        print("🏁 Mac demo experiment completed")

if __name__ == "__main__":
    main()
