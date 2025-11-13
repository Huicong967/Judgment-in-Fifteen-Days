"""
Internationalization (i18n) manager for the game.
游戏国际化管理器。
"""

import json
import os
from typing import Any, Dict, Literal


class I18nManager:
    """Manages game text in multiple languages."""
    
    SUPPORTED_LANGUAGES = {'zh', 'en'}
    I18N_DIR = os.path.dirname(__file__)  # 直接指向当前目录，而不是 i18n/i18n
    
    def __init__(self, language: Literal['zh', 'en'] = 'zh'):
        """Initialize i18n manager.
        
        Args:
            language: Language code ('zh' for Chinese, 'en' for English)
        """
        if language not in self.SUPPORTED_LANGUAGES:
            language = 'zh'
        
        self.language = language
        self.data = self._load_language_data(language)
    
    def _load_language_data(self, language: str) -> Dict[str, Any]:
        """Load language data from JSON file.
        
        Args:
            language: Language code
        
        Returns:
            Dictionary containing all language data
        """
        file_path = os.path.join(self.I18N_DIR, f'{language}.json')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback to Chinese if file not found
            if language != 'zh':
                return self._load_language_data('zh')
            return {}
        except json.JSONDecodeError:
            print(f"Error parsing {language}.json")
            return {}
    
    def set_language(self, language: Literal['zh', 'en']):
        """Switch to a different language.
        
        Args:
            language: Language code
        """
        if language in self.SUPPORTED_LANGUAGES:
            self.language = language
            self.data = self._load_language_data(language)
    
    def get(self, key: str, default: str = '') -> str:
        """Get a translation by dotted key path.
        
        Examples:
            get('ui.stamina')
            get('level1.title')
        
        Args:
            key: Dotted path to translation key
            default: Default value if key not found
        
        Returns:
            Translated string or default value
        """
        keys = key.split('.')
        current = self.data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return str(current) if current else default
    
    def format(self, key: str, **kwargs) -> str:
        """Get a translation and format it with variables.
        
        Examples:
            format('ui.day', day=1)
            format('ui.max_days', max_days=15)
        
        Args:
            key: Dotted path to translation key
            **kwargs: Variables for string formatting
        
        Returns:
            Formatted translation string
        """
        text = self.get(key)
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    
    def get_level_option(self, level: str, option: str, field: str) -> str:
        """Get a level's option text.
        
        Args:
            level: Level name (e.g., 'level1')
            option: Option code ('A', 'B', 'C')
            field: Field name ('name', 'description', etc.)
        
        Returns:
            Translated text
        """
        return self.get(f'{level}.options.{option}.{field}', f'Option {option}')
    
    def get_level_result(self, level: str, option: str, field: str) -> Any:
        """Get a level's result text or data.
        
        Args:
            level: Level name (e.g., 'level1')
            option: Option code ('A', 'B', 'C')
            field: Field name ('narrative', 'stamina_change', etc.)
        
        Returns:
            Result value (could be string, int, etc.)
        """
        key = f'{level}.results.{option}.{field}'
        value = self.get(key)
        
        # Try to parse as int if it looks like one
        if field.endswith('_change') and value.lstrip('-').isdigit():
            return int(value)
        
        return value
    
    def get_ui_text(self, key: str, **kwargs) -> str:
        """Get UI text with optional formatting.
        
        Args:
            key: UI element name (e.g., 'stamina', 'mana')
            **kwargs: Optional formatting variables
        
        Returns:
            UI text string
        """
        full_key = f'ui.{key}'
        if kwargs:
            return self.format(full_key, **kwargs)
        return self.get(full_key)


# Global i18n instance
_i18n_instance = None


def get_i18n(language: Literal['zh', 'en'] = None) -> I18nManager:
    """Get or create global i18n instance.
    
    Args:
        language: Language code (only used on first call)
    
    Returns:
        Global I18nManager instance
    """
    global _i18n_instance
    
    if _i18n_instance is None:
        _i18n_instance = I18nManager(language or 'zh')
    
    return _i18n_instance


def set_language(language: Literal['zh', 'en']):
    """Set global language.
    
    Args:
        language: Language code
    """
    get_i18n().set_language(language)
