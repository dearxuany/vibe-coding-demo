## 一、终端 CLI 启动命令

| 命令 | 功能说明 |
| :--- | :--- |
| `claude` | 启动交互式 REPL 环境 |
| `claude "任务描述"` | 启动时直接携带任务 |
| `claude -p "查询"` | 非交互模式，执行后自动退出 |
| `claude -c` | 继续当前目录最近一次对话 |
| `claude -r <会话ID>` | 恢复指定历史会话 |
| `claude update` | 更新 Claude Code 到最新版 |
| `claude mcp` | 进入 MCP 服务器配置 |
| `claude commit` | 用 Claude 生成 Git 提交信息 |
| `cat 文件 \| claude -p "分析"` | 管道传递内容进行分析 |

**使用示例：**
```bash
# 基础启动
claude

# 继续上次对话
claude --continue

# 非交互模式查询
claude -p "检查这个文件的错误"

# 指定模型
claude --model opus
```

---

## 二、交互模式快捷键

| 快捷键 | 功能说明 |
| :--- | :--- |
| `Ctrl+C` | 取消当前输入或生成 |
| `Ctrl+D` | 安全退出会话 |
| `Ctrl+L` | 清屏（保留对话历史） |
| `Tab` | 切换扩展思考模式 |
| `Shift+Tab` / `Alt+M` | 切换权限模式 |
| `Ctrl+R` | 反向搜索历史提示词 |
| `Esc` 双击 | 回退对话（仅重置对话，不撤销代码） |
| `Ctrl+A` / `Ctrl+E` | 行首 / 行尾 |
| `Option+F` / `Option+B` | 单词前进 / 后退 |
| `Ctrl+W` | 删除前一个单词 |

---

## 三、内置斜杠命令（对话内使用）

| 命令 | 功能说明 |
| :--- | :--- |
| `/help` | 显示所有可用命令 |
| `/clear` | 清空当前会话上下文 |
| `/compact` | 压缩对话内容，节省 Token |
| `/init` | 生成 `CLAUDE.md` 项目记忆文件 |
| `/memory` | 编辑长期记忆 |
| `/todos` | 管理任务清单 |
| `/review` | 发起代码审查 |
| `/bug` | 报告工具错误 |
| `/config` | 调整全局设置 |
| `/status` | 查看运行状态 |
| `/doctor` | 诊断安装问题 |
| `/context` | 可视化上下文占用 |
| `/cost` | 统计 Token 成本 |
| `/vim` | 开启 Vim 编辑模式 |

---

## 四、提示原则（适用于 Claude）

**TRIRO 原则**可显著提升 Claude 回答质量：

| 原则 | 说明 |
| :--- | :--- |
| **T**ask | 明确描述具体任务 |
| **R**ole | 设定角色（如"资深软件工程师"） |
| **I**teration | 通过多次反馈迭代优化 |
| **R**eference | 提供参考示例或文档 |
| **O**utput | 明确输出格式和风格 |

Claude 偏好"合约式"指令——清楚列出做什么、不做什么，使用 `<task>`、`<context>` 等 XML 标签效果更佳。