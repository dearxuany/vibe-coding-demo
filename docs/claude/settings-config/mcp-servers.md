# MCP 服务器集成

## 什么是 MCP

MCP（Model Context Protocol）是 Anthropic 推出的开放协议，允许 Claude 通过标准化的服务器接口访问外部工具和数据源。

## 配置 MCP 服务器

在 `settings.json` 中配置：

```json
{
  "mcpServers": {
    "server-name": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@scope/mcp-server-name"],
      "env": {
        "API_KEY": "${ENV_VAR}"
      }
    }
  }
}
```

## 官方 MCP 服务器

### 文件系统

```json
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@anthropic-ai/mcp-server-filesystem",
        "/path/to/allowed/directory"
      ]
    }
  }
}
```

允许 Claude 访问指定目录的文件系统。

### GitHub

```json
{
  "mcpServers": {
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

允许 Claude 操作 GitHub Issues、PR、仓库。

### PostgreSQL

```json
{
  "mcpServers": {
    "postgres": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@anthropic-ai/mcp-server-postgres",
        "postgresql://user:pass@localhost:5432/dbname"
      ]
    }
  }
}
```

允许 Claude 查询 PostgreSQL 数据库。

### Slack

```json
{
  "mcpServers": {
    "slack": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "${SLACK_TOKEN}"
      }
    }
  }
}
```

## 社区 MCP 服务器

### Docker

```json
{
  "mcpServers": {
    "docker": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-docker"]
    }
  }
}
```

### Jira

```json
{
  "mcpServers": {
    "jira": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "mcp-server-jira"],
      "env": {
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "you@example.com",
        "JIRA_API_TOKEN": "${JIRA_TOKEN}"
      }
    }
  }
}
```

## MCP 服务器开发

### 基本结构

```python
# my_mcp_server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
import asyncio

server = Server("my-server")

@server.tool("my_tool")
async def my_tool(param1: str, param2: int = 10) -> str:
    """我的自定义工具"""
    return f"处理结果: {param1} x {param2}"

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write)

if __name__ == "__main__":
    asyncio.run(main())
```

### 配置自定义服务器

```json
{
  "mcpServers": {
    "my-server": {
      "type": "stdio",
      "command": "python",
      "args": ["/path/to/my_mcp_server.py"],
      "env": {
        "MY_API_KEY": "${MY_API_KEY}"
      }
    }
  }
}
```

## 最佳实践

1. **最小权限** — MCP 服务器应只暴露必要的工具和数据
2. **环境变量** — 敏感信息（API Key、Token）通过环境变量传递
3. **错误处理** — 服务器应优雅处理错误，不暴露内部细节
4. **日志记录** — 记录工具调用日志便于审计
5. **速率限制** — 对 API 调用实现速率限制，避免超出配额
6. **输入验证** — 对所有工具输入参数进行严格验证
