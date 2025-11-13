"""
GUI game runner using the new redesigned interface.
使用新 UI 设计的游戏运行器。
"""

import tkinter as tk
from typing import Optional, Dict

from game.gui.language_selector import select_language
from game.gui.widgets_new import GameWindow, ResultWindow, Colors
from game.i18n import set_language, get_i18n
from game.manager import LevelManager
from game.state import GameState


class ChoiceButtonsFrame(tk.Frame):
    """Frame for displaying choice buttons in the image area."""
    
    def __init__(self, parent, choices: Dict[str, str], callback, **kwargs):
        super().__init__(parent, bg=Colors.BG_DARK, **kwargs)
        
        self.i18n = get_i18n()
        self.callback = callback
        self.buttons = []
        
        # Create a main container that fills available space
        container = tk.Frame(self, bg=Colors.BG_DARK)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title = tk.Label(
            container,
            text=self.i18n.get_ui_text('choose_action'),
            font=('Arial', 12, 'bold'),
            bg=Colors.BG_DARK,
            fg=Colors.ACCENT
        )
        title.pack(pady=10)
        
        # Buttons frame - horizontal layout
        buttons_frame = tk.Frame(container, bg=Colors.BG_DARK)
        buttons_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create choice buttons
        for choice in ['A', 'B', 'C']:
            if choice in choices:
                btn = tk.Button(
                    buttons_frame,
                    text=f"【 {choice} 】\n{choices[choice]}",
                    font=('Arial', 9, 'bold'),
                    bg=Colors.ACCENT,
                    fg=Colors.BG_DARK,
                    cursor='hand2',
                    wraplength=120,
                    command=lambda c=choice: self._on_choice(c),
                    justify=tk.CENTER,
                    padx=5,
                    pady=8
                )
                btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
                self.buttons.append(btn)
    
    def _on_choice(self, choice: str):
        """Handle choice button click."""
        if self.callback:
            self.callback(choice)


class GUIGameRunner:
    """Game runner with new GUI interface."""
    
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
        self.choice_buttons = None
        
        # Create main window
        self.window = GameWindow()
        self._update_window_title()
        
        # Set up callbacks
        self.window.narrative_panel.on_continue_click = self.on_continue_click
        
        # Start game
        self.start_game()
    
    def _update_window_title(self):
        """Update window title with current day."""
        day = self.manager.current_day
        self.window.title(
            f"《审判在十五天》- Day {day}/15"
            if self.i18n.language == 'zh'
            else f"Judgment in Fifteen Days - Day {day}/15"
        )
    
    def start_game(self):
        """Initialize and display first level."""
        try:
            level_instance = self.manager.get_current_level()
            self.current_level = level_instance
            
            if level_instance:
                self.show_current_level()
            else:
                self.show_game_over()
        
        except Exception as e:
            print(f"Error starting game: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(str(e))
    
    def show_current_level(self):
        """Display current level's narrative."""
        try:
            if not self.current_level:
                self.show_game_over()
                return
            
            # Get narrative
            narrative_text = self.current_level.get_narrative()
            self.window.set_narrative(narrative_text)
            
            # Set background
            bg_name = self.current_level.get_background()
            self.window.set_background_image(bg_name)
            
            # Update properties display
            self._update_properties_display()
            
            # Update day counter
            self._update_window_title()
            
            # Show continue button and narrative text
            self.window.narrative_panel.show_narrative_text(True)
            self.window.narrative_panel.show_continue_button(True)
            
            # Hide choice buttons if they exist
            if self.choice_buttons:
                self.choice_buttons.destroy()
                self.choice_buttons = None
        
        except Exception as e:
            print(f"Error showing level: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(str(e))
    
    def on_continue_click(self):
        """Handle 'continue' button click to show choice options."""
        if not self.current_level:
            return
        
        try:
            # Get options
            options_dict = self.current_level.get_options()
            
            # Hide continue button and narrative text
            self.window.narrative_panel.show_continue_button(False)
            self.window.narrative_panel.show_narrative_text(False)
            
            # Show choice buttons in image area
            self._show_choice_buttons(options_dict)
        
        except Exception as e:
            print(f"Error showing options: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(str(e))
    
    def _show_choice_buttons(self, options_dict: Dict[str, str]):
        """Show choice buttons in the image panel.
        
        Args:
            options_dict: Dict mapping 'A', 'B', 'C' to option names
        """
        # Destroy existing buttons if any
        if self.choice_buttons:
            self.choice_buttons.destroy()
        
        # Create choice buttons frame
        self.choice_buttons = ChoiceButtonsFrame(
            self.window.image_panel,
            options_dict,
            self.on_choice_selected
        )
        self.choice_buttons.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    def on_choice_selected(self, choice: str):
        """Handle choice selection.
        
        Args:
            choice: Choice code ('A', 'B', 'C')
        """
        if not self.current_level or choice not in ['A', 'B', 'C']:
            return
        
        try:
            # Hide choice buttons
            if self.choice_buttons:
                self.choice_buttons.destroy()
                self.choice_buttons = None
            
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
                    self.window.add_item(item)
            
            # Prepare changes dict for display
            changes = {}
            if result.get('stamina_change'):
                changes['体力' if self.i18n.language == 'zh' else 'Stamina'] = result['stamina_change']
            if result.get('mana_change'):
                changes['魔力' if self.i18n.language == 'zh' else 'Mana'] = result['mana_change']
            if result.get('bribe_change'):
                changes['贿赂' if self.i18n.language == 'zh' else 'Bribe'] = result['bribe_change']
            if result.get('sabotage_change'):
                changes['破坏' if self.i18n.language == 'zh' else 'Sabotage'] = result['sabotage_change']
            if result.get('legal_change'):
                changes['法学' if self.i18n.language == 'zh' else 'Legal'] = result['legal_change']
            
            item = result.get('items_gained', [None])[0] if result.get('items_gained') else None
            
            # Show result dialog
            result_window = ResultWindow(
                self.window,
                result['narrative'],
                changes,
                item
            )
            
            self.window.wait_window(result_window)
            
            # Update properties display
            self._update_properties_display()
            
            # Prepare for next level/scene
            self.manager.current_day += 1
            self.show_current_level()
        
        except Exception as e:
            print(f"Error handling choice: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(str(e))
    
    def _update_properties_display(self):
        """Update property panel display."""
        self.window.update_properties(
            self.state.stamina,
            self.state.mana,
            self.state.bribe_progress,
            self.state.sabotage_progress,
            self.state.legal_progress
        )
    
    def show_game_over(self):
        """Show game over screen."""
        self.window.set_narrative(
            "游戏结束" if self.i18n.language == 'zh' else "Game Over"
        )
    
    def show_error(self, message: str):
        """Show error message.
        
        Args:
            message: Error message
        """
        error_text = f"错误: {message}" if self.i18n.language == 'zh' else f"Error: {message}"
        self.window.set_narrative(error_text)
    
    def run(self):
        """Start the game."""
        self.window.mainloop()


def main():
    """Main entry point."""
    runner = GUIGameRunner()
    runner.run()


if __name__ == '__main__':
    main()
