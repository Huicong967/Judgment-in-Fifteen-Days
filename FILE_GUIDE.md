# 📁 文件用途导览

## 🎮 游戏文件

### 启动脚本
**`start_game_new.py`** (15 行)
- 游戏入口点
- 设置 Python 路径
- 调用 `game.runner_gui_new` 中的 `main()` 函数
- 唯一需要执行的文件

---

## 🎯 核心游戏逻辑 (`game/` 目录)

### `state.py` (39 行)
- 定义 `GameState` 数据类
- 管理所有游戏状态：
  - `stamina` - 体力 (初值: 20, 最大: 50)
  - `mana` - 魔力 (初值: 20, 最大: 50)
  - `bribe_progress` - 贿赂路线进度
  - `sabotage_progress` - 破坏路线进度
  - `legal_progress` - 法律路线进度
  - `inventory` - 物品栏
- 提供 `apply_change()` 方法更新状态
- 提供 `snapshot()` 方法保存状态

### `level.py` (60+ 行)
- 定义 `Level` 基类（模板模式）
- 包含关卡编号、标题等基本信息
- 定义了所有关卡需要实现的接口：
  - `get_narrative()` - 获取故事文本
  - `get_options()` - 获取选择列表
  - `get_background()` - 获取背景图名称
  - `handle_choice()` - 处理玩家选择
- 实现 `play()` 方法作为主游戏循环

### `manager.py` (80+ 行)
- 定义 `LevelManager` 类
- 管理所有关卡（第 1-15 天）
- 提供方法：
  - `get_level(day)` - 获取指定第几天的关卡
  - `get_current_level()` - 获取当前天的关卡
  - `next_day()` - 进入下一天
  - `is_game_over()` - 检查游戏是否结束
- 跟踪当前进度

### `image_manager.py` (250+ 行)
- 定义 `ImageManager` 类（单例模式）
- 管理所有图片资源
- 功能：
  - 自动创建 `assets/` 目录
  - 加载或生成占位符图片
  - 缓存已加载的图片
  - 支持图片合成
- 用法: `image_manager.get_background('level1')`

### `runner_gui_new.py` (291 行)
- **主游戏运行器** - 最重要的文件
- 定义 `ChoiceButtonsFrame` - 选择按钮框架
- 定义 `GUIGameRunner` 类 - 游戏主逻辑
- 功能：
  - 初始化 GUI 窗口和游戏管理器
  - 处理语言选择
  - 管理游戏流程和 UI 交互
  - 处理玩家选择
  - 显示结果和更新属性
  - 提供 `main()` 函数作为入口

---

## 🎨 GUI 系统 (`game/gui/` 目录)

### `widgets_new.py` (620 行)
- **新 UI 组件库** - UI 系统的核心
- 定义的类：
  - `Colors` - 颜色方案
  - `PropertyPanel` - 左侧属性面板（体力、魔力、路线、线索按钮）
  - `ItemPanel` - 左侧物品栏
  - `ImagePanel` - 右侧背景图（支持线索叠加）
  - `NarrativePanel` - 下方叙述文本框和"进行选择"按钮
  - `GameWindow` - 主游戏窗口（1600×1000）
  - `ResultWindow` - 选择结果弹窗（属性变化和获得物品）
  - `ChoiceButtonsFrame` - 显示 A/B/C 选择按钮

### `language_selector.py` (120+ 行)
- 游戏启动时显示的语言选择窗口
- 返回用户选择的语言代码（'zh' 或 'en'）
- 使用 Tkinter 的 Toplevel 实现模态对话框
- 用法: `language = select_language()`

### `__init__.py` (23 行)
- 包初始化文件
- 从 `widgets_new.py` 导出所有 UI 组件
- 定义 `__all__` 列表方便导入

---

## 🌍 国际化系统 (`game/i18n/` 目录)

### `__init__.py` (184 行)
- **i18n 管理器** - 多语言支持的核心
- 定义 `I18nManager` 类，提供方法：
  - `get(key)` - 通过点号路径获取翻译
  - `format(key, **kwargs)` - 获取并格式化翻译
  - `get_ui_text(key)` - 获取 UI 文本
  - `get_level_option()` - 获取关卡选项文本
  - `get_level_result()` - 获取关卡结果数据
  - `set_language()` - 切换语言
- 全局实例函数:
  - `get_i18n()` - 获取全局 i18n 实例
  - `set_language()` - 设置全局语言
- 支持的语言: 中文 ('zh') 和英文 ('en')

### `zh.json` (67 行)
- 中文翻译文件
- 包含两部分：
  - **ui** - 所有 UI 文本标签
  - **level1** - 第一关的所有文本（故事、选项、结果）
- 结构示例:
  ```json
  {
    "ui": {
      "stamina_label": "体力值",
      "bribe_full": "贿路与交易",
      ...
    },
    "level1": {
      "title": "第一关：...",
      "scene": "...",
      "options": { "A": {...}, "B": {...}, "C": {...} },
      "results": { "A": {...}, "B": {...}, "C": {...} }
    }
  }
  ```

### `en.json` (类似结构)
- 英文翻译文件
- 与 `zh.json` 结构相同，但是英文翻译

---

## 📖 关卡系统 (`game/levels/` 目录)

### `level1.py` (80+ 行)
- **第一天的关卡实现** - 所有其他关卡的模板
- 继承自 `game.level.Level`
- 实现所有必需方法
- 所有数据来自 i18n JSON
- 实现了三个选择 (A, B, C)
- 用作其他关卡的参考实现

### `__init__.py` (5 行)
- 包初始化文件
- 导出 `Level1` 类

---

## 📚 文档文件

### `README.md` (新) 🆕
- **项目说明文档** - 最重要的用户文档
- 包含：
  - 快速开始说明
  - 游戏特点介绍
  - 文件结构说明
  - 双语本地化说明
  - 开发指南（如何添加关卡、翻译、图片）
  - 技术栈说明
  - 系统要求

### `UI_REFINEMENTS.md`
- **UI 细节调整文档**
- 记录最新的 UI 改进：
  - 路线完整名称显示
  - 真相线索功能
  - 背景图占据空间
  - 多语言一致性
  - 双语准备

### `PROJECT_STATUS.md`
- **项目状态报告**
- 包含：
  - 完整的清理摘要
  - 最终项目结构
  - 删除的文件详情
  - 代码质量指标
  - 验证清单
  - 后续建议

### `CLEANUP_REPORT.md`
- **详细的清理工作报告**
- 列出：
  - 所有删除的文件及原因
  - 代码量统计
  - 项目统计
  - 项目现状

### `CLEANUP_SUMMARY.md`
- **清理工作总结**
- 关键信息概览

### `QUICK_REFERENCE.md`
- **快速参考指南** 🆕
- 快速上手文档：
  - 启动游戏命令
  - 文件总览表
  - 基本操作步骤
  - 常见问题解答
  - 开发路线

### `COMPLETION_NOTICE.md`
- **项目完成通知** 🆕
- 项目清理完成的通知和总结

---

## 🔄 文件关系图

```
start_game_new.py
    ↓
runner_gui_new.py (main())
    ↓
    ├→ language_selector.py (选择语言)
    ├→ GameWindow (创建 UI)
    │  ├→ PropertyPanel
    │  ├→ ItemPanel
    │  ├→ ImagePanel
    │  └→ NarrativePanel
    │
    ├→ i18n/__init__.py (获取翻译)
    │  ├→ i18n/zh.json 或 en.json
    │
    ├→ manager.py (管理关卡)
    │  └→ levels/level1.py (获取关卡数据)
    │
    └→ image_manager.py (管理图片)
```

---

## 📊 文件统计

| 类型 | 数量 | 总行数 |
|------|------|--------|
| Python 源文件 | 17 | ~2000+ |
| JSON 文件 | 2 | ~140 |
| Markdown 文档 | 7 | ~2000+ |
| **总计** | **26** | **~4140+** |

---

## 🎯 文件优先级

### 🔴 必须理解
1. `start_game_new.py` - 启动脚本
2. `runner_gui_new.py` - 主游戏逻辑
3. `level.py` - 关卡基类（添加新关卡时必需）
4. `levels/level1.py` - 关卡模板示例

### 🟡 重要文件
1. `widgets_new.py` - UI 系统（定制 UI 时）
2. `i18n/__init__.py` - i18n 系统（添加翻译时）
3. `state.py` - 游戏状态（修改属性时）
4. `manager.py` - 关卡管理（修改关卡流程时）

### 🟢 参考文件
1. `image_manager.py` - 图片管理（添加图片时）
2. `language_selector.py` - 语言选择（修改语言系统时）
3. `i18n/*.json` - 翻译数据（添加翻译时）

### 🔵 文档文件
1. `README.md` - 开发指南
2. `QUICK_REFERENCE.md` - 快速参考
3. `UI_REFINEMENTS.md` - UI 细节
4. 其他文档 - 参考资料

---

## 💡 快速导航

| 我想... | 看这个文件 |
|--------|----------|
| 启动游戏 | `start_game_new.py` |
| 添加新关卡 | `levels/level1.py` (模板) + `README.md` |
| 修改 UI | `widgets_new.py` |
| 添加翻译 | `i18n/zh.json` 或 `en.json` |
| 修改游戏逻辑 | `runner_gui_new.py` |
| 修改属性系统 | `state.py` |
| 管理图片 | `image_manager.py` |
| 理解项目 | `README.md` |
| 快速查询 | `QUICK_REFERENCE.md` |

---

📝 **最后更新**: 2025-11-06  
✅ **文件清理**: 完成  
🎮 **项目状态**: 生产就绪

