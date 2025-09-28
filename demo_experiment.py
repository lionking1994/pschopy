#!/usr/bin/env python3
"""
Demo Mode Experiment Runner
Runs the experiment with same full functionality as main experiment, except:
- 10 trials per SART block instead of 120
- All other phases remain the same (full Velten statements, videos, etc.)
- Display size selection for different screen configurations
"""

import sys
import argparse
from pathlib import Path

# Add config to path
sys.path.append(str(Path(__file__).parent / 'config'))

def setup_display_config(display_size=None):
    """Setup display configuration based on user selection"""
    from display_config import get_layout_for_config, print_available_configs
    
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
                choice = input("Enter choice (1-13) or display name: ").strip().lower()
                
                if choice in choice_map:
                    display_size = choice_map[choice]
                    break
                elif choice in ['tiny', 'compact', 'small', 'standard', 'medium', 'wide', 
                               'large', 'tall', 'retina', 'xlarge', 'ultrawide', '4k', 'auto']:
                    display_size = choice
                    break
                else:
                    print("❌ Invalid choice. Please enter 1-13 or a display name.")
                    
            except KeyboardInterrupt:
                print("\n👋 Experiment cancelled.")
                sys.exit(0)
    
    # Get layout configuration
    layout_config = get_layout_for_config(display_size)
    
    print(f"\n✅ Selected: {layout_config['name']}")
    if layout_config['size']:
        print(f"   Screen size: {layout_config['size'][0]}x{layout_config['size'][1]}")
    print(f"   Display mode: {'Fullscreen' if layout_config.get('fullscr', True) else 'Windowed'}")
    print(f"   Text position: {layout_config['text_pos']}")
    print(f"   SART cue position: {layout_config['cue_pos']}")
    print(f"   Text wrap width: {layout_config['text_wrap']}")
    
    # Show video quality information
    if 'video_quality' in layout_config:
        video_info = layout_config['video_quality']
        print(f"   📺 Video quality: {video_info['rating']} - {video_info['description']}")
        print(f"   💡 Recommendation: {video_info['recommendation']}")
    
    return layout_config

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='PsychoPy Experiment Demo Mode',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Display Size Options:
  📱 Small Displays:
    tiny     - Tiny Display (1024x768) - Old/small laptop, tablet
    compact  - Compact Display (1280x720) - HD ready, compact laptop
    small    - Small Display (1366x768) - Typical laptop

  🖥️  Standard Displays:
    standard - Standard Display (1440x900) - Standard laptop/desktop
    medium   - Medium Display (1600x900) - Medium laptop/desktop
    wide     - Wide Display (1680x1050) - Wide desktop monitor

  🖥️  Large Displays:
    large    - Large Display (1920x1080) - Full HD desktop/laptop
    tall     - Tall Display (1920x1200) - Full HD with extra height
    retina   - Retina Display (2880x1800) - MacBook Pro Retina

  🖥️  High-Resolution Displays:
    xlarge   - Extra Large (2560x1440) - 1440p high-res display
    ultrawide- Ultrawide (3440x1440) - 21:9 ultrawide monitor
    4k       - 4K Display (3840x2160) - 4K Ultra HD display
    
  🔄 Auto-Detection:
    auto     - Auto-detect screen size

Examples:
  python demo_experiment.py                      # Interactive selection
  python demo_experiment.py --display large     # Use Full HD preset
  python demo_experiment.py --display tiny      # Use tiny display for testing
  python demo_experiment.py --display 4k        # Use 4K display preset
  python demo_experiment.py --display auto      # Auto-detect screen size
        """
    )
    
    parser.add_argument(
        '--display', '-d',
        choices=['tiny', 'compact', 'small', 'standard', 'medium', 'wide', 
                 'large', 'tall', 'retina', 'xlarge', 'ultrawide', '4k', 'auto'],
        help='Display size configuration (default: interactive selection)'
    )
    
    return parser.parse_args()

# Parse command line arguments
args = parse_arguments()

# Setup display configuration
layout_config = setup_display_config(args.display)

# Enable demo mode
import experiment_config as config
config.DEMO_MODE = True

# Apply display configuration to experiment config
config.SCREEN_PARAMS['size'] = layout_config['size']
config.SCREEN_PARAMS['fullscr'] = layout_config['fullscr']  # Apply windowed/fullscreen setting
config.TEXT_STYLE['wrapWidth'] = layout_config['text_wrap']
config.CONDITION_CUES['inhibition']['pos'] = layout_config['cue_pos']
config.CONDITION_CUES['inhibition']['radius'] = layout_config['cue_radius']
config.CONDITION_CUES['non_inhibition']['pos'] = layout_config['cue_pos']
config.CONDITION_CUES['non_inhibition']['radius'] = layout_config['cue_radius']

# Store layout config for use in main experiment
config.LAYOUT_CONFIG = layout_config

# Update parameters for demo mode (only SART shortened)
config.SART_PARAMS['total_trials'] = 40  # 8 steps x 5 trials each
config.SART_PARAMS['trials_per_step_min'] = 5
config.SART_PARAMS['trials_per_step_max'] = 5

print("\n🚀 Starting DEMO MODE experiment...")
print(f"   - Display: {layout_config['name']}")
if layout_config['size']:
    print(f"   - Resolution: {layout_config['size'][0]}x{layout_config['size'][1]}")
print(f"   - SART trials total: {config.SART_PARAMS['total_trials']} in {config.SART_PARAMS['steps_per_block']} steps (shortened)")
print(f"   - Velten statements: 3 per phase (shortened from 12)")
print(f"   - Velten statement duration: {config.TIMING['velten_statement_duration']}s (same as main)")
print(f"   - MW probes: After each of {config.SART_PARAMS['steps_per_block']} steps (same structure as main)")
print(f"   - Videos and other phases: Same as main experiment")
print(f"   - Estimated total time: ~20-25 minutes")
print()

# Import and run the main experiment
from main_experiment import MoodSARTExperimentSimple

if __name__ == '__main__':
    try:
        experiment = MoodSARTExperimentSimple()
        experiment.run_experiment()
    except KeyboardInterrupt:
        print("\nExperiment interrupted by user")
    except Exception as e:
        print(f"Error running experiment: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Demo experiment completed")
