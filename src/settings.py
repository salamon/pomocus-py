"""
Settings management for Pomocus
Handles persistent storage of user preferences including theme colors
"""

from typing import Dict
from pathlib import Path
import json


class SettingsManager:
    """Manages persistent settings storage including theme colors"""
    
    # Default timer durations
    DEFAULT_WORK = 25
    DEFAULT_SHORT_BREAK = 5
    DEFAULT_LONG_BREAK = 15
    DEFAULT_LONG_BREAK_INTERVAL = 4
    DEFAULT_SOUND_ENABLED = True
    DEFAULT_AUTO_START = False
    DEFAULT_THEME_MODE = 'dark'
    
    THEMES = {
        'dark': {
            'work': '#FF6B6B',
            'short_break': '#4ECDC4',
            'long_break': '#45B7D1',
            'bg_primary': '#1A1A2E',
            'button_bg': '#30475E',
            'modal_bg': '#16213E',
            'modal_border': '#4ECDC4',
            'text_primary': '#FFFFFF',
            'text_secondary': '#B8C5D6',
            'text_muted': '#94A3B8',
            'progress_bg': '#2d3748',
            'timer_bg': '#16213E',
            'success': '#10B981',
            'error': '#DC3545',
            'warning': '#F59E0B'
        },
        'light': {
            'work': '#FF6B6B',
            'short_break': '#4ECDC4',
            'long_break': '#45B7D1',
            'bg_primary': '#F8F9FA',
            'button_bg': '#E9ECEF',
            'modal_bg': '#FFFFFF',
            'modal_border': '#4ECDC4',
            'text_primary': '#212529',
            'text_secondary': '#495057',
            'text_muted': '#6C757D',
            'progress_bg': '#DEE2E6',
            'timer_bg': '#FFFFFF',
            'success': '#198754',
            'error': '#DC3545',
            'warning': '#FFC107'
        }
    }
    
    def __init__(self, settings_file: str = "pomocus_settings.json"):
        self.settings_file = Path(settings_file)
        self.settings = self._load_settings()

    def _sanitize_settings(self, settings: Dict) -> Dict:
        """Validate and clamp settings loaded from disk."""
        defaults = self._get_defaults()

        def _clamp_int(value, min_value: int, max_value: int, fallback: int) -> int:
            try:
                ivalue = int(value)
            except (TypeError, ValueError):
                return fallback
            return max(min_value, min(max_value, ivalue))

        sanitized = dict(defaults)
        sanitized['work_duration'] = _clamp_int(settings.get('work_duration'), 1, 90, defaults['work_duration'])
        sanitized['short_break_duration'] = _clamp_int(settings.get('short_break_duration'), 1, 30, defaults['short_break_duration'])
        sanitized['long_break_duration'] = _clamp_int(settings.get('long_break_duration'), 1, 60, defaults['long_break_duration'])
        sanitized['long_break_interval'] = _clamp_int(settings.get('long_break_interval'), 1, 10, defaults['long_break_interval'])

        sanitized['auto_start'] = bool(settings.get('auto_start', defaults['auto_start']))
        sanitized['enable_sound'] = bool(settings.get('enable_sound', defaults['enable_sound']))

        theme_mode = settings.get('theme_mode', defaults['theme_mode'])
        sanitized['theme_mode'] = theme_mode if theme_mode in self.THEMES else defaults['theme_mode']

        return sanitized
    
    def _load_settings(self) -> Dict:
        """Load settings from file or return defaults"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    defaults = self._get_defaults()
                    defaults.update(loaded)
                    return self._sanitize_settings(defaults)
            except (json.JSONDecodeError, IOError):
                return self._get_defaults()
        return self._get_defaults()
    
    def _get_defaults(self) -> Dict:
        """Get default settings including theme"""
        return {
            'work_duration': self.DEFAULT_WORK,
            'short_break_duration': self.DEFAULT_SHORT_BREAK,
            'long_break_duration': self.DEFAULT_LONG_BREAK,
            'long_break_interval': self.DEFAULT_LONG_BREAK_INTERVAL,
            'auto_start': self.DEFAULT_AUTO_START,
            'theme_mode': self.DEFAULT_THEME_MODE,
            'enable_sound': self.DEFAULT_SOUND_ENABLED
        }
    
    def save_settings(self, work_min: int, short_min: int, long_min: int, long_break_interval: int, auto_start: bool, enable_sound: bool = True):
        """Save settings to file"""
        self.settings['work_duration'] = work_min
        self.settings['short_break_duration'] = short_min
        self.settings['long_break_duration'] = long_min
        self.settings['long_break_interval'] = long_break_interval
        self.settings['auto_start'] = auto_start
        self.settings['enable_sound'] = enable_sound
        # theme_mode is saved separately usually, but here in same file
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except IOError as e:
            print(f"Error saving settings: {e}")
    
    def get_work_duration(self) -> int:
        """Get work duration in minutes"""
        return self.settings.get('work_duration', self.DEFAULT_WORK)
    
    def get_short_break_duration(self) -> int:
        """Get short break duration in minutes"""
        return self.settings.get('short_break_duration', self.DEFAULT_SHORT_BREAK)
    
    def get_long_break_duration(self) -> int:
        """Get long break duration in minutes"""
        return self.settings.get('long_break_duration', self.DEFAULT_LONG_BREAK)
    
    def get_long_break_interval(self) -> int:
        """Get number of work sessions before a long break"""
        return self.settings.get('long_break_interval', self.DEFAULT_LONG_BREAK_INTERVAL)
    
    def get_auto_start(self) -> bool:
        """Get whether auto-start is enabled"""
        return self.settings.get('auto_start', self.DEFAULT_AUTO_START)
    
    def get_sound_enabled(self) -> bool:
        """Get whether sound is enabled"""
        return self.settings.get('enable_sound', self.DEFAULT_SOUND_ENABLED)
    
    def get_theme_mode(self) -> str:
        return self.settings.get('theme_mode', self.DEFAULT_THEME_MODE)
    
    def get_theme(self) -> Dict[str, str]:
        """Get current theme colors"""
        mode = self.get_theme_mode()
        return self.THEMES.get(mode, self.THEMES['dark'])
    
    def toggle_theme(self):
        """Switch theme mode and save"""
        current = self.get_theme_mode()
        new_mode = 'light' if current == 'dark' else 'dark'
        self.settings['theme_mode'] = new_mode
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except IOError as e:
            print(f"Error saving settings: {e}")
        return self.get_theme()
    
    def reset_to_defaults(self):
        """Reset settings to defaults"""
        self.settings = self._get_defaults()
        self.save_settings(
            self.DEFAULT_WORK, 
            self.DEFAULT_SHORT_BREAK, 
            self.DEFAULT_LONG_BREAK,
            self.DEFAULT_LONG_BREAK_INTERVAL,
            self.DEFAULT_AUTO_START,
            self.DEFAULT_SOUND_ENABLED
        )

