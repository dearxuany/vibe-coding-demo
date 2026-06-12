# 快速入门

## 安装 Claude Code

```bash
# npm 全局安装
npm install -g @anthropic-ai/claude-code

# 或使用 npx 直接运行
npx @anthropic-ai/claude-code
```

## 首次启动

```bash
# 进入项目目录后启动
cd your-project
claude
```

首次启动时 Claude Code 会引导你完成：
1. **认证** — 使用 Anthropic API Key 或 OAuth 登录
2. **模型选择** — 默认推荐使用最新的 Claude 模型
3. **项目初始化** — 自动生成 `CLAUDE.md` 项目指引文件

## 基本命令

### 对话模式

```bash
# 启动交互式对话
claude

# 带初始提示词启动
claude "解释这个项目的架构"

# 管道模式
cat error.log | claude "分析这些错误日志"
```

### 斜杠命令

| 命令 | 说明 |
|------|------|
| `/help` | 查看帮助 |
| `/clear` | 清空对话历史 |
| `/compact` | 压缩上下文（保留关键信息） |
| `/config` | 打开配置界面 |
| `/cost` | 查看当前会话费用 |
| `/doctor` | 诊断环境问题 |
| `/init` | 初始化项目 CLAUDE.md |
| `/review` | 审查 PR 变更 |
| `/security-review` | 安全审查 |

### 文件操作

在对话中直接描述需求，Claude Code 会自动读写文件：

```
"帮我重构 app.py 中的 User 类，提取到单独的 models.py"
"给所有 API 端点添加请求日志"
"修复 README.md 中的拼写错误"
```

## 关键概念

### CLAUDE.md

项目根目录下的 `CLAUDE.md` 是 Claude Code 的项目指引文件，包含：
- 项目描述和架构说明
- 常用命令（构建、测试、运行）
- 编码规范和约定
- 重要注意事项

Claude Code 每次会话都会自动加载此文件作为上下文。

### 权限控制

Claude Code 默认需要你确认文件写入、命令执行等操作。可以通过 `settings.json` 配置权限：

```json
{
  "permissions": {
    "allow": ["Bash(npm test)", "Bash(git diff)", "Bash(git status)"]
  }
}
```

### 上下文管理

- 对话历史会持续累积，长会话建议使用 `/compact` 压缩
- CLAUDE.md 和 memory 文件始终保持在上下文中
- 使用 `/cost` 监控 token 消耗

## 下一步

- 阅读 [项目配置指南](project-setup.md) 优化你的 CLAUDE.md
- 学习 [提示词工程](prompt-engineering.md) 提高交互效率
