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
            print(f"🎬 Checking video: {video_key}")
            print(f"   Path: {video_path}")
            print(f"   Absolute path: {video_path.resolve()}")
            print(f"   Exists: {video_path.exists()}")
            
            if video_path.exists():
                file_size = video_path.stat().st_size / (1024*1024)  # Size in MB
                print(f"   Size: {file_size:.1f} MB")
                print(f"   Preloading {video_key}...")
                # Try different video components based on availability
                try:
                    video = visual.MovieStim3(
                        win=self.win,
                        filename=str(video_path),
                        size=(800, 600),
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
                            size=(800, 600),
                            pos=(0, 0),
                            noAudio=False,
                            loop=False,
                            autoStart=False
                        )
                    except (AttributeError, Exception) as e:
                        # Final fallback - skip video preloading but don't fail
                        print(f"Info: Skipping preload for {video_key} - will load on-demand")
                        print(f"Reason: {str(e)[:80]}...")
                        video = None
                self.preloaded_videos[video_key] = video
                print(f"Successfully preloaded {video_key}")
            else:
                print(f"   ❌ Video file not found: {video_path}")
                print(f"   Parent directory exists: {video_path.parent.exists()}")
                if video_path.parent.exists():
                    # List what files ARE in the directory
                    try:
                        files_in_dir = list(video_path.parent.glob("*"))
                        print(f"   Files in {video_path.parent.name}: {[f.name for f in files_in_dir]}")
                    except Exception as e:
                        print(f"   Could not list directory: {e}")
                self.preloaded_videos[video_key] = None
        except Exception as e:
            print(f"Error preloading {video_key}: {e}")
            self.preloaded_videos[video_key] = None
    
    def preload_all_videos(self):
        """Preload all experiment videos"""
        print("Starting video preloading...")
        
        for video_key, video_path in config.VIDEO_FILES.items():
            self.preload_video(video_key, video_path)
        
        print("Video preloading completed")
    
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
        height=30,
        color='white',
        pos=(0, 0)
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