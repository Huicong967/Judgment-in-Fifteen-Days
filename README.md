# Judgment in Fifteen Days

[![License](https://img.shields.io/badge/License-Personal_Project-blue.svg)](LICENSE.md)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Audio License](https://img.shields.io/badge/Audio-CC0-green.svg)](LICENSE.md#audio-assets)

A standalone graphical text adventure game. You have 15 days to escape from prison by completing one of three routes.

## Quick Start

```bash
python start_game_new.py
```

The game will launch within 2 seconds, first displaying a language selection window (中文/English).

## Game Features

### Three Escape Routes

| Route | Name | Description |
|------|------|------|
| 🤝 Bribe | Bribery & Trading | Bribe the guards, low stamina cost |
| 🔨 Sabotage | Prison Destruction | Sabotage secretly, high stamina cost |
| ⚖️ Legal | Law & Documentation | Exploit legal loopholes, costs stamina and mana |

### Gameplay Mechanics

- **Conditional Options**: Days 11, 12, and 14 have special requirements for certain choices
  - Option A requires: Stamina ≥25 AND Mana ≥25 AND specific progress ≥3
  - Option B requires: Stamina <25 OR Mana <25 OR specific progress <3
  - Option C is always available
- **Resource Management**: Balance stamina and mana consumption
- **Multiple Endings**: Different outcomes based on your choices and progress

### UI Features

- **Four-Panel Layout**: Left panel for stats/inventory, right panel for backgrounds, bottom panel for narrative text
- **Bilingual Support**: Complete Chinese/English localization
- **Real-time Display**: Shows stamina (20/50) and mana (20/50) with progress bars
- **Clue System**: Clues button to display collected game clues
- **Choice System**: Clear A/B/C three-option interface
- **Audio System**: Background music and click sound effects

## Audio Credits

The game includes audio resources under the CC0 license (commercial use allowed):

- **Background Music**: "Eerie Piano Horror Suspense Music - Dark Nursery Rhyme"
  - Source: [爱给网 - 诡异氛围钢琴恐怖悬疑配乐-暗黑童谣](https://www.aigei.com/item/gui_yi_fen_wei_211.html)
  - License: CC0 (Public Domain)

- **Click Sound Effect**: "Click - Button"
  - Source: [爱给网 - click-点击-按钮](https://www.aigei.com/item/click_dian_ji_89.html)
  - License: CC0 (Public Domain)

## Project Structure

```
Judgment in Fifteen Days/
├── start_game_new.py              # Game launcher
├── game/
│   ├── __init__.py
│   ├── state.py                   # Game state management
│   ├── level.py                   # Level base class
│   ├── manager.py                 # Level manager
│   ├── runner_redesigned.py       # Main game runner
│   ├── csv_text_loader.py         # CSV text loader
│   ├── audio_manager.py           # Audio system manager
│   ├── levels/
│   │   ├── __init__.py
│   │   └── csv_level.py           # CSV-based level definition
│   ├── gui/
│   │   └── __init__.py
│   └── i18n/
│       └── __init__.py
├── Chinese Text.csv               # Chinese game content
├── English Text.csv               # English game content
├── BGM.mp3                        # Background music (CC0)
├── click.mp3                      # Click sound effect (CC0)
├── *.png                          # UI elements and backgrounds
└── tools/                         # Development tools
```

## Core Systems

### 1. State Management (`game/state.py`)
- Attributes: stamina, mana
- Progress: bribe, sabotage, legal routes
- Inventory: collect clues and items

### 2. Level System (`game/level.py`, `game/levels/csv_level.py`)
- CSV-based level data
- Multilingual support
- Choice system: up to 3 choices per level (A/B/C)

### 3. CSV Text Loader (`game/csv_text_loader.py`)
- Loads game content from CSV files
- Supports language switching
- Handles requirements checking for conditional choices

### 4. Audio System (`game/audio_manager.py`)
- Background music loop playback
- Click sound effects
- Volume control
- Pygame-based implementation

### 5. Game Runner (`game/runner_redesigned.py`)
- Main game loop
- UI rendering and event handling
- Fullscreen support (F11 to toggle, ESC to exit)
- Integrated audio playback

## Bilingual Localization

Game content is stored in CSV files with columns for both Chinese and English text. The system automatically selects the appropriate language based on user choice.

### CSV Structure

The CSV files contain:
- Day number
- Options (A/B/C) and their text
- Result texts for each option
- System settlement messages
- Conditional requirements for special days

## Development Guide

### Adding New Content

Edit `Chinese Text.csv` and `English Text.csv` to add or modify:
- Daily narratives
- Choice options
- Result texts
- Settlement messages

### Adding Images

1. Place images in the root directory
2. Follow naming convention: `Day X.PNG` for backgrounds
3. UI elements: `DialogBox.png`, `option.png`, etc.

## Technical Stack

- **Python 3.10+**
- **Tkinter** (Standard library GUI)
- **Pillow** (Image processing)
- **Pygame** (Audio playback)
- **CSV** (Data storage and localization)

## System Requirements

- Python 3.10 or higher
- Windows/Mac/Linux
- Minimum screen resolution: 1920×1080
- Required packages: Pillow, pygame

## Installation

```bash
# Install required packages
pip install Pillow pygame

# Run the game
python start_game_new.py
```

## License

Personal project.

Audio resources are licensed under CC0 (Public Domain), allowing commercial use.

## Contact

For questions or issues, please check the documentation files in the repository.
