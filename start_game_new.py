#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
New GUI Game Launcher
新 UI 游戏启动器
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.runner_gui_new import main

if __name__ == '__main__':
    main()
