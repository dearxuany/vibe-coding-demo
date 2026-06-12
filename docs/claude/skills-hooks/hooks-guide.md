# Hooks 配置指南

## 什么是 Hooks

Hooks 是 Claude Code 的事件驱动自动化机制。在特定事件发生时（如写入文件、执行命令、会话启动等），自动触发自定义动作。

## 可用事件

| 事件 | 触发时机 |
|------|----------|
| `PreToolUse` | 工具调用之前 |
| `PostToolUse` | 工具调用之后 |
| `Notification` | 收到通知时 |
| `UserPromptSubmit` | 用户提交提示词时 |
| `SessionStart` | 会话启动时 |
| `SessionEnd` | 会话结束时 |
| `Stop` | Claude 停止响应时 |

## 配置 Hooks

在 `settings.json` 中配置：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "command": "python -m pytest tests/ -q --tb=short"
          }
        ]
      },
      {
        "matcher": "Write",
        "hooks": [
          {
            "command": "black --check --diff ${CLAUDE_TOOL_FILE_PATH}"
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "command": "git fetch --all --prune"
          }
        ]
      }
    ]
  }
}
```

## 常用 Hooks 示例

### 自动运行测试

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "command": "python -m pytest tests/ -x --tb=short 2>&1 | tail -20"
          }
        ]
      }
    ]
  }
}
```

每次 Claude 写入或编辑文件后，自动运行测试。

### 自动格式化代码

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "command": "npx prettier --write ${CLAUDE_TOOL_FILE_PATH}"
          }
        ]
      }
    ]
  }
}
```

### 代码质量检查

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "command": "npx eslint ${CLAUDE_TOOL_FILE_PATH} --format compact"
          }
        ]
      }
    ]
  }
}
```

### 会话启动准备

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "command": "git fetch --all --prune && git status --short"
          }
        ]
      }
    ]
  }
}
```

### 自动提交

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "command": "git add -A && git diff --cached --quiet || git commit -m 'chore: auto-save session changes'"
          }
        ]
      }
    ]
  }
}
```

## Hook 环境变量

Hook 命令中可以使用的环境变量：

| 变量 | 说明 |
|------|------|
| `CLAUDE_TOOL_NAME` | 触发 Hook 的工具名称 |
| `CLAUDE_TOOL_FILE_PATH` | 被修改的文件路径 |
| `CLAUDE_PROJECT_DIR` | 项目根目录 |

## Hook 最佳实践

1. **轻量快速** — Hook 命令应在秒级完成，避免阻塞 Claude
2. **非侵入** — Hook 失败不应阻止 Claude 继续工作
3. **matcher 精准** — 使用正则精确匹配，避免不必要的触发
4. **输出简洁** — 使用 `tail -20` 等限制输出长度
5. **团队共识** — 项目级 Hook 需要团队一致同意
