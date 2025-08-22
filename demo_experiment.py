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
config.SART_PARAMS['trials_per_block'] = 10

print("🚀 Starting DEMO MODE experiment...")
print(f"   - SART trials per block: {config.SART_PARAMS['trials_per_block']} (shortened)")
print(f"   - Velten statements: 3 per phase (shortened from 12)")
print(f"   - Velten statement duration: {config.TIMING['velten_statement_duration']}s (same as main)")
print(f"   - MW probe interval: {config.SART_PARAMS['probe_interval_min']}-{config.SART_PARAMS['probe_interval_max']} trials (same as main)")
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
