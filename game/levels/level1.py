from typing import Tuple, List, Dict, Literal
from game.level import Level
from game.state import GameState
from game.i18n import get_i18n


class Level1(Level):
    """Level 1: Dawn in the Cell."""
    
    id = 1
    title = "第一关：囚室的黎明"
    
    def get_narrative(self) -> str:
        """Get narrative text for this level."""
        return self.i18n.get('level1.scene')
    
    def get_options(self) -> Dict[str, str]:
        """Get available options."""
        return {
            'A': self.i18n.get_level_option('level1', 'A', 'name'),
            'B': self.i18n.get_level_option('level1', 'B', 'name'),
            'C': self.i18n.get_level_option('level1', 'C', 'name'),
        }
    
    def handle_choice(self, choice: str, state: GameState) -> Dict:
        """Handle player's choice."""
        if choice not in ['A', 'B', 'C']:
            return {}
        
        # Get result from i18n
        narrative = self.i18n.get_level_result('level1', choice, 'narrative')
        
        # Get attribute changes
        stamina_change = int(self.i18n.get_level_result('level1', choice, 'stamina_change') or 0)
        mana_change = int(self.i18n.get_level_result('level1', choice, 'mana_change') or 0)
        bribe_change = int(self.i18n.get_level_result('level1', choice, 'bribe_change') or 0)
        sabotage_change = int(self.i18n.get_level_result('level1', choice, 'sabotage_change') or 0)
        legal_change = int(self.i18n.get_level_result('level1', choice, 'legal_change') or 0)
        
        # Get item
        item = self.i18n.get_level_result('level1', choice, 'item')
        items_gained = [item] if item else []
        
        return {
            'narrative': narrative,
            'stamina_change': stamina_change,
            'mana_change': mana_change,
            'bribe_change': bribe_change,
            'sabotage_change': sabotage_change,
            'legal_change': legal_change,
            'items_gained': items_gained,
            'items_lost': [],
        }
    
    def play(self, state: GameState) -> Tuple[str, List[str], Dict]:
        """Play this level (backward compatible)."""
        narrative = self.get_narrative()
        options_dict = self.get_options()
        
        options = [f"[{k}] {options_dict[k]}" for k in ['A', 'B', 'C']]
        
        handlers = {}
        for choice in ['A', 'B', 'C']:
            handlers[choice] = self.handle_choice(choice, state)
        
        return narrative, options, handlers
