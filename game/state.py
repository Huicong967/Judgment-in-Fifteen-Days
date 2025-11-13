from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class GameState:
    stamina: int = 20  # 体力 (Initial: 20, Max: 50)
    mana: int = 20     # 魔力 (Initial: 20, Max: 50)
    bribe_progress: int = 0
    sabotage_progress: int = 0
    legal_progress: int = 0
    inventory: List[str] = field(default_factory=list)

    def apply_change(self, stamina_delta=0, mana_delta=0,
                     bribe_delta=0, sabotage_delta=0, legal_delta=0,
                     add_items: List[str]=None, remove_items: List[str]=None):
        self.stamina = max(0, self.stamina + stamina_delta)
        self.mana = max(0, self.mana + mana_delta)
        self.bribe_progress = max(0, self.bribe_progress + bribe_delta)
        self.sabotage_progress = max(0, self.sabotage_progress + sabotage_delta)
        self.legal_progress = max(0, self.legal_progress + legal_delta)
        if add_items:
            for it in add_items:
                if it not in self.inventory:
                    self.inventory.append(it)
        if remove_items:
            for it in remove_items:
                if it in self.inventory:
                    self.inventory.remove(it)

    def snapshot(self) -> Dict:
        return {
            "stamina": self.stamina,
            "mana": self.mana,
            "bribe_progress": self.bribe_progress,
            "sabotage_progress": self.sabotage_progress,
            "legal_progress": self.legal_progress,
            "inventory": list(self.inventory),
        }
