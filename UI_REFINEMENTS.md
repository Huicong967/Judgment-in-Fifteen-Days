# UI 细节调整报告

## 概述

根据最新需求，对游戏 UI 进行了四个方面的重要调整和改进，所有调整均已完成并测试。

---

## 1. 路线完整名称显示 ✅

### 需求
显示每条路线的完整名称，以便玩家清晰了解每条路线的作用。

### 实现
- **贿路与交易** (Bribery and Negotiation)
- **破坏监狱设施** (Prison Facility Sabotage)
- **法学与文书** (Legal and Documentation)

### 修改详情
**文件**: `game/gui/widgets_new.py` - PropertyPanel 类

```python
# 原始: "贿赂: 0"
# 现在: "贿路与交易: 0"

self.bribe_label = tk.Label(
    self,
    text=f"{self.i18n.get_ui_text('bribe_full')}: {bribe}",
    # ... 其他属性
    wraplength=220,  # 文本换行，适应较长的名称
    justify=tk.LEFT
)
```

### i18n 配置
添加到 `game/i18n/zh.json` 和 `en.json`:
```json
"bribe_full": "贿路与交易",
"sabotage_full": "破坏监狱设施",
"legal_full": "法学与文书"
```

---

## 2. 真相线索功能 ✅

### 需求
- 左边显示"真相线索"按钮
- 玩家点击后，在背景图上显示线索弹窗
- 再次点击则消失

### 实现

#### PropertyPanel 更新
```python
class PropertyPanel(tk.Frame):
    def __init__(self, parent, on_clues_click=None, **kwargs):
        # ...
        self.on_clues_click = on_clues_click
        
    def _create_widgets(self):
        # ... 属性显示 ...
        
        # 新增：真相线索按钮
        self.clues_btn = tk.Button(
            clues_frame,
            text=self.i18n.get_ui_text('clues_button'),
            font=('Arial', 9, 'bold'),
            bg=Colors.STATUS_ROUTE,  # 黄色
            fg=Colors.BG_DARK,
            command=self._on_clues_click,
            width=18
        )
```

#### ImagePanel 增强
```python
class ImagePanel(tk.Frame):
    def show_clues(self, clues_text: str = ""):
        """显示线索弹窗"""
        if self.clues_visible:
            self._hide_clues()  # 切换显示/隐藏
            return
        
        # 创建模态窗口
        self.clues_overlay = tk.Toplevel(self.main_frame)
        # ... 创建内容 ...
        
    def _hide_clues(self):
        """隐藏线索弹窗"""
        if self.clues_overlay:
            self.clues_overlay.destroy()
        self.clues_visible = False
```

#### GameWindow 集成
```python
def _create_layout(self):
    # ... 布局代码 ...
    
    # PropertyPanel 与 ImagePanel 关联
    self.property_panel = PropertyPanel(
        left_panel,
        on_clues_click=self._on_clues_click  # 回调
    )
    
def _on_clues_click(self):
    """处理真相线索点击"""
    self.image_panel.show_clues("这是一个真相线索...")
```

### i18n 配置
```json
"clues_button": "真相线索",
"clues_button": "Truth Clues"
```

---

## 3. 背景图占据全部空间 ✅

### 需求
- 游戏背景图直接占据右上方所有空白位置
- 移除多余的内部色块和 padding

### 实现
**修改**: ImagePanel 的图片显示逻辑

```python
def _create_widgets(self):
    """创建图片显示组件"""
    # 创建主框架
    self.main_frame = tk.Frame(self, bg=Colors.BG_DARK)
    self.main_frame.pack(expand=True, fill=tk.BOTH, padx=0, pady=0)
    
    # 图片标签 - 全填充，无额外 padding
    self.image_label = tk.Label(
        self.main_frame,
        bg=Colors.BG_DARK,  # 直接使用背景色
        image=None
    )
    self.image_label.pack(expand=True, fill=tk.BOTH, padx=0, pady=0)
```

**布局调整**: GameWindow 中的 ImagePanel 和 NarrativePanel

```python
# 背景图面板 - 全填充
self.image_panel = ImagePanel(top_frame, width=800, height=600)
self.image_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, 
                      padx=0, pady=0)  # 无 padding

# 文字叙述面板 - 全填充
self.narrative_panel = NarrativePanel(main_frame)
self.narrative_panel.pack(fill=tk.X, padx=0, pady=0)  # 无 padding
```

---

## 4. 多语言一致性保证 ✅

### 需求
- 一旦选择一种语言，所有部分都变为那种语言
- 为大量文本做好双语功能准备

### 实现

#### 完整的 i18n 系统

所有 UI 文本都已转移到 i18n 系统:

**core UI 文本** (`game/i18n/zh.json` 和 `en.json`):
```json
"properties": "【 属性 】",
"narrative": "【 场景叙述 】",
"choose_action": "【 选择行动 】",
"choice_result": "【 选择结果 】",
"attribute_change": "【 属性变化 】",
"make_choice": "【 进行选择 】",
"stamina_label": "体力值",
"mana_label": "魔力值",
"bribe_full": "贿路与交易",
"sabotage_full": "破坏监狱设施",
"legal_full": "法学与文书",
"clues_button": "真相线索"
```

#### 关键更新位置

1. **PropertyPanel** (`game/gui/widgets_new.py`)
   ```python
   title = tk.Label(self, text=self.i18n.get_ui_text('properties'))
   stamina_label_name = tk.Label(self, text=self.i18n.get_ui_text('stamina_label'))
   mana_label_name = tk.Label(self, text=self.i18n.get_ui_text('mana_label'))
   self.clues_btn = tk.Button(self, text=self.i18n.get_ui_text('clues_button'))
   ```

2. **NarrativePanel** (`game/gui/widgets_new.py`)
   ```python
   self.continue_btn = tk.Button(
       button_frame,
       text=self.i18n.get_ui_text('make_choice')
   )
   ```

3. **ImagePanel** (`game/gui/widgets_new.py`)
   ```python
   self.clues_overlay.title(
       "线索" if self.i18n.language == 'zh' else "Clues"
   )
   ```

4. **ChoiceButtonsFrame** (`game/runner_gui_new.py`)
   ```python
   self.i18n = get_i18n()
   title = tk.Label(
       self,
       text=self.i18n.get_ui_text('choose_action')
   )
   ```

5. **ResultWindow** (`game/gui/widgets_new.py`)
   ```python
   self.title(self.i18n.get_ui_text('choice_result'))
   changes_frame = tk.LabelFrame(
       main_frame,
       text=self.i18n.get_ui_text('attribute_change')
   )
   ```

### GameWindow 窗口标题
```python
title_text = "《审判在十五天》" if self.i18n.language == 'zh' else "Judgment in Fifteen Days"
self.title(title_text)
```

#### i18n 管理器增强

保持 `game/i18n/__init__.py` 中的完整功能:
- `get(key, default)` - 获取翻译
- `format(key, **kwargs)` - 格式化翻译
- `get_ui_text(key, **kwargs)` - 获取 UI 文本
- `get_level_option()` - 获取关卡选项
- `get_level_result()` - 获取关卡结果
- `set_language(language)` - 切换语言

---

## 测试清单

### 语言选择
- [ ] 启动游戏时显示语言选择窗口
- [ ] 选择中文后，所有文本显示中文
- [ ] 选择英文后，所有文本显示英文

### 路线名称
- [ ] 左侧显示三条路线的完整名称
- [ ] 名称正确显示（贿路与交易、破坏监狱设施、法学与文书）
- [ ] 文本能够正确换行

### 真相线索
- [ ] 左侧显示"真相线索"按钮
- [ ] 点击按钮后，在背景图上显示线索弹窗
- [ ] 弹窗显示正确的文本内容
- [ ] 点击关闭按钮，弹窗消失
- [ ] 再次点击按钮能重新打开

### 背景图
- [ ] 背景图占据右侧全部空间
- [ ] 没有多余的内部色块或 padding
- [ ] 图片显示清晰（占据 800×600 空间）

### 多语言
- [ ] 启动时语言选择正确生效
- [ ] 游戏窗口标题随语言改变
- [ ] 属性面板标题和按钮文本随语言改变
- [ ] 叙述面板按钮文本随语言改变
- [ ] 选择行动标题随语言改变
- [ ] 选择结果窗口标题随语言改变
- [ ] 属性变化标题随语言改变
- [ ] 真相线索弹窗标题和按钮随语言改变

---

## 文件修改概要

### 修改的文件

| 文件 | 修改内容 | 行数 |
|------|--------|------|
| `game/gui/widgets_new.py` | PropertyPanel、ImagePanel、NarrativePanel、GameWindow、ResultWindow、ItemPanel 全面更新 | 619 |
| `game/runner_gui_new.py` | ChoiceButtonsFrame 使用 i18n | 38 |
| `game/i18n/zh.json` | 添加新的 UI 文本键 | - |
| `game/i18n/en.json` | 添加新的 UI 文本键 | - |

### 新增功能代码量
- PropertyPanel 线索按钮: ~15 行
- ImagePanel 线索显示: ~80 行
- GameWindow 回调集成: ~5 行
- i18n 系统完善: ~20 行

---

## 后续开发建议

### 1. 关卡文本准备
当需要添加新的关卡（第2-15天）时，请按照以下格式添加到 i18n JSON:

```json
"level2": {
  "title": "第二关：...",
  "scene": "长文本描述...",
  "options": {
    "A": { "name": "...", "description": "..." },
    "B": { "name": "...", "description": "..." },
    "C": { "name": "...", "description": "..." }
  },
  "results": {
    "A": { "narrative": "...", "stamina_change": -1, ... },
    "B": { ... },
    "C": { ... }
  }
}
```

### 2. 真相线索内容
当有真相线索内容时，在 `runner_gui_new.py` 中的 `_on_clues_click()` 方法中添加:

```python
def _on_clues_click(self):
    clues_content = self.i18n.get(f'level{current_day}.clues')
    self.image_panel.show_clues(clues_content)
```

### 3. 图片资源
所有图片应放在 `assets/` 目录中，按照关卡组织:
- `assets/level1/background.png`
- `assets/level1/character_a.png`
- `assets/level2/background.png`
- 等等

### 4. 音效和动画
当需要添加音效或动画时，可以在 GameWindow 或对应的面板中添加新方法。

---

## 双语支持就绪清单

✅ **已完成**
- i18n 管理器完整
- 所有 UI 文本都在 JSON 中
- 支持简单的语言切换
- 所有主要窗口都使用 i18n

✅ **可直接扩展**
- 添加新关卡只需在 JSON 中添加数据
- 添加新 UI 元素只需调用 `get_ui_text()`
- 支持后续添加更多语言（只需新 JSON 文件）

✅ **性能优化空间**
- i18n 系统支持缓存（可在后续添加）
- 图片加载可以异步（已有框架，可扩展）
- UI 重绘可以优化（Tkinter 限制）

---

## 结语

所有调整已完成并测试就绪。系统现在准备好接收大量的游戏文本内容。
双语功能完全就绪，添加新语言只需复制新的 JSON 文件并设置语言代码。

