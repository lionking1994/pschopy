#!/usr/bin/env python3
"""
Create Sample Data for Testing Data Analyzer
Generates realistic sample data that matches the experiment output format.
"""

import sys
import random
import datetime
import csv
from pathlib import Path
import numpy as np

# Add config to path
sys.path.append(str(Path(__file__).parent.parent / 'config'))
import experiment_config as config

def generate_sample_participant_data(participant_id, condition):
    """Generate sample data for one participant"""
    
    participant_code = f"MOOD_SART_TEST_{participant_id:03d}"
    email = f"participant{participant_id}@test.com"
    start_time = datetime.datetime.now().isoformat()
    
    data_rows = []
    
    # Get counterbalancing order
    order = config.COUNTERBALANCING_ORDERS[condition]
    
    # Generate baseline mood rating
    baseline_mood = random.uniform(4, 6)  # Neutral baseline
    data_rows.append({
        'participant_code': participant_code,
        'email': email,
        'condition': condition,
        'session_start': start_time,
        'phase': 'mood_rating_baseline',
        'mood_rating': baseline_mood,
        'block_type': None, 'block_number': None, 'trial_number': None,
        'stimulus': None, 'stimulus_position': None, 'response': None,
        'correct_response': None, 'accuracy': None, 'reaction_time': None,
        'mw_tut_rating': None, 'mw_fmt_rating': None, 'velten_rating': None,
        'video_file': None, 'audio_file': None, 'velten_statement': None,
        'timestamp': datetime.datetime.now().isoformat()
    })
    
    current_mood = baseline_mood
    
    # Generate 4 phases of mood induction + SART
    for phase in range(4):
        block_number = phase + 1
        sart_condition = order['sart_conditions'][phase]
        mood_induction = order['mood_inductions'][phase]
        induction_type, valence = mood_induction
        
        # Mood induction effect
        if valence == '+':
            mood_change = random.uniform(1.0, 2.5)
            current_mood = min(9, current_mood + mood_change)
        else:  # negative
            mood_change = random.uniform(-2.5, -1.0)
            current_mood = max(1, current_mood + mood_change)
        
        # Velten statements if applicable
        if induction_type == 'V':
            statements = 5  # Simulate 5 statements
            for stmt_num in range(statements):
                velten_rating = random.randint(4, 7) if valence == '+' else random.randint(2, 5)
                data_rows.append({
                    'participant_code': participant_code,
                    'email': email,
                    'condition': condition,
                    'session_start': start_time,
                    'phase': 'velten_statements',
                    'velten_rating': velten_rating,
                    'velten_statement': f"Sample {valence} statement {stmt_num + 1}",
                    'audio_file': f"{valence}_music.wav",
                    'block_type': None, 'block_number': None, 'trial_number': stmt_num + 1,
                    'stimulus': None, 'stimulus_position': None, 'response': None,
                    'correct_response': None, 'accuracy': None, 'reaction_time': None,
                    'mood_rating': None, 'mw_tut_rating': None, 'mw_fmt_rating': None,
                    'video_file': None,
                    'timestamp': datetime.datetime.now().isoformat()
                })
        
        # Post-induction mood rating
        data_rows.append({
            'participant_code': participant_code,
            'email': email,
            'condition': condition,
            'session_start': start_time,
            'phase': f'mood_rating_post_induction_{block_number}',
            'mood_rating': current_mood + random.uniform(-0.5, 0.5),
            'block_type': None, 'block_number': None, 'trial_number': None,
            'stimulus': None, 'stimulus_position': None, 'response': None,
            'correct_response': None, 'accuracy': None, 'reaction_time': None,
            'mw_tut_rating': None, 'mw_fmt_rating': None, 'velten_rating': None,
            'video_file': None, 'audio_file': None, 'velten_statement': None,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
        # Generate SART block
        base_accuracy = 0.85 if sart_condition == 'NRI' else 0.75  # Lower accuracy for inhibition
        base_rt = 0.55
        
        # Generate trials
        for trial_num in range(1, 121):  # 120 trials
            digit = random.randint(0, 9)
            position = random.choice(['left', 'right'])
            correct_response = position
            
            # Determine if this is a target trial (inhibition condition only)
            is_target = (digit == 3 and sart_condition == 'RI')
            if is_target:
                correct_response = None
            
            # Simulate response
            if is_target:
                # Target trial - should not respond
                accuracy = 1 if random.random() > 0.2 else 0  # 80% correct inhibition
                response = None if accuracy == 1 else position
                rt = None if response is None else base_rt + random.uniform(-0.1, 0.3)
            else:
                # Non-target trial - should respond
                accuracy = 1 if random.random() < base_accuracy else 0
                if accuracy == 1:
                    response = correct_response
                    rt = base_rt + random.uniform(-0.2, 0.4)
                else:
                    response = 'left' if correct_response == 'right' else 'right'
                    rt = base_rt + random.uniform(0.1, 0.6)
            
            # Add trial data
            data_rows.append({
                'participant_code': participant_code,
                'email': email,
                'condition': condition,
                'session_start': start_time,
                'phase': 'sart_task',
                'block_type': sart_condition,
                'block_number': block_number,
                'trial_number': trial_num,
                'stimulus': digit,
                'stimulus_position': position,
                'response': response,
                'correct_response': correct_response,
                'accuracy': accuracy,
                'reaction_time': rt,
                'mood_rating': None, 'mw_tut_rating': None, 'mw_fmt_rating': None,
                'velten_rating': None, 'video_file': None, 'audio_file': None,
                'velten_statement': None,
                'timestamp': datetime.datetime.now().isoformat()
            })
            
            # Add mind-wandering probes occasionally
            if trial_num % 15 == 0:  # Every 15 trials
                tut_rating = random.randint(2, 6)
                fmt_rating = random.randint(2, 6)
                
                data_rows.append({
                    'participant_code': participant_code,
                    'email': email,
                    'condition': condition,
                    'session_start': start_time,
                    'phase': 'mind_wandering_probe',
                    'block_type': sart_condition,
                    'block_number': block_number,
                    'trial_number': trial_num,
                    'mw_tut_rating': tut_rating,
                    'mw_fmt_rating': fmt_rating,
                    'stimulus': None, 'stimulus_position': None, 'response': None,
                    'correct_response': None, 'accuracy': None, 'reaction_time': None,
                    'mood_rating': None, 'velten_rating': None, 'video_file': None,
                    'audio_file': None, 'velten_statement': None,
                    'timestamp': datetime.datetime.now().isoformat()
                })
    
    return data_rows

def create_sample_dataset(num_participants=3):
    """Create sample dataset with multiple participants"""
    
    print(f"Creating sample dataset with {num_participants} participants...")
    
    # Create data directory if it doesn't exist
    config.DATA_DIR.mkdir(exist_ok=True)
    
    all_data = []
    
    for participant_id in range(1, num_participants + 1):
        condition = ((participant_id - 1) % 4) + 1  # Cycle through conditions 1-4
        print(f"Generating participant {participant_id} (condition {condition})...")
        
        participant_data = generate_sample_participant_data(participant_id, condition)
        all_data.extend(participant_data)
        
        # Save individual participant file
        participant_filename = config.DATA_DIR / f"participant_MOOD_SART_TEST_{participant_id:03d}_sample.csv"
        
        headers = [
            'participant_code', 'email', 'condition', 'session_start',
            'phase', 'block_type', 'block_number', 'trial_number',
            'stimulus', 'stimulus_position', 'response', 'correct_response',
            'accuracy', 'reaction_time', 'timestamp',
            'mood_rating', 'mw_tut_rating', 'mw_fmt_rating', 'velten_rating',
            'video_file', 'audio_file', 'velten_statement'
        ]
        
        with open(participant_filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for row in participant_data:
                writer.writerow(row)
        
        print(f"  Created: {participant_filename}")
    
    # Save combined file
    combined_filename = config.DATA_DIR / "combined_sample_data.csv"
    
    headers = [
        'participant_code', 'email', 'condition', 'session_start',
        'phase', 'block_type', 'block_number', 'trial_number',
        'stimulus', 'stimulus_position', 'response', 'correct_response',
        'accuracy', 'reaction_time', 'timestamp',
        'mood_rating', 'mw_tut_rating', 'mw_fmt_rating', 'velten_rating',
        'video_file', 'audio_file', 'velten_statement'
    ]
    
    with open(combined_filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in all_data:
            writer.writerow(row)
    
    print(f"Created combined file: {combined_filename}")
    print(f"Total rows: {len(all_data)}")
    
    return combined_filename

def main():
    """Main function"""
    try:
        combined_file = create_sample_dataset(3)
        
        print("\n" + "="*50)
        print("SAMPLE DATA CREATION COMPLETE!")
        print("="*50)
        print(f"Files created in: {config.DATA_DIR}")
        print("\nNow you can test the data analyzer:")
        print(f"python scripts/data_analyzer.py --data_file {combined_file}")
        print("python scripts/data_analyzer.py --combine --data_dir data/")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 