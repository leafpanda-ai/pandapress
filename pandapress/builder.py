"""PandaPress 构建引擎."""
import os
import shutil
from pathlib import Path

from .template import render_page, render_index, load_theme, load_theme_static_dir, list_posts


def build(input_dir: str, output_dir: str, theme_name: str = "default") -> int:
    """Build static site.

    Returns the number of posts built.
    """
    src = Path(input_dir)
    dst = Path(output_dir)

    if dst.exists():
        shutil.rmtree(dst)

    # Load theme
    theme = load_theme(theme_name)

    # Copy static assets
    static_dir = load_theme_static_dir(theme_name)
    if static_dir is not None and static_dir.exists():
        dst_static = dst / "static"
        if dst_static.exists():
            shutil.rmtree(dst_static)
        shutil.copytree(static_dir, dst_static)

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
    return count
