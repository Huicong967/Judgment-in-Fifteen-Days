"""
游戏UI组件 - 使用PIL合成UI到背景图像上。
Game UI components - compositing UI onto background using PIL.
"""

import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk, ImageFilter
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
        # Allow user to resize window; elements will reflow on resize
        self.resizable(True, True)
        
        self.on_language_change = on_language_change
        self.on_tools_click = on_tools_click
        self.on_clues_click = on_clues_click
        self.on_choice_selected = on_choice_selected
        
        # Image loader
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.image_loader = ImageLoader(root_dir)

        # Base design resolution (aspect ratio reference)
        self.base_w = 1920
        self.base_h = 1080

        # compute scale based on current screen size to fit the 16:9 canvas
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        # scale to fit screen while preserving aspect ratio
        self.scale = min(screen_w / self.base_w, screen_h / self.base_h)

        self.current_day = 1
        self.current_language = 'zh'
        self.text_history = []
        self.current_stamina = 20
        self.current_mana = 20
        self.tools: List[str] = []
        self.center_overlay_id = None
        
        # Compute window size based on scale and screen available area
        # Leave a small margin so the window isn't obscured by taskbar or window borders
        margin = 48
        desired_w = int(self.base_w * self.scale)
        desired_h = int(self.base_h * self.scale)
        win_w = min(desired_w, max(100, screen_w - margin))
        win_h = min(desired_h, max(100, screen_h - margin))

        # Center the window on the screen
        pos_x = max(0, (screen_w - win_w) // 2)
        pos_y = max(0, (screen_h - win_h) // 2)

        # Main canvas to display composited image (scaled)
        self.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.config(bg='black')
        self.resizable(False, False)

        self.canvas = tk.Canvas(self, width=win_w, height=win_h, bg='black',
                       highlightthickness=0, borderwidth=0)
        self.canvas.place(x=0, y=0, width=win_w, height=win_h)
        
        self.bg_image_id = None
        self.bg_photo = None

        # Resize debounce id
        self._resize_after_id = None
        # Bind configure events so UI can adapt when window is resized
        try:
            self.bind('<Configure>', self._on_configure)
        except Exception:
            pass
        
        # Load scaled UI images (keep references to avoid GC)
        # helper to scale ints
        def s(v):
            return max(1, int(v * self.scale))

        self.win_w = win_w
        self.win_h = win_h

        self.clues_photo = self.image_loader.load_image('button for clues.png', size=(s(80), s(80)))
        self.tools_photo = self.image_loader.load_image('button for tools.png', size=(s(80), s(80)))
        self.lang_photo = self.image_loader.load_image('language change.png', size=(s(80), s(80)))
        self.textbox_photo = self.image_loader.load_image('Text box.png', size=(win_w, s(200)))
        self.recall_photo = self.image_loader.load_image('recall.png', size=(s(64), s(64)))
        self.continue_photo = self.image_loader.load_image('continue.png', size=(s(64), s(64)))
        self.choice_photo = self.image_loader.load_image('option.png', size=(s(420), s(120)))

        # create layout after images are loaded so placements use self.win_w/self.win_h
        self._create_layout()

        # Apply images to buttons (if loaded)
        self._apply_button_images()
        # Temporarily bring window to front and print geometry for debugging
        try:
            self.update_idletasks()
            # set topmost briefly so the window appears above others
            try:
                self.attributes('-topmost', True)
            except Exception:
                pass
            x = self.winfo_x()
            y = self.winfo_y()
            w = self.winfo_width()
            h = self.winfo_height()
            print(f"[UI] window geometry: x={x} y={y} w={w} h={h}")

            def _clear_topmost():
                try:
                    self.attributes('-topmost', False)
                except Exception:
                    pass
                try:
                    print(f"[UI] window geometry after clear: x={self.winfo_x()} y={self.winfo_y()} w={self.winfo_width()} h={self.winfo_height()}")
                except Exception:
                    pass

            # remove topmost after 2 seconds
            try:
                self.after(2000, _clear_topmost)
            except Exception:
                pass
        except Exception as e:
            print(f"[UI] error printing geometry: {e}")

    def _on_configure(self, event):
        """Handle window configure (resize/move). Debounce heavy redraw operations."""
        try:
            # Only handle root window size changes
            if event.widget is not self:
                return
            # update width/height from event
            new_w = max(100, event.width)
            new_h = max(100, event.height)
            # store tentative sizes
            self.win_w = new_w
            self.win_h = new_h
            # reposition canvas to fill window
            try:
                self.canvas.place(x=0, y=0, width=new_w, height=new_h)
            except Exception:
                pass
            # debounce actual heavy redraw (set_background_image)
            if self._resize_after_id:
                try:
                    self.after_cancel(self._resize_after_id)
                except Exception:
                    pass
            self._resize_after_id = self.after(200, lambda: self._on_resize_end())
        except Exception:
            pass

    def _on_resize_end(self):
        """Called after resize debounce timer expires. Redraw background and reposition overlays."""
        try:
            self._resize_after_id = None
            # redraw background for current day with new canvas size
            try:
                self.set_background_image(self.current_day)
            except Exception:
                pass
            # reapply button images (ensure correct sizing)
            try:
                self._apply_button_images()
            except Exception:
                pass
        except Exception:
            pass
    
    def _create_layout(self):
        """Create layout with composited UI."""
        # helper to scale base pixels
        def s(v):
            return max(1, int(v * self.scale))

        # RIGHT TOP - Language Button (overlay) as image button
        self.language_button = tk.Button(self, image=None, command=self._on_language_click,
                                         relief=tk.FLAT, bd=0, highlightthickness=0)
        lang_x = self.win_w - s(80) - s(20)
        self.language_button.place(x=lang_x, y=s(20), width=s(80), height=s(80))

        # Fullscreen toggle button next to language button
        self.fullscreen = False
        self.fullscreen_btn = tk.Button(self, text='全屏', command=self._on_fullscreen_toggle,
                                        relief=tk.FLAT, bd=0, highlightthickness=0, bg='#222', fg='#fff')
        try:
            self.fullscreen_btn.place(x=lang_x - s(90), y=s(20), width=s(80), height=s(80))
        except Exception:
            pass
        
        # BOTTOM TEXT (we'll draw narrative directly on the canvas so the Text box image shows through)
        # make narrative font slightly larger for readability
        text_font_size = max(10, int(20 * self.scale))
        self.text_font = ('Arial', text_font_size)
        tb_h = max(1, int(200 * self.scale))
        tb_x = s(10)
        tb_y = self.win_h - tb_h + s(10)
        tb_w = self.win_w - s(20)
        # canvas text id for narrative
        self.canvas_text_id = self.canvas.create_text(tb_x + s(20), tb_y + s(10), text='',
                                  anchor='nw', fill='#eaeaea', font=self.text_font,
                                  width=tb_w - s(40))
        
        # Recall and Continue buttons (image buttons) placed inside the bottom textbox area
        # recall/continue buttons will show image with centered text
        self.recall_btn = tk.Button(self, image=None, text='回忆', compound='center', command=self._on_recall, relief=tk.FLAT, bd=0,
                        fg='#ffffff')
        recall_y = self.win_h - tb_h + s(10) + (tb_h - s(20) - s(64))
        self.recall_btn.place(x=s(30), y=recall_y, width=s(64), height=s(64))

        self.continue_btn = tk.Button(self, image=None, text='继续', compound='center', command=self._on_continue, relief=tk.FLAT, bd=0,
                          fg='#ffffff')
        self.continue_btn.place(x=self.win_w - s(64) - s(30), y=recall_y, width=s(64), height=s(64))
        
        # Choice buttons container (center)
        self.choice_buttons_frame = None

        # Left-side clues/tools placeholder buttons (will be set with images)
        # clues/tools buttons show image with center text overlay
        self.clues_btn = tk.Button(self, image=None, text='线索', compound='center', command=self._on_clues_click, relief=tk.FLAT, bd=0,
                   fg='#ffffff')
        # moved further left for tighter alignment with left edge
        self.clues_btn.place(x=s(2), y=s(180), width=s(80), height=s(80))

        self.tools_btn = tk.Button(self, image=None, text='道具', compound='center', command=self._on_tools_click, relief=tk.FLAT, bd=0,
                   fg='#ffffff')
        # moved further left for tighter alignment with left edge
        self.tools_btn.place(x=s(2), y=s(260), width=s(80), height=s(80))
    
    def _on_language_click(self):
        """Handle language button click."""
        # Toggle language between 'zh' and 'en'
        self.current_language = 'en' if self.current_language == 'zh' else 'zh'
        if self.on_language_change:
            try:
                self.on_language_change(self.current_language)
            except TypeError:
                # fallback to older callback signature
                self.on_language_change()
    
    def _on_recall(self):
        """Handle recall button click."""
        if len(self.text_history) > 1:
            self.text_history.pop()
            self._display_text(self.text_history[-1])
        print(f"[DEBUG] recall pressed, text_index now {len(self.text_history)-1}")
    
    def _on_continue(self):
        """Handle continue button click."""
        print("[DEBUG] continue pressed (window)")
        # call the bound handler if runner attached one
        handler = getattr(self, '_on_continue_handler', None)
        if callable(handler):
            try:
                handler()
            except Exception as e:
                print(f"Error calling continue handler: {e}")
        return

    def _on_tools_click(self):
        """Handle tools button click: show center overlay with tool name or open popup."""
        if self.tools:
            # show the first tool name in center (non-modal)
            self.show_center_overlay(self.tools[0])
        else:
            # open popup listing tools
            ToolsPopup(self, self.tools)

    def _on_clues_click(self):
        """Handle clues button click."""
        if self.on_clues_click:
            self.on_clues_click()
    
    def _display_text(self, text: str):
        """Display text in widget."""
        # Update canvas text inside the textbox area
        try:
            self.canvas.itemconfig(self.canvas_text_id, text=text)
        except Exception:
            # fallback: keep history but do nothing
            pass
    
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

    def _draw_label_bg(self, draw, x: int, y: int, w: int, h: int, fill=(0,0,0,160)):
        """Draw a semi-opaque rectangle behind labels for readability."""
        draw.rectangle([x, y, x + w, y + h], fill=fill)
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def set_background_image(self, day: int):
        """Set background image based on day with composited UI."""
        filename = f"{day} day.png"
        filepath = os.path.join(self.image_loader.root_dir, filename)
        
        try:
            # Load original image and resize to fit the current window size while preserving entire image (no crop)
            img = Image.open(filepath).convert('RGBA')
            orig_width, orig_height = img.size

            # compute target display area so all day images share a similar visual size
            target_display_w = int(self.win_w * 0.96)
            target_display_h = int(self.win_h * 0.92)
            # compute scale so the whole image fits into the target display area
            fit_scale = min(target_display_w / orig_width, target_display_h / orig_height)
            new_w = max(1, int(orig_width * fit_scale))
            new_h = max(1, int(orig_height * fit_scale))

            img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # create a visually-consistent fullscreen background even when aspect ratios differ
            # approach: create a blurred, cover-resized background from the original image,
            # then paste the full, fit-resized image centered on top (no cropping of main subject)
            try:
                cover = img.resize((self.win_w, self.win_h), Image.Resampling.LANCZOS)
                # apply gentle blur to make overlaid main image readable
                cover = cover.filter(ImageFilter.GaussianBlur(radius=18)).convert('RGB')
            except Exception:
                cover = Image.new('RGB', (self.win_w, self.win_h), (0, 0, 0))

            offset_x = (self.win_w - new_w) // 2
            offset_y = (self.win_h - new_h) // 2
            # paste the fit-resized (complete) image on top of the blurred cover
            cover.paste(img_resized.convert('RGB'), (offset_x, offset_y))
            bg = cover

            # Create a copy for drawing (draw on bg so UI overlays match image area)
            img_display = bg.convert('RGB')
            draw = ImageDraw.Draw(img_display)

            # helper to scale base coords relative to the image area
            image_draw_scale_x = new_w / self.base_w
            image_draw_scale_y = new_h / self.base_h
            def si_x(v):
                return int(offset_x + v * image_draw_scale_x)
            def si_y(v):
                return int(offset_y + v * image_draw_scale_y)

            # Draw left sidebar UI elements (scaled positions relative to image)
            # Title (with small background for readability)
            title_x, title_y = si_x(20), si_y(15)
            tbw, tbh = int(120 * image_draw_scale_x), int(24 * image_draw_scale_y)
            try:
                self._draw_label_bg(draw, title_x - int(4 * image_draw_scale_x), title_y - int(4 * image_draw_scale_y), tbw, tbh, fill=(10,10,10))
            except Exception:
                pass
            draw.text((title_x, title_y), "【属性】", fill=self._hex_to_rgb('#00d4ff'),
                     font=self._get_font(max(10, int(14 * min(image_draw_scale_x, image_draw_scale_y))), bold=True))

            # Stamina
            label_x, label_y = si_x(20), si_y(45)
            try:
                self._draw_label_bg(draw, label_x - int(4 * image_draw_scale_x), label_y - int(4 * image_draw_scale_y), int(120 * image_draw_scale_x), int(20 * image_draw_scale_y), fill=(8,8,8))
            except Exception:
                pass
            draw.text((label_x, label_y), "体力值", fill=self._hex_to_rgb('#eaeaea'),
                     font=self._get_font(max(10, int(12 * min(image_draw_scale_x, image_draw_scale_y))), bold=True))

            # Stamina progress bar
            self._draw_progress_bar(draw, si_x(20), si_y(67), int(220 * image_draw_scale_x), int(18 * image_draw_scale_y), self.current_stamina, 50,
                                   self._hex_to_rgb('#ff6b6b'))

            # Stamina value
            draw.text((si_x(20), si_y(85)), f"{self.current_stamina}/50", fill=self._hex_to_rgb('#ff6b6b'),
                     font=self._get_font(max(10, int(11 * min(image_draw_scale_x, image_draw_scale_y)))))

            # Mana
            mlabel_x, mlabel_y = si_x(20), si_y(107)
            try:
                self._draw_label_bg(draw, mlabel_x - int(4 * image_draw_scale_x), mlabel_y - int(4 * image_draw_scale_y), int(120 * image_draw_scale_x), int(20 * image_draw_scale_y), fill=(8,8,8))
            except Exception:
                pass
            draw.text((mlabel_x, mlabel_y), "魔力值", fill=self._hex_to_rgb('#eaeaea'),
                     font=self._get_font(max(10, int(12 * min(image_draw_scale_x, image_draw_scale_y))), bold=True))

            # Mana progress bar
            self._draw_progress_bar(draw, si_x(20), si_y(129), int(220 * image_draw_scale_x), int(18 * image_draw_scale_y), self.current_mana, 50,
                                   self._hex_to_rgb('#4ecdc4'))

            # Mana value
            draw.text((si_x(20), si_y(147)), f"{self.current_mana}/50", fill=self._hex_to_rgb('#4ecdc4'),
                     font=self._get_font(max(10, int(11 * min(image_draw_scale_x, image_draw_scale_y)))))

            # Paste textbox image at bottom of the displayed image area (if available as file)
            try:
                tb_path = os.path.join(self.image_loader.root_dir, 'Text box.png')
                if os.path.exists(tb_path):
                    tb_img = Image.open(tb_path).convert('RGBA')
                    tb_h_scaled = int(200 * min(image_draw_scale_x, image_draw_scale_y))
                    tb_target = tb_img.resize((new_w, tb_h_scaled), Image.Resampling.LANCZOS)
                    paste_x = offset_x
                    paste_y = offset_y + new_h - tb_h_scaled
                    img_display.paste(tb_target.convert('RGB'), (paste_x, paste_y))
            except Exception:
                pass

            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img_display)

            # Delete old image
            if self.bg_image_id:
                self.canvas.delete(self.bg_image_id)

            # Display on canvas
            self.bg_image_id = self.canvas.create_image(0, 0, image=photo, anchor='nw')
            self.bg_photo = photo
            self.current_day = day
            # record bg offset and size for overlay positioning
            self._bg_offset = (offset_x, offset_y)
            self._bg_size = (new_w, new_h)

            # reposition overlay widgets (buttons, text) to align with image
            try:
                tb_h_scaled = int(200 * min(image_draw_scale_x, image_draw_scale_y))
                self._position_overlay_widgets(offset_x, offset_y, new_w, new_h, tb_h_scaled)
            except Exception:
                pass

            # Ensure narrative text and other canvas items are above the background image
            try:
                if getattr(self, 'canvas_text_id', None):
                    self.canvas.tag_raise(self.canvas_text_id, self.bg_image_id)
            except Exception:
                pass

            print(f"Loaded background for day {day}")
        except Exception as e:
            print(f"Error loading background: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_font(self, size: int, bold: bool = False) -> object:
        """Get font object."""
        # Try a list of common fonts that include Chinese glyphs on Windows
        candidates = [
            ("msyh.ttc", size),
            ("msyh.ttf", size),
            ("SimHei.ttf", size),
            ("simsun.ttc", size),
            ("arial.ttf", size),
            ("arialbd.ttf", size),
        ]
        for name, sz in candidates:
            try:
                return ImageFont.truetype(name, sz)
            except Exception:
                continue
        # Fallback to default PIL font (may not support CJK)
        return ImageFont.load_default()

    def _apply_button_images(self):
        """Apply loaded PhotoImage objects to tkinter Buttons."""
        try:
            # Set image + centered text for each button so label appears on top of image
            if getattr(self, 'lang_photo', None) and self.lang_photo:
                self.language_button.config(image=self.lang_photo, compound='center')
            if getattr(self, 'clues_photo', None) and self.clues_photo:
                self.clues_btn.config(image=self.clues_photo, compound='center')
            if getattr(self, 'tools_photo', None) and self.tools_photo:
                self.tools_btn.config(image=self.tools_photo, compound='center')
            if getattr(self, 'recall_photo', None) and self.recall_photo:
                self.recall_btn.config(image=self.recall_photo, compound='center')
            if getattr(self, 'continue_photo', None) and self.continue_photo:
                self.continue_btn.config(image=self.continue_photo, compound='center')
        except Exception as e:
            print(f"Error applying button images: {e}")

    def _position_overlay_widgets(self, ox: int, oy: int, img_w: int, img_h: int, tb_h: int):
        """Position image-overlay widgets (buttons and canvas text) relative to the background image."""
        def s(v):
            return max(1, int(v * min(img_w / self.base_w, img_h / self.base_h)))

        # language button: right-top inside image
        lang_x = ox + img_w - s(80) - s(20)
        lang_y = oy + s(20)
        try:
            self.language_button.place(x=lang_x, y=lang_y, width=s(80), height=s(80))
        except Exception:
            pass

        # clues/tools left-side
        try:
            self.clues_btn.place(x=ox + s(20), y=oy + s(180), width=s(80), height=s(80))
            self.tools_btn.place(x=ox + s(20), y=oy + s(260), width=s(80), height=s(80))
        except Exception:
            pass

        # place fullscreen button next to language button
        try:
            fs_x = ox + img_w - s(80) - s(20) - s(90)
            fs_y = oy + s(20)
            self.fullscreen_btn.place(x=fs_x, y=fs_y, width=s(80), height=s(80))
        except Exception:
            pass

        # recall / continue inside textbox area
        recall_x = ox + s(30)
        recall_y = oy + img_h - tb_h + s(10) + max(0, (tb_h - s(20) - s(64)))
        try:
            self.recall_btn.place(x=recall_x, y=recall_y, width=s(64), height=s(64))
            self.continue_btn.place(x=ox + img_w - s(64) - s(30), y=recall_y, width=s(64), height=s(64))
        except Exception:
            pass

        # move canvas text into textbox area
        try:
            text_x = ox + s(20)
            text_y = oy + img_h - tb_h + s(10)
            text_w = img_w - s(40)
            self.canvas.coords(self.canvas_text_id, text_x, text_y)
            self.canvas.itemconfig(self.canvas_text_id, width=text_w)
        except Exception:
            pass

    def show_center_overlay(self, text: str, timeout: int = 1500):
        """Show a transient centered label with the given text."""
        # Remove existing
        if self.center_overlay_id:
            try:
                self.center_overlay_id.destroy()
            except Exception:
                pass
            self.center_overlay_id = None

        lbl_font_size = max(10, int(18 * self.scale))
        lbl = tk.Label(self, text=text, font=('Arial', lbl_font_size, 'bold'), bg='#000000', fg='#ffffff')
        lbl.place(relx=0.5, rely=0.45, anchor=tk.CENTER)
        self.center_overlay_id = lbl

        def _clear():
            try:
                lbl.destroy()
            except Exception:
                pass
            if self.center_overlay_id == lbl:
                self.center_overlay_id = None

        self.after(timeout, _clear)

    def _on_fullscreen_toggle(self):
        """Toggle fullscreen mode for the window."""
        try:
            self.fullscreen = not self.fullscreen
            if self.fullscreen:
                try:
                    self.attributes('-fullscreen', True)
                except Exception:
                    # fall back to maximize
                    self.state('zoomed')
                self.fullscreen_btn.config(text='退出')
            else:
                try:
                    self.attributes('-fullscreen', False)
                except Exception:
                    try:
                        self.state('normal')
                    except Exception:
                        pass
                self.fullscreen_btn.config(text='全屏')
                # restore to centered geometry
                try:
                    screen_w = self.winfo_screenwidth()
                    screen_h = self.winfo_screenheight()
                    margin = 48
                    desired_w = int(self.base_w * self.scale)
                    desired_h = int(self.base_h * self.scale)
                    win_w = min(desired_w, max(100, screen_w - margin))
                    win_h = min(desired_h, max(100, screen_h - margin))
                    pos_x = max(0, (screen_w - win_w) // 2)
                    pos_y = max(0, (screen_h - win_h) // 2)
                    self.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
                except Exception:
                    pass
        except Exception as e:
            print(f"Error toggling fullscreen: {e}")
    
    def set_narrative(self, text: str):
        """Set narrative text in text box."""
        self.text_history.append(text)
        self._display_text(text)
    
    def show_choice_buttons(self, choices: Dict[str, str]):
        """Show choice buttons in center."""
        if self.choice_buttons_frame:
            self.choice_buttons_frame.destroy()
        self.choice_buttons_frame = tk.Frame(self)
        # move the group further upward (was rely=0.38)
        self.choice_buttons_frame.place(relx=0.5, rely=0.34, anchor=tk.CENTER)

        for choice in ['A', 'B', 'C']:
            if choice in choices:
                # Use image button with text overlay (compound center)
                choice_font_size = max(10, int(14 * self.scale))
                wraplen = max(100, int(380 * self.scale))
                btn = tk.Button(
                    self.choice_buttons_frame,
                    text=f"{choice} {choices[choice]}",
                    font=('Arial', choice_font_size, 'bold'),
                    image=self.choice_photo if getattr(self, 'choice_photo', None) else None,
                    compound='center',
                    fg='#ffffff',
                    wraplength=wraplen,
                    justify=tk.CENTER,
                    relief=tk.FLAT,
                    bd=0,
                    highlightthickness=0,
                    command=lambda c=choice: self.on_choice_selected(c) if self.on_choice_selected else None,
                )
                btn.pack(fill=tk.X, expand=False, pady=12)
    
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
