#!/usr/bin/env python3
"""
Demo Mode Experiment Runner
Runs the experiment with same full functionality as main experiment, except:
- 10 trials per SART block instead of 120
- All other phases remain the same (full Velten statements, videos, etc.)
"""

import sys
from pathlib import Path

# Add config to path
sys.path.append(str(Path(__file__).parent / 'config'))

# Enable demo mode
import experiment_config as config
config.DEMO_MODE = True

# Update parameters for demo mode (only SART shortened)
config.SART_PARAMS['total_trials'] = 40  # 8 steps x 5 trials each
config.SART_PARAMS['trials_per_step_min'] = 5
config.SART_PARAMS['trials_per_step_max'] = 5

print("🚀 Starting DEMO MODE experiment...")
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
