# Flask Metrics Demo

Flask web 服务示例，通过 `/metrics` 接口暴露 Prometheus 兼容的性能指标。

## 快速开始

```bash
# 1. 创建虚拟环境
python3 -m venv flask-metrics-venv
source flask-metrics-venv/bin/activate

# 2. 安装依赖
pip install flask prometheus-client

# 3. 启动服务
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

## 项目结构

```
├── flask-metrics-venv/   # Python 虚拟环境
├── app.py                # Flask 应用主程序
├── quicksort.py          # 快速排序脚本
├── test.txt              # 测试文件
└── README.md
```

## 依赖

- Python ≥ 3.10
- Flask 3.1
- prometheus-client 0.25
