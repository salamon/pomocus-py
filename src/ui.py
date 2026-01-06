"""
UI components for Pomocus
Contains all user interface classes and widgets
"""

import tkinter as tk
import sys
from typing import Callable, Optional, List

from settings import SettingsManager


class ToolTip:
    """Simple tooltip for widgets"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        self.x = self.y = 0
        
        self.widget.bind('<Enter>', self.show_tip)
        self.widget.bind('<Leave>', self.hide_tip)
        
    def show_tip(self, event=None):
        """Show value of tooltip"""
        self.schedule()
        
    def hide_tip(self, event=None):
        """Hide tooltip"""
        self.unschedule()
        self.hidetip()
        
    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.show)
        
    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)
            
    def show(self):
        """Display text in tooltip window"""
        if self.tip_window or not self.text:
            return
        
        # Calculate centering based on widget dimensions, not text insertion point
        # Fixes alignment issues and flickering
        x = self.widget.winfo_rootx() + (self.widget.winfo_width() // 2)
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        
        # Create label first to measure it
        label = tk.Label(tw, text=self.text, justify='left',
                       background="#ffffe0", relief='solid', borderwidth=1,
                       font=("tahoma", "10", "normal"))
        label.pack(ipadx=1)
        
        # Update to get dimensions
        tw.update_idletasks()
        width = tw.winfo_width()
        
        # Center x relative to widget center
        x -= (width // 2)
        
        tw.wm_geometry(f"+{x}+{y}")
        
    def hidetip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


class ModalOverlay:
    """In-app modal overlay for messages"""
    
    def __init__(self, parent: tk.Widget, title: str, message: str, color: str = '#FF6B6B'):
        self.overlay = tk.Frame(parent, bg='black')
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        modal = tk.Frame(self.overlay, bg='#16213E', highlightthickness=2, highlightbackground=color)
        modal.place(relx=0.5, rely=0.5, anchor='center')
        
        content = tk.Frame(modal, bg='#16213E')
        content.pack(padx=20, pady=20)
        
        tk.Label(content, text=title, font=('Segoe UI', 18, 'bold'), bg='#16213E', fg=color).pack(pady=(0, 15))
        tk.Label(content, text=message, font=('Segoe UI', 12), bg='#16213E', fg='white', justify='center').pack(pady=(0, 20))
        
        btn = tk.Button(content, text="OK", font=('Segoe UI', 12, 'bold'), bg=color, fg='white', command=self.close)
        btn.config(bd=2, relief='raised', padx=40, pady=12, cursor='hand2', highlightthickness=0)
        btn.pack()
        
        self.overlay.bind('<Button-1>', lambda e: self.close() if e.widget == self.overlay else None)
    
    def close(self):
        """Close the modal"""
        self.overlay.destroy()


class SettingsDialog:
    """Settings dialog for timer durations"""
    
    def __init__(self, parent: tk.Widget, work_min: int, short_min: int, long_min: int, long_interval: int, auto_start: bool, theme: dict = None, enable_sound: bool = True):
        self.result: Optional[tuple] = None
        
        # Use provided theme or defaults
        if theme is None:
            theme = SettingsManager.THEMES['dark']
        
        modal_bg = theme.get('modal_bg', '#16213E')
        modal_border = theme.get('modal_border', '#4ECDC4')
        text_muted = theme.get('text_muted', '#94A3B8')
        text_primary = theme.get('text_primary', '#FFFFFF')
        success = theme.get('success', '#10B981')
        error = theme.get('error', '#DC3545')
        button_bg = theme.get('button_bg', '#6C757D')
        
        self.overlay = tk.Frame(parent, bg='black')
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # ... modal creation code ...
        modal = tk.Frame(self.overlay, bg=modal_bg, highlightthickness=2, highlightbackground=modal_border)
        modal.place(relx=0.5, rely=0.5, anchor='center')
        
        content = tk.Frame(modal, bg=modal_bg)
        content.pack(padx=20, pady=20)
        
        tk.Label(content, text="Timer Settings", font=('Segoe UI', 18, 'bold'), bg=modal_bg, fg=modal_border).pack(pady=(0, 20))
        
        settings_frame = tk.Frame(content, bg=modal_bg)
        settings_frame.pack(pady=10)
        
        # Work duration
        tk.Label(settings_frame, text="Focus Duration (min)", font=('Segoe UI', 10, 'bold'), bg=modal_bg, fg=text_muted).grid(row=0, column=0, sticky='w', pady=(5,0))
        self.work_var = tk.IntVar(value=work_min)
        self.work_scale = tk.Scale(settings_frame, from_=1, to=90, orient='horizontal', variable=self.work_var, 
                                 length=200, bg=modal_bg, fg=text_primary, highlightthickness=0, bd=0, 
                                 troughcolor=button_bg, font=('Segoe UI', 9))
        self.work_scale.grid(row=1, column=0, pady=(0,10))
        
        # Short break
        tk.Label(settings_frame, text="Short Break (min)", font=('Segoe UI', 10, 'bold'), bg=modal_bg, fg=text_muted).grid(row=2, column=0, sticky='w', pady=(5,0))
        self.short_var = tk.IntVar(value=short_min)
        self.short_scale = tk.Scale(settings_frame, from_=1, to=30, orient='horizontal', variable=self.short_var, 
                                  length=200, bg=modal_bg, fg=text_primary, highlightthickness=0, bd=0, 
                                  troughcolor=button_bg, font=('Segoe UI', 9))
        self.short_scale.grid(row=3, column=0, pady=(0,10))
        
        # Long break
        tk.Label(settings_frame, text="Long Break (min)", font=('Segoe UI', 10, 'bold'), bg=modal_bg, fg=text_muted).grid(row=4, column=0, sticky='w', pady=(5,0))
        self.long_var = tk.IntVar(value=long_min)
        self.long_scale = tk.Scale(settings_frame, from_=1, to=60, orient='horizontal', variable=self.long_var, 
                                 length=200, bg=modal_bg, fg=text_primary, highlightthickness=0, bd=0, 
                                 troughcolor=button_bg, font=('Segoe UI', 9))
        self.long_scale.grid(row=5, column=0, pady=(0,10))
        
        # Long Break Interval
        tk.Label(settings_frame, text="Rounds (Long Break after..)", font=('Segoe UI', 10, 'bold'), bg=modal_bg, fg=text_muted).grid(row=6, column=0, sticky='w', pady=(5,0))
        self.interval_var = tk.IntVar(value=long_interval)
        self.interval_scale = tk.Scale(settings_frame, from_=1, to=10, orient='horizontal', variable=self.interval_var, 
                                 length=200, bg=modal_bg, fg=text_primary, highlightthickness=0, bd=0, 
                                 troughcolor=button_bg, font=('Segoe UI', 9))
        self.interval_scale.grid(row=7, column=0, pady=(0,10))
        
        # Auto-start toggle
        self.auto_start_var = tk.BooleanVar(value=auto_start)
        auto_check = tk.Checkbutton(settings_frame, text="Auto-start next timer", variable=self.auto_start_var,
                                      font=('Segoe UI', 10), bg=modal_bg, fg=text_primary, selectcolor=modal_bg,
                                      activebackground=modal_bg, activeforeground=text_primary)
        auto_check.grid(row=8, column=0, columnspan=2, pady=(10, 5))
        
        # Sound toggle
        self.sound_var = tk.BooleanVar(value=enable_sound)
        sound_check = tk.Checkbutton(settings_frame, text="Enable Sound Effects", variable=self.sound_var,
                                      font=('Segoe UI', 10), bg=modal_bg, fg=text_primary, selectcolor=modal_bg,
                                      activebackground=modal_bg, activeforeground=text_primary)
        sound_check.grid(row=9, column=0, columnspan=2, pady=(0, 10))
        
        button_frame = tk.Frame(content, bg=modal_bg)
        button_frame.pack(pady=20)
        
        # Default (Reset)
        default_btn = tk.Button(button_frame, text="↺", font=('Segoe UI', 16, 'bold'), width=4,
                              bg=button_bg, fg=text_primary, command=self._reset_to_defaults)
        default_btn.config(bd=0, relief='flat', padx=0, pady=5, cursor='hand2', highlightthickness=0)
        default_btn.pack(side='left', padx=10)
        ToolTip(default_btn, "Restore Defaults")
        
        # Cancel (Close)
        cancel_btn = tk.Button(button_frame, text="✕", font=('Segoe UI', 16, 'bold'), width=4,
                             bg=error, fg=text_primary, command=self.close)
        cancel_btn.config(bd=0, relief='flat', padx=0, pady=5, cursor='hand2', highlightthickness=0)
        cancel_btn.pack(side='left', padx=10)
        ToolTip(cancel_btn, "Cancel")
        
        # Save (Check)
        save_btn = tk.Button(button_frame, text="✓", font=('Segoe UI', 16, 'bold'), width=4,
                           bg=success, fg=text_primary, command=self._save)
        save_btn.config(bd=0, relief='flat', padx=0, pady=5, cursor='hand2', highlightthickness=0)
        save_btn.pack(side='left', padx=10)
        ToolTip(save_btn, "Save Settings")
    
    def _reset_to_defaults(self):
        """Reset fields to default Pomodoro values"""
        self.work_var.set(SettingsManager.DEFAULT_WORK)
        self.short_var.set(SettingsManager.DEFAULT_SHORT_BREAK)
        self.long_var.set(SettingsManager.DEFAULT_LONG_BREAK)
        self.interval_var.set(SettingsManager.DEFAULT_LONG_BREAK_INTERVAL)
        self.auto_start_var.set(SettingsManager.DEFAULT_AUTO_START)
        self.sound_var.set(SettingsManager.DEFAULT_SOUND_ENABLED)
    
    def _save(self):
        """Save settings"""
        try:
            work = self.work_var.get()
            short = self.short_var.get()
            long_val = self.long_var.get()
            interval = self.interval_var.get()
            auto_start = self.auto_start_var.get()
            enable_sound = self.sound_var.get()
            
            if work < 1 or short < 1 or long_val < 1 or interval < 1:
                return
            
            self.result = (work, short, long_val, interval, auto_start, enable_sound)
            self.close()
        except ValueError:
            pass
    
    def close(self):
        """Close the dialog"""
        self.overlay.destroy()


class PomocusUI:
    """UI layer for Pomocus application"""
    
    def __init__(self, root: tk.Tk, logic, settings_manager: SettingsManager):
        self.root = root
        self.logic = logic
        self.settings_manager = settings_manager
        
        # Load theme colors from settings
        self.COLORS = self.settings_manager.get_theme()
        
        # Setup window
        self.root.title("Pomocus - Focus Timer")
        self.root.geometry("400x600")
        self.root.configure(bg=self.COLORS['bg_primary'])
        self.root.resizable(True, True)
        self.root.minsize(360, 500)
        
        # Bind resize event
        self.root.bind('<Configure>', self._on_resize)
        
        # UI elements
    
        self.mode_label: Optional[tk.Label] = None
        self.canvas: Optional[tk.Canvas] = None
        self.timer_label: Optional[int] = None
        self.progress_arc: Optional[int] = None
        self.progress_frame: Optional[tk.Frame] = None
        self.progress_dots: List[tk.Label] = []
        self.start_button: Optional[tk.Button] = None
        self.control_frame: Optional[tk.Frame] = None
        self.reset_btn: Optional[tk.Button] = None
        self.skip_btn: Optional[tk.Button] = None
        self.settings_btn: Optional[tk.Button] = None
        self.theme_btn: Optional[tk.Button] = None

        self._resize_after_id: Optional[str] = None
        
        # Pixel image for geometry control
        self.pixel = tk.PhotoImage(width=1, height=1)
        
        # Setup callbacks
        self.logic.on_tick = self._on_tick
        self.logic.on_complete = self._on_complete
        self.logic.on_mode_change = self._on_mode_change
        
        # Build UI
        self._setup_ui()
        self._update_display()
        
        # Start timer loop
        self._timer_loop()
    
    def _get_color_at_y(self, y: int) -> str:
        """Return background color (solid)"""
        return self.COLORS['bg_primary']
    
    def _toggle_theme(self):
        """Toggle between light and dark theme"""
        self.COLORS = self.settings_manager.toggle_theme()
        self._apply_theme()
        
    def _apply_theme(self):
        """Apply current theme colors to all widgets"""
        bg = self.COLORS['bg_primary']
        fg = self.COLORS['text_primary']
        muted = self.COLORS['text_muted']
        accent = self.COLORS['work'] # default accent
        mode_color = accent
        
        # Root
        self.root.configure(bg=bg)
        
        # Timer Canvas
        if self.canvas:
            self.canvas.config(bg=bg)
            self.canvas.itemconfig(self.timer_label, fill=fg)
            self.canvas.itemconfig(self.bg_circle, fill=self.COLORS['timer_bg'])
            self.canvas.itemconfig(self.bg_ring, outline=self.COLORS['progress_bg'])
            
            # Update mode color
            current_mode = self.logic.timer_mode if self.logic else 'work'
            mode_color = self.COLORS.get(current_mode, self.COLORS['work'])
            self.canvas.itemconfig(self.progress_arc, outline=mode_color)
            
        # Labels
        if self.mode_label:
            self.mode_label.config(bg=bg, fg=mode_color)

        # Frame and dots
        if self.progress_frame:
            self.progress_frame.config(bg=bg)
            for dot in self.progress_dots:
                dot.config(bg=bg)
                # individual fg update happens in _update_display
            
        # Controls
        # Note: Control buttons are local vars in _setup_ui, so we can't easily update them unless we store them.
        # But we previously converted them to self.start_button. Others (Reset/Skip/Settings) need to be stored or found.
        # We'll need to update _setup_ui to store them as self.xxx.
        
        # For now, let's update what we have.
        if self.control_frame:
            self.control_frame.config(bg=bg)
            
        if self.title_label:
            self.title_label.config(bg=bg, fg=mode_color)
            
        if self.settings_btn:
            self.settings_btn.config(bg=bg, fg=muted, activebackground=bg, activeforeground=fg)
            
        if self.theme_btn:
            self.theme_btn.config(bg=bg, fg=muted, activebackground=bg, activeforeground=fg)
            # Update icon based on mode
            mode = self.settings_manager.get_theme_mode()
            self.theme_btn.config(text="☀" if mode == 'dark' else "🌙")

        if self.reset_btn:
            self.reset_btn.config(bg=bg, fg=muted, activebackground=bg, activeforeground=fg)
             
        if self.start_button:
            self.start_button.config(bg=bg, fg=mode_color, activebackground=bg, activeforeground=mode_color)
             
        if self.skip_btn:
            self.skip_btn.config(bg=bg, fg=muted, activebackground=bg, activeforeground=fg)

    
    # ... existing methods ...

    def _show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(
            self.root, 
            self.logic.work_duration, 
            self.logic.short_break_duration, 
            self.logic.long_break_duration,
            self.logic.long_break_interval,
            self.logic.auto_start,
            self.settings_manager.get_theme(),
            self.settings_manager.get_sound_enabled()
        )
        self.root.wait_window(dialog.overlay)
        
        if dialog.result:
            # Save settings to file
            # result is (work, short, long, interval, auto_start, enable_sound)
            self.settings_manager.save_settings(*dialog.result)
            
            # Update logic (durations only)
            self.logic.update_durations(dialog.result[0], dialog.result[1], dialog.result[2], dialog.result[3], dialog.result[4])
            
            # Update UI for new settings
            self._handle_resize_redraw()
            self.start_button.config(text="▶")
            self._update_display()
            


    def _setup_ui(self):
        """Setup the user interface"""
        bg = self.COLORS['bg_primary']
        self.root.configure(bg=bg)
        
        # Theme Toggle (Top-left)
        mode = self.settings_manager.get_theme_mode()
        icon = "☀" if mode == 'dark' else "🌙"
        self.theme_btn = tk.Button(self.root, text=icon, font=('Segoe UI', 16),
                                  bg=bg, fg=self.COLORS['text_muted'],
                                  activebackground=bg, activeforeground=self.COLORS['text_primary'],
                                  command=self._toggle_theme)
        self.theme_btn.config(bd=0, relief='flat', cursor='hand2', highlightthickness=0)
        self.theme_btn.place(relx=0.0, x=20, y=20, anchor='nw')
        ToolTip(self.theme_btn, "Toggle Theme")
        
        # Settings button (Top-right)
        self.settings_btn = tk.Button(self.root, text="⚙", font=('Segoe UI', 16), 
                                 bg=bg, fg=self.COLORS['text_muted'], 
                                 activebackground=bg, activeforeground=self.COLORS['text_primary'],
                                 command=self._show_settings)
        self.settings_btn.config(bd=0, relief='flat', cursor='hand2', highlightthickness=0)
        self.settings_btn.place(relx=1.0, x=-20, y=20, anchor='ne')
        ToolTip(self.settings_btn, "Settings")
    
        # App Title (Centered Top)
        self.title_label = tk.Label(self.root, text="Pomofocus", font=('Segoe UI', 20, 'bold'),
                                   bg=bg, fg=self.COLORS['work'])
        self.title_label.place(relx=0.5, y=42, anchor='center')


        # Center X position
        center_x = 0.5
        
        # Timer canvas (Moved down to avoid overlap)
        curr_y = 240
        
        self.canvas = tk.Canvas(self.root, width=320, height=320, bg=bg, highlightthickness=0)
        self.canvas.place(relx=center_x, y=curr_y, anchor='center')
        
        # Mode label (Moved down near steps)
        curr_y = 430
        mode_bg = bg
        self.mode_label = tk.Label(self.root, text="FOCUS TIME", font=('Segoe UI', 20, 'bold'), 
                                   bg=mode_bg, fg=self.COLORS['work'])
        self.mode_label.place(relx=center_x, y=curr_y, anchor='center')
        

        # Progress dots
        # Progress dots Frame
        curr_y = 465
        dots_bg = bg
        self.progress_frame = tk.Frame(self.root, bg=dots_bg)
        self.progress_frame.place(relx=center_x, y=curr_y, anchor='center')
        self.progress_dots = []
        
        # Control Row Frame (Centered)
        curr_y = 540
        btn_bg = bg
        
        self.control_frame = tk.Frame(self.root, bg=btn_bg)
        self.control_frame.place(relx=center_x, y=curr_y, anchor='center')
        
        
        # Reset
        self.reset_btn = tk.Button(self.control_frame, text="↺", font=('Segoe UI', 18), 
                              bg=btn_bg, fg=self.COLORS['text_muted'], 
                              activebackground=btn_bg, activeforeground=self.COLORS['text_primary'],
                              image=self.pixel, compound='center', width=40, height=40)
        self.reset_btn.config(bd=0, relief='flat', padx=0, pady=0, cursor='hand2', highlightthickness=0)
        self.reset_btn.pack(side='left', padx=15)
        # Bind clicks manually
        self.reset_btn.bind('<Button-1>', self._on_reset_click)
        self.reset_btn.bind('<Double-Button-1>', self._on_reset_double_click)
        ToolTip(self.reset_btn, "Reset Timer (Double-click to Reset Flow)")
        
        # Play/Pause (Big)
        self.start_button = tk.Button(self.control_frame, text="▶", font=('Segoe UI', 36), 
                                      bg=btn_bg, fg=self.COLORS['work'], 
                                      activebackground=btn_bg, activeforeground=self.COLORS['work'],
                                      command=self._toggle_timer, image=self.pixel, compound='center', width=80, height=60)
        self.start_button.config(bd=0, relief='flat', padx=0, pady=0, cursor='hand2', highlightthickness=0)
        self.start_button.pack(side='left', padx=15)
        ToolTip(self.start_button, "Start/Pause")
        
        # Skip
        self.skip_btn = tk.Button(self.control_frame, text="⏭", font=('Segoe UI', 18), 
                             bg=btn_bg, fg=self.COLORS['text_muted'], 
                             activebackground=btn_bg, activeforeground=self.COLORS['text_primary'],
                             command=self._skip_timer, image=self.pixel, compound='center', width=40, height=40)
        self.skip_btn.config(bd=0, relief='flat', padx=0, pady=0, cursor='hand2', highlightthickness=0)
        self.skip_btn.pack(side='left', padx=15)
        ToolTip(self.skip_btn, "Skip Phase")

        # Initial draw of timer canvas (must be after elements are created)
        self._redraw_timer_canvas(50)
    
    def _redraw_timer_canvas(self, start_y: int):
        """Redraw timer elements"""
        self.canvas.delete('all')
        
        # 1. Background already handled by canvas.config(bg=...)
            
        # 2. Draw timer elements on top
        self.bg_circle = self.canvas.create_oval(10, 10, 310, 310, fill=self.COLORS['timer_bg'], outline='', width=0)
        self.bg_ring = self.canvas.create_oval(20, 20, 300, 300, outline=self.COLORS['progress_bg'], width=10)
        
        # Re-create arc and text items and store references
        # Determine current mode color
        current_mode = self.logic.timer_mode if self.logic else 'work'
        mode_color = self.COLORS.get(current_mode, self.COLORS['work'])
        
        self.progress_arc = self.canvas.create_arc(20, 20, 300, 300, start=90, extent=0, outline=mode_color, width=10, style='arc')
        
        # Get current time string if logic exists, else default
        time_str = self.logic.get_time_display() if self.logic else "25:00"
        self.timer_label = self.canvas.create_text(160, 160, text=time_str, font=('Segoe UI', 60, 'bold'), fill=self.COLORS['text_primary'])

        # Update display to ensure arc is correct
        if self.logic:
            self._update_display()

    

    
    def _on_resize(self, event):
        """Handle window resize"""
        if event.widget == self.root:
            if self._resize_after_id:
                self.root.after_cancel(self._resize_after_id)
            self._resize_after_id = self.root.after(75, self._handle_resize_redraw)

    def _handle_resize_redraw(self):
        """Debounced resize redraw handler"""
        self._resize_after_id = None
        self._redraw_timer_canvas(50)
        self._update_display()
            

    
    def _update_widget_backgrounds(self):
        """Update backgrounds of widgets to match new gradient"""
        # Title/Mode
        if self.mode_label:
            bg = self._get_color_at_y(390)
            self.mode_label.config(bg=bg)
        
        # Dots
        # Dots Frame
        if self.progress_frame:
            bg = self._get_color_at_y(425)
            self.progress_frame.config(bg=bg)
            for dot in self.progress_dots:
                dot.config(bg=bg)
            
    def _toggle_timer(self):
        """Toggle timer start/pause"""
        if self.logic.is_running:
            self.logic.pause()
            self.start_button.config(text="▶")
        else:
            self.logic.start()
            self.start_button.config(text="⏸")
    
    def _reset_timer(self):
        """Reset timer"""
        self.logic.reset()
        self.start_button.config(text="▶")
        self._update_display()
        
    def _reset_flow(self):
        """Reset entire flow"""
        self.logic.reset_flow()
        self.start_button.config(text="▶")
        self._update_display()
        
    def _on_reset_click(self, event):
        """Handle single click on reset"""
        self._reset_timer()
        
    def _on_reset_double_click(self, event):
        """Handle double click on reset"""
        self._reset_flow()
    
    def _skip_timer(self):
        """Skip to next phase"""
        self.logic.skip()
    

    
    def _on_tick(self):
        """Called on each timer tick"""
        self._update_display()
    
    def _on_complete(self, previous_mode: str):
        """Called when timer completes"""
        self.start_button.config(text="▶")
        self._play_notification()
        self._flash_window()
        
        # Alerts removed as requested
        # UI automatically updates via _on_mode_change
    
    def _on_mode_change(self, mode: str):
        """Called when mode changes"""
        mode_config = {
            'work': ("FOCUS TIME", self.COLORS['work']),
            'short_break': ("SHORT BREAK", self.COLORS['short_break']),
            'long_break': ("LONG BREAK", self.COLORS['long_break'])
        }
        
        text, color = mode_config.get(mode, ("FOCUS TIME", self.COLORS['work']))
        self.mode_label.config(text=text, fg=color)
        self.start_button.config(fg=color, activeforeground=color)
        self.canvas.itemconfig(self.progress_arc, outline=color)
        
        self._update_display()
    
    def _update_display(self):
        """Update all display elements"""
        # Update timer text
        time_str = self.logic.get_time_display()
        self.canvas.itemconfig(self.timer_label, text=time_str)
        self.root.title(f"Pomocus - {time_str}")
        
        # Update progress arc
        progress = self.logic.get_progress()
        extent = -360 * progress
        self.canvas.itemconfig(self.progress_arc, extent=extent)
        
        # Update progress dots sequence: Circle - Dash - Circle ...
        interval = self.logic.long_break_interval
        current_completed = self.logic.pomodoros_completed % interval
        current_mode = self.logic.timer_mode
        
        # Colors
        c_work = self.COLORS.get('work', '#FF6B6B')
        c_short = self.COLORS.get('short_break', '#4ECDC4')
        c_long = self.COLORS.get('long_break', '#45B7D1')
        c_muted = self.COLORS['text_muted'] # Pending/Inactive

        needed_widgets = interval * 2 - 1
        
        has_coffee = False
        if len(self.progress_dots) > needed_widgets:
             # assume last is coffee
             has_coffee = True
        
        # Check if we SHOULD have coffee
        should_have_coffee = (current_mode == 'long_break')
        #should_have_coffee = True #always
        
        if len(self.progress_dots) < needed_widgets or (len(self.progress_dots) != needed_widgets and not (has_coffee and len(self.progress_dots) == needed_widgets + 1)):
            # Full rebuild simple
            for w in self.progress_dots:
                w.destroy()
            self.progress_dots.clear()
            
            for i in range(interval):
                # Circle
                lbl = tk.Label(self.progress_frame, text="○", font=('Segoe UI', 18), bg=self.progress_frame.cget('bg'), fg=c_muted)
                lbl.pack(side='left', padx=0)
                self.progress_dots.append(lbl)
                
                # Dash (if not last)
                if i < interval - 1:
                    lbl_d = tk.Label(self.progress_frame, text="—", font=('Segoe UI', 14, 'bold'), bg=self.progress_frame.cget('bg'), fg=c_muted)
                    lbl_d.pack(side='left', padx=0)
                    self.progress_dots.append(lbl_d)
            
            # Reset coffee flag after rebuild
            has_coffee = False
        
        # Manage Coffee Widget
        if should_have_coffee and not has_coffee:
            lbl_coffee = tk.Label(self.progress_frame, text="☕", font=('Segoe UI', 18), bg=self.progress_frame.cget('bg'), fg=c_long)
            lbl_coffee.pack(side='left', padx=(5,0))
            self.progress_dots.append(lbl_coffee)
        elif not should_have_coffee and has_coffee:
            # Remove last widget
            w = self.progress_dots.pop()
            w.destroy()

        for i in range(interval):
            # Widget Indices
            idx_c = i * 2       # Circle Index
            idx_d = i * 2 + 1   # Dash Index (exists if i < interval-1)
            
            circle = self.progress_dots[idx_c]
            
            # State of Work Circle i
            if i < current_completed:
                # Completed
                circle.config(text="●", fg=c_work)
            elif i == current_completed:
                # Current Round
                if current_mode == 'work':
                    # Active Work
                    circle.config(text="●", fg=c_work)
                else:
                    # Work pending (we are in break before this? No, breaks follow work)
                    # If we are in work i, it is active.
                    # If we are in break after i, i is done.
                    # Wait, current_completed is count of DONE works.
                    # So if i == current_completed, this is the NEXT work (Pending).
                    circle.config(text="○", fg=c_muted)
            else:
                # Future
                circle.config(text="○", fg=c_muted)
            
            # State of Break Dash i (after Work i)
            if i < interval - 1:
                dash = self.progress_dots[idx_d]
                # Break i happens after Work i is done.
                # So if i < current_completed: Work i is done.
                # If i == current_completed - 1: We just finished Work i. We are in Break i.
                
                if i < current_completed - 1:
                    # Past break
                    dash.config(fg=c_work) # or muted? Let's color it work to show continuity "Line of Work"? Or muted.
                    # User want 'dash indicator for short break'.
                    # Let's use muted for done, Teal for active.
                    dash.config(fg=c_work) 
                elif i == current_completed - 1:
                    # Most recent completed work was i.
                    if current_mode == 'short_break':
                        # ACTIVE BREAK
                        dash.config(fg=c_short)
                    elif current_mode == 'long_break':
                        # Should only start after last work, but if interval logic allows early long break?
                        # Usually long break is at end.
                        dash.config(fg=c_long)
                    else:
                        # Back to work (next), so this break is done.
                        dash.config(fg=c_work)
                else:
                    # Future break
                    dash.config(fg=c_muted)
    
    def _timer_loop(self):
        """Main timer loop"""
        self.logic.tick()
        self.root.after(1000, self._timer_loop)
    
    def _show_modal(self, title: str, message: str, color: str):
        """Show modal overlay"""
        ModalOverlay(self.root, title, message, color)
    
    def _flash_window(self):
        """Flash window to get attention"""
        if sys.platform.startswith('win'):
            try:
                import ctypes
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                ctypes.windll.user32.FlashWindow(hwnd, True)
                return
            except Exception:
                pass

        # Cross-platform fallback: try to raise the window, otherwise no-op
        try:
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.after(200, lambda: self.root.attributes('-topmost', False))
        except Exception:
            pass
    
    def _play_notification(self):
        """Play notification sound"""
        if not self.settings_manager.get_sound_enabled():
            return
            
        try:
            # Cross-platform standard alert sound
            self.root.bell()
        except Exception:
            pass
