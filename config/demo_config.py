"""
Demo Mode Configuration
Import this file to automatically enable demo mode settings
"""

# Import the main config
from . import experiment_config as config

# Override settings for demo mode (only SART shortened)
config.DEMO_MODE = True
config.SART_PARAMS['trials_per_block'] = 10

print("🎯 DEMO MODE ENABLED")
print(f"   📊 SART: {config.SART_PARAMS['trials_per_block']} trials per block (shortened)")
print(f"   📝 Velten: 3 statements per phase (shortened from 12)")
print(f"   ⏱️  Velten: {config.TIMING['velten_statement_duration']}s per statement (same as main)")
print(f"   🧠 MW probes: Every {config.SART_PARAMS['probe_interval_min']}-{config.SART_PARAMS['probe_interval_max']} trials (same as main)")
print(f"   🎬 Videos and other phases: Same as main experiment")
print(f"   🕒 Estimated duration: 20-25 minutes")
print()
