# 项目配置指南

## CLAUDE.md 最佳实践

`CLAUDE.md` 是 Claude Code 最重要的项目配置文件。它在每次会话启动时自动加载到上下文中。

### 推荐结构

```markdown
# CLAUDE.md

## About
简短的项目描述（1-2句话）。

## Commands
列出常用命令，Claude 可以直接执行：
- 构建命令
- 测试命令
- 运行命令
- Lint / 格式化命令

## Architecture
描述项目架构：
- 目录结构和各目录用途
- 核心技术栈
- 关键模块和它们的职责
- 数据流向

## Conventions
编码规范：
- 命名约定
- 文件组织规则
- 注释风格
- 测试策略

## Important Notes
需要特别注意的事项：
- 已知限制
- 外部依赖
- 环境变量要求
```

### 编写原则

1. **简洁精确** — CLAUDE.md 会被加载到每次会话的上下文中，冗长内容会消耗 token
2. **命令优先** — 列出可执行的命令而非描述性说明，Claude 可以直接运行
3. **结构清晰** — 使用标题层级组织内容，方便 Claude 定位信息
4. **及时更新** — 项目结构变化后同步更新 CLAUDE.md

### 示例

```markdown
# CLAUDE.md

## About
A Flask + Prometheus metrics demo.

## Commands
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run
python app.py                    # port 5000, or set PORT env var

# Test
python -m pytest tests/ -v

## Architecture
- app.py — Flask app with metrics endpoints
- templates/ — Jinja2 templates
- static/ — static assets
- docs/ — Markdown documentation
```

## .gitignore 配置

确保以下内容在 `.gitignore` 中：

```gitignore
# Python
__pycache__/
*.pyc
venv/
.venv/

# Claude Code
.claude/

# Environment
.env
.env.local
```

## Memory 系统

Claude Code 支持持久化记忆功能，存储在 `.claude/memory/` 目录下。每个记忆文件包含：

```markdown
---
name: short-kebab-slug
description: 一句话描述
metadata:
  type: user | feedback | project | reference
---

记忆内容...
```

### 记忆类型

| 类型 | 用途 |
|------|------|
| `user` | 用户偏好、角色、专长 |
| `feedback` | 用户反馈和纠正 |
| `project` | 项目状态、决策、约束 |
| `reference` | 外部资源链接（URL、文档） |

## 多项目配置

### 全局设置 vs 项目设置

```
~/.claude/settings.json       # 全局设置（所有项目生效）
.claude/settings.json         # 项目级设置（覆盖全局）
.claude/settings.local.json   # 本地设置（不提交到 Git）
```

推荐做法：
- 全局设置：个人偏好（主题、模型选择）
- 项目设置：团队共享的权限和钩子
- 本地设置：敏感信息、个人调试配置

### settings.json 关键配置

```json
{
  "model": "claude-sonnet-4-6",
  "theme": "dark",
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(npm run lint)",
      "Bash(git diff)",
      "Bash(git status)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{"command": "python -m pytest tests/ -q"}]
      }
    ]
  }
}
```
