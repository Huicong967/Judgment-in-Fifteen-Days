import tkinter as tk
from tkinter import font as tkfont
from tkinter import simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import re
from typing import Optional

from game.levels.csv_level import get_special_text, LevelFromCSV
from game.manager import LevelManager
from game.state import GameState
from game.csv_text_loader import CSVTextLoader
from game.audio_manager import AudioManager


def number_to_chinese(num):
    """Convert number to Chinese characters (1-15)."""
    chinese_nums = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                    '十一', '十二', '十三', '十四', '十五']
    if 1 <= num <= 15:
        return chinese_nums[num]
    return str(num)


def show_language_selection_dialog():
    """Show language selection dialog before starting the game."""
    dialog = tk.Tk()
    dialog.title("Language / 语言")
    dialog.geometry("400x200")
    dialog.resizable(False, False)
    
    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
    y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")
    
    selected_language = {"lang": "中文"}  # Default to Chinese
    
    # Title label
    title_font = tkfont.Font(family="微软雅黑", size=16, weight="bold")
    title_label = tk.Label(dialog, text="Please Select Language\n请选择语言", 
                          font=title_font, pady=20)
    title_label.pack()
    
    # Button frame
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=10)
    
    button_font = tkfont.Font(family="微软雅黑", size=14)
    
    def select_chinese():
        selected_language["lang"] = "中文"
        dialog.destroy()
    
    def select_english():
        selected_language["lang"] = "English"
        dialog.destroy()
    
    # Chinese button
    cn_button = tk.Button(button_frame, text="中文", font=button_font,
                         width=12, height=2, command=select_chinese)
    cn_button.pack(side=tk.LEFT, padx=10)
    
    # English button
    en_button = tk.Button(button_frame, text="English", font=button_font,
                         width=12, height=2, command=select_english)
    en_button.pack(side=tk.LEFT, padx=10)
    
    dialog.mainloop()
    
    return selected_language["lang"]


class GUIGameRunnerRedesigned:
    def __init__(self, manager: LevelManager, window: tk.Tk, initial_language='中文', on_language_change=None, on_game_over=None):
        self.manager = manager
        self.window = window
        self.on_language_change_callback = on_language_change
        self.on_game_over_callback = on_game_over
        
        # Language setting - use parameter instead of environment variable
        self.current_language = initial_language
        
        # CSV text loader
        self.csv_loader = CSVTextLoader(language=self.current_language)
        
        # Audio manager
        self.audio_manager = AudioManager()
        
        # Initialize scale and dimensions
        self.scale = 1.0
        self.display_width = 1920
        self.display_height = 1080
        
        self.canvas = None
        self.bg_image = None
        self.bg_photo = None
        self.dialog_box_photo = None
        # Fullscreen state flag
        self.is_fullscreen = False
        self._prev_geometry = None
        self._prev_overrideredirect = False
        # Debug flag to print fullscreen scaling info
        self.debug_fullscreen = True
        
        # Text display state
        self.current_text_sentences = []  # List of sentences
        self.current_sentence_index = 0
        self.text_display_mode = None  # 'narrative', 'result', or None
        self.pending_choice_result = None  # Store result text after choice
        
        # Navigation buttons
        self.left_button = None
        self.right_button = None
        self.left_btn_photo = None
        self.right_btn_photo = None
        
        # Button images
        self.tools_btn_photo = None
        self.clues_btn_photo = None
        self.lang_btn_photo = None
        self.choice_btn_photos = []  # For A, B, C buttons
        
        # UI elements
        self.day_text_id = None
        self.narrative_text = None
        self.choice_buttons = []
        
        # Status text IDs (canvas text items)
        self.stamina_text_id = None
        self.mana_text_id = None
        self.bribe_text_id = None
        self.sabotage_text_id = None
        self.legal_text_id = None
        self.mystery_text_id = None
        
        # Tools and clues buttons
        self.tools_button = None
        self.clues_button = None
        
        # Action buttons
        self.recall_button = None
        self.continue_button = None
        
        # Language button
        self.lang_button = None
        
        # Story background modal tracking
        self.story_modal = None
        self.story_modal_open = False
        
        # Result popup elements
        self.result_popup = None
        self.result_label = None
        # Bind resize event
        self.window.bind('<Configure>', self._on_window_resize)
        # Fullscreen toggle: F11 to toggle, Esc to exit
        self.window.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.window.bind('<Escape>', lambda e: self.exit_fullscreen())
        
        # Setup UI
        self._setup_ui()
    
    def cleanup(self):
        """Clean up resources when game ends."""
        if hasattr(self, 'audio_manager'):
            self.audio_manager.cleanup()
    
    def _play_click_sound(self):
        """Play click sound effect."""
        if hasattr(self, 'audio_manager'):
            self.audio_manager.play_click()
    
    def _wrap_with_click_sound(self, callback):
        """Wrap a callback function to play click sound before execution.
        
        Args:
            callback: The original callback function
            
        Returns:
            A new function that plays click sound then calls the callback
        """
        def wrapped(*args, **kwargs):
            self._play_click_sound()
            if callback:
                return callback(*args, **kwargs)
        return wrapped
    
    def _create_button_image(self, image_path: str, text: str, scale_factor: float = 1.0, button_type: str = "normal") -> ImageTk.PhotoImage:
        """Create a button image with text overlay.
        
        Args:
            image_path: Path to button background image
            text: Text to display on button
            scale_factor: Scale factor for button size
            button_type: Type of button ('normal', 'tools', 'clues') for different font sizes
        """
        if not os.path.exists(image_path):
            # Fallback: create a simple colored button
            img = Image.new('RGBA', (200, 60), color=(100, 100, 100, 255))
        else:
            img = Image.open(image_path).convert('RGBA')
        
        # Scale button image (apply both self.scale and scale_factor)
        scaled_width = int(img.width * self.scale * scale_factor)
        scaled_height = int(img.height * self.scale * scale_factor)
        img = img.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
        
        # Add text overlay
        draw = ImageDraw.Draw(img)
        
        # Try to use a nice font, fallback to default
        try:
            # Adjust font size based on button type
            if button_type in ["tools", "clues"]:
                font_size = int(19 * self.scale)  # Smaller by 1 for tools/clues buttons
            else:
                font_size = int(20 * self.scale)  # Normal size for other buttons
            font = ImageFont.truetype("msyh.ttc", font_size)  # Microsoft YaHei
        except:
            try:
                if button_type in ["tools", "clues"]:
                    font = ImageFont.truetype("arial.ttf", int(17 * self.scale))
                else:
                    font = ImageFont.truetype("arial.ttf", int(18 * self.scale))
            except:
                font = ImageFont.load_default()
        
        # Calculate text position (center)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (scaled_width - text_width) // 2
        y = (scaled_height - text_height) // 2
        
        # Draw text with shadow for better visibility
        draw.text((x+1, y+1), text, font=font, fill=(0, 0, 0, 200))  # Shadow
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))  # Text
        
        return ImageTk.PhotoImage(img)
    
    def _calculate_scale(self):
        """Calculate appropriate scale based on current window size."""
        # Get current window dimensions
        self.window.update_idletasks()
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        # If the window is fullscreen, prefer the screen resolution to avoid stale widget sizes
        try:
            is_fs = bool(self.window.attributes('-fullscreen')) or self.is_fullscreen
        except Exception:
            is_fs = self.is_fullscreen
        if is_fs:
            try:
                window_width = self.window.winfo_screenwidth()
                window_height = self.window.winfo_screenheight()
            except Exception:
                pass
        
        # If window is too small (initial state), use reduced default size
        if window_width < 100 or window_height < 100:
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            # Use 45% of screen size and reserve more space for taskbar
            window_width = int(screen_width * 0.45)
            window_height = int(screen_height * 0.45)
        
        # Calculate scaling to fit window while maintaining aspect ratio
        target_width = 1920
        target_height = 1080
        width_scale = window_width / target_width
        height_scale = window_height / target_height
        self.scale = min(width_scale, height_scale)
        
        # Set display size to actual window (or screen when fullscreen) to ensure cover/fill works
        self.display_width = int(window_width)
        self.display_height = int(window_height)
        
        if self.debug_fullscreen:
            print(f"[DEBUG] _calculate_scale: is_fs={is_fs} window=({window_width},{window_height}) display=({self.display_width},{self.display_height}) scale={self.scale:.3f}")
    
    def _on_window_resize(self, event):
        """Handle window resize event."""
        # Only handle resize for the main window, not child widgets
        if event.widget != self.window:
            return
        
        # Recalculate scale
        old_scale = self.scale
        self._calculate_scale()
        
        # Only rebuild UI if scale changed significantly
        if abs(old_scale - self.scale) > 0.05:
            self._rebuild_ui()
    
    def _rebuild_ui(self):
        """Rebuild the entire UI with new scale."""
        if not self.canvas:
            return
        
        if self.debug_fullscreen:
            print(f"[DEBUG] _rebuild_ui: canvas will be resized to ({self.display_width},{self.display_height})")
        
        # Save current text display state before rebuilding
        saved_sentence_index = self.current_sentence_index
        saved_text_mode = self.text_display_mode
        saved_sentences = self.current_text_sentences.copy() if self.current_text_sentences else []
        
        if self.debug_fullscreen:
            print(f"[DEBUG] _rebuild_ui: Saved state - mode={saved_text_mode}, sentence_index={saved_sentence_index}/{len(saved_sentences)}")
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Resize canvas
        self.canvas.config(width=self.display_width, height=self.display_height)
        
        # Recreate button images with new scale
        tools_text = "道具" if self.current_language == "中文" else "Tools"
        clues_text = "线索" if self.current_language == "中文" else "Clues"
        lang_text = "English" if self.current_language == "中文" else "中文"
        self.tools_btn_photo = self._create_button_image("button for tools.png", tools_text, scale_factor=0.25)
        self.clues_btn_photo = self._create_button_image("button for clues.png", clues_text, scale_factor=0.25)
        self.lang_btn_photo = self._create_button_image("language change.png", lang_text, scale_factor=0.25)
        
        # Recreate choice button images
        self.choice_btn_photos = []
        for label in ["A", "B", "C"]:
            choice_photo = self._create_button_image("option.png", label, scale_factor=0.5)
            self.choice_btn_photos.append(choice_photo)
        
        # Reload background for current day
        # Recalculate and load background; if currently fullscreen use cover mode
        self._calculate_scale()
        self._load_background_for_day(self.manager.current_day)
        
        # Recreate all UI elements
        self._create_ui_elements()
        
        # Refresh current level display - but NOT for special modes
        # Special modes (transition, death_ending_final) will be restored by the caller
        if saved_text_mode in ['transition', 'death_ending_final']:
            # Don't call show_current_level() for special modes
            # Just restore the saved state
            if saved_sentences and saved_text_mode:
                self.current_text_sentences = saved_sentences
                self.current_sentence_index = saved_sentence_index
                self.text_display_mode = saved_text_mode
                
                if self.debug_fullscreen:
                    print(f"[DEBUG] _rebuild_ui: Special mode {saved_text_mode}, not calling show_current_level()")
        elif self.manager.get_current_level():
            self.show_current_level()
            
            # Restore saved text display state
            if saved_sentences and saved_text_mode:
                self.current_text_sentences = saved_sentences
                self.current_sentence_index = saved_sentence_index
                self.text_display_mode = saved_text_mode
                
                if self.debug_fullscreen:
                    print(f"[DEBUG] _rebuild_ui: Restoring state - mode={saved_text_mode}, sentence_index={saved_sentence_index}")
                
                # Redisplay current sentence (unless in choices mode where text should be empty)
                if saved_text_mode != 'choices':
                    self._update_text_display()
                else:
                    # In choices mode, clear text and show buttons
                    if self.debug_fullscreen:
                        print(f"[DEBUG] _rebuild_ui: Restoring choices mode")
                    self.canvas.itemconfig(self.narrative_canvas_text, text="")
                    # Show choice buttons
                    current_day = self.manager.current_day
                    options_dict = self.csv_loader.get_options(current_day)
                    for i, (choice_key, btn) in enumerate(zip(['A', 'B', 'C'], self.choice_buttons)):
                        option_text = options_dict.get(choice_key, choice_key)
                        btn.config(text=option_text, state=tk.NORMAL)
                        if hasattr(self, 'choice_button_windows') and i < len(self.choice_button_windows):
                            win_id = self.choice_button_windows[i]
                            self.canvas.itemconfig(win_id, state='normal')
                            self.canvas.tag_raise(win_id)
    
    def _load_background_for_day(self, day: int):
        """Load the background image for the specified day."""
        # Load day background
        bg_path = f"Day {day}.PNG"
        if os.path.exists(bg_path):
            img = Image.open(bg_path).convert('RGBA')
            img_w, img_h = img.size
            if img_w == 0 or img_h == 0:
                self.bg_photo = ImageTk.PhotoImage(Image.new('RGB', (self.display_width, self.display_height), color='black'))
                return

            # If fullscreen (or is_fullscreen flag), scale to COVER (no black bars) and crop center
            # Always use cover mode - fill entire screen
            cover_scale = max(self.display_width / img_w, self.display_height / img_h)
            cover_w = max(1, int(img_w * cover_scale))
            cover_h = max(1, int(img_h * cover_scale))
            resized = img.resize((cover_w, cover_h), Image.Resampling.LANCZOS)

            # Crop center to display size
            left = (cover_w - self.display_width) // 2
            top = (cover_h - self.display_height) // 2
            right = left + self.display_width
            bottom = top + self.display_height
            cropped = resized.crop((left, top, right, bottom))

            bg_rgb = cropped.convert('RGB')
            self.bg_photo = ImageTk.PhotoImage(bg_rgb)
            if self.debug_fullscreen:
                print(f"[DEBUG] COVER MODE: display=({self.display_width},{self.display_height}) img=({img_w},{img_h}) cover_scale={cover_scale:.3f} cover=({cover_w},{cover_h}) crop=({left},{top},{right},{bottom})")
        else:
            # Fallback to solid color if image not found
            bg_image = Image.new('RGB', (self.display_width, self.display_height), color='black')
            self.bg_photo = ImageTk.PhotoImage(bg_image)
        
        # Update canvas background
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.delete("background")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_photo, tags="background")
            self.canvas.tag_lower("background")
        
        # Load and display DialogBox at the bottom
        dialog_box_path = "DialogBox.png"
        if os.path.exists(dialog_box_path):
            dialog_box = Image.open(dialog_box_path)
            # Scale DialogBox proportionally
            box_width = int(dialog_box.width * self.scale)
            box_height = int(dialog_box.height * self.scale)
            dialog_box = dialog_box.resize((box_width, box_height), Image.Resampling.LANCZOS)
            self.dialog_box_photo = ImageTk.PhotoImage(dialog_box)
            
            # Position at bottom of the screen
            if hasattr(self, 'canvas') and self.canvas:
                self.canvas.delete("dialogbox")
                # Center horizontally, place at bottom
                x = self.display_width // 2
                y = self.display_height - (box_height // 2)
                self.canvas.create_image(x, y, image=self.dialog_box_photo, tags="dialogbox")
                # Ensure text is above dialogbox
                if hasattr(self, 'narrative_canvas_text'):
                    self.canvas.tag_raise(self.narrative_canvas_text)
                if hasattr(self, 'left_button_id'):
                    self.canvas.tag_raise(self.left_button_id)
                if hasattr(self, 'right_button_id'):
                    self.canvas.tag_raise(self.right_button_id)
    
    def _setup_ui(self):
        """Set up the main game UI."""
        # Start in fullscreen borderless mode by default
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        
        self.display_width = screen_w
        self.display_height = screen_h
        self.is_fullscreen = True
        
        # Set borderless fullscreen
        self.window.overrideredirect(True)
        self.window.geometry(f"{screen_w}x{screen_h}+0+0")
        
        # Create canvas for background at full screen size
        self.canvas = tk.Canvas(self.window, width=screen_w, height=screen_h, 
                                highlightthickness=0, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Calculate scale based on screen size
        target_width = 1920
        target_height = 1080
        width_scale = screen_w / target_width
        height_scale = screen_h / target_height
        self.scale = min(width_scale, height_scale)
        
        # Set topmost
        try:
            self.window.attributes('-topmost', True)
        except Exception:
            pass
        
        # Load initial background (will be updated per day)
        self._load_background_for_day(1)
        
        # Create UI overlay elements
        self._create_ui_elements()
        
        # Force text elements to top after initial setup
        self.window.after(100, self._ensure_text_visible)
    
    def _create_ui_elements(self):
        """Create all UI elements on canvas."""
        # Scale factor for positioning
        s = self.scale
        
        # Status display at top-left
        status_x = int(50 * s)
        status_y_start = int(30 * s)
        
        state = self.manager.state
        
        # Stamina label (using canvas text for transparent background)
        stamina_text = (f"体力值: {state.stamina}/{state.max_stamina}" if self.current_language == "中文" 
                       else f"Stamina: {state.stamina}/{state.max_stamina}")
        self.stamina_text_id = self.canvas.create_text(
            status_x,
            status_y_start,
            text=stamina_text,
            font=tkfont.Font(family="微软雅黑", size=int(18 * s), weight="bold"),
            fill="white",
            anchor=tk.W
        )
        
        # Mana label (using canvas text for transparent background)
        mana_text = (f"魔力值: {state.mana}/{state.max_mana}" if self.current_language == "中文" 
                    else f"Mana: {state.mana}/{state.max_mana}")
        self.mana_text_id = self.canvas.create_text(
            status_x,
            status_y_start + int(35 * s),
            text=mana_text,
            font=tkfont.Font(family="微软雅黑", size=int(18 * s), weight="bold"),
            fill="white",
            anchor=tk.W
        )
        
        # Progress labels (using canvas text for transparent background)
        progress_y = status_y_start + int(70 * s)
        
        bribe_text = f"贿赂: {state.bribe_progress}" if self.current_language == "中文" else f"Bribe: {state.bribe_progress}"
        self.bribe_text_id = self.canvas.create_text(
            status_x,
            progress_y,
            text=bribe_text,
            font=tkfont.Font(family="微软雅黑", size=int(18 * s), weight="bold"),
            fill="white",
            anchor=tk.W
        )
        
        sabotage_text = f"破坏: {state.sabotage_progress}" if self.current_language == "中文" else f"Sabotage: {state.sabotage_progress}"
        self.sabotage_text_id = self.canvas.create_text(
            status_x,
            progress_y + int(35 * s),
            text=sabotage_text,
            font=tkfont.Font(family="微软雅黑", size=int(18 * s), weight="bold"),
            fill="white",
            anchor=tk.W
        )
        
        legal_text = f"法学: {state.legal_progress}" if self.current_language == "中文" else f"Legal: {state.legal_progress}"
        self.legal_text_id = self.canvas.create_text(
            status_x,
            progress_y + int(70 * s),
            text=legal_text,
            font=tkfont.Font(family="微软雅黑", size=int(18 * s), weight="bold"),
            fill="white",
            anchor=tk.W
        )
        
        # Mystery progress (?) - only show when mystery_progress >= 1
        show_mystery = state.mystery_progress >= 1
        mystery_text = f"?: {state.mystery_progress}" if self.current_language == "中文" else f"?: {state.mystery_progress}"
        self.mystery_text_id = self.canvas.create_text(
            status_x,
            progress_y + int(105 * s),
            text=mystery_text if show_mystery else "",
            font=tkfont.Font(family="微软雅黑", size=int(18 * s), weight="bold"),
            fill="white",
            anchor=tk.W
        )
        
        # Tools and Clues buttons below progress (vertical layout)
        button_start_y = progress_y + int(165 * s)
        button_spacing_y = int(80 * s)
        
        # Create button images with text (1/4 size)
        tools_text = "道具" if self.current_language == "中文" else "Tools"
        clues_text = "线索" if self.current_language == "中文" else "Clues"
        
        # Scale buttons to 1/4 of original size
        self.tools_btn_photo = self._create_button_image("button for tools.png", tools_text, scale_factor=0.25, button_type="tools")
        self.clues_btn_photo = self._create_button_image("button for clues.png", clues_text, scale_factor=0.25, button_type="clues")
        
        # Tools button
        self.tools_button = tk.Button(
            self.window,
            image=self.tools_btn_photo,
            command=self._wrap_with_click_sound(self.show_tools),
            borderwidth=0,
            highlightthickness=0,
            bg="black",
            activebackground="black"
        )
        self.canvas.create_window(status_x, button_start_y, anchor=tk.W, window=self.tools_button)
        
        # Clues button
        self.clues_button = tk.Button(
            self.window,
            image=self.clues_btn_photo,
            command=self._wrap_with_click_sound(self.show_clues),
            borderwidth=0,
            highlightthickness=0,
            bg="black",
            activebackground="black"
        )
        self.canvas.create_window(status_x, button_start_y + button_spacing_y, anchor=tk.W, window=self.clues_button)
        
        # Day label at top-center (using canvas text for transparent background)
        self.day_text_id = self.canvas.create_text(
            self.display_width // 2,
            int(30 * s),
            text="",
            font=tkfont.Font(family="微软雅黑", size=int(24 * s), weight="bold"),
            fill="white",
            anchor=tk.N
        )
        
        # Language button at top-right
        lang_text = "English" if self.current_language == "中文" else "中文"
        self.lang_btn_photo = self._create_button_image("language change.png", lang_text, scale_factor=0.4)
        
        self.lang_button = tk.Button(
            self.window,
            image=self.lang_btn_photo,
            command=self._wrap_with_click_sound(self.toggle_language),
            borderwidth=0,
            highlightthickness=0,
            bg="black",
            activebackground="black"
        )
        self.canvas.create_window(self.display_width - int(40 * s), int(30 * s), window=self.lang_button)
        
        # Narrative text area in DialogBox (bottom area) - use canvas text instead of Text widget
        text_y = self.display_height - int(200 * s)
        
        # Create canvas text for narrative (no white background)
        self.narrative_canvas_text = self.canvas.create_text(
            self.display_width // 2,
            text_y + int(20 * s),
            text="",
            font=tkfont.Font(family="微软雅黑", size=int(16 * s)),
            fill="white",
            width=int(self.display_width * 0.6),
            justify=tk.LEFT,
            anchor=tk.N
        )
        
        # Choice buttons (ABC) above text box - vertically stacked
        # 再次上移 ABC 组：将偏移从 480 增加到 560，整体往上移动更多
        choice_start_y = text_y - int(560 * s)
        choice_spacing_y = int(130 * s)
        
        # Clear old button windows list and create new ones
        self.choice_button_windows = []
        
        # Create choice button images (initially hidden)
        self.choice_btn_photos = []
        self.choice_buttons = []
        for i, label in enumerate(["A", "B", "C"]):
            # Create button image without the letter overlay (we'll set the option text at runtime)
            choice_photo = self._create_button_image("option.png", "", scale_factor=0.5)
            self.choice_btn_photos.append(choice_photo)
            
            btn = tk.Button(
                self.window,
                image=choice_photo,
                text="",
                compound='center',
                font=tkfont.Font(family="微软雅黑", size=int(18 * s), weight="bold"),
                command=lambda choice=label: self._wrap_with_click_sound(lambda: self.on_choice_selected(choice))(),
                borderwidth=0,
                highlightthickness=0,
                bg="black",
                fg="white",
                activebackground="black",
                activeforeground="white"
            )
            y_pos = choice_start_y + i * choice_spacing_y
            # Create window on canvas
            btn_window = self.canvas.create_window(self.display_width // 2, y_pos, window=btn)
            self.choice_buttons.append(btn)
            # Initially hide the button window
            self.canvas.itemconfig(btn_window, state='hidden')
            # Store window id for show/hide
            self.choice_button_windows.append(btn_window)
        
        # Bottom-right buttons
        right_x_start = self.display_width - int(220 * s)
        bottom_y = self.display_height - int(30 * s)
        
        # Left/Right navigation buttons using images
        # Left button: position from bottom-left corner
        # Original coordinates at 1920x1080: x=120, y=10 from bottom-left
        # Calculate scaled position
        left_x = int(120 * s)
        left_y = self.display_height - int(10 * s)
        
        # Load and create left button image (scale to 1/16 of original size)
        if os.path.exists("Left.png"):
            left_img = Image.open("Left.png").convert('RGBA')
            # Scale to 1/16 (multiply by s for screen scaling and 0.25 for size reduction to 1/16)
            left_scaled_w = int(left_img.width * s * 0.25)
            left_scaled_h = int(left_img.height * s * 0.25)
            left_img = left_img.resize((left_scaled_w, left_scaled_h), Image.Resampling.LANCZOS)
            self.left_btn_photo = ImageTk.PhotoImage(left_img)
            
            # Create button as a canvas image (clickable) to avoid tk.Button black border
            self.left_button_id = self.canvas.create_image(
                left_x, left_y, 
                anchor=tk.SW, 
                image=self.left_btn_photo,
                tags="left_nav_button"
            )
            self.canvas.tag_bind("left_nav_button", "<Button-1>", lambda e: self.prev_sentence())
        
        # Right button: symmetric to left button across vertical center axis
        # Calculate mirrored x position: if left is at offset `left_x` from left edge,
        # right should be at offset `left_x` from right edge
        right_x = self.display_width - left_x
        right_y = left_y
        
        # Load and create right button image (scale to 1/16 of original size)
        if os.path.exists("Right.png"):
            right_img = Image.open("Right.png").convert('RGBA')
            # Scale to 1/16 (multiply by s for screen scaling and 0.25 for size reduction to 1/16)
            right_scaled_w = int(right_img.width * s * 0.25)
            right_scaled_h = int(right_img.height * s * 0.25)
            right_img = right_img.resize((right_scaled_w, right_scaled_h), Image.Resampling.LANCZOS)
            self.right_btn_photo = ImageTk.PhotoImage(right_img)
            
            # Create button as a canvas image (clickable) to avoid tk.Button black border
            self.right_button_id = self.canvas.create_image(
                right_x, right_y, 
                anchor=tk.SE, 
                image=self.right_btn_photo,
                tags="right_nav_button"
            )
            self.canvas.tag_bind("right_nav_button", "<Button-1>", lambda e: self.next_sentence())
        
        # Ensure text and navigation buttons are on top of everything
        if hasattr(self, 'narrative_canvas_text'):
            self.canvas.tag_raise(self.narrative_canvas_text)
        if hasattr(self, 'left_button_id'):
            self.canvas.tag_raise(self.left_button_id)
        if hasattr(self, 'right_button_id'):
            self.canvas.tag_raise(self.right_button_id)
    
    def _split_into_sentences(self, text: str) -> list:
        """Split text into sentences based on Chinese/English punctuation.
        Keep quotation marks that immediately follow sentence-ending punctuation.
        Also keep text after closing quotes if on same line (e.g., '。"那人说')."""
        # Split by sentence-ending punctuation + optional quote, but only before whitespace or end
        # This keeps things like '。"那人说' together as one sentence
        sentences = re.split(r'([。！？.!?][""\'"'']?)(?=\s|$)', text)
        
        # Recombine punctuation (with optional quotes) with sentences
        result = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                result.append(sentences[i] + sentences[i + 1])
            else:
                result.append(sentences[i])
        
        # Add last part if exists
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            result.append(sentences[-1])
        
        return [s.strip() for s in result if s.strip()]
    
    def prev_sentence(self):
        """Navigate to previous sentence."""
        self._play_click_sound()
        if self.current_sentence_index > 0:
            self.current_sentence_index -= 1
            self._update_text_display()
    
    def next_sentence(self):
        """Navigate to next sentence."""
        self._play_click_sound()
        print(f"[DEBUG] next_sentence: current_index={self.current_sentence_index}, total={len(self.current_text_sentences)}, mode={self.text_display_mode}")
        
        if self.current_sentence_index < len(self.current_text_sentences) - 1:
            self.current_sentence_index += 1
            self._update_text_display()
            print(f"[DEBUG] Moved to next sentence: {self.current_sentence_index}")
        elif self.text_display_mode == 'narrative':
            # Finished narrative, show options
            print("[DEBUG] Reached end of narrative, calling _show_choice_options()")
            self._show_choice_options()
        elif self.text_display_mode == 'result':
            # Finished result text, show settlement modal
            print("[DEBUG] Reached end of result, calling _show_settlement_modal()")
            self._show_settlement_modal()
        elif self.text_display_mode == 'result_before_ending':
            # Finished result text, now show ending text on black screen
            print("[DEBUG] Reached end of result, transitioning to death ending")
            if hasattr(self, 'pending_ending_text'):
                self._show_death_ending_black_screen(self.pending_ending_text)
            else:
                print("[ERROR] No pending_ending_text found!")
        elif self.text_display_mode == 'transition':
            # Finished transition text, proceed to next day (Day 6)
            print("[DEBUG] Reached end of transition, proceeding to Day 6")
            self._proceed_to_day6()
        elif self.text_display_mode == 'death_ending':
            # Finished death ending text, transition to black screen with white text
            print("[DEBUG] Reached end of death ending text, transitioning to black screen")
            # Get the full ending text
            full_ending_text = '\n'.join(self.current_text_sentences)
            # Clear and show black screen with ending
            self._show_death_ending_black_screen(full_ending_text)
        elif self.text_display_mode == 'death_ending_final':
            # Already on black screen, just show restart button
            print("[DEBUG] Reached end of black screen death ending, showing restart button")
            self._show_restart_button_on_death()
        else:
            print(f"[DEBUG] next_sentence: no action taken (mode={self.text_display_mode})")
    
    def _update_text_display(self):
        """Update the text box with current sentence."""
        if 0 <= self.current_sentence_index < len(self.current_text_sentences):
            current_text = self.current_text_sentences[self.current_sentence_index]
            self.canvas.itemconfig(self.narrative_canvas_text, text=current_text)
            
            # Get text coordinates for debugging
            text_coords = self.canvas.coords(self.narrative_canvas_text)
            text_config = self.canvas.itemcget(self.narrative_canvas_text, 'fill')
            
            # Ensure text and navigation buttons are visible on top of everything
            self.canvas.tag_raise(self.narrative_canvas_text)
            if hasattr(self, 'left_button_id'):
                self.canvas.tag_raise(self.left_button_id)
            if hasattr(self, 'right_button_id'):
                self.canvas.tag_raise(self.right_button_id)
            
            print(f"[DEBUG] Text display - position: {text_coords}, color: {text_config}, display_size: ({self.display_width}, {self.display_height})")
            print(f"[DEBUG] Displaying sentence {self.current_sentence_index + 1}/{len(self.current_text_sentences)}: {current_text[:50]}...")
        else:
            self.canvas.itemconfig(self.narrative_canvas_text, text="")
    
    def _show_choice_options(self):
        """Show ABC choice buttons after narrative is complete."""
        print("[DEBUG] _show_choice_options called!")
        
        # Get current day options from CSV
        current_day = self.manager.current_day
        options_dict = self.csv_loader.get_options(current_day)

        # Debug: print options and internal state
        print(f"[DEBUG] Showing choices for day {current_day}: {options_dict}")
        
        # Check if this day has any valid options (Day 15 has none)
        has_valid_options = any(options_dict.get(k, '').strip() for k in ['A', 'B', 'C'])
        
        if not has_valid_options:
            print(f"[DEBUG] No valid options for day {current_day}, checking for ending text")
            # Day 15 or other days without choices - check if there's an ending in settlement
            # Get the settlement text for any option (since there are no real options)
            settlement_text = self.csv_loader.get_settlement(current_day, 'A')  # Try A first
            if not settlement_text:
                settlement_text = self.csv_loader.data.get(current_day, {}).get('settlement_a', '')
            
            print(f"[DEBUG] Settlement text for day {current_day}: {settlement_text[:100] if settlement_text else 'None'}")
            
            # Check if settlement contains ending trigger
            if settlement_text and ('触发结局' in settlement_text or 'Trigger Ending' in settlement_text):
                print(f"[DEBUG] Found ending in settlement, showing black screen ending")
                # Store the ending text and show it
                self.pending_ending_text = settlement_text
                self._show_death_ending_black_screen(settlement_text)
                return
            else:
                # No ending found, show generic game over
                print(f"[DEBUG] No ending found, calling on_game_over()")
                self.on_game_over()
                return
        
        # Clear text and mark mode
        self.canvas.itemconfig(self.narrative_canvas_text, text="")
        self.text_display_mode = 'choices'
        
        if hasattr(self, 'choice_button_windows'):
            print(f"[DEBUG] choice_button_windows count: {len(self.choice_button_windows)}")
        else:
            print("[DEBUG] ERROR: No choice_button_windows attribute!")
            return

        # Update and show choice buttons
        for i, (choice_key, btn) in enumerate(zip(['A', 'B', 'C'], self.choice_buttons)):
            option_text = options_dict.get(choice_key, choice_key)
            print(f"[DEBUG] Setting button {i} ({choice_key}) to: {option_text}")
            
            # Update button label if supported
            try:
                btn.config(text=option_text)
            except Exception as e:
                print(f"[DEBUG] Could not set button text: {e}")
            
            btn.config(state=tk.NORMAL)
            
            # Show the button window and raise it above other canvas items
            if hasattr(self, 'choice_button_windows') and i < len(self.choice_button_windows):
                win_id = self.choice_button_windows[i]
                print(f"[DEBUG] Showing button window {i} (id={win_id})")
                self.canvas.itemconfig(win_id, state='normal')
                self.canvas.tag_raise(win_id)
        
        print("[DEBUG] All choice buttons should now be visible!")
    
    def _show_settlement_modal(self):
        """Show settlement modal after result text is complete."""
        state = self.manager.state
        
        # Build settlement text from pending settlement data
        settlement_lines = []
        settlement_lines.append("=" * 30)
        settlement_lines.append("系统结算" if self.current_language == "中文" else "Settlement")
        settlement_lines.append("=" * 30)
        
        # Add the settlement text from CSV if available
        if hasattr(self, 'pending_settlement_text') and self.pending_settlement_text:
            csv_text = self.pending_settlement_text.strip()
            
            # Split by lines and filter out item/clue section headers only
            lines = csv_text.split('\n')
            filtered_lines = []
            for line in lines:
                stripped = line.strip()
                # Skip empty lines
                if not stripped:
                    continue
                # Skip ONLY the standalone section headers (not the "获得道具：" lines)
                if stripped in ["持有道具：", "Items:", "持有线索：", "Clues:"]:
                    continue
                # Keep all other lines including "获得道具：XXX" and "获得线索：XXX"
                filtered_lines.append(line)
            
            csv_text = '\n'.join(filtered_lines).strip()
            
            if csv_text:  # Only add if there's content left
                settlement_lines.append("")
                settlement_lines.append(csv_text)
                settlement_lines.append("")
        
        # Add current stats
        settlement_lines.append("-" * 30)
        settlement_lines.append("当前状态：" if self.current_language == "中文" else "Current Status:")
        settlement_lines.append((f"体力值: {state.stamina}/{state.max_stamina}" if self.current_language == "中文" 
                     else f"Stamina: {state.stamina}/{state.max_stamina}"))
        settlement_lines.append((f"魔力值: {state.mana}/{state.max_mana}" if self.current_language == "中文" 
                     else f"Mana: {state.mana}/{state.max_mana}"))
        
        # Normal progress always shown
        settlement_lines.append(f"贿赂进度: {state.bribe_progress}" if self.current_language == "中文" else f"Bribe: {state.bribe_progress}")
        settlement_lines.append(f"破坏进度: {state.sabotage_progress}" if self.current_language == "中文" else f"Sabotage: {state.sabotage_progress}")
        settlement_lines.append(f"法学进度: {state.legal_progress}" if self.current_language == "中文" else f"Legal: {state.legal_progress}")
        
        # Mystery progress (?) - only show when mystery_progress >= 1
        if state.mystery_progress >= 1:
            settlement_lines.append(f"?进度: {state.mystery_progress}" if self.current_language == "中文" else f"?: {state.mystery_progress}")
        
        # DEBUG: Print inventory and clues state
        print(f"[SETTLEMENT DEBUG] Day {state.stamina}, Inventory: {state.inventory}, Clues: {state.clues}")
        print(f"[SETTLEMENT DEBUG] Inventory check: {state.inventory and any(item.strip() for item in state.inventory)}")
        print(f"[SETTLEMENT DEBUG] Clues check: {state.clues and any(clue.strip() for clue in state.clues)}")
        
        # REMOVED: Don't show "持有道具：" section - items are already shown in CSV text as "获得道具：XXX"
        # if state.inventory and any(item.strip() for item in state.inventory):
        #     settlement_lines.append("")
        #     settlement_lines.append("持有道具：" if self.current_language == "中文" else "Items:")
        #     for item in state.inventory:
        #         if item.strip():  # Only show non-empty items
        #             settlement_lines.append(f"  • {item}")
        #             print(f"[SETTLEMENT DEBUG] Adding item to display: {repr(item)}")
        
        # REMOVED: Don't show "持有线索：" section - clues are already shown in CSV text as "获得线索：XXX"
        # if state.clues and any(clue.strip() for clue in state.clues):
        #     settlement_lines.append("")
        #     settlement_lines.append("持有线索：" if self.current_language == "中文" else "Clues:")
        #     for clue in state.clues:
        #         if clue.strip():  # Only show non-empty clues
        #             settlement_lines.append(f"  • {clue}")
        #             print(f"[SETTLEMENT DEBUG] Adding clue to display: {repr(clue)}")
        
        settlement_text = "\n".join(settlement_lines)
        
        # DEBUG: Print final settlement text
        print(f"[SETTLEMENT DEBUG] Final settlement text:")
        print("=" * 50)
        print(settlement_text)
        print("=" * 50)
        
        # Create modal
        modal = tk.Toplevel(self.window)
        modal.title("系统结算" if self.current_language == "中文" else "Settlement")
        modal.geometry("700x430")
        modal.configure(bg="black")
        modal.transient(self.window)
        modal.grab_set()
        
        # Center the modal
        modal.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.window.winfo_screenheight() // 2) - (430 // 2)
        modal.geometry(f"700x430+{x}+{y}")
        
        # Settlement text
        text_widget = tk.Text(
            modal,
            width=70,
            height=15,
            font=tkfont.Font(family="微软雅黑", size=12),
            bg="black",
            fg="white",
            wrap=tk.WORD,
            state=tk.NORMAL
        )
        text_widget.pack(padx=20, pady=20)
        text_widget.insert("1.0", settlement_text)
        text_widget.config(state=tk.DISABLED)
        
        # Continue button
        def on_continue():
            self._play_click_sound()
            modal.destroy()
            self.continue_game()
        
        print(f"[DEBUG] Creating continue button with enlarged size")
        continue_btn = tk.Button(
            modal,
            text="继续" if self.current_language == "中文" else "Continue",
            font=tkfont.Font(family="微软雅黑", size=9),  # Reduced to 9 to fit completely
            command=on_continue,
            width=8,  # Increased width from 6 to 8
            height=3
        )
        continue_btn.pack(pady=10)
        
        # Force update to get actual size
        modal.update_idletasks()
        btn_width = continue_btn.winfo_width()
        btn_height = continue_btn.winfo_height()
        print(f"[DEBUG] Button actual size: width={btn_width}px, height={btn_height}px")
        
        # Wait for modal to close
        modal.wait_window()
    
    def start_game(self):
        """Start the game by showing story background modal, then first level."""
        # Start background music
        self.audio_manager.start_bgm()
        # First, do a quick fullscreen refresh cycle before showing story
        self.window.after(100, self._initial_fullscreen_refresh)
    
    def _initial_fullscreen_refresh(self):
        """Do a quick fullscreen exit-reenter cycle to ensure proper display."""
        if self.is_fullscreen:
            # Exit fullscreen
            self.toggle_fullscreen()
            # Re-enter fullscreen after a short delay
            self.window.after(100, self._reenter_fullscreen_and_start_story)
        else:
            # Already not fullscreen, just show story
            self._show_story_directly()
    
    def _reenter_fullscreen_and_start_story(self):
        """Re-enter fullscreen and then show story modal."""
        self.toggle_fullscreen()
        # Show story after fullscreen is ready
        self.window.after(100, self._show_story_directly)
    
    def _show_story_directly(self):
        """Show story modal or start game."""
        # Get story background text based on current language
        header = '故事背景' if self.current_language == "中文" else 'Story background'
        story_text = get_special_text(header, self.current_language)
        if story_text:
            self._show_story_modal(story_text)
        else:
            # If no story text, just show first level
            self.show_current_level()
    
    def _show_story_modal(self, text: str):
        """Show story background modal with confirm button."""
        modal = tk.Toplevel(self.window)
        modal.title("故事背景" if self.current_language == "中文" else "Story Background")
        modal.geometry("800x600")
        modal.configure(bg="black")
        modal.transient(self.window)
        # Don't grab_set to allow language button clicks
        # modal.grab_set()
        
        # Save modal reference and set flag
        self.story_modal = modal
        self.story_modal_open = True
        
        # Center the modal
        modal.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        modal.geometry(f"800x600+{x}+{y}")
        
        # Story text
        text_widget = tk.Text(
            modal,
            width=80,
            height=25,
            font=tkfont.Font(family="微软雅黑", size=14),
            bg="black",
            fg="white",
            wrap=tk.WORD,
            state=tk.NORMAL
        )
        text_widget.pack(padx=20, pady=20)
        text_widget.insert("1.0", text)
        text_widget.config(state=tk.DISABLED)
        
        # Confirm button
        def on_confirm():
            self._play_click_sound()
            self.story_modal_open = False
            self.story_modal = None
            modal.destroy()
            # Exit fullscreen then re-enter to refresh UI
            self.window.after(50, self._refresh_fullscreen_and_show)
        
        # Handle modal close
        def on_close():
            self._play_click_sound()
            self.story_modal_open = False
            self.story_modal = None
            modal.destroy()
            self.window.after(50, self._refresh_fullscreen_and_show)
        
        modal.protocol("WM_DELETE_WINDOW", on_close)
        
        confirm_btn = tk.Button(
            modal,
            text="确认" if self.current_language == "中文" else "Confirm",
            font=tkfont.Font(family="微软雅黑", size=16),
            command=on_confirm,
            width=15,
            height=2
        )
        confirm_btn.pack(pady=10)
        
        # Don't wait_window to allow language switching
        # modal.wait_window()
    
    def _refresh_fullscreen_and_show(self):
        """Exit and re-enter fullscreen to refresh UI, then show content."""
        if self.is_fullscreen:
            # Exit fullscreen first
            self.toggle_fullscreen()
            # Wait a bit, then re-enter fullscreen
            self.window.after(100, self._reenter_fullscreen)
        else:
            # Not in fullscreen, just enter it
            self.toggle_fullscreen()
            self.window.after(100, self.show_current_level)
    
    def _reenter_fullscreen(self):
        """Re-enter fullscreen and show content."""
        self.toggle_fullscreen()
        # Show current level after fullscreen is ready
        self.window.after(100, self.show_current_level)
    
    def _enter_fullscreen_and_start(self):
        """Enter fullscreen mode and start the game."""
        # Enter fullscreen (will trigger _rebuild_ui)
        if not self.is_fullscreen:
            self.toggle_fullscreen()
        # Show current level after UI rebuild completes
        self.window.after(200, self.show_current_level)
    
    def _force_fullscreen_and_show(self):
        """Force fullscreen mode with complete UI rebuild."""
        # Ensure fullscreen state
        if not self.is_fullscreen:
            # Need to enter fullscreen
            self.toggle_fullscreen()
        else:
            # Already fullscreen but may have lost state, force rebuild
            self._rebuild_ui()
        
        # Show level after UI is ready
        self.window.after(100, self.show_current_level)
    
    def _restore_fullscreen_and_show(self):
        """Restore fullscreen mode and then show current level."""
        self.toggle_fullscreen()
        # Wait for fullscreen to complete, then show level
        self.window.after(100, self.show_current_level)
    
    def show_current_level(self):
        """Display the current day's narrative and choices."""
        state = self.manager.state
        current_day = self.manager.current_day
        
        # Load background for current day
        self._load_background_for_day(current_day)
        
        # Update day label (now using canvas text)
        if self.current_language == "中文":
            day_text = f"第{number_to_chinese(current_day)}天"
        else:
            day_text = f"Day {current_day}"
        self.canvas.itemconfig(self.day_text_id, text=day_text)
        
        # Update status displays
        self._update_status_display()
        
        # Get narrative from CSV
        narrative = self.csv_loader.get_narrative(current_day)
        
        self.current_text_sentences = self._split_into_sentences(narrative)
        self.current_sentence_index = 0
        self.text_display_mode = 'narrative'
        
        # Display first sentence
        self._update_text_display()
        
        # Hide choice buttons initially
        if hasattr(self, 'choice_button_windows'):
            for btn_window in self.choice_button_windows:
                self.canvas.itemconfig(btn_window, state='hidden')
        for btn in self.choice_buttons:
            btn.config(state=tk.DISABLED)
        
        # Force text and navigation buttons to top after everything is loaded
        self.window.after(10, self._ensure_text_visible)
    
    def _ensure_text_visible(self):
        """Ensure text and navigation buttons are always on top."""
        # Debug: print all canvas items and their tags
        all_items = self.canvas.find_all()
        print(f"[DEBUG] Total canvas items: {len(all_items)}")
        for item in all_items[-10:]:  # Print last 10 items
            tags = self.canvas.gettags(item)
            item_type = self.canvas.type(item)
            print(f"  Item {item}: type={item_type}, tags={tags}")
        
        if hasattr(self, 'narrative_canvas_text'):
            print(f"[DEBUG] narrative_canvas_text ID: {self.narrative_canvas_text}")
            # Check if text exists
            try:
                text_content = self.canvas.itemcget(self.narrative_canvas_text, 'text')
                text_state = self.canvas.itemcget(self.narrative_canvas_text, 'state')
                print(f"[DEBUG] Text content length: {len(text_content)}, state: {text_state}")
            except:
                print("[DEBUG] ERROR: Text item not found!")
            self.canvas.tag_raise(self.narrative_canvas_text)
        if hasattr(self, 'left_button_id'):
            self.canvas.tag_raise(self.left_button_id)
        if hasattr(self, 'right_button_id'):
            self.canvas.tag_raise(self.right_button_id)
        print("[DEBUG] Text visibility ensured - text raised to top")
    
    def _update_status_display(self):
        """Update all status labels with current game state."""
        state = self.manager.state
        
        # Update stamina and mana (now using canvas text items)
        stamina_text = f"体力值: {state.stamina}" if self.current_language == "中文" else f"Stamina: {state.stamina}"
        self.canvas.itemconfig(self.stamina_text_id, text=stamina_text)
        
        mana_text = f"魔力值: {state.mana}" if self.current_language == "中文" else f"Mana: {state.mana}"
        self.canvas.itemconfig(self.mana_text_id, text=mana_text)
        
        # Update progress (normal progress always visible)
        bribe_text = f"贿赂: {state.bribe_progress}" if self.current_language == "中文" else f"Bribe: {state.bribe_progress}"
        self.canvas.itemconfig(self.bribe_text_id, text=bribe_text)
        
        sabotage_text = f"破坏: {state.sabotage_progress}" if self.current_language == "中文" else f"Sabotage: {state.sabotage_progress}"
        self.canvas.itemconfig(self.sabotage_text_id, text=sabotage_text)
        
        legal_text = f"法学: {state.legal_progress}" if self.current_language == "中文" else f"Legal: {state.legal_progress}"
        self.canvas.itemconfig(self.legal_text_id, text=legal_text)
        
        # Mystery progress (?) - only show when mystery_progress >= 1
        show_mystery = state.mystery_progress >= 1
        mystery_text = f"?: {state.mystery_progress}" if self.current_language == "中文" else f"?: {state.mystery_progress}"
        self.canvas.itemconfig(self.mystery_text_id, text=mystery_text if show_mystery else "")
    
    def _show_requirements_warning(self, unmet_conditions: list):
        """Show modal warning when player doesn't meet requirements."""
        import tkinter.font as tkfont
        
        modal = tk.Toplevel(self.window)
        modal.title("条件不足" if self.current_language == "中文" else "Requirements Not Met")
        modal.geometry("500x300")
        modal.configure(bg="black")
        modal.transient(self.window)
        modal.grab_set()
        
        # Center the modal
        modal.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (300 // 2)
        modal.geometry(f"500x300+{x}+{y}")
        
        # Title
        title_text = "选项条件不足" if self.current_language == "中文" else "Requirements Not Met"
        title_label = tk.Label(
            modal,
            text=title_text,
            font=tkfont.Font(family="微软雅黑", size=16, weight="bold"),
            bg="black",
            fg="red"
        )
        title_label.pack(pady=20)
        
        # Message
        msg_text = "您需要满足以下条件才能选择此选项：" if self.current_language == "中文" else "You need to meet the following requirements:"
        msg_label = tk.Label(
            modal,
            text=msg_text,
            font=tkfont.Font(family="微软雅黑", size=12),
            bg="black",
            fg="white"
        )
        msg_label.pack(pady=10)
        
        # Unmet conditions list
        conditions_text = "\n".join([f"• {cond}" for cond in unmet_conditions])
        conditions_label = tk.Label(
            modal,
            text=conditions_text,
            font=tkfont.Font(family="微软雅黑", size=11),
            bg="black",
            fg="yellow",
            justify=tk.LEFT
        )
        conditions_label.pack(pady=10)
        
        # Close button
        close_btn = tk.Button(
            modal,
            text="确定" if self.current_language == "中文" else "OK",
            font=tkfont.Font(family="微软雅黑", size=12),
            command=self._wrap_with_click_sound(modal.destroy),
            width=10,
            height=2
        )
        close_btn.pack(pady=20)
    
    def on_choice_selected(self, choice: str):
        """Handle choice selection."""
        current_day = self.manager.current_day
        
        # Save the choice for language switching
        self.last_choice = choice
        
        # Check if player meets requirements for this day and choice (only for days 11, 12, 14 options A/B)
        meets_reqs, unmet_conditions = self.csv_loader.check_requirements(current_day, choice, self.manager.state)
        if not meets_reqs:
            # Show warning modal with unmet conditions
            self._show_requirements_warning(unmet_conditions)
            return  # Don't proceed with choice
        
        # Hide choice buttons after selection
        if hasattr(self, 'choice_button_windows'):
            for btn_window in self.choice_button_windows:
                self.canvas.itemconfig(btn_window, state='hidden')
        for btn in self.choice_buttons:
            btn.config(state=tk.DISABLED)
        
        # Get result text from CSV
        result_text = self.csv_loader.get_result(current_day, choice)
        
        # Get settlement data from CSV and parse it
        settlement_text = self.csv_loader.get_settlement(current_day, choice)
        
        # Check if settlement text contains death/ending keywords
        death_keywords = ['触发结局：', '触发结局:', '游戏结束', '火刑', '判定死亡', 'Game Over', 'THE END', 'death ending', 'Ending:']
        is_death_ending = any(keyword in settlement_text for keyword in death_keywords)
        
        if is_death_ending:
            print(f"[DEBUG] Death ending detected in settlement text!")
            # Extract ending text after "触发结局：" keyword
            ending_text = settlement_text
            for keyword in ['触发结局：', '触发结局:']:
                if keyword in settlement_text:
                    # Get everything after the keyword
                    parts = settlement_text.split(keyword, 1)
                    if len(parts) > 1:
                        ending_text = keyword + parts[1].strip()
                    break
            
            print(f"[DEBUG] Extracted ending text: {ending_text[:100]}...")
            # Store the ending text to show AFTER result text
            self.pending_ending_text = ending_text
            # Set mode to show result first, then ending
            self.text_display_mode = 'result_before_ending'
        else:
            # Normal result mode - parse settlement and apply changes
            settlement_data = self.csv_loader.parse_settlement(settlement_text)
            
            # Apply changes to game state
            state = self.manager.state
            state.apply_change(
                stamina_delta=settlement_data['stamina_change'],
                mana_delta=settlement_data['mana_change'],
                bribe_delta=settlement_data['bribe_change'],
                sabotage_delta=settlement_data['sabotage_change'],
                legal_delta=settlement_data['legal_change'],
                mystery_delta=settlement_data['mystery_change'],
                add_items=settlement_data['items_gained'],
                add_clues=settlement_data['clues_gained'],
                remove_items=[]
            )
            
            # Store settlement text for display later
            self.pending_settlement_text = settlement_text
            self.text_display_mode = 'result'
        
        # Update status display
        self._update_status_display()
        
        # Split result text into sentences and start displaying
        self.current_text_sentences = self._split_into_sentences(result_text)
        self.current_sentence_index = 0
        self._update_text_display()
        
        # Check for special settlement cases (negative stamina/mana) - only if not death ending
        if not is_death_ending:
            state = self.manager.state
            if state.stamina < 0 or state.mana < 0:
                special_key = None
                if state.stamina < 0 and state.mana < 0:
                    special_key = '体力值魔力值同时≤0' if self.current_language == "中文" else 'Stamina Value Magic Value ≤ 0'
                elif state.stamina < 0:
                    special_key = '体力值≤0' if self.current_language == "中文" else 'Stamina value ≤ 0'
                elif state.mana < 0:
                    special_key = '魔力值≤0' if self.current_language == "中文" else 'Magic value ≤ 0'
                
                if special_key:
                    special_text = get_special_text(special_key, self.current_language)
                    if special_text:
                        # Show special end dialog after result display finishes
                        # For now, show immediately
                        action = self._show_special_end_dialog(special_text)
                        if action == 'retry':
                            # Reset game state and restart from day 1
                            self.manager.state = GameState()
                            self.manager.current_day = 1
                            self.show_current_level()
                        elif action == 'quit':
                            # Exit the game
                            self.window.destroy()
                            import sys
                            sys.exit(0)
                        return
    
    def _show_result_popup(self, result_text: str):
        """Show result popup after choice."""
        if self.result_popup:
            self.result_popup.destroy()
        
        self.result_popup = tk.Toplevel(self.window)
        self.result_popup.title("结果" if self.current_language == "中文" else "Result")
        self.result_popup.geometry("600x400")
        self.result_popup.configure(bg="white")
        self.result_popup.transient(self.window)
        
        # Center the popup
        self.result_popup.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.window.winfo_screenheight() // 2) - (400 // 2)
        self.result_popup.geometry(f"600x400+{x}+{y}")
        
        # Result text
        self.result_label = tk.Label(
            self.result_popup,
            text=result_text,
            font=tkfont.Font(family="微软雅黑", size=14),
            bg="white",
            fg="black",
            wraplength=550,
            justify=tk.LEFT
        )
        self.result_label.pack(padx=20, pady=20)
        
        # Close button
        close_btn = tk.Button(
            self.result_popup,
            text="关闭" if self.current_language == "中文" else "Close",
            font=tkfont.Font(family="微软雅黑", size=12),
            command=self._wrap_with_click_sound(self.result_popup.destroy)
        )
        close_btn.pack(pady=10)
    
    def _show_special_end_dialog(self, text: str) -> str:
        """Show special end dialog with Retry/Quit buttons. Returns 'retry' or 'quit'."""
        result = {'action': 'quit'}  # Default to quit
        
        modal = tk.Toplevel(self.window)
        modal.title("游戏结束" if self.current_language == "中文" else "Game Over")
        modal.geometry("800x600")
        modal.configure(bg="black")
        modal.transient(self.window)
        modal.grab_set()
        
        # Center the modal
        modal.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        modal.geometry(f"800x600+{x}+{y}")
        
        # Special text
        text_widget = tk.Text(
            modal,
            width=80,
            height=20,
            font=tkfont.Font(family="微软雅黑", size=14),
            bg="black",
            fg="white",
            wrap=tk.WORD,
            state=tk.NORMAL
        )
        text_widget.pack(padx=20, pady=20)
        text_widget.insert("1.0", text)
        text_widget.config(state=tk.DISABLED)
        
        # Button frame
        btn_frame = tk.Frame(modal, bg="black")
        btn_frame.pack(pady=20)
        
        def on_retry():
            self._play_click_sound()
            result['action'] = 'retry'
            modal.destroy()
        
        def on_quit():
            self._play_click_sound()
            result['action'] = 'quit'
            modal.destroy()
        
        # Retry button
        retry_btn = tk.Button(
            btn_frame,
            text="再次尝试" if self.current_language == "中文" else "Retry",
            font=tkfont.Font(family="微软雅黑", size=16),
            command=on_retry,
            width=15,
            height=2
        )
        retry_btn.pack(side=tk.LEFT, padx=20)
        
        # Quit button
        quit_btn = tk.Button(
            btn_frame,
            text="结束游戏" if self.current_language == "中文" else "Quit",
            font=tkfont.Font(family="微软雅黑", size=16),
            command=on_quit,
            width=15,
            height=2
        )
        quit_btn.pack(side=tk.LEFT, padx=20)
        
        # Wait for modal to close
        modal.wait_window()
        
        return result['action']
    
    def _show_day56_screen(self):
        """Show Day 56 transition screen after Day 5 settlement."""
        # Get transition text from CSV
        transition_text = self.csv_loader.get_transition_text(5)
        
        if not transition_text:
            # If no transition text, just proceed to day 6
            self._proceed_to_day6()
            return
        
        print("[DEBUG] Showing Day56 transition screen")
        
        # Load Day 56 background if exists, otherwise use day 5 background
        day56_path = "Day 56.PNG"
        if os.path.exists(day56_path):
            print(f"[DEBUG] Loading Day 56 background from {day56_path}")
            background_image = Image.open(day56_path)
        else:
            # Try to load day 5 background
            bg_path = os.path.join("normalized_backgrounds", "5 day.png")
            if os.path.exists(bg_path):
                print(f"[DEBUG] Loading Day 5 background from {bg_path}")
                background_image = Image.open(bg_path)
            else:
                # If no background, use current background
                print("[DEBUG] No background found, using current")
                background_image = None
        
        if background_image:
            # Resize using cover mode (same as _load_background_for_day)
            img_w, img_h = background_image.size
            if img_w > 0 and img_h > 0:
                cover_scale = max(self.display_width / img_w, self.display_height / img_h)
                cover_w = max(1, int(img_w * cover_scale))
                cover_h = max(1, int(img_h * cover_scale))
                resized = background_image.resize((cover_w, cover_h), Image.Resampling.LANCZOS)
                
                # Crop center to display size
                left = (cover_w - self.display_width) // 2
                top = (cover_h - self.display_height) // 2
                right = left + self.display_width
                bottom = top + self.display_height
                cropped = resized.crop((left, top, right, bottom))
                
                bg_rgb = cropped.convert('RGB')
                self.bg_photo = ImageTk.PhotoImage(bg_rgb)
            else:
                self.bg_photo = ImageTk.PhotoImage(Image.new('RGB', (self.display_width, self.display_height), color='black'))
            
            # Update canvas background
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_photo)
            
            # Recreate UI elements (status, buttons, etc.)
            print("[DEBUG] Recreating UI elements")
            self._create_ui_elements()
            
            # Load DialogBox for text display
            dialog_box_path = "DialogBox.png"
            if os.path.exists(dialog_box_path):
                dialog_box = Image.open(dialog_box_path)
                box_width = int(dialog_box.width * self.scale)
                box_height = int(dialog_box.height * self.scale)
                dialog_box = dialog_box.resize((box_width, box_height), Image.Resampling.LANCZOS)
                self.dialog_box_photo = ImageTk.PhotoImage(dialog_box)
                
                # Position at bottom of the screen
                x = self.display_width // 2
                y = self.display_height - (box_height // 2)
                self.canvas.create_image(x, y, image=self.dialog_box_photo, tags="dialogbox")
        
        # Split transition text into sentences and prepare for display
        self.current_text_sentences = self._split_into_sentences(transition_text)
        self.current_sentence_index = 0
        self.text_display_mode = 'transition'  # Special mode for transition
        
        print(f"[DEBUG] Transition text split into {len(self.current_text_sentences)} sentences")
        
        # Display first sentence
        self._update_text_display()
        
        print("[DEBUG] Day56 screen setup complete")
    
    def _show_death_ending(self, ending_text: str):
        """Display death ending on full black background with white text.
        
        Args:
            ending_text: The ending text to display (from stamina/mana <= 0)
        """
        print(f"[DEBUG] Showing death ending screen (from stats)")
        
        # Clear entire canvas to black
        self.canvas.delete("all")
        self.canvas.configure(bg="black")
        
        # Split ending text into sentences for progressive display
        sentences = [s.strip() for s in ending_text.split('\n') if s.strip()]
        self.current_text_sentences = sentences
        self.current_sentence_index = 0
        self.text_display_mode = 'death_ending_final'
        
        # Calculate text position (center of screen)
        text_x = self.display_width // 2
        text_y = self.display_height // 2
        
        # Use same font size as day number display (18)
        text_size = int(18 * self.scale)
        text_font = tkfont.Font(family="微软雅黑", size=text_size)
        
        # Create white text on black background with wraplength
        max_width = int(800 * self.scale)
        self.narrative_canvas_text = self.canvas.create_text(
            text_x, text_y,
            text=sentences[0] if sentences else ending_text,
            fill="white",
            font=text_font,
            width=max_width,
            justify="left",
            tags="death_ending_text"
        )
        
        # Add navigation arrows if there are multiple sentences
        if len(sentences) > 1:
            self._add_navigation_arrows()
        else:
            # If only one screen of text, add a "重新开始" button after a moment
            self.window.after(2000, self._show_restart_button_on_death)
        
        print(f"[DEBUG] Death ending displayed with {len(sentences)} sentences")
    
    def _show_restart_button_on_death(self):
        """Show restart button on death ending screen."""
        button_x = self.display_width // 2
        button_y = int(self.display_height * 0.9)
        
        # Create restart button
        restart_text = "重新开始" if self.current_language == "中文" else "Restart"
        button_font = tkfont.Font(family="微软雅黑", size=int(16 * self.scale))
        
        # Create button background
        button_bg = self.canvas.create_rectangle(
            button_x - 80, button_y - 25,
            button_x + 80, button_y + 25,
            fill="#333333",
            outline="white",
            tags="restart_button"
        )
        
        # Create button text
        button_text_id = self.canvas.create_text(
            button_x, button_y,
            text=restart_text,
            fill="white",
            font=button_font,
            tags="restart_button"
        )
        
        # Bind click event to restart game
        def restart_game(event):
            print("[DEBUG] Restarting game...")
            # Reset game state
            from game.state import GameState
            self.manager.state = GameState()
            self.manager.current_day = 1
            # Clear canvas and restart
            self.canvas.delete("all")
            self._load_background_for_day(1)
            self._create_ui_elements()
            self.show_current_level()
        
        self.canvas.tag_bind("restart_button", "<Button-1>", restart_game)
    
    def _show_death_ending_black_screen(self, ending_text: str, death_type: str = 'custom'):
        """Transition from normal game screen to black screen death ending.
        
        Args:
            ending_text: The ending text to display on black background
            death_type: Type of death ending - 'stamina', 'mana', 'both', or 'custom' (default)
        """
        print(f"[DEBUG] Transitioning to black screen death ending (type: {death_type})")
        print(f"[DEBUG] Ending text: {ending_text[:200]}...")
        
        # Store the ending text and type for language switching
        self.current_ending_text = ending_text
        self.current_ending_type = death_type
        
        # Clear entire canvas to black
        self.canvas.delete("all")
        self.canvas.configure(bg="black")
        
        # Calculate text position (center of screen, slightly above center)
        text_x = self.display_width // 2
        text_y = self.display_height // 2 - int(50 * self.scale)
        
        # Use same font size as day number display (18)
        text_size = int(18 * self.scale)
        text_font = tkfont.Font(family="微软雅黑", size=text_size)
        
        # Create white text on black background with wraplength
        max_width = int(800 * self.scale)
        self.narrative_canvas_text = self.canvas.create_text(
            text_x, text_y,
            text=ending_text,
            fill="white",
            font=text_font,
            width=max_width,
            justify="left",
            tags="death_ending_text"
        )
        
        # Set mode to death_ending_final for language switching support
        self.text_display_mode = 'death_ending_final'
        
        # Show restart button after a brief delay
        self.window.after(1000, self._show_restart_button_on_death)
        
        print(f"[DEBUG] Black screen death ending displayed")
    
    def _proceed_to_day6(self):
        """Proceed to Day 6 after Day 56 screen."""
        self.manager.current_day = 6
        
        # Clear canvas and recreate UI
        self.canvas.delete("all")
        self._load_background_for_day(6)
        self._create_ui_elements()
        self.show_current_level()
    
    def continue_game(self):
        """Continue to next day."""
        # Close result popup if open
        if self.result_popup:
            self.result_popup.destroy()
            self.result_popup = None
        
        current_day = self.manager.current_day
        
        # Check if we just finished Day 5 - show Day 56 screen BEFORE incrementing
        if current_day == 5:
            # Don't increment day yet - Day56 screen will handle it
            self._show_day56_screen()
        # Check if game is over (15 days completed)
        elif current_day >= 15:
            # Day 15 always has an ending - check if it was stored from settlement
            if hasattr(self, 'pending_ending_text') and self.pending_ending_text:
                ending_text = self.pending_ending_text
                # Clear pending to avoid repeated display
                self.pending_ending_text = None
                self._show_death_ending_black_screen(ending_text)
            else:
                # No ending stored - this shouldn't happen for Day 15, but handle gracefully
                # Try to get the ending text from the last settlement
                if hasattr(self, 'pending_settlement_text') and self.pending_settlement_text:
                    # Check if settlement contains ending text
                    if '触发结局' in self.pending_settlement_text or 'Trigger Ending' in self.pending_settlement_text:
                        self._show_death_ending_black_screen(self.pending_settlement_text)
                    else:
                        self.manager.current_day += 1
                        self.on_game_over()
                else:
                    self.manager.current_day += 1
                    self.on_game_over()
        else:
            self.manager.current_day += 1
            self.show_current_level()
    
    def show_tools(self):
        """Show tools inventory."""
        state = self.manager.state
        # Use inventory as source for tools/items
        tools = state.inventory or []
        
        popup = tk.Toplevel(self.window)
        popup.title("道具" if self.current_language == "中文" else "Tools")
        popup.geometry("450x350")
        popup.configure(bg="white")
        popup.transient(self.window)
        
        # Center the popup
        popup.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.window.winfo_screenheight() // 2) - (350 // 2)
        popup.geometry(f"450x350+{x}+{y}")
        
        # Create frame for items
        frame = tk.Frame(popup, bg="white")
        frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        if not tools:
            no_tools_label = tk.Label(frame, text="无道具" if self.current_language == "中文" else "No tools",
                                     font=tkfont.Font(family="微软雅黑", size=12), bg="white")
            no_tools_label.pack(pady=20)
        else:
            # Display each tool with use button if applicable
            for tool in tools:
                tool_frame = tk.Frame(frame, bg="white")
                tool_frame.pack(fill=tk.X, pady=5, padx=5)
                
                tool_label = tk.Label(tool_frame, text=tool, font=tkfont.Font(family="微软雅黑", size=12),
                                    bg="white", anchor=tk.W)
                tool_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Add use button for blood potion
                if "血息药剂" in tool or "Blood Potion" in tool:
                    use_btn = tk.Button(tool_frame, 
                                      text="使用" if self.current_language == "中文" else "Use",
                                      font=tkfont.Font(family="微软雅黑", size=10),
                                      command=lambda t=tool, p=popup: self._wrap_with_click_sound(lambda: self._use_blood_potion(t, p))())
                    use_btn.pack(side=tk.RIGHT, padx=5)
        
        close_btn = tk.Button(popup, text="关闭" if self.current_language == "中文" else "Close", 
                             command=self._wrap_with_click_sound(popup.destroy))
        close_btn.pack(pady=5)
    
    def _use_blood_potion(self, tool_name, popup):
        """Use blood potion to restore stamina and mana."""
        state = self.manager.state
        
        # Add 5 to both stamina and mana
        old_stamina = state.stamina
        old_mana = state.mana
        state.apply_change(stamina_delta=5, mana_delta=5)
        
        # Remove the potion from inventory
        if tool_name in state.inventory:
            state.inventory.remove(tool_name)
        
        # Update display
        self._update_status_display()
        
        # Show confirmation message
        stamina_change = state.stamina - old_stamina
        mana_change = state.mana - old_mana
        message = (f"使用血息药剂成功！\n体力值 +{stamina_change}\n魔力值 +{mana_change}" 
                  if self.current_language == "中文" 
                  else f"Blood Potion used successfully!\nStamina +{stamina_change}\nMana +{mana_change}")
        
        # Close the tools popup
        popup.destroy()
        
        # Show result message
        result_popup = tk.Toplevel(self.window)
        result_popup.title("使用道具" if self.current_language == "中文" else "Use Item")
        result_popup.geometry("300x150")
        result_popup.configure(bg="white")
        result_popup.transient(self.window)
        
        # Center the popup
        result_popup.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.window.winfo_screenheight() // 2) - (150 // 2)
        result_popup.geometry(f"300x150+{x}+{y}")
        
        msg_label = tk.Label(result_popup, text=message, font=tkfont.Font(family="微软雅黑", size=12),
                           bg="white", justify=tk.CENTER)
        msg_label.pack(pady=20)
        
        ok_btn = tk.Button(result_popup, text="确定" if self.current_language == "中文" else "OK",
                         command=self._wrap_with_click_sound(result_popup.destroy))
        ok_btn.pack(pady=10)
    
    def show_clues(self):
        """Show clues inventory."""
        state = self.manager.state
        # Use clues list as source
        clues = state.clues or []
        clues_list = "\n".join(clues) if clues else ("无线索" if self.current_language == "中文" else "No clues")
        
        popup = tk.Toplevel(self.window)
        popup.title("线索" if self.current_language == "中文" else "Clues")
        popup.geometry("400x300")
        popup.configure(bg="white")
        popup.transient(self.window)
        
        # Center the popup
        popup.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (300 // 2)
        popup.geometry(f"400x300+{x}+{y}")
        
        text_widget = tk.Text(popup, width=40, height=15, font=tkfont.Font(family="微软雅黑", size=12))
        text_widget.pack(padx=10, pady=10)
        text_widget.insert("1.0", clues_list)
        text_widget.config(state=tk.DISABLED)
        
        close_btn = tk.Button(popup, text="关闭" if self.current_language == "中文" else "Close", 
                             command=self._wrap_with_click_sound(popup.destroy))
        close_btn.pack(pady=5)
    
    def show_recall(self):
        """Show recall/history."""
        popup = tk.Toplevel(self.window)
        popup.title("回忆" if self.current_language == "中文" else "Recall")
        popup.geometry("600x400")
        popup.transient(self.window)
        
        text = "回忆功能待实现" if self.current_language == "中文" else "Recall feature not implemented yet"
        label = tk.Label(popup, text=text, font=tkfont.Font(family="微软雅黑", size=14))
        label.pack(padx=20, pady=20)
        
        close_btn = tk.Button(popup, text="关闭" if self.current_language == "中文" else "Close", 
                             command=self._wrap_with_click_sound(popup.destroy))
        close_btn.pack(pady=10)
    
    def toggle_language(self):
        """Toggle between Chinese and English."""
        new_lang = "English" if self.current_language == "中文" else "中文"
        self.current_language = new_lang
        
        # Check if story modal is open
        story_was_open = self.story_modal_open
        if story_was_open and self.story_modal:
            # Close the current story modal
            try:
                self.story_modal.destroy()
            except:
                pass
            self.story_modal = None
            self.story_modal_open = False
        
        # Save current game state before language switch
        saved_mode = self.text_display_mode
        saved_index = self.current_sentence_index
        saved_day = self.manager.current_day
        
        print(f"[DEBUG] Language switch: saving state - day={saved_day}, mode={saved_mode}, index={saved_index}")
        
        # Reload CSV data with new language
        self.csv_loader = CSVTextLoader(language=self.current_language)
        
        # Rebuild entire UI with new language
        self._calculate_scale()
        self._rebuild_ui()
        
        # If story modal was open, reopen it with new language
        if story_was_open:
            header = '故事背景' if self.current_language == "中文" else 'Story background'
            story_text = get_special_text(header, self.current_language)
            if story_text:
                self._show_story_modal(story_text)
        else:
            # Reload current day content in new language
            current_day = self.manager.current_day
            
            # Load appropriate text based on saved mode
            if saved_mode == 'narrative':
                # Reload narrative text in new language
                narrative = self.csv_loader.get_narrative(current_day)
                self.current_text_sentences = self._split_into_sentences(narrative)
                self.current_sentence_index = min(saved_index, len(self.current_text_sentences) - 1)
                self.text_display_mode = 'narrative'
                self._update_text_display()
                
                # Hide choice buttons
                if hasattr(self, 'choice_button_windows'):
                    for btn_window in self.choice_button_windows:
                        self.canvas.itemconfig(btn_window, state='hidden')
                for btn in self.choice_buttons:
                    btn.config(state=tk.DISABLED)
                    
            elif saved_mode == 'choices':
                # In choices mode - clear text and show choice buttons
                self.text_display_mode = 'choices'
                self.canvas.itemconfig(self.narrative_canvas_text, text="")
                
                # Show choice buttons with new language
                options_dict = self.csv_loader.get_options(current_day)
                for i, (choice_key, btn) in enumerate(zip(['A', 'B', 'C'], self.choice_buttons)):
                    option_text = options_dict.get(choice_key, choice_key)
                    btn.config(text=option_text, state=tk.NORMAL)
                    if hasattr(self, 'choice_button_windows') and i < len(self.choice_button_windows):
                        win_id = self.choice_button_windows[i]
                        self.canvas.itemconfig(win_id, state='normal')
                        self.canvas.tag_raise(win_id)
                        
            elif saved_mode == 'result':
                # In result mode - reload result text for the last choice
                if hasattr(self, 'last_choice') and self.last_choice:
                    # Reload result text in new language
                    result_text = self.csv_loader.get_result(current_day, self.last_choice)
                    self.current_text_sentences = self._split_into_sentences(result_text)
                    self.current_sentence_index = min(saved_index, len(self.current_text_sentences) - 1)
                    self.text_display_mode = 'result'
                    self._update_text_display()
                    
                    # Hide choice buttons
                    if hasattr(self, 'choice_button_windows'):
                        for btn_window in self.choice_button_windows:
                            self.canvas.itemconfig(btn_window, state='hidden')
                    for btn in self.choice_buttons:
                        btn.config(state=tk.DISABLED)
                else:
                    # No choice saved - fallback to narrative
                    narrative = self.csv_loader.get_narrative(current_day)
                    self.current_text_sentences = self._split_into_sentences(narrative)
                    self.current_sentence_index = 0
                    self.text_display_mode = 'narrative'
                    self._update_text_display()
                    
                    # Hide choice buttons
                    if hasattr(self, 'choice_button_windows'):
                        for btn_window in self.choice_button_windows:
                            self.canvas.itemconfig(btn_window, state='hidden')
                    for btn in self.choice_buttons:
                        btn.config(state=tk.DISABLED)
            elif saved_mode == 'result_before_ending':
                # In result_before_ending mode - reload result text for the last choice
                if hasattr(self, 'last_choice') and self.last_choice:
                    # Reload result text in new language
                    result_text = self.csv_loader.get_result(current_day, self.last_choice)
                    self.current_text_sentences = self._split_into_sentences(result_text)
                    self.current_sentence_index = min(saved_index, len(self.current_text_sentences) - 1)
                    self.text_display_mode = 'result_before_ending'
                    self._update_text_display()
                    
                    # Reload ending text in new language
                    settlement_text = self.csv_loader.get_settlement(current_day, self.last_choice)
                    if '触发结局：' in settlement_text or '触发结局:' in settlement_text or 'Trigger Ending' in settlement_text:
                        ending_text = settlement_text
                        for keyword in ['触发结局：', '触发结局:', 'Trigger Ending']:
                            if keyword in settlement_text:
                                parts = settlement_text.split(keyword, 1)
                                if len(parts) > 1:
                                    ending_text = keyword + parts[1].strip()
                                break
                        self.pending_ending_text = ending_text
                    
                    # Hide choice buttons
                    if hasattr(self, 'choice_button_windows'):
                        for btn_window in self.choice_button_windows:
                            self.canvas.itemconfig(btn_window, state='hidden')
                    for btn in self.choice_buttons:
                        btn.config(state=tk.DISABLED)
                else:
                    # No choice saved - fallback to narrative
                    narrative = self.csv_loader.get_narrative(current_day)
                    self.current_text_sentences = self._split_into_sentences(narrative)
                    self.current_sentence_index = 0
                    self.text_display_mode = 'narrative'
                    self._update_text_display()
                    
                    # Hide choice buttons
                    if hasattr(self, 'choice_button_windows'):
                        for btn_window in self.choice_button_windows:
                            self.canvas.itemconfig(btn_window, state='hidden')
                    for btn in self.choice_buttons:
                        btn.config(state=tk.DISABLED)
            elif saved_mode == 'transition':
                # In transition mode - reload transition text in new language
                # Transition happens after Day 5, before Day 6
                # current_day should be 5 at this point
                transition_day = 5  # The transition is after Day 5
                transition_text = self.csv_loader.get_transition_text(transition_day)
                
                if transition_text:
                    # Reload Day 56 background (transition uses special background)
                    day56_path = "Day 56.PNG"
                    if os.path.exists(day56_path):
                        print(f"[DEBUG] Language switch: Loading Day 56 background")
                        background_image = Image.open(day56_path)
                        img_w, img_h = background_image.size
                        if img_w > 0 and img_h > 0:
                            cover_scale = max(self.display_width / img_w, self.display_height / img_h)
                            cover_w = max(1, int(img_w * cover_scale))
                            cover_h = max(1, int(img_h * cover_scale))
                            resized = background_image.resize((cover_w, cover_h), Image.Resampling.LANCZOS)
                            
                            left = (cover_w - self.display_width) // 2
                            top = (cover_h - self.display_height) // 2
                            right = left + self.display_width
                            bottom = top + self.display_height
                            cropped = resized.crop((left, top, right, bottom))
                            
                            bg_rgb = cropped.convert('RGB')
                            self.bg_photo = ImageTk.PhotoImage(bg_rgb)
                            
                            # Clear and recreate background
                            self.canvas.delete("all")
                            self.canvas.create_image(0, 0, image=self.bg_photo, anchor='nw')
                            
                            # Load DialogBox (needed for text display)
                            dialog_box_path = "DialogBox.png"
                            if os.path.exists(dialog_box_path):
                                dialog_box = Image.open(dialog_box_path)
                                box_width = int(dialog_box.width * self.scale)
                                box_height = int(dialog_box.height * self.scale)
                                dialog_box = dialog_box.resize((box_width, box_height), Image.Resampling.LANCZOS)
                                self.dialog_box_photo = ImageTk.PhotoImage(dialog_box)
                                x = self.display_width // 2
                                y = self.display_height - (box_height // 2)
                                self.canvas.create_image(x, y, image=self.dialog_box_photo, tags="dialogbox")
                            
                            # Recreate UI elements on top of new background
                            self._create_ui_elements()
                    
                    # Reload transition text in new language
                    self.current_text_sentences = self._split_into_sentences(transition_text)
                    self.current_sentence_index = min(saved_index, len(self.current_text_sentences) - 1)
                    self.text_display_mode = 'transition'
                    self._update_text_display()
                    
                    # Hide choice buttons
                    if hasattr(self, 'choice_button_windows'):
                        for btn_window in self.choice_button_windows:
                            self.canvas.itemconfig(btn_window, state='hidden')
                    for btn in self.choice_buttons:
                        btn.config(state=tk.DISABLED)
                    
                    print(f"[DEBUG] Language switch in transition mode: reloaded {len(self.current_text_sentences)} sentences at index {self.current_sentence_index}")
                else:
                    # No transition text found - fallback to showing current level
                    print("[DEBUG] No transition text found, falling back to show_current_level")
                    if self.manager.get_current_level():
                        self.show_current_level()
            elif saved_mode == 'death_ending_final':
                # In death_ending_final mode - reload ending text in new language
                if hasattr(self, 'current_ending_type') and hasattr(self, 'current_ending_text'):
                    ending_type = self.current_ending_type
                    
                    # Get the appropriate ending text in new language
                    if ending_type == 'stamina':
                        # Stamina death ending
                        ending_text = self.csv_loader.get_death_ending(0, 1)  # stamina=0, mana>0
                    elif ending_type == 'mana':
                        # Mana death ending
                        ending_text = self.csv_loader.get_death_ending(1, 0)  # stamina>0, mana=0
                    elif ending_type == 'both':
                        # Both stats death ending
                        ending_text = self.csv_loader.get_death_ending(0, 0)  # both=0
                    elif ending_type == 'custom':
                        # Custom ending (like Day 15) - need to re-extract from settlement
                        # This is tricky because we don't know which day/choice triggered it
                        # For now, keep the old text (can't translate custom endings dynamically)
                        ending_text = None
                        print("[DEBUG] Cannot translate custom ending - keeping original")
                    else:
                        ending_text = None
                    
                    if ending_text:
                        # Reload death ending screen with new language text
                        self._show_death_ending_black_screen(ending_text, ending_type)
                        print(f"[DEBUG] Language switch in death_ending_final mode: reloaded {ending_type} ending")
                    else:
                        # Can't reload - keep current display
                        print(f"[DEBUG] Cannot reload death ending in new language (type={ending_type})")
                else:
                    print("[DEBUG] No ending type/text saved, cannot reload death ending")
            else:
                # Default: show current level normally
                if self.manager.get_current_level():
                    self.show_current_level()
            
            # Update day label
            if self.current_language == "中文":
                day_text = f"第{number_to_chinese(current_day)}天"
            else:
                day_text = f"Day {current_day}"
            self.canvas.itemconfig(self.day_text_id, text=day_text)
            
            # Update status displays with new language
            self._update_status_display()
            
            # Ensure text is visible
            self.window.after(10, self._ensure_text_visible)
        
        # Call callback if provided
        if self.on_language_change_callback:
            self.on_language_change_callback(new_lang)

    def toggle_fullscreen(self):
        """Toggle fullscreen mode (F11). In fullscreen we try to cover the taskbar by making window fullscreen and topmost."""
        # Use borderless fullscreen to better cover taskbar (overrideredirect)
        enter_fs = not self.is_fullscreen
        self.is_fullscreen = enter_fs

        try:
            if enter_fs:
                # save previous geometry and overrideredirect
                try:
                    self._prev_geometry = self.window.geometry()
                except Exception:
                    self._prev_geometry = None
                try:
                    self._prev_overrideredirect = bool(self.window.overrideredirect())
                except Exception:
                    self._prev_overrideredirect = False

                # set to borderless and cover the whole screen
                screen_w = self.window.winfo_screenwidth()
                screen_h = self.window.winfo_screenheight()
                
                # Force display dimensions to screen size BEFORE overrideredirect
                self.display_width = screen_w
                self.display_height = screen_h
                
                self.window.overrideredirect(True)
                self.window.geometry(f"{screen_w}x{screen_h}+0+0")
                
                # Force window update to apply geometry
                self.window.update_idletasks()
                
                # Reconfigure canvas to exact screen size
                if hasattr(self, 'canvas') and self.canvas:
                    self.canvas.config(width=screen_w, height=screen_h)
                    self.canvas.pack_forget()
                    self.canvas.pack(fill=tk.BOTH, expand=True)
                
                self.window.lift()
                try:
                    self.window.attributes('-topmost', True)
                except Exception:
                    pass
            else:
                # restore windowed state
                try:
                    self.window.overrideredirect(self._prev_overrideredirect)
                except Exception:
                    pass
                try:
                    if self._prev_geometry:
                        self.window.geometry(self._prev_geometry)
                except Exception:
                    pass
                try:
                    self.window.attributes('-topmost', False)
                except Exception:
                    pass
        except Exception:
            pass

        # Force window update before recalculating
        self.window.update_idletasks()
        
        # Recalculate scale and UI to adapt to new screen size
        self._calculate_scale()
        self._rebuild_ui()

    def exit_fullscreen(self):
        if self.is_fullscreen:
            self.toggle_fullscreen()
    
    def on_game_over(self):
        """Handle game over."""
        if self.on_game_over_callback:
            self.on_game_over_callback()
        else:
            # Default game over handling
            popup = tk.Toplevel(self.window)
            popup.title("游戏结束" if self.current_language == "中文" else "Game Over")
            popup.geometry("400x200")
            popup.transient(self.window)
            popup.grab_set()
            
            text = "恭喜完成15天的审判！" if self.current_language == "中文" else "Congratulations on completing 15 days of judgment!"
            label = tk.Label(popup, text=text, font=tkfont.Font(family="微软雅黑", size=14))
            label.pack(padx=20, pady=40)
            
            quit_btn = tk.Button(
                popup,
                text="退出" if self.current_language == "中文" else "Quit",
                command=lambda: [self._play_click_sound(), popup.destroy(), self.window.destroy()]
            )
            quit_btn.pack(pady=10)
