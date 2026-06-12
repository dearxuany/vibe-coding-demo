# 代码审查工作流

## 内置审查命令

Claude Code 提供两个内置审查命令：

### `/review` — 审查 PR 变更

```bash
# 审查当前分支的变更
/review

# 审查指定 PR
/review #42
```

### `/security-review` — 安全审查

```bash
# 审查当前变更的安全问题
/security-review
```

## 自定义审查工作流

### 基础代码审查

```javascript
export const meta = {
  name: 'code-review-custom',
  description: '自定义多维度代码审查',
  phases: [
    { title: '审查', detail: '多维度审查' },
    { title: '验证', detail: '验证发现' },
  ],
}

const DIMENSIONS = [
  {
    key: 'bugs',
    prompt: `审查代码中的 bug：
    - 空指针/None 引用
    - 边界条件错误
    - 逻辑错误
    - 竞态条件`,
  },
  {
    key: 'security',
    prompt: `审查安全问题：
    - SQL 注入
    - XSS 漏洞
    - 敏感信息泄露
    - 不安全的反序列化
    - 权限绕过`,
  },
  {
    key: 'performance',
    prompt: `审查性能问题：
    - N+1 查询
    - 不必要的循环
    - 内存泄漏
    - 阻塞 IO
    - 缺少缓存`,
  },
  {
    key: 'maintainability',
    prompt: `审查可维护性问题：
    - 重复代码
    - 过长函数
    - 过多参数
    - 缺少类型注解
    - 魔法数字`,
  },
]

const results = await pipeline(
  DIMENSIONS,
  (d) => agent(d.prompt, {
    label: d.key,
    phase: '审查',
    schema: {
      type: 'object',
      properties: {
        findings: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              file: { type: 'string' },
              line: { type: 'number' },
              severity: { type: 'string', enum: ['critical', 'high', 'medium', 'low'] },
              title: { type: 'string' },
              description: { type: 'string' },
              suggestion: { type: 'string' },
            },
          },
        },
      },
    },
  }),
  (result) => {
    if (!result || !result.findings.length) return []
    return parallel(
      result.findings
        .filter((f) => f.severity === 'critical' || f.severity === 'high')
        .map((f) => () =>
          agent(`对抗验证此发现是否为真实问题: ${f.title}\n${f.description}`, {
            label: `verify:${f.file}:${f.line}`,
            phase: '验证',
            schema: {
              type: 'object',
              properties: {
                isReal: { type: 'boolean' },
                reason: { type: 'string' },
              },
            },
          }).then((v) => v && v.isReal ? { ...f, verified: true } : null)
        )
    )
  }
)

const confirmed = results.flat().filter(Boolean)
return { findings: confirmed, summary: `发现 ${confirmed.length} 个确认问题` }
```

### PR 描述生成

```javascript
export const meta = {
  name: 'generate-pr-description',
  description: '根据变更生成 PR 描述',
}

phase('分析变更')
const diff = await agent('分析 git diff 中的变更', {
  schema: {
    type: 'object',
    properties: {
      summary: { type: 'string' },
      changes: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            file: { type: 'string' },
            what: { type: 'string' },
            why: { type: 'string' },
          },
        },
      },
      breakingChanges: { type: 'array', items: { type: 'string' } },
      testingNotes: { type: 'string' },
    },
  },
})

// 生成 PR 正文
const body = `## Summary
${diff.summary}

## Changes
${diff.changes.map((c) => `- **${c.file}**: ${c.what}\n  > ${c.why}`).join('\n')}

${diff.breakingChanges.length ? `## ⚠️ Breaking Changes\n${diff.breakingChanges.map((c) => `- ${c}`).join('\n')}` : ''}

## Testing
${diff.testingNotes}

🤖 Generated with [Claude Code](https://claude.com/claude-code)
`

return { body }
```

## 审查最佳实践

1. **多维度审查** — 不要只查 bug，同时关注安全、性能、可维护性
2. **对抗验证** — 用多个 Agent 独立审查同一个发现，减少误报
3. **优先级排序** — critical/high 的问题需要严格验证，medium/low 可快速确认
4. **上下文完整** — 确保 Agent 能访问相关文件，不仅仅是 diff
5. **增量审查** — 大 PR 分批审查，避免单次上下文过大
