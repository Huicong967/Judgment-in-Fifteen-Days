from typing import Tuple, List, Dict, Optional, Literal
from abc import ABC, abstractmethod
from game.state import GameState
from game.i18n import get_i18n


class Level(ABC):
    """Base class for game levels.
    
    Each level represents a scene or set of scenes in the game.
    """
    
    id: int = 0
    title: str = ""
    
    def __init__(self, language: Literal['zh', 'en'] = 'zh'):
        """Initialize level.
        
        Args:
            language: Game language ('zh' or 'en')
        """
        self.language = language
        self.i18n = get_i18n()
        self.current_scene = 0
    
    def get_title(self) -> str:
        """Get level title.
        
        Returns:
            Localized title string
        """
        return self.i18n.get(f'level{self.id}.title', self.title)
    
    def get_narrative(self) -> str:
        """Get current scene narrative text.
        
        Returns:
            Localized narrative text
        """
        raise NotImplementedError
    
    def get_background(self) -> str:
        """Get background image name.
        
        Returns:
            Background image name
        """
        return "prison_cell"
    
    def get_options(self) -> Dict[str, str]:
        """Get available options for current scene.
        
        Returns:
            Dict mapping option key ('A', 'B', 'C') to option name
        """
        raise NotImplementedError
    
    def handle_choice(self, choice: str, state: GameState) -> Dict:
        """Handle player's choice and return results.
        
        Args:
            choice: Choice code ('A', 'B', 'C')
            state: Current game state
        
        Returns:
            Dict containing:
            - 'narrative': str - Result narrative
            - 'stamina_change': int
            - 'mana_change': int
            - 'bribe_change': int
            - 'sabotage_change': int
            - 'legal_change': int
            - 'items_gained': List[str]
            - 'items_lost': List[str]
        """
        raise NotImplementedError
    
    def is_complete(self) -> bool:
        """Check if level is complete.
        
        Returns:
            True if level has finished
        """
        return True
    
    def play(self, state: GameState) -> Tuple[str, List[str], Dict]:
        """Execute the level's narrative and return choice handlers.
        
        This maintains backward compatibility with the old interface.
        
        Args:
            state: Current game state
        
        Returns:
            Tuple of:
            - intro_text: str - Scene description
            - options: List[str] - Option texts
            - handlers: Dict - Maps option key to result dict
        """
        narrative = self.get_narrative()
        options_dict = self.get_options()
        
        options = [f"[{k}] {options_dict[k]}" for k in ['A', 'B', 'C'] if k in options_dict]
        
        handlers = {}
        for choice_key in ['A', 'B', 'C']:
            if choice_key in options_dict:
                handlers[choice_key] = self.handle_choice(choice_key, state)
        
        return narrative, options, handlers
