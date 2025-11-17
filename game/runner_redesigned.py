"""
Game runner using the redesigned UI (1920x1080).
使用重新设计的UI运行游戏。
"""

import tkinter as tk
from typing import Optional, Dict

from game.gui.language_selector import select_language
from game.gui.widgets_redesigned import GameWindowRedesigned, ToolsPopup
from game.i18n import set_language, get_i18n
from game.manager import LevelManager
from game.state import GameState


class GUIGameRunnerRedesigned:
    """Game runner with redesigned UI (1920x1080)."""
    
    def __init__(self):
        """Initialize game runner."""
        # Select language first
        language = select_language()
        set_language(language)
        
        # Initialize game state and manager
        self.state = GameState()
        self.manager = LevelManager()
        self.current_level = None
        self.i18n = get_i18n()
        self.choice_buttons_visible = False
        self.text_index = 0
        self.day_texts = []  # Store all texts for a day
        
        # Create main window
        self.window = GameWindowRedesigned(
            on_language_change=self.on_language_change,
            on_tools_click=self.on_tools_click,
            on_clues_click=self.on_clues_click,
            on_choice_selected=self.on_choice_selected
        )
        
        # Setup callbacks
        self.window._on_recall = self.on_recall_click
        self.window._on_continue = self.on_continue_click
        
        # Start game
        self.start_game()
        
        # Start main loop
        self.window.mainloop()
    
    def start_game(self):
        """Start the game - show first level."""
        self.manager.current_day = 1
        self.show_current_level()
    
    def show_current_level(self):
        """Display current level's narrative."""
        try:
            if not self.current_level:
                self.current_level = self.manager.get_level(self.manager.current_day)
            
            if not self.current_level:
                self.show_game_over()
                return
            
            # Get narrative
            narrative_text = self.current_level.get_narrative()
            
            # Split narrative by sentences or paragraphs
            # For now, treat whole narrative as one
            self.day_texts = [narrative_text]
            self.text_index = 0
            
            # Set background
            self.window.set_background_image(self.manager.current_day)
            
            # Update properties
            self._update_properties_display()
            
            # Show first text
            self.window.set_narrative(self.day_texts[0])
            
            # Reset choice buttons
            self.choice_buttons_visible = False
            self.window.hide_choice_buttons()
        
        except Exception as e:
            print(f"Error showing level: {e}")
            import traceback
            traceback.print_exc()
    
    def on_recall_click(self):
        """Handle recall button click."""
        if self.text_index > 0:
            self.text_index -= 1
            self.window.set_narrative(self.day_texts[self.text_index])
            self.choice_buttons_visible = False
            self.window.hide_choice_buttons()
    
    def on_continue_click(self):
        """Handle continue button click."""
        if self.choice_buttons_visible:
            # Already showing choices, user clicked continue but should click choice
            return
        
        # Check if there's next text
        if self.text_index < len(self.day_texts) - 1:
            self.text_index += 1
            self.window.set_narrative(self.day_texts[self.text_index])
        else:
            # Show choice buttons
            self.choice_buttons_visible = True
            options_dict = self.current_level.get_options()
            self.window.show_choice_buttons(options_dict)
    
    def on_choice_selected(self, choice: str):
        """Handle choice selection."""
        if not self.current_level or choice not in ['A', 'B', 'C']:
            return
        
        try:
            # Hide choice buttons
            self.window.hide_choice_buttons()
            self.choice_buttons_visible = False
            
            # Get result
            result = self.current_level.handle_choice(choice, self.state)
            
            # Update state
            self.state.stamina += result.get('stamina_change', 0)
            self.state.mana += result.get('mana_change', 0)
            self.state.bribe_progress += result.get('bribe_change', 0)
            self.state.sabotage_progress += result.get('sabotage_change', 0)
            self.state.legal_progress += result.get('legal_change', 0)
            
            # Add items
            for item in result.get('items_gained', []):
                if item not in self.state.inventory:
                    self.state.inventory.append(item)
            
            # Show result narrative
            result_narrative = result.get('narrative', '')
            self.day_texts.append(result_narrative)
            self.text_index = len(self.day_texts) - 1
            self.window.set_narrative(result_narrative)
            
            # Update properties
            self._update_properties_display()
            
            # Move to next day
            self.manager.current_day += 1
            self.current_level = None
            
            # Show next level
            self.show_current_level()
        
        except Exception as e:
            print(f"Error handling choice: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_properties_display(self):
        """Update property panel display."""
        self.window.update_properties(
            self.state.stamina,
            self.state.mana
        )
    
    def on_language_change(self):
        """Handle language change."""
        new_language = 'en' if self.i18n.language == 'zh' else 'zh'
        set_language(new_language)
        self.i18n = get_i18n()
        
        # Refresh current display
        if self.current_level:
            self.show_current_level()
    
    def on_tools_click(self):
        """Handle tools button click."""
        popup = ToolsPopup(self.window, self.state.inventory)
    
    def on_clues_click(self):
        """Handle clues button click."""
        # Show clues popup
        clues_text = "这是游戏线索。\n点击关闭此窗口。" if self.i18n.language == 'zh' else "These are game clues.\nClick to close this window."
        popup = tk.Toplevel(self.window)
        popup.title(self.i18n.get_ui_text('clues'))
        popup.geometry("400x300")
        popup.config(bg='#16213e')
        popup.transient(self.window)
        popup.grab_set()
        
        text_widget = tk.Text(
            popup,
            font=('Arial', 11),
            bg='#16213e',
            fg='#eaeaea',
            wrap=tk.WORD
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert('1.0', clues_text)
        text_widget.config(state=tk.DISABLED)
    
    def show_game_over(self):
        """Show game over screen."""
        popup = tk.Toplevel(self.window)
        popup.title("游戏结束" if self.i18n.language == 'zh' else "Game Over")
        popup.geometry("400x200")
        popup.config(bg='#1a1a2e')
        popup.transient(self.window)
        popup.grab_set()
        
        label = tk.Label(
            popup,
            text="游戏结束！" if self.i18n.language == 'zh' else "Game Over!",
            font=('Arial', 16, 'bold'),
            bg='#1a1a2e',
            fg='#00d4ff'
        )
        label.pack(expand=True)
        
        close_btn = tk.Button(
            popup,
            text="关闭" if self.i18n.language == 'zh' else "Close",
            bg='#00d4ff',
            fg='#1a1a2e',
            font=('Arial', 10, 'bold'),
            command=self.window.destroy
        )
        close_btn.pack(pady=10)


if __name__ == "__main__":
    runner = GUIGameRunnerRedesigned()
