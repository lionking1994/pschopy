#!/usr/bin/env python3
"""
PsychoPy Experiment: Mood Induction + SART Study (SIMPLIFIED VERSION)
Uses modern PsychoPy components with keyboard-based input to avoid GUI dialog issues.
This version addresses all known issues and works in headless environments.

Author: Generated for Nate Speert Lab Study
Date: 2024
"""

import os
import warnings
import logging

# Suppress specific PsychoPy deprecation warnings
warnings.filterwarnings('ignore', message='.*RGB parameter is deprecated.*')
warnings.filterwarnings('ignore', message='.*lineRGB.*deprecated.*')
warnings.filterwarnings('ignore', message='.*fillRGB.*deprecated.*')

# Also suppress via logging for PsychoPy's internal logging
logging.getLogger('psychopy').setLevel(logging.ERROR)

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
            print(f"   📊 SART blocks: {config.SART_PARAMS['total_trials']} trials total in 8 steps (shortened)")
            print(f"   📝 Velten statements: 3 per phase (shortened from 12)")
            print(f"   ⏱️  Velten duration: {config.TIMING['velten_statement_duration']}s per statement (same as main)")
            print(f"   🧠 MW probes: After each of 8 steps ({config.SART_PARAMS['trials_per_step_min']}-{config.SART_PARAMS['trials_per_step_max']} trials per step)")
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
        
        # Hide mouse cursor by default (will be shown only for mood scale)
        self.win.mouseVisible = False
        
        # Ensure window is fully ready before proceeding
        self.win.flip()  # Force initial flip to initialize graphics
        core.wait(0.1)  # Brief pause to ensure window is ready
        print("✅ Window initialization complete")
        
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
        # Text stimuli - RESPONSIVE: Use layout configuration for positioning
        # Get text position from layout config (if available) or use default
        if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG:
            text_pos = config.LAYOUT_CONFIG['text_pos']
            print(f"📐 Using layout config text position: {text_pos}")
        else:
            text_pos = (-500, 0)  # Default fallback
            print(f"📐 Using default text position: {text_pos}")
            
        # Get responsive text height from layout config
        if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG and 'text_height' in config.LAYOUT_CONFIG:
            text_height = config.LAYOUT_CONFIG['text_height']
            print(f"📐 Using responsive text height: {text_height}")
        else:
            text_height = config.TEXT_STYLE['height']  # Fallback
            print(f"📐 Using default text height: {text_height}")
            
        self.instruction_text = visual.TextStim(
            win=self.win,
            text='',
            font=config.TEXT_STYLE['font'],
            height=text_height,  # RESPONSIVE: Use calculated height
            color=config.TEXT_STYLE['color'],
            wrapWidth=config.TEXT_STYLE['wrapWidth'],
            pos=text_pos,  # RESPONSIVE: Use calculated position
            alignText=config.TEXT_STYLE.get('alignText', 'left'),  # FIXED: Left align
            anchorHoriz=config.TEXT_STYLE.get('anchorHoriz', 'left'),  # FIXED: Anchor left
            bold=False  # FIXED: Explicitly disable bold to prevent font warnings
        )
         
        # Get responsive Velten text height from layout config
        if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG and 'velten_text_height' in config.LAYOUT_CONFIG:
            velten_text_height = config.LAYOUT_CONFIG['velten_text_height']
            print(f"📐 Using responsive Velten text height: {velten_text_height}")
        else:
            velten_text_height = config.VELTEN_TEXT_STYLE['height']  # Fallback
            print(f"📐 Using default Velten text height: {velten_text_height}")
         
        # Centered text stimulus for Velten statements
        self.velten_text = visual.TextStim(
            win=self.win,
            text='',
            font=config.VELTEN_TEXT_STYLE['font'],
            height=velten_text_height,  # RESPONSIVE: Use calculated height
            color=config.VELTEN_TEXT_STYLE['color'],
            wrapWidth=config.VELTEN_TEXT_STYLE['wrapWidth'],
            pos=config.VELTEN_TEXT_STYLE['pos'],
            alignText=config.VELTEN_TEXT_STYLE.get('alignText', 'center'),
            anchorHoriz=config.VELTEN_TEXT_STYLE.get('anchorHoriz', 'center'),
            bold=False  # FIXED: Explicitly disable bold to prevent font warnings
        )
        
        # Get responsive SART element sizes from layout config
        if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG:
            fixation_height = config.LAYOUT_CONFIG.get('fixation_height', 80)
            digit_height = config.LAYOUT_CONFIG.get('digit_height', 120)
            print(f"📐 Using responsive SART sizes: fixation={fixation_height}, digit={digit_height}")
        else:
            fixation_height = 80  # Fallback
            digit_height = 120    # Fallback
            print(f"📐 Using default SART sizes: fixation={fixation_height}, digit={digit_height}")
            
        # SART stimuli - Responsive sizes for different displays
        self.fixation = visual.TextStim(
            win=self.win,
            text='+',
            font=config.TEXT_STYLE['font'],
            height=fixation_height,  # RESPONSIVE: Use calculated height
            color=config.TEXT_STYLE['color'],
            pos=(0, 0),
            bold=False  # FIXED: Explicitly disable bold to prevent font warnings
        )
        
        self.digit_stim = visual.TextStim(
            win=self.win,
            text='',
            font=config.TEXT_STYLE['font'],
            height=digit_height,  # RESPONSIVE: Use calculated height
            color=config.TEXT_STYLE['color'],
            pos=(0, 0),
            bold=False  # FIXED: Explicitly disable bold to prevent font warnings
        )
        
        # Condition cue circles - RESPONSIVE: Use layout configuration
        # Get cue position and size from layout config (if available) or use config defaults
        if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG:
            cue_pos = config.LAYOUT_CONFIG['cue_pos']
            cue_radius = config.LAYOUT_CONFIG['cue_radius']
            print(f"📐 Using layout config cue position: {cue_pos}, radius: {cue_radius}")
        else:
            cue_pos = config.CONDITION_CUES['inhibition']['pos']
            cue_radius = config.CONDITION_CUES['inhibition']['radius']
            print(f"📐 Using default cue position: {cue_pos}, radius: {cue_radius}")
            
        self.inhibition_cue = visual.Circle(
            win=self.win,
            radius=cue_radius,  # RESPONSIVE: Use calculated radius
            pos=cue_pos,        # RESPONSIVE: Use calculated position
            fillColor=config.CONDITION_CUES['inhibition']['color'],
            lineColor=config.CONDITION_CUES['inhibition']['color']
        )
        
        self.non_inhibition_cue = visual.Circle(
            win=self.win,
            radius=cue_radius,  # RESPONSIVE: Use calculated radius
            pos=cue_pos,        # RESPONSIVE: Use calculated position
            fillColor=config.CONDITION_CUES['non_inhibition']['color'],
            lineColor=config.CONDITION_CUES['non_inhibition']['color']
        )
        
        # Get responsive mood slider size from layout config
        if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG:
            mood_slider_width = config.LAYOUT_CONFIG.get('mood_slider_width', 800)
            mood_slider_height = config.LAYOUT_CONFIG.get('mood_slider_height', 70)
            print(f"📐 Using responsive mood slider size: {mood_slider_width}x{mood_slider_height}")
        else:
            mood_slider_width = 800   # Fallback
            mood_slider_height = 70   # Fallback
            print(f"📐 Using default mood slider size: {mood_slider_width}x{mood_slider_height}")
            
        # Get responsive mood slider position from layout config
        if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG:
            mood_slider_pos = (0, config.LAYOUT_CONFIG.get('mood_slider_pos', -200))
            print(f"📐 Using responsive mood slider position: {mood_slider_pos}")
        else:
            mood_slider_pos = (0, -200)  # Fallback
            print(f"📐 Using default mood slider position: {mood_slider_pos}")
            
        # MODERN: Mood rating slider (replaces RatingScale) - Responsive sizing and positioning
        # Calculate responsive label height for mood slider
        if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG:
            # Make labels larger - about 50% of slider height for better visibility
            mood_label_height = max(30, int(mood_slider_height * 0.5))
            print(f"📐 Using mood slider label height: {mood_label_height}px")
        else:
            mood_label_height = 35  # Fallback (increased)
            
        self.mood_slider = visual.Slider(
            win=self.win,
            ticks=config.MOOD_SCALE['tick_positions'],
            labels=config.MOOD_SCALE['labels'],
            pos=mood_slider_pos,  # RESPONSIVE: Use calculated position
            size=(mood_slider_width, mood_slider_height),  # RESPONSIVE: Use calculated size
            granularity=config.MOOD_SCALE['granularity'],
            style='slider',  # FIXED: Use 'slider' style for horizontal appearance
            color=[0.5, 0.5, 0.5],     # Neutral gray color
            markerColor=[0.7, 0.7, 0.7],  # Light gray marker for neutral appearance
            lineColor=[0.5, 0.5, 0.5],    # Neutral gray line
            labelColor='white',
            labelHeight=mood_label_height  # RESPONSIVE: Larger labels for better visibility
            # Note: showValue parameter not supported in this PsychoPy version
        )
        
        # Get responsive button sizes and positions from layout config
        if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG:
            button_width = config.LAYOUT_CONFIG.get('button_width', 260)
            button_height = config.LAYOUT_CONFIG.get('button_height', 75)
            button_text_height = config.LAYOUT_CONFIG.get('button_text_height', 35)
            mood_button_pos = (0, config.LAYOUT_CONFIG.get('mood_button_pos', -300))
            mw_button_pos = (0, config.LAYOUT_CONFIG.get('mw_button_pos', -200))
            print(f"📐 Using responsive button size: {button_width}x{button_height}, text={button_text_height}")
            print(f"📐 Using responsive button positions: mood={mood_button_pos}, mw={mw_button_pos}")
        else:
            button_width = 260    # Fallback
            button_height = 75    # Fallback
            button_text_height = 35  # Fallback
            mood_button_pos = (0, -300)  # Fallback
            mw_button_pos = (0, -200)    # Fallback
            print(f"📐 Using default button size: {button_width}x{button_height}, text={button_text_height}")
            print(f"📐 Using default button positions: mood={mood_button_pos}, mw={mw_button_pos}")
            
        # Continue button for mood rating - Responsive sizing and positioning
        self.continue_button = visual.Rect(
            win=self.win,
            width=button_width,   # RESPONSIVE: Use calculated width
            height=button_height, # RESPONSIVE: Use calculated height
            pos=mood_button_pos,  # RESPONSIVE: Use calculated position
            fillColor=[0.0, 0.5, 1.0],  # Brighter blue button
            lineColor=[1.0, 1.0, 1.0]   # White border for better visibility
        )
        
        self.continue_button_text = visual.TextStim(
            win=self.win,
            text="Continue",
            pos=mood_button_pos,  # RESPONSIVE: Use same calculated position
            color='white',
            height=button_text_height,  # RESPONSIVE: Use calculated height
            bold=True   # Bold text for better visibility
        )
        
        # Continue button for mind-wandering probe sliders - Responsive sizing and positioning
        self.mw_continue_button = visual.Rect(
            win=self.win,
            width=button_width,   # RESPONSIVE: Use same calculated width
            height=button_height, # RESPONSIVE: Use same calculated height
            pos=mw_button_pos,    # RESPONSIVE: Use calculated position
            fillColor=[0.0, 0.5, 1.0],  # Brighter blue button
            lineColor=[1.0, 1.0, 1.0]   # White border for better visibility
        )
        
        self.mw_continue_button_text = visual.TextStim(
            win=self.win,
            text="Continue",
            pos=mw_button_pos,    # RESPONSIVE: Use same calculated position
            color='white',
            height=button_text_height,  # RESPONSIVE: Use same calculated height
            bold=True   # Bold text for better visibility
        )
        
        # Get responsive MW slider sizes from layout config
        if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG:
            mw_slider_width = config.LAYOUT_CONFIG.get('mw_slider_width', 900)
            mw_slider_height = config.LAYOUT_CONFIG.get('mw_slider_height', 70)
            print(f"📐 Using responsive MW slider size: {mw_slider_width}x{mw_slider_height}")
        else:
            mw_slider_width = 900   # Fallback
            mw_slider_height = 70   # Fallback
            print(f"📐 Using default MW slider size: {mw_slider_width}x{mw_slider_height}")
            
        # Get responsive MW slider position from layout config
        if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG:
            mw_slider_pos = (0, config.LAYOUT_CONFIG.get('mw_slider_pos', -200))
            print(f"📐 Using responsive MW slider position: {mw_slider_pos}")
        else:
            mw_slider_pos = (0, -200)  # Fallback
            print(f"📐 Using default MW slider position: {mw_slider_pos}")
            
        # MODERN: Mind-wandering probe sliders - Responsive sizing and positioning
        self.mw_tut_slider = visual.Slider(
            win=self.win,
            ticks=list(range(config.MW_PROBES['scale_range'][0], config.MW_PROBES['scale_range'][1] + 1)),
            labels=config.MW_PROBES['scale_labels'],
            pos=mw_slider_pos,  # RESPONSIVE: Use calculated position
            size=(mw_slider_width, mw_slider_height),  # RESPONSIVE: Use calculated size
            granularity=1,   # Force discrete integer values
            style='rating',  # Discrete tick selection
            color=[-1, -1, -1],      # Invisible background - using custom tick marks
            markerColor=[1, 0, 0],   # Red marker for visibility
            lineColor=[-1, -1, -1],  # Invisible line - using custom tick marks
            labelColor=[-1, -1, -1], # Invisible labels - using custom labels
            labelHeight=22
        )
        
        self.mw_fmt_slider = visual.Slider(
            win=self.win,
            ticks=list(range(config.MW_PROBES['scale_range'][0], config.MW_PROBES['scale_range'][1] + 1)),
            labels=config.MW_PROBES['scale_labels'],
            pos=mw_slider_pos,  # RESPONSIVE: Use same calculated position
            size=(mw_slider_width, mw_slider_height),  # RESPONSIVE: Use same calculated size
            granularity=1,   # Force discrete integer values
            style='rating',  # Discrete tick selection
            color=[-1, -1, -1],      # Invisible background - using custom tick marks
            markerColor=[1, 0, 0],   # Red marker for visibility
            lineColor=[-1, -1, -1],  # Invisible line - using custom tick marks
            labelColor=[-1, -1, -1], # Invisible labels - using custom labels
            labelHeight=22
        )
        
        # Get responsive Velten slider sizes from layout config
        if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG:
            velten_slider_width = config.LAYOUT_CONFIG.get('velten_slider_width', 750)
            velten_slider_height = config.LAYOUT_CONFIG.get('velten_slider_height', 60)
            print(f"📐 Using responsive Velten slider size: {velten_slider_width}x{velten_slider_height}")
        else:
            velten_slider_width = 750   # Fallback
            velten_slider_height = 60   # Fallback
            print(f"📐 Using default Velten slider size: {velten_slider_width}x{velten_slider_height}")
            
        # Get responsive Velten slider position from layout config
        if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG:
            velten_slider_pos = (0, config.LAYOUT_CONFIG.get('velten_slider_pos', -380))
            print(f"📐 Using responsive Velten slider position: {velten_slider_pos}")
        else:
            velten_slider_pos = (0, -380)  # Fallback
            print(f"📐 Using default Velten slider position: {velten_slider_pos}")
            
        # UPDATED: 7-point scale slider (made invisible - using custom tick marks instead)
        self.velten_slider = visual.Slider(
            win=self.win,
            ticks=config.VELTEN_RATING_SCALE['tick_positions'],  # [1, 2, 3, 4, 5, 6, 7]
            labels=config.VELTEN_RATING_SCALE['scale_labels'],
            pos=velten_slider_pos,  # RESPONSIVE: Use calculated position
            size=(velten_slider_width, velten_slider_height),  # RESPONSIVE: Use calculated size
            granularity=1,  # Force discrete integer values only (1, 2, 3, 4, 5, 6, 7)
            style='rating',  # Use rating style for discrete tick selection
            color=[-1, -1, -1],      # Invisible - using custom tick marks instead
            markerColor=[-1, -1, -1], # Invisible - using custom tick marks instead
            lineColor=[-1, -1, -1],   # Invisible - using custom tick marks instead
            labelColor=[-1, -1, -1],  # Invisible - using custom tick marks instead
            labelHeight=20,
            flip=False,
            readOnly=False
        )
        
        # Create custom tick marks with different heights
        self.create_custom_tick_marks()
        
        # Initialize audio (will be loaded as needed)
        self.current_audio = None
        
        # Preload audio for instant playback
        self.preload_audio_files()
    
    def draw_velten_marker(self, current_value):
        """Draw red marker at the current value position on custom tick marks"""
        if current_value is None:
            return
            
        # Get responsive Velten slider size from layout config
        if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG:
            slider_width = config.LAYOUT_CONFIG.get('velten_slider_width', 750)
        else:
            slider_width = 750  # Fallback
            
        # Calculate marker position based on current value (1-7)
        slider_x = 0
        # Get responsive Velten tick marks Y position (matches create_custom_tick_marks calculation)
        if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG:
            velten_slider_pos_y = config.LAYOUT_CONFIG.get('velten_slider_pos', -380)
            slider_y = velten_slider_pos_y + 60  # Match the custom tick marks position
        else:
            slider_y = -320  # Fallback position
        
        # Calculate x position for the marker
        # Values 1-7 map to positions along the slider width
        value_ratio = (current_value - 1) / 6  # Convert 1-7 to 0-1
        marker_x = slider_x - (slider_width / 2) + (value_ratio * slider_width)
        
        # Create and draw red marker circle
        marker = visual.Circle(
            win=self.win,
            radius=15,  # Size of the red dot
            pos=(marker_x, slider_y),
            fillColor=[1, 0, 0],  # Red color
            lineColor=[1, 0, 0]   # Red border
        )
        marker.draw()
    
    def create_custom_tick_marks(self):
        """Create custom tick marks with different heights and white horizontal line for 7-point scales"""
        # Get responsive slider widths from layout config
        if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG:
            velten_width = config.LAYOUT_CONFIG.get('velten_slider_width', 750)
            mw_width = config.LAYOUT_CONFIG.get('mw_slider_width', 900)
        else:
            velten_width = 750  # Fallback
            mw_width = 900      # Fallback
            
        # Velten slider custom ticks (responsive positioning for better layout)
        self.velten_tick_marks = []
        slider_width = velten_width  # RESPONSIVE: Use calculated width
        slider_x = 0  # Center position
        # Calculate Velten tick marks position (offset from slider position for better visibility)
        if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG:
            velten_slider_pos_y = config.LAYOUT_CONFIG.get('velten_slider_pos', -380)
            slider_y = velten_slider_pos_y + 60  # Position above the invisible slider for better visibility
        else:
            slider_y = -320  # Fallback position
        
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
            font=config.TEXT_STYLE['font'],  # Same font as instruction text
            bold=False  # FIXED: Explicitly disable bold to prevent font warnings
        )
        self.velten_end_label = visual.TextStim(
            win=self.win,
            text="Completely",
            pos=(tick_positions[6], slider_y - 60),  # Below the last tick
            color=[1, 1, 1],  # White color
            height=config.TEXT_STYLE['height'],  # Same as instruction text
            alignText='center',
            font=config.TEXT_STYLE['font'],  # Same font as instruction text
            bold=False  # FIXED: Explicitly disable bold to prevent font warnings
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
        
        # MW probe sliders custom ticks (match actual slider position with responsive positioning)
        self.mw_tick_marks = []
        mw_slider_width = mw_width  # RESPONSIVE: Use calculated width
        mw_slider_x = 0  # Center position
        # Get responsive MW slider Y position
        if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG:
            mw_slider_y = config.LAYOUT_CONFIG.get('mw_slider_pos', -200)
        else:
            mw_slider_y = -200  # Fallback
        
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
            font=config.TEXT_STYLE['font'],  # Same font as instruction text
            bold=False  # FIXED: Explicitly disable bold to prevent font warnings
        )
        self.mw_end_label = visual.TextStim(
            win=self.win,
            text="Very much",
            pos=(mw_tick_positions[6], mw_slider_y - 50),  # Below the last tick
            color=[1, 1, 1],  # White color
            height=config.TEXT_STYLE['height'],  # Same as instruction text
            alignText='center',
            font=config.TEXT_STYLE['font'],  # Same font as instruction text
            bold=False  # FIXED: Explicitly disable bold to prevent font warnings
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
        email = self.get_text_input("Enter the email address you provided\nwhen completing the consent form:")
        
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
        """Automatically assign random counterbalancing order (25% chance each) - silent assignment"""
        # Randomly select from conditions 1-4 (25% chance each)
        condition = random.randint(1, 4)
        
        # Display condition descriptions for reference (console only)
        condition_descriptions = {
            1: "V(+) → V(+) → V(-) → V(-)",  # Positive Velten → Negative Velten
            2: "V(-) → V(-) → V(+) → V(+)",  # Negative Velten → Positive Velten
            3: "M(+) → M(+) → M(-) → M(-)",  # Positive Video → Negative Video
            4: "M(-) → M(-) → M(+) → M(+)"   # Negative Video → Positive Video
        }
        
        print(f"🎲 Automatically assigned counterbalancing order: {condition}")
        print(f"   Order {condition}: {condition_descriptions[condition]}")
        
        # No screen shown to participant - assignment happens silently
        return condition
        
    def get_text_input(self, prompt):
        """Get text input using keyboard - Normal typing for email addresses"""
        input_text = ""
        
        # Store original settings to restore later
        original_wrap_width = self.instruction_text.wrapWidth
        original_pos = self.instruction_text.pos
        original_align = self.instruction_text.alignText
        original_anchor = self.instruction_text.anchorHoriz
        original_height = self.instruction_text.height
        
        # DEBUG: Print current text configuration
        print(f"🔍 DEBUG - Email Input Text Configuration:")
        print(f"   Original wrapWidth: {original_wrap_width}")
        print(f"   Original pos: {original_pos}")
        print(f"   Original alignText: {original_align}")
        print(f"   Original anchorHoriz: {original_anchor}")
        print(f"   Original height: {original_height}")
        print(f"   Window size: {self.win.size}")
        
        # Calculate appropriate wrap width based on screen size
        screen_width = self.win.size[0] if hasattr(self.win, 'size') else 1920
        screen_height = self.win.size[1] if hasattr(self.win, 'size') else 1080
        
        # Use 80% of screen width for wrap to ensure text doesn't go to edges
        # For high-res displays like retina16, this prevents text cutoff
        calculated_wrap_width = int(screen_width * 0.8)
        
        # Adjust text height for better readability on high-res displays
        # Check if we have a high-res display (width > 2500)
        text_height = original_height
        if screen_width > 2500:
            # For retina16 and similar high-res displays
            calculated_wrap_width = int(screen_width * 0.6)  # Use less width for better centering
            # Also reduce text size slightly for better fit
            text_height = min(original_height, 50)  # Cap text height for email input
            print(f"   High-res display detected, using 60% width and adjusted text height")
        
        print(f"   Screen dimensions: {screen_width}x{screen_height}")
        print(f"   Calculated wrapWidth: {calculated_wrap_width}")
        print(f"   Text height for email: {text_height}")
        
        # For email input, keep left alignment but center the text block
        # Calculate position to center the text block while keeping text left-aligned
        if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG:
            # Use the responsive text position from layout config
            text_pos_x = config.LAYOUT_CONFIG.get('text_pos', [-500, 0])[0]
        else:
            # Fallback: Calculate position for centered text block with left alignment
            text_pos_x = -(calculated_wrap_width / 2)
        
        self.instruction_text.pos = (text_pos_x, 50)  # Slightly above center for better visibility
        self.instruction_text.alignText = 'left'  # Keep text left-aligned
        self.instruction_text.anchorHoriz = 'left'  # Anchor on left
        self.instruction_text.wrapWidth = calculated_wrap_width
        self.instruction_text.height = text_height
        
        while True:
            # Display current input with normal instructions
            display_text = f"{prompt}\n\nInput: {input_text}_\n\nPress ENTER when done"
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
                        # Restore original settings before returning
                        self.instruction_text.wrapWidth = original_wrap_width
                        self.instruction_text.pos = original_pos
                        self.instruction_text.alignText = original_align
                        self.instruction_text.anchorHoriz = original_anchor
                        self.instruction_text.height = original_height
                        print(f"✅ Email input completed: {input_text.strip()}")
                        return input_text.strip()
                elif key == 'escape':
                    # Restore original settings before quitting
                    self.instruction_text.wrapWidth = original_wrap_width
                    self.instruction_text.pos = original_pos
                    self.instruction_text.alignText = original_align
                    self.instruction_text.anchorHoriz = original_anchor
                    self.instruction_text.height = original_height
                    core.quit()
                elif key == 'backspace':
                    input_text = input_text[:-1]
                elif key == 'space':
                    input_text += ' '
                elif key == '2' and (modifiers.get('shift', False) or modifiers.get('lshift', False) or modifiers.get('rshift', False)):
                    # Handle Shift+2 = @
                    input_text += '@'
                elif key == 'period':
                    input_text += '.'
                elif key == 'minus':
                    input_text += '-'
                elif key == 'at' or key == '@':
                    input_text += '@'
                elif key == '2' and not (modifiers.get('shift', False) or modifiers.get('lshift', False) or modifiers.get('rshift', False)):
                    # Handle plain "2" key (only if no shift modifiers)
                    input_text += '2'
                elif len(key) == 1 and key.isalnum() and key != '2':
                    # Add letters and other numbers (but not '2' since it's handled above)
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
            'video_file', 'audio_file', 'velten_statement',
            'mood_repair_type', 'mood_repair_choice'
        ]
        
        with open(self.data_filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
    
    def save_trial_data(self, trial_data):
        """Save trial data to CSV file"""
        # Check if participant data is available yet
        if not self.participant_data or not self.data_filename:
            return  # Skip saving if participant info is not yet collected
            
        # Use the same headers as defined in init_csv_file to ensure consistent column order
        headers = [
            'participant_code', 'email', 'condition', 'session_start',
            'phase', 'block_type', 'block_number', 'trial_number',
            'stimulus', 'stimulus_position', 'response', 'correct_response',
            'accuracy', 'reaction_time', 'timestamp',
            'mood_rating', 'mw_tut_rating', 'mw_fmt_rating', 'velten_rating',
            'video_file', 'audio_file', 'velten_statement',
            'mood_repair_type', 'mood_repair_choice'
        ]
            
        # Add participant info to trial data
        full_data = {
            'participant_code': self.participant_data['participant_code'],
            'email': self.participant_data['email'],
            'condition': self.participant_data['condition'],
            'session_start': self.participant_data['start_time'],
            'timestamp': datetime.datetime.now().isoformat(),
        }
        
        # Add all fields from headers with None as default if not provided in trial_data
        for header in headers:
            if header not in full_data:
                full_data[header] = trial_data.get(header, None)
        
        # Write to CSV using consistent headers
        with open(self.data_filename, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
            writer.writerow(full_data)
    
    def show_instruction(self, instruction_key, wait_for_key=True, condition_cue=None):
        """Display instruction screen - FIXED: Can show condition indicators for SART"""
        print(f"🔍 DEBUG - Showing instruction: {instruction_key}")
        instruction = config.INSTRUCTIONS[instruction_key]
        self.instruction_text.text = instruction['text']
        self.instruction_text.draw()
        
        # FIXED: Draw condition cue if provided (for SART instructions)
        if condition_cue:
            condition_cue.draw()
        
        self.win.flip()
        print(f"🔍 DEBUG - Instruction displayed, waiting for key: {wait_for_key}")
        
        if wait_for_key:
            print("🔍 DEBUG - Waiting for key press...")
            # Clear any pending keyboard events to ensure clean state
            event.clearEvents('keyboard')
            keys = event.waitKeys()
            print(f"🔍 DEBUG - Key pressed: {keys}")
            if keys and 'escape' in keys:
                print("🔍 DEBUG - Escape pressed, quitting...")
                core.quit()
            else:
                print("🔍 DEBUG - Continuing after key press")
    
    def collect_mood_rating(self, phase):
        """MODERN: Collect mood rating using Slider component with button and keyboard advance"""
        print(f"📊 COLLECTING MOOD RATING: {phase}")
        
        # IMPORTANT: Make mouse visible for mood rating
        self.win.mouseVisible = True
        
        self.instruction_text.text = config.INSTRUCTIONS['mood_rating']['text'] + "\n\nMake your selection, then click the Continue button or press SPACEBAR/ENTER."
        self.mood_slider.reset()
        
        rating_selected = False
        mouse = event.Mouse(win=self.win)
         
        # Show slider, button and wait for rating + button click or keyboard
        while True:
            self.instruction_text.draw()
            self.mood_slider.draw()
            
            # Always show button, but change appearance based on selection status
            if self.mood_slider.getRating() is not None:
                if not rating_selected:
                    rating_selected = True
                    print(f"📝 Rating selected: {self.mood_slider.getRating()}")
            
                # Draw active (blue) button
                self.continue_button.fillColor = [0.0, 0.5, 1.0]  # Bright blue
                self.continue_button.lineColor = [1.0, 1.0, 1.0]  # White border
                self.continue_button_text.color = 'white'
            else:
                # Draw inactive (greyed out) button
                self.continue_button.fillColor = [0.3, 0.3, 0.3]  # Dark grey
                self.continue_button.lineColor = [0.5, 0.5, 0.5]  # Light grey border
                self.continue_button_text.color = [0.6, 0.6, 0.6]  # Grey text
            
            # Always draw the button (active or inactive)
            self.continue_button.draw()
            self.continue_button_text.draw()
            
            self.win.flip()
            
            # Check for escape
            keys = event.getKeys()
            if 'escape' in keys:
                core.quit()
            
            # Only allow advancement if rating is selected
            if rating_selected:
                # Check for mouse click on button (using same method as MW probes)
                if mouse.isPressedIn(self.continue_button):
                    print("📝 Continue button clicked")
                    break
                
                # Check for keyboard input (spacebar or enter)
                if any(key in ['space', 'return'] for key in keys):
                    print("📝 Keyboard advance used")
                    break
        
        rating = self.mood_slider.getRating()
        
        # Hide mouse cursor after rating is complete
        self.win.mouseVisible = False
        
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
    
    def collect_mood_rating_arrow_keys(self, phase):
        """Collect mood rating using mouse-click control with Continue button"""
        print(f"📊 COLLECTING MOOD RATING (Mouse Click + Button): {phase}")
        
        # Show mouse cursor for mood scale only
        self.win.mouseVisible = True
        
        # Start with no rating - user must click to set initial position
        current_value = None
        self.mood_slider.reset()
        # Don't set initial rating - slider starts empty
        
        # Updated instruction text for mouse-click control (button-only per client request)
        instruction_text = """Please rate your current mood by clicking anywhere on the slider.
 
Click on the slider to set your rating, then click the Continue button to proceed."""
        
        # Mouse for click detection
        mouse = event.Mouse(win=self.win)
        
        while True:
            # Update current_value based on any slider interaction (click or drag)
            slider_val = self.mood_slider.getRating()
            if slider_val is not None:
                current_value = int(slider_val)
            
            # Check if rating has been made
            rating_made = current_value is not None
            
            # Draw Continue button with appropriate styling
            if rating_made:
                # Active button - blue with white border
                self.continue_button.fillColor = [0.0, 0.5, 1.0]
                self.continue_button.lineColor = [1.0, 1.0, 1.0]
                self.continue_button_text.color = [1.0, 1.0, 1.0]
            else:
                # Inactive button - grey
                self.continue_button.fillColor = [0.5, 0.5, 0.5]
                self.continue_button.lineColor = [0.7, 0.7, 0.7]
                self.continue_button_text.color = [0.8, 0.8, 0.8]
            
            # Update instruction text (no current rating display)
            self.instruction_text.text = instruction_text
            self.instruction_text.draw()
            self.mood_slider.draw()
            self.continue_button.draw()
            self.continue_button_text.draw()
            self.win.flip()
            
            # Check for keyboard input (ENTER disabled - button click only per client request)
            keys = event.getKeys(['escape'])  # Only listen for escape key
            for key in keys:
                if key == 'escape':
                    core.quit()
            
            # Check for button click (only if rating made)
            if rating_made and mouse.getPressed()[0]:
                mouse_pos = mouse.getPos()
                # Check if click is on the Continue button
                button_center_x, button_center_y = self.continue_button.pos
                button_width, button_height = self.continue_button.size
                left_x = button_center_x - (button_width / 2.0)
                right_x = button_center_x + (button_width / 2.0)
                top_y = button_center_y + (button_height / 2.0)
                bottom_y = button_center_y - (button_height / 2.0)
                
                if (left_x <= mouse_pos[0] <= right_x) and (bottom_y <= mouse_pos[1] <= top_y):
                    print(f"😊 Mood Rating ({phase}): {current_value}/100 (via button click)")
                    print(f"✅ Mood rating collection completed")
                    
                    # Save mood rating data
                    self.save_trial_data({
                        'phase': f'mood_rating_{phase}',
                        'mood_rating': current_value,
                        'block_type': None, 'block_number': None, 'trial_number': None,
                        'stimulus': None, 'stimulus_position': None, 'response': None,
                        'correct_response': None, 'accuracy': None, 'reaction_time': None,
                        'mw_tut_rating': None, 'mw_fmt_rating': None, 'velten_rating': None,
                        'video_file': None, 'audio_file': None, 'velten_statement': None
                    })
                    
                    # Hide cursor when leaving mood scale
                    self.win.mouseVisible = False
                    return current_value
    
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
    
    def play_video(self, video_key, instruction_key=None, collect_rating=False):
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
                
                # Get window size for video scaling
                import sys
                
                # Get the raw window size
                raw_window_size = self.win.size if hasattr(self.win, 'size') else [1920, 1080]
                
                # Check if window size is suspiciously large (likely Retina reporting physical pixels)
                if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG and 'screen_size' in config.LAYOUT_CONFIG:
                    config_size = config.LAYOUT_CONFIG['screen_size']
                    # If window reports ~2x the configured size, it's likely Retina
                    if (raw_window_size[0] > config_size[0] * 1.8 and 
                        raw_window_size[1] > config_size[1] * 1.8):
                        # Use the configured size instead of the reported size
                        window_size = config_size
                        print(f"🔍 DEBUG - Retina Display Detected (auto-corrected):")
                        print(f"   Reported size: {raw_window_size[0]}x{raw_window_size[1]} (physical pixels)")
                        print(f"   Using logical size: {window_size[0]}x{window_size[1]}")
                    else:
                        window_size = config_size
                        print(f"🔍 DEBUG - Video Playback Sizing:")
                        print(f"   Using configured size: {window_size[0]}x{window_size[1]}")
                else:
                    # No config, check if this looks like Retina
                    if sys.platform == 'darwin' and raw_window_size[0] > 2500:
                        # Likely Retina, use half size
                        window_size = [raw_window_size[0] // 2, raw_window_size[1] // 2]
                        print(f"🔍 DEBUG - Retina Display Detected (halved):")
                        print(f"   Reported size: {raw_window_size[0]}x{raw_window_size[1]}")
                        print(f"   Using logical size: {window_size[0]}x{window_size[1]}")
                    else:
                        window_size = raw_window_size
                        print(f"🔍 DEBUG - Video Playback Sizing:")
                        print(f"   Window size: {window_size[0]}x{window_size[1]}")
                
                print(f"   Window aspect ratio: {window_size[0]/window_size[1]:.2f}")
                
                # Use corrected window size to ensure video fills screen completely
                video_size = window_size  # Use corrected window size
                print(f"📺 Setting video to fill entire window: {video_size[0]}x{video_size[1]}")
                
                # Try MovieStim3 first
                try:
                    video = visual.MovieStim3(
                        win=self.win,
                        filename=str(video_path),
                        size=video_size,  # Full window size for complete screen fill
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
                            size=video_size,  # Full window size for complete screen fill
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
            
            # Add safety limit to prevent infinite loops - will be adjusted based on video duration
            max_frames = 18000  # Default fallback
            
            video_naturally_ended = False
            consecutive_same_status = 0
            last_status = video.status
            
            # Get video duration and frame rate for accurate completion detection
            video_duration = None
            video_fps = 30.0  # Default fallback
            
            # Try to get monitor refresh rate as a better fallback
            try:
                if hasattr(self.win, 'getActualFrameRate'):
                    monitor_fps = self.win.getActualFrameRate()
                    if monitor_fps and monitor_fps > 0:
                        video_fps = monitor_fps
                        print(f"📏 Using monitor refresh rate: {video_fps:.1f} fps")
                    else:
                        video_fps = 60.0  # Common default for modern displays
                        print(f"📏 Using common display rate fallback: {video_fps} fps")
                else:
                    video_fps = 60.0  # Most modern displays are 60fps
                    print(f"📏 Using modern display fallback: {video_fps} fps")
            except:
                video_fps = 60.0
                print(f"📏 Using safe fallback: {video_fps} fps")
            
            try:
                if hasattr(video, 'duration') and video.duration:
                    video_duration = video.duration
                    print(f"📏 Video duration: {video_duration:.1f} seconds")
                
                # Try multiple ways to get actual video frame rate
                actual_video_fps = None
                
                # Method 1: Try video._player.source.video_format
                if hasattr(video, '_player') and video._player:
                    if hasattr(video._player, 'source') and video._player.source:
                        if hasattr(video._player.source, 'video_format'):
                            if hasattr(video._player.source.video_format, 'frame_rate'):
                                actual_video_fps = video._player.source.video_format.frame_rate
                                print(f"📏 Video frame rate (method 1): {actual_video_fps:.1f} fps")
                
                # Method 2: Try accessing fps property directly
                if not actual_video_fps and hasattr(video, 'fps'):
                    actual_video_fps = video.fps
                    print(f"📏 Video frame rate (method 2): {actual_video_fps:.1f} fps")
                
                # Method 3: Try video._player properties
                if not actual_video_fps and hasattr(video, '_player') and video._player:
                    if hasattr(video._player, 'fps'):
                        actual_video_fps = video._player.fps
                        print(f"📏 Video frame rate (method 3): {actual_video_fps:.1f} fps")
                
                # Use actual video fps if we found it and it's reasonable
                if actual_video_fps and actual_video_fps > 0 and actual_video_fps <= 120:
                    video_fps = actual_video_fps
                    print(f"✅ Using actual video frame rate: {video_fps:.1f} fps")
                else:
                    print(f"📏 Keeping display-based frame rate: {video_fps:.1f} fps")
                    
            except Exception as e:
                print(f"⚠️ Could not get video properties: {e}")
                print(f"📏 Keeping fallback frame rate: {video_fps:.1f} fps")
            
            # Adjust safety limit based on video duration
            if video_duration:
                # Allow 2x the expected duration at 60fps display rate as safety margin
                expected_display_frames = video_duration * 60.0 * 2.0
                max_frames = max(int(expected_display_frames), 18000)
                print(f"🔒 Adjusted safety limit to {max_frames} frames (2x duration at 60fps)")
            
            # CRITICAL: Explicitly start video playback
            video.play()
            print("▶️ Video.play() called - starting playback")
            
            # DEBUG: Print actual video information during playback
            try:
                print(f"🔍 DEBUG - Video Playback Info:")
                print(f"   Video size: {video.size}")
                print(f"   Video position: {video.pos}")
                print(f"   Window size: {self.win.size}")
                if hasattr(video, 'movieSize'):
                    print(f"   Original video dimensions: {video.movieSize}")
                if hasattr(video, 'aspectRatio'):
                    print(f"   Video aspect ratio: {video.aspectRatio:.2f}")
            except Exception as e:
                print(f"   Could not get video info: {e}")
            
            # Record actual start time for accurate timing
            playback_start_time = core.getTime()
            print(f"⏰ Playback started at: {playback_start_time:.3f}")
            
            while True:
                # CRITICAL: Only draw video - NO TEXT during playback
                video.draw()
                self.win.flip()
                frame_count += 1
                
                current_status = video.status
                
                # Track status changes (only log significant ones)
                if current_status == last_status:
                    consecutive_same_status += 1
                else:
                    # Only log status changes that might indicate completion or issues
                    if current_status == visual.FINISHED or consecutive_same_status > 60:
                        print(f"📝 Video status: {last_status} → {current_status} (frame {frame_count})")
                    consecutive_same_status = 0
                    last_status = current_status
                
                # Progress updates every 5 seconds (300 frames at 60fps) instead of every second
                if frame_count % 300 == 0:
                    current_real_time = core.getTime()
                    elapsed_time = current_real_time - playback_start_time
                    
                    if video_duration:
                        progress_pct = (elapsed_time / video_duration) * 100
                        remaining_time = max(0, video_duration - elapsed_time)
                        print(f"🎞️ Video: {progress_pct:.0f}% complete ({elapsed_time:.0f}s/{video_duration:.0f}s, ~{remaining_time:.0f}s remaining)")
                    else:
                        print(f"🎞️ Video: {elapsed_time:.0f}s elapsed, frame {frame_count}")
                
                # Check for escape key during playback
                keys = event.getKeys()
                if 'escape' in keys:
                    video_skipped = True
                    print(f"🔄 Video skipped by user (ESC pressed) at frame {frame_count}")
                    break
                
                # Method 1: Check if status changed to FINISHED
                if current_status == visual.FINISHED:
                    video_naturally_ended = True
                    print(f"✅ Video finished (status = FINISHED)")
                    break
                
                                # Method 2: Use video's actual time property if available (PRIMARY METHOD)
                actual_video_time = None
                try:
                    if hasattr(video, '_player') and video._player and hasattr(video._player, 'time'):
                        actual_video_time = video._player.time
                        if video_duration and actual_video_time >= video_duration:
                            video_naturally_ended = True
                            print(f"✅ Video finished (internal time reached duration)")
                            break
                    # Try VLC player time method
                    elif hasattr(video, 'getCurrentFrameTime'):
                        actual_video_time = video.getCurrentFrameTime()
                        if video_duration and actual_video_time >= video_duration:
                            video_naturally_ended = True
                            print(f"✅ Video finished (frame time reached duration)")
                            break
                    # DISABLED: Percentage completion method (unreliable)
                    # elif hasattr(video, 'getPercentageComplete'):
                    #     percentage = video.getPercentageComplete()
                    #     if percentage >= 99.0:  # 99% to account for rounding
                    #         video_naturally_ended = True
                    #         print(f"✅ Video percentage reached completion ({percentage:.1f}% >= 99%)")
                    #         break
                except Exception as e:
                    print(f"⚠️ Video time check failed: {e}")

                # Method 3: Use REAL ELAPSED TIME (most accurate)
                if video_duration:
                    current_real_time = core.getTime()
                    elapsed_time = current_real_time - playback_start_time
                    if elapsed_time >= video_duration:
                        video_naturally_ended = True
                        print(f"✅ Video finished (elapsed time reached duration)")
                        break
                
                                # Method 4: Safety fallback - only if REAL elapsed time is way beyond expected
                if video_duration:
                    current_real_time = core.getTime()
                    elapsed_time = current_real_time - playback_start_time
                    # Only trigger if we're 30+ seconds past expected duration (something is really wrong)
                    if elapsed_time > (video_duration + 30) and consecutive_same_status > 300:
                        print(f"⚠️ SAFETY: Video exceeded expected duration - forcing completion")
                        video_naturally_ended = True
                        break
                else:
                    # Fallback if no duration available - use longer time limits
                    if consecutive_same_status > 1800 and frame_count > 7200:  # 1 minute unchanged after 4 minutes
                        print(f"⚠️ SAFETY: Video appears stuck - forcing completion")
                        video_naturally_ended = True
                        break
                
                # Safety: Absolute maximum to prevent infinite loops
                if frame_count >= max_frames:
                    print(f"⚠️ SAFETY: Frame limit reached - forcing completion")
                    video_naturally_ended = True
                    break
            
            # Video playback completed
            
            should_show_completion = (video_naturally_ended or video_skipped) and frame_count > 60
            
            if should_show_completion:
                print(f"✅ Video completed ({'skipped' if video_skipped else 'finished'})")
                
                # Stop the video and show completion screen
                try:
                    if hasattr(video, 'stop'):
                        video.stop()
                    if hasattr(video, 'pause'):
                        video.pause()
                except Exception as e:
                    print(f"⚠️ Could not stop video: {e}")
                
                core.wait(0.5)  # Brief pause for video to stop
                
                # Show completion message
                self.instruction_text.text = "Video completed.\n\nPress ESC key to continue..."
                self.instruction_text.pos = (0, -200)  # Below video
                self.instruction_text.color = [1, 1, 1]  # White text
                
                # Draw final frame with completion text
                try:
                    video.draw()
                    self.instruction_text.draw()
                    self.win.flip()
                    print("📺 Video completion screen displayed - waiting for ESC key...")
                except Exception as e:
                    print(f"⚠️ Could not draw completion screen: {e}")
            else:
                print("❌ Video did not complete properly - skipping completion screen")
                return
            
            # Wait for escape key to continue
            event.waitKeys(keyList=['escape'])
            print("✅ Continuing experiment")
            
            # Reset text position to better left positioning for equal margins
            self.instruction_text.pos = (-500, 0)
                        
        except Exception as e:
            print(f"Error playing video: {e}")
            self.show_video_placeholder(video_key)
        
        # Collect mood congruency rating if requested (for mood induction videos)
        if collect_rating:
            print(f"📊 Collecting mood congruency rating after video")
            rating = self.get_velten_rating_slider_safe()  # Use the same rating scale as Velten
            
            # Save video data with rating
            self.save_trial_data({
                'phase': 'video_stimulus_with_rating',
                'video_file': str(config.VIDEO_FILES[video_key]),
                'velten_rating': rating,  # Using velten_rating field for consistency
                'block_type': None, 'block_number': None, 'trial_number': None,
                'stimulus': None, 'stimulus_position': None, 'response': None,
                'correct_response': None, 'accuracy': None, 'reaction_time': None,
                'mood_rating': None, 'mw_tut_rating': None, 'mw_fmt_rating': None,
                'audio_file': None, 'velten_statement': None
            })
        else:
            # Save video data without rating
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
        keys = event.waitKeys()
        if keys and 'escape' in keys:
            core.quit()
    
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
            
            # IMPORTANT: Do NOT randomize - statements must be presented in exact order
            
            # Apply demo mode reduction BEFORE printing the count
            if config.DEMO_MODE:
                original_count = len(statements)
                statements = statements[:3]  # Only use first 3 statements in demo
                print(f"Loaded {len(statements)} {valence} statements from {set_key} ({phase_type}) - Demo mode (reduced from {original_count})")
            else:
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
        
        # Debug audio file existence
        print(f"🔍 Audio file check: {audio_file}")
        print(f"   Exists: {audio_file.exists()}")
        if audio_file.exists():
            print(f"   Size: {audio_file.stat().st_size} bytes")
        else:
            print(f"   ❌ Audio file not found!")
        
        # Instant audio playback using preloaded files
        audio_loaded = False
        self.current_audio = None
        audio_key = f'{valence}_music'
        
        # Debug preloaded audio
        print(f"🔍 Preloaded audio check:")
        print(f"   Has preloaded_audio: {hasattr(self, 'preloaded_audio')}")
        if hasattr(self, 'preloaded_audio'):
            print(f"   Audio key '{audio_key}' in preloaded: {audio_key in self.preloaded_audio}")
            if audio_key in self.preloaded_audio:
                print(f"   Audio object is not None: {self.preloaded_audio[audio_key] is not None}")
                if self.preloaded_audio[audio_key] is not None:
                    audio_obj = self.preloaded_audio[audio_key]
                    print(f"   Audio object type: {type(audio_obj).__name__}")
                    print(f"   Has set_volume: {hasattr(audio_obj, 'set_volume')}")
                    print(f"   Has setVolume: {hasattr(audio_obj, 'setVolume')}")
                    print(f"   Has play: {hasattr(audio_obj, 'play')}")
                    print(f"   Has setLoops: {hasattr(audio_obj, 'setLoops')}")
        
        # Try preloaded audio first (instant playback)
        if hasattr(self, 'preloaded_audio') and audio_key in self.preloaded_audio and self.preloaded_audio[audio_key] is not None:
            try:
                self.current_audio = self.preloaded_audio[audio_key]
                
                # Check if it's pygame or PsychoPy sound and use appropriate methods
                if hasattr(self.current_audio, 'set_volume'):
                    # pygame.mixer.Sound
                    self.current_audio.set_volume(0.7)
                    self.current_audio.play(loops=-1)
                    print(f"🎵 Audio started instantly (pygame): {audio_file.name}")
                elif hasattr(self.current_audio, 'setVolume'):
                    # PsychoPy Sound
                    self.current_audio.setVolume(0.7)
                    # Try to set looping if supported
                    if hasattr(self.current_audio, 'setLoops'):
                        self.current_audio.setLoops(-1)  # Set infinite looping
                        print(f"🎵 Audio started instantly (PsychoPy with looping): {audio_file.name}")
                    else:
                        print(f"🎵 Audio started instantly (PsychoPy, single play): {audio_file.name}")
                        print(f"   ⚠️ Note: Looping not supported, music will play once")
                    self.current_audio.play()
                else:
                    raise AttributeError("Unknown audio object type")
                
                audio_loaded = True
                
                # Wait a brief moment to ensure audio starts
                core.wait(0.1)
                print(f"🎵 Audio playback confirmed")
                
            except Exception as e:
                # If preloaded fails, fall back to loading
                print(f"Preloaded audio failed: {str(e)}")
                print(f"   Will attempt to load fresh audio file...")
                
        # Fallback to regular loading if preload unavailable
        if not audio_loaded:
            if not audio_file.exists():
                print(f"⚠️ Audio file missing: {audio_file}")
                print(f"   Continuing without background music...")
                self.current_audio = None
                return  # Skip audio loading but continue with experiment
                
            print(f"🎵 Loading audio file: {audio_file}")
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
                print(f"🎵 Audio loaded and playing: {audio_file.name}")
                
                # Wait a brief moment to ensure audio starts
                core.wait(0.1)
                print(f"🎵 Pygame audio playback confirmed")
                
            except Exception as e:
                try:
                    self.current_audio = sound.Sound(str(audio_file))
                    self.current_audio.setVolume(0.7)
                    # Try to set looping if supported
                    if hasattr(self.current_audio, 'setLoops'):
                        self.current_audio.setLoops(-1)  # Set infinite looping
                        print(f"🎵 Audio loaded and playing (PsychoPy with looping): {audio_file.name}")
                    else:
                        print(f"🎵 Audio loaded and playing (PsychoPy, single play): {audio_file.name}")
                        print(f"   ⚠️ Note: Looping not supported, music will play once")
                    self.current_audio.play()
                    audio_loaded = True
                    
                    # Wait a brief moment to ensure audio starts
                    core.wait(0.1)
                    print(f"🎵 PsychoPy audio playback confirmed")
                except Exception as e2:
                    print(f"⚠️ Audio unavailable: {str(e2)[:50]}...")
                    self.current_audio = None
        
        # Demo mode reduction already applied in load_velten_statements() method
        
        # Present statements with ratings every 4 statements
        for i, statement in enumerate(statements):
            # Add 5-second black screen between statements (not before the first one, and not after ratings)
            # Skip black screen after statements 4 and 8 (where ratings occur)
            if i > 0 and i != 4 and i != 8:
                self.win.flip()  # Show black screen
                print(f"⬛ 5-second black screen between statements {i} and {i+1}")
                core.wait(5.0)  # Wait 5 seconds with black screen
            
            # Show statement for specified duration using centered text
            self.velten_text.text = statement
            self.velten_text.draw()
            self.win.flip()
            
            # Wait for statement duration while keeping audio playing and clearing keyboard events
            statement_start_time = core.getTime()
            statement_duration = config.TIMING['velten_statement_duration']
            
            while (core.getTime() - statement_start_time) < statement_duration:
                # Clear any keyboard events during statement display to prevent carryover
                event.clearEvents(eventType='keyboard')
                core.wait(0.1)  # Small wait to prevent excessive CPU usage
            
            print(f"🔄 Keyboard events cleared during statement {i+1} display")
            
            # UPDATED: Collect mood congruency rating every 4 statements
            # Each set has 12 statements, so ratings after statements 4 and 8
            # No rating after statement 12 (mood scale will be collected instead)
            rating = None
            if (i + 1) == 4 or (i + 1) == 8:  # After statements 4 and 8 only
                print(f"📊 Collecting mood congruency rating after statement {i+1}")
                rating = self.get_velten_rating_slider_safe()  # Use safe version that doesn't interfere with audio
            
            # Save Velten data (with rating when collected)
            self.save_trial_data({
                'phase': 'velten_statements',
                'velten_statement': statement,
                'velten_rating': rating,  # Rating collected after statements 4 and 8
                'audio_file': str(audio_file) if audio_loaded else None,
                'block_type': None, 'block_number': None, 'trial_number': i + 1,
                'stimulus': None, 'stimulus_position': None, 'response': None,
                'correct_response': None, 'accuracy': None, 'reaction_time': None,
                'mood_rating': None, 'mw_tut_rating': None, 'mw_fmt_rating': None,
                'video_file': None
            })
        
        # UPDATED: Collect mood scale rating at the end of each Velten set
        print(f"📊 Collecting mood scale rating at end of Velten {valence} set")
        mood_rating = self.collect_mood_rating(f'post_velten_{valence}')
        
        # Save mood rating data
        self.save_trial_data({
            'phase': 'mood_rating_post_velten',
            'velten_statement': None,
            'velten_rating': None,
            'audio_file': str(audio_file) if audio_loaded else None,
            'block_type': None, 'block_number': None, 'trial_number': None,
            'stimulus': None, 'stimulus_position': None, 'response': None,
            'correct_response': None, 'accuracy': None, 'reaction_time': None,
            'mood_rating': mood_rating, 
            'mw_tut_rating': None, 'mw_fmt_rating': None,
                'video_file': None
            })
        
        # FIXED: Properly stop music after all statements
        if self.current_audio and audio_loaded:
            try:
                # Both pygame and PsychoPy sounds have stop() method
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
    
    def get_velten_rating_slider_safe(self):
        """SAFE VERSION: Get Velten rating without interfering with audio playback
        This version doesn't stop or restart audio, allowing music to continue seamlessly"""
        print(f"📝 COLLECTING VELTEN RATING (Safe Interactive Slider - Music Continues)")
        
        # Check if audio is currently playing
        audio_playing = False
        if hasattr(self, 'current_audio') and self.current_audio:
            audio_playing = True
            print(f"   🎵 Music continues playing during rating...")
        
        # Store original text position and alignment to restore later
        original_pos = self.instruction_text.pos
        original_align = self.instruction_text.alignText
        original_anchor = self.instruction_text.anchorHoriz
        
        # Center text like mind wandering probes
        self.instruction_text.pos = (0, 150)  # Move to top center of screen
        self.instruction_text.alignText = 'center'
        self.instruction_text.anchorHoriz = 'center'
        
        # Start at middle of scale (4)
        current_value = 4
        self.velten_slider.reset()
        self.velten_slider.rating = current_value
        
        # Updated instruction text for interactive slider (adaptive for video or statements)
        instruction_text = """To what extent were you able to bring your mood in line with what you just experienced?

Move the slider or use A/D keys to adjust your rating, then press ENTER to confirm.

A = decrease rating, D = increase rating

Current rating: {}"""
        
        # Get scale labels for current value
        scale_labels = config.VELTEN_RATING_SCALE['scale_labels']
        # Mouse for wheel scrolling support over the slider
        mouse = event.Mouse(win=self.win)
        tolerance_px = 10  # extra vertical band around slider for easier targeting
        
        # Keyboard for continuous A/D hold support and single press debounce
        kb = keyboard.Keyboard()
        key_repeat_interval = 0.16  # seconds between repeats when holding key
        hold_start_delay = 0.3  # delay before hold behavior starts (300ms)
        _last_repeat_time = core.getTime()
        _key_press_start_time = {'a': None, 'd': None}  # Track when keys were first pressed
        _key_processed_as_single = {'a': False, 'd': False}  # Track if key was processed as single press
        
        while True:
            # Handle mouse wheel scrolling when cursor is over the slider
            wheel_y = mouse.getWheelRel()[1]
            if wheel_y != 0:
                # Cursor position
                mouse_x, mouse_y = mouse.getPos()
                # Slider geometry (in pix)
                slider_center_x, slider_center_y = self.velten_slider.pos
                slider_width, slider_height = self.velten_slider.size
                left_x = slider_center_x - (slider_width / 2.0)
                right_x = slider_center_x + (slider_width / 2.0)
                top_y = slider_center_y + (slider_height / 2.0) + tolerance_px
                bottom_y = slider_center_y - (slider_height / 2.0) - tolerance_px
                # Only apply wheel change if cursor is within slider band
                if (bottom_y <= mouse_y <= top_y) and (left_x <= mouse_x <= right_x):
                    delta = 1 if wheel_y > 0 else -1
                    new_value = max(1, min(7, current_value + delta))
                    if new_value != current_value:
                        current_value = new_value
                        self.velten_slider.rating = current_value
            
            # Handle keyboard input with proper single press vs hold distinction
            now = core.getTime()
            
            # Check for currently held keys
            held_a = kb.getKeys(keyList=['a'], waitRelease=False, clear=False)
            held_d = kb.getKeys(keyList=['d'], waitRelease=False, clear=False)
            
            # Track key press start times
            if held_a and _key_press_start_time['a'] is None:
                _key_press_start_time['a'] = now
                _key_processed_as_single['a'] = False
            elif not held_a:
                _key_press_start_time['a'] = None
                _key_processed_as_single['a'] = False
                
            if held_d and _key_press_start_time['d'] is None:
                _key_press_start_time['d'] = now
                _key_processed_as_single['d'] = False
            elif not held_d:
                _key_press_start_time['d'] = None
                _key_processed_as_single['d'] = False
            
            # Handle 'A' key (decrease)
            key_handled_by_hold = False
            if held_a and _key_press_start_time['a'] is not None:
                key_hold_duration = now - _key_press_start_time['a']
                
                if key_hold_duration < hold_start_delay and not _key_processed_as_single['a']:
                    # Process as single press (only once)
                    new_value = max(1, current_value - 1)
                    if new_value != current_value:
                        current_value = new_value
                        self.velten_slider.rating = current_value
                        _key_processed_as_single['a'] = True
                elif key_hold_duration >= hold_start_delay and now - _last_repeat_time >= key_repeat_interval:
                    # Process as continuous hold
                    new_value = max(1, current_value - 1)
                    if new_value != current_value:
                        current_value = new_value
                        self.velten_slider.rating = current_value
                        _last_repeat_time = now
                        key_handled_by_hold = True
            
            # Handle 'D' key (increase)
            if held_d and _key_press_start_time['d'] is not None:
                key_hold_duration = now - _key_press_start_time['d']
                
                if key_hold_duration < hold_start_delay and not _key_processed_as_single['d']:
                    # Process as single press (only once)
                    new_value = min(7, current_value + 1)
                    if new_value != current_value:
                        current_value = new_value
                        self.velten_slider.rating = current_value
                        _key_processed_as_single['d'] = True
                elif key_hold_duration >= hold_start_delay and now - _last_repeat_time >= key_repeat_interval:
                    # Process as continuous hold
                    new_value = min(7, current_value + 1)
                    if new_value != current_value:
                        current_value = new_value
                        self.velten_slider.rating = current_value
                        _last_repeat_time = now
                        key_handled_by_hold = True
            
            # Also update based on direct slider movement (drag/click)
            slider_val = self.velten_slider.getRating()
            if slider_val is not None:
                current_value = int(slider_val)
            
            # Update instruction text with current label
            current_label = scale_labels[current_value - 1]  # Convert to 0-based index
            self.instruction_text.text = instruction_text.format(current_label)
            self.instruction_text.draw()
            # Don't draw the invisible built-in slider - using custom tick marks instead
            # Draw horizontal line
            self.velten_horizontal_line.draw()
            # Draw custom tick marks with different heights
            for tick_mark in self.velten_tick_marks:
                tick_mark.draw()
            # Draw text labels at start and end
            self.velten_start_label.draw()
            self.velten_end_label.draw()
            # Draw red marker at current position
            self.draw_velten_marker(current_value)
            self.win.flip()
            
            # Handle ENTER and ESCAPE keys
            if not key_handled_by_hold:
                keys = event.getKeys()
                
                for key in keys:
                    if key == 'escape':
                        print("ESCAPE key detected, quitting...")
                        # Restore original text position and alignment before quitting
                        self.instruction_text.pos = original_pos
                        self.instruction_text.alignText = original_align
                        self.instruction_text.anchorHoriz = original_anchor
                        core.quit()
                    elif key == 'return':
                        # Confirm selection
                        print(f"📝 Velten Statement Rating: {current_value}/7 (mood alignment)")
                        if audio_playing:
                            print(f"   🎵 Music continues playing...")
                        # Restore original text position and alignment
                        self.instruction_text.pos = original_pos
                        self.instruction_text.alignText = original_align
                        self.instruction_text.anchorHoriz = original_anchor
                        return current_value
    
    def get_velten_rating_slider(self):
        """UPDATED: Get Velten rating using interactive slider (7-point scale as specified in PDF)"""
        print(f"📝 COLLECTING VELTEN RATING (Interactive Slider)")
        
        # Store original text position and alignment to restore later
        original_pos = self.instruction_text.pos
        original_align = self.instruction_text.alignText
        original_anchor = self.instruction_text.anchorHoriz
        
        # Center text like mind wandering probes
        self.instruction_text.pos = (0, 150)  # Move to top center of screen
        self.instruction_text.alignText = 'center'
        self.instruction_text.anchorHoriz = 'center'
        
        # Start at middle of scale (4)
        current_value = 4
        self.velten_slider.reset()
        self.velten_slider.rating = current_value
        
        # Updated instruction text for interactive slider with current rating display
        instruction_text = """To what extent were you able to bring your mood in line with this statement?

Move the slider or use A/D keys to adjust your rating, then press ENTER to confirm.

A = decrease rating, D = increase rating

Current rating: {}"""
        
        # Get scale labels for current value
        scale_labels = config.VELTEN_RATING_SCALE['scale_labels']
        # Mouse for wheel scrolling support over the slider
        mouse = event.Mouse(win=self.win)
        tolerance_px = 10  # extra vertical band around slider for easier targeting
        
        # Keyboard for continuous A/D hold support and single press debounce
        kb = keyboard.Keyboard()
        key_repeat_interval = 0.16  # seconds between repeats when holding key
        hold_start_delay = 0.3  # delay before hold behavior starts (300ms)
        _last_repeat_time = core.getTime()
        _key_press_start_time = {'a': None, 'd': None}  # Track when keys were first pressed
        _key_processed_as_single = {'a': False, 'd': False}  # Track if key was processed as single press
        
        while True:
            # Handle mouse wheel scrolling when cursor is over the slider
            wheel_y = mouse.getWheelRel()[1]
            if wheel_y != 0:
                # Cursor position
                mouse_x, mouse_y = mouse.getPos()
                # Slider geometry (in pix)
                slider_center_x, slider_center_y = self.velten_slider.pos
                slider_width, slider_height = self.velten_slider.size
                left_x = slider_center_x - (slider_width / 2.0)
                right_x = slider_center_x + (slider_width / 2.0)
                top_y = slider_center_y + (slider_height / 2.0) + tolerance_px
                bottom_y = slider_center_y - (slider_height / 2.0) - tolerance_px
                # Only apply wheel change if cursor is within slider band
                if (bottom_y <= mouse_y <= top_y) and (left_x <= mouse_x <= right_x):
                    delta = 1 if wheel_y > 0 else -1
                    new_value = max(1, min(7, current_value + delta))
                    if new_value != current_value:
                        current_value = new_value
                        self.velten_slider.rating = current_value
            
            # Handle keyboard input with proper single press vs hold distinction
            now = core.getTime()
            
            # Check for currently held keys
            held_a = kb.getKeys(keyList=['a'], waitRelease=False, clear=False)
            held_d = kb.getKeys(keyList=['d'], waitRelease=False, clear=False)
            
            # Track key press start times
            if held_a and _key_press_start_time['a'] is None:
                _key_press_start_time['a'] = now
                _key_processed_as_single['a'] = False
            elif not held_a:
                _key_press_start_time['a'] = None
                _key_processed_as_single['a'] = False
                
            if held_d and _key_press_start_time['d'] is None:
                _key_press_start_time['d'] = now
                _key_processed_as_single['d'] = False
            elif not held_d:
                _key_press_start_time['d'] = None
                _key_processed_as_single['d'] = False
            
            # Handle 'A' key (decrease)
            key_handled_by_hold = False
            if held_a and _key_press_start_time['a'] is not None:
                key_hold_duration = now - _key_press_start_time['a']
                
                if key_hold_duration < hold_start_delay and not _key_processed_as_single['a']:
                    # Process as single press (only once)
                    new_value = max(1, current_value - 1)
                    if new_value != current_value:
                        current_value = new_value
                        self.velten_slider.rating = current_value
                        _key_processed_as_single['a'] = True
                        print(f"🔍 DEBUG - A single press: value changed to {current_value}")
                elif key_hold_duration >= hold_start_delay and now - _last_repeat_time >= key_repeat_interval:
                    # Process as continuous hold
                    new_value = max(1, current_value - 1)
                    if new_value != current_value:
                        current_value = new_value
                        self.velten_slider.rating = current_value
                        _last_repeat_time = now
                        key_handled_by_hold = True
                        print(f"🔍 DEBUG - A hold: value changed to {current_value}")
            
            # Handle 'D' key (increase)
            if held_d and _key_press_start_time['d'] is not None:
                key_hold_duration = now - _key_press_start_time['d']
                
                if key_hold_duration < hold_start_delay and not _key_processed_as_single['d']:
                    # Process as single press (only once)
                    new_value = min(7, current_value + 1)
                    if new_value != current_value:
                        current_value = new_value
                        self.velten_slider.rating = current_value
                        _key_processed_as_single['d'] = True
                        print(f"🔍 DEBUG - D single press: value changed to {current_value}")
                elif key_hold_duration >= hold_start_delay and now - _last_repeat_time >= key_repeat_interval:
                    # Process as continuous hold
                    new_value = min(7, current_value + 1)
                    if new_value != current_value:
                        current_value = new_value
                        self.velten_slider.rating = current_value
                        _last_repeat_time = now
                        key_handled_by_hold = True
                        print(f"🔍 DEBUG - D hold: value changed to {current_value}")
            
            # Also update based on direct slider movement (drag/click)
            slider_val = self.velten_slider.getRating()
            if slider_val is not None:
                current_value = int(slider_val)
            
            # Update instruction text with current label
            current_label = scale_labels[current_value - 1]  # Convert to 0-based index
            self.instruction_text.text = instruction_text.format(current_label)
            self.instruction_text.draw()
            # Don't draw the invisible built-in slider - using custom tick marks instead
            # Draw horizontal line
            self.velten_horizontal_line.draw()
            # Draw custom tick marks with different heights
            for tick_mark in self.velten_tick_marks:
                tick_mark.draw()
            # Draw text labels at start and end
            self.velten_start_label.draw()
            self.velten_end_label.draw()
            # Draw red marker at current position
            self.draw_velten_marker(current_value)
            self.win.flip()
            
            # Handle ENTER and ESCAPE keys (only process if not handled by hold logic)
            if not key_handled_by_hold:
                keys = event.getKeys()
                
                for key in keys:
                    if key == 'escape':
                        print("🔍 DEBUG - ESCAPE key detected, quitting...")
                        # Restore original text position and alignment before quitting
                        self.instruction_text.pos = original_pos
                        self.instruction_text.alignText = original_align
                        self.instruction_text.anchorHoriz = original_anchor
                        core.quit()
                    elif key == 'return':
                        print(f"🔍 DEBUG - ENTER key pressed, confirming rating: {current_value}")
                        # Confirm selection
                        print(f"📝 Velten Statement Rating: {current_value}/7 (mood alignment)")
                        # Restore original text position and alignment
                        self.instruction_text.pos = original_pos
                        self.instruction_text.alignText = original_align
                        self.instruction_text.anchorHoriz = original_anchor
                        return current_value
    
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
        """Present mind-wandering probes using slider with custom tick marks and Continue button"""
        print(f"Presenting mind-wandering probe at trial {trial_number}")
        
        mouse = event.Mouse(win=self.win)
        
        # TUT probe
        self.instruction_text.text = config.MW_PROBES['tut']
        self.mw_tut_slider.reset()
        
        # Show TUT slider with button and wait for rating + button click or keyboard
        while True:
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
            
            # Check if rating has been made
            current_rating = self.mw_tut_slider.getRating()
            rating_made = current_rating is not None
            
            # Draw Continue button with appropriate styling
            if rating_made:
                # Active button - blue with white border
                self.mw_continue_button.fillColor = [0.0, 0.5, 1.0]
                self.mw_continue_button.lineColor = [1.0, 1.0, 1.0]
                self.mw_continue_button_text.color = [1.0, 1.0, 1.0]
            else:
                # Inactive button - grey
                self.mw_continue_button.fillColor = [0.5, 0.5, 0.5]
                self.mw_continue_button.lineColor = [0.7, 0.7, 0.7]
                self.mw_continue_button_text.color = [0.8, 0.8, 0.8]
            
            self.mw_continue_button.draw()
            self.mw_continue_button_text.draw()
            self.win.flip()
            
            # Check for escape
            if 'escape' in event.getKeys():
                core.quit()
            
            # Check for advancement (only if rating made)
            if rating_made:
                # Check for mouse click on button
                if mouse.isPressedIn(self.mw_continue_button):
                    break
                # Check for keyboard press
                keys = event.getKeys(['space', 'return'])
                if keys:
                    break
        
        tut_rating = self.mw_tut_slider.getRating()
        
        # FMT probe
        self.instruction_text.text = config.MW_PROBES['fmt']
        self.mw_fmt_slider.reset()
        
        # Show FMT slider with button and wait for rating + button click or keyboard
        while True:
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
            
            # Check if rating has been made
            current_rating = self.mw_fmt_slider.getRating()
            rating_made = current_rating is not None
            
            # Draw Continue button with appropriate styling
            if rating_made:
                # Active button - blue with white border
                self.mw_continue_button.fillColor = [0.0, 0.5, 1.0]
                self.mw_continue_button.lineColor = [1.0, 1.0, 1.0]
                self.mw_continue_button_text.color = [1.0, 1.0, 1.0]
            else:
                # Inactive button - grey
                self.mw_continue_button.fillColor = [0.5, 0.5, 0.5]
                self.mw_continue_button.lineColor = [0.7, 0.7, 0.7]
                self.mw_continue_button_text.color = [0.8, 0.8, 0.8]
            
            self.mw_continue_button.draw()
            self.mw_continue_button_text.draw()
            self.win.flip()
            
            # Check for escape
            if 'escape' in event.getKeys():
                core.quit()
            
            # Check for advancement (only if rating made)
            if rating_made:
                # Check for mouse click on button
                if mouse.isPressedIn(self.mw_continue_button):
                    break
                # Check for keyboard press
                keys = event.getKeys(['space', 'return'])
                if keys:
                    break
        
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
        
        # Generate trial sequence with 15% target digit (3) for RI condition, or 0% for NRI condition
        trials = []
        total_trials = config.SART_PARAMS['total_trials']
        
        if condition == 'RI':  # Response Inhibition - include target digit 3 at 15%
            # Calculate exact number of target trials (15% of total for this condition)
            target_trials = int(total_trials * 0.15)  # 18 trials out of 120
            non_target_trials = total_trials - target_trials  # 102 trials
            
            # Create digit list with correct proportions
            digit_list = []
            # Add target trials (digit 3)
            digit_list.extend([3] * target_trials)
            # Add non-target trials (other digits 0-2, 4-9) - distribute evenly
            other_digits = [d for d in config.SART_PARAMS['digits'] if d != 3]  # [0,1,2,4,5,6,7,8,9]
            for i in range(non_target_trials):
                digit_list.append(other_digits[i % len(other_digits)])
            
            print(f"📊 SART Block {block_number} ({condition}): Generated {target_trials} target trials (digit 3) ({target_trials/total_trials*100:.1f}%) out of {total_trials} total trials")
        else:  # NRI - Non-Response Inhibition - no target digit 3
            # All trials are non-target (digits 0-2, 4-9) - distribute evenly
            other_digits = [d for d in config.SART_PARAMS['digits'] if d != 3]  # [0,1,2,4,5,6,7,8,9]
            digit_list = []
            for i in range(total_trials):
                digit_list.append(other_digits[i % len(other_digits)])
            
            print(f"📊 SART Block {block_number} ({condition}): Generated 0 target trials (digit 3) - all digits are non-targets for NRI condition")
        
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
        
        # Generate step sizes that total exactly 120 trials
        steps = config.SART_PARAMS['steps_per_block']  # 8 steps
        min_per_step = config.SART_PARAMS['trials_per_step_min']  # 13
        max_per_step = config.SART_PARAMS['trials_per_step_max']  # 17
        
        # Generate step sizes
        step_sizes = []
        remaining_trials = total_trials
        
        for i in range(steps - 1):  # First 7 steps
            # Calculate constraints for this step
            remaining_steps = steps - i
            max_possible = min(max_per_step, remaining_trials - min_per_step * (remaining_steps - 1))
            min_possible = max(min_per_step, remaining_trials - max_per_step * (remaining_steps - 1))
            
            # Choose random size within constraints
            step_size = random.randint(min_possible, max_possible)
            step_sizes.append(step_size)
            remaining_trials -= step_size
        
        # Last step gets remaining trials
        step_sizes.append(remaining_trials)
        
        print(f"📊 Step sizes: {step_sizes} (total: {sum(step_sizes)})")
        
        # Initialize performance tracking
        total_correct = 0
        total_rts = []
        
        print(f"\n🎯 Starting SART Block {block_number} ({condition}) - 8 steps with probes")
        print("=" * 60)
        
        # Run 8 steps with probes
        trial_index = 0
        
        for step_num in range(1, steps + 1):
            step_size = step_sizes[step_num - 1]
            print(f"\n📍 Step {step_num}/{steps}: {step_size} trials")
            
            # Run trials for this step
            step_correct = 0
            for i in range(step_size):
                trial = trials[trial_index]
                response, rt, accuracy = self.run_sart_trial(trial, condition, block_number, cue_circle)
                
                if accuracy == 1:
                    step_correct += 1
                    total_correct += 1
                if rt is not None:
                    total_rts.append(rt)
                
                trial_index += 1
            
            # Mind-wandering probe after each step
            print(f"📝 Mind-wandering probe after step {step_num}")
            self.run_mind_wandering_probe_slider_ad_keys(condition, block_number, step_num)
            
            print(f"✅ Step {step_num} completed: {step_correct}/{step_size} correct")
        
        # Final summary
        print("=" * 60)
        print(f"📊 SART Block {block_number} Summary:")
        print(f"   Total Steps: {steps}")
        print(f"   Total Trials: {trial_index}")
        print(f"   Total Probes: {steps}")
        print(f"   Overall Accuracy: {total_correct}/{total_trials} ({100*total_correct/total_trials:.1f}%)")
        
        if total_rts:
            avg_rt = sum(total_rts) / len(total_rts)
            print(f"   Average RT: {avg_rt*1000:.0f}ms (n={len(total_rts)})")
        
        print("=" * 60)
        print(f"🏁 SART Block {block_number} ({condition}) COMPLETED")
        
        # CRITICAL: Return control to main experiment
        return
    
    def run_sart_trial(self, trial, condition, block_number, cue_circle):
        """Run a single SART trial with improved stability"""
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
        
        # Start trial clock and record stimulus onset time
        self.trial_clock.reset()
        self.kb.clearEvents()
        stimulus_onset_time = self.trial_clock.getTime()  # Record when stimulus appeared
        
        # FIXED: Display digit for full duration regardless of key press
        response = None
        rt = None
        
        # FIXED: Collect keys during extended response window for mind-wandering research
        # This ensures we capture even very slow reaction times that indicate mind-wandering
        max_response_time = config.SART_PARAMS['max_response_time']
        start_time = self.trial_clock.getTime()
        keys_pressed = []
        stimulus_shown = True
        first_key_time = None  # Track when the first key was pressed
        
        # Frame rate limiting for SART trials
        frame_duration = 1.0 / 60.0  # Target 60 FPS
        last_frame_time = self.trial_clock.getTime()
        
        try:
            while self.trial_clock.getTime() - start_time < max_response_time:
                current_time = self.trial_clock.getTime() - start_time
                current_frame_time = self.trial_clock.getTime()
            
                # Only update display at 60 FPS to prevent excessive rendering
                if current_frame_time - last_frame_time >= frame_duration:
                    # Hide stimulus after stimulus_duration, show fixation + cue for remainder
                    if stimulus_shown and current_time >= config.SART_PARAMS['stimulus_duration']:
                        self.fixation.draw()
                        cue_circle.draw()
                        self.win.flip()
                        stimulus_shown = False
                    
                    last_frame_time = current_frame_time
            
                # Check for key presses throughout the entire trial duration
                keys = self.kb.getKeys(keyList=['left', 'right', 'escape'], waitRelease=False)
                if keys:
                    # Record the first key press (if multiple keys pressed)
                    if not keys_pressed:
                        keys_pressed = keys
                        first_key_time = self.trial_clock.getTime()  # Record when key was pressed
                    # Handle escape immediately
                    if keys[0].name == 'escape':
                        self.cleanup_and_quit()
                
                # Small wait to prevent excessive CPU usage
                core.wait(0.01)  # Increased from 0.001 to 0.01 (10ms)
                
        except Exception as e:
            print(f"⚠️  SART trial error: {e}")
            print("🔄 Continuing with next trial...")
            # Set default values to prevent crash
            response = None
            rt = None
        
        # Process the first key press if any occurred
        if keys_pressed:
            response = keys_pressed[0].name
            # FIXED: Calculate RT from stimulus onset to key press time
            rt = first_key_time - stimulus_onset_time
        
        # Determine accuracy
        if correct_response is None:  # Target trial (should not respond)
            accuracy = 1 if response is None else 0
        else:  # Non-target trial (should respond correctly)
            accuracy = 1 if response == correct_response else 0
        
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
        
        # Ensure proper inter-trial interval after extended response window
        # If response came early, wait for remaining ISI time
        elapsed_time = self.trial_clock.getTime() - start_time
        min_trial_time = config.SART_PARAMS['stimulus_duration'] + config.SART_PARAMS['isi_duration']
        if elapsed_time < min_trial_time:
            remaining_time = min_trial_time - elapsed_time
            core.wait(remaining_time)
        
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
    
    def run_mind_wandering_probe_slider_ad_keys(self, condition, block_number, trial_number):
        """Present mind-wandering probes using slider with A/D key control"""
        print(f"Presenting mind-wandering probe at trial {trial_number}")
        
        # TUT probe with A/D key control
        tut_value = 4  # Start at middle (4 out of 7)
        self.mw_tut_slider.reset()
        self.mw_tut_slider.rating = tut_value
        
        instruction_text = """{}

Move slider or use A/D keys to adjust rating | ENTER = confirm

A = decrease rating, D = increase rating

Current rating: {}"""
        
        scale_labels = ['Not at all', 'Slightly', 'Somewhat', 'Moderately', 'Quite a bit', 'Very much', 'Completely']
        
        # Mouse for wheel scrolling and keyboard for continuous hold
        mouse = event.Mouse(win=self.win)
        kb = keyboard.Keyboard()
        tolerance_px = 10
        key_repeat_interval = 0.16  # seconds between repeats when holding key
        hold_start_delay = 0.3  # delay before hold behavior starts (300ms)
        _last_repeat_time = core.getTime()
        _key_press_start_time = {'a': None, 'd': None}  # Track when keys were first pressed
        _key_processed_as_single = {'a': False, 'd': False}  # Track if key was processed as single press
        
        while True:
            # Handle mouse wheel scrolling when cursor is over the slider
            wheel_y = mouse.getWheelRel()[1]
            if wheel_y != 0:
                mouse_x, mouse_y = mouse.getPos()
                slider_center_x, slider_center_y = self.mw_tut_slider.pos
                slider_width, slider_height = self.mw_tut_slider.size
                left_x = slider_center_x - (slider_width / 2.0)
                right_x = slider_center_x + (slider_width / 2.0)
                top_y = slider_center_y + (slider_height / 2.0) + tolerance_px
                bottom_y = slider_center_y - (slider_height / 2.0) - tolerance_px
                if (bottom_y <= mouse_y <= top_y) and (left_x <= mouse_x <= right_x):
                    delta = 1 if wheel_y > 0 else -1
                    new_value = max(1, min(7, tut_value + delta))
                    if new_value != tut_value:
                        tut_value = new_value
                        self.mw_tut_slider.rating = tut_value
            
            # Handle keyboard input with proper single press vs hold distinction
            now = core.getTime()
            
            # Check for currently held keys
            held_a = kb.getKeys(keyList=['a'], waitRelease=False, clear=False)
            held_d = kb.getKeys(keyList=['d'], waitRelease=False, clear=False)
            
            # Track key press start times
            if held_a and _key_press_start_time['a'] is None:
                _key_press_start_time['a'] = now
                _key_processed_as_single['a'] = False
            elif not held_a:
                _key_press_start_time['a'] = None
                _key_processed_as_single['a'] = False
                
            if held_d and _key_press_start_time['d'] is None:
                _key_press_start_time['d'] = now
                _key_processed_as_single['d'] = False
            elif not held_d:
                _key_press_start_time['d'] = None
                _key_processed_as_single['d'] = False
            
            # Handle 'A' key (decrease)
            if held_a and _key_press_start_time['a'] is not None:
                key_hold_duration = now - _key_press_start_time['a']
                
                if key_hold_duration < hold_start_delay and not _key_processed_as_single['a']:
                    # Process as single press (only once)
                    new_value = max(1, tut_value - 1)
                    if new_value != tut_value:
                        tut_value = new_value
                        self.mw_tut_slider.rating = tut_value
                        _key_processed_as_single['a'] = True
                        print(f"🔍 DEBUG TUT - A single press: value changed to {tut_value}")
                elif key_hold_duration >= hold_start_delay and now - _last_repeat_time >= key_repeat_interval:
                    # Process as continuous hold
                    new_value = max(1, tut_value - 1)
                    if new_value != tut_value:
                        tut_value = new_value
                        self.mw_tut_slider.rating = tut_value
                        _last_repeat_time = now
                        print(f"🔍 DEBUG TUT - A hold: value changed to {tut_value}")
            
            # Handle 'D' key (increase)
            if held_d and _key_press_start_time['d'] is not None:
                key_hold_duration = now - _key_press_start_time['d']
                
                if key_hold_duration < hold_start_delay and not _key_processed_as_single['d']:
                    # Process as single press (only once)
                    new_value = min(7, tut_value + 1)
                    if new_value != tut_value:
                        tut_value = new_value
                        self.mw_tut_slider.rating = tut_value
                        _key_processed_as_single['d'] = True
                        print(f"🔍 DEBUG TUT - D single press: value changed to {tut_value}")
                elif key_hold_duration >= hold_start_delay and now - _last_repeat_time >= key_repeat_interval:
                    # Process as continuous hold
                    new_value = min(7, tut_value + 1)
                    if new_value != tut_value:
                        tut_value = new_value
                        self.mw_tut_slider.rating = tut_value
                        _last_repeat_time = now
                        print(f"🔍 DEBUG TUT - D hold: value changed to {tut_value}")
            
            # Handle ENTER and ESCAPE keys
            keys = event.getKeys()
            break_main_loop = False
            if keys:
                print(f"🔍 DEBUG TUT - Keys pressed: {keys}")
                for key in keys:
                    if key == 'escape':
                        print("🔍 DEBUG TUT - ESCAPE key detected, quitting...")
                        core.quit()
                    elif key == 'return':
                        print(f"🔍 DEBUG TUT - ENTER key pressed, confirming rating: {tut_value}")
                        print("🔍 DEBUG TUT - Breaking from TUT loop...")
                        break_main_loop = True
                        break
            
            # Break out of main loop if ENTER was pressed
            if break_main_loop:
                break
            
            # Also update based on direct slider movement (after keyboard input)
            slider_val = self.mw_tut_slider.getRating()
            if slider_val is not None:
                tut_value = int(slider_val)
            
            # Update instruction with current label only (no number)
            current_label = scale_labels[tut_value - 1]  # Convert to 0-based index
            self.instruction_text.text = instruction_text.format(config.MW_PROBES['tut'], current_label)
            
            # Temporarily move text higher to avoid overlap with slider
            original_pos = self.instruction_text.pos
            self.instruction_text.pos = (0, 150)  # Move to top center of screen
            self.instruction_text.alignText = 'center'
            self.instruction_text.anchorHoriz = 'center'
            
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
            
            # Restore original text position and alignment for other parts of experiment
            self.instruction_text.pos = original_pos
            self.instruction_text.alignText = 'left'
            self.instruction_text.anchorHoriz = 'left'
        
        tut_rating = tut_value
        
        # FMT probe with A/D key control
        fmt_value = 4  # Start at middle (4 out of 7)
        self.mw_fmt_slider.reset()
        self.mw_fmt_slider.rating = fmt_value
        
        # Reset mouse and keyboard for FMT probe
        mouse = event.Mouse(win=self.win)
        kb = keyboard.Keyboard()
        _last_repeat_time = core.getTime()
        _key_press_start_time = {'a': None, 'd': None}  # Track when keys were first pressed
        _key_processed_as_single = {'a': False, 'd': False}  # Track if key was processed as single press
        
        while True:
            # Handle mouse wheel scrolling when cursor is over the slider
            wheel_y = mouse.getWheelRel()[1]
            if wheel_y != 0:
                mouse_x, mouse_y = mouse.getPos()
                slider_center_x, slider_center_y = self.mw_fmt_slider.pos
                slider_width, slider_height = self.mw_fmt_slider.size
                left_x = slider_center_x - (slider_width / 2.0)
                right_x = slider_center_x + (slider_width / 2.0)
                top_y = slider_center_y + (slider_height / 2.0) + tolerance_px
                bottom_y = slider_center_y - (slider_height / 2.0) - tolerance_px
                if (bottom_y <= mouse_y <= top_y) and (left_x <= mouse_x <= right_x):
                    delta = 1 if wheel_y > 0 else -1
                    new_value = max(1, min(7, fmt_value + delta))
                    if new_value != fmt_value:
                        fmt_value = new_value
                        self.mw_fmt_slider.rating = fmt_value
            
            # Handle keyboard input with proper single press vs hold distinction
            now = core.getTime()
            
            # Check for currently held keys
            held_a = kb.getKeys(keyList=['a'], waitRelease=False, clear=False)
            held_d = kb.getKeys(keyList=['d'], waitRelease=False, clear=False)
            
            # Track key press start times
            if held_a and _key_press_start_time['a'] is None:
                _key_press_start_time['a'] = now
                _key_processed_as_single['a'] = False
            elif not held_a:
                _key_press_start_time['a'] = None
                _key_processed_as_single['a'] = False
                
            if held_d and _key_press_start_time['d'] is None:
                _key_press_start_time['d'] = now
                _key_processed_as_single['d'] = False
            elif not held_d:
                _key_press_start_time['d'] = None
                _key_processed_as_single['d'] = False
            
            # Handle 'A' key (decrease)
            if held_a and _key_press_start_time['a'] is not None:
                key_hold_duration = now - _key_press_start_time['a']
                
                if key_hold_duration < hold_start_delay and not _key_processed_as_single['a']:
                    # Process as single press (only once)
                    new_value = max(1, fmt_value - 1)
                    if new_value != fmt_value:
                        fmt_value = new_value
                        self.mw_fmt_slider.rating = fmt_value
                        _key_processed_as_single['a'] = True
                        print(f"🔍 DEBUG FMT - A single press: value changed to {fmt_value}")
                elif key_hold_duration >= hold_start_delay and now - _last_repeat_time >= key_repeat_interval:
                    # Process as continuous hold
                    new_value = max(1, fmt_value - 1)
                    if new_value != fmt_value:
                        fmt_value = new_value
                        self.mw_fmt_slider.rating = fmt_value
                        _last_repeat_time = now
                        print(f"🔍 DEBUG FMT - A hold: value changed to {fmt_value}")
            
            # Handle 'D' key (increase)
            if held_d and _key_press_start_time['d'] is not None:
                key_hold_duration = now - _key_press_start_time['d']
                
                if key_hold_duration < hold_start_delay and not _key_processed_as_single['d']:
                    # Process as single press (only once)
                    new_value = min(7, fmt_value + 1)
                    if new_value != fmt_value:
                        fmt_value = new_value
                        self.mw_fmt_slider.rating = fmt_value
                        _key_processed_as_single['d'] = True
                        print(f"🔍 DEBUG FMT - D single press: value changed to {fmt_value}")
                elif key_hold_duration >= hold_start_delay and now - _last_repeat_time >= key_repeat_interval:
                    # Process as continuous hold
                    new_value = min(7, fmt_value + 1)
                    if new_value != fmt_value:
                        fmt_value = new_value
                        self.mw_fmt_slider.rating = fmt_value
                        _last_repeat_time = now
                        print(f"🔍 DEBUG FMT - D hold: value changed to {fmt_value}")
            
            # Handle ENTER and ESCAPE keys
            keys = event.getKeys()
            break_main_loop = False
            if keys:
                print(f"🔍 DEBUG FMT - Keys pressed: {keys}")
                for key in keys:
                    if key == 'escape':
                        print("🔍 DEBUG FMT - ESCAPE key detected, quitting...")
                        core.quit()
                    elif key == 'return':
                        print(f"🔍 DEBUG FMT - ENTER key pressed, confirming rating: {fmt_value}")
                        print("🔍 DEBUG FMT - Breaking from FMT loop...")
                        break_main_loop = True
                        break
            
            # Break out of main loop if ENTER was pressed
            if break_main_loop:
                break
            
            # Also update based on direct slider movement (after keyboard input)
            slider_val = self.mw_fmt_slider.getRating()
            if slider_val is not None:
                fmt_value = int(slider_val)
            
            # Update instruction with current label only (no number)
            current_label = scale_labels[fmt_value - 1]  # Convert to 0-based index
            self.instruction_text.text = instruction_text.format(config.MW_PROBES['fmt'], current_label)
            
            # Temporarily move text higher to avoid overlap with slider
            original_pos = self.instruction_text.pos
            self.instruction_text.pos = (0, 150)  # Move to top center of screen
            self.instruction_text.alignText = 'center'
            self.instruction_text.anchorHoriz = 'center'
            
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
            
            # Restore original text position and alignment for other parts of experiment
            self.instruction_text.pos = original_pos
            self.instruction_text.alignText = 'left'
            self.instruction_text.anchorHoriz = 'left'
        
        fmt_rating = fmt_value
        
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
                    self.play_video('positive_clip1', 'film_positive_clip1', collect_rating=True)
                else:
                    self.play_video('positive_clip2', 'film_positive_clip2', collect_rating=True)
            else:  # negative
                # Use specific negative clips based on phase
                if phase_number == 1 or phase_number == 3:
                    self.play_video('negative_clip', 'film_general', collect_rating=True)  # Phase 1 and 3 use negative_clip
                else:
                    self.play_video('negative_clip2', 'film_general', collect_rating=True)  # Phase 2 and 4 use negative_clip2
        
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
        keys = event.waitKeys()
        if keys and 'escape' in keys:
            core.quit()
    
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
            self.collect_mood_rating_arrow_keys('baseline')
            
            # Step 2: Mood Induction 1
            print(f"\n📍 STEP 2 - Mood Induction 1")
            induction_1 = order['mood_inductions'][0]
            self.run_mood_induction(induction_1[0], induction_1[1], 1)
            # Only collect mood scale if not Velten (Velten collects it at the end of procedure)
            if induction_1[0] != 'V':
                print(f"\n📍 STEP 3 - Post-Induction Mood Scale")
                self.collect_mood_rating_arrow_keys('post_induction_1')
            else:
                print(f"📍 STEP 3 - Mood scale already collected at end of Velten procedure")
            
            # Step 4: SART 1
            print(f"\n📍 STEP 4 - SART Block 1 ({order['sart_conditions'][0]})")
            self.run_sart_block(order['sart_conditions'][0], 1)
            print(f"✅ SART Block 1 completed - moving to next phase")
            
            # Step 5: Pre-induction mood scale for re-induction
            print(f"\n📍 STEP 5 - Pre-Induction Mood Scale (before re-induction)")
            self.collect_mood_rating_arrow_keys('pre_induction_2')
            
            # Step 6: Mood Induction 2 (re-induction)
            print(f"\n📍 STEP 6 - Mood Induction 2 (Re-induction)")
            induction_2 = order['mood_inductions'][1]
            self.run_mood_induction(induction_2[0], induction_2[1], 2)
            # Only collect mood scale if not Velten (Velten collects it at the end of procedure)
            if induction_2[0] != 'V':
                print(f"\n📍 STEP 7 - Post-Induction Mood Scale")
                self.collect_mood_rating_arrow_keys('post_induction_2')
            else:
                print(f"📍 STEP 7 - Mood scale already collected at end of Velten procedure")
            
            # Step 8: SART 2
            print(f"\n📍 STEP 8 - SART Block 2 ({order['sart_conditions'][1]})")
            self.run_sart_block(order['sart_conditions'][1], 2)
            print(f"✅ SART Block 2 completed - moving to neutral washout")
            
            # Step 9: Neutral Washout
            print(f"\n📍 STEP 9 - Neutral Washout")
            self.run_neutral_washout()
            print(f"\n📍 STEP 10 - Post-Washout Mood Scale")
            self.collect_mood_rating_arrow_keys('post_washout')
            
            # Step 11: Mood Induction 3
            print(f"\n📍 STEP 11 - Mood Induction 3")
            induction_3 = order['mood_inductions'][2]
            self.run_mood_induction(induction_3[0], induction_3[1], 3)
            # Only collect mood scale if not Velten (Velten collects it at the end of procedure)
            if induction_3[0] != 'V':
                print(f"\n📍 STEP 12 - Post-Induction Mood Scale")
                self.collect_mood_rating_arrow_keys('post_induction_3')
            else:
                print(f"📍 STEP 12 - Mood scale already collected at end of Velten procedure")
            
            # Step 13: SART 3
            print(f"\n📍 STEP 13 - SART Block 3 ({order['sart_conditions'][2]})")
            self.run_sart_block(order['sart_conditions'][2], 3)
            print(f"✅ SART Block 3 completed - moving to final phase")
            
            # Step 14: Pre-induction mood scale for second re-induction
            print(f"\n📍 STEP 14 - Pre-Induction Mood Scale (before second re-induction)")
            self.collect_mood_rating_arrow_keys('pre_induction_4')
            
            # Step 15: Mood Induction 4
            print(f"\n📍 STEP 15 - Mood Induction 4")
            induction_4 = order['mood_inductions'][3]
            self.run_mood_induction(induction_4[0], induction_4[1], 4)
            # Only collect mood scale if not Velten (Velten collects it at the end of procedure)
            if induction_4[0] != 'V':
                print(f"\n📍 STEP 16 - Post-Induction Mood Scale")
                self.collect_mood_rating_arrow_keys('post_induction_4')
            else:
                print(f"📍 STEP 16 - Mood scale already collected at end of Velten procedure")
            
            # Step 17: SART 4
            print(f"\n📍 STEP 17 - SART Block 4 ({order['sart_conditions'][3]})")
            self.run_sart_block(order['sart_conditions'][3], 4)
            print(f"✅ SART Block 4 completed")
            
            # Step 18: Mood Repair (if applicable)
            if order['mood_repair']:
                print(f"\n📍 STEP 18 - Mood Repair (Required for Order {condition})")
                self.run_mood_repair()
                print(f"\n📍 STEP 19 - Final Mood Scale")
                self.collect_mood_rating_arrow_keys('post_repair')
            else:
                print(f"\n📍 No Mood Repair needed for Order {condition} (ends with positive induction)")
            
            # Final debrief
            print(f"\n📍 FINAL STEP - Debrief")
            self.show_instruction('debrief')
            
            total_steps = 19 if order['mood_repair'] else 17
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