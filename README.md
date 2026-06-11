# Flask Metrics Demo

Flask web 服务示例，通过 `/metrics` 接口暴露 Prometheus 兼容的性能指标。

## 快速开始

```bash
# 使用脚本
bin/run.sh

# 或手动操作
python3 -m venv flask-metrics-venv
source flask-metrics-venv/bin/activate
pip install flask prometheus-client
python app.py
```

服务默认监听 `http://0.0.0.0:5000`，可通过环境变量 `PORT` 修改端口。

## 接口

| 路径 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务信息与接口列表 |
| `/health` | GET | 健康检查 |
| `/api/hello?name=xxx` | GET | 示例业务接口 |
| `/metrics` | GET | Prometheus 指标（text/plain） |

## 指标

### 自定义指标

| 指标名 | 类型 | 标签 | 说明 |
|--------|------|------|------|
| `flask_http_requests_total` | Counter | method, endpoint, status | HTTP 请求总数 |
| `flask_http_request_duration_seconds` | Histogram | method, endpoint | 请求耗时分布 |
| `flask_http_requests_in_flight` | Gauge | — | 当前处理中的请求数 |

### 内置指标

包含 `prometheus_client` 默认注册的进程指标：CPU 时间、内存使用、文件描述符数、Python GC 统计等。

## Prometheus 接入

```yaml
scrape_configs:
  - job_name: "flask-metrics-demo"
    scrape_interval: 15s
    static_configs:
      - targets: ["localhost:5000"]
```

## Docker

```bash
bin/docker-manage.sh
```

## 项目结构

```
├── bin/
│   ├── run.sh              # 本地运行脚本
│   └── docker-manage.sh    # Docker 构建 & 运行脚本
├── flask-metrics-venv/     # Python 虚拟环境
├── .claude/                # Claude Code 配置
├── .gitignore              # Git 忽略规则
├── Dockerfile              # Docker 镜像定义
├── .dockerignore           # Docker 构建忽略
├── app.py                  # Flask 应用主程序
├── quicksort.py            # 快速排序脚本
├── CLAUDE.md               # Claude Code 指引
└── README.md
```

## 依赖

- Python ≥ 3.10
- Flask 3.1
- prometheus-client 0.25

---

> **推送到 GitHub**
>
> GitHub 已不再支持密码认证，需使用 Fine-grained Personal Access Token 登录。
>
> 1. 打开 [github.com/settings/tokens](https://github.com/settings/tokens?type=beta)，点击 **Generate new token**
> 2. **Repository access**: 选择 **"Only select repositories"**，勾选目标仓库
> 3. **Permissions** → **Repository permissions**，只设一项：
>
>    | 权限 | 级别 |
>    |------|------|
>    | Contents | Read and write |
>
> 4. 生成后复制 token（仅显示一次），然后执行：
>
>    ```bash
>    git remote set-url origin https://<你的用户名>:<token>@github.com/<用户名>/<仓库名>.git
>    git push -u origin main
>    ```
>
> ⚠️ token 会明文保存在 `.git/config` 中，注意不要提交或分享该文件。
