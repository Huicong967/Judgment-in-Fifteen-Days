#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Launcher for Judgment in Fifteen Days Game
"""

import sys
import os
import tkinter as tk

# Ensure project root is on sys.path so `import game.*` works
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.runner_redesigned import GUIGameRunnerRedesigned, show_language_selection_dialog
from game.manager import LevelManager

if __name__ == '__main__':
    # Show language selection dialog first
    selected_language = show_language_selection_dialog()
    
    # Create main window
    root = tk.Tk()
    root.title("Judgment in Fifteen Days - 十五日裁决")
    root.geometry("1920x1080")
    
    # Create manager
    manager = LevelManager()
    
    # Create runner with selected language
    runner = GUIGameRunnerRedesigned(manager, root, initial_language=selected_language)
    
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
    
    # Run main loop
    root.mainloop()