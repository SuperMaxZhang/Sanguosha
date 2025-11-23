#!/bin/bash
# 启动三国杀游戏

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 直接使用虚拟环境的Python运行
./.venv/bin/python main.py
