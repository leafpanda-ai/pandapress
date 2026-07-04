"""PandaPress 模板引擎."""
import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict


def list_posts(src: Path) -> List[Dict]:
    posts = []
    for f in sorted(src.glob("*.md"), reverse=True):
        text = f.read_text(encoding="utf-8")
        meta = parse_front_matter(text)
        content = strip_front_matter(text)
        posts.append({
            "title": meta.get("title", f.stem),
            "date": meta.get("date", ""),
            "slug": f.stem,
            "content": markdown_to_html(content),
            "excerpt": markdown_to_html(content[:200] + "..." if len(content) > 200 else content),
        })
    return posts


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


def markdown_to_html(md: str) -> str:
    """极简 Markdown 转 HTML（不依赖外部库）."""
    lines = md.split("\n")
    html = []
    in_list = False
    for line in lines:
        # Headers
        if line.startswith("### "):
            html.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("## "):
            html.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            html.append(f"<h1>{line[2:]}</h1>")
        # List items
        elif line.startswith("- ") or line.startswith("* "):
            if not in_list:
                html.append("<ul>")
                in_list = True
            html.append(f"<li>{line[2:]}</li>")
        elif line.startswith("1. "):
            if not in_list:
                html.append("<ol>")
                in_list = True
            html.append(f"<li>{line[3:]}</li>")
        # Code block
        elif line.startswith("```"):
            html.append("<pre><code>")
        # Empty line
        elif line.strip() == "":
            if in_list:
                html.append("</ul>" if in_list else "</ol>")
                in_list = False
        # Paragraph
        else:
            html.append(f"<p>{line}</p>")
    if in_list:
        html.append("</ul>")
    return "\n".join(html)


def render_page(post: Dict, theme: Dict) -> str:
    tpl = theme.get("post", """<!DOCTYPE html>
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
</html>""")
    return tpl.format(**post)


def render_index(posts: List[Dict], theme: Dict) -> str:
    items = "\n".join(
        f'<li><a href="/{p["slug"]}/">{p["title"]}</a> <time>{p["date"]}</time><p>{p.get("excerpt", "")}</p></li>'
        for p in posts
    )
    tpl = theme.get("index", """<!DOCTYPE html>
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
</html>""")
    return tpl.replace("{items}", items)


def load_theme() -> Dict:
    return {}


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
