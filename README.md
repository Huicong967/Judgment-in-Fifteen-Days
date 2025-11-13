# 《审判在十五天》- Judgment in Fifteen Days

一个独立图形界面的文本冒险游戏。你有 15 天时间在监狱中逃脱，需要通过三条路线之一达成目标。

## 快速开始

```bash
python start_game_new.py
```

游戏将在 2 秒内启动，首先显示语言选择窗口（中文/English）。

## 游戏特点

### 三条逃脱路线

| 路线 | 名称 | 描述 |
|------|------|------|
| 🤝 贿赂 | 贿路与交易 | 收买狱卒，消耗体力少 |
| 🔨 破坏 | 破坏监狱设施 | 暗中破坏，消耗体力多 |
| ⚖️ 法学 | 法学与文书 | 利用法律漏洞，消耗体力和魔力 |

### UI 特性

- **四区域布局**: 左侧属性/道具、右侧背景图、下方叙述文本
- **双语支持**: 完整的中文/英文本地化
- **多语言就绪**: 易于扩展支持更多语言
- **进度条显示**: 实时显示体力值(20/50)和魔力值(20/50)
- **线索系统**: 真相线索按钮，点击显示游戏线索
- **选择系统**: 清晰的 A/B/C 三选项界面

## 文件结构

```
Judgment in Fifteen Days/
├── start_game_new.py              # 游戏启动脚本
├── game/
│   ├── __init__.py
│   ├── state.py                   # 游戏状态管理
│   ├── level.py                   # 关卡基类
│   ├── manager.py                 # 关卡管理器
│   ├── image_manager.py           # 图片管理系统
│   ├── runner_gui_new.py          # GUI 游戏运行器
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── widgets_new.py         # 新 UI 组件库
│   │   └── language_selector.py   # 语言选择窗口
│   ├── i18n/
│   │   ├── __init__.py            # i18n 管理器
│   │   ├── zh.json                # 中文翻译
│   │   └── en.json                # 英文翻译
│   └── levels/
│       ├── __init__.py
│       └── level1.py              # 第一天关卡
├── assets/                        # 游戏资源目录（准备就绪）
└── UI_REFINEMENTS.md              # UI 细节调整文档
```

## 核心系统

### 1. 状态管理 (`game/state.py`)
- 属性: 体力(stamina)、魔力(mana)
- 进度: 贿赂、破坏、法学三条路线
- 物品栏: 收集线索和物品

### 2. 关卡系统 (`game/level.py`, `game/levels/level1.py`)
- 基类设计支持模板模式
- 多语言支持通过 i18n
- 选择系统: 每个关卡最多 3 个选择 (A/B/C)

### 3. 国际化系统 (`game/i18n/`)
- 完整的 JSON 翻译系统
- 支持简单的字符串格式化
- 易于添加新语言或翻译

### 4. 图片管理 (`game/image_manager.py`)
- 自动占位符生成
- 图片缓存机制
- 支持多层合成

### 5. GUI 系统 (`game/gui/`)
- PropertyPanel: 显示属性和进度
- ImagePanel: 背景图和线索显示
- NarrativePanel: 故事文本和选择
- ResultWindow: 选择结果显示

## 双语本地化

所有 UI 文本都在 `game/i18n/` 目录的 JSON 文件中:

```json
"ui": {
  "stamina_label": "体力值",
  "mana_label": "魔力值",
  "bribe_full": "贿路与交易",
  "sabotage_full": "破坏监狱设施",
  "legal_full": "法学与文书",
  "clues_button": "真相线索",
  ...
}
```

### 添加新语言

1. 复制 `game/i18n/zh.json` 为 `game/i18n/xx.json`（xx 为语言代码）
2. 翻译所有文本
3. 在 `game/i18n/__init__.py` 中添加语言代码到 `SUPPORTED_LANGUAGES`

## 开发指南

### 添加新关卡（第 2-15 天）

1. 在 `game/levels/` 中创建 `level2.py`:
   ```python
   from game.level import Level
   from game.i18n import get_i18n
   
   class Level2(Level):
       def __init__(self):
           super().__init__(2)
       
       def play(self, state):
           i18n = get_i18n()
           # 返回 scene, options, results
   ```

2. 在 `game/i18n/zh.json` 和 `en.json` 中添加关卡数据:
   ```json
   "level2": {
     "scene": "...",
     "options": { "A": {...}, "B": {...}, "C": {...} },
     "results": { "A": {...}, "B": {...}, "C": {...} }
   }
   ```

### 添加游戏图片

1. 将图片放在 `assets/level1/`, `assets/level2/` 等目录
2. 在关卡代码中调用:
   ```python
   image = image_manager.get_background('level1_intro')
   ```

## 技术栈

- **Python 3.10+**
- **Tkinter** (标准库 GUI)
- **Pillow** (图片处理)
- **JSON** (数据存储和本地化)

## 系统要求

- Python 3.10 或更高版本
- Windows/Mac/Linux
- 最小屏幕分辨率: 1600×1000

## 许可证

个人项目

## 联系方式

有问题？查看 `UI_REFINEMENTS.md` 获取最新的 UI 调整详情。
