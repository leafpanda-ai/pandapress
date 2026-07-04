"""PandaPress 构建引擎."""
import os
import shutil
from pathlib import Path
from datetime import datetime

from .template import render_page, render_index, load_theme, list_posts


def build(input_dir: str, output_dir: str):
    src = Path(input_dir)
    dst = Path(output_dir)

    if dst.exists():
        shutil.rmtree(dst)

    # Copy static assets
    theme = load_theme()
    theme_dir = Path(__file__).parent / "themes" / "default"
    if theme_dir.exists():
        shutil.copytree(theme_dir / "static", dst / "static", dirs_exist_ok=True)

    # Scan markdown posts
    posts = list_posts(src)
    for post in posts:
        html = render_page(post, theme)
        out_path = dst / post["slug"]
        os.makedirs(out_path, exist_ok=True)
        (out_path / "index.html").write_text(html, encoding="utf-8")

    # Build index
    index_html = render_index(posts, theme)
    (dst / "index.html").write_text(index_html, encoding="utf-8")

    count = len(posts)
    print(f"PandaPress: built {count} post{'s' if count != 1 else ''} -> {output_dir}/")
