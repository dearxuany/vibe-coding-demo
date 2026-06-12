#!/usr/bin/env python3
"""Flask web service exposing Prometheus-compatible metrics at /metrics."""

from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    flash,
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CollectorRegistry,
    multiprocess,
    GC_COLLECTOR,
    PLATFORM_COLLECTOR,
    PROCESS_COLLECTOR,
)
import mistune
import json
import shutil
import time
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# --- Flask-Login setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "请先登录后再访问此页面。"


class User(UserMixin):
    """Simple user class for Flask-Login."""

    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username


# User store (credentials via env vars, with dev defaults)
_DEFAULT_USER = os.environ.get("DOCS_USER", "admin")
_DEFAULT_PASS = os.environ.get("DOCS_PASS", "password123")
_USERS = {_DEFAULT_USER: {"password": _DEFAULT_PASS, "id": "1"}}


@login_manager.user_loader
def load_user(user_id):
    for username, data in _USERS.items():
        if data["id"] == user_id:
            return User(user_id=user_id, username=username)
    return None


# --- Markdown renderer (mistune 3.x) ---
_markdown = mistune.create_markdown(
    plugins=["strikethrough", "footnotes", "table", "task_lists"],
)

# --- Docs directory ---
DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
os.makedirs(DOCS_DIR, exist_ok=True)
TAGS_FILE = os.path.join(DOCS_DIR, ".tags.json")


def _load_tags():
    """Load file→tags mapping from .tags.json."""
    if os.path.isfile(TAGS_FILE):
        try:
            with open(TAGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_tags(tags: dict):
    """Save file→tags mapping to .tags.json."""
    with open(TAGS_FILE, "w", encoding="utf-8") as f:
        json.dump(tags, f, ensure_ascii=False, indent=2)


def _all_tags():
    """Return sorted list of all unique tags."""
    tags = _load_tags()
    all_t = set()
    for tlist in tags.values():
        for t in tlist:
            all_t.add(t)
    return sorted(all_t)


def _scan_docs(base_dir, rel_prefix=""):
    """Recursively scan for .md files under base_dir. Returns list of doc dicts."""
    docs = []
    try:
        for name in sorted(os.listdir(base_dir)):
            full = os.path.join(base_dir, name)
            rel = os.path.join(rel_prefix, name) if rel_prefix else name
            if os.path.isdir(full):
                docs.extend(_scan_docs(full, rel))
            elif name.endswith(".md"):
                title = name
                try:
                    with open(full, "r", encoding="utf-8") as f:
                        first_line = f.readline().lstrip("#").strip()
                        if first_line:
                            title = first_line
                except Exception:
                    pass
                mtime = datetime.fromtimestamp(os.path.getmtime(full)).strftime(
                    "%Y-%m-%d %H:%M"
                )
                docs.append({
                    "filename": rel,
                    "display": _strip_md(rel),
                    "title": title,
                    "mtime": mtime,
                    "dirname": rel_prefix or "",
                })
    except FileNotFoundError:
        pass
    return docs


def _get_doc_path(filename):
    """Resolve a filename to its absolute path under DOCS_DIR (safe join)."""
    safe = os.path.normpath(filename)
    if safe.startswith("/") or ".." in safe.split(os.sep):
        return None
    return os.path.join(DOCS_DIR, safe)


def _strip_md(filename: str) -> str:
    """Strip .md suffix from display name."""
    if filename.endswith(".md"):
        return filename[:-3]
    return filename


def _render_markdown(raw: str) -> str:
    """Render raw markdown text to HTML using mistune."""
    return _markdown(raw) or ""


# Create a dedicated registry so built-in process metrics are included
registry = CollectorRegistry(auto_describe=True)

# Register built-in collectors for process/GC/platform metrics
registry.register(PROCESS_COLLECTOR)
registry.register(PLATFORM_COLLECTOR)
registry.register(GC_COLLECTOR)

# Custom metrics
REQUEST_COUNT = Counter(
    "flask_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
    registry=registry,
)

REQUEST_LATENCY = Histogram(
    "flask_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
    registry=registry,
)

IN_FLIGHT = Gauge(
    "flask_http_requests_in_flight",
    "Currently in-flight HTTP requests",
    registry=registry,
)


@app.before_request
def before_request():
    request._start_time = time.time()
    IN_FLIGHT.inc()


@app.after_request
def after_request(response):
    IN_FLIGHT.dec()
    latency = time.time() - request._start_time
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint or request.path,
        status=response.status_code,
    ).inc()
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.endpoint or request.path,
    ).observe(latency)
    return response


@app.route("/")
def index():
    return jsonify({
        "service": "flask-metrics-demo",
        "endpoints": {
            "/": "this info",
            "/metrics": "Prometheus metrics",
            "/health": "health check",
            "/api/hello": "sample API endpoint",
        },
    })


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/api/hello")
def hello():
    name = request.args.get("name", "world")
    return jsonify({"message": f"Hello, {name}!"})


@app.route("/metrics")
def metrics():
    """Expose metrics in Prometheus text format."""
    return generate_latest(registry), 200, {"Content-Type": "text/plain; charset=utf-8"}


# --- Markdown docs routes ---


@app.route("/docs")
def docs_index():
    """Document list with optional preview pane, tag filter, and tree view."""
    tag_filter = request.args.get("tag", "").strip()
    subdir = request.args.get("dir", "").strip()

    # Determine base scan directory
    if subdir:
        scan_dir = os.path.join(DOCS_DIR, subdir)
        if not os.path.isdir(scan_dir) or _get_doc_path(subdir) is None:
            scan_dir = DOCS_DIR
            subdir = ""
    else:
        scan_dir = DOCS_DIR

    all_docs = _scan_docs(scan_dir, subdir)
    tags_data = _load_tags()
    all_tags = _all_tags()

    # Filter by tag
    if tag_filter:
        all_docs = [d for d in all_docs if tag_filter in tags_data.get(d["filename"], [])]

    # Build directory tree for sidebar
    dirs = []
    try:
        for name in sorted(os.listdir(scan_dir)):
            full = os.path.join(scan_dir, name)
            rel = os.path.join(subdir, name) if subdir else name
            if os.path.isdir(full):
                md_count = sum(
                    1 for f in os.listdir(full)
                    if f.endswith(".md")
                )
                dirs.append({"name": name, "rel": rel, "count": md_count})
    except FileNotFoundError:
        pass

    # Optional preview
    preview_file = request.args.get("file", "")
    preview_html = None
    preview_title = None
    preview_mtime = None
    preview_tags = []
    if preview_file:
        if not preview_file.endswith(".md"):
            preview_file = preview_file + ".md"
        fpath = _get_doc_path(preview_file)
        if fpath and os.path.isfile(fpath):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    raw = f.read()
                preview_html = _render_markdown(raw)
                preview_title = _strip_md(preview_file)
                if raw.startswith("# "):
                    preview_title = raw.split("\n")[0].lstrip("#").strip()
                preview_mtime = datetime.fromtimestamp(
                    os.path.getmtime(fpath)
                ).strftime("%Y-%m-%d %H:%M")
                preview_tags = tags_data.get(preview_file, [])
            except Exception:
                preview_html = "<p class='text-danger'>读取文档失败</p>"

    return render_template(
        "index.html",
        docs=all_docs,
        dirs=dirs,
        all_tags=all_tags,
        current_tag=tag_filter,
        current_dir=subdir,
        preview_file=preview_file or "",
        preview_html=preview_html,
        preview_title=preview_title,
        preview_mtime=preview_mtime,
        preview_tags=preview_tags,
        tags_data=tags_data,
    )


@app.route("/docs/new", methods=["GET", "POST"])
@login_required
def doc_new():
    """Create a new Markdown document (supports subdirectories)."""
    subdir = request.args.get("dir", "").strip()
    if request.method == "POST":
        filename = request.form.get("filename", "").strip()
        if not filename:
            flash("文件名不能为空。", "error")
            return render_template("doc_new.html", subdir=subdir)
        if not filename.endswith(".md"):
            filename = filename + ".md"
        # Prefix subdir if given
        if subdir:
            filename = os.path.join(subdir, filename)
        fpath = _get_doc_path(filename)
        if fpath is None:
            flash("无效的文件名。", "error")
            return render_template("doc_new.html", subdir=subdir)
        if os.path.exists(fpath):
            flash("该文件已存在，请使用其他名称。", "error")
            return render_template("doc_new.html", subdir=subdir)
        content = request.form.get("content", "")
        try:
            os.makedirs(os.path.dirname(fpath), exist_ok=True)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            # Handle tags
            tags_str = request.form.get("tags", "").strip()
            if tags_str:
                tags_data = _load_tags()
                tags_data[filename] = [t.strip() for t in tags_str.split(",") if t.strip()]
                _save_tags(tags_data)
            flash("文档创建成功！", "success")
            return redirect(url_for("doc_view", filename=filename))
        except Exception as e:
            flash(f"创建失败：{e}", "error")
    return render_template("doc_new.html", subdir=subdir)


@app.route("/docs/mkdir", methods=["POST"])
@login_required
def doc_mkdir():
    """Create a new subdirectory under docs/."""
    dirname = request.form.get("dirname", "").strip()
    parent = request.form.get("parent", "").strip()
    if not dirname:
        flash("目录名不能为空。", "error")
        return redirect(url_for("docs_index"))
    # Sanitize
    safe = os.path.normpath(dirname)
    if safe.startswith("/") or ".." in safe.split(os.sep):
        flash("无效的目录名。", "error")
        return redirect(url_for("docs_index"))
    if parent:
        parent_safe = os.path.normpath(parent)
        if parent_safe.startswith("/") or ".." in parent_safe.split(os.sep):
            flash("无效的父目录。", "error")
            return redirect(url_for("docs_index"))
        target = os.path.join(DOCS_DIR, parent_safe, safe)
    else:
        target = os.path.join(DOCS_DIR, safe)
    try:
        os.makedirs(target, exist_ok=True)
        flash(f"目录 '{dirname}' 创建成功！", "success")
    except Exception as e:
        flash(f"创建目录失败：{e}", "error")
    redirect_dir = parent if parent else ""
    return redirect(url_for("docs_index", dir=redirect_dir))


@app.route("/docs/_api/dirs")
def api_dirs():
    """Return JSON list of all subdirectories under docs/ for move target preview."""
    dirs = []
    for root, subdirs, _files in os.walk(DOCS_DIR):
        rel = os.path.relpath(root, DOCS_DIR)
        if rel == ".":
            rel = ""
        dirs.append({"path": rel, "name": os.path.basename(root) or "(根目录)"})
    dirs.sort(key=lambda d: d["path"])
    return jsonify(dirs)


@app.route("/docs/<path:filename>/move", methods=["POST"])
@login_required
def doc_move(filename):
    """Move/rename a Markdown document or directory."""
    if not filename.endswith(".md"):
        filename = filename + ".md"
    fpath = _get_doc_path(filename)
    if fpath is None or not os.path.exists(fpath):
        flash("源文件不存在。", "error")
        return redirect(url_for("docs_index"))

    new_name = request.form.get("new_name", "").strip()
    if not new_name:
        flash("新文件名不能为空。", "error")
        return redirect(url_for("docs_index"))
    if not new_name.endswith(".md"):
        new_name = new_name + ".md"

    new_path = _get_doc_path(new_name)
    if new_path is None:
        flash("无效的目标路径。", "error")
        return redirect(url_for("docs_index"))
    if os.path.exists(new_path):
        flash("目标文件已存在。", "error")
        return redirect(url_for("docs_index"))

    try:
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.move(fpath, new_path)
        # Update tags
        tags_data = _load_tags()
        if filename in tags_data:
            tags_data[new_name] = tags_data.pop(filename)
            _save_tags(tags_data)
        flash("文件移动成功！", "success")
        return redirect(url_for("docs_index"))
    except Exception as e:
        flash(f"移动失败：{e}", "error")
        return redirect(url_for("docs_index"))


@app.route("/docs/<path:filename>/tags", methods=["POST"])
@login_required
def doc_tags(filename):
    """Update tags for a document."""
    if not filename.endswith(".md"):
        filename = filename + ".md"
    fpath = _get_doc_path(filename)
    if fpath is None or not os.path.isfile(fpath):
        flash("文件不存在。", "error")
        return redirect(url_for("docs_index"))

    tags_str = request.form.get("tags", "").strip()
    tags_data = _load_tags()
    if tags_str:
        tags_data[filename] = [t.strip() for t in tags_str.split(",") if t.strip()]
    else:
        tags_data.pop(filename, None)
    _save_tags(tags_data)
    flash("标签更新成功！", "success")
    return redirect(url_for("docs_index", file=filename))


@app.route("/docs/<path:filename>/delete", methods=["POST"])
@login_required
def doc_delete(filename):
    """Delete a Markdown document."""
    if not filename.endswith(".md"):
        filename = filename + ".md"
    fpath = _get_doc_path(filename)
    if fpath is None or not os.path.isfile(fpath):
        flash("文件不存在。", "error")
        return redirect(url_for("docs_index"))
    try:
        os.remove(fpath)
        # Remove tags
        tags_data = _load_tags()
        tags_data.pop(filename, None)
        _save_tags(tags_data)
        flash("文档已删除。", "success")
    except Exception as e:
        flash(f"删除失败：{e}", "error")
    return redirect(url_for("docs_index"))


@app.route("/docs/<path:filename>")
def doc_view(filename):
    """Render a Markdown document as HTML."""
    if not filename.endswith(".md"):
        filename = filename + ".md"
    fpath = _get_doc_path(filename)
    if fpath is None or not os.path.isfile(fpath):
        return render_template("base.html", content="<h1>404 - 文档未找到</h1>"), 404
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception:
        return render_template("base.html", content="<h1>500 - 读取文档失败</h1>"), 500
    html = _render_markdown(raw)
    mtime = datetime.fromtimestamp(os.path.getmtime(fpath)).strftime("%Y-%m-%d %H:%M")
    title = _strip_md(filename)
    if raw.startswith("# "):
        title = raw.split("\n")[0].lstrip("#").strip()
    display_name = _strip_md(filename)
    return render_template(
        "doc_view.html",
        display_name=display_name,
        title=title,
        filename=filename,
        content=html,
        mtime=mtime,
    )


@app.route("/docs/<path:filename>/edit", methods=["GET", "POST"])
@login_required
def doc_edit(filename):
    """Edit a Markdown document (login required)."""
    if not filename.endswith(".md"):
        filename = filename + ".md"
    fpath = _get_doc_path(filename)
    if fpath is None:
        return render_template("base.html", content="<h1>400 - 无效的文件名</h1>"), 400

    if request.method == "POST":
        content = request.form.get("content", "")
        try:
            os.makedirs(os.path.dirname(fpath), exist_ok=True)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            flash("文档保存成功！", "success")
            return redirect(url_for("doc_view", filename=filename))
        except Exception as e:
            flash(f"保存失败：{e}", "error")

    content = ""
    if os.path.isfile(fpath):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            flash("读取文档失败", "error")

    # Load current tags
    tags_data = _load_tags()
    tags_str = ", ".join(tags_data.get(filename, []))

    return render_template(
        "doc_edit.html", filename=filename, content=content, tags_str=tags_str, display_name=_strip_md(filename)
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for("docs_index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user_data = _USERS.get(username)
        if user_data and user_data["password"] == password:
            user = User(user_id=user_data["id"], username=username)
            login_user(user)
            flash("登录成功！", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("docs_index"))
        flash("用户名或密码错误。", "error")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Logout."""
    logout_user()
    flash("已成功登出。", "success")
    return redirect(url_for("docs_index"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
