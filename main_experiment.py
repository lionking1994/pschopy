#!/usr/bin/env python3
"""
PsychoPy Experiment: Mood Induction + SART Study (SIMPLIFIED VERSION)
Uses modern PsychoPy components with keyboard-based input to avoid GUI dialog issues.
This version addresses all known issues and works in headless environments.

Author: Generated for Nate Speert Lab Study
Date: 2024
"""

import os
# Configure audio environment for proper audio support
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
# Allow audio backends to work properly
if 'SDL_AUDIODRIVER' in os.environ:
    del os.environ['SDL_AUDIODRIVER']
if 'SDL_AUDIO_DRIVER' in os.environ:
    del os.environ['SDL_AUDIO_DRIVER']

import sys
import random
import csv
import datetime
from pathlib import Path
import numpy as np

# Add config and scripts directories to path
sys.path.append(str(Path(__file__).parent / 'config'))
sys.path.append(str(Path(__file__).parent / 'scripts'))

from psychopy import visual, core, event, sound
from psychopy.hardware import keyboard
import experiment_config as config
from video_preloader import VideoPreloader, create_loading_screen

class MoodSARTExperimentSimple:
    """SIMPLIFIED version of the Mood Induction + SART experiment avoiding GUI dialogs"""
    
    def __init__(self):
        """Initialize the experiment"""
        # Check if demo mode is enabled
        if config.DEMO_MODE:
            print("🎯 DEMO MODE ACTIVE:")
            print(f"   📊 SART blocks: {config.SART_PARAMS['trials_per_block']} trials each (shortened)")
            print(f"   📝 Velten statements: 3 per phase (shortened from 12)")
            print(f"   ⏱️  Velten duration: {config.TIMING['velten_statement_duration']}s per statement (same as main)")
            print(f"   🧠 MW probes: Every {config.SART_PARAMS['probe_interval_min']}-{config.SART_PARAMS['probe_interval_max']} trials (same as main)")
            print(f"   🎬 Videos and other phases: Same as main experiment")
            print()
        
        self.setup_experiment()
        self.setup_stimuli()
        self.setup_video_preloader()
        
        # UPDATED: Track Velten statement set usage for proper counterbalancing
        self.velten_phase_counter = {'positive': 0, 'negative': 0}  # Track which set to use
        
        # Initialize participant data variables (will be set up later)
        self.participant_data = {}
        self.data_filename = None
        
    def setup_experiment(self):
        """Set up PsychoPy window and basic experiment parameters"""
        # Create window - FIXED: Use windowed mode and enable GUI
        # Mac-specific window initialization to reduce HID errors
        screen_params = {
            'size': config.SCREEN_PARAMS['size'],
            'fullscr': config.SCREEN_PARAMS['fullscr'],
            'color': config.SCREEN_PARAMS['color'],
            'units': config.SCREEN_PARAMS['units'],
            'allowGUI': config.SCREEN_PARAMS['allowGUI'],
            'winType': config.SCREEN_PARAMS.get('winType', 'pyglet')
        }
        
        if config.IS_MAC:
            # Additional Mac-specific settings to reduce HID and timing issues
            screen_params.update({
                'allowStencil': False,
                'monitor': None,  # Let PsychoPy auto-detect
                'waitBlanking': config.SCREEN_PARAMS.get('waitBlanking', True),
                'useFBO': config.SCREEN_PARAMS.get('useFBO', False),
                'checkTiming': config.SCREEN_PARAMS.get('checkTiming', False)
            })
            print("🍎 Mac detected - using Mac-optimized settings")
        
        self.win = visual.Window(**screen_params)
        
        # Set up keyboard with Mac-specific handling
        if config.IS_MAC:
            # Mac-specific keyboard setup to reduce HID errors
            try:
                self.kb = keyboard.Keyboard()
                print("🍎 Mac keyboard initialized successfully")
            except Exception as e:
                print(f"🍎 Mac keyboard warning (continuing anyway): {e}")
                self.kb = keyboard.Keyboard()  # Try again
        else:
            self.kb = keyboard.Keyboard()
        
        # Mac-specific timing setup
        if config.IS_MAC:
            # Disable frame interval recording on Mac to reduce timing warnings
            self.win.recordFrameIntervals = False
            print("🍎 Mac timing optimizations applied")
        
        # Set up clocks
        self.global_clock = core.Clock()
        self.trial_clock = core.Clock()
        
        # Initialize experiment variables
        self.trial_data = []
        self.current_block = 0
        self.probe_counter = 0
        
    def setup_stimuli(self):
        """Set up visual and audio stimuli using modern PsychoPy components"""
        # Text stimuli - FIXED: Left-aligned text
        self.instruction_text = visual.TextStim(
            win=self.win,
            text='',
            font=config.TEXT_STYLE['font'],
            height=config.TEXT_STYLE['height'],
            color=config.TEXT_STYLE['color'],
            wrapWidth=config.TEXT_STYLE['wrapWidth'],
            pos=(-400, 0),  # FIXED: Move text to left side of screen
            alignText=config.TEXT_STYLE.get('alignText', 'left'),  # FIXED: Left align
            anchorHoriz=config.TEXT_STYLE.get('anchorHoriz', 'left')  # FIXED: Anchor left
        )
         
        # Centered text stimulus for Velten statements
        self.velten_text = visual.TextStim(
            win=self.win,
            text='',
            font=config.VELTEN_TEXT_STYLE['font'],
            height=config.VELTEN_TEXT_STYLE['height'],
            color=config.VELTEN_TEXT_STYLE['color'],
            wrapWidth=config.VELTEN_TEXT_STYLE['wrapWidth'],
            pos=config.VELTEN_TEXT_STYLE['pos'],
            alignText=config.VELTEN_TEXT_STYLE.get('alignText', 'center'),
            anchorHoriz=config.VELTEN_TEXT_STYLE.get('anchorHoriz', 'center')
        )
        
        # SART stimuli
        self.fixation = visual.TextStim(
            win=self.win,
            text='+',
            font=config.TEXT_STYLE['font'],
            height=40,
            color=config.TEXT_STYLE['color'],
            pos=(0, 0)
        )
        
        self.digit_stim = visual.TextStim(
            win=self.win,
            text='',
            font=config.TEXT_STYLE['font'],
            height=60,
            color=config.TEXT_STYLE['color'],
            pos=(0, 0)
        )
        
        # Condition cue circles
        self.inhibition_cue = visual.Circle(
            win=self.win,
            radius=config.CONDITION_CUES['inhibition']['radius'],
            pos=config.CONDITION_CUES['inhibition']['pos'],
            fillColor=config.CONDITION_CUES['inhibition']['color'],
            lineColor=config.CONDITION_CUES['inhibition']['color']
        )
        
        self.non_inhibition_cue = visual.Circle(
            win=self.win,
            radius=config.CONDITION_CUES['non_inhibition']['radius'],
            pos=config.CONDITION_CUES['non_inhibition']['pos'],
            fillColor=config.CONDITION_CUES['non_inhibition']['color'],
            lineColor=config.CONDITION_CUES['non_inhibition']['color']
        )
        
        # MODERN: Mood rating slider (replaces RatingScale) - Neutral colors as per specification
        self.mood_slider = visual.Slider(
            win=self.win,
            ticks=config.MOOD_SCALE['tick_positions'],
            labels=config.MOOD_SCALE['labels'],
            pos=(0, -200),
            size=(600, 50),
            granularity=config.MOOD_SCALE['granularity'],
            style='slider',  # FIXED: Use 'slider' style for horizontal appearance
            color=[0.5, 0.5, 0.5],     # Neutral gray color
            markerColor=[0.7, 0.7, 0.7],  # Light gray marker for neutral appearance
            lineColor=[0.5, 0.5, 0.5],    # Neutral gray line
            labelColor='white'
            # Note: showValue parameter not supported in this PsychoPy version
        )
        
        # MODERN: Mind-wandering probe sliders - 7-point discrete scales (no line, smaller height for smaller marker)
        self.mw_tut_slider = visual.Slider(
            win=self.win,
            ticks=list(range(config.MW_PROBES['scale_range'][0], config.MW_PROBES['scale_range'][1] + 1)),
            labels=config.MW_PROBES['scale_labels'],
            pos=(0, -100),
            size=(500, 30),  # Smaller height to reduce marker size
            granularity=1,   # Force discrete integer values
            style='rating',  # Discrete tick selection
            color=[-1, -1, -1],      # Black color (invisible against black background)
            markerColor=[1, 0, 0],   # Red marker for visibility
            lineColor=[-1, -1, -1],  # Black line (invisible against black background)
            labelColor='white',
            labelHeight=16
        )
        
        self.mw_fmt_slider = visual.Slider(
            win=self.win,
            ticks=list(range(config.MW_PROBES['scale_range'][0], config.MW_PROBES['scale_range'][1] + 1)),
            labels=config.MW_PROBES['scale_labels'],
            pos=(0, -100),
            size=(500, 30),  # Smaller height to reduce marker size
            granularity=1,   # Force discrete integer values
            style='rating',  # Discrete tick selection
            color=[-1, -1, -1],      # Black color (invisible against black background)
            markerColor=[1, 0, 0],   # Red marker for visibility
            lineColor=[-1, -1, -1],  # Black line (invisible against black background)
            labelColor='white'
        )
        
        # UPDATED: 7-point scale slider matching attached image design (no line, smaller marker)
        self.velten_slider = visual.Slider(
            win=self.win,
            ticks=config.VELTEN_RATING_SCALE['tick_positions'],  # [1, 2, 3, 4, 5, 6, 7]
            labels=config.VELTEN_RATING_SCALE['scale_labels'],
            pos=(0, -200),  # Lower position for better visibility
            size=(700, 40),  # Smaller height to reduce marker size
            granularity=1,  # Force discrete integer values only (1, 2, 3, 4, 5, 6, 7)
            style='rating',  # Use rating style for discrete tick selection
            color=[-1, -1, -1],      # Black color (invisible against black background)
            markerColor=[1, 0, 0],   # Red marker for visibility
            lineColor=[-1, -1, -1],  # Black line (invisible against black background)
            labelColor='white',
            labelHeight=18,  # Readable label text
            flip=False,  # Ensure proper orientation
            readOnly=False
        )
        
        # Create custom tick marks with different heights
        self.create_custom_tick_marks()
        
        # Initialize audio (will be loaded as needed)
        self.current_audio = None
        
        # Preload audio for instant playback
        self.preload_audio_files()
    
    def create_custom_tick_marks(self):
        """Create custom tick marks with different heights and white horizontal line for 7-point scales"""
        # Velten slider custom ticks (position: 0, -200, size: 700x40)
        self.velten_tick_marks = []
        slider_width = 700
        slider_x = 0  # Center position
        slider_y = -200
        
        # Create horizontal line connecting all ticks
        line_start_x = slider_x - (slider_width / 2)
        line_end_x = slider_x + (slider_width / 2)
        self.velten_horizontal_line = visual.Line(
            win=self.win,
            start=(line_start_x, slider_y),
            end=(line_end_x, slider_y),
            lineColor=[1, 1, 1],  # White color
            lineWidth=2  # Thin line
        )
        
        # Calculate positions for 7 ticks
        tick_positions = []
        for i in range(7):
            x_pos = slider_x - (slider_width / 2) + (i * slider_width / 6)
            tick_positions.append(x_pos)
        
        # Add text labels at start and end ticks for Velten slider
        self.velten_start_label = visual.TextStim(
            win=self.win,
            text="Not at all",
            pos=(tick_positions[0], slider_y - 60),  # Below the first tick
            color=[1, 1, 1],  # White color
            height=config.TEXT_STYLE['height'],  # Same as instruction text
            alignText='center',
            font=config.TEXT_STYLE['font']  # Same font as instruction text
        )
        self.velten_end_label = visual.TextStim(
            win=self.win,
            text="Completely",
            pos=(tick_positions[6], slider_y - 60),  # Below the last tick
            color=[1, 1, 1],  # White color
            height=config.TEXT_STYLE['height'],  # Same as instruction text
            alignText='center',
            font=config.TEXT_STYLE['font']  # Same font as instruction text
        )
        
        # Create tick marks with different heights (start/end longer, middle shorter)
        for i, x_pos in enumerate(tick_positions):
            if i == 0 or i == 6:  # Start and end ticks (longer)
                tick_height = 40
            else:  # Middle ticks (shorter)
                tick_height = 25
            
            tick_mark = visual.Line(
                win=self.win,
                start=(x_pos, slider_y - tick_height/2),
                end=(x_pos, slider_y + tick_height/2),
                lineColor=[1, 1, 1],  # White color
                lineWidth=3
            )
            self.velten_tick_marks.append(tick_mark)
        
        # MW probe sliders custom ticks (position: 0, -100, size: 500x30)
        self.mw_tick_marks = []
        mw_slider_width = 500
        mw_slider_x = 0  # Center position
        mw_slider_y = -100
        
        # Create horizontal line connecting all MW ticks
        mw_line_start_x = mw_slider_x - (mw_slider_width / 2)
        mw_line_end_x = mw_slider_x + (mw_slider_width / 2)
        self.mw_horizontal_line = visual.Line(
            win=self.win,
            start=(mw_line_start_x, mw_slider_y),
            end=(mw_line_end_x, mw_slider_y),
            lineColor=[1, 1, 1],  # White color
            lineWidth=2  # Thin line
        )
        
        # Calculate positions for 7 ticks
        mw_tick_positions = []
        for i in range(7):
            x_pos = mw_slider_x - (mw_slider_width / 2) + (i * mw_slider_width / 6)
            mw_tick_positions.append(x_pos)
        
        # Add text labels at start and end ticks for MW probe sliders
        self.mw_start_label = visual.TextStim(
            win=self.win,
            text="Not at all",
            pos=(mw_tick_positions[0], mw_slider_y - 50),  # Below the first tick
            color=[1, 1, 1],  # White color
            height=config.TEXT_STYLE['height'],  # Same as instruction text
            alignText='center',
            font=config.TEXT_STYLE['font']  # Same font as instruction text
        )
        self.mw_end_label = visual.TextStim(
            win=self.win,
            text="Very much",
            pos=(mw_tick_positions[6], mw_slider_y - 50),  # Below the last tick
            color=[1, 1, 1],  # White color
            height=config.TEXT_STYLE['height'],  # Same as instruction text
            alignText='center',
            font=config.TEXT_STYLE['font']  # Same font as instruction text
        )
        
        # Create MW tick marks with different heights (start/end longer, middle shorter)
        for i, x_pos in enumerate(mw_tick_positions):
            if i == 0 or i == 6:  # Start and end ticks (longer)
                tick_height = 30
            else:  # Middle ticks (shorter)
                tick_height = 18
            
            tick_mark = visual.Line(
                win=self.win,
                start=(x_pos, mw_slider_y - tick_height/2),
                end=(x_pos, mw_slider_y + tick_height/2),
                lineColor=[1, 1, 1],  # White color
                lineWidth=2
            )
            self.mw_tick_marks.append(tick_mark)
        
    def preload_audio_files(self):
        """Preload audio files for instant playback during experiment"""
        self.preloaded_audio = {}
        print("🎵 Preloading audio files...")
        
        for audio_key, audio_path in config.AUDIO_FILES.items():
            if audio_path.exists():
                try:
                    # Try pygame first (usually faster)
                    import pygame.mixer
                    if not pygame.mixer.get_init():
                        # Mac-specific audio configuration for better compatibility
                        if config.IS_MAC:
                            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
                        else:
                            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
                        pygame.mixer.init()
                    
                    self.preloaded_audio[audio_key] = pygame.mixer.Sound(str(audio_path))
                    print(f"  ✓ {audio_key}")
                    
                except Exception as e:
                    try:
                        # Fallback to PsychoPy
                        self.preloaded_audio[audio_key] = sound.Sound(str(audio_path))
                        print(f"  ✓ {audio_key} (PsychoPy)")
                    except Exception as e2:
                        print(f"  ✗ Failed: {audio_key} - {str(e2)[:50]}...")
                        # Create a placeholder to avoid errors
                        self.preloaded_audio[audio_key] = None
        
    def setup_video_preloader(self):
        """Set up video preloader to fix loading delays"""
        self.video_preloader = VideoPreloader(self.win)
        
    def setup_data_collection(self):
        """Set up data collection and file handling"""
        # Get participant info using keyboard input
        self.get_participant_info()
        
        # Create data directory if it doesn't exist
        config.DATA_DIR.mkdir(exist_ok=True)
        config.DATA_PARAMS['backup_dir'].mkdir(exist_ok=True)
        
        # Generate timestamp and filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.data_filename = config.DATA_DIR / config.DATA_PARAMS['data_filename_template'].format(
            code=self.participant_data['participant_code'],
            timestamp=timestamp
        )
        
        # Initialize CSV file with headers
        self.init_csv_file()
        
    def get_participant_info(self):
        """Get participant information through keyboard input (no GUI)"""
        # Get email address using keyboard input (as per specification)
        email = self.get_text_input("Enter the email address you provided when completing the consent form:")
        
        # Get counterbalancing order selection from user
        condition = self.get_counterbalancing_order()
        
        # Generate participant code
        participant_code = config.DATA_PARAMS['participant_code_prefix'] + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.participant_data = {
            'email': email,
            'participant_code': participant_code,
            'condition': condition,
            'start_time': datetime.datetime.now().isoformat(),
            'counterbalancing': config.COUNTERBALANCING_ORDERS[condition]
        }
        
    def get_counterbalancing_order(self):
        """Get counterbalancing order selection from user (1-4)"""
        self.instruction_text.text = """Please select the counterbalancing order for this participant:

1 - Order 1: V(+) → V(+) → M(-) → M(-)
2 - Order 2: M(-) → M(-) → V(+) → V(+) 
3 - Order 3: V(-) → V(-) → M(+) → M(+)
4 - Order 4: M(+) → M(+) → V(-) → V(-)

Where:
V = Velten statements, M = Movie clips
(+) = Positive mood, (-) = Negative mood

Press 1, 2, 3, or 4 to select the order:"""
        
        self.instruction_text.draw()
        self.win.flip()
        
        # Wait for valid input (1-4)
        while True:
            keys = event.waitKeys()
            if keys:
                key = keys[0]
                if key in ['1', '2', '3', '4']:
                    condition = int(key)
                    print(f"Selected counterbalancing order: {condition}")
                    return condition
                elif key == 'escape':
                    core.quit()
        
    def get_text_input(self, prompt):
        """Get text input using keyboard - Normal typing for email addresses"""
        input_text = ""
        
        while True:
            # Display current input with normal instructions
            display_text = f"{prompt}\n\nInput: {input_text}_\n\nPress ENTER when done, BACKSPACE to delete\nType normally - Shift+2 for @, period key for ."
            self.instruction_text.text = display_text
            self.instruction_text.draw()
            self.win.flip()
            
            # Use event.waitKeys with modifiers check for proper symbol handling
            keys = event.waitKeys(modifiers=True)
            
            for key_info in keys:
                if isinstance(key_info, tuple):
                    key, modifiers = key_info
                else:
                    key = key_info
                    modifiers = []
                
                if key == 'return':
                    if input_text.strip():
                        return input_text.strip()
                elif key == 'escape':
                    core.quit()
                elif key == 'backspace':
                    input_text = input_text[:-1]
                elif key == 'space':
                    input_text += ' '
                elif key == '2' and ('shift' in modifiers or 'lshift' in modifiers or 'rshift' in modifiers):
                    # Handle Shift+2 = @
                    input_text += '@'
                elif key == 'period':
                    input_text += '.'
                elif key == 'minus':
                    input_text += '-'
                elif key == 'at' or key == '@':
                    input_text += '@'
                elif len(key) == 1 and key.isalnum():
                    # Add letters and numbers
                    input_text += key
            
            # Small delay to prevent excessive CPU usage
            core.wait(0.01)
    
    def get_number_input(self, prompt, min_val, max_val):
        """Get number input using keyboard"""
        self.instruction_text.text = f"{prompt}\nPress number keys {min_val}-{max_val}:"
        self.instruction_text.draw()
        self.win.flip()
        
        while True:
            keys = event.waitKeys()
            for key in keys:
                if key == 'escape':
                    core.quit()
                elif key.isdigit():
                    num = int(key)
                    if min_val <= num <= max_val:
                        return num
        
    def init_csv_file(self):
        """Initialize CSV file with headers"""
        headers = [
            'participant_code', 'email', 'condition', 'session_start',
            'phase', 'block_type', 'block_number', 'trial_number',
            'stimulus', 'stimulus_position', 'response', 'correct_response',
            'accuracy', 'reaction_time', 'timestamp',
            'mood_rating', 'mw_tut_rating', 'mw_fmt_rating', 'velten_rating',
            'video_file', 'audio_file', 'velten_statement'
        ]
        
        with open(self.data_filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
    
    def save_trial_data(self, trial_data):
        """Save trial data to CSV file"""
        # Check if participant data is available yet
        if not self.participant_data or not self.data_filename:
            return  # Skip saving if participant info is not yet collected
            
        # Add participant info to trial data
        full_data = {
            'participant_code': self.participant_data['participant_code'],
            'email': self.participant_data['email'],
            'condition': self.participant_data['condition'],
            'session_start': self.participant_data['start_time'],
            'timestamp': datetime.datetime.now().isoformat(),
            **trial_data
        }
        
        # Write to CSV
        with open(self.data_filename, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=full_data.keys())
            writer.writerow(full_data)
    
    def show_instruction(self, instruction_key, wait_for_key=True, condition_cue=None):
        """Display instruction screen - FIXED: Can show condition indicators for SART"""
        instruction = config.INSTRUCTIONS[instruction_key]
        self.instruction_text.text = instruction['text']
        self.instruction_text.draw()
        
        # FIXED: Draw condition cue if provided (for SART instructions)
        if condition_cue:
            condition_cue.draw()
        
        self.win.flip()
        
        if wait_for_key:
            event.waitKeys()
    
    def collect_mood_rating(self, phase):
        """MODERN: Collect mood rating using Slider component with mouse click to advance"""
        print(f"📊 COLLECTING MOOD RATING: {phase}")
        self.instruction_text.text = config.INSTRUCTIONS['mood_rating']['text'] + "\n\nClick anywhere to continue after making your selection."
        self.mood_slider.reset()
        
        rating_selected = False
        mouse = event.Mouse(win=self.win)
         
        # Show slider and wait for rating + mouse click
        while True:
            self.instruction_text.draw()
            self.mood_slider.draw()
            self.win.flip()
            
            # Check if rating has been made
            if self.mood_slider.getRating() is not None and not rating_selected:
                rating_selected = True
                print(f"📝 Rating selected: {self.mood_slider.getRating()}")
            
            # Check for mouse click after rating is selected
            if rating_selected and mouse.getPressed()[0]:  # Left mouse button
                break
            
            # Check for escape
            if 'escape' in event.getKeys():
                core.quit()
        
        rating = self.mood_slider.getRating()
        
        # Print mood rating to console
        print(f"😊 Mood Rating ({phase}): {rating}/100")
        print(f"✅ Mood rating collection completed")
        
        # Save mood rating data
        self.save_trial_data({
            'phase': f'mood_rating_{phase}',
            'mood_rating': rating,
            'block_type': None, 'block_number': None, 'trial_number': None,
            'stimulus': None, 'stimulus_position': None, 'response': None,
            'correct_response': None, 'accuracy': None, 'reaction_time': None,
            'mw_tut_rating': None, 'mw_fmt_rating': None, 'velten_rating': None,
            'video_file': None, 'audio_file': None, 'velten_statement': None
        })
        
        return rating
    
    def collect_mood_rating_keyboard(self, phase):
        """Fallback: Collect mood rating using keyboard input (1-9)"""
        prompt = f"{config.INSTRUCTIONS['mood_rating']['text']}\n\nPress keys 1-9 (1=Very Negative, 5=Neutral, 9=Very Positive):"
        self.instruction_text.text = prompt
        self.instruction_text.draw()
        self.win.flip()
        
        while True:
            keys = event.waitKeys()
            for key in keys:
                if key == 'escape':
                    core.quit()
                elif key.isdigit() and 1 <= int(key) <= 9:
                    rating = int(key)
                    
                    # Save mood rating data
                    self.save_trial_data({
                        'phase': f'mood_rating_{phase}',
                        'mood_rating': rating,
                        'block_type': None, 'block_number': None, 'trial_number': None,
                        'stimulus': None, 'stimulus_position': None, 'response': None,
                        'correct_response': None, 'accuracy': None, 'reaction_time': None,
                        'mw_tut_rating': None, 'mw_fmt_rating': None, 'velten_rating': None,
                        'video_file': None, 'audio_file': None, 'velten_statement': None
                    })
                    
                    return rating
    
    def play_video(self, video_key, instruction_key=None):
        """Play video stimulus using preloaded videos"""
        # Show instruction if provided
        if instruction_key:
            self.show_instruction(instruction_key)
        
        # Try to get preloaded video first
        video = self.video_preloader.get_preloaded_video(video_key)
        
        if video is None:
            # Fallback to loading video on demand
            video_path = config.VIDEO_FILES[video_key]
            if not video_path.exists():
                print(f"Warning: Video file {video_path} not found. Creating placeholder.")
                self.show_video_placeholder(video_key)
                return
            
            try:
                # Try different video components based on availability
                video = None
                video_errors = []
                
                # Try MovieStim3 first
                try:
                    video = visual.MovieStim3(
                        win=self.win,
                        filename=str(video_path),
                        size=(800, 600),
                        pos=(0, 0),
                        loop=False,
                        autoStart=False
                    )
                except Exception as e:
                    video_errors.append(f"MovieStim3: {str(e)[:60]}...")
                    
                    # Fallback to MovieStim
                    try:
                        video = visual.MovieStim(
                            win=self.win,
                            filename=str(video_path),
                            size=(800, 600),
                            pos=(0, 0),
                            loop=False,
                            autoStart=False
                        )
                    except Exception as e:
                        video_errors.append(f"MovieStim: {str(e)[:60]}...")
                
                if video is None:
                    print(f"Cannot load video {video_path}")
                    for error in video_errors:
                        print(f"  - {error}")
                    self.show_video_placeholder(video_key)
                    return
                    
            except Exception as e:
                print(f"Unexpected error loading video {video_path}: {e}")
                self.show_video_placeholder(video_key)
                return
        
        # Play video
        try:
            print(f"🎬 Starting video playback: {video_key}")
            print(f"🔍 Initial video status: {video.status}")
            video_skipped = False
            frame_count = 0
            
            # Add safety limit to prevent infinite loops
            max_frames = 18000  # About 10 minutes at 30fps - way more than any video should be
            
            video_naturally_ended = False
            consecutive_same_status = 0
            last_status = video.status
            
            # Get video duration if available
            video_duration = None
            try:
                if hasattr(video, 'duration') and video.duration:
                    video_duration = video.duration
                    print(f"📏 Video duration: {video_duration:.1f} seconds")
            except:
                pass
            
            # CRITICAL: Explicitly start video playback
            video.play()
            print("▶️ Video.play() called - starting playback")
            
            while True:
                # CRITICAL: Only draw video - NO TEXT during playback
                video.draw()
                self.win.flip()
                frame_count += 1
                
                current_status = video.status
                
                # Track status changes
                if current_status == last_status:
                    consecutive_same_status += 1
                else:
                    print(f"📝 Status changed from {last_status} to {current_status} at frame {frame_count}")
                    consecutive_same_status = 0
                    last_status = current_status
                
                # Debug every 60 frames (about 2 seconds at 30fps)
                if frame_count % 60 == 0:
                    current_time = frame_count / 30.0
                    print(f"🎞️ Frame {frame_count}: Video status = {current_status}")
                    print(f"   Current time: {current_time:.1f}s")
                    if video_duration:
                        progress_pct = (current_time / video_duration) * 100
                        remaining_time = video_duration - current_time
                        print(f"   Progress: {progress_pct:.1f}% of {video_duration:.1f}s (remaining: {remaining_time:.1f}s)")
                
                # Check for escape key during playback
                keys = event.getKeys()
                if 'escape' in keys:
                    video_skipped = True
                    print(f"🔄 Video skipped by user (ESC pressed) at frame {frame_count}")
                    break
                
                # Method 1: Check if status changed to FINISHED
                if current_status == visual.FINISHED:
                    video_naturally_ended = True
                    print(f"✅ Video status changed to FINISHED at frame {frame_count}")
                    break
                
                # Method 2: Use video duration if available - wait for FULL duration
                if video_duration:
                    estimated_current_time = frame_count / 30.0  # Assume 30fps
                    # Only consider video finished if we're past the actual duration
                    if estimated_current_time >= video_duration:  # Wait for full duration
                        video_naturally_ended = True
                        print(f"✅ Video reached full duration ({estimated_current_time:.1f}s >= {video_duration:.1f}s)")
                        break
                
                # Method 3: Detect if video appears to be looping - but ONLY after full expected duration
                # Don't assume looping until we're well past the expected end time
                if video_duration:
                    # Only check for looping after we're past the full duration + buffer
                    expected_frames = int(video_duration * 30)  # Full expected duration in frames
                    buffer_frames = 300  # 10 seconds buffer after expected end
                    
                    if frame_count > (expected_frames + buffer_frames) and consecutive_same_status > 300:
                        print(f"🔄 Video playing beyond expected duration + buffer")
                        print(f"   Expected end: {video_duration:.1f}s ({expected_frames} frames)")
                        print(f"   Current time: {frame_count / 30.0:.1f}s ({frame_count} frames)")
                        print(f"   Status unchanged for: {consecutive_same_status} frames")
                        video_naturally_ended = True
                        print(f"✅ Assuming video finished - playing beyond expected duration")
                        break
                else:
                    # Fallback if no duration available - use longer time limits
                    if consecutive_same_status > 1800 and frame_count > 7200:  # 1 minute unchanged after 4 minutes
                        print(f"🔄 Video status unchanged for {consecutive_same_status} frames after {frame_count} total frames")
                        video_naturally_ended = True
                        print(f"✅ Assuming video finished due to long static status")
                        break
                
                # Safety: Absolute maximum to prevent infinite loops
                if frame_count >= max_frames:
                    print(f"🔄 Safety limit reached at {frame_count} frames")
                    video_naturally_ended = True
                    break
            
            print(f"📝 Video playback ended - Status: {video.status}, Skipped: {video_skipped}, Frames: {frame_count}")
            print(f"   - Naturally ended: {video_naturally_ended}")
            print(f"🔍 Video status constants - FINISHED: {visual.FINISHED}")
            
            # CRITICAL: Only show completion text if video has ACTUALLY finished
            # Be very strict about this to prevent text appearing during playback
            should_show_completion = (video_naturally_ended or video_skipped) and frame_count > 60
            
            if should_show_completion:
                print("✅ Video has ACTUALLY finished - NOW showing completion message...")
                print(f"   - Video naturally ended: {video_naturally_ended}")
                print(f"   - Video was skipped: {video_skipped}")
                print(f"   - Total frames played: {frame_count}")
                
                # CRITICAL: Stop the video completely to freeze on final frame
                print("🛑 Stopping video to freeze final frame...")
                try:
                    if hasattr(video, 'stop'):
                        video.stop()
                        print("✅ Video.stop() called")
                    if hasattr(video, 'pause'):
                        video.pause()
                        print("✅ Video.pause() called")
                except Exception as e:
                    print(f"⚠️ Could not stop video: {e}")
                
                # Wait longer for video to completely stop
                print("⏳ Waiting for video to fully stop...")
                core.wait(0.5)
                
                # Verify video has stopped by checking status
                final_status = video.status
                print(f"🔍 Final video status after stopping: {final_status}")
                
                # Now draw the FINAL STATIC frame with completion text
                self.instruction_text.text = "Video completed.\n\nPress ESC key to continue..."
                self.instruction_text.pos = (0, -200)  # Below video
                self.instruction_text.color = [1, 1, 1]  # White text
                print(f"🔍 Text properties - Color: {self.instruction_text.color}, Pos: {self.instruction_text.pos}")
                
                print("🎨 Drawing FINAL STATIC frame with completion text...")
                print("   ⚠️  IMPORTANT: Video should be completely stopped now")
                
                # Draw the stopped video frame
                try:
                    video.draw()
                    print("✅ Final STATIC video frame drawn")
                except Exception as e:
                    print(f"⚠️ Could not draw final frame: {e}")
                
                # Draw completion text over the STATIC frame
                try:
                    self.instruction_text.draw()
                    print("✅ Completion text drawn over STATIC frame")
                except Exception as e:
                    print(f"❌ Could not draw text: {e}")
                
                # Display the final result
                self.win.flip()
                print("💡 FINAL RESULT: STATIC video frame + completion text should now be visible")
                print("👀 Check the window - you should see:")
                print("   1. A COMPLETELY STATIC (not moving) video frame")
                print("   2. White text saying 'Video completed. Press ESC key to continue...'")
                print("   3. NO MOVEMENT in the video")
            else:
                print("❌ Video did not properly finish - NOT showing completion text")
                print("   This prevents text from appearing while video is still playing")
                print(f"   - Video naturally ended: {video_naturally_ended}")
                print(f"   - Video was skipped: {video_skipped}")
                print(f"   - Frame count: {frame_count}")
                return  # Exit without showing completion text
            
            # Stop the video after displaying the message
            if hasattr(video, 'stop'):
                try:
                    video.stop()
                    print("🛑 Video stopped")
                except Exception as e:
                    print(f"⚠️ Could not stop video: {e}")
            
            # Wait for escape key specifically
            print("⏳ Waiting for ESC key press...")
            while True:
                keys = event.waitKeys()
                if keys and 'escape' in keys:
                    print("✅ ESC pressed - continuing experiment")
                    break
            
            # Reset text position to original left-aligned position
            self.instruction_text.pos = (-400, 0)
                        
        except Exception as e:
            print(f"Error playing video: {e}")
            self.show_video_placeholder(video_key)
        
        # Save video data
        self.save_trial_data({
            'phase': 'video_stimulus',
            'video_file': str(config.VIDEO_FILES[video_key]),
            'block_type': None, 'block_number': None, 'trial_number': None,
            'stimulus': None, 'stimulus_position': None, 'response': None,
            'correct_response': None, 'accuracy': None, 'reaction_time': None,
            'mood_rating': None, 'mw_tut_rating': None, 'mw_fmt_rating': None,
            'velten_rating': None, 'audio_file': None, 'velten_statement': None
        })
    
    def show_video_placeholder(self, video_key):
        """Show placeholder when video file is missing"""
        self.instruction_text.text = f"[VIDEO PLACEHOLDER]\n\n{video_key.upper()}\n\nPress any key to continue..."
        self.instruction_text.draw()
        self.win.flip()
        event.waitKeys()
    
    def load_velten_statements(self, valence):
        """UPDATED: Load Velten statements using new PDF-based structure with Set A/B counterbalancing"""
        # Determine which set to use based on phase counter
        phase_count = self.velten_phase_counter[valence]
        
        # Select appropriate set based on induction phase
        if phase_count == 0:
            # First induction - use Set A
            set_key = f'{valence}_set_a'
            phase_type = 'first_induction'
        else:
            # Re-induction - use Set B
            set_key = f'{valence}_set_b' 
            phase_type = 're_induction'
        
        # Get statements from configuration
        if set_key in config.VELTEN_STATEMENTS:
            statements = config.VELTEN_STATEMENTS[set_key].copy()  # Copy to avoid modifying original
            
            # Randomize order within set as specified in PDF
            random.shuffle(statements)
            
            print(f"Loaded {len(statements)} {valence} statements from {set_key} ({phase_type})")
        else:
            # Fallback to old file-based loading if new structure not available
            statements_file = config.VELTEN_FILES[valence]
            
            if not statements_file.exists():
                # Create placeholder statements if file doesn't exist
                if valence == 'positive':
                    statements = [
                        "I feel really good about myself.",
                        "I am filled with energy and enthusiasm.",
                        "This is one of those days when I feel really happy."
                    ]
                else:  # negative
                    statements = [
                        "I feel rather sluggish now.",
                        "I feel a bit depressed and downhearted.",
                        "I don't feel very confident about myself."
                    ]
                print(f"Using fallback {valence} statements (file not found)")
            else:
                # Load statements from file
                with open(statements_file, 'r') as f:
                    statements = [line.strip() for line in f if line.strip()]
                print(f"Loaded {len(statements)} {valence} statements from file")
        
        # Increment phase counter for next use
        self.velten_phase_counter[valence] += 1
        
        return statements
    
    def run_velten_procedure(self, valence):
        """FIXED: Run Velten self-referential statements with music properly playing"""
        # Show instruction
        self.show_instruction('velten_intro')
        
        # Load statements and audio
        statements = self.load_velten_statements(valence)
        audio_file = config.AUDIO_FILES[f'{valence}_music']
        
        # Instant audio playback using preloaded files
        audio_loaded = False
        self.current_audio = None
        audio_key = f'{valence}_music'
        
        # Try preloaded audio first (instant playback)
        if hasattr(self, 'preloaded_audio') and audio_key in self.preloaded_audio and self.preloaded_audio[audio_key] is not None:
            try:
                self.current_audio = self.preloaded_audio[audio_key]
                self.current_audio.set_volume(0.7)
                self.current_audio.play(loops=-1)
                audio_loaded = True
                print(f"🎵 Audio started instantly: {audio_file.name}")
                
            except Exception as e:
                # If preloaded fails, fall back to loading
                print(f"Preloaded audio failed ({str(e)[:30]}...), loading fresh...")
                
        # Fallback to regular loading if preload unavailable
        if not audio_loaded and audio_file.exists():
            try:
                import pygame.mixer
                if not pygame.mixer.get_init():
                    # Mac-specific audio configuration
                    if config.IS_MAC:
                        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
                    else:
                        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
                    pygame.mixer.init()
                
                self.current_audio = pygame.mixer.Sound(str(audio_file))
                self.current_audio.set_volume(0.7)
                self.current_audio.play(loops=-1)
                audio_loaded = True
                print(f"🎵 Audio loaded: {audio_file.name}")
                
            except Exception as e:
                try:
                    self.current_audio = sound.Sound(str(audio_file))
                    self.current_audio.setVolume(0.7)
                    self.current_audio.play()
                    audio_loaded = True
                    print(f"🎵 Audio loaded (PsychoPy): {audio_file.name}")
                except Exception as e2:
                    print(f"⚠️ Audio unavailable: {str(e2)[:50]}...")
                    self.current_audio = None
        
        # Use fewer statements in demo mode
        if config.DEMO_MODE:
            original_count = len(statements)
            statements = statements[:3]  # Only use first 3 statements in demo
            print(f"📝 Demo mode: Using {len(statements)} statements instead of full set ({original_count} total)")
        
        # Present statements
        for i, statement in enumerate(statements):
            # Show statement for specified duration using centered text
            self.velten_text.text = statement
            self.velten_text.draw()
            self.win.flip()
            
            # Wait for statement duration while keeping audio playing
            core.wait(config.TIMING['velten_statement_duration'])
            
            # UPDATED: Get rating using numbered Likert scale
            rating = self.get_velten_rating_likert()
            
            # Save Velten data
            self.save_trial_data({
                'phase': 'velten_statements',
                'velten_statement': statement,
                'velten_rating': rating,
                'audio_file': str(audio_file) if audio_loaded else None,
                'block_type': None, 'block_number': None, 'trial_number': i + 1,
                'stimulus': None, 'stimulus_position': None, 'response': None,
                'correct_response': None, 'accuracy': None, 'reaction_time': None,
                'mood_rating': None, 'mw_tut_rating': None, 'mw_fmt_rating': None,
                'video_file': None
            })
        
        # FIXED: Properly stop music after all statements
        if self.current_audio and audio_loaded:
            try:
                self.current_audio.stop()
                print("Stopped background music")
            except Exception as e:
                print(f"Error stopping audio: {e}")
            finally:
                self.current_audio = None
    
    def get_velten_rating_keyboard(self):
        """Get Velten rating using keyboard (1-7) - LEGACY FALLBACK"""
        prompt = f"{config.INSTRUCTIONS['velten_rating']['text']}\n\nPress keys 1-7:"
        self.instruction_text.text = prompt
        self.instruction_text.draw()
        self.win.flip()
        
        while True:
            keys = event.waitKeys()
            for key in keys:
                if key == 'escape':
                    core.quit()
                elif key.isdigit() and 1 <= int(key) <= 7:
                    return int(key)
    
    def get_velten_rating_slider(self):
        """UPDATED: Get Velten rating using slider (7-point scale as specified in PDF)"""
        # Display question and slider
        self.instruction_text.text = config.VELTEN_RATING_SCALE['question']
        self.velten_slider.reset()
        
        # Show slider and wait for rating
        while self.velten_slider.getRating() is None:
            self.instruction_text.draw()
            self.velten_slider.draw()
            # Draw horizontal line
            self.velten_horizontal_line.draw()
            # Draw custom tick marks with different heights
            for tick_mark in self.velten_tick_marks:
                tick_mark.draw()
            # Draw text labels at start and end
            self.velten_start_label.draw()
            self.velten_end_label.draw()
            self.win.flip()
            
            # Check for escape
            if 'escape' in event.getKeys():
                core.quit()
        
        rating = self.velten_slider.getRating()
        
        # Print Velten rating to console
        print(f"📝 Velten Statement Rating: {rating}/7 (mood alignment)")
        
        return rating
    
    def get_velten_rating_likert(self):
        """Get Velten rating using numbered Likert scale (1-7)"""
        # Display question with numbered scale
        question_text = config.VELTEN_RATING_SCALE['question']
        scale_text = "\n\n1 = Not at all\n2 = Very little\n3 = A little\n4 = Moderately\n5 = Quite a bit\n6 = Very much\n7 = Completely"
        instruction_text = question_text + scale_text + "\n\nPress a number key (1-7):"
        
        self.instruction_text.text = instruction_text
        self.instruction_text.draw()
        self.win.flip()
        
        # Wait for number key press
        while True:
            keys = event.waitKeys(keyList=['1', '2', '3', '4', '5', '6', '7', 'escape'])
            if keys:
                key = keys[0]
                if key == 'escape':
                    core.quit()
                else:
                    rating = int(key)
                    print(f"📝 Velten Statement Rating: {rating}/7 (mood alignment)")
                    return rating
    
    def run_mind_wandering_probe_likert(self, condition, block_number, trial_number):
        """Present mind-wandering probes using numbered Likert scale"""
        print(f"Presenting mind-wandering probe at trial {trial_number}")
        
        # TUT probe
        tut_question = config.MW_PROBES['tut']
        scale_text = "\n\n1 = Not at all\n2 = Very little\n3 = A little\n4 = Moderately\n5 = Quite a bit\n6 = Very much\n7 = Very much"
        tut_instruction = tut_question + scale_text + "\n\nPress a number key (1-7):"
        
        self.instruction_text.text = tut_instruction
        self.instruction_text.draw()
        self.win.flip()
        
        # Get TUT rating
        while True:
            keys = event.waitKeys(keyList=['1', '2', '3', '4', '5', '6', '7', 'escape'])
            if keys:
                key = keys[0]
                if key == 'escape':
                    core.quit()
                else:
                    tut_rating = int(key)
                    break
        
        # FMT probe
        fmt_question = config.MW_PROBES['fmt']
        fmt_instruction = fmt_question + scale_text + "\n\nPress a number key (1-7):"
        
        self.instruction_text.text = fmt_instruction
        self.instruction_text.draw()
        self.win.flip()
        
        # Get FMT rating
        while True:
            keys = event.waitKeys(keyList=['1', '2', '3', '4', '5', '6', '7', 'escape'])
            if keys:
                key = keys[0]
                if key == 'escape':
                    core.quit()
                else:
                    fmt_rating = int(key)
                    break
        
        # Save mind-wandering data
        self.save_trial_data({
            'phase': 'mind_wandering_probe',
            'block_type': condition, 'block_number': block_number, 'trial_number': trial_number,
            'mw_tut_rating': tut_rating, 'mw_fmt_rating': fmt_rating,
            'stimulus': None, 'stimulus_position': None, 'response': None,
            'correct_response': None, 'accuracy': None, 'reaction_time': None,
            'mood_rating': None, 'velten_rating': None, 'velten_statement': None,
            'video_file': None, 'audio_file': None
        })
        
        # Print MW probe results to console
        print(f"📝 Mind-Wandering Probe Results:")
        print(f"   TUT (thinking about something else): {tut_rating}/7")
        print(f"   FMT (thoughts moving freely): {fmt_rating}/7")
    
    def run_mind_wandering_probe_slider(self, condition, block_number, trial_number):
        """Present mind-wandering probes using slider with custom tick marks"""
        print(f"Presenting mind-wandering probe at trial {trial_number}")
        
        # TUT probe
        self.instruction_text.text = config.MW_PROBES['tut']
        self.mw_tut_slider.reset()
        
        # Show TUT slider and wait for rating
        while self.mw_tut_slider.getRating() is None:
            self.instruction_text.draw()
            self.mw_tut_slider.draw()
            # Draw horizontal line
            self.mw_horizontal_line.draw()
            # Draw custom tick marks with different heights
            for tick_mark in self.mw_tick_marks:
                tick_mark.draw()
            # Draw text labels at start and end
            self.mw_start_label.draw()
            self.mw_end_label.draw()
            self.win.flip()
            
            # Check for escape
            if 'escape' in event.getKeys():
                core.quit()
        
        tut_rating = self.mw_tut_slider.getRating()
        
        # FMT probe
        self.instruction_text.text = config.MW_PROBES['fmt']
        self.mw_fmt_slider.reset()
        
        # Show FMT slider and wait for rating
        while self.mw_fmt_slider.getRating() is None:
            self.instruction_text.draw()
            self.mw_fmt_slider.draw()
            # Draw horizontal line
            self.mw_horizontal_line.draw()
            # Draw custom tick marks with different heights
            for tick_mark in self.mw_tick_marks:
                tick_mark.draw()
            # Draw text labels at start and end
            self.mw_start_label.draw()
            self.mw_end_label.draw()
            self.win.flip()
            
            # Check for escape
            if 'escape' in event.getKeys():
                core.quit()
        
        fmt_rating = self.mw_fmt_slider.getRating()
        
        # Print MW probe results to console
        print(f"📋 MW Probe Results - TUT (task-unrelated thoughts): {tut_rating}/7 | FMT (freely moving thoughts): {fmt_rating}/7")
        
        # Save MW probe data
        self.save_trial_data({
            'phase': f'mind_wandering_probe_block_{block_number}',
            'block_type': condition, 'block_number': block_number, 'trial_number': trial_number,
            'stimulus': None, 'stimulus_position': None, 'response': None,
            'correct_response': None, 'accuracy': None, 'reaction_time': None,
            'mood_rating': None, 'mw_tut_rating': tut_rating, 'mw_fmt_rating': fmt_rating,
            'velten_rating': None, 'velten_statement': None, 'audio_file': None
        })
    
    def run_sart_block(self, condition, block_number):
        """FIXED: Run a single SART block with probes DURING the block, not after"""
        # Show instruction with condition cue - FIXED: Display indicator during instructions
        if condition == 'RI':  # Response Inhibition
            cue_circle = self.inhibition_cue
            self.show_instruction('sart_inhibition', condition_cue=cue_circle)
        else:  # Non-Response Inhibition
            cue_circle = self.non_inhibition_cue
            self.show_instruction('sart_non_inhibition', condition_cue=cue_circle)
        
        # Generate trial sequence with exactly 15% No-Go trials (digit 3)
        trials = []
        total_trials = config.SART_PARAMS['trials_per_block']
        
        # Calculate exact number of No-Go trials (15% of total)
        nogo_trials = int(total_trials * 0.15)  # 18 trials out of 120
        go_trials = total_trials - nogo_trials  # 102 trials
        
        # Create digit list with correct proportions
        digit_list = []
        # Add No-Go trials (digit 3)
        digit_list.extend([3] * nogo_trials)
        # Add Go trials (other digits 0-2, 4-9) - distribute evenly
        other_digits = [d for d in config.SART_PARAMS['digits'] if d != 3]  # [0,1,2,4,5,6,7,8,9]
        for i in range(go_trials):
            digit_list.append(other_digits[i % len(other_digits)])
        
        # Shuffle to randomize order
        random.shuffle(digit_list)
        
        # Create trials
        for trial_num in range(total_trials):
            digit = digit_list[trial_num]
            position = random.choice(['left', 'right'])
            trials.append({
                'trial_number': trial_num + 1,
                'digit': digit,
                'position': position,
                'is_target': digit == config.SART_PARAMS['target_digit'] and condition == 'RI'
            })
        
        print(f"📊 SART Block {block_number} ({condition}): Generated {nogo_trials} No-Go trials ({nogo_trials/total_trials*100:.1f}%) out of {total_trials} total trials")
        
        # FIXED: Initialize probe timing - probes occur DURING the block
        # Schedule probes at random intervals (every 13-17 trials as per config)
        probe_trials = []
        current_trial = random.randint(config.SART_PARAMS['probe_interval_min'], config.SART_PARAMS['probe_interval_max'])
        while current_trial < config.SART_PARAMS['trials_per_block']:
            probe_trials.append(current_trial)
            current_trial += random.randint(config.SART_PARAMS['probe_interval_min'], config.SART_PARAMS['probe_interval_max'])
        
        print(f"Scheduled probes for trials: {probe_trials}")
        
        # Initialize performance tracking
        correct_responses = 0
        total_responses = 0
        commission_errors = 0  # Responding to targets when shouldn't
        omission_errors = 0    # Not responding to non-targets when should
        target_trials = 0
        non_target_trials = 0
        total_rt = 0
        rt_count = 0
        
        print(f"\n🎯 Starting SART Block {block_number} ({condition})")
        print("=" * 60)
        
        # Run trials
        for trial in trials:
            # FIXED: Check if it's time for a mind-wandering probe BEFORE the trial
            if trial['trial_number'] in probe_trials:
                self.run_mind_wandering_probe_likert(condition, block_number, trial['trial_number'])
            
            # Run SART trial
            response, rt, accuracy = self.run_sart_trial(trial, condition, block_number, cue_circle)
            
            # Update performance metrics
            if trial['is_target']:
                target_trials += 1
                if response is not None:
                    commission_errors += 1
                else:
                    correct_responses += 1
            else:
                non_target_trials += 1
                if response is None:
                    omission_errors += 1
                elif response in ['left', 'right']:
                    if accuracy == 1:
                        correct_responses += 1
                    if rt is not None:
                        total_rt += rt
                        rt_count += 1
            
            total_responses += 1
        
        # Print block summary
        print("=" * 60)
        print(f"📊 SART Block {block_number} Summary:")
        print(f"   Overall Accuracy: {correct_responses}/{total_responses} ({correct_responses/total_responses*100:.1f}%)")
        commission_pct = (commission_errors/target_trials*100) if target_trials > 0 else 0
        omission_pct = (omission_errors/non_target_trials*100) if non_target_trials > 0 else 0
        print(f"   Commission Errors: {commission_errors}/{target_trials} targets ({commission_pct:.1f}%)")
        print(f"   Omission Errors: {omission_errors}/{non_target_trials} non-targets ({omission_pct:.1f}%)")
        if rt_count > 0:
            avg_rt = total_rt / rt_count
            print(f"   Average RT: {avg_rt*1000:.0f}ms (n={rt_count})")
        print("=" * 60)
        print(f"🏁 SART Block {block_number} ({condition}) COMPLETED - Returning to main experiment flow")
        
        # CRITICAL: Return control to main experiment
        return
    
    def run_sart_trial(self, trial, condition, block_number, cue_circle):
        """Run a single SART trial"""
        # Set digit position
        if trial['position'] == 'left':
            digit_pos = (-150, 0)
            correct_response = 'left'
        else:
            digit_pos = (150, 0)
            correct_response = 'right'
        
        # Override correct response for inhibition trials
        if trial['is_target']:
            correct_response = None  # No response expected
        
        # Show fixation
        self.fixation.draw()
        cue_circle.draw()
        self.win.flip()
        core.wait(config.TIMING['fixation_duration'])
        
        # Show digit and collect response - FIXED: Keep fixation cross visible
        self.digit_stim.text = str(trial['digit'])
        self.digit_stim.pos = digit_pos
        self.fixation.draw()  # FIXED: Keep fixation cross visible during digit presentation
        self.digit_stim.draw()
        cue_circle.draw()
        self.win.flip()
        
        # Start trial clock
        self.trial_clock.reset()
        self.kb.clearEvents()
        
        # FIXED: Display digit for full duration regardless of key press
        response = None
        rt = None
        
        # Collect keys during the full stimulus duration
        start_time = self.trial_clock.getTime()
        keys_pressed = []
        
        while self.trial_clock.getTime() - start_time < config.SART_PARAMS['stimulus_duration']:
            # Check for key presses but don't break the loop
            keys = self.kb.getKeys(keyList=['left', 'right', 'escape'], waitRelease=False)
        if keys:
                # Record the first key press (if multiple keys pressed)
            if not keys_pressed:
                keys_pressed = keys
                # Handle escape immediately
            if keys[0].name == 'escape':
                self.cleanup_and_quit()
            
            # Small wait to prevent excessive CPU usage
            core.wait(0.001)
        
        # Process the first key press if any occurred
        if keys_pressed:
            response = keys_pressed[0].name
            rt = keys_pressed[0].rt
        
        # FIXED: Keep fixation cross and condition indicator visible during ISI
        self.fixation.draw()
        cue_circle.draw()
        self.win.flip()
        
        # Determine accuracy
        if correct_response is None:  # Target trial (should not respond)
            accuracy = 1 if response is None else 0
        else:  # Non-target trial (should respond correctly)
            accuracy = 1 if response == correct_response else 0
        
        # Wait for ISI
        core.wait(config.SART_PARAMS['isi_duration'])
        
        # Print trial metrics to console
        if correct_response is None:  # Target trial (should not respond)
            trial_type = "TARGET (no-go)"
            result = "CORRECT" if response is None else "COMMISSION ERROR"
        else:  # Non-target trial (should respond)
            trial_type = "NON-TARGET"
            if response is None:
                result = "OMISSION ERROR"
            elif response == correct_response:
                result = "CORRECT"
            else:
                result = "INCORRECT SIDE"
        
        rt_display = f"{rt*1000:.0f}ms" if rt else "no response"
        print(f"SART Trial {trial['trial_number']:2d}: Digit={trial['digit']} {trial['position']:>5} | {trial_type:>12} | {result:>15} | RT: {rt_display:>10}")
        
        # Save trial data
        self.save_trial_data({
            'phase': 'sart_task',
            'block_type': condition,
            'block_number': block_number,
            'trial_number': trial['trial_number'],
            'stimulus': trial['digit'],
            'stimulus_position': trial['position'],
            'response': response,
            'correct_response': correct_response,
            'accuracy': accuracy,
            'reaction_time': rt,
            'mood_rating': None, 'mw_tut_rating': None, 'mw_fmt_rating': None,
            'velten_rating': None, 'video_file': None, 'audio_file': None,
            'velten_statement': None
        })
        
        return response, rt, accuracy
    
    def run_mind_wandering_probe_keyboard(self, condition, block_number, trial_number):
        """Present mind-wandering probes using keyboard input"""
        print(f"Presenting mind-wandering probe at trial {trial_number}")
        
        # TUT probe
        prompt = f"{config.MW_PROBES['tut']}\n\nPress keys 1-7 (1=Not at all, 7=Very much):"
        self.instruction_text.text = prompt
        self.instruction_text.draw()
        self.win.flip()
        
        tut_rating = None
        while tut_rating is None:
            keys = event.waitKeys()
            for key in keys:
                if key == 'escape':
                    core.quit()
                elif key.isdigit() and 1 <= int(key) <= 7:
                    tut_rating = int(key)
        
        # FMT probe
        prompt = f"{config.MW_PROBES['fmt']}\n\nPress keys 1-7 (1=Not at all, 7=Very much):"
        self.instruction_text.text = prompt
        self.instruction_text.draw()
        self.win.flip()
        
        fmt_rating = None
        while fmt_rating is None:
            keys = event.waitKeys()
            for key in keys:
                if key == 'escape':
                    core.quit()
                elif key.isdigit() and 1 <= int(key) <= 7:
                    fmt_rating = int(key)
        
        # Print mind-wandering probe results to console
        print(f"📋 MW Probe Results - TUT (task-unrelated thoughts): {tut_rating}/7 | FMT (freely moving thoughts): {fmt_rating}/7")
        
        # Save probe data
        self.save_trial_data({
            'phase': 'mind_wandering_probe',
            'block_type': condition,
            'block_number': block_number,
            'trial_number': trial_number,
            'mw_tut_rating': tut_rating,
            'mw_fmt_rating': fmt_rating,
            'stimulus': None, 'stimulus_position': None, 'response': None,
            'correct_response': None, 'accuracy': None, 'reaction_time': None,
            'mood_rating': None, 'velten_rating': None, 'video_file': None,
            'audio_file': None, 'velten_statement': None
        })
    
    def run_mood_induction(self, induction_type, valence, phase_number):
        """UPDATED: Run mood induction (either video or Velten+music) with enhanced video selection"""
        print(f"🎭 PHASE {phase_number}: Running {induction_type}({valence}) mood induction")
        
        if induction_type == 'M':  # Movie/Video
            print(f"   📽️ Movie induction ({'Positive' if valence == '+' else 'Negative'})")
            if valence == '+':
                if phase_number == 1:
                    self.play_video('positive_clip1', 'film_positive_clip1')
                else:
                    self.play_video('positive_clip2', 'film_positive_clip2')
            else:  # negative
                # Use specific negative clips based on phase
                if phase_number == 1 or phase_number == 3:
                    self.play_video('negative_clip', 'film_general')  # Phase 1 and 3 use negative_clip
                else:
                    self.play_video('negative_clip2', 'film_general')  # Phase 2 and 4 use negative_clip2
        
        elif induction_type == 'V':  # Velten + music
            valence_word = 'positive' if valence == '+' else 'negative'
            print(f"   📝 Velten + music induction ({valence_word.title()})")
            self.run_velten_procedure(valence_word)
        
        print(f"✅ {induction_type}({valence}) mood induction completed")
    
    def run_neutral_washout(self):
        """Run neutral washout procedure using actual neutral video"""
        self.show_instruction('neutral_washout')
        self.play_video('neutral_clip')
    
    def run_mood_repair(self):
        """Run mood repair procedure with participant choice for animal preference"""
        # Show mood repair instruction with choice options
        self.show_instruction('mood_repair')
        
        # Get participant's preference
        choice = None
        while choice is None:
            keys = event.waitKeys()
            for key in keys:
                if key == 'escape':
                    core.quit()
                elif key in ['1', 'num_1']:
                    choice = 'with_animals'
                    break
                elif key in ['2', 'num_2']:
                    choice = 'without_animals'
                    break
                elif key in ['3', 'num_3']:
                    choice = 'no_preference'
                    break
        
        # Determine which video to show
        if choice == 'with_animals':
            video_key = 'mood_repair_animal'
            repair_type = 'with_animals'
        elif choice == 'without_animals':
            video_key = 'mood_repair'
            repair_type = 'without_animals'
        else:  # no_preference
            # Randomize between the two options (50/50)
            import random
            if random.random() < 0.5:
                video_key = 'mood_repair_animal'
                repair_type = 'with_animals_random'
            else:
                video_key = 'mood_repair'
                repair_type = 'without_animals_random'
        
        # Show brief loading message
        self.instruction_text.text = "Loading your selected video clip..."
        self.instruction_text.draw()
        self.win.flip()
        core.wait(1.0)
        
        # Play the selected video
        self.play_video(video_key)
        
        # Save mood repair choice data
        self.save_trial_data({
            'phase': 'mood_repair',
            'mood_repair_choice': choice,
            'mood_repair_type': repair_type,
            'video_file': str(config.VIDEO_FILES[video_key]),
            'block_type': None, 'block_number': None, 'trial_number': None,
            'stimulus': None, 'stimulus_position': None, 'response': None,
            'correct_response': None, 'accuracy': None, 'reaction_time': None,
            'mood_rating': None, 'mw_tut_rating': None, 'mw_fmt_rating': None,
            'velten_rating': None, 'velten_statement': None, 'audio_file': None
        })
    

    

    
    def preload_videos_for_experiment(self):
        """FIXED: Preload videos during intro to reduce loading delays"""
        # Show loading screen
        loading_screen = create_loading_screen(self.win, "Loading experiment materials, please wait...")
        
        # Preload all videos
        self.video_preloader.preload_all_videos()
        
        # Show completion
        loading_screen.text = "Loading complete! Press any key to continue."
        loading_screen.draw()
        self.win.flip()
        event.waitKeys()
    
    def run_experiment(self):
        """Run the complete experiment following the exact step sequence provided"""
        try:
            # Step 1: Welcome screen
            self.show_instruction('welcome')
            
            # Step 2: Collect participant info (email and counterbalancing)
            self.setup_data_collection()
            
            # FIXED: Preload videos during intro to prevent delays
            self.preload_videos_for_experiment()
            
            # Step 3: Overview instructions
            self.show_instruction('overview')
            
            # Get counterbalancing order for this participant
            order = self.participant_data['counterbalancing']
            condition = self.participant_data['condition']
            
            print(f"\n🎯 Running Order {condition} - Complete Experimental Protocol")
            print("=" * 60)
            
            # Step 1: Baseline mood scale
            print(f"\n📍 STEP 1 - Baseline Mood Scale")
            self.collect_mood_rating('baseline')
            
            # Step 2: Mood Induction 1
            print(f"\n📍 STEP 2 - Mood Induction 1")
            induction_1 = order['mood_inductions'][0]
            self.run_mood_induction(induction_1[0], induction_1[1], 1)
            print(f"\n📍 STEP 3 - Post-Induction Mood Scale")
            self.collect_mood_rating('post_induction_1')
            
            # Step 4: SART 1
            print(f"\n📍 STEP 4 - SART Block 1 ({order['sart_conditions'][0]})")
            self.run_sart_block(order['sart_conditions'][0], 1)
            print(f"✅ SART Block 1 completed - moving to next phase")
            
            # Step 5: Mood Induction 2 (re-induction)
            print(f"\n📍 STEP 5 - Mood Induction 2 (Re-induction)")
            induction_2 = order['mood_inductions'][1]
            self.run_mood_induction(induction_2[0], induction_2[1], 2)
            print(f"\n📍 STEP 6 - Post-Induction Mood Scale")
            self.collect_mood_rating('post_induction_2')
            
            # Step 7: SART 2
            print(f"\n📍 STEP 7 - SART Block 2 ({order['sart_conditions'][1]})")
            self.run_sart_block(order['sart_conditions'][1], 2)
            print(f"✅ SART Block 2 completed - moving to neutral washout")
            
            # Step 8: Neutral Washout
            print(f"\n📍 STEP 8 - Neutral Washout")
            self.run_neutral_washout()
            print(f"\n📍 STEP 9 - Post-Washout Mood Scale")
            self.collect_mood_rating('post_washout')
            
            # Step 10: Mood Induction 3
            print(f"\n📍 STEP 10 - Mood Induction 3")
            induction_3 = order['mood_inductions'][2]
            self.run_mood_induction(induction_3[0], induction_3[1], 3)
            print(f"\n📍 STEP 11 - Post-Induction Mood Scale")
            self.collect_mood_rating('post_induction_3')
            
            # Step 12: SART 3
            print(f"\n📍 STEP 12 - SART Block 3 ({order['sart_conditions'][2]})")
            self.run_sart_block(order['sart_conditions'][2], 3)
            print(f"✅ SART Block 3 completed - moving to final phase")
            
            # Step 13: Mood Induction 4
            print(f"\n📍 STEP 13 - Mood Induction 4")
            induction_4 = order['mood_inductions'][3]
            self.run_mood_induction(induction_4[0], induction_4[1], 4)
            print(f"\n📍 STEP 14 - Post-Induction Mood Scale")
            self.collect_mood_rating('post_induction_4')
            
            # Step 15: SART 4
            print(f"\n📍 STEP 15 - SART Block 4 ({order['sart_conditions'][3]})")
            self.run_sart_block(order['sart_conditions'][3], 4)
            print(f"✅ SART Block 4 completed")
            
            # Step 16: Mood Repair (if applicable)
            if order['mood_repair']:
                print(f"\n📍 STEP 16 - Mood Repair (Required for Order {condition})")
                self.run_mood_repair()
                print(f"\n📍 STEP 17 - Final Mood Scale")
                self.collect_mood_rating('post_repair')
            else:
                print(f"\n📍 No Mood Repair needed for Order {condition} (ends with positive induction)")
            
            # Final debrief
            print(f"\n📍 FINAL STEP - Debrief")
            self.show_instruction('debrief')
            
            total_steps = 17 if order['mood_repair'] else 15
            print(f"\n🎉 Complete experiment finished! All {total_steps} steps completed.")
            print(f"Data saved to: {self.data_filename}")
            print(f"Order: {condition} | Mood repair: {'Yes' if order['mood_repair'] else 'No'}")
            
        except Exception as e:
            print(f"Experiment error: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            self.cleanup_and_quit()
    
    def cleanup_and_quit(self):
        """Clean up resources and quit"""
        if self.current_audio:
            try:
                self.current_audio.stop()
            except:
                pass
            self.current_audio = None
        
        if hasattr(self, 'video_preloader'):
            self.video_preloader.cleanup()
        
        self.win.close()
        core.quit()

def main():
    """Main function to run the simplified experiment"""
    try:
        print("Starting SIMPLIFIED Mood Induction + SART Experiment")
        print("This version uses:")
        print("1. Keyboard input only (no GUI dialogs)")
        print("2. Modern Slider components where possible")
        print("3. Mind-wandering probes DURING SART blocks")
        print("4. Shortened demo version for testing")
        print("5. All known issues fixed")
        print("-" * 50)
        
        # Create and run experiment
        experiment = MoodSARTExperimentSimple()
        experiment.run_experiment()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        core.quit()

if __name__ == '__main__':
    main() 