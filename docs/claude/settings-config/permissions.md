# 权限管理最佳实践

## 权限模型

Claude Code 的权限系统基于工具级别的 allow/deny 规则，支持通配符匹配。

### 工具类型

| 工具 | 说明 | 风险等级 |
|------|------|----------|
| `Read` | 读取文件 | 低 |
| `Write` | 写入文件 | 中 |
| `Edit` | 编辑文件 | 中 |
| `Bash` | 执行命令 | 高 |
| `WebSearch` | 搜索网页 | 低 |
| `WebFetch` | 获取 URL 内容 | 中 |
| `NotebookEdit` | 编辑 Jupyter Notebook | 中 |

## 推荐配置

### 开发环境（安全）

```json
{
  "permissions": {
    "allow": [
      "Read(*)",
      "Write(*)",
      "Edit(*)",
      "Bash(npm test)",
      "Bash(npm run *)",
      "Bash(python -m pytest *)",
      "Bash(git diff)",
      "Bash(git status)",
      "Bash(git log *)",
      "Bash(git branch)",
      "Bash(ls *)",
      "Bash(cat *)",
      "WebSearch(*)",
      "WebFetch(*)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push *)",
      "Bash(git reset --hard *)",
      "Bash(curl *)",
      "Bash(wget *)",
      "Bash(sudo *)",
      "Bash(chmod 777 *)",
      "Bash(> *)",
      "Bash(docker rm *)"
    ]
  }
}
```

### CI 环境（受控）

```json
{
  "permissions": {
    "defaultMode": "acceptEdits",
    "allow": [
      "Read(*)",
      "Write(*)",
      "Edit(*)",
      "Bash(*)",
      "WebSearch(*)",
      "WebFetch(*)"
    ],
    "deny": [
      "Bash(rm -rf / *)",
      "Bash(curl * | sh)",
      "Bash(wget * -O *)",
      "Bash(sudo *)"
    ]
  }
}
```

### 演示/教学环境（完全信任）

```json
{
  "permissions": {
    "defaultMode": "bypassPermissions"
  }
}
```

## 通配符规则

| 模式 | 匹配 |
|------|------|
| `Bash(*)` | 所有 Bash 命令 |
| `Bash(npm *)` | 所有 npm 命令 |
| `Bash(npm test)` | 精确匹配 `npm test` |
| `Bash(git *)` | 所有 git 命令 |
| `Bash(git push *)` | 所有 git push 命令 |
| `WebSearch(*)` | 所有网页搜索 |
| `WebFetch(https://docs.example.com/*)` | 仅允许特定域名 |

## 安全最佳实践

### 1. 最小权限原则

只开放 Claude 完成任务所需的最小权限：

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(npm run lint)",
      "Bash(git diff)",
      "Bash(git status)"
    ]
  }
}
```

### 2. 分环境配置

```json
// 开发环境 — settings.local.json
{
  "permissions": {
    "allow": ["Bash(npm run dev)", "Bash(npm test)"]
  }
}

// 生产环境 — 不要配置 bypassPermissions
```

### 3. 危险操作明确拒绝

```json
{
  "permissions": {
    "deny": [
      "Bash(rm -rf *)",
      "Bash(> /dev/*)",
      "Bash(dd *)",
      "Bash(mkfs.*)",
      "Bash(:(){ :|:& };:)",
      "Bash(git push --force origin main)",
      "Bash(curl * | bash)",
      "Bash(wget * -O - | sh)"
    ]
  }
}
```

### 4. 定期审查

```bash
# 查看当前权限配置
cat .claude/settings.json | grep -A 20 permissions

# 检查是否有过宽的 allow 规则
grep -r "Bash(\*)" .claude/settings.json
```

### 5. 敏感信息保护

```json
// settings.local.json — 不提交到 Git
{
  "env": {
    "API_KEY": "sk-xxx",
    "DATABASE_URL": "postgresql://..."
  }
}
```

```gitignore
# .gitignore
.claude/settings.local.json
```

## 常见场景

### 前端项目

```json
{
  "permissions": {
    "allow": [
      "Bash(npm *)",
      "Bash(npx *)",
      "Bash(git *)",
      "WebSearch(*)",
      "WebFetch(*)"
    ],
    "deny": [
      "Bash(npm publish)",
      "Bash(git push *)"
    ]
  }
}
```

### Python 项目

```json
{
  "permissions": {
    "allow": [
      "Bash(python *)",
      "Bash(pip *)",
      "Bash(pytest *)",
      "Bash(black *)",
      "Bash(ruff *)",
      "Bash(mypy *)",
      "Bash(git *)",
      "WebSearch(*)"
    ],
    "deny": [
      "Bash(pip install --user *)",
      "Bash(git push --force *)"
    ]
  }
}
```
