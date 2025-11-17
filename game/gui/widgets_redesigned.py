"""
完全重新设计的游戏 UI 组件。
背景图片占满整个1920x1080，所有UI元素叠加在图片上。
"""

import tkinter as tk
from PIL import Image, ImageTk
import os
from typing import Callable, Dict, Optional, List


class Colors:
    """Color scheme."""
    BG_DARK = '#1a1a2e'
    BG_MEDIUM = '#16213e'
    TEXT_PRIMARY = '#eaeaea'
    ACCENT = '#00d4ff'
    STATUS_STAMINA = '#ff6b6b'
    STATUS_MANA = '#4ecdc4'


class ImageLoader:
    """Utility class to load and manage images."""
    
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.cache = {}
    
    def load_image(self, filename: str, size: tuple = None) -> Optional[ImageTk.PhotoImage]:
        """Load and cache images."""
        cache_key = f"{filename}_{size}" if size else filename
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        filepath = os.path.join(self.root_dir, filename)
        try:
            img = Image.open(filepath)
            if size:
                img = img.resize(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.cache[cache_key] = photo
            return photo
        except Exception as e:
            print(f"Error loading image {filename}: {e}")
            return None


class GameWindowRedesigned(tk.Tk):
    """Redesigned main game window (1920x1080) with background image filling entire screen."""
    
    def __init__(self, on_language_change: Optional[Callable] = None, 
                 on_tools_click: Optional[Callable] = None,
                 on_clues_click: Optional[Callable] = None,
                 on_choice_selected: Optional[Callable] = None):
        super().__init__()
        
        self.title("《审判在十五天》")
        # Compute window size to fit the screen while preserving 16:9 ratio
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        # Target ratio 16:9
        target_ratio = 16 / 9
        # Fit by width or height
        if screen_w / target_ratio <= screen_h:
            win_w = int(screen_w * 0.95)  # leave small margin
            win_h = int(win_w / target_ratio)
        else:
            win_h = int(screen_h * 0.95)
            win_w = int(win_h * target_ratio)

        # Center the window
        x_off = max(0, (screen_w - win_w) // 2)
        y_off = max(0, (screen_h - win_h) // 2)
        self.win_width = win_w
        self.win_height = win_h
        self.geometry(f"{self.win_width}x{self.win_height}+{x_off}+{y_off}")
        self.resizable(False, False)
        
        self.on_language_change = on_language_change
        self.on_tools_click = on_tools_click
        self.on_clues_click = on_clues_click
        self.on_choice_selected = on_choice_selected
        
        # Image loader
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.image_loader = ImageLoader(root_dir)
        
        self.current_day = 1
        self.current_language = 'zh'
        self.text_history = []
        
        # Background Label - fills entire window with image (will scale image to window)
        self.bg_label = tk.Label(self, bg='black')
        self.bg_label.place(x=0, y=0, width=self.win_width, height=self.win_height)
        self.bg_photo = None
        
        # Create UI on top
        self._create_layout()
    
    def set_background_image(self, day: int):
        """Set background image for the specified day."""
        self.current_day = day
        filename = f"{day} day.png"
        print(f"Loading background for day {day}: {filename}")
        
        # Load and resize image to the current window size
        try:
            bg_image = self.image_loader.load_image(filename, size=(self.win_width, self.win_height))
        except Exception:
            bg_image = None

        if bg_image:
            self.bg_photo = bg_image
            # Set image on background label
            self.bg_label.config(image=self.bg_photo)
            self.bg_label.image = self.bg_photo
            print(f"Background image loaded successfully: {self.win_width}x{self.win_height}")
        else:
            print(f"Failed to load background image: {filename}")
    
    def _create_layout(self):
        """Create all UI layout on top of background image using proportional placement."""
        # Create widgets (placement will be computed by ratio)
        self._create_left_panel()
        self._create_language_button()
        self._create_bottom_panel()

        # CENTER - Choice buttons (hidden initially)
        self.choice_buttons_frame = None

        # Position elements according to ratios of the current window
        self._layout_elements_by_ratio()
    
    def _create_left_panel(self):
        """Create left sidebar widgets (positions computed later by ratio)."""
        # Create elements without hard-coded placement
        self.left_title = tk.Label(self, text="【属性】", font=('Arial', 13, 'bold'), fg='#00d4ff', bg='black')

        self.stamina_title = tk.Label(self, text="体力值", font=('Arial', 10, 'bold'), fg='#eaeaea', bg='black')
        self.stamina_progress = tk.Canvas(self, width=1, height=1, bg='#16213e', highlightthickness=0, borderwidth=0)
        self.stamina_label = tk.Label(self, text="20/50", font=('Arial', 9), fg='#ff6b6b', bg='black')

        self.mana_title = tk.Label(self, text="魔力值", font=('Arial', 10, 'bold'), fg='#eaeaea', bg='black')
        self.mana_progress = tk.Canvas(self, width=1, height=1, bg='#16213e', highlightthickness=0, borderwidth=0)
        self.mana_label = tk.Label(self, text="20/50", font=('Arial', 9), fg='#4ecdc4', bg='black')

        clues_img = self.image_loader.load_image("button for clues.png", size=(150, 50))
        if clues_img:
            self.clues_btn = tk.Button(self, image=clues_img, command=lambda: self._on_clues_click() if self.on_clues_click else None, relief=tk.FLAT, bd=0, bg='black', activebackground='black')
            self.clues_btn.image = clues_img
            self.clues_text = tk.Label(self, text="线索", font=('Arial', 12, 'bold'), fg='white', bg='black')
    
    def _create_language_button(self):
        """Create language switch button (top right)."""
        lang_img = self.image_loader.load_image("languege change.png", size=(80, 50))
        if lang_img:
            self.lang_btn = tk.Button(self, image=lang_img, command=self._on_language_click, relief=tk.FLAT, bd=0, bg='black', activebackground='black')
            self.lang_btn.image = lang_img
            self.lang_text_label = tk.Label(self, text=("语言" if self.current_language == 'zh' else "Lang"), font=('Arial', 10, 'bold'), fg='white', bg='black')
    
    def _create_bottom_panel(self):
        """Create bottom panel with text box and buttons (placement by ratio later)."""
        # Create background label placeholder for text box; actual image will be resized to window width
        text_bg_img = self.image_loader.load_image("Text box.png", size=(int(self.win_width * 0.95), int(self.win_height * 0.09)))
        if text_bg_img:
            self.text_bg_label = tk.Label(self, image=text_bg_img, bg='black')
            self.text_bg_label.image = text_bg_img

        # Text display area (placed later)
        self.text_widget = tk.Text(self, width=110, height=5, font=('Arial', 11), fg='white', bg='#1a1a2e', relief=tk.FLAT, borderwidth=0, highlightthickness=0, wrap=tk.WORD)
        
        # Recall and Continue buttons (images loaded; placement later)
        recall_img = self.image_loader.load_image("recall.png", size=(int(self.win_width * 0.05), int(self.win_height * 0.05)))
        if recall_img:
            self.recall_btn = tk.Button(self, image=recall_img, command=self._on_recall, bd=0, bg='black', activebackground='black')
            self.recall_btn.image = recall_img

        continue_img = self.image_loader.load_image("continue.png", size=(int(self.win_width * 0.05), int(self.win_height * 0.05)))
        if continue_img:
            self.continue_btn = tk.Button(self, image=continue_img, command=self._on_continue, bd=0, bg='black', activebackground='black')
            self.continue_btn.image = continue_img

    def _layout_elements_by_ratio(self):
        """Place UI elements using ratios so they always sit within the background image bounds."""
        w = self.win_width
        h = self.win_height

        # Left column horizontal position between 1/20 and 3/20 -> use 2/20 (0.10)
        left_x = int(w * 0.10)
        top_margin = int(h * 0.02)
        # vertical spacing
        small_gap = int(h * 0.025)

        # Place left elements vertically
        self.left_title.place(x=left_x, y=top_margin)
        y_pos = top_margin + int(h * 0.05)

        self.stamina_title.place(x=left_x, y=y_pos)
        y_pos += small_gap
        self.stamina_progress.place(x=left_x, y=y_pos, width=int(w * 0.12), height=int(h * 0.02))
        y_pos += small_gap
        self.stamina_label.place(x=left_x, y=y_pos)
        y_pos += small_gap

        self.mana_title.place(x=left_x, y=y_pos)
        y_pos += small_gap
        self.mana_progress.place(x=left_x, y=y_pos, width=int(w * 0.12), height=int(h * 0.02))
        y_pos += small_gap
        self.mana_label.place(x=left_x, y=y_pos)
        y_pos += int(h * 0.05)

        # Clues button placement
        if hasattr(self, 'clues_btn'):
            btn_w = int(w * 0.08)
            btn_h = int(h * 0.06)
            self.clues_btn.place(x=left_x, y=y_pos, width=btn_w, height=btn_h)
            if hasattr(self, 'clues_text'):
                # center the text over button
                self.clues_text.place(x=left_x + btn_w // 2 - 20, y=y_pos + btn_h // 2 - 10)

        # Right-side language button: near right edge at 0.90 of width
        right_x = int(w * 0.90)
        lang_w = int(w * 0.06)
        lang_h = int(h * 0.06)
        if hasattr(self, 'lang_btn'):
            self.lang_btn.place(x=right_x, y=top_margin, width=lang_w, height=lang_h)
            if hasattr(self, 'lang_text_label'):
                self.lang_text_label.place(x=right_x + lang_w // 2 - 20, y=top_margin + lang_h // 2 - 10)

        # Bottom text box: occupy most width and sit at bottom
        text_h = int(h * 0.12)
        text_w = int(w * 0.95)
        text_x = int(w * 0.025)
        text_y = h - text_h - int(h * 0.02)
        if hasattr(self, 'text_bg_label'):
            self.text_bg_label.place(x=text_x, y=text_y, width=text_w, height=text_h)
        self.text_widget.place(x=text_x + int(w * 0.01), y=text_y + int(h * 0.01), width=text_w - int(w * 0.02), height=text_h - int(h * 0.02))

        # Recall and Continue buttons at bottom corners (just outside text box)
        if hasattr(self, 'recall_btn'):
            recall_w = int(w * 0.06)
            recall_h = int(h * 0.06)
            self.recall_btn.place(x=text_x, y=text_y + text_h + int(h * 0.01), width=recall_w, height=recall_h)
        if hasattr(self, 'continue_btn'):
            cont_w = int(w * 0.06)
            cont_h = int(h * 0.06)
            self.continue_btn.place(x=w - cont_w - text_x, y=text_y + text_h + int(h * 0.01), width=cont_w, height=cont_h)
    
    def display_choices(self, choices: Dict[str, str]):
        """Display choice buttons in center of screen."""
        if self.choice_buttons_frame:
            self.choice_buttons_frame.destroy()
        
        # Create frame for choice buttons
        self.choice_buttons_frame = tk.Frame(self, bg='black', highlightthickness=0)
        self.choice_buttons_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Load button image
        btn_img = self.image_loader.load_image("ABC.png", size=(400, 80))
        
        for choice in ['A', 'B', 'C']:
            if choice in choices:
                # Create button with image
                if btn_img:
                    choice_btn = tk.Button(
                        self.choice_buttons_frame,
                        image=btn_img,
                        command=lambda c=choice: self._on_choice_selected(c),
                        relief=tk.FLAT,
                        highlightthickness=0,
                        bd=0,
                        bg='black',
                        activebackground='black'
                    )
                    choice_btn.image = btn_img
                    choice_btn.pack(pady=5)
                    
                    # Add text overlay with choice and description
                    choice_text = f"【{choice}】 {choices[choice]}"
                    text_label = tk.Label(
                        self.choice_buttons_frame,
                        text=choice_text,
                        font=('Arial', 11),
                        fg='white',
                        bg='black',
                        wraplength=350
                    )
                    text_label.pack()
    
    def display_text(self, text: str):
        """Display text in the text widget."""
        self.text_history.append(text)
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete('1.0', tk.END)
        self.text_widget.insert('1.0', text)
        self.text_widget.config(state=tk.DISABLED)
    
    def set_narrative(self, text: str):
        """Set narrative text (alias for display_text)."""
        self.display_text(text)
    
    def show_choice_buttons(self, choices: Dict[str, str]):
        """Show choice buttons (alias for display_choices)."""
        self.display_choices(choices)
    
    def hide_choice_buttons(self):
        """Hide choice buttons."""
        if self.choice_buttons_frame:
            self.choice_buttons_frame.destroy()
            self.choice_buttons_frame = None
    
    def update_properties(self, stamina: int, mana: int = None, max_stamina: int = 100, max_mana: int = 100):
        """Update stamina and mana display."""
        # Handle default values
        if mana is None:
            mana = stamina
        
        # Update text
        self.stamina_label.config(text=f"{stamina}/{max_stamina}")
        self.mana_label.config(text=f"{mana}/{max_mana}")
        
        # Update progress bars
        progress_width = 190
        
        # Stamina progress
        stamina_ratio = stamina / max_stamina if max_stamina > 0 else 0
        stamina_fill_width = int(progress_width * stamina_ratio)
        
        # Clear and redraw stamina progress
        self.stamina_progress.delete('all')
        self.stamina_progress.create_rectangle(0, 0, stamina_fill_width, 16,
                                             fill='#ff6b6b', outline='')
        
        # Mana progress
        mana_ratio = mana / max_mana if max_mana > 0 else 0
        mana_fill_width = int(progress_width * mana_ratio)
        
        # Clear and redraw mana progress
        self.mana_progress.delete('all')
        self.mana_progress.create_rectangle(0, 0, mana_fill_width, 16,
                                          fill='#4ecdc4', outline='')
    
    def _on_language_click(self):
        """Handle language button click."""
        if self.on_language_change:
            self.on_language_change()
    
    def _on_recall(self):
        """Handle recall button click."""
        if len(self.text_history) > 1:
            self.text_history.pop()
            previous_text = self.text_history[-1]
            self.display_text(previous_text)
    
    def _on_continue(self):
        """Handle continue button click (placeholder)."""
        pass
    
    def _on_clues_click(self):
        """Handle clues button click."""
        if self.on_clues_click:
            self.on_clues_click()
    
    def _on_choice_selected(self, choice: str):
        """Handle choice button click."""
        if self.on_choice_selected:
            self.on_choice_selected(choice)


class ToolsPopup:
    """Tools/items popup in center of screen."""
    
    def __init__(self, parent: tk.Tk, items: List[str]):
        self.parent = parent
        self.items = items
        self.popup = None
        self.create_popup()
    
    def create_popup(self):
        """Create popup window for tools/items."""
        self.popup = tk.Toplevel(self.parent)
        self.popup.title("工具")
        self.popup.geometry("400x300")
        self.popup.transient(self.parent)
        self.popup.grab_set()
        
        # Title
        title = tk.Label(self.popup, text="工具", font=('Arial', 14, 'bold'),
                        fg='#00d4ff')
        title.pack(pady=10)
        
        # Items list
        for item in self.items:
            item_label = tk.Label(self.popup, text=f"• {item}", font=('Arial', 11),
                                 fg='white', bg='#1a1a2e')
            item_label.pack(anchor='w', padx=20, pady=5)
        
        # Close button
        close_btn = tk.Button(self.popup, text="关闭", command=self.popup.destroy,
                             font=('Arial', 11), bg='#16213e', fg='white')
        close_btn.pack(pady=20)
    
    def destroy(self):
        """Destroy the popup."""
        if self.popup:
            self.popup.destroy()
