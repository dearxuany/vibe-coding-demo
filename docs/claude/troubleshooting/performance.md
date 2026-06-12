# 性能优化

## 上下文管理

### 理解上下文窗口

Claude Code 的上下文包含：
- 系统提示词（固定开销）
- CLAUDE.md 项目指引
- Memory 文件
- 对话历史
- 工具调用结果
- 当前工具调用参数

### 减少上下文消耗

#### 1. 精简 CLAUDE.md

```markdown
# 优化前（冗长）
## Architecture
The project is a Flask web application that serves Prometheus metrics.
It uses the prometheus_client library for instrumentation.
The main file is app.py which contains all the routes...

# 优化后（简洁）
## Architecture
- app.py — Flask app with 4 routes (/, /health, /api/hello, /metrics)
- templates/ — Jinja2 templates
- Uses prometheus_client for metrics
```

#### 2. 管理 Memory 文件

```bash
# 列出 memory 文件
ls .claude/memory/

# 删除不再需要的
rm .claude/memory/old-reference.md

# 合并相似内容
# 多个相关 memory 合并为一个文件
```

#### 3. 分会话处理

不要在一个会话中完成所有任务：

```
会话 1: "创建 User 模型和数据库迁移"
会话 2: "实现认证 API"
会话 3: "添加前端登录页面"
```

#### 4. 使用 /compact

当会话变长时：

```bash
/compact
```

自动压缩会将对话历史总结为关键信息，释放上下文空间。

## 模型选择策略

| 任务类型 | 推荐模型 | 原因 |
|----------|----------|------|
| 简单修复 | Haiku | 快速、低成本 |
| 日常开发 | Sonnet | 平衡性能和成本 |
| 复杂架构 | Opus | 最强推理能力 |
| 代码审查 | Sonnet | 性价比最佳 |

### 动态切换

```bash
# 简单任务切换到 Haiku
/model haiku
"修复这个拼写错误"

# 复杂任务切换到 Opus
/model opus
"设计数据库 schema 并考虑扩展性"
```

## 工作流优化

### 并行 vs 串行

```javascript
// ❌ 串行 — 慢
const a = await agent('task A')
const b = await agent('task B')
const c = await agent('task C')

// ✅ 并行 — 快
const [a, b, c] = await parallel([
  () => agent('task A'),
  () => agent('task B'),
  () => agent('task C'),
])
```

### Pipeline vs Parallel

```javascript
// ❌ 不必要的 barrier — 浪费等待时间
const all = await parallel(tasks.map(t => () => agent(t)))
const processed = all.map(transform)

// ✅ 使用 pipeline — 处理完一个立即进入下一阶段
const results = await pipeline(
  tasks,
  t => agent(t),
  r => transform(r)
)
```

### 批量操作

```javascript
// ❌ 逐个处理 — N 次 API 调用
for (const file of files) {
  await agent(`处理 ${file}`)
}

// ✅ 批量处理 — 1 次 API 调用
await agent(`处理以下文件:\n${files.join('\n')}`)
```

## 缓存优化

### Prompt Caching

Anthropic API 支持 prompt caching（5 分钟 TTL），合理利用可降低 90% 的输入成本：

1. **保持会话活跃** — 5 分钟内的连续对话享受缓存
2. **稳定上下文** — CLAUDE.md 和 memory 内容不变时可被缓存
3. **避免频繁重启** — 每次重启都需要重建缓存

### 工具调用优化

```javascript
// ❌ 多次小调用
const line1 = await agent('读第 1 行')
const line2 = await agent('读第 2 行')

// ✅ 一次大调用
const all = await agent('读整个文件')
```

## 监控指标

### 使用 /cost 监控

```bash
# 定期检查费用
/cost

# 输出示例：
# Total tokens: 125,430
# Input tokens: 98,200 ($0.30)
# Output tokens: 27,230 ($0.41)
# Total cost: $0.71
```

### Token 消耗估算

| 操作 | 大致 Token 消耗 |
|------|----------------|
| CLAUDE.md (500行) | ~2,000 tokens |
| 单个文件读取 (200行) | ~1,500 tokens |
| 工具调用结果 | ~500-5,000 tokens |
| 每轮对话输出 | ~500-8,000 tokens |

## 项目结构优化

### 大型项目分模块

```
.claude/
├── CLAUDE.md              # 总体概述（精简）
├── memory/
│   ├── architecture.md    # 架构细节
│   ├── conventions.md     # 编码规范
│   └── api-docs.md        # API 文档
```

CLAUDE.md 只放高频信息，细节通过 memory 按需加载。

### 使用 .gitignore 减少噪音

```gitignore
# 不让 Claude 看到不需要的文件
node_modules/
dist/
build/
*.log
coverage/
```

Claude Code 会读取 `.gitignore` 来决定哪些文件需要关注。
