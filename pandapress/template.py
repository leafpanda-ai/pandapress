"""PandaPress 模板引擎."""
import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


def list_posts(src: Path) -> List[Dict]:
    posts = []
    for f in sorted(src.glob("*.md"), reverse=True):
        text = f.read_text(encoding="utf-8")
        meta = parse_front_matter(text)
        content = strip_front_matter(text)
        html_content = markdown_to_html(content)
        posts.append({
            "title": meta.get("title", f.stem),
            "date": meta.get("date", ""),
            "slug": f.stem,
            "content": html_content,
            "excerpt": excerpt(html_content),
        })
    return posts


def excerpt(html: str, length: int = 200) -> str:
    """Strip HTML tags and truncate to approximate plain-text length."""
    plain = re.sub(r"<[^>]+>", "", html).strip()
    if len(plain) <= length:
        return plain
    return plain[:length].rsplit(" ", 1)[0] + "..."


def parse_front_matter(text: str) -> Dict:
    meta = {}
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
    return meta


def strip_front_matter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return text


# ── Inline formatting ──────────────────────────────────────────────

_INLINE_RE = re.compile(
    r"(!\[(?P<alt>[^\]]*)\]\((?P<img_url>[^)]+)\))"    # ![alt](url)
    r"|(\[(?P<link_text>[^\]]*)\]\((?P<link_url>[^)]+)\))"  # [text](url)
    r"|(`(?P<code>[^`]+)`)"                                   # `code`
    r"|(\*\*(?P<bold>[^*]+)\*\*)"                            # **bold**
    r"|(\*(?P<italic>[^*]+)\*)"                              # *italic*
)


def _replace_inline(m: re.Match) -> str:
    if m.group("img_url"):
        alt = m.group("alt") or ""
        return f'<img src="{m.group("img_url")}" alt="{alt}">'
    if m.group("link_url"):
        text = m.group("link_text")
        return f'<a href="{m.group("link_url")}">{text}</a>'
    if m.group("code"):
        return f"<code>{m.group('code')}</code>"
    if m.group("bold"):
        return f"<strong>{m.group('bold')}</strong>"
    if m.group("italic"):
        return f"<em>{m.group('italic')}</em>"
    return m.group(0)


def inline_format(text: str) -> str:
    """Apply inline Markdown formatting to a line of text."""
    return _INLINE_RE.sub(_replace_inline, text)


# ── Block-level Markdown → HTML ────────────────────────────────────

def markdown_to_html(md: str) -> str:
    """Convert Markdown to HTML (zero external dependencies)."""
    lines = md.split("\n")
    out: List[str] = []
    in_code_block = False
    in_ul = False
    in_ol = False
    i = 0
    n = len(lines)

    def close_list():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    def close_para():
        if out and out[-1] == "</p>":
            pass  # already closed

    while i < n:
        line = lines[i]

        # ── Code block ──
        if line.startswith("```"):
            close_list()
            if not in_code_block:
                in_code_block = True
                lang = line[3:].strip()
                if lang:
                    out.append(f'<pre><code class="language-{lang}">')
                else:
                    out.append("<pre><code>")
            else:
                in_code_block = False
                out.append("</code></pre>")
            i += 1
            continue

        if in_code_block:
            # Escape HTML inside code blocks
            out.append(_escape_html(line))
            i += 1
            continue

        # ── Empty line ──
        if line.strip() == "":
            close_list()
            i += 1
            continue

        # ── Headers ──
        h_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if h_match:
            close_list()
            level = len(h_match.group(1))
            text = inline_format(h_match.group(2))
            out.append(f"<h{level}>{text}</h{level}>")
            i += 1
            continue

        # ── Horizontal rule ──
        if re.match(r"^[-*_]{3,}\s*$", line):
            close_list()
            out.append("<hr>")
            i += 1
            continue

        # ── Unordered list ──
        ul_match = re.match(r"^[-*+]\s+(.+)$", line)
        if ul_match:
            if not in_ul:
                close_list()
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline_format(ul_match.group(1))}</li>")
            i += 1
            continue

        # ── Ordered list ──
        ol_match = re.match(r"^\d+\.\s+(.+)$", line)
        if ol_match:
            if not in_ol:
                close_list()
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{inline_format(ol_match.group(1))}</li>")
            i += 1
            continue

        # ── Paragraph (with hard break support) ──
        close_list()
        # Collect consecutive non-empty lines into one paragraph
        para_lines = []
        while i < n:
            l = lines[i]
            if l.strip() == "" or l.startswith("#") or l.startswith("```") or re.match(r"^[-*+]\s", l) or re.match(r"^\d+\.\s", l) or re.match(r"^[-*_]{3,}\s*$", l):
                break
            para_lines.append(l)
            i += 1
        if para_lines:
            para_text = "<br>\n".join(inline_format(l) for l in para_lines if l.strip())
            if para_text:
                out.append(f"<p>{para_text}</p>")
        continue

    close_list()
    if in_code_block:
        out.append("</code></pre>")  # unclosed code block

    return "\n".join(out)


def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ── Theme loading ──────────────────────────────────────────────────

_THEME_DIR = Path(__file__).parent / "themes"

_DEFAULT_POST_TPL = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} - PandaPress</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <nav><a href="/">← Home</a></nav>
  <article>
    <h1>{title}</h1>
    <time>{date}</time>
    <div class="content">{content}</div>
  </article>
</body>
</html>"""

_DEFAULT_INDEX_TPL = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PandaPress</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <header>
    <h1>🐼 PandaPress</h1>
    <p>极简 Markdown 静态博客</p>
  </header>
  <main>
    <ul>{items}</ul>
  </main>
</body>
</html>"""


def load_theme(name: str = "default") -> Dict:
    """Load theme templates from themes/{name}/.

    Falls back to built-in defaults when template files are missing.
    """
    theme_dir = _THEME_DIR / name
    result: Dict = {}

    post_path = theme_dir / "post.html"
    if post_path.exists():
        result["post"] = post_path.read_text(encoding="utf-8")
    else:
        result["post"] = _DEFAULT_POST_TPL

    index_path = theme_dir / "index.html"
    if index_path.exists():
        result["index"] = index_path.read_text(encoding="utf-8")
    else:
        result["index"] = _DEFAULT_INDEX_TPL

    return result


def load_theme_static_dir(name: str = "default") -> Optional[Path]:
    """Return path to theme static directory if it exists."""
    static_dir = _THEME_DIR / name / "static"
    return static_dir if static_dir.is_dir() else None


# ── Rendering ──────────────────────────────────────────────────────

def render_page(post: Dict, theme: Dict) -> str:
    tpl = theme.get("post", _DEFAULT_POST_TPL)
    return tpl.format(**post)


def render_index(posts: List[Dict], theme: Dict) -> str:
    items = "\n".join(
        f'<li><a href="/{p["slug"]}/">{p["title"]}</a> <time>{p["date"]}</time><p>{p.get("excerpt", "")}</p></li>'
        for p in posts
    )
    tpl = theme.get("index", _DEFAULT_INDEX_TPL)
    return tpl.replace("{items}", items)


# ── New post ───────────────────────────────────────────────────────

def new_post(title: str):
    slug = title.lower().replace(" ", "-")
    date = datetime.now().strftime("%Y-%m-%d")
    content = f"""---
title: {title}
date: {date}
---

# {title}

开始写作...
"""
    path = Path(f"{slug}.md")
    path.write_text(content, encoding="utf-8")
    print(f"Created {path}")
