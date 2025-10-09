"""
Experiment Configuration for PsychoPy Mood Induction + SART Study
"""

import os
import sys
from pathlib import Path

# ===== DEMO MODE SETTINGS =====
# Set to True for shortened experiment (10 trials per SART block, 3 Velten statements)
DEMO_MODE = False

# ===== PLATFORM-SPECIFIC SETTINGS =====
IS_MAC = sys.platform == 'darwin'
IS_WINDOWS = sys.platform == 'win32'
IS_LINUX = sys.platform == 'linux'

# Base paths with debugging and fallback
BASE_DIR = Path(__file__).parent.parent
print(f"🔍 Path debugging:")
print(f"   __file__: {__file__}")
print(f"   BASE_DIR calculated: {BASE_DIR}")
print(f"   BASE_DIR absolute: {BASE_DIR.resolve()}")
print(f"   BASE_DIR exists: {BASE_DIR.exists()}")

# Fallback path resolution if BASE_DIR doesn't exist
if not BASE_DIR.exists():
    # Try current working directory
    import os
    cwd_base = Path(os.getcwd())
    print(f"   Trying CWD: {cwd_base}")
    if cwd_base.exists() and (cwd_base / "stimuli").exists():
        BASE_DIR = cwd_base
        print(f"   ✅ Using CWD as BASE_DIR: {BASE_DIR}")
    else:
        print(f"   ❌ CWD fallback failed")

STIMULI_DIR = BASE_DIR / "stimuli"
SCRIPTS_DIR = BASE_DIR / "scripts"

# OneDrive detection and data directory setup
def detect_onedrive_path():
    """Detect OneDrive directory for data storage"""
    import os
    username = os.getenv('USERNAME', os.getenv('USER', ''))
    
    # Common OneDrive paths on Windows
    potential_onedrive_paths = [
        Path.home() / 'OneDrive',
        Path(f'C:/Users/{username}/OneDrive') if username else None,
    ]
    
    # Filter out None values and check which paths exist
    for path in potential_onedrive_paths:
        if path and path.exists() and path.is_dir():
            return path
    
    return None

# Try to use OneDrive, fall back to local directory
onedrive_path = detect_onedrive_path()
if onedrive_path:
    DATA_DIR = onedrive_path / "PsychoPy_Data"
    print(f"📁 OneDrive detected: Using {DATA_DIR} for data storage")
    # Create the directory if it doesn't exist
    DATA_DIR.mkdir(exist_ok=True)
else:
    DATA_DIR = BASE_DIR / "data"
    print(f"📁 OneDrive not found: Using local directory {DATA_DIR}")

print(f"   DATA_DIR: {DATA_DIR}")
print(f"   DATA_DIR exists: {DATA_DIR.exists()}")

print(f"   STIMULI_DIR: {STIMULI_DIR}")
print(f"   STIMULI_DIR exists: {STIMULI_DIR.exists()}")
if STIMULI_DIR.exists():
    print(f"   Videos dir exists: {(STIMULI_DIR / 'videos').exists()}")
    print(f"   Audio dir exists: {(STIMULI_DIR / 'audio').exists()}")
print()

# Stimulus file paths
VIDEO_DIR = STIMULI_DIR / "videos"
AUDIO_DIR = STIMULI_DIR / "audio"
VELTEN_DIR = STIMULI_DIR / "velten_statements"

# UPDATED: Video files (actual files provided)
VIDEO_FILES = {
    'positive_clip1': VIDEO_DIR / 'positive_clip.mp4',      # Life is Beautiful scene
    'positive_clip2': VIDEO_DIR / 'positive_clip2.mp4',    # Forrest Gump scene
    'negative_clip': VIDEO_DIR / 'negative_clip.mp4',      # Primary negative clip
    'negative_clip2': VIDEO_DIR / 'negative_clip2.mp4',    # Secondary negative clip
    'neutral_clip': VIDEO_DIR / 'neutral_clip.mp4',        # Neutral washout clip
    'mood_repair': VIDEO_DIR / 'repair_clip.mp4',          # Primary mood repair clip
    'mood_repair_animal': VIDEO_DIR / 'repair_clip_animal.mp4'  # Alternative repair clip
}

# Audio files for Velten statements
AUDIO_FILES = {
    'positive_music': AUDIO_DIR / 'positive_music.wav',
    'negative_music': AUDIO_DIR / 'negative_music.wav'
}

# Velten statement files
VELTEN_FILES = {
    'positive': VELTEN_DIR / 'positive_statements.txt',
    'negative': VELTEN_DIR / 'negative_statements.txt'
}

# UPDATED: Velten Mood Induction Statements (from provided document)
# Two distinct sets for initial induction and re-induction to reduce repetition
VELTEN_STATEMENTS = {
    'positive_set_a': [
        "Where I am in life right now makes my dreams feel more possible.",
        "The world is full of opportunity and I'm taking advantage of it.",
        "I know if I try I can make things turn out fine.",
        "I bet things will go well for the rest of the day.",
        "When I have the right attitude, nothing can depress me.",
        "Most people like me.",
        "I've got some good friends.",
        "I can make things happen.",
        "My parents are proud of me.",
        "I know I can get the things I want in life.",
        "Good things are waiting for me in the future.",
        "I feel creative.",
        "I feel too good to be brought down right now.",
        "Things are going so well for me.",
        "The relationships I have now are the best I've ever had.",
        "It doesn't get any better than this.",
        "I can make any situation turn out right.",
        "I feel completely aware.",
        "I'm in charge of my life and I like it that way.",
        "Life feels amazing — I can't remember when I felt so good.",
        "Everything's falling into place for me.",
        "I'm proud of who I am.",
        "I know I can do it; I'm going to seize the day!",
        "I'm energized.",
        "It's great to be alive!"
    ],
    'positive_set_b': [
        "Where I am in life right now makes my dreams feel more possible.",
        "The world is full of opportunity and I'm taking advantage of it.",
        "I know if I try I can make things turn out fine.",
        "I bet things will go well for the rest of the day.",
        "When I have the right attitude, nothing can depress me.",
        "Most people like me.",
        "I've got some good friends.",
        "I can make things happen.",
        "My parents are proud of me.",
        "I know I can get the things I want in life.",
        "Good things are waiting for me in the future.",
        "I feel creative.",
        "I feel too good to be brought down right now.",
        "Things are going so well for me.",
        "The relationships I have now are the best I've ever had.",
        "It doesn't get any better than this.",
        "I can make any situation turn out right.",
        "I feel completely aware.",
        "I'm in charge of my life and I like it that way.",
        "Life feels amazing — I can't remember when I felt so good.",
        "Everything's falling into place for me.",
        "I'm proud of who I am.",
        "I know I can do it; I'm going to seize the day!",
        "I'm energized.",
        "It's great to be alive!"
    ],
    'negative_set_a': [
        "I feel a little down today.",
        "Things are harder than I expected.",
        "Everyone else seems to be having more fun.",
        "Sometimes I feel so guilty that I can't sleep.",
        "I wish I could be myself, but nobody likes me when I am.",
        "Today is one of those days when everything I do is wrong.",
        "I doubt that I'll ever make a contribution in the world.",
        "I feel like my life's in a rut that I'm never going to get out of.",
        "My mistakes haunt me, I've made too many.",
        "Life is such a heavy burden.",
        "I'm tired of trying.",
        "Even when I give my best effort, it just doesn't seem to be good enough.",
        "Nobody understands me or even tries to.",
        "I don't think things are ever going to get better.",
        "I feel worthless.",
        "What's the point of trying?",
        "The people close to me don't really understand me.",
        "When I talk no one really listens.",
        "I feel cheated by life.",
        "Why should I try when I can't make a difference anyway?",
        "Sometimes I feel really guilty about the way I've treated people close to me.",
        "Every time I turn around, something else has gone wrong.",
        "I'm completely alone.",
        "There is no hope.",
        "I feel I am being suffocated by the weight of my past mistakes."
    ],
    'negative_set_b': [
        "I feel a little down today.",
        "Things are harder than I expected.",
        "Everyone else seems to be having more fun.",
        "Sometimes I feel so guilty that I can't sleep.",
        "I wish I could be myself, but nobody likes me when I am.",
        "Today is one of those days when everything I do is wrong.",
        "I doubt that I'll ever make a contribution in the world.",
        "I feel like my life's in a rut that I'm never going to get out of.",
        "My mistakes haunt me, I've made too many.",
        "Life is such a heavy burden.",
        "I'm tired of trying.",
        "Even when I give my best effort, it just doesn't seem to be good enough.",
        "Nobody understands me or even tries to.",
        "I don't think things are ever going to get better.",
        "I feel worthless.",
        "What's the point of trying?",
        "The people close to me don't really understand me.",
        "When I talk no one really listens.",
        "I feel cheated by life.",
        "Why should I try when I can't make a difference anyway?",
        "Sometimes I feel really guilty about the way I've treated people close to me.",
        "Every time I turn around, something else has gone wrong.",
        "I'm completely alone.",
        "There is no hope.",
        "I feel I am being suffocated by the weight of my past mistakes."
    ]
}

# Velten statement usage mapping for counterbalancing
# Set A used during initial induction, Set B used during re-induction
VELTEN_SET_MAPPING = {
    'first_induction': {
        'positive': 'positive_set_a',
        'negative': 'negative_set_a'
    },
    're_induction': {
        'positive': 'positive_set_b',
        'negative': 'negative_set_b'
    }
}

# SART Task Parameters
SART_PARAMS = {
    'digits': list(range(10)),  # 0-9
    'target_digit': 3,  # No-go stimulus for inhibition condition
    'total_trials': 120,  # Total trials across all steps
    'steps_per_block': 8,  # 8 steps per SART block
    'trials_per_step_min': 13,  # Minimum trials per step
    'trials_per_step_max': 17,  # Maximum trials per step
    'stimulus_duration': 0.5,  # 500ms
    'isi_duration': 2.0,  # 2000ms inter-stimulus interval
    'max_response_time': 2.5,  # 2500ms - Response window covers full trial duration
    'response_keys': ['left', 'right']
}

# Screen dimensions and colors
SCREEN_PARAMS = {
    'size': [1920, 1080],       # High resolution for better video quality
    'fullscr': True,            # UPDATED: Enable fullscreen mode
    'color': [-1, -1, -1],      # Black background (PsychoPy uses -1 to 1 range)
    'units': 'pix',
    'allowGUI': True,           # ADDED: Allow GUI elements
    'winType': 'pyglet',        # ADDED: Specify window type for better compatibility
    # Mac-specific settings to reduce HID and timing issues
    'waitBlanking': IS_MAC,     # Enable VSync on Mac for better timing
    'useFBO': not IS_MAC,       # Disable FBO on Mac to avoid graphics issues
    'checkTiming': not IS_MAC,  # Disable strict timing checks on Mac
}

# Visual cue parameters
CONDITION_CUES = {
    'inhibition': {
        'color': [1, 1, 0],  # Yellow
        'pos': [-800, 450],  # Further top-left for fullscreen
        'radius': 50         # Larger radius for better visibility
    },
    'non_inhibition': {
        'color': [0, 0, 1],  # Blue
        'pos': [-800, 450],  # Further top-left for fullscreen
        'radius': 50         # Larger radius for better visibility
    }
}

# Cross-platform font selection
def get_system_font():
    """Get the best available system font for the current platform."""
    if IS_MAC:
        # Use system fonts that are guaranteed to exist on Mac
        return 'Helvetica'  # Use regular Helvetica on Mac (no Bold variant issues)
    elif IS_WINDOWS:
        return 'Arial'
    else:
        return 'DejaVu Sans'  # Linux fallback

def get_system_font_bold():
    """Get the best available bold system font for the current platform."""
    if IS_MAC:
        # Use Helvetica-Bold instead of 'Helvetica Bold' to avoid font warnings
        return 'Helvetica-Bold'  
    elif IS_WINDOWS:
        return 'Arial Bold'
    else:
        return 'DejaVu Sans Bold'  # Linux fallback

# Text styling - UPDATED: Moderately larger text for fullscreen readability
TEXT_STYLE = {
    'font': get_system_font(),
    'height': 38,          # Reduced from 48 to 38 for better balance
    'color': [1, 1, 1],    # White text (PsychoPy uses -1 to 1 range)
    'wrapWidth': 1200,     # Increased wrap width to work with -500 positioning
    'alignText': 'left',   # Keep left-align for instructions (as requested)
    'anchorHoriz': 'left'  # Keep left anchor for instructions (as requested)
}

# Velten text styling (centered) - UPDATED: Moderately larger text for fullscreen
VELTEN_TEXT_STYLE = {
    'font': get_system_font(),
    'height': 36,          # Reduced from 42 to 36 for better balance
    'color': [1, 1, 1],    # White text
    'wrapWidth': 900,      # Reduced wrap width for better balance
    'pos': (0, 0),         # Centered position
    'alignText': 'center',
    'anchorHoriz': 'center'
}

# Mood rating scale parameters (0-100 horizontal slider) - No midpoint
MOOD_SCALE = {
    'low': 0,
    'high': 100,
    'labels': ['Very Negative', 'Very Positive'],
    'tick_positions': [0, 100],
    'granularity': 1
}

# Counterbalancing orders (UPDATED: Consistent induction types with randomization)
# Four possible orders: Positive Velten → Negative Velten, Negative Velten → Positive Velten,
# Positive Video → Negative Video, Negative Video → Positive Video
COUNTERBALANCING_ORDERS = {
    1: {  # Order 1: Positive Velten → Negative Velten (ends with negative = mood repair)
        'sart_conditions': ['RI', 'NRI', 'RI', 'NRI'],
        'mood_inductions': [('V', '+'), ('V', '+'), ('V', '-'), ('V', '-')],
        'mood_repair': True  # Ends with negative, needs mood repair
    },
    2: {  # Order 2: Negative Velten → Positive Velten (ends with positive = no repair)
        'sart_conditions': ['RI', 'NRI', 'RI', 'NRI'],
        'mood_inductions': [('V', '-'), ('V', '-'), ('V', '+'), ('V', '+')],
        'mood_repair': False  # Ends with positive, no repair needed
    },
    3: {  # Order 3: Positive Video → Negative Video (ends with negative = mood repair)
        'sart_conditions': ['NRI', 'RI', 'NRI', 'RI'],
        'mood_inductions': [('M', '+'), ('M', '+'), ('M', '-'), ('M', '-')],
        'mood_repair': True  # Ends with negative, needs mood repair
    },
    4: {  # Order 4: Negative Video → Positive Video (ends with positive = no repair)
        'sart_conditions': ['NRI', 'RI', 'NRI', 'RI'],
        'mood_inductions': [('M', '-'), ('M', '-'), ('M', '+'), ('M', '+')],
        'mood_repair': False  # Ends with positive, no repair needed
    }
}

# UPDATED: Velten statement rating scale parameters (user-friendly 7-point Likert scale)
VELTEN_RATING_SCALE = {
    'scale_range': [1, 7],
    'scale_labels': ['Not at all', 'Slightly', 'Somewhat', 'Moderately', 'Quite a bit', 'Very much', 'Completely'],
    'tick_positions': [1, 2, 3, 4, 5, 6, 7],
    'granularity': 1,
    'question': "To what extent were you able to bring your mood in line with this statement?"
}

# Instructions text
INSTRUCTIONS = {
    'welcome': {
        'title': "Welcome to the study",
        'text': """Welcome to the study. Please enter the email address you provided when completing the consent form.

Press any key to continue."""
    },
    'overview': {
        'title': "Study Overview", 
        'text': """In this session, you will:
• read short statements while music plays,
• watch brief video clips designed to influence mood, and
• complete simple response tasks.

At times, we will also ask about your mood, your thoughts, and whether your mind is on or off task.

There are no right or wrong answers—please answer honestly about what you are experiencing in the moment.

Press any key to begin."""
    },
    'mood_rating': {
        'text': """Please rate your current mood by moving the slider to show how you feel right now."""
    },
    'film_general': {
        'text': """You will now watch a short film clip. Please watch the clip carefully and allow your mood to align with the emotions portrayed.

Press any key to begin the video."""
    },
    'film_positive_clip1': {
        'text': """In this scene from Life is Beautiful, a father and his young son are imprisoned in a Nazi concentration camp.
Throughout the film, the father has been protecting his son by pretending their situation is part of a game.
Here, he volunteers to "translate" the guard's words, turning them into playful rules to keep up the illusion.

Please watch the clip carefully and allow your mood to align with the emotions portrayed.
Press any key to begin the video."""
    },
    'film_positive_clip2': {
        'text': """In the next scene, Forrest learns for the first time that he has a son with Jenny. 
Please watch the clip carefully and allow your mood to align with the emotions portrayed.

Press any key to begin the video"""
    },
    'velten_intro': {
        'text': """You will now read a series of statements while listening to music. Each statement will appear on the screen for a short time. While it is displayed, focus on the words and try to bring your mood in line with what the statement says.

Press any key to begin"""
    },
    'velten_rating': {
        'text': """To what extent were you able to bring your mood in line with this statement? 1 = Not at all ... 7 = Completely"""
    },
    'sart_inhibition': {
        'text': """In this block, a number will appear to the LEFT or RIGHT of the + sign. Press the ARROW KEY that matches the side of the number. BUT: if the number is 3, do not press any key. The yellow circle in the top-left corner is a reminder of this rule."""
    },
    'sart_non_inhibition': {
        'text': """In this block, a number will appear to the LEFT or RIGHT of the + sign. Press the ARROW KEY that matches the side of the number. Respond to ALL digits, including 3. The blue circle in the top-left corner is a reminder of this rule."""
    },
    'neutral_washout': {
        'text': """In the next part, you will watch a neutral video clip. Please allow your mood to return to a neutral state as you watch. Afterward, the experiment will continue.

Press any key to begin."""
    },
    'mood_repair': {
        'text': """Some earlier parts of this study may have lowered your mood.
Before we finish, we'll show you a short uplifting video clip intended to bring your mood back toward neutral or positive.
To help us select the clip, please let us know:
Do you prefer a video that includes animals, or one without animals?

Response options:
1 - With animals
2 - Without animals  
3 - No preference"""
    },
    'debrief': {
        'text': """Thank you for participating!
Your responses have been recorded.

If you have any questions about the study, please contact:
Nate Speert, nate.speert@my.viu.ca

Press any key to end the session."""
    }
}

# Mind-wandering probe questions
MW_PROBES = {
    'tut': "To what extent were you thinking about something other than the task?",
    'fmt': "To what extent were your thoughts moving about freely?",
    'scale_labels': ['Not at all', 'Very much'],
    'scale_range': [1, 7]
}

# Timing parameters
TIMING = {
    'velten_statement_duration': 8.0,  # 8 seconds per statement
    'fixation_duration': 0.5,
    'feedback_duration': 1.0,
    'inter_trial_interval': 0.5,
    # Mac-specific timing adjustments
    'mac_frame_tolerance': 0.01 if IS_MAC else 0.005,  # More lenient frame timing on Mac
    'mac_refresh_rate': 60.0 if IS_MAC else None,      # Assume 60Hz on Mac
}

# Data collection parameters
DATA_PARAMS = {
    'participant_code_prefix': 'MOOD_SART_',
    'data_filename_template': 'participant_{code}_{timestamp}.csv',
    'backup_dir': DATA_DIR / 'backups'
} 