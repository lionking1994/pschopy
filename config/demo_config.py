"""
Demo Mode Configuration
Import this file to automatically enable demo mode settings
"""

# Import the main config
from . import experiment_config as config

# Override settings for demo mode (only SART shortened)
config.DEMO_MODE = True
config.SART_PARAMS['total_trials'] = 40  # Shortened total (5 trials per step x 8 steps)
config.SART_PARAMS['trials_per_step_min'] = 5  # Shortened steps
config.SART_PARAMS['trials_per_step_max'] = 5  # Fixed size for demo

print("🎯 DEMO MODE ENABLED")
print(f"   📊 SART: {config.SART_PARAMS['total_trials']} trials total in {config.SART_PARAMS['steps_per_block']} steps (shortened)")
print(f"   📝 Velten: 3 statements per phase (shortened from 25)")
print(f"   ⏱️  Velten: {config.TIMING['velten_statement_duration']}s per statement (same as main)")
print(f"   🧠 MW probes: After each of {config.SART_PARAMS['steps_per_block']} steps (same structure as main)")
print(f"   🎬 Videos and other phases: Same as main experiment")
print(f"   🕒 Estimated duration: 20-25 minutes")
print()
