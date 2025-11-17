"""
游戏UI组件 - 使用PIL合成UI到背景图像上。
Game UI components - compositing UI onto background using PIL.
"""

import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
from typing import Callable, Dict, Optional, List


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
    """Redesigned main game window (1920x1080) with composited UI."""
    
    def __init__(self, on_language_change: Optional[Callable] = None, 
                 on_tools_click: Optional[Callable] = None,
                 on_clues_click: Optional[Callable] = None,
                 on_choice_selected: Optional[Callable] = None):
        super().__init__()
        
        self.title("《审判在十五天》")
        self.geometry("1920x1080")
        self.config(bg='black')
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
        self.current_stamina = 20
        self.current_mana = 20
        
        # Main canvas to display composited image
        self.canvas = tk.Canvas(self, width=1920, height=1080, bg='black',
                               highlightthickness=0, borderwidth=0)
        self.canvas.place(x=0, y=0, width=1920, height=1080)
        
        self.bg_image_id = None
        self.bg_photo = None
        
        self._create_layout()
    
    def _create_layout(self):
        """Create layout with composited UI."""
        # RIGHT TOP - Language Button (overlay)
        self.language_button = tk.Button(
            self,
            text="语言",
            bg='#00d4ff',
            fg='#1a1a2e',
            font=('Arial', 9, 'bold'),
            command=self._on_language_click,
            relief=tk.FLAT,
            highlightthickness=0,
            width=8,
            height=2,
            bd=0
        )
        self.language_button.place(x=1850, y=15)
        
        # BOTTOM TEXT BOX
        self.text_widget = tk.Text(
            self,
            height=6,
            font=('Arial', 10),
            bg='#16213e',
            fg='#eaeaea',
            wrap=tk.WORD,
            relief=tk.FLAT,
            state=tk.DISABLED,
            borderwidth=0,
            highlightthickness=0
        )
        self.text_widget.place(x=10, y=895, width=1900, height=155)
        
        # Recall button
        self.recall_btn = tk.Button(
            self,
            text="回忆",
            bg='#4ecdc4',
            fg='white',
            font=('Arial', 8, 'bold'),
            command=self._on_recall,
            relief=tk.FLAT,
            highlightthickness=0,
            width=8,
            height=1,
            bd=0
        )
        self.recall_btn.place(x=20, y=1060)
        
        # Continue button
        self.continue_btn = tk.Button(
            self,
            text="继续",
            bg='#00d4ff',
            fg='#1a1a2e',
            font=('Arial', 8, 'bold'),
            command=self._on_continue,
            relief=tk.FLAT,
            highlightthickness=0,
            width=8,
            height=1,
            bd=0
        )
        self.continue_btn.place(x=1880, y=1060)
        
        # Choice buttons container
        self.choice_buttons_frame = None
    
    def _on_language_click(self):
        """Handle language button click."""
        if self.on_language_change:
            self.on_language_change()
    
    def _on_recall(self):
        """Handle recall button click."""
        if len(self.text_history) > 1:
            self.text_history.pop()
            self._display_text(self.text_history[-1])
    
    def _on_continue(self):
        """Handle continue button click."""
        pass
    
    def _display_text(self, text: str):
        """Display text in widget."""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete('1.0', tk.END)
        self.text_widget.insert('1.0', text)
        self.text_widget.config(state=tk.DISABLED)
    
    def _draw_progress_bar(self, draw, x: int, y: int, width: int, height: int,
                          value: int, max_val: int, color: tuple):
        """Draw progress bar using PIL."""
        # Background
        draw.rectangle([x, y, x + width, y + height], fill=(15, 52, 96), outline=None)
        
        # Progress
        if max_val > 0:
            progress_width = int(width * value / max_val)
            if progress_width > 0:
                draw.rectangle([x, y, x + progress_width, y + height], fill=color, outline=None)
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def set_background_image(self, day: int):
        """Set background image based on day with composited UI."""
        filename = f"{day} day.png"
        filepath = os.path.join(self.image_loader.root_dir, filename)
        
        try:
            # Load original image
            img = Image.open(filepath)
            orig_width, orig_height = img.size
            
            # Center crop to 1920x1080
            target_w, target_h = 1920, 1080
            left = (orig_width - target_w) // 2
            top = (orig_height - target_h) // 2
            right = left + target_w
            bottom = top + target_h
            
            left = max(0, min(left, orig_width - target_w))
            top = max(0, min(top, orig_height - target_h))
            right = min(orig_width, right)
            bottom = min(orig_height, bottom)
            
            img_cropped = img.crop((left, top, right, bottom))
            
            if img_cropped.size != (target_w, target_h):
                img_cropped = img_cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
            # Create a copy for drawing
            img_display = img_cropped.copy()
            draw = ImageDraw.Draw(img_display)
            
            # Draw left sidebar UI elements
            # Title
            draw.text((20, 15), "【属性】", fill=self._hex_to_rgb('#00d4ff'),
                     font=self._get_font(11, bold=True))
            
            # Stamina
            draw.text((20, 45), "体力值", fill=self._hex_to_rgb('#eaeaea'),
                     font=self._get_font(9, bold=True))
            
            # Stamina progress bar
            self._draw_progress_bar(draw, 20, 67, 180, 14, self.current_stamina, 50,
                                   self._hex_to_rgb('#ff6b6b'))
            
            # Stamina value
            draw.text((20, 85), f"{self.current_stamina}/50", fill=self._hex_to_rgb('#ff6b6b'),
                     font=self._get_font(8))
            
            # Mana
            draw.text((20, 107), "魔力值", fill=self._hex_to_rgb('#eaeaea'),
                     font=self._get_font(9, bold=True))
            
            # Mana progress bar
            self._draw_progress_bar(draw, 20, 129, 180, 14, self.current_mana, 50,
                                   self._hex_to_rgb('#4ecdc4'))
            
            # Mana value
            draw.text((20, 147), f"{self.current_mana}/50", fill=self._hex_to_rgb('#4ecdc4'),
                     font=self._get_font(8))
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img_display)
            
            # Delete old image
            if self.bg_image_id:
                self.canvas.delete(self.bg_image_id)
            
            # Display on canvas
            self.bg_image_id = self.canvas.create_image(0, 0, image=photo, anchor='nw')
            self.bg_photo = photo
            self.current_day = day
            
            print(f"Loaded background for day {day}")
        except Exception as e:
            print(f"Error loading background: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_font(self, size: int, bold: bool = False) -> Optional:
        """Get font object."""
        try:
            font_name = "arial.ttf" if not bold else "arialbd.ttf"
            return ImageFont.truetype(font_name, size)
        except:
            # Fallback to default
            return ImageFont.load_default()
    
    def set_narrative(self, text: str):
        """Set narrative text in text box."""
        self.text_history.append(text)
        self._display_text(text)
    
    def show_choice_buttons(self, choices: Dict[str, str]):
        """Show choice buttons in center."""
        if self.choice_buttons_frame:
            self.choice_buttons_frame.destroy()
        
        self.choice_buttons_frame = tk.Frame(self)
        self.choice_buttons_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        for choice in ['A', 'B', 'C']:
            if choice in choices:
                btn = tk.Button(
                    self.choice_buttons_frame,
                    text=f"【{choice}】\n{choices[choice]}",
                    font=('Arial', 11, 'bold'),
                    bg='#00d4ff',
                    fg='#1a1a2e',
                    wraplength=300,
                    justify=tk.CENTER,
                    padx=20,
                    pady=12,
                    relief=tk.RAISED,
                    bd=2,
                    highlightthickness=0,
                    command=lambda c=choice: self.on_choice_selected(c) if self.on_choice_selected else None,
                    width=25,
                    height=3
                )
                btn.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def hide_choice_buttons(self):
        """Hide choice buttons."""
        if self.choice_buttons_frame:
            self.choice_buttons_frame.destroy()
            self.choice_buttons_frame = None
    
    def update_properties(self, stamina: int, mana: int):
        """Update property display."""
        self.current_stamina = max(0, min(stamina, 50))
        self.current_mana = max(0, min(mana, 50))
        
        # Refresh background image to update stamina/mana display
        self.set_background_image(self.current_day)


class ToolsPopup(tk.Toplevel):
    """Popup window for displaying tools/items."""
    
    def __init__(self, parent, items: List[str]):
        super().__init__(parent)
        self.title("道具")
        self.geometry("400x300")
        self.config(bg=Colors.BG_DARK)
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        # Title
        title_label = tk.Label(self, text="【 道具清单 】", font=('Arial', 12, 'bold'),
                              bg=Colors.BG_DARK, fg=Colors.ACCENT)
        title_label.pack(pady=10)
        
        # Items frame
        items_frame = tk.Frame(self, bg=Colors.BG_MEDIUM)
        items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        if items:
            for item in items:
                item_label = tk.Label(items_frame, text=f"• {item}", font=('Arial', 11),
                                     bg=Colors.BG_MEDIUM, fg=Colors.TEXT_PRIMARY, justify=tk.LEFT)
                item_label.pack(anchor=tk.W, pady=5, padx=10)
        else:
            empty_label = tk.Label(items_frame, text="没有道具", font=('Arial', 11),
                                  bg=Colors.BG_MEDIUM, fg=Colors.TEXT_SECONDARY)
            empty_label.pack(expand=True)
        
        # Close button
        close_btn = tk.Button(self, text="关闭", bg=Colors.ACCENT, fg=Colors.BG_DARK,
                             font=('Arial', 10, 'bold'), command=self.destroy, relief=tk.FLAT)
        close_btn.pack(pady=10)
