from typing import Tuple, List, Dict
from game.level import Level
from game.state import GameState
from game.i18n import get_i18n

class LevelFromI18n(Level):
    """Generic level that reads content from i18n files using keys like level{n}."""

    def __init__(self, level_id: int):
        super().__init__()
        self.id = level_id
        self.i18n = get_i18n()

    def get_narrative(self) -> str:
        return self.i18n.get(f'level{self.id}.scene', '')

    def get_options(self) -> Dict[str, str]:
        return {
            k: self.i18n.get_level_option(f'level{self.id}', k, 'name')
            for k in ['A', 'B', 'C']
            if self.i18n.get_level_option(f'level{self.id}', k, 'name')
        }

    def handle_choice(self, choice: str, state: GameState) -> Dict:
        if choice not in ['A', 'B', 'C']:
            return {}

        narrative = self.i18n.get_level_result(f'level{self.id}', choice, 'narrative')
        stamina_change = int(self.i18n.get_level_result(f'level{self.id}', choice, 'stamina_change') or 0)
        mana_change = int(self.i18n.get_level_result(f'level{self.id}', choice, 'mana_change') or 0)
        bribe_change = int(self.i18n.get_level_result(f'level{self.id}', choice, 'bribe_change') or 0)
        sabotage_change = int(self.i18n.get_level_result(f'level{self.id}', choice, 'sabotage_change') or 0)
        legal_change = int(self.i18n.get_level_result(f'level{self.id}', choice, 'legal_change') or 0)
        item = self.i18n.get_level_result(f'level{self.id}', choice, 'item')
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
        narrative = self.get_narrative()
        options_dict = self.get_options()
        options = [f"[{k}] {options_dict[k]}" for k in options_dict]
        handlers = {k: self.handle_choice(k, state) for k in options_dict}
        return narrative, options, handlers
