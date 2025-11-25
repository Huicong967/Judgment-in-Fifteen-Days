from typing import Dict, List, Optional
from game.state import GameState
from game.level import Level
from game.levels.csv_level import LevelFromCSV

class LevelManager:
    """
    管理游戏流程：15 天倒计时、关卡序列、胜负判定。
    """
    def __init__(self):
        # Initialize levels dynamically from CSV
        self.levels: Dict[int, Level] = {}
        
        # Load all levels from CSV (days 1-15)
        for day in range(1, 16):
            try:
                lvl = LevelFromCSV(day)
                # only use if CSV actually contains the day
                if lvl and lvl.get_narrative():
                    self.levels[day] = lvl
            except Exception:
                # ignore if creation fails
                pass
        
        self.current_day = 1
        self.max_days = 15
        self.state = GameState()

    def get_level(self, day: int) -> Optional[Level]:
        """获取指定天数对应的关卡（暂时只有第1关）"""
        return self.levels.get(day, None)
    
    def get_current_level(self) -> Optional[Level]:
        """获取当前天数的关卡"""
        return self.get_level(self.current_day)

    def is_game_over(self) -> bool:
        """检查是否已到达执行时刻（第15天结束）"""
        return self.current_day > self.max_days

    def check_win_condition(self) -> bool:
        """
        检查是否满足越狱成功条件：
        三条线中任意一条达到或超过 5，且相应资源满足最低要求。
        """
        # 贿赂线：需要 bribe_progress >= 5 且 stamina > 0
        bribe_win = self.state.bribe_progress >= 5 and self.state.stamina > 0

        # 破坏线：需要 sabotage_progress >= 5 且 stamina > 2（破坏需要体力）
        sabotage_win = self.state.sabotage_progress >= 5 and self.state.stamina > 2

        # 法学线：需要 legal_progress >= 5 且 mana > 1（文书需要魔力）
        legal_win = self.state.legal_progress >= 5 and self.state.mana > 1

        return bribe_win or sabotage_win or legal_win

    def check_loss_condition(self) -> bool:
        """
        检查是否满足失败条件：
        - 体力与魔力均为 0（无法继续活动）
        - 或到达第15天且未满足胜利条件（被处死）
        """
        if self.state.stamina == 0 and self.state.mana == 0:
            return True
        if self.current_day > self.max_days and not self.check_win_condition():
            return True
        return False

    def get_day_description(self) -> str:
        """获取当前天数描述"""
        return f"第 {self.current_day} 天 / 共 {self.max_days} 天"

    def get_status_snapshot(self) -> Dict:
        """获取当前游戏状态快照"""
        return {
            "day": self.current_day,
            "max_days": self.max_days,
            **self.state.snapshot(),
        }

    def advance_day(self):
        """推进到下一天"""
        self.current_day += 1

    def execute_level(self, level: Level):
        """
        执行一个关卡：获取叙述与选项，返回给玩家，
        等待选择，应用变动，返回结算文本。
        """
        intro, options, handlers = level.play(self.state)
        return intro, options, handlers
