"""
完全重新设计的游戏 UI 组件（Canvas 渲染）。
背景图片占满整个窗口，所有 UI 元素由 Canvas 项目绘制和绑定事件，避免不透明 widget 覆盖背景的问题。
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
    """Redesigned main game window with single-canvas rendering."""

    def __init__(self, on_language_change: Optional[Callable] = None,
                 on_tools_click: Optional[Callable] = None,
                 on_clues_click: Optional[Callable] = None,
                 on_choice_selected: Optional[Callable] = None):
        super().__init__()

        self.title("《审判在十五天》")
        # Compute window size to fit the screen while preserving 16:9 ratio
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        target_ratio = 16 / 9
        if screen_w / target_ratio <= screen_h:
            win_w = int(screen_w * 0.95)
            win_h = int(win_w / target_ratio)
        else:
            win_h = int(screen_h * 0.95)
            win_w = int(win_h * target_ratio)

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

        # Canvas covers entire window
        self.canvas = tk.Canvas(self, width=self.win_width, height=self.win_height, highlightthickness=0)
        self.canvas.place(x=0, y=0, width=self.win_width, height=self.win_height)
        self.bg_photo = None
        self._canvas_ids = {}

        # Build UI on canvas
        self._create_layout()

    def set_background_image(self, day: int):
        """Load and draw background image on canvas."""
        self.current_day = day
        filename = f"{day} day.png"
        print(f"Loading background for day {day}: {filename}")

        bg_image = self.image_loader.load_image(filename, size=(self.win_width, self.win_height))
        if bg_image:
            self.bg_photo = bg_image
            if 'bg' in self._canvas_ids:
                self.canvas.itemconfig(self._canvas_ids['bg'], image=self.bg_photo)
            else:
                bg_id = self.canvas.create_image(0, 0, image=self.bg_photo, anchor='nw')
                self._canvas_ids['bg'] = bg_id
                self.canvas.tag_lower(bg_id)
            # record background bounding box (x1,y1,x2,y2) for layout reference
            self._bg_bbox = (0, 0, float(self.win_width), float(self.win_height))
            # draw debug rectangles: canvas border (blue) and background bbox (red)
            # remove existing debug boxes if present
            if 'debug_canvas_box' in self._canvas_ids:
                try:
                    self.canvas.delete(self._canvas_ids['debug_canvas_box'])
                except Exception:
                    pass
            if 'debug_bg_box' in self._canvas_ids:
                try:
                    self.canvas.delete(self._canvas_ids['debug_bg_box'])
                except Exception:
                    pass
            # canvas box equals full canvas
            cb = self.canvas.create_rectangle(0, 0, self.win_width, self.win_height, outline='blue', width=2)
            bb = self.canvas.create_rectangle(self._bg_bbox[0], self._bg_bbox[1], self._bg_bbox[2], self._bg_bbox[3], outline='red', width=2)
            self._canvas_ids['debug_canvas_box'] = cb
            self._canvas_ids['debug_bg_box'] = bb
            print(f"Background image loaded successfully: {self.win_width}x{self.win_height}")
            try:
                coords = self.canvas.coords(self._canvas_ids['bg'])
                print(f"Background canvas id={self._canvas_ids['bg']} coords={coords}")
            except Exception:
                print("Background canvas id exists but coords unavailable")
        else:
            print(f"Failed to load background image: {filename}")

    def _create_layout(self):
        """Create canvas-based UI items and then place them by ratio."""
        print("[DEBUG] _create_layout: start creating canvas UI items")
        self._create_left_panel()
        self._create_language_button()
        self._create_bottom_panel()

        # choices container ids list
        self._canvas_ids['choices'] = []

        self._layout_elements_by_ratio()
        print("[DEBUG] _create_layout: finished; canvas ids keys:", list(self._canvas_ids.keys()))

    def _create_left_panel(self):
        """Create left-side canvas items (titles, bars, clues button)."""
        print("[DEBUG] _create_left_panel: creating left panel items")
        self._canvas_ids['left_title'] = self.canvas.create_text(0, 0, text='【属性】', font=('Arial', 13, 'bold'), fill=Colors.ACCENT, anchor='nw')

        self._canvas_ids['stamina_title'] = self.canvas.create_text(0, 0, text='体力值', font=('Arial', 10, 'bold'), fill=Colors.TEXT_PRIMARY, anchor='nw')
        self._canvas_ids['stamina_bg'] = self.canvas.create_rectangle(0, 0, 1, 1, fill=Colors.BG_MEDIUM, outline='')
        self._canvas_ids['stamina_fill'] = self.canvas.create_rectangle(0, 0, 1, 1, fill=Colors.STATUS_STAMINA, outline='')
        self._canvas_ids['stamina_text'] = self.canvas.create_text(0, 0, text='20/50', font=('Arial', 9), fill=Colors.STATUS_STAMINA, anchor='nw')

        self._canvas_ids['mana_title'] = self.canvas.create_text(0, 0, text='魔力值', font=('Arial', 10, 'bold'), fill=Colors.TEXT_PRIMARY, anchor='nw')
        self._canvas_ids['mana_bg'] = self.canvas.create_rectangle(0, 0, 1, 1, fill=Colors.BG_MEDIUM, outline='')
        self._canvas_ids['mana_fill'] = self.canvas.create_rectangle(0, 0, 1, 1, fill=Colors.STATUS_MANA, outline='')
        self._canvas_ids['mana_text'] = self.canvas.create_text(0, 0, text='20/50', font=('Arial', 9), fill=Colors.STATUS_MANA, anchor='nw')

        clues_photo = self.image_loader.load_image('button for clues.png', size=(int(self.win_width * 0.08), int(self.win_height * 0.06)))
        if clues_photo:
            self._clues_photo = clues_photo
            clues_id = self.canvas.create_image(0, 0, image=self._clues_photo, anchor='nw')
            self._canvas_ids['clues_btn'] = clues_id
            self.canvas.tag_bind(clues_id, '<Button-1>', lambda e: self._on_clues_click())
            self._canvas_ids['clues_label'] = self.canvas.create_text(0, 0, text='线索', font=('Arial', 12, 'bold'), fill='white', anchor='center')
            print(f"[DEBUG] _create_left_panel: clues image loaded, id={clues_id}")
        else:
            print("[DEBUG] _create_left_panel: clues image NOT found")

    def _create_language_button(self):
        """Create a language image button on canvas."""
        lang_photo = self.image_loader.load_image('languege change.png', size=(int(self.win_width * 0.06), int(self.win_height * 0.06)))
        if lang_photo:
            self._lang_photo = lang_photo
            lang_id = self.canvas.create_image(0, 0, image=self._lang_photo, anchor='nw')
            self._canvas_ids['lang_btn'] = lang_id
            self.canvas.tag_bind(lang_id, '<Button-1>', lambda e: self._on_language_click())
            self._canvas_ids['lang_label'] = self.canvas.create_text(0, 0, text=('语言' if self.current_language == 'zh' else 'Lang'), font=('Arial', 10, 'bold'), fill='white', anchor='center')
            print(f"[DEBUG] _create_language_button: lang image loaded, id={lang_id}")
        else:
            print("[DEBUG] _create_language_button: lang image NOT found")

    def _create_bottom_panel(self):
        """Create bottom text box background, content and bottom buttons on canvas."""
        text_bg_photo = self.image_loader.load_image('Text box.png', size=(int(self.win_width * 0.95), int(self.win_height * 0.12)))
        if text_bg_photo:
            self._text_bg_photo = text_bg_photo
            text_bg_id = self.canvas.create_image(0, 0, image=self._text_bg_photo, anchor='nw')
            self._canvas_ids['text_bg'] = text_bg_id
            print(f"[DEBUG] _create_bottom_panel: text_bg id={text_bg_id}")

        self._canvas_ids['text_content'] = self.canvas.create_text(0, 0, text='', font=('Arial', 11), fill='white', anchor='nw', width=int(self.win_width * 0.90))

        recall_photo = self.image_loader.load_image('recall.png', size=(int(self.win_width * 0.06), int(self.win_height * 0.06)))
        if recall_photo:
            self._recall_photo = recall_photo
            recall_id = self.canvas.create_image(0, 0, image=self._recall_photo, anchor='nw')
            self._canvas_ids['recall_btn'] = recall_id
            self.canvas.tag_bind(recall_id, '<Button-1>', lambda e: self._on_recall())
            print(f"[DEBUG] _create_bottom_panel: recall id={recall_id}")

        continue_photo = self.image_loader.load_image('continue.png', size=(int(self.win_width * 0.06), int(self.win_height * 0.06)))
        if continue_photo:
            self._continue_photo = continue_photo
            continue_id = self.canvas.create_image(0, 0, image=self._continue_photo, anchor='nw')
            self._canvas_ids['continue_btn'] = continue_id
            self.canvas.tag_bind(continue_id, '<Button-1>', lambda e: self._on_continue())
            print(f"[DEBUG] _create_bottom_panel: continue id={continue_id}")

    def _layout_elements_by_ratio(self):
        """Place UI elements using ratios so they always sit within the background image bounds."""
        # Use background bbox as layout reference when available
        w = self.win_width
        h = self.win_height
        if hasattr(self, '_bg_bbox') and self._bg_bbox:
            bg_x, bg_y, bg_w, bg_h = self._bg_bbox
            # bg_w/bg_h currently stored as x2,y2 - x1,y1 are full width/height
            layout_x = int(bg_x)
            layout_y = int(bg_y)
            layout_w = int(bg_w)
            layout_h = int(bg_h)
        else:
            layout_x, layout_y, layout_w, layout_h = 0, 0, w, h

        left_x = layout_x + int(layout_w * 0.10)
        top_margin = layout_y + int(layout_h * 0.02)
        small_gap = int(layout_h * 0.025)

        # Left column
        self.canvas.coords(self._canvas_ids['left_title'], left_x, top_margin)
        y_pos = top_margin + int(layout_h * 0.05)

        # stamina
        self.canvas.coords(self._canvas_ids['stamina_title'], left_x, y_pos)
        y_pos += small_gap
        bar_w = int(layout_w * 0.12)
        bar_h = int(layout_h * 0.02)
        self.canvas.coords(self._canvas_ids['stamina_bg'], left_x, y_pos, left_x + bar_w, y_pos + bar_h)
        # default fill 40%
        self.canvas.coords(self._canvas_ids['stamina_fill'], left_x, y_pos, left_x + int(bar_w * 0.4), y_pos + bar_h)
        self.canvas.coords(self._canvas_ids['stamina_text'], left_x, y_pos + bar_h + 2)
        y_pos += small_gap

        # mana
        self.canvas.coords(self._canvas_ids['mana_title'], left_x, y_pos)
        y_pos += small_gap
        self.canvas.coords(self._canvas_ids['mana_bg'], left_x, y_pos, left_x + bar_w, y_pos + bar_h)
        self.canvas.coords(self._canvas_ids['mana_fill'], left_x, y_pos, left_x + int(bar_w * 0.4), y_pos + bar_h)
        self.canvas.coords(self._canvas_ids['mana_text'], left_x, y_pos + bar_h + 2)
        y_pos += int(h * 0.05)

        # clues
        if 'clues_btn' in self._canvas_ids:
            btn_w = int(w * 0.08)
            btn_h = int(h * 0.06)
            self.canvas.coords(self._canvas_ids['clues_btn'], left_x, y_pos)
            self.canvas.coords(self._canvas_ids['clues_label'], left_x + btn_w // 2, y_pos + btn_h // 2)

        # language on right
        right_x = layout_x + int(layout_w * 0.90)
        lang_w = int(layout_w * 0.06)
        lang_h = int(layout_h * 0.06)
        if 'lang_btn' in self._canvas_ids:
            self.canvas.coords(self._canvas_ids['lang_btn'], right_x, top_margin)
            self.canvas.coords(self._canvas_ids['lang_label'], right_x + lang_w // 2, top_margin + lang_h // 2)

        # bottom text box
        text_h = int(layout_h * 0.12)
        text_w = int(layout_w * 0.95)
        text_x = layout_x + int(layout_w * 0.025)
        text_y = layout_y + layout_h - text_h - int(layout_h * 0.02)
        if 'text_bg' in self._canvas_ids:
            self.canvas.coords(self._canvas_ids['text_bg'], text_x, text_y)
        self.canvas.coords(self._canvas_ids['text_content'], text_x + int(layout_w * 0.01), text_y + int(layout_h * 0.015))

        # recall / continue
        if 'recall_btn' in self._canvas_ids:
            recall_w = int(w * 0.06)
            recall_h = int(h * 0.06)
            self.canvas.coords(self._canvas_ids['recall_btn'], text_x, text_y + text_h + int(layout_h * 0.01))
        if 'continue_btn' in self._canvas_ids:
            cont_w = int(layout_w * 0.06)
            cont_h = int(layout_h * 0.06)
            self.canvas.coords(self._canvas_ids['continue_btn'], layout_x + layout_w - cont_w - int(layout_w * 0.025), text_y + text_h + int(layout_h * 0.01))

    def display_choices(self, choices: Dict[str, str]):
        """Display choices as canvas images + text in center."""
        # clear previous choices
        for cid in list(self._canvas_ids.get('choices', [])):
            try:
                self.canvas.delete(cid)
            except Exception:
                pass
        self._canvas_ids['choices'] = []

        btn_photo = self.image_loader.load_image('ABC.png', size=(int(self.win_width * 0.4), int(self.win_height * 0.08)))
        cx = self.win_width // 2
        cy = self.win_height // 2
        y = cy - int(self.win_height * 0.08)
        for choice in ['A', 'B', 'C']:
            if choice in choices:
                if btn_photo:
                    img_id = self.canvas.create_image(cx, y, image=btn_photo, anchor='n')
                    self._canvas_ids['choices'].append(img_id)
                    # bind click by tag
                    self.canvas.tag_bind(img_id, '<Button-1>', lambda e, c=choice: self._on_choice_selected(c))
                    # text below image
                    text_id = self.canvas.create_text(cx, y + int(self.win_height * 0.085), text=f"【{choice}】 {choices[choice]}", font=('Arial', 11), fill='white', width=int(self.win_width * 0.45))
                    self._canvas_ids['choices'].append(text_id)
                    y += int(self.win_height * 0.18)

    def display_text(self, text: str):
        """Show narrative text in canvas text content and save history."""
        self.text_history.append(text)
        if 'text_content' in self._canvas_ids:
            self.canvas.itemconfig(self._canvas_ids['text_content'], text=text)

    def set_narrative(self, text: str):
        self.display_text(text)

    def show_choice_buttons(self, choices: Dict[str, str]):
        self.display_choices(choices)

    def hide_choice_buttons(self):
        for cid in list(self._canvas_ids.get('choices', [])):
            try:
                self.canvas.delete(cid)
            except Exception:
                pass
        self._canvas_ids['choices'] = []

    def update_properties(self, stamina: int, mana: int = None, max_stamina: int = 100, max_mana: int = 100):
        """Update the canvas-drawn stamina and mana bars and texts."""
        if mana is None:
            mana = stamina

        # Update text
        if 'stamina_text' in self._canvas_ids:
            self.canvas.itemconfig(self._canvas_ids['stamina_text'], text=f"{stamina}/{max_stamina}")
        if 'mana_text' in self._canvas_ids:
            self.canvas.itemconfig(self._canvas_ids['mana_text'], text=f"{mana}/{max_mana}")

        # Update bars: compute current bar background coords
        if 'stamina_bg' in self._canvas_ids:
            x1, y1, x2, y2 = self.canvas.coords(self._canvas_ids['stamina_bg'])
            width = max(1, int(x2 - x1))
            ratio = (stamina / max_stamina) if max_stamina > 0 else 0
            fill_w = int(width * ratio)
            self.canvas.coords(self._canvas_ids['stamina_fill'], x1, y1, x1 + fill_w, y2)

        if 'mana_bg' in self._canvas_ids:
            x1, y1, x2, y2 = self.canvas.coords(self._canvas_ids['mana_bg'])
            width = max(1, int(x2 - x1))
            ratio = (mana / max_mana) if max_mana > 0 else 0
            fill_w = int(width * ratio)
            self.canvas.coords(self._canvas_ids['mana_fill'], x1, y1, x1 + fill_w, y2)

    def _on_language_click(self):
        if self.on_language_change:
            self.on_language_change()

    def _on_recall(self):
        if len(self.text_history) > 1:
            self.text_history.pop()
            previous_text = self.text_history[-1]
            self.display_text(previous_text)

    def _on_continue(self):
        pass

    def _on_clues_click(self):
        if self.on_clues_click:
            self.on_clues_click()

    def _on_choice_selected(self, choice: str):
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
        title = tk.Label(self.popup, text="工具", font=('Arial', 14, 'bold'), fg=Colors.ACCENT)
        title.pack(pady=10)

        # Items list
        for item in self.items:
            item_label = tk.Label(self.popup, text=f"• {item}", font=('Arial', 11), fg='white', bg=Colors.BG_DARK)
            item_label.pack(anchor='w', padx=20, pady=5)

        # Close button
        close_btn = tk.Button(self.popup, text="关闭", command=self.popup.destroy, font=('Arial', 11), bg=Colors.BG_MEDIUM, fg='white')
        close_btn.pack(pady=20)

    def destroy(self):
        if self.popup:
            self.popup.destroy()
