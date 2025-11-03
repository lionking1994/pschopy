#!/usr/bin/env python3
"""
Demo mode launcher for the PsychoPy experiment
Automatically detects display configuration and runs in demo mode
Cross-platform: Windows, macOS, and Linux
"""

import sys
import os
import platform
from pathlib import Path

# Add config to path
sys.path.append(str(Path(__file__).parent / 'config'))

# Platform-specific setup
system = platform.system()
if system == 'Linux':
    # Linux-specific optimizations
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'  # Better Qt scaling
    # Set SDL audio driver for better compatibility
    os.environ['SDL_AUDIODRIVER'] = 'pulse'  # Use PulseAudio on Linux
    # Disable some warnings that are common on Linux
    import warnings
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    warnings.filterwarnings('ignore', message='.*ALSA.*')
    print(f"🐧 Linux detected - applying Linux-specific optimizations...")
    print(f"   Audio backend: PulseAudio")
elif system == 'Darwin':
    print(f"🍎 macOS detected - for Mac-specific optimizations use mac_demo_experiment.py")
elif system == 'Windows':
    print(f"🪟 Windows detected")
else:
    print(f"⚠️ Unknown platform: {system}")

def setup_display_config():
    """Setup display configuration using automatic detection"""
    from display_config import get_layout_for_config
    
    print("🔍 Detecting display configuration...")
    
    # Always use auto-detection mode
    display_size = 'auto'
    
    # Get layout configuration
    layout_config = get_layout_for_config(display_size)
    
    print(f"\n✅ Detected: {layout_config['name']}")
    if layout_config['size']:
        print(f"   Screen size: {layout_config['size'][0]}x{layout_config['size'][1]}")
    print(f"   Display mode: {'Fullscreen' if layout_config.get('fullscr', True) else 'Windowed'}")
    
    # Show video quality information
    if 'video_quality' in layout_config:
        video_info = layout_config['video_quality']
        print(f"   📺 Video quality: {video_info['rating']}")
    
    return layout_config

# Clear any cached modules to ensure fresh import
import sys
if 'config.experiment_config' in sys.modules:
    del sys.modules['config.experiment_config']
if 'experiment_config' in sys.modules:
    del sys.modules['experiment_config']

# Import config FIRST before anything else
import config.experiment_config as config

# Force demo mode
print("🔧 Configuring DEMO mode...")
config.DEMO_MODE = True
config.SART_PARAMS['total_trials'] = 2  # Only 2 trials for ultra-quick demo
config.SART_PARAMS['steps_per_block'] = 1  # Only 1 step (2 trials + MW probe)
config.SART_PARAMS['trials_per_step_min'] = 2  # 2 trials per step
config.SART_PARAMS['trials_per_step_max'] = 2  # 2 trials per step
print(f"✅ DEMO_MODE = {config.DEMO_MODE}")
print(f"✅ SART trials = {config.SART_PARAMS['total_trials']} (2 trials + MW probe per block)")

# Now import the main experiment
try:
    from main_experiment import MoodSARTExperimentSimple
    print("✅ Main experiment imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def main():
    """Run the demo experiment with auto-detected display configuration"""
    try:
        print("\n" + "="*60)
        print("🎯 STARTING DEMO EXPERIMENT")
        print(f"   Platform: {platform.system()} {platform.release()}")
        print("="*60)
        
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
        
        # Update SART cue positions and sizes
        config.CONDITION_CUES['inhibition']['pos'] = layout_config['cue_pos']
        config.CONDITION_CUES['inhibition']['radius'] = layout_config['cue_radius']
        config.CONDITION_CUES['non_inhibition']['pos'] = layout_config['cue_pos']
        config.CONDITION_CUES['non_inhibition']['radius'] = layout_config['cue_radius']
        
        print("\n📊 DEMO Mode Configuration:")
        print(f"   • SART trials: {config.SART_PARAMS['total_trials']} per block (2 trials + MW probe)")
        print(f"   • Velten statements: 2 per phase (reduced from 12)")
        print(f"   • Estimated duration: ~5-10 minutes")
        print("="*60)
        
        # Create and run the experiment
        try:
            experiment = MoodSARTExperimentSimple()
            print("✅ Experiment initialized")
        except Exception as init_error:
            if system == 'Linux' and 'audio' in str(init_error).lower():
                print("\n⚠️ Audio initialization issue detected on Linux")
                print("   Try: sudo apt-get install pulseaudio python3-pyaudio")
                print("   Or run with: SDL_AUDIODRIVER=alsa python3 demo_experiment.py")
            raise init_error
        
        print("\n🚀 Starting experiment...")
        experiment.run_experiment()
        
    except KeyboardInterrupt:
        print("\n⚠️  Experiment interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n✅ Demo experiment completed")

if __name__ == "__main__":
    main()