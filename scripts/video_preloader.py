#!/usr/bin/env python3
"""
Video Preloader for PsychoPy Experiment
Addresses the known issue of video loading delays by preloading videos during intro screens.
"""

import sys
from pathlib import Path
from psychopy import visual, core
import threading
import queue

# Add config to path
sys.path.append(str(Path(__file__).parent.parent / 'config'))
import experiment_config as config

class VideoPreloader:
    """Preloads videos to reduce loading delays during experiment"""
    
    def __init__(self, win):
        """Initialize preloader with PsychoPy window"""
        self.win = win
        self.preloaded_videos = {}
        self.loading_queue = queue.Queue()
        self.loading_thread = None
        
    def preload_video(self, video_key, video_path):
        """Preload a single video"""
        try:
            if video_path.exists():
                # Get window size for aspect ratio calculation
                import config
                if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG and 'screen_size' in config.LAYOUT_CONFIG:
                    window_size = tuple(config.LAYOUT_CONFIG['screen_size'])
                    print(f"📺 Preloader window size: {window_size[0]}x{window_size[1]}")
                else:
                    window_size = self.win.size if hasattr(self.win, 'size') else (1920, 1080)
                    print(f"📺 Preloader window size: {window_size[0]}x{window_size[1]}")
                
                # Calculate video size to maintain aspect ratio
                # Use 90% of window size to ensure video fits with letterboxing
                video_width = int(window_size[0] * 0.9)
                video_height = int(window_size[1] * 0.9)
                
                # Maintain 16:9 aspect ratio (most common for videos)
                aspect_ratio = 16.0 / 9.0
                current_ratio = video_width / video_height
                
                if current_ratio > aspect_ratio:
                    # Window is wider than 16:9, fit to height
                    video_width = int(video_height * aspect_ratio)
                else:
                    # Window is taller than 16:9, fit to width
                    video_height = int(video_width / aspect_ratio)
                
                video_size = (video_width, video_height)
                print(f"📺 Video size with aspect ratio: {video_width}x{video_height}")
                
                # Try different video components based on availability
                try:
                    video = visual.MovieStim3(
                        win=self.win,
                        filename=str(video_path),
                        size=video_size,  # Use aspect-ratio-corrected size
                        pos=(0, 0),
                        noAudio=False,
                        loop=False,
                        autoStart=False
                    )
                except (AttributeError, Exception) as e:
                    # Fallback to MovieStim if MovieStim3 not available or fails
                    try:
                        video = visual.MovieStim(
                            win=self.win,
                            filename=str(video_path),
                            size=video_size,  # Use aspect-ratio-corrected size
                            pos=(0, 0),
                            noAudio=False,
                            loop=False,
                            autoStart=False
                        )
                    except (AttributeError, Exception) as e:
                        # Final fallback - skip video preloading but don't fail
                        print(f"⚠️ Could not preload {video_key} - will load on-demand")
                        video = None
                self.preloaded_videos[video_key] = video
                print(f"✓ {video_key}")
            else:
                print(f"❌ Video not found: {video_key}")
                self.preloaded_videos[video_key] = None
        except Exception as e:
            print(f"❌ Error preloading {video_key}: {e}")
            self.preloaded_videos[video_key] = None
    
    def preload_all_videos(self):
        """Preload all experiment videos"""
        print("🎬 Preloading videos...")
        
        for video_key, video_path in config.VIDEO_FILES.items():
            self.preload_video(video_key, video_path)
        
        print("✅ Video preloading completed")
    
    def preload_videos_background(self, video_keys):
        """Preload videos in background thread"""
        def background_loader():
            for video_key in video_keys:
                if video_key in config.VIDEO_FILES:
                    self.preload_video(video_key, config.VIDEO_FILES[video_key])
        
        self.loading_thread = threading.Thread(target=background_loader)
        self.loading_thread.daemon = True
        self.loading_thread.start()
    
    def get_preloaded_video(self, video_key):
        """Get a preloaded video"""
        return self.preloaded_videos.get(video_key, None)
    
    def wait_for_loading(self):
        """Wait for background loading to complete"""
        if self.loading_thread:
            self.loading_thread.join()
    
    def cleanup(self):
        """Clean up preloaded videos"""
        for video in self.preloaded_videos.values():
            if video:
                try:
                    video = None
                except:
                    pass
        self.preloaded_videos.clear()

def create_loading_screen(win, text="Loading videos, please wait..."):
    """Create a loading screen to show during video preloading"""
    loading_text = visual.TextStim(
        win=win,
        text=text,
        font='Arial',
        height=42,  # Increased from 30 to 42 for fullscreen visibility
        color='white',
        pos=(0, 0),
        wrapWidth=2000,  # Wide wrap width to keep loading messages on one line
        alignText='center',
        anchorHoriz='center'
    )
    
    # Show loading screen
    loading_text.draw()
    win.flip()
    
    return loading_text

def demo_preloader():
    """Demo function to test the preloader"""
    # Create window
    win = visual.Window(
        size=[800, 600],
        fullscr=False,
        color=[0, 0, 0],
        units='pix'
    )
    
    try:
        # Show loading screen
        loading_screen = create_loading_screen(win)
        
        # Create preloader
        preloader = VideoPreloader(win)
        
        # Preload videos
        preloader.preload_all_videos()
        
        # Show completion message
        loading_screen.text = "Loading complete! Press any key to exit."
        loading_screen.draw()
        win.flip()
        
        # Wait for key press
        from psychopy import event
        event.waitKeys()
        
    finally:
        preloader.cleanup()
        win.close()

if __name__ == '__main__':
    demo_preloader() 