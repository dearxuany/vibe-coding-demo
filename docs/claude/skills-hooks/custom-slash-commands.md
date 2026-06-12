# 自定义斜杠命令（Skills）

## 什么是 Skill

Skill 是 Claude Code 的自定义斜杠命令，通过 `/skill-name` 触发。每个 Skill 是一个 Markdown 文件，包含指令和上下文。

## 创建 Skill

### 目录结构

```
.claude/
└── skills/
    ├── deploy.md        # /deploy 命令
    ├── review.md        # /review 命令
    └── generate-api.md  # /generate-api 命令
```

### Skill 文件格式

```markdown
---
description: 部署应用到生产环境
---

# Deploy Skill

当用户调用 /deploy 时执行以下步骤：

## 步骤 1：确认分支
检查当前分支是否为 main。如果不是，询问用户确认。

## 步骤 2：运行测试
执行 `npm test`，如果有失败则终止。

## 步骤 3：构建
执行 `npm run build`。

## 步骤 4：部署
执行 `npm run deploy` 并报告结果。
```

## Skill 示例

### 部署 Skill

```markdown
---
description: 安全部署到生产环境
---

# /deploy

1. 运行 `git status` 确认没有未提交的变更
2. 确认当前在 main 分支
3. 运行 `npm test` 全量测试
4. 运行 `npm run build` 构建
5. 运行 `git push origin main`
6. 触发 CI/CD 部署
7. 等待部署完成，检查健康状态
```

### 生成变更日志 Skill

```markdown
---
description: 从 git 历史生成 CHANGELOG
---

# /changelog

1. 运行 `git log --oneline main..HEAD` 获取当前分支的提交
2. 按类型分类（feat, fix, docs, refactor 等）
3. 生成 markdown 格式的 CHANGELOG
4. 写入 CHANGELOG.md
5. 如果用户确认，添加到 git 暂存区
```

### 依赖更新 Skill

```markdown
---
description: 检查并更新过时的依赖
---

# /update-deps

1. 运行 `npm outdated` 检查过时依赖
2. 列出每个依赖的当前版本和最新版本
3. 检查 breaking changes（读取 CHANGELOG）
4. 逐个更新 patch/minor 版本
5. 运行测试确认兼容性
6. 对 major 版本更新，询问用户确认
```

## 使用现有 Skill

Claude Code 内置了一些 Skill：

| 命令 | 说明 |
|------|------|
| `/review` | 审查代码变更 |
| `/security-review` | 安全审查 |
| `/simplify` | 简化代码 |
| `/init` | 初始化项目 CLAUDE.md |
| `/loop` | 循环执行命令 |
| `/run` | 启动并测试应用 |
| `/verify` | 验证变更是否正常工作 |

## 第三方 Skill

社区维护的 Skill 可以通过插件系统安装。查看 [Claude Code 插件市场](https://github.com/anthropics/claude-code-plugins) 获取更多。

## Skill 最佳实践

1. **单一职责** — 每个 Skill 只做一件事
2. **幂等性** — Skill 应该可以安全地重复执行
3. **用户确认** — 危险操作（部署、删除）需要用户确认
4. **错误处理** — 明确说明失败时的回退策略
5. **输出清晰** — 每个步骤完成后报告状态
