"""
GUI widgets for the redesigned game interface.
重设计的游戏 GUI 组件。
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Optional, List
from PIL import Image, ImageTk

from game.i18n import get_i18n
from game.image_manager import get_image_manager


class Colors:
    """Color scheme."""
    BG_DARK = '#1a1a2e'
    BG_MEDIUM = '#16213e'
    BG_LIGHT = '#0f3460'
    TEXT_PRIMARY = '#eaeaea'
    TEXT_SECONDARY = '#b0b0b0'
    ACCENT = '#00d4ff'
    STATUS_STAMINA = '#ff6b6b'
    STATUS_MANA = '#4ecdc4'
    STATUS_ROUTE = '#ffd93d'


class PropertyPanel(tk.Frame):
    """Left sidebar panel showing player properties."""
    
    def __init__(self, parent, on_clues_click=None, **kwargs):
        super().__init__(parent, bg=Colors.BG_DARK, **kwargs)
        self.i18n = get_i18n()
        self.max_stamina = 50
        self.max_mana = 50
        self.current_stamina = 20
        self.current_mana = 20
        self.on_clues_click = on_clues_click
        self.clues_overlay = None
        self._create_widgets()
    
    def _create_widgets(self):
        """Create property display widgets."""
        # Title
        title = tk.Label(
            self,
            text=self.i18n.get_ui_text('properties'),
            font=('Arial', 12, 'bold'),
            bg=Colors.BG_DARK,
            fg=Colors.ACCENT
        )
        title.pack(pady=10)
        
        # Stamina section
        stamina_label_name = tk.Label(
            self,
            text=self.i18n.get_ui_text('stamina_label'),
            font=('Arial', 9, 'bold'),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_PRIMARY
        )
        stamina_label_name.pack(pady=(5, 2))
        
        # Stamina progress bar
        self.stamina_progress = ttk.Progressbar(
            self,
            length=200,
            mode='determinate',
            maximum=self.max_stamina,
            value=self.current_stamina
        )
        self.stamina_progress.pack(padx=10, pady=2)
        
        # Stamina value display
        self.stamina_label = tk.Label(
            self,
            text=f"{self.current_stamina}/{self.max_stamina}",
            font=('Arial', 9),
            bg=Colors.BG_DARK,
            fg=Colors.STATUS_STAMINA
        )
        self.stamina_label.pack(pady=(0, 5))
        
        # Mana section
        mana_label_name = tk.Label(
            self,
            text=self.i18n.get_ui_text('mana_label'),
            font=('Arial', 9, 'bold'),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_PRIMARY
        )
        mana_label_name.pack(pady=(5, 2))
        
        # Mana progress bar
        self.mana_progress = ttk.Progressbar(
            self,
            length=200,
            mode='determinate',
            maximum=self.max_mana,
            value=self.current_mana
        )
        self.mana_progress.pack(padx=10, pady=2)
        
        # Mana value display
        self.mana_label = tk.Label(
            self,
            text=f"{self.current_mana}/{self.max_mana}",
            font=('Arial', 9),
            bg=Colors.BG_DARK,
            fg=Colors.STATUS_MANA
        )
        self.mana_label.pack(pady=(0, 5))
        
        # Routes title
        routes_title = tk.Label(
            self,
            text="【 路线 】" if self.i18n.language == 'zh' else "【 Routes 】",
            font=('Arial', 11, 'bold'),
            bg=Colors.BG_DARK,
            fg=Colors.ACCENT
        )
        routes_title.pack(pady=(15, 5))
        
        # Route progress with full names
        self.bribe_label = tk.Label(
            self,
            text=f"{self.i18n.get_ui_text('bribe_full')}: 0",
            font=('Arial', 8),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_PRIMARY,
            wraplength=220,
            justify=tk.LEFT
        )
        self.bribe_label.pack(pady=3, padx=5)
        
        self.sabotage_label = tk.Label(
            self,
            text=f"{self.i18n.get_ui_text('sabotage_full')}: 0",
            font=('Arial', 8),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_PRIMARY,
            wraplength=220,
            justify=tk.LEFT
        )
        self.sabotage_label.pack(pady=3, padx=5)
        
        self.legal_label = tk.Label(
            self,
            text=f"{self.i18n.get_ui_text('legal_full')}: 0",
            font=('Arial', 8),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_PRIMARY,
            wraplength=220,
            justify=tk.LEFT
        )
        self.legal_label.pack(pady=3, padx=5)
        
        # Clues button
        clues_frame = tk.Frame(self, bg=Colors.BG_DARK)
        clues_frame.pack(pady=(15, 5))
        
        self.clues_btn = tk.Button(
            clues_frame,
            text=self.i18n.get_ui_text('clues_button'),
            font=('Arial', 9, 'bold'),
            bg=Colors.STATUS_ROUTE,
            fg=Colors.BG_DARK,
            cursor='hand2',
            command=self._on_clues_click,
            width=18
        )
        self.clues_btn.pack()
    
    def _on_clues_click(self):
        """Handle clues button click."""
        if self.on_clues_click:
            self.on_clues_click()
    
    def update_properties(self, stamina: int, mana: int, bribe: int, sabotage: int, legal: int):
        """Update property display."""
        self.current_stamina = stamina
        self.current_mana = mana
        self.stamina_progress.config(value=stamina)
        self.stamina_label.config(text=f"{stamina}/{self.max_stamina}")
        self.mana_progress.config(value=mana)
        self.mana_label.config(text=f"{mana}/{self.max_mana}")
        self.bribe_label.config(text=f"{self.i18n.get_ui_text('bribe_full')}: {bribe}")
        self.sabotage_label.config(text=f"{self.i18n.get_ui_text('sabotage_full')}: {sabotage}")
        self.legal_label.config(text=f"{self.i18n.get_ui_text('legal_full')}: {legal}")


class ItemPanel(tk.Frame):
    """Left sidebar panel for items and clues."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Colors.BG_DARK, **kwargs)
        self.i18n = get_i18n()
        self.items = []
        self._create_widgets()
    
    def _create_widgets(self):
        """Create item display widgets."""
        # Title
        items_text = "【 道具 】" if self.i18n.language == 'zh' else "【 Items 】"
        title = tk.Label(
            self,
            text=items_text,
            font=('Arial', 11, 'bold'),
            bg=Colors.BG_DARK,
            fg=Colors.ACCENT
        )
        title.pack(pady=10)
        
        # Scrollable frame for items
        self.scroll_frame = tk.Frame(self, bg=Colors.BG_DARK)
        self.scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5)
    
    def add_item(self, name: str, description: str = ""):
        """Add an item to display.
        
        Args:
            name: Item name
            description: Item description
        """
        item_btn = tk.Button(
            self.scroll_frame,
            text=f"🔍 {name}",
            font=('Arial', 9),
            bg=Colors.BG_MEDIUM,
            fg=Colors.ACCENT,
            relief=tk.RAISED,
            height=2,
            wraplength=220
        )
        item_btn.pack(fill=tk.X, pady=3)
        self.items.append((name, description, item_btn))
    
    def clear_items(self):
        """Clear all items."""
        for _, _, btn in self.items:
            btn.destroy()
        self.items.clear()


class ImagePanel(tk.Frame):
    """Right side panel for displaying game images."""
    
    def __init__(self, parent, width: int = 800, height: int = 600, **kwargs):
        super().__init__(parent, bg=Colors.BG_DARK, width=width, height=height, **kwargs)
        self.image_manager = get_image_manager()
        self.i18n = get_i18n()
        self.width = width
        self.height = height
        self.current_image = None
        self.photo_image = None
        self.clues_visible = False
        self.clues_overlay = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create image display widgets."""
        # Main frame for image and overlay
        self.main_frame = tk.Frame(self, bg=Colors.BG_DARK)
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=0, pady=0)
        
        # Image label - full fill with no background color showing
        self.image_label = tk.Label(
            self.main_frame,
            bg=Colors.BG_DARK,
            image=None
        )
        self.image_label.pack(expand=True, fill=tk.BOTH, padx=0, pady=0)
        self.image_label.bind('<Button-1>', self._on_image_click)
        
        # Initially show placeholder
        self._show_placeholder()
    
    def _show_placeholder(self):
        """Show placeholder image."""
        img = Image.new('RGB', (self.width, self.height), color=Colors.BG_LIGHT)
        self.set_image(img)
    
    def _on_image_click(self, event):
        """Handle image click to toggle clues."""
        if self.clues_visible:
            self._hide_clues()
    
    def show_clues(self, clues_text: str = ""):
        """Show clues overlay on image.
        
        Args:
            clues_text: Text to display on clues overlay
        """
        if self.clues_visible:
            self._hide_clues()
            return
        
        self.clues_visible = True
        
        # Create overlay window
        self.clues_overlay = tk.Toplevel(self.main_frame)
        self.clues_overlay.geometry(f"{self.width}x{self.height}")
        self.clues_overlay.config(bg=Colors.BG_DARK)
        
        # Position overlay on top of image
        x = self.image_label.winfo_rootx()
        y = self.image_label.winfo_rooty()
        self.clues_overlay.geometry(f"+{x}+{y}")
        self.clues_overlay.attributes('-topmost', True)
        self.clues_overlay.title("线索" if self.i18n.language == 'zh' else "Clues")
        
        # Clues content
        clues_frame = tk.Frame(self.clues_overlay, bg=Colors.BG_MEDIUM, relief=tk.RAISED, bd=2)
        clues_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Clues text
        clues_text_widget = tk.Text(
            clues_frame,
            font=('Arial', 10),
            bg=Colors.BG_MEDIUM,
            fg=Colors.TEXT_PRIMARY,
            wrap=tk.WORD,
            relief=tk.FLAT,
            state=tk.DISABLED,
            height=15
        )
        clues_text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add text
        clues_text_widget.config(state=tk.NORMAL)
        clues_text_widget.delete('1.0', tk.END)
        clues_text_widget.insert('1.0', clues_text or ("暂无线索" if self.i18n.language == 'zh' else "No clues yet"))
        clues_text_widget.config(state=tk.DISABLED)
        
        # Close button
        close_btn = tk.Button(
            clues_frame,
            text="关闭" if self.i18n.language == 'zh' else "Close",
            font=('Arial', 9),
            bg=Colors.ACCENT,
            fg=Colors.BG_DARK,
            command=self._hide_clues
        )
        close_btn.pack(pady=5)
        
        # Handle window close
        def on_overlay_close():
            self._hide_clues()
        
        self.clues_overlay.protocol("WM_DELETE_WINDOW", on_overlay_close)
    
    def _hide_clues(self):
        """Hide clues overlay."""
        if self.clues_overlay:
            self.clues_overlay.destroy()
            self.clues_overlay = None
        self.clues_visible = False
    
    def set_image(self, image: Image.Image):
        """Set the displayed image.
        
        Args:
            image: PIL Image to display
        """
        if image is None:
            self._show_placeholder()
            return
        
        # Resize if necessary
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)
        
        self.current_image = image
        self.photo_image = ImageTk.PhotoImage(image)
        self.image_label.config(image=self.photo_image)
    
    def set_background(self, name: str):
        """Set background image.
        
        Args:
            name: Background name
        """
        bg_image = self.image_manager.get_background(name)
        self.set_image(bg_image)


class NarrativePanel(tk.Frame):
    """Bottom panel for narrative text."""
    
    def __init__(self, parent, on_continue_click: Optional[Callable] = None, **kwargs):
        super().__init__(parent, bg=Colors.BG_DARK, height=150, **kwargs)
        self.i18n = get_i18n()
        self.on_continue_click = on_continue_click
        self._create_widgets()
    
    def _create_widgets(self):
        """Create narrative display widgets."""
        # Container for text and button
        content_frame = tk.Frame(self, bg=Colors.BG_DARK)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text display (read-only) - full fill
        self.text_widget = tk.Text(
            content_frame,
            height=6,
            font=('Arial', 9),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_PRIMARY,
            wrap=tk.WORD,
            relief=tk.FLAT,
            state=tk.DISABLED,
            borderwidth=0
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Button frame at bottom
        button_frame = tk.Frame(self, bg=Colors.BG_DARK)
        button_frame.pack(pady=5)
        
        # Continue button
        self.continue_btn = tk.Button(
            button_frame,
            text=self.i18n.get_ui_text('make_choice'),
            font=('Arial', 10, 'bold'),
            bg=Colors.ACCENT,
            fg=Colors.BG_DARK,
            cursor='hand2',
            command=self._on_continue
        )
        self.continue_btn.pack()
    
    def set_narrative(self, text: str):
        """Set narrative text.
        
        Args:
            text: Narrative text to display
        """
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete('1.0', tk.END)
        self.text_widget.insert('1.0', text)
        self.text_widget.config(state=tk.DISABLED)
    
    def _on_continue(self):
        """Handle continue button click."""
        if self.on_continue_click:
            self.on_continue_click()
    
    def show_continue_button(self, show: bool = True):
        """Show or hide continue button.
        
        Args:
            show: True to show, False to hide
        """
        if show:
            self.continue_btn.pack()
        else:
            self.continue_btn.pack_forget()
    
    def show_narrative_text(self, show: bool = True):
        """Show or hide narrative text.
        
        Args:
            show: True to show, False to hide
        """
        if show:
            self.text_widget.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        else:
            self.text_widget.pack_forget()


class GameWindow(tk.Tk):
    """Main game window with new layout."""
    
    def __init__(self):
        super().__init__()
        
        self.i18n = get_i18n()
        title_text = "《审判在十五天》" if self.i18n.language == 'zh' else "Judgment in Fifteen Days"
        self.title(title_text)
        self.geometry("1600x1000")
        self.config(bg=Colors.BG_DARK)
        
        self._create_layout()
    
    def _create_layout(self):
        """Create the main layout with four regions."""
        # Main container
        main_frame = tk.Frame(self, bg=Colors.BG_DARK)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top frame (content area)
        top_frame = tk.Frame(main_frame, bg=Colors.BG_DARK)
        top_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Left sidebar
        left_panel = tk.Frame(top_frame, bg=Colors.BG_DARK, width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        left_panel.pack_propagate(False)
        
        # Right image panel - full fill (create first so we can reference it)
        self.image_panel = ImagePanel(top_frame, width=800, height=600)
        self.image_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Property panel with clues callback
        self.property_panel = PropertyPanel(
            left_panel,
            on_clues_click=self._on_clues_click
        )
        self.property_panel.pack(fill=tk.X, pady=5)
        
        # Item panel
        self.item_panel = ItemPanel(left_panel)
        self.item_panel.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Bottom narrative panel - full fill
        self.narrative_panel = NarrativePanel(main_frame)
        self.narrative_panel.pack(fill=tk.X, padx=0, pady=0)
    
    def _on_clues_click(self):
        """Handle clues button click."""
        self.image_panel.show_clues("这是一个真相线索。\n点击此窗口关闭，或再次点击真相线索按钮。" if self.i18n.language == 'zh' else "This is a truth clue.\nClick the close button or the clues button again to hide.")
    
    def update_properties(self, stamina: int, mana: int, bribe: int, sabotage: int, legal: int):
        """Update all property displays."""
        self.property_panel.update_properties(stamina, mana, bribe, sabotage, legal)
    
    def set_narrative(self, text: str):
        """Set narrative text."""
        self.narrative_panel.set_narrative(text)
    
    def set_background_image(self, name: str):
        """Set background image."""
        self.image_panel.set_background(name)
    
    def add_item(self, name: str, description: str = ""):
        """Add item to inventory display."""
        self.item_panel.add_item(name, description)


# Result dialog
class ResultWindow(tk.Toplevel):
    """Dialog for displaying choice results."""
    
    def __init__(self, parent, result_text: str, changes: Dict[str, int], item: Optional[str] = None):
        super().__init__(parent)
        
        self.i18n = get_i18n()
        self.result = None
        
        self.title(self.i18n.get_ui_text('choice_result'))
        self.geometry("400x300")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center dialog
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 150
        self.geometry(f"+{x}+{y}")
        
        self._create_widgets(result_text, changes, item)
        self._center_on_parent(parent)
    
    def _create_widgets(self, result_text: str, changes: Dict[str, int], item: Optional[str]):
        """Create result dialog widgets."""
        # Main frame
        main_frame = tk.Frame(self, bg=Colors.BG_DARK)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Result text
        text_label = tk.Label(
            main_frame,
            text=result_text,
            font=('Arial', 9),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_PRIMARY,
            wraplength=350,
            justify=tk.LEFT
        )
        text_label.pack(pady=10)
        
        # Changes
        changes_frame = tk.LabelFrame(
            main_frame,
            text=self.i18n.get_ui_text('attribute_change'),
            bg=Colors.BG_DARK,
            fg=Colors.ACCENT,
            font=('Arial', 10, 'bold')
        )
        changes_frame.pack(fill=tk.X, pady=10)
        
        for key, value in changes.items():
            change_label = tk.Label(
                changes_frame,
                text=f"{key}: {value:+d}",
                bg=Colors.BG_DARK,
                fg=Colors.ACCENT if value > 0 else Colors.STATUS_STAMINA
            )
            change_label.pack(anchor=tk.W, padx=10, pady=2)
        
        # Item
        if item:
            obtained_text = "✓ 获得: " if self.i18n.language == 'zh' else "✓ Obtained: "
            item_label = tk.Label(
                main_frame,
                text=f"{obtained_text}{item}",
                font=('Arial', 9, 'bold'),
                bg=Colors.BG_DARK,
                fg=Colors.ACCENT
            )
            item_label.pack(pady=10)
        
        # Continue button
        continue_text = "【 继续 】" if self.i18n.language == 'zh' else "【 Continue 】"
        continue_btn = tk.Button(
            main_frame,
            text=continue_text,
            font=('Arial', 10, 'bold'),
            bg=Colors.ACCENT,
            fg=Colors.BG_DARK,
            cursor='hand2',
            command=self.destroy
        )
        continue_btn.pack(pady=10)
    
    def _center_on_parent(self, parent):
        """Center dialog on parent window."""
        self.update_idletasks()
