"""
Pomocus - A Beautiful Pomodoro Timer for Windows
Main application with core logic
"""

import os
import sys
import tkinter as tk
from typing import Callable, Optional

from settings import SettingsManager
from ui import PomocusUI


class PomodoroLogic:
    """Core Pomodoro timer logic"""
    
    def __init__(self, work_min: int = 25, short_break_min: int = 5, long_break_min: int = 15, long_break_interval: int = 4, auto_start: bool = False):
        self.work_duration = work_min
        self.short_break_duration = short_break_min
        self.long_break_duration = long_break_min
        self.long_break_interval = long_break_interval
        self.auto_start = auto_start
        
        self.time_left = self.work_duration * 60
        self.total_time = self.work_duration * 60
        self.is_running = False
        self.timer_mode = 'work'
        self.pomodoros_completed = 0
        
        # Callbacks
        self.on_tick: Optional[Callable] = None
        self.on_complete: Optional[Callable] = None
        self.on_mode_change: Optional[Callable] = None
    
    def start(self):
        """Start the timer"""
        self.is_running = True
    
    def pause(self):
        """Pause the timer"""
        self.is_running = False
    
    def reset(self):
        """Reset timer to current mode's duration"""
        self.is_running = False
        if self.timer_mode == 'work':
            self.time_left = self.work_duration * 60
            self.total_time = self.work_duration * 60
        elif self.timer_mode == 'short_break':
            self.time_left = self.short_break_duration * 60
            self.total_time = self.short_break_duration * 60
        else:
            self.time_left = self.long_break_duration * 60
            self.total_time = self.long_break_duration * 60
            
    def reset_flow(self):
        """Reset entire flow (rounds and timer)"""
        self.pomodoros_completed = 0
        self.is_running = False
        self.switch_mode('work')

    def skip(self):
        """Skip to next phase"""
        self.is_running = False
        self.time_left = 0
        self.complete()
    
    def tick(self):
        """Decrement timer by one second"""
        if self.is_running and self.time_left > 0:
            self.time_left -= 1
            if self.on_tick:
                self.on_tick()
            return True
        elif self.is_running and self.time_left == 0:
            self.complete()
            return False
        return False
    
    def complete(self):
        """Handle timer completion"""
        self.is_running = False
        
        completed_mode = self.timer_mode
        
        if self.timer_mode == 'work':
            self.pomodoros_completed += 1
            next_mode = 'long_break' if self.pomodoros_completed % self.long_break_interval == 0 else 'short_break'
            self.switch_mode(next_mode)
        else:
            self.switch_mode('work')
        
        if self.on_complete:
            self.on_complete(completed_mode)

        # Auto start next timer
        if self.auto_start:
            self.start()
    
    def switch_mode(self, mode: str):
        """Switch timer mode"""
        self.timer_mode = mode
        
        if mode == 'work':
            self.time_left = self.work_duration * 60
            self.total_time = self.work_duration * 60
        elif mode == 'short_break':
            self.time_left = self.short_break_duration * 60
            self.total_time = self.short_break_duration * 60
        else:
            self.time_left = self.long_break_duration * 60
            self.total_time = self.long_break_duration * 60
        
        if self.on_mode_change:
            self.on_mode_change(mode)
    
    def update_durations(self, work_min: int, short_min: int, long_min: int, interval: int = 4, auto_start: bool = False):
        """Update timer durations and reset flow"""
        self.work_duration = work_min
        self.short_break_duration = short_min
        self.long_break_duration = long_min
        self.long_break_interval = interval
        self.auto_start = auto_start

        # reset app flow
        self.pomodoros_completed = 0
        self.is_running = False
        self.switch_mode('work')
    
    def get_progress(self) -> float:
        """Get progress as a ratio (0.0 to 1.0)"""
        if self.total_time > 0:
            return (self.total_time - self.time_left) / self.total_time
        return 0.0
    
    def get_time_display(self) -> str:
        """Get formatted time string"""
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_progress_dots(self) -> str:
        """Get progress dots string"""
        interval = self.long_break_interval
        completed = self.pomodoros_completed % interval
        return "● " * completed + "○ " * (interval - completed)


def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Set window icon
    try:
        # Try platform-specific icon formats
        if sys.platform == 'darwin':  # macOS
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon.icns')
        else:  # Windows and Linux
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon.ico')
        
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception:
        # Fallback: continue without icon if there's any issue
        pass
    
    # Load settings
    settings_manager = SettingsManager()
    
    # Create logic with saved settings
    logic = PomodoroLogic(
        work_min=settings_manager.get_work_duration(),
        short_break_min=settings_manager.get_short_break_duration(),
        long_break_min=settings_manager.get_long_break_duration(),
        long_break_interval=settings_manager.get_long_break_interval(),
        auto_start=settings_manager.get_auto_start()
    )
    
    # Create UI and pass settings manager
    ui = PomocusUI(root, logic, settings_manager)
    root.mainloop()


if __name__ == "__main__":
    main()
