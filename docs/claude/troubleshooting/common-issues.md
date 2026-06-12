# 常见问题与解决方案

## 安装问题

### npm 安装失败

```bash
# 错误：EACCES permission denied
sudo npm install -g @anthropic-ai/claude-code

# 或使用 nvm 避免权限问题
nvm install 20
nvm use 20
npm install -g @anthropic-ai/claude-code
```

### 认证失败

```bash
# 确认 API Key 已设置
echo $ANTHROPIC_API_KEY

# 设置 API Key
export ANTHROPIC_API_KEY="sk-ant-..."

# 或使用 OAuth
claude --oauth
```

## 运行时问题

### "Tool use not allowed" 错误

原因：权限配置拒绝了该工具调用。

解决方案：
1. 检查 `.claude/settings.json` 中的 `permissions.deny` 规则
2. 添加对应的 `allow` 规则
3. 或在对话中手动允许

### 上下文过大导致性能下降

现象：
- 响应变慢
- 输出截断
- 费用飙升

解决方案：
```bash
# 使用 /compact 压缩上下文
/compact

# 或在 settings.json 启用自动压缩
{
  "autoCompact": true,
  "autoCompactThreshold": 0.7
}
```

### 文件修改未被应用

原因：
- 文件被外部进程修改
- 权限不足
- 文件被 Git 锁定

解决方案：
```bash
# 检查文件状态
git status
ls -la <file>

# 检查是否有未保存的更改
git diff <file>
```

## 性能问题

### Token 消耗过高

```bash
# 查看当前会话费用
/cost

# 减少上下文的方法：
# 1. 使用 /clear 重置会话
# 2. 精简 CLAUDE.md
# 3. 删除不需要的 memory 文件
# 4. 分多个小会话完成任务
```

### 响应缓慢

可能原因和解决方案：

1. **选择了慢速模型** — 切换为 Haiku 处理简单任务
   ```
   /model haiku
   ```

2. **上下文过大** — 使用 `/compact`

3. **网络问题** — 检查网络连接

4. **API 限流** — 等待一段时间后重试

## Git 相关问题

### Claude 创建了不需要的分支

```bash
# 查看 Claude 创建的分支
git branch | grep claude

# 删除不需要的分支
git branch -D branch-name
```

### Claude 提交了不需要的更改

```bash
# 查看最近的提交
git log --oneline -10

# 撤销最近一次提交（保留更改）
git reset --soft HEAD~1

# 撤销最近一次提交（丢弃更改）
git reset --hard HEAD~1
```

## 配置问题

### 配置不生效

1. 确认配置文件路径正确
2. 检查 JSON 格式是否正确
3. 重启 Claude Code

```bash
# 验证 JSON 格式
python -m json.tool .claude/settings.json > /dev/null && echo "OK" || echo "Invalid JSON"
```

### settings.local.json 不生效

`.claude/settings.local.json` 优先级最高，但如果与 `settings.json` 中的数组配置（如 permissions）冲突，需要合并而非替换。

## 调试技巧

### 启用调试日志

```bash
# 查看诊断信息
/doctor

# 环境变量调试
DEBUG=1 claude
```

### 检查 Hook 输出

Hook 输出通常显示在终端中。如果 Hook 静默失败：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "command": "your-command 2>&1 | tee /tmp/claude-hook.log"
          }
        ]
      }
    ]
  }
}
```

### 查看 Memory 文件

```bash
# 列出所有 memory 文件
ls .claude/memory/

# 查看 memory 索引
cat .claude/memory/MEMORY.md
```
