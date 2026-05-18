import os


def get_directory_tree(path):
    """递归构建目录树结构"""
    tree = {}
    for root, dirs, files in os.walk(path):
        files = [f for f in files if not f[0] in ('.', '_')]
        dirs[:] = [d for d in dirs if not d[0] in ('.', '_')]
        rel_path = os.path.relpath(root, path)
        if rel_path == '.':
            current_dict = tree
        else:
            parts = rel_path.split(os.sep)
            current_dict = tree
            for part in parts:
                if part not in current_dict:
                    current_dict[part] = {}
                current_dict = current_dict[part]

        if 'files' not in current_dict:
            current_dict['files'] = files
        else:
            current_dict['files'].extend(files)

    def clean_tree(t):
        if isinstance(t, dict):
            for k, v in list(t.items()):
                if isinstance(v, dict):
                    clean_tree(v)
                elif k == 'files' and not v:
                    del t[k]
        return t

    return clean_tree(tree)


def escape_html(text):
    """转义 HTML 特殊字符"""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def render_tree(tree, base_path=".", depth=0):
    """
    递归渲染可折叠的目录树 HTML。
    每个目录项渲染为一个 <li>，包含：
      - 一个 <button>（展开/折叠按钮 + 文件夹图标 + 目录链接）
      - 一个 <ul> 子列表（包含子目录和文件）
    文件项直接渲染为 <li><a>。
    """
    html_parts = []

    # 分离子目录和文件
    directories = {k: v for k, v in tree.items() if isinstance(v, dict)}
    files = tree.get("files", [])

    # 1. 渲染每个子目录（带展开/折叠按钮）
    for idx, (name, sub_tree) in enumerate(directories.items()):
        child_id = "tree-{}-{}-{}".format(depth, idx, hash(name) & 0xFFFFFFFF)
        child_content = render_tree(sub_tree, os.path.join(base_path, name), depth + 1)
        safe_name = escape_html(name)

        html_parts.append(
            '<li class="tree-node">'
            '<button class="dir-toggle" aria-expanded="false" '
            'data-target="' + child_id + '">'
            '<span class="toggle-arrow">&#9654;</span>'
            '<span class="dir-icon">&#128193;</span>'
            '<span class="dir-name">'
            '<a href="' + escape_html(os.path.join(base_path, name)) + '">' + safe_name + '</a>'
            '</span>'
            '</button>'
            '<ul class="sub-tree collapsed" id="' + child_id + '">'
            + child_content
            + '</ul>'
            '</li>'
        )

    # 2. 渲染文件列表
    for fname in files:
        href = escape_html(os.path.join(base_path, fname))
        safe_fname = escape_html(fname)
        html_parts.append(
            '<li class="tree-node file-node">'
            '<a class="file-link" href="' + href + '">'
            '<span class="file-icon">&#128196;</span>'
            + safe_fname
            + '</a>'
            '</li>'
        )

    return '\n'.join(html_parts)


def main():
    current_directory = os.getcwd()
    directory_tree = get_directory_tree(current_directory)

    tree_html = render_tree(directory_tree)

    # 注意：这里用字符串拼接而非 f-string，避免 JS 中的 {} 与 Python f-string 冲突
    html_head = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Directory Tree</title>
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                     "Helvetica Neue", Arial, "Noto Sans SC", sans-serif;
        background: #1e1e2e;
        color: #cdd6f4;
        padding: 24px 40px;
        line-height: 1.6;
    }
    h1 {
        margin-bottom: 16px;
        font-size: 22px;
        color: #89b4fa;
    }

    /* 根列表 */
    ul.tree { list-style: none; padding-left: 0; }

    /* 每个节点的子列表 */
    .sub-tree {
        list-style: none;
        padding-left: 22px;
        border-left: 1px solid #45475a;
        margin-left: 9px;
        overflow: hidden;
        transition: max-height 0.25s ease, opacity 0.25s ease;
    }

    .tree-node { margin: 2px 0; }

    /* ---- 目录切换按钮 ---- */
    .dir-toggle {
        display: inline-flex;
        align-items: center;
        background: none;
        border: none;
        color: inherit;
        cursor: pointer;
        padding: 3px 6px;
        border-radius: 4px;
        font-size: 14px;
        font-family: inherit;
        transition: background 0.15s;
    }
    .dir-toggle:hover { background: #313244; }

    .toggle-arrow {
        display: inline-block;
        width: 14px;
        font-size: 10px;
        text-align: center;
        transition: transform 0.2s;
    }
    .dir-toggle[aria-expanded="true"] .toggle-arrow { transform: rotate(90deg); }

    .dir-icon, .file-icon { margin-right: 5px; }

    .dir-name a {
        color: #89b4fa;
        text-decoration: none;
        font-weight: 500;
    }
    .dir-name a:hover { text-decoration: underline; }

    /* 折叠时隐藏子菜单 */
    .sub-tree.collapsed {
        max-height: 0 !important;
        opacity: 0;
        border-left-color: transparent;
    }
    .sub-tree.expanded {
        max-height: 10000px;
        opacity: 1;
    }

    /* 文件链接 */
    .file-link {
        display: inline-flex;
        align-items: center;
        padding: 3px 8px;
        border-radius: 4px;
        color: #a6adc8;
        text-decoration: none;
        font-size: 14px;
    }
    .file-link:hover {
        background: #313244;
        text-decoration: none;
        color: #b4befe;
    }
</style>
<script>
    // 点击按钮展开/折叠
    document.addEventListener("click", function (e) {
        const btn = e.target.closest(".dir-toggle");
        if (!btn) return;

        const targetId = btn.getAttribute("data-target");
        const sub = document.getElementById(targetId);
        if (!sub) return;

        const isExpanded = btn.getAttribute("aria-expanded") === "true";
        btn.setAttribute("aria-expanded", isExpanded ? "false" : "true");

        if (isExpanded) {
            sub.classList.remove("expanded");
            sub.classList.add("collapsed");
        } else {
            sub.classList.remove("collapsed");
            sub.classList.add("expanded");
        }
    });

    // 页面加载后默认全部折叠
    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".sub-tree").forEach(function (ul) {
            ul.classList.add("collapsed");
        });
    });
</script>
</head>
<body>
    <h1>📂 Directory Tree</h1>
    <ul class="tree">
"""

    html_tail = """
    </ul>
</body>
</html>"""

    html_content = html_head + tree_html + html_tail

    output_file = "directory_tree.html"
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(html_content)

    print("Directory tree has been saved to '{}'.".format(output_file))


if __name__ == "__main__":
    main()
