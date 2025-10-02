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
                # Get configured display size for video scaling
                import config
                if hasattr(config, 'LAYOUT_CONFIG') and config.LAYOUT_CONFIG and 'size' in config.LAYOUT_CONFIG:
                    # Use the configured display size, NOT the actual window size
                    display_size = config.LAYOUT_CONFIG['size']
                    print(f"🔍 DEBUG - Video Preloader Sizing:")
                    print(f"   Configured display size: {display_size[0]}x{display_size[1]}")
                    print(f"   Actual window size: {self.win.size if hasattr(self.win, 'size') else 'unknown'}")
                else:
                    # Fallback to window size if no layout config
                    display_size = self.win.size if hasattr(self.win, 'size') else [1920, 1080]
                    print(f"🔍 DEBUG - Video Preloader Sizing (fallback):")
                    print(f"   Using window size: {display_size[0]}x{display_size[1]}")
                
                print(f"   Display aspect ratio: {display_size[0]/display_size[1]:.2f}")
                
                # Use None for size to maintain aspect ratio and fit within display
                # This prevents zooming/cropping and shows full video content
                video_size = None  # Let PsychoPy auto-scale to fit
                print(f"📺 Setting video to auto-scale within display: {display_size[0]}x{display_size[1]}")
                print(f"   Note: Video will maintain aspect ratio and fit within display")
                
                # Try different video components based on availability
                try:
                    video = visual.MovieStim3(
                        win=self.win,
                        filename=str(video_path),
                        size=video_size,  # None = auto-scale to fit, maintain aspect ratio
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
                            size=video_size,  # None = auto-scale to fit, maintain aspect ratio
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
                
                # DEBUG: Print actual video dimensions after loading
                if video:
                    try:
                        print(f"✓ {video_key}")
                        print(f"   Actual video dimensions: {video.size}")
                        print(f"   Video position: {video.pos}")
                    except:
                        print(f"✓ {video_key} (dimensions not available)")
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