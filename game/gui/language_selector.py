"""
Language selector dialog for the game.
游戏语言选择弹窗。
"""

import tkinter as tk
from tkinter import messagebox
from typing import Literal


class LanguageSelectorWindow:
    """Language selection dialog window."""
    
    def __init__(self, parent=None):
        """Initialize language selector.
        
        Args:
            parent: Parent window (optional)
        """
        self.selected_language = None
        
        if parent:
            self.window = tk.Toplevel(parent)
            self.is_root = False
        else:
            # Create a hidden root window first
            self.root = tk.Tk()
            self.root.withdraw()  # Hide it
            self.window = tk.Toplevel(self.root)
            self.is_root = True
        
        self.window.title("Language Selection / 语言选择")
        self.window.geometry("400x200")
        self.window.resizable(False, False)
        
        # Center window
        if parent:
            self.window.transient(parent)
            self.window.grab_set()
        
        # Create UI
        self._create_widgets()
        
        # Center on screen
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - 200
        y = (self.window.winfo_screenheight() // 2) - 100
        self.window.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create UI widgets."""
        # Main frame
        main_frame = tk.Frame(self.window, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="选择语言 / Choose Language",
            font=('Arial', 16, 'bold'),
            bg='#1a1a2e',
            fg='#00d4ff'
        )
        title_label.pack(pady=(0, 20))
        
        # Subtitle
        subtitle_label = tk.Label(
            main_frame,
            text="Select your preferred language:",
            font=('Arial', 10),
            bg='#1a1a2e',
            fg='#eaeaea'
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#1a1a2e')
        button_frame.pack()
        
        # Chinese button
        chinese_btn = tk.Button(
            button_frame,
            text="🇨🇳 中文",
            font=('Arial', 12, 'bold'),
            bg='#00d4ff',
            fg='#1a1a2e',
            width=15,
            height=2,
            cursor='hand2',
            command=self._select_chinese
        )
        chinese_btn.pack(side=tk.LEFT, padx=10)
        
        # English button
        english_btn = tk.Button(
            button_frame,
            text="🇬🇧 English",
            font=('Arial', 12, 'bold'),
            bg='#00d4ff',
            fg='#1a1a2e',
            width=15,
            height=2,
            cursor='hand2',
            command=self._select_english
        )
        english_btn.pack(side=tk.LEFT, padx=10)
    
    def _select_chinese(self):
        """Select Chinese language."""
        self.selected_language = 'zh'
        self.window.destroy()
    
    def _select_english(self):
        """Select English language."""
        self.selected_language = 'en'
        self.window.destroy()
    
    def get_language(self) -> Literal['zh', 'en']:
        """Wait for language selection and return it.
        
        Returns:
            'zh' for Chinese, 'en' for English
        """
        self.window.wait_window()
        
        if self.is_root and hasattr(self, 'root'):
            self.root.destroy()
        
        return self.selected_language or 'zh'  # Default to Chinese


def select_language(parent=None) -> Literal['zh', 'en']:
    """Show language selector and return selected language.
    
    Args:
        parent: Parent window (optional)
    
    Returns:
        'zh' for Chinese, 'en' for English
    """
    selector = LanguageSelectorWindow(parent)
    return selector.get_language()
