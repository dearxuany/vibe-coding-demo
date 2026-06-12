# 提示词工程

## 核心原则

### 1. 具体明确

❌ 差的提示词：
```
"修复 bug"
```

✅ 好的提示词：
```
"修复 app.py 第 42 行 login 函数中密码验证失败时没有返回 401 状态码的问题"
```

### 2. 提供上下文

```
"我正在开发一个 Flask 应用，使用 Flask-Login 做认证。
请帮我实现一个记住我（Remember Me）功能，使用 Flask-Login 的 remember 参数。"
```

### 3. 分步指令

复杂任务分解为多个步骤：

```
"请完成以下步骤：
1. 创建 models/user.py，定义 User 数据模型
2. 创建 services/auth.py，实现认证逻辑
3. 更新 app.py，注册新的 Blueprint
4. 添加单元测试"
```

### 4. 指定约束条件

```
"重构 utils.py，要求：
- 保持所有公开 API 不变
- 不引入新的依赖
- 使用类型注解
- 添加 docstring"
```

## 常用模式

### 代码生成

```
"帮我创建一个 Python FastAPI 端点，功能是：
- POST /api/users
- 接收 JSON: {name, email, role}
- 验证 email 格式
- 写入 SQLite 数据库
- 返回 201 Created"
```

### 代码审查

```
"审查 app.py 的变更，重点关注：
- SQL 注入风险
- 异常处理是否完整
- 是否有资源泄漏"
```

### 调试

```
"这段代码在 production 环境中偶发 500 错误，
错误日志显示 'KeyError: user_id'。
请分析可能的原因并给出修复方案。"

[粘贴相关代码]
```

### 重构

```
"将 app.py 中的路由处理函数拆分到独立的 Blueprint 模块：
- auth.py — 登录/登出/注册
- api.py — API 端点
- pages.py — 页面路由
保持所有 URL 路径不变。"
```

### 文档生成

```
"为 api/ 目录下的所有函数生成 docstring，
格式使用 Google style。"
```

## 高级技巧

### 使用文件引用

直接在对话中提及文件路径，Claude 会自动读取：

```
"参考 services/auth.py 的实现方式，为 services/payment.py 添加类似的错误处理"
```

### 渐进式改进

不要一次性提出大需求，分轮迭代：

```
第一轮: "给 User 模型添加 email 字段"
第二轮: "添加 email 格式验证"
第三轮: "添加 email 唯一性检查"
```

### 利用 CLAUDE.md

把项目约定写入 CLAUDE.md，Claude 会自动遵守：

```markdown
## Conventions
- 使用 Python 3.10+ 语法
- 所有公开函数必须有 type hints
- 异常处理使用自定义异常类，不要裸用 Exception
- 测试使用 pytest，覆盖率要求 80%+
```

### 确认后再执行

对于高风险操作，在提示词中要求先出计划：

```
"先列出改动计划，不要立即修改代码：
将 SQLite 迁移到 PostgreSQL"
```

## 避免的陷阱

1. **信息过载** — 一次性给太多无关代码，Claude 上下文有限
2. **模糊指令** — "让它更好"、"优化一下" 这类指令效果差
3. **冲突指令** — 同时要求 "保持兼容" 和 "彻底重构" 会让 Claude 困惑
4. **忽略反馈** — Claude 的提问通常是发现了歧义，认真回答
5. **跳过验证** — 生成代码后务必运行测试确认
