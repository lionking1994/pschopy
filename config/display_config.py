"""
Display Configuration System for PsychoPy Experiment
Handles different screen sizes and resolutions with responsive layout
"""

import sys
import os

# Common display configurations
DISPLAY_CONFIGS = {
    'tiny': {
        'name': 'Tiny Display (1024x768)',
        'size': [1024, 768],
        'description': 'Old/small laptop, tablet landscape'
    },
    'small': {
        'name': 'Small Display (1366x768)',
        'size': [1366, 768],
        'description': 'Typical laptop screen'
    },
    'compact': {
        'name': 'Compact Display (1280x720)',
        'size': [1280, 720],
        'description': 'HD ready, compact laptop'
    },
    'standard': {
        'name': 'Standard Display (1440x900)',
        'size': [1440, 900],
        'description': 'Standard laptop/desktop'
    },
    'medium': {
        'name': 'Medium Display (1600x900)',
        'size': [1600, 900],
        'description': 'Medium laptop/desktop screen'
    },
    'wide': {
        'name': 'Wide Display (1680x1050)',
        'size': [1680, 1050],
        'description': 'Wide desktop monitor'
    },
    'large': {
        'name': 'Large Display (1920x1080)',
        'size': [1920, 1080],
        'description': 'Full HD desktop/laptop'
    },
    'tall': {
        'name': 'Tall Display (1920x1200)',
        'size': [1920, 1200],
        'description': 'Full HD with extra height'
    },
    'xlarge': {
        'name': 'Extra Large Display (2560x1440)',
        'size': [2560, 1440],
        'description': '1440p high-res display'
    },
    'ultrawide': {
        'name': 'Ultrawide Display (3440x1440)',
        'size': [3440, 1440],
        'description': '21:9 ultrawide monitor'
    },
    '4k': {
        'name': '4K Display (3840x2160)',
        'size': [3840, 2160],
        'description': '4K Ultra HD display'
    },
    'retina': {
        'name': 'Retina Display (2880x1800)',
        'size': [1440, 900],  # Use logical resolution for Retina displays (half of physical)
        'description': 'MacBook Pro Retina display',
        'is_retina': True,
        'physical_size': [2880, 1800]
    },
    'retina16': {
        'name': 'MacBook Pro 16" (3456x2234)',
        'size': [1728, 1117],  # Use logical resolution for Retina displays (half of physical)
        'description': 'MacBook Pro 16-inch Retina display',
        'is_retina': True,
        'physical_size': [3456, 2234]
    },
    'auto': {
        'name': 'Auto-detect Display Size',
        'size': None,  # Will be detected automatically
        'description': 'Automatically detect and adapt to screen size'
    }
}

def get_display_config(config_name='auto'):
    """Get display configuration by name"""
    if config_name not in DISPLAY_CONFIGS:
        print(f"⚠️  Unknown display config '{config_name}', using 'auto'")
        config_name = 'auto'
    
    return DISPLAY_CONFIGS[config_name]

def calculate_responsive_layout(screen_width, screen_height, is_retina=False):
    """Calculate responsive layout parameters based on screen dimensions
    
    For Retina displays, screen_width and screen_height should be the logical resolution,
    not the physical pixel resolution.
    """
    
    # Calculate text position (left-aligned but centered in screen)
    # Text should be left-aligned but the text block should be centered
    text_wrap = min(1400, int(screen_width * 0.7))  # 70% of screen width, max 1400
    
    # Calculate position to center the text block:
    # Left margin = (screen_width - text_wrap) / 2
    # Text position = -screen_width/2 + left_margin
    left_margin = (screen_width - text_wrap) // 2
    text_pos_x = -(screen_width // 2) + left_margin
    text_pos = (text_pos_x, 0)
    
    # Calculate SART cue position (top-left corner, but fully visible)
    # Use conservative positioning to ensure visibility on all displays
    cue_radius_temp = max(30, min(60, int(min(screen_width, screen_height) * 0.04)))
    
    # Position cue in top-left with generous margins
    # For 3456x2234: x from -1728 to +1728, y from -1117 to +1117
    margin_from_edge = max(100, int(min(screen_width, screen_height) * 0.1))  # 10% margin or 100px minimum
    
    cue_x = -(screen_width//2) + margin_from_edge + cue_radius_temp
    cue_y = (screen_height//2) - margin_from_edge - cue_radius_temp
    cue_pos = [cue_x, cue_y]
    
    # Calculate cue radius based on screen size
    cue_radius = max(30, min(60, int(min(screen_width, screen_height) * 0.04)))
    
    # Calculate responsive element sizes based on screen resolution
    # Base sizes are for 1920x1080, scale proportionally
    base_width, base_height = 1920, 1080
    width_scale = screen_width / base_width
    height_scale = screen_height / base_height
    scale_factor = min(width_scale, height_scale)  # Use smaller scale to maintain proportions
    
    # Text sizes (increased for better readability)
    text_height = max(30, int(46 * scale_factor))  # Min 30, scaled from base 46 (increased)
    velten_text_height = max(28, int(42 * scale_factor))  # Min 28, scaled from base 42 (increased)
    
    # Button sizes and positions
    button_width = max(200, int(260 * scale_factor))  # Min 200, scaled from base 260
    button_height = max(60, int(75 * scale_factor))   # Min 60, scaled from base 75
    button_text_height = max(24, int(38 * scale_factor))  # Min 24, scaled from base 38 (increased)
    
    # Button positions (responsive to screen height)
    mood_button_pos = max(-400, int(-300 * (screen_height / base_height)))  # Scale with screen height
    mw_button_pos = max(-300, int(-200 * (screen_height / base_height)))    # Scale with screen height
    
    # Slider sizes (mood slider increased for better visibility)
    mood_slider_width = max(450, int(650 * scale_factor))  # Min 450, scaled from base 650 (increased)
    mood_slider_height = max(35, int(55 * scale_factor))   # Min 35, scaled from base 55 (increased)
    
    velten_slider_width = max(450, int(650 * scale_factor))  # Min 450, scaled from base 650 (reduced)
    velten_slider_height = max(40, int(60 * scale_factor))   # Min 40, scaled from base 60 (reduced)
    
    mw_slider_width = max(500, int(750 * scale_factor))    # Min 500, scaled from base 750 (reduced)
    mw_slider_height = max(40, int(55 * scale_factor))     # Min 40, scaled from base 55 (reduced)
    
    # SART element sizes
    fixation_height = max(50, int(80 * scale_factor))      # Min 50, scaled from base 80
    digit_height = max(80, int(120 * scale_factor))        # Min 80, scaled from base 120
    
    return {
        'text_pos': text_pos,
        'cue_pos': cue_pos,
        'cue_radius': cue_radius,
        'text_wrap': text_wrap,
        'screen_size': [screen_width, screen_height],
        'scale_factor': scale_factor,
        # Text sizes
        'text_height': text_height,
        'velten_text_height': velten_text_height,
        # Button sizes and positions
        'button_width': button_width,
        'button_height': button_height,
        'button_text_height': button_text_height,
        'mood_button_pos': mood_button_pos,
        'mw_button_pos': mw_button_pos,
        # Slider sizes
        'mood_slider_width': mood_slider_width,
        'mood_slider_height': mood_slider_height,
        'velten_slider_width': velten_slider_width,
        'velten_slider_height': velten_slider_height,
        'mw_slider_width': mw_slider_width,
        'mw_slider_height': mw_slider_height,
        # SART element sizes
        'fixation_height': fixation_height,
        'digit_height': digit_height,
        # Responsive slider positions
        'mood_slider_pos': calculate_mood_slider_position(screen_height),
        'mw_slider_pos': calculate_mw_slider_position(screen_height),
        'velten_slider_pos': calculate_velten_slider_position(screen_height),
        # Video quality assessment
        'video_quality': get_video_quality_rating(screen_width, screen_height)
    }

def calculate_mood_slider_position(screen_height):
    """Calculate responsive mood slider position based on screen height"""
    # Base position is -200 for 1080p, scale proportionally
    base_height = 1080
    base_position = -200
    
    # Scale position based on screen height, but keep reasonable bounds
    scaled_position = int(base_position * (screen_height / base_height))
    # Ensure slider doesn't go too high or too low
    return max(-300, min(-150, scaled_position))

def calculate_mw_slider_position(screen_height):
    """Calculate responsive mind-wandering slider position based on screen height"""
    # Base position is -200 for 1080p, scale proportionally
    base_height = 1080
    base_position = -200
    
    # Scale position based on screen height, but keep reasonable bounds
    scaled_position = int(base_position * (screen_height / base_height))
    # Ensure slider doesn't go too high or too low
    return max(-300, min(-150, scaled_position))

def calculate_velten_slider_position(screen_height):
    """Calculate responsive Velten slider position based on screen height"""
    # Base position is -380 for 1080p, scale proportionally
    base_height = 1080
    base_position = -380
    
    # Scale position based on screen height, but keep reasonable bounds
    scaled_position = int(base_position * (screen_height / base_height))
    # Ensure slider doesn't go too low
    return max(-450, min(-250, scaled_position))

def get_video_quality_rating(screen_width, screen_height):
    """Assess expected video quality for the given screen size"""
    total_pixels = screen_width * screen_height
    
    if total_pixels >= 8294400:  # 4K (3840x2160) and above
        return {
            'rating': 'Excellent',
            'description': 'Ultra-high resolution - videos will look crisp and detailed',
            'recommendation': 'Perfect for high-quality video content'
        }
    elif total_pixels >= 3686400:  # 1440p (2560x1440) and above
        return {
            'rating': 'Very Good',
            'description': 'High resolution - videos will look sharp and clear',
            'recommendation': 'Excellent video quality with good detail'
        }
    elif total_pixels >= 2073600:  # 1080p (1920x1080) and above
        return {
            'rating': 'Good',
            'description': 'Full HD resolution - videos will look clear',
            'recommendation': 'Good video quality suitable for experiments'
        }
    elif total_pixels >= 1440000:  # 1600x900 and above
        return {
            'rating': 'Fair',
            'description': 'Medium resolution - videos may show some scaling',
            'recommendation': 'Acceptable for most experimental purposes'
        }
    elif total_pixels >= 1049088:  # 1366x768 and above
        return {
            'rating': 'Basic',
            'description': 'Standard resolution - videos will be scaled down',
            'recommendation': 'Basic quality, may affect fine visual details'
        }
    else:  # Below 1366x768
        return {
            'rating': 'Limited',
            'description': 'Low resolution - significant video scaling required',
            'recommendation': 'Consider using larger display for better video quality'
        }

def auto_detect_display():
    """Auto-detect the best display configuration"""
    try:
        import tkinter as tk
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        
        print(f"📱 Detected screen size: {screen_width}x{screen_height}")
        
        # Find the best matching preset
        if screen_width <= 1366:
            return 'small'
        elif screen_width <= 1600:
            return 'medium'
        elif screen_width <= 1920:
            return 'large'
        else:
            return 'xlarge'
            
    except Exception as e:
        print(f"⚠️  Could not auto-detect display: {e}")
        return 'large'  # Safe fallback

def get_layout_for_config(config_name):
    """Get complete layout configuration with automatic windowed/fullscreen detection"""
    config = get_display_config(config_name)
    
    # Check if this is a Retina display configuration
    is_retina = config.get('is_retina', False)
    
    # Get actual screen size for comparison
    try:
        import tkinter as tk
        root = tk.Tk()
        actual_width = root.winfo_screenwidth()
        actual_height = root.winfo_screenheight()
        root.destroy()
        print(f"🖥️  Actual screen size detected: {actual_width}x{actual_height}")
    except Exception as e:
        print(f"⚠️  Could not detect actual screen size: {e}")
        actual_width, actual_height = 1920, 1080  # Safe fallback
    
    if config_name == 'auto':
        # Auto-detect screen and calculate responsive layout
        # Check if this might be a Retina display (Mac with high resolution)
        import sys
        if sys.platform == 'darwin' and actual_width > 2500:
            # Likely a Retina display, use half resolution for logical pixels
            logical_width = actual_width // 2
            logical_height = actual_height // 2
            print(f"🍎 Retina display detected, using logical resolution: {logical_width}x{logical_height}")
            layout = calculate_responsive_layout(logical_width, logical_height, is_retina=True)
            config['size'] = [logical_width, logical_height]
        else:
            layout = calculate_responsive_layout(actual_width, actual_height)
            config['size'] = [actual_width, actual_height]
        
        config.update(layout)
        config['fullscr'] = True  # Auto mode uses fullscreen
        
    else:
        # For configured displays
        selected_width, selected_height = config['size']
        
        # For Retina displays, the size is already in logical pixels
        if is_retina:
            print(f"🍎 Using Retina display configuration with logical resolution: {selected_width}x{selected_height}")
            config['fullscr'] = True  # Retina displays should use fullscreen
        elif selected_width < actual_width or selected_height < actual_height:
            # Use windowed mode for smaller sizes
            config['fullscr'] = False
            print(f"📱 Using windowed mode: {selected_width}x{selected_height} < {actual_width}x{actual_height}")
        else:
            # Use fullscreen for equal or larger sizes
            config['fullscr'] = True
            print(f"🖥️  Using fullscreen mode: {selected_width}x{selected_height} >= {actual_width}x{actual_height}")
        
        # Calculate responsive sizes for preset configurations
        layout = calculate_responsive_layout(selected_width, selected_height, is_retina=is_retina)
        config.update(layout)
    
    return config

def print_available_configs():
    """Print all available display configurations"""
    print("\n🖥️  Available Display Configurations:")
    print("=" * 50)
    
    for key, config in DISPLAY_CONFIGS.items():
        size_str = f"{config['size'][0]}x{config['size'][1]}" if config['size'] else "Auto-detect"
        print(f"  {key:8} - {config['name']}")
        print(f"           Size: {size_str}")
        print(f"           {config['description']}")
        print()

if __name__ == "__main__":
    # Test the configuration system
    print_available_configs()
    
    # Test auto-detection
    auto_config = get_layout_for_config('auto')
    print(f"Auto-detected configuration:")
    print(f"  Screen size: {auto_config['size']}")
    print(f"  Text position: {auto_config['text_pos']}")
    print(f"  Cue position: {auto_config['cue_pos']}")
    print(f"  Cue radius: {auto_config['cue_radius']}")
    print(f"  Text wrap: {auto_config['text_wrap']}")
