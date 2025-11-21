import csv
import os
from typing import Dict, Optional, List


class CSVTextLoader:
    """Load game text from CSV files."""
    
    def __init__(self, language='中文'):
        self.language = language
        self.data = {}
        self._load_csv()
    
    def _load_csv(self):
        """Load CSV file based on language."""
        filename = "Chinese Text.csv" if self.language == "中文" else "English Text.csv"
        
        # Try multiple possible paths
        possible_paths = [
            filename,  # Current directory
            os.path.join(os.path.dirname(__file__), '..', filename),  # Parent of game folder
            os.path.join(os.getcwd(), filename),  # Working directory
        ]
        
        filepath = None
        for path in possible_paths:
            if os.path.exists(path):
                filepath = path
                break
        
        if not filepath:
            print(f"[ERROR] CSV file not found. Tried: {possible_paths}")
            return
        
        print(f"[INFO] Loading CSV from: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:  # Use utf-8-sig to handle BOM
                reader = csv.DictReader(f)
                row_count = 0
                for row in reader:
                    row_count += 1
                    day_str = row.get('天数', '')
                    if not day_str or not day_str.strip():
                        continue
                    
                    # Extract day number from "第X天 ..." format
                    try:
                        day_str = day_str.strip()
                        if '第' in day_str and '天' in day_str:
                            # Extract number between 第 and 天
                            parts = day_str.split('第')
                            if len(parts) > 1:
                                num_part = parts[1].split('天')[0].strip()
                                day_num = int(num_part)
                            else:
                                continue
                        else:
                            continue
                    except (ValueError, IndexError) as e:
                        print(f"[DEBUG] Failed to parse day from '{day_str}': {e}")
                        continue
                    
                    self.data[day_num] = {
                        'narrative': row.get('叙述文本', '').strip(),
                        'option_a': row.get('A', '').strip(),
                        'option_b': row.get('B', '').strip(),
                        'option_c': row.get('C', '').strip(),
                        'result_a': row.get('A结果文本', '').strip(),
                        'result_b': row.get('B结果文本', '').strip(),
                        'result_c': row.get('C结果文本', '').strip(),
                        'settlement_a': row.get('A系统结算', '').strip(),
                        'settlement_b': row.get('B系统结算', '').strip(),
                        'settlement_c': row.get('C系统结算', '').strip(),
                    }
                    print(f"[DEBUG] Loaded day {day_num}: {day_str}")
                
                print(f"[DEBUG] Processed {row_count} rows total")
            
            print(f"[INFO] Loaded {len(self.data)} days from {filename}")
        except Exception as e:
            print(f"[ERROR] Failed to load CSV: {e}")
            import traceback
            traceback.print_exc()
    
    def get_narrative(self, day: int) -> str:
        """Get narrative text for a specific day."""
        return self.data.get(day, {}).get('narrative', f'第{day}天叙述文本未找到')
    
    def get_options(self, day: int) -> Dict[str, str]:
        """Get options A, B, C for a specific day."""
        day_data = self.data.get(day, {})
        return {
            'A': day_data.get('option_a', '选项A'),
            'B': day_data.get('option_b', '选项B'),
            'C': day_data.get('option_c', '选项C')
        }
    
    def get_result(self, day: int, choice: str) -> str:
        """Get result text for a specific day and choice."""
        day_data = self.data.get(day, {})
        key = f'result_{choice.lower()}'
        return day_data.get(key, f'{choice}选项结果文本未找到')
    
    def get_settlement(self, day: int, choice: str) -> str:
        """Get settlement text for a specific day and choice."""
        day_data = self.data.get(day, {})
        key = f'settlement_{choice.lower()}'
        return day_data.get(key, '')
    
    def parse_settlement(self, settlement_text: str) -> Dict:
        """Parse settlement text to extract stat changes and items.
        
        Format examples:
        - 体力-5
        - 魔力+5
        - 获得线索：xxx
        - 获得道具：xxx
        """
        result = {
            'stamina_change': 0,
            'mana_change': 0,
            'bribe_change': 0,
            'sabotage_change': 0,
            'legal_change': 0,
            'items_gained': [],
            'clues_gained': []
        }
        
        if not settlement_text:
            return result
        
        lines = settlement_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Parse stat changes
            if '体力' in line:
                try:
                    if '+' in line:
                        result['stamina_change'] = int(line.split('+')[1])
                    elif '-' in line:
                        result['stamina_change'] = -int(line.split('-')[1])
                except (ValueError, IndexError):
                    pass
            
            if '魔力' in line:
                try:
                    if '+' in line:
                        result['mana_change'] = int(line.split('+')[1])
                    elif '-' in line:
                        result['mana_change'] = -int(line.split('-')[1])
                except (ValueError, IndexError):
                    pass
            
            # Parse items and clues
            if '获得道具：' in line or '获得道具:' in line:
                item = line.split('：')[-1].split(':')[-1].strip()
                if item:
                    result['items_gained'].append(item)
            
            if '获得线索：' in line or '获得线索:' in line:
                clue = line.split('：')[-1].split(':')[-1].strip()
                if clue:
                    result['clues_gained'].append(clue)
            
            # Parse progress changes
            if '贿赂' in line and ('推进' in line or '+' in line or '-' in line):
                result['bribe_change'] = 1  # Simplified: just increment
            
            if '破坏' in line and ('推进' in line or '+' in line or '-' in line):
                result['sabotage_change'] = 1
            
            if '法学' in line or '文书' in line:
                if '推进' in line or '+' in line or '-' in line:
                    result['legal_change'] = 1
        
        return result
