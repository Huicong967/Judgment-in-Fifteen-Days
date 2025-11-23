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
        
        # Column name mappings for different languages
        if self.language == "中文":
            col_map = {
                'day': '天数',
                'narrative': '叙述文本',
                'option_a': 'A',
                'option_b': 'B',
                'option_c': 'C',
                'result_a': 'A结果文本',
                'result_b': 'B结果文本',
                'result_c': 'C结果文本',
                'settlement_a': 'A系统结算',
                'settlement_b': 'B系统结算',
                'settlement_c': 'C系统结算',
            }
        else:  # English
            col_map = {
                'day': 'Days',
                'narrative': 'narrative text',
                'option_a': 'A',
                'option_b': 'B',
                'option_c': 'C',
                'result_a': 'A Result text',
                'result_b': 'B Result text',
                'result_c': 'C Result Text',
                'settlement_a': 'A System Settlement',
                'settlement_b': 'B System Settlement',
                'settlement_c': 'C System Settlement',
            }
        
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
                last_day_num = 0
                for row in reader:
                    row_count += 1
                    day_str = row.get(col_map['day'], '')
                    
                    # Check if this is a transition row (no day number but has narrative)
                    if not day_str or not day_str.strip():
                        narrative = row.get(col_map['narrative'], '').strip()
                        if narrative and last_day_num > 0:
                            # This is a transition after last_day_num
                            transition_key = f'transition_{last_day_num}'
                            self.data[transition_key] = {
                                'narrative': narrative,
                            }
                            print(f"[DEBUG] Loaded transition after day {last_day_num}")
                        continue
                    
                    # Extract day number from "第X天 ..." format (Chinese) or "Day X ..." format (English)
                    try:
                        day_str = day_str.strip()
                        if self.language == "中文":
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
                        else:  # English
                            if 'Day' in day_str:
                                # Extract number after "Day"
                                parts = day_str.split('Day')
                                if len(parts) > 1:
                                    num_part = parts[1].strip().split()[0]  # Get first word after "Day"
                                    day_num = int(num_part)
                                else:
                                    continue
                            else:
                                continue
                    except (ValueError, IndexError) as e:
                        print(f"[DEBUG] Failed to parse day from '{day_str}': {e}")
                        continue
                    
                    self.data[day_num] = {
                        'narrative': row.get(col_map['narrative'], '').strip(),
                        'option_a': row.get(col_map['option_a'], '').strip(),
                        'option_b': row.get(col_map['option_b'], '').strip(),
                        'option_c': row.get(col_map['option_c'], '').strip(),
                        'result_a': row.get(col_map['result_a'], '').strip(),
                        'result_b': row.get(col_map['result_b'], '').strip(),
                        'result_c': row.get(col_map['result_c'], '').strip(),
                        'settlement_a': row.get(col_map['settlement_a'], '').strip(),
                        'settlement_b': row.get(col_map['settlement_b'], '').strip(),
                        'settlement_c': row.get(col_map['settlement_c'], '').strip(),
                    }
                    print(f"[DEBUG] Loaded day {day_num}: {day_str}")
                    last_day_num = day_num
                
                print(f"[DEBUG] Processed {row_count} rows total")
            
            print(f"[INFO] Loaded {len(self.data)} days from {filename}")
        except Exception as e:
            print(f"[ERROR] Failed to load CSV: {e}")
            import traceback
            traceback.print_exc()
    
    def get_narrative(self, day: int) -> str:
        """Get narrative text for a specific day."""
        if self.language == "中文":
            return self.data.get(day, {}).get('narrative', f'第{day}天叙述文本未找到')
        else:
            return self.data.get(day, {}).get('narrative', f'Day {day} narrative text not found')
    
    def get_options(self, day: int) -> Dict[str, str]:
        """Get options A, B, C for a specific day."""
        day_data = self.data.get(day, {})
        if self.language == "中文":
            return {
                'A': day_data.get('option_a', '选项A'),
                'B': day_data.get('option_b', '选项B'),
                'C': day_data.get('option_c', '选项C')
            }
        else:
            return {
                'A': day_data.get('option_a', 'Option A'),
                'B': day_data.get('option_b', 'Option B'),
                'C': day_data.get('option_c', 'Option C')
            }
    
    def get_result(self, day: int, choice: str) -> str:
        """Get result text for a specific day and choice."""
        day_data = self.data.get(day, {})
        key = f'result_{choice.lower()}'
        if self.language == "中文":
            return day_data.get(key, f'{choice}选项结果文本未找到')
        else:
            return day_data.get(key, f'Option {choice} result text not found')
    
    def get_settlement(self, day: int, choice: str) -> str:
        """Get settlement text for a specific day and choice."""
        day_data = self.data.get(day, {})
        key = f'settlement_{choice.lower()}'
        return day_data.get(key, '')
    
    def get_transition_text(self, after_day: int) -> Optional[str]:
        """Get transition text that appears after a specific day.
        
        Transitions are stored in rows between day entries (天数 column is empty).
        For example, the transition after day 5 appears in the row between day 5 and day 6.
        """
        # In the CSV data structure, we need to check if there's a special entry
        # Let's use a special key format: transition_X where X is the day number
        transition_key = f'transition_{after_day}'
        if transition_key in self.data:
            return self.data[transition_key].get('narrative', '')
        return None
    
    def parse_settlement(self, settlement_text: str) -> Dict:
        """Parse settlement text to extract stat changes and items.
        
        Format examples:
        Chinese: 体力-5, 魔力+5, 获得线索：xxx, 获得道具：xxx
        English: Strength -5, Magic +5, Get clue: xxx, Item: xxx
        """
        result = {
            'stamina_change': 0,
            'mana_change': 0,
            'bribe_change': 0,
            'sabotage_change': 0,
            'legal_change': 0,
            'mystery_change': 0,
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
            
            # Parse stat changes (Chinese)
            if '体力' in line:
                try:
                    if '+' in line:
                        result['stamina_change'] = int(line.split('+')[1].split()[0])
                    elif '-' in line:
                        result['stamina_change'] = -int(line.split('-')[1].split()[0])
                except (ValueError, IndexError):
                    pass
            
            if '魔力' in line:
                try:
                    if '+' in line:
                        result['mana_change'] = int(line.split('+')[1].split()[0])
                    elif '-' in line:
                        result['mana_change'] = -int(line.split('-')[1].split()[0])
                except (ValueError, IndexError):
                    pass
            
            # Parse stat changes (English)
            if 'Strength' in line or 'strength' in line:
                try:
                    if '+' in line:
                        result['stamina_change'] = int(line.split('+')[1].split()[0])
                    elif '-' in line:
                        result['stamina_change'] = -int(line.split('-')[1].split()[0])
                except (ValueError, IndexError):
                    pass
            
            if 'Magic' in line or 'magic' in line:
                try:
                    if '+' in line:
                        result['mana_change'] = int(line.split('+')[1].split()[0])
                    elif '-' in line:
                        result['mana_change'] = -int(line.split('-')[1].split()[0])
                except (ValueError, IndexError):
                    pass
            
            # Parse items and clues (Chinese)
            if '获得道具：' in line or '获得道具:' in line:
                # Extract item name after colon
                if '获得道具：' in line:
                    item = line.split('获得道具：', 1)[1].strip()
                else:
                    item = line.split('获得道具:', 1)[1].strip()
                
                # Remove parentheses content at the end (e.g., (可补充体力和魔力), (贿赂线推进))
                # Keep content before first opening parenthesis
                if '（' in item:
                    item = item.split('（')[0].strip()
                if '(' in item:
                    item = item.split('(')[0].strip()
                
                if item:
                    result['items_gained'].append(item)
            
            if '获得线索：' in line or '获得线索:' in line:
                # Extract clue text after colon
                if '获得线索：' in line:
                    clue = line.split('获得线索：', 1)[1].strip()
                else:
                    clue = line.split('获得线索:', 1)[1].strip()
                
                # Remove parentheses content at the end (e.g., (破坏线推进), (贿赂线推进))
                if '（' in clue:
                    clue = clue.split('（')[0].strip()
                if '(' in clue:
                    clue = clue.split('(')[0].strip()
                
                if clue:
                    result['clues_gained'].append(clue)
            
            # Parse items and clues (English)
            if 'Item:' in line or 'item:' in line or 'Item acquired:' in line:
                item = line.split(':')[-1].strip()
                if item:
                    result['items_gained'].append(item)
            
            if 'Get clue:' in line or 'get clue:' in line or 'Get Clue:' in line:
                clue = line.split(':')[-1].strip()
                if clue:
                    result['clues_gained'].append(clue)
            
            # Parse progress changes (Chinese)
            if '贿赂' in line and ('推进' in line or '+' in line or '-' in line):
                result['bribe_change'] = 1  # Simplified: just increment
            
            if '破坏' in line and ('推进' in line or '+' in line or '-' in line):
                result['sabotage_change'] = 1
            
            # Support both full-width ？ and half-width ? for mystery line
            if ('？' in line or '?' in line) and '推进' in line:
                result['mystery_change'] = 1
            
            # Parse progress changes (English)
            if 'bribe' in line.lower() and ('advance' in line.lower() or 'line' in line.lower()):
                result['bribe_change'] = 1
            
            if ('destruction' in line.lower() or 'damage' in line.lower()) and ('advance' in line.lower() or 'line' in line.lower()):
                result['sabotage_change'] = 1
            
            if '法学' in line or '文书' in line:
                if '推进' in line or '+' in line or '-' in line:
                    result['legal_change'] = 1
        
        return result
