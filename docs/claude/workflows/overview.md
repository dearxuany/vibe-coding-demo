# 工作流概述

## 什么是工作流

Claude Code 工作流（Workflow）是编排多个子 Agent 协同完成复杂任务的脚本机制。工作流脚本使用 JavaScript 编写，通过 `parallel()`、`pipeline()` 等函数实现并行和流水线处理。

## 基本结构

```javascript
export const meta = {
  name: 'my-workflow',
  description: '我的工作流描述',
  phases: [
    { title: '扫描', detail: '扫描代码库' },
    { title: '分析', detail: '分析发现的问题' },
  ],
}

phase('扫描')
const findings = await agent('扫描代码库中的安全问题', {
  schema: FINDINGS_SCHEMA,
})

phase('分析')
const results = await agent(`分析这些发现: ${JSON.stringify(findings)}`)
```

## 核心 API

### agent(prompt, options)

启动一个子 Agent 执行任务。

```javascript
// 基础用法 — 返回文本
const result = await agent('找到所有未使用的导入')

// 结构化输出 — 返回解析后的对象
const bugs = await agent('找到所有 bug', {
  schema: {
    type: 'object',
    properties: {
      bugs: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            file: { type: 'string' },
            line: { type: 'number' },
            description: { type: 'string' },
          },
        },
      },
    },
  },
})

// 指定 Agent 类型
const review = await agent('审查 app.py', {
  agentType: 'code-reviewer',
})
```

### parallel(tasks)

并行执行多个任务，等待全部完成后返回结果。

```javascript
const results = await parallel([
  () => agent('审查 auth.py', { schema: REVIEW_SCHEMA }),
  () => agent('审查 api.py', { schema: REVIEW_SCHEMA }),
  () => agent('审查 models.py', { schema: REVIEW_SCHEMA }),
])
```

### pipeline(items, stage1, stage2, ...)

流水线处理 — 每个 item 独立流经所有 stage，无需等待其他 item。

```javascript
const results = await pipeline(
  ['auth.py', 'api.py', 'models.py'],
  // Stage 1: 审查
  (file) => agent(`审查 ${file}`, { schema: REVIEW_SCHEMA, phase: '审查' }),
  // Stage 2: 验证发现
  (review) => agent(`验证这个发现是否真实: ${review.title}`, {
    schema: VERDICT_SCHEMA,
    phase: '验证',
  })
)
```

### budget

控制 token 消耗。

```javascript
// 在预算内循环查找
while (budget.total && budget.remaining() > 50_000) {
  const result = await agent('查找更多问题', { schema: BUGS_SCHEMA })
  bugs.push(...result.bugs)
}
```

## 工作流设计模式

### 1. 查找-验证模式

先并发查找，再逐个验证。

```javascript
export const meta = {
  name: 'find-and-verify',
  description: '查找问题并验证',
  phases: [
    { title: '查找', detail: '多角度扫描问题' },
    { title: '验证', detail: '验证每个发现的真实性' },
  ],
}

// 多角度查找
const finders = [
  { key: 'bugs', prompt: '查找逻辑错误' },
  { key: 'perf', prompt: '查找性能问题' },
  { key: 'security', prompt: '查找安全漏洞' },
]

const results = await pipeline(
  finders,
  (f) => agent(f.prompt, { label: f.key, phase: '查找', schema: FINDINGS_SCHEMA }),
  (findings) => parallel(
    findings.map((f) => () =>
      agent(`验证: ${f.title}`, { phase: '验证', schema: VERDICT_SCHEMA })
    )
  )
)
```

### 2. 审查-修复模式

审查代码后自动应用修复。

```javascript
export const meta = {
  name: 'review-and-fix',
  description: '审查并修复代码',
  phases: [
    { title: '审查', detail: '代码审查' },
    { title: '修复', detail: '应用修复' },
  ],
}

phase('审查')
const issues = await agent('审查变更', { schema: ISSUES_SCHEMA })

phase('修复')
const fixes = await pipeline(
  issues,
  (issue) => agent(`修复: ${issue.description}`, { phase: '修复' })
)
```

### 3. 对抗验证模式

多个 Agent 独立审查同一问题，多数投票决定。

```javascript
const votes = await parallel(
  Array.from({ length: 3 }, (_, i) => () =>
    agent(`审查这个变更是否引入了 bug。你是第 ${i + 1} 位审查者。`, {
      schema: {
        type: 'object',
        properties: {
          hasBug: { type: 'boolean' },
          severity: { type: 'string', enum: ['low', 'medium', 'high'] },
        },
      },
    })
  )
)

const bugConfirmed = votes.filter(Boolean).filter((v) => v.hasBug).length >= 2
```

### 4. 循环至收敛模式

持续查找直到连续 N 轮无新发现。

```javascript
const seen = new Set()
const confirmed = []
let dry = 0

while (dry < 2) {
  const found = await agent('查找问题', { schema: BUGS_SCHEMA })
  const fresh = found.bugs.filter((b) => !seen.has(b.id))

  if (!fresh.length) {
    dry++
    continue
  }

  dry = 0
  fresh.forEach((b) => seen.add(b.id))

  const verified = await parallel(
    fresh.map((b) => () =>
      agent(`验证: ${b.description}`, { schema: VERDICT_SCHEMA })
    )
  )

  confirmed.push(...verified.filter(Boolean).filter((v) => v.isReal))
}
```

## 使用建议

1. **默认使用 pipeline()** — 除非 stage 之间确实需要所有数据，否则不需要 barrier
2. **结构化输出** — 使用 `schema` 参数获取类型安全的结果
3. **预算控制** — 大任务使用 `budget.remaining()` 防止超支
4. **命名清晰** — agent 的 `label` 参数有助于日志追踪
