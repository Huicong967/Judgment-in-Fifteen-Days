import csv
import re
from typing import Dict, List
from game.level import Level
from game.state import GameState


def get_special_text(header: str, language: str = '中文') -> str:
    """Return the special block text for a header like '故事背景' or '体力值≤0'.

    Strategy: read the CSV file lines and find a row whose first cell equals header,
    then return the first non-empty cell in the subsequent non-empty row(s).
    
    Args:
        header: The header to search for (e.g., '故事背景' or 'Story background')
        language: Language for CSV file ('中文' or 'English')
    """
    import os
    root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filename = 'Chinese Text.csv' if language == '中文' else 'English Text.csv'
    path = os.path.join(root, filename)
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            lines = [line.rstrip('\n') for line in f]
    except Exception:
        return ''

    # split CSV cells by comma but respect quoted fields simply by using csv.reader
    import csv
    reader = list(csv.reader(lines))
    for idx, row in enumerate(reader):
        if not row:
            continue
        first = (row[0] or '').strip()
        if first == header:
            # look for the next row that contains a non-empty second column or any long text
            for j in range(idx + 1, min(len(reader), idx + 6)):
                r2 = reader[j]
                if not r2:
                    continue
                # find the first non-empty cell beyond first column
                for cell in r2[1:]:
                    if cell and cell.strip():
                        return cell.strip()
                # if entire row single long quoted field present in first column
                if r2 and r2[0] and r2[0].strip():
                    # avoid returning another header
                    if r2[0].strip() != header:
                        return r2[0].strip()
            return ''
    return ''


def _parse_int_from_text(txt: str, key_cn: str) -> int:
    """Parse numeric change like '体力-5' or '魔力+5' from text for given key_cn."""
    if not txt:
        return 0
    m = re.search(rf"{re.escape(key_cn)}\s*([+-]?\d+)", txt)
    if m:
        try:
            return int(m.group(1))
        except Exception:
            return 0
    return 0


def _parse_items_from_text(txt: str) -> List[str]:
    if not txt:
        return []
    items = []
    # find occurrences of '获得道具：X' or '获得道具: X'
    for m in re.finditer(r'获得道具[:：]\s*([^，,\n（(]+)', txt):
        items.append(m.group(1).strip())
    return items


def _parse_progress_from_text(txt: str) -> Dict[str, int]:
    # detect mentions like '贿赂线推进', '破坏线推进', '文书线推进'
    changes = {'bribe': 0, 'sabotage': 0, 'legal': 0}
    if not txt:
        return changes
    if '贿赂线推进' in txt or '贿赂线' in txt:
        changes['bribe'] = 1
    if '破坏线推进' in txt or '破坏线' in txt:
        changes['sabotage'] = 1
    if '文书线推进' in txt or '文书' in txt or '法学' in txt:
        changes['legal'] = 1
    return changes


class LevelFromCSV(Level):
    """Level loaded from a CSV file (Chinese/English)."""

    CSV_FILES = {
        'zh': 'Chinese Text.csv',
        'en': 'English Text.csv'
    }

    def __init__(self, day: int, language: str = 'zh'):
        super().__init__(language=language)
        self.id = day
        self.data = {}
        self._load_csv()

    def _load_csv(self):
        fname = LevelFromCSV.CSV_FILES.get(self.language, 'Chinese Text.csv')
        # file is in project root
        import os
        root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        path = os.path.join(root, fname)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # attempt to get day number from first column (天数)
                    key0 = list(row.keys())[0]
                    raw_day = (row.get(key0) or '').strip()
                    if not raw_day:
                        continue
                    m = re.search(r'第\s*(\d+)\s*天', raw_day)
                    if m:
                        daynum = int(m.group(1))
                    else:
                        # try to extract leading number
                        m2 = re.search(r'(\d+)', raw_day)
                        if m2:
                            daynum = int(m2.group(1))
                        else:
                            continue
                    self.data[daynum] = row
        except FileNotFoundError:
            # no CSV found
            self.data = {}

    def _row(self) -> Dict:
        return self.data.get(self.id, {})

    def get_narrative(self) -> str:
        row = self._row()
        # header likely '叙述文本' or 'Narrative'
        return row.get('叙述文本') or row.get('Narrative') or ''

    def get_options(self) -> Dict[str, str]:
        row = self._row()
        opts = {}
        for k in ['A', 'B', 'C']:
            val = row.get(k)
            if val and val.strip():
                opts[k] = val.strip()
        return opts

    def handle_choice(self, choice: str, state: GameState) -> Dict:
        row = self._row()
        choice = choice.upper()
        # result columns may be 'A结果文本' etc
        res_col = f'{choice}结果文本'
        settlement_col = f'{choice}系统结算'
        narrative = row.get(res_col) or row.get(f'{choice} result', '') or ''

        # parse stat changes from narrative text
        stamina_change = _parse_int_from_text(narrative, '体力')
        mana_change = _parse_int_from_text(narrative, '魔力')
        items = _parse_items_from_text(narrative)
        progress = _parse_progress_from_text(narrative)

        # also parse settlement text
        settlement_text = row.get(settlement_col) or ''
        settlement_changes = _parse_progress_from_text(settlement_text)
        settlement_items = _parse_items_from_text(settlement_text)
        # parse stat changes in settlement text
        settlement_stamina = _parse_int_from_text(settlement_text, '体力')
        settlement_mana = _parse_int_from_text(settlement_text, '魔力')

        return {
            'narrative': narrative,
            'stamina_change': stamina_change,
            'mana_change': mana_change,
            'bribe_change': progress.get('bribe', 0),
            'sabotage_change': progress.get('sabotage', 0),
            'legal_change': progress.get('legal', 0),
            'items_gained': items,
            'items_lost': [],
            'settlement_text': settlement_text,
            'settlement_changes': {
                'stamina': settlement_stamina,
                'mana': settlement_mana,
                'bribe': settlement_changes.get('bribe', 0),
                'sabotage': settlement_changes.get('sabotage', 0),
                'legal': settlement_changes.get('legal', 0),
                'items': settlement_items,
            }
        }
