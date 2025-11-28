#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Launcher for Judgment in Fifteen Days Game
"""

import sys
import os
import tkinter as tk
from PIL import Image, ImageTk

# Ensure project root is on sys.path so `import game.*` works
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.runner_redesigned import GUIGameRunnerRedesigned, show_language_selection_dialog
from game.manager import LevelManager
from game.audio_manager import AudioManager


def show_start_menu(root, selected_language):
    """Show start menu with Begin and Exit buttons."""
    # Get screen dimensions
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    
    # Fullscreen state
    is_fullscreen = [True]
    default_window_width = int(screen_w * 0.85)
    default_window_height = int(screen_h * 0.85)
    
    # Set fullscreen borderless
    root.overrideredirect(True)
    root.geometry(f"{screen_w}x{screen_h}+0+0")
    
    # Create canvas for start menu
    canvas = tk.Canvas(root, width=screen_w, height=screen_h, highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # Store loaded images for redrawing
    image_cache = {}
    
    def load_and_draw_menu(width, height):
        """Load and draw all menu elements at given size."""
        canvas.delete("all")
        canvas.config(width=width, height=height)
        
        center_x = width // 2
        
        # Calculate positions based on window size
        logo_y = int(height * 0.25)
        begin_y = int(height * 0.6)
        exit_y = int(height * 0.75)
        
        # Load and display background image
        try:
            bg_img = Image.open("UI/begingame.png")
            img_w, img_h = bg_img.size
            if img_w > 0 and img_h > 0:
                cover_scale = max(width / img_w, height / img_h)
                cover_w = max(1, int(img_w * cover_scale))
                cover_h = max(1, int(img_h * cover_scale))
                resized = bg_img.resize((cover_w, cover_h), Image.Resampling.LANCZOS)
                
                left = (cover_w - width) // 2
                top = (cover_h - height) // 2
                right = left + width
                bottom = top + height
                cropped = resized.crop((left, top, right, bottom))
                
                bg_photo = ImageTk.PhotoImage(cropped)
                canvas.create_image(0, 0, anchor=tk.NW, image=bg_photo)
                image_cache['bg_photo'] = bg_photo
        except Exception as e:
            print(f"Warning: Could not load begingame.png: {e}")
            canvas.configure(bg="black")
        
        # Load and display logo
        try:
            logo_img = Image.open("UI/logo.png").convert('RGBA')
            max_logo_width = int(width * 0.6)
            if logo_img.width > max_logo_width:
                scale = max_logo_width / logo_img.width
                new_w = int(logo_img.width * scale)
                new_h = int(logo_img.height * scale)
                logo_img = logo_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            logo_photo = ImageTk.PhotoImage(logo_img)
            canvas.create_image(center_x, logo_y, image=logo_photo)
            image_cache['logo_photo'] = logo_photo
        except Exception as e:
            print(f"Warning: Could not load logo.png: {e}")
        
        # Load and display Begin button
        try:
            begin_button_file = "UI/beginbuttonChinese.png" if selected_language == "中文" else "UI/beginbutton.png"
            begin_img = Image.open(begin_button_file).convert('RGBA')
            max_btn_width = int(width * 0.25)
            if begin_img.width > max_btn_width:
                scale = max_btn_width / begin_img.width
                new_w = int(begin_img.width * scale)
                new_h = int(begin_img.height * scale)
                begin_img = begin_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            begin_photo = ImageTk.PhotoImage(begin_img)
            canvas.create_image(center_x, begin_y, image=begin_photo, tags="begin_button")
            image_cache['begin_photo'] = begin_photo
            
            canvas.tag_bind("begin_button", "<Button-1>", lambda e: start_game())
            canvas.tag_bind("begin_button", "<Enter>", lambda e: canvas.config(cursor="hand2"))
            canvas.tag_bind("begin_button", "<Leave>", lambda e: canvas.config(cursor=""))
        except Exception as e:
            print(f"Warning: Could not load begin button: {e}")
        
        # Load and display Exit button
        try:
            exit_button_file = "UI/exitbuttonChinese.png" if selected_language == "中文" else "UI/exitbutton.png"
            exit_img = Image.open(exit_button_file).convert('RGBA')
            max_btn_width = int(width * 0.25)
            if exit_img.width > max_btn_width:
                scale = max_btn_width / exit_img.width
                new_w = int(exit_img.width * scale)
                new_h = int(exit_img.height * scale)
                exit_img = exit_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            exit_photo = ImageTk.PhotoImage(exit_img)
            canvas.create_image(center_x, exit_y, image=exit_photo, tags="exit_button")
            image_cache['exit_photo'] = exit_photo
            
            canvas.tag_bind("exit_button", "<Button-1>", lambda e: exit_game())
            canvas.tag_bind("exit_button", "<Enter>", lambda e: canvas.config(cursor="hand2"))
            canvas.tag_bind("exit_button", "<Leave>", lambda e: canvas.config(cursor=""))
        except Exception as e:
            print(f"Warning: Could not load exit button: {e}")
    
    def toggle_fullscreen(event=None):
        """Toggle fullscreen mode."""
        # Cancel any pending redraws
        if pending_redraw[0] is not None:
            root.after_cancel(pending_redraw[0])
            pending_redraw[0] = None
        
        if is_fullscreen[0]:
            # Exit fullscreen
            root.overrideredirect(False)
            # Center window
            x = (screen_w - default_window_width) // 2
            y = (screen_h - default_window_height) // 2
            root.geometry(f"{default_window_width}x{default_window_height}+{x}+{y}")
            is_fullscreen[0] = False
            last_size[0] = default_window_width
            last_size[1] = default_window_height
            # Redraw menu at new size with delay
            pending_redraw[0] = root.after(150, lambda: load_and_draw_menu(default_window_width, default_window_height))
        else:
            # Enter fullscreen
            root.overrideredirect(True)
            root.geometry(f"{screen_w}x{screen_h}+0+0")
            is_fullscreen[0] = True
            last_size[0] = screen_w
            last_size[1] = screen_h
            # Redraw menu at new size with delay
            pending_redraw[0] = root.after(150, lambda: load_and_draw_menu(screen_w, screen_h))
    
    # Bind Esc key to toggle fullscreen
    root.bind('<Escape>', toggle_fullscreen)
    
    # Track last known size to detect changes
    last_size = [screen_w, screen_h]
    pending_redraw = [None]  # Store pending after() id
    
    def on_configure(event):
        """Handle window resize events."""
        # Only respond to window resize events, not widget resizes
        if event.widget == root:
            new_width = event.width
            new_height = event.height
            # Only redraw if size actually changed significantly
            if abs(new_width - last_size[0]) > 10 or abs(new_height - last_size[1]) > 10:
                last_size[0] = new_width
                last_size[1] = new_height
                
                # Cancel any pending redraw
                if pending_redraw[0] is not None:
                    root.after_cancel(pending_redraw[0])
                
                # Schedule redraw with delay to avoid multiple rapid redraws
                pending_redraw[0] = root.after(50, lambda: load_and_draw_menu(new_width, new_height))
    
    # Bind window resize event
    root.bind('<Configure>', on_configure)
    
    # Initialize audio manager and play background music
    audio_manager = AudioManager()
    audio_manager.start_bgm()
    
    def play_click_sound():
        """Play button click sound."""
        audio_manager.play_click()
    
    # Variable to track if game should start
    game_started = [False]
    
    def start_game():
        """Start the game."""
        play_click_sound()
        game_started[0] = True
        # Don't stop background music - let it continue into the game
        canvas.destroy()
        # Create manager and runner, pass the audio manager to continue music
        manager = LevelManager()
        runner = GUIGameRunnerRedesigned(manager, root, initial_language=selected_language, audio_manager=audio_manager)
        
        # Set up window close protocol
        def on_closing():
            """Handle window close event."""
            try:
                runner.cleanup()
                root.quit()
                root.destroy()
            except:
                pass
            sys.exit(0)
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the game
        runner.start_game()
    
    def exit_game():
        """Exit the game."""
        play_click_sound()
        audio_manager.cleanup()
        root.quit()
        root.destroy()
        sys.exit(0)
    
    # Initial draw at fullscreen size
    load_and_draw_menu(screen_w, screen_h)


if __name__ == '__main__':
    # Show language selection dialog first
    selected_language = show_language_selection_dialog()
    
    # Create main window
    root = tk.Tk()
    root.title("Judgment in Fifteen Days - 十五日裁决")
    
    # Show start menu
    show_start_menu(root, selected_language)
    
    # Run main loop
    root.mainloop()