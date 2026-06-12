# TDD 工作流

## 概述

使用 Claude Code 实践测试驱动开发（TDD）的最佳方式。

## 标准 TDD 循环

```
1. RED   — 写一个失败的测试
2. GREEN — 写最少代码让测试通过
3. REFACTOR — 重构代码，保持测试通过
```

## 使用 Claude Code 实践 TDD

### 第一步：描述需求

```
"我需要一个 validate_email 函数，要求：
- 检查 email 是否包含 @
- 检查 @ 前后都有内容
- 检查域名部分包含 .
- 返回 True/False

请先生成测试用例，不要写实现。"
```

### 第二步：生成测试

Claude 生成测试文件：

```python
# test_email.py
import pytest
from email_validator import validate_email

def test_valid_email():
    assert validate_email("user@example.com") is True

def test_no_at_symbol():
    assert validate_email("userexample.com") is False

def test_empty_string():
    assert validate_email("") is False

def test_no_local_part():
    assert validate_email("@example.com") is False

def test_no_domain():
    assert validate_email("user@") is False

def test_no_dot_in_domain():
    assert validate_email("user@example") is False
```

### 第三步：生成实现

```
"现在实现 validate_email 函数，让这些测试通过。"
```

### 第四步：重构

```
"validate_email 可以工作但代码可读性不好，
请用正则表达式重写，保持所有测试通过。"
```

## 自动化 TDD 工作流

```javascript
export const meta = {
  name: 'tdd-cycle',
  description: '自动 TDD 循环',
  phases: [
    { title: '生成测试', detail: '根据需求生成测试' },
    { title: '实现', detail: '实现功能' },
    { title: '重构', detail: '优化代码' },
  ],
}

const requirement = args.requirement

// 1. 生成测试
phase('生成测试')
const tests = await agent(
  `根据以下需求生成测试用例（只写测试，不写实现）：
${requirement}

请使用 ${args.framework || 'pytest'} 框架。`,
  { label: 'generate-tests' }
)

// 2. 实现
phase('实现')
const impl = await agent(
  `以下是要通过的测试用例。请实现满足所有测试的最小代码：

${tests}

要求：
- 只写最小实现
- 不做过度设计
- 不添加测试未要求的功能`,
  { label: 'implement' }
)

// 3. 重构
phase('重构')
const refactored = await agent(
  `以下代码已通过所有测试。请重构以提高可读性和可维护性：

${impl}

约束：
- 不改变外部 API
- 不引入新依赖
- 保持所有现有测试通过`,
  { label: 'refactor' }
)

return { tests, implementation: impl, refactored }
```

## TDD 提示词模板

### 功能需求 → 测试

```
"为以下功能编写测试，使用 [pytest/jest/go test]：
[描述功能需求]

测试应覆盖：
- 正常情况
- 边界条件
- 错误输入
- 空值/null 处理"
```

### 红-绿循环

```
"运行测试。对于每个失败的测试：
1. 分析失败原因
2. 写最少代码让其通过
3. 重新运行确认

每通过一个测试后向我汇报进度。"
```

### 重构请求

```
"所有测试通过。请审查 [文件名] 并建议重构：
- 消除重复
- 提高可读性
- 优化性能瓶颈

对每个建议，说明它如何改进代码。
只建议不自动修改。"
```

## 最佳实践

1. **测试先行** — 始终先写测试再写实现，Claude 擅长从测试推导实现
2. **小步迭代** — 一次只写一个测试/实现，保持上下文可控
3. **即时反馈** — 利用 Hooks 在每次写入后自动运行测试
4. **重构独立** — 将重构作为单独步骤，明确告诉 Claude "只重构不改变行为"
5. **覆盖边界** — 提示词中明确要求边界条件测试，Claude 容易忽略
