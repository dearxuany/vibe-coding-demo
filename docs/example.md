# 示例文档

欢迎使用 Markdown 文档系统！这是一个示例文档，展示了系统支持的 Markdown 功能。

## 功能列表

- 📄 **文档展示**：支持将 Markdown 渲染为美观的 HTML 页面
- ✏️ **在线编辑**：登录后可直接编辑 Markdown 文档
- 🔐 **用户认证**：通过登录保护编辑功能
- 💡 **代码高亮**：自动高亮代码块

## 代码示例

下面是一段 Python 快速排序代码：

```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

print(quicksort([3, 6, 8, 10, 1, 2, 1]))
```

## 数据表格

| 功能 | 状态 | 说明 |
|------|------|------|
| 文档展示 | ✅ 完成 | 支持 Markdown → HTML |
| 文档编辑 | ✅ 完成 | 登录后可编辑保存 |
| 用户认证 | ✅ 完成 | Flask-Login 实现 |
| 代码高亮 | ✅ 完成 | highlight.js |
| 响应式布局 | ✅ 完成 | Bootstrap 5 |

## 扩展语法

这个系统还支持一些扩展语法：

- 删除线：~~这段文字被删除了~~
- 脚注引用[^1]

[^1]: 这是一个脚注示例。

---

> 提示：登录后点击页面上的「编辑」按钮即可修改文档内容。
