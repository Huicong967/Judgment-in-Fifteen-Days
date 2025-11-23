from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class GameState:
    stamina: int = 10  # 体力 (Initial: 10)
    mana: int = 10     # 魔力 (Initial: 10)
    max_stamina: int = 50
    max_mana: int = 50
    bribe_progress: int = 0
    sabotage_progress: int = 0
    legal_progress: int = 0
    mystery_progress: int = 0  # ？线进度
    inventory: List[str] = field(default_factory=list)  # 道具
    clues: List[str] = field(default_factory=list)  # 线索

    def apply_change(self, stamina_delta=0, mana_delta=0,
                     bribe_delta=0, sabotage_delta=0, legal_delta=0, mystery_delta=0,
                     add_items: List[str]=None, remove_items: List[str]=None,
                     add_clues: List[str]=None, remove_clues: List[str]=None):
        # Clamp values between 0 and their respective maxima
        self.stamina = min(self.max_stamina, max(0, self.stamina + stamina_delta))
        self.mana = min(self.max_mana, max(0, self.mana + mana_delta))
        self.bribe_progress = max(0, self.bribe_progress + bribe_delta)
        self.sabotage_progress = max(0, self.sabotage_progress + sabotage_delta)
        self.legal_progress = max(0, self.legal_progress + legal_delta)
        self.mystery_progress = max(0, self.mystery_progress + mystery_delta)
        if add_items:
            for it in add_items:
                if it not in self.inventory:
                    self.inventory.append(it)
        if remove_items:
            for it in remove_items:
                if it in self.inventory:
                    self.inventory.remove(it)
        if add_clues:
            for clue in add_clues:
                if clue not in self.clues:
                    self.clues.append(clue)
        if remove_clues:
            for clue in remove_clues:
                if clue in self.clues:
                    self.clues.remove(clue)

    def snapshot(self) -> Dict:
        return {
            "stamina": self.stamina,
            "mana": self.mana,
            "bribe_progress": self.bribe_progress,
            "sabotage_progress": self.sabotage_progress,
            "legal_progress": self.legal_progress,
            "mystery_progress": self.mystery_progress,
            "inventory": list(self.inventory),
            "clues": list(self.clues),
        }
