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
                'sabotage': '破坏',
                'legal': '文书',
                'bribe': '贿赂',
                'mystery': '？',
                'stamina_min': '体力最小值（初始10）',
                'mana_min': '魔力最小值（初始10）',
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
                    
                    # Check if day_str contains death condition (not a day number)
                    if day_str and day_str.strip():
                        day_str_stripped = day_str.strip()
                        
                        # Check if this is a death ending condition row
                        if '体力值≤0' in day_str_stripped and '魔力值' not in day_str_stripped:
                            # Stamina death only
                            narrative = row.get(col_map['narrative'], '').strip()
                            self.data['death_stamina'] = {'narrative': narrative}
                            print(f"[DEBUG] Loaded stamina death ending: {narrative[:50]}...")
                            continue
                        elif '魔力值≤0' in day_str_stripped and '体力值' not in day_str_stripped:
                            # Mana death only
                            narrative = row.get(col_map['narrative'], '').strip()
                            self.data['death_mana'] = {'narrative': narrative}
                            print(f"[DEBUG] Loaded mana death ending: {narrative[:50]}...")
                            continue
                        elif '体力值魔力值同时≤0' in day_str_stripped or ('体力值' in day_str_stripped and '魔力值' in day_str_stripped and '≤0' in day_str_stripped):
                            # Both stats death
                            narrative = row.get(col_map['narrative'], '').strip()
                            self.data['death_both'] = {'narrative': narrative}
                            print(f"[DEBUG] Loaded both stats death ending: {narrative[:50]}...")
                            continue
                    
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
                    
                    # Parse condition requirements
                    def parse_int(val):
                        try:
                            v = val.strip()
                            if v and v != '结束':
                                return int(v)
                            return 0
                        except:
                            return 0
                    
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
                        # Condition requirements
                        'stamina_min': parse_int(row.get(col_map.get('stamina_min', ''), '0')),
                        'mana_min': parse_int(row.get(col_map.get('mana_min', ''), '0')),
                        'sabotage_req': parse_int(row.get(col_map.get('sabotage', ''), '0')),
                        'legal_req': parse_int(row.get(col_map.get('legal', ''), '0')),
                        'bribe_req': parse_int(row.get(col_map.get('bribe', ''), '0')),
                        'mystery_req': parse_int(row.get(col_map.get('mystery', ''), '0')),
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
    
    def get_death_ending(self, stamina: int, mana: int) -> Optional[str]:
        """Get death ending text based on current stamina and mana.
        
        Returns the appropriate ending text if player is dead, None otherwise.
        """
        if stamina <= 0 and mana <= 0:
            # Both stats depleted
            ending_data = self.data.get('death_both', {})
            return ending_data.get('narrative', '')
        elif stamina <= 0:
            # Only stamina depleted
            ending_data = self.data.get('death_stamina', {})
            return ending_data.get('narrative', '')
        elif mana <= 0:
            # Only mana depleted
            ending_data = self.data.get('death_mana', {})
            return ending_data.get('narrative', '')
        return None
    
    def get_requirements(self, day: int, choice: str) -> Dict:
        """Get requirement conditions for a specific day and choice.
        
        Only days 11, 12, 14 options A and B have requirements.
        
        Returns:
            Dict with keys: has_requirements, min_hp, min_mp, min_progress, progress_type
        """
        # Only check for days 11, 12, 14 and choices A, B
        if day not in [11, 12, 14] or choice not in ['A', 'B']:
            return {'has_requirements': False}
        
        day_data = self.data.get(day, {})
        option_text = day_data.get(f'option_{choice.lower()}', '')
        
        # Parse requirements from option text
        if day == 11:
            if choice == 'A':
                # HP≥25且MP≥25且破坏线进度≥3
                return {
                    'has_requirements': True,
                    'min_hp': 25,
                    'min_mp': 25,
                    'min_progress': 3,
                    'progress_type': 'sabotage'
                }
            else:  # B
                # HP＜25或MP＜25或破坏线进度＜3
                return {
                    'has_requirements': True,
                    'max_hp': 24,  # Less than 25
                    'max_mp': 24,  # Less than 25
                    'max_progress': 2,  # Less than 3
                    'progress_type': 'sabotage',
                    'is_inverse': True  # OR condition, not AND
                }
        elif day == 12:
            if choice == 'A':
                # HP≥25且MP≥25且文书线进度≥3
                return {
                    'has_requirements': True,
                    'min_hp': 25,
                    'min_mp': 25,
                    'min_progress': 3,
                    'progress_type': 'legal'
                }
            else:  # B
                # HP＜25或MP＜25或文书线进度＜3
                return {
                    'has_requirements': True,
                    'max_hp': 24,
                    'max_mp': 24,
                    'max_progress': 2,
                    'progress_type': 'legal',
                    'is_inverse': True
                }
        elif day == 14:
            if choice == 'A':
                # HP≥25且MP≥25且贿赂线进度≥3
                return {
                    'has_requirements': True,
                    'min_hp': 25,
                    'min_mp': 25,
                    'min_progress': 3,
                    'progress_type': 'bribe'
                }
            else:  # B
                # HP＜25或MP＜25或贿赂线进度＜3
                return {
                    'has_requirements': True,
                    'max_hp': 24,
                    'max_mp': 24,
                    'max_progress': 2,
                    'progress_type': 'bribe',
                    'is_inverse': True
                }
        
        return {'has_requirements': False}
    
    def check_requirements(self, day: int, choice: str, state) -> tuple:
        """Check if player meets requirements for a specific day and choice.
        
        Returns:
            (meets_requirements, list_of_unmet_conditions)
        """
        reqs = self.get_requirements(day, choice)
        
        if not reqs.get('has_requirements', False):
            return (True, [])  # No requirements, always allowed
        
        current_hp = state.stamina
        current_mp = state.mana
        progress_type = reqs.get('progress_type', '')
        
        if progress_type == 'sabotage':
            current_progress = state.sabotage_progress
            progress_name = '破坏进度' if self.language == '中文' else 'Sabotage Progress'
        elif progress_type == 'legal':
            current_progress = state.legal_progress
            progress_name = '文书进度' if self.language == '中文' else 'Legal Progress'
        elif progress_type == 'bribe':
            current_progress = state.bribe_progress
            progress_name = '贿赂进度' if self.language == '中文' else 'Bribe Progress'
        else:
            current_progress = 0
            progress_name = ''
        
        # Check if this is an inverse condition (option B - "less than" requirements)
        if reqs.get('is_inverse', False):
            # For option B: need HP<25 OR MP<25 OR progress<3
            # Player can choose if ANY condition is true
            max_hp = reqs.get('max_hp', 24)
            max_mp = reqs.get('max_mp', 24)
            max_progress = reqs.get('max_progress', 2)
            
            hp_ok = current_hp <= max_hp
            mp_ok = current_mp <= max_mp
            progress_ok = current_progress <= max_progress
            
            if hp_ok or mp_ok or progress_ok:
                return (True, [])  # At least one condition met
            else:
                # All conditions failed - player is too strong for option B
                unmet = []
                if self.language == '中文':
                    unmet.append(f"此选项需要：体力<25 或 魔力<25 或 {progress_name}<3")
                    unmet.append(f"您当前：体力={current_hp}，魔力={current_mp}，{progress_name}={current_progress}")
                    unmet.append(f"您的条件过强，请选择选项A")
                else:
                    unmet.append(f"This option requires: HP<25 OR MP<25 OR {progress_name}<3")
                    unmet.append(f"Your current: HP={current_hp}, MP={current_mp}, {progress_name}={current_progress}")
                    unmet.append(f"You are too strong, please choose option A")
                return (False, unmet)
        else:
            # For option A: need HP>=25 AND MP>=25 AND progress>=3
            min_hp = reqs.get('min_hp', 25)
            min_mp = reqs.get('min_mp', 25)
            min_progress = reqs.get('min_progress', 3)
            
            unmet = []
            
            if current_hp < min_hp:
                if self.language == '中文':
                    unmet.append(f"体力需要≥{min_hp}（当前：{current_hp}）")
                else:
                    unmet.append(f"HP must be ≥{min_hp} (Current: {current_hp})")
            
            if current_mp < min_mp:
                if self.language == '中文':
                    unmet.append(f"魔力需要≥{min_mp}（当前：{current_mp}）")
                else:
                    unmet.append(f"MP must be ≥{min_mp} (Current: {current_mp})")
            
            if current_progress < min_progress:
                if self.language == '中文':
                    unmet.append(f"{progress_name}需要≥{min_progress}（当前：{current_progress}）")
                else:
                    unmet.append(f"{progress_name} must be ≥{min_progress} (Current: {current_progress})")
            
            return (len(unmet) == 0, unmet)
    
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
