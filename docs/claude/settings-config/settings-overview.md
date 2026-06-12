# Settings 配置参考

## 配置文件位置

```
~/.claude/settings.json          # 全局用户设置
<project>/.claude/settings.json  # 项目设置（提交到 Git）
<project>/.claude/settings.local.json  # 本地设置（不提交）
```

优先级：`settings.local.json` > `settings.json`（项目） > `settings.json`（全局）

## 完整配置项

### 基础设置

```json
{
  "model": "claude-sonnet-4-6",
  "theme": "dark",
  "autoCompact": true,
  "autoCompactThreshold": 0.8
}
```

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `model` | 模型 ID | 默认使用的 Claude 模型 |
| `theme` | `"dark"` `"light"` | 终端主题 |
| `autoCompact` | `boolean` | 是否自动压缩上下文 |
| `autoCompactThreshold` | `0.0-1.0` | 触发自动压缩的阈值 |

### 可用模型

| 模型 ID | 说明 |
|---------|------|
| `claude-sonnet-4-6` | 默认推荐，平衡性能与成本 |
| `claude-opus-4-8` | 最强性能，适合复杂任务 |
| `claude-haiku-4-5` | 最快速度，适合简单任务 |
| `claude-fable-5` | 最新模型 |

### 权限配置

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(npm run lint)",
      "Bash(git diff)",
      "Bash(git status)",
      "Bash(git log *)",
      "WebSearch(*)",
      "WebFetch(*)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force *)",
      "Bash(git reset --hard *)",
      "Bash(curl *)",
      "Bash(wget *)"
    ],
    "defaultMode": "acceptEdits"
  }
}
```

| 配置项 | 说明 |
|--------|------|
| `allow` | 自动允许的工具调用（支持通配符） |
| `deny` | 始终拒绝的工具调用 |
| `defaultMode` | 默认权限模式 |

### 权限模式

| 模式 | 说明 |
|------|------|
| `default` | 每次询问 |
| `acceptEdits` | 自动接受文件编辑 |
| `bypassPermissions` | 跳过所有权限检查（仅限信任环境） |

### MCP 服务器

```json
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-filesystem", "/path/to/data"]
    },
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "postgres": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-postgres", "${DATABASE_URL}"]
    }
  }
}
```

### Hooks

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{"command": "npm test"}]
      }
    ],
    "SessionStart": [
      {
        "hooks": [{"command": "git fetch --all"}]
      }
    ]
  }
}
```

### Worktree 配置

```json
{
  "worktree": {
    "baseRef": "fresh",
    "autoCleanup": true
  }
}
```

| 值 | 说明 |
|-----|------|
| `baseRef: "fresh"` | 从 origin/main 创建 worktree |
| `baseRef: "head"` | 从当前 HEAD 创建 worktree |
| `autoCleanup` | 是否自动清理未使用的 worktree |

### 其他设置

```json
{
  "env": {
    "DEBUG": "true",
    "API_URL": "http://localhost:3000"
  },
  "includeCoAuthoredBy": false,
  "skipCommitMessagePrompts": false
}
```

| 配置项 | 说明 |
|--------|------|
| `env` | 传递给 Hook 的环境变量 |
| `includeCoAuthoredBy` | 是否在 commit 中包含 Co-Authored-By |
| `skipCommitMessagePrompts` | 是否跳过 commit message 提示 |

## 配置管理建议

1. **分层配置** — 全局放个人偏好，项目级放团队共享配置，本地放敏感信息
2. **权限最小化** — 只 allow 确实需要的命令，deny 危险操作
3. **版本控制** — `settings.json` 提交到 Git，`settings.local.json` 加入 `.gitignore`
4. **定期审查** — 随着项目演进，审查和更新权限配置
