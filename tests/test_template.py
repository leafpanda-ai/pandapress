"""Tests for the Markdown-to-HTML renderer in pandapress/template.py."""
import pytest
from pandapress.template import (
    markdown_to_html,
    parse_front_matter,
    strip_front_matter,
    inline_format,
    excerpt,
)


# ── Headers ──────────────────────────────────────────────────────────

class TestHeaders:
    def test_h1(self):
        html = markdown_to_html("# Hello")
        assert "<h1>Hello</h1>" in html

    def test_h2(self):
        html = markdown_to_html("## Subtitle")
        assert "<h2>Subtitle</h2>" in html

    def test_h3(self):
        html = markdown_to_html("### Section")
        assert "<h3>Section</h3>" in html

    def test_h4(self):
        html = markdown_to_html("#### Sub-section")
        assert "<h4>Sub-section</h4>" in html

    def test_h5(self):
        html = markdown_to_html("##### Deep")
        assert "<h5>Deep</h5>" in html

    def test_h6(self):
        html = markdown_to_html("###### Deepest")
        assert "<h6>Deepest</h6>" in html

    def test_header_with_inline_formatting(self):
        html = markdown_to_html("# **Bold** and *italic* title")
        assert "<h1><strong>Bold</strong> and <em>italic</em> title</h1>" in html

    def test_header_no_space_after_hash_is_not_header(self):
        # Must have a space after #
        html = markdown_to_html("#NotHeader")
        assert "<h1>" not in html

    def test_multiple_headers(self):
        md = "# Title\n\n## Section 1\n\n### Subsection"
        html = markdown_to_html(md)
        assert "<h1>Title</h1>" in html
        assert "<h2>Section 1</h2>" in html
        assert "<h3>Subsection</h3>" in html


# ── Bold ─────────────────────────────────────────────────────────────

class TestBold:
    def test_bold_in_paragraph(self):
        html = markdown_to_html("This is **bold** text.")
        assert "<strong>bold</strong>" in html

    def test_bold_multiple(self):
        html = markdown_to_html("**first** and **second**")
        assert html.count("<strong>") == 2

    def test_bold_with_punctuation(self):
        html = markdown_to_html("**bold!**")
        assert "<strong>bold!</strong>" in html


# ── Italic ───────────────────────────────────────────────────────────

class TestItalic:
    def test_italic_in_paragraph(self):
        html = markdown_to_html("This is *italic* text.")
        assert "<em>italic</em>" in html

    def test_italic_multiple(self):
        html = markdown_to_html("*first* and *second*")
        assert html.count("<em>") == 2

    def test_italic_with_punctuation(self):
        html = markdown_to_html("*italics!*")
        assert "<em>italics!</em>" in html


# ── Inline Code ──────────────────────────────────────────────────────

class TestInlineCode:
    def test_inline_code(self):
        html = markdown_to_html("Use the `print()` function.")
        assert "<code>print()</code>" in html

    def test_inline_code_multiple(self):
        html = markdown_to_html("`foo` and `bar`")
        assert html.count("<code>") == 2

    def test_inline_code_with_special_chars(self):
        html = markdown_to_html("`a < b` is true")
        assert "<code>a &lt; b</code>" in html or "<code>a < b</code>" in html


# ── Links ────────────────────────────────────────────────────────────

class TestLinks:
    def test_basic_link(self):
        html = markdown_to_html("[Click here](https://example.com)")
        assert '<a href="https://example.com">Click here</a>' in html

    def test_link_in_paragraph(self):
        html = markdown_to_html("Visit [PandaPress](https://pandapress.dev) today.")
        assert '<a href="https://pandapress.dev">PandaPress</a>' in html

    def test_link_with_title(self):
        html = inline_format('[text](url "Title")')
        assert '<a href="url " title' in html or '<a href="url' in html


# ── Images ───────────────────────────────────────────────────────────

class TestImages:
    def test_basic_image(self):
        html = markdown_to_html("![alt text](image.png)")
        assert '<img src="image.png" alt="alt text">' in html

    def test_image_in_paragraph(self):
        html = markdown_to_html("Look at ![this](img.jpg) here.")
        assert '<img src="img.jpg" alt="this">' in html

    def test_image_empty_alt(self):
        html = markdown_to_html("![](icon.png)")
        assert '<img src="icon.png" alt="">' in html


# ── Code Blocks ──────────────────────────────────────────────────────

class TestCodeBlocks:
    def test_code_block_no_lang(self):
        md = "```\nprint('hello')\n```"
        html = markdown_to_html(md)
        assert "<pre><code>" in html
        assert "print('hello')" in html
        assert "</code></pre>" in html

    def test_code_block_with_language(self):
        md = "```python\nprint('hello')\n```"
        html = markdown_to_html(md)
        assert '<pre><code class="language-python">' in html
        assert "print('hello')" in html
        assert "</code></pre>" in html

    def test_code_block_html_escaped(self):
        md = "```\n<div>tag</div>\n```"
        html = markdown_to_html(md)
        assert "&lt;div&gt;" in html
        assert "<div>" not in html

    def test_code_block_multi_line(self):
        md = "```\nline1\nline2\nline3\n```"
        html = markdown_to_html(md)
        assert "line1" in html
        assert "line2" in html
        assert "line3" in html

    def test_unclosed_code_block(self):
        md = "```\nunclosed"
        html = markdown_to_html(md)
        assert "</code></pre>" in html


# ── Unordered Lists ─────────────────────────────────────────────────

class TestUnorderedLists:
    def test_unordered_list_dash(self):
        html = markdown_to_html("- item")
        assert "<ul>" in html
        assert "<li>item</li>" in html
        assert "</ul>" in html

    def test_unordered_list_star(self):
        html = markdown_to_html("* item")
        assert "<li>item</li>" in html

    def test_unordered_list_plus(self):
        html = markdown_to_html("+ item")
        assert "<li>item</li>" in html

    def test_unordered_list_multiple_items(self):
        md = "- one\n- two\n- three"
        html = markdown_to_html(md)
        assert "<li>one</li>" in html
        assert "<li>two</li>" in html
        assert "<li>three</li>" in html
        assert html.count("<li>") == 3

    def test_unordered_list_with_inline_formatting(self):
        html = markdown_to_html("- **bold** item")
        assert "<li><strong>bold</strong> item</li>" in html

    def test_unordered_list_closed_by_paragraph(self):
        md = "- item\n\nparagraph"
        html = markdown_to_html(md)
        assert "</ul>" in html
        assert "<p>paragraph</p>" in html


# ── Ordered Lists ───────────────────────────────────────────────────

class TestOrderedLists:
    def test_ordered_list(self):
        html = markdown_to_html("1. item")
        assert "<ol>" in html
        assert "<li>item</li>" in html
        assert "</ol>" in html

    def test_ordered_list_multiple_items(self):
        md = "1. first\n2. second\n3. third"
        html = markdown_to_html(md)
        assert html.count("<li>") == 3

    def test_ordered_list_with_inline_formatting(self):
        html = markdown_to_html("1. `code` item")
        assert "<li><code>code</code> item</li>" in html

    def test_ordered_list_closed_by_paragraph(self):
        md = "1. item\n\npara"
        html = markdown_to_html(md)
        assert "</ol>" in html
        assert "<p>para</p>" in html


# ── Paragraphs ───────────────────────────────────────────────────────

class TestParagraphs:
    def test_simple_paragraph(self):
        html = markdown_to_html("Just a paragraph.")
        assert "<p>Just a paragraph.</p>" in html

    def test_multiple_paragraphs(self):
        md = "First paragraph.\n\nSecond paragraph."
        html = markdown_to_html(md)
        assert "<p>First paragraph.</p>" in html
        assert "<p>Second paragraph.</p>" in html

    def test_paragraph_with_inline_formatting(self):
        md = "This is **bold**, *italic*, and `code`."
        html = markdown_to_html(md)
        assert "<p>This is <strong>bold</strong>, <em>italic</em>, and <code>code</code>.</p>" in html

    def test_paragraph_with_link(self):
        md = "Check [this](https://x.com) out."
        html = markdown_to_html(md)
        assert '<a href="https://x.com">this</a>' in html

    def test_paragraph_with_image(self):
        md = "See ![photo](pic.jpg) below."
        html = markdown_to_html(md)
        assert '<img src="pic.jpg" alt="photo">' in html

    def test_paragraph_line_breaks(self):
        md = "Line one\nLine two"
        html = markdown_to_html(md)
        assert "<br>" in html or "<br />" in html

    def test_empty_input(self):
        html = markdown_to_html("")
        assert html == "" or html.strip() == ""

    def test_whitespace_only(self):
        html = markdown_to_html("   \n\n  ")
        assert html.strip() == ""


# ── Front Matter ────────────────────────────────────────────────────

class TestFrontMatter:
    def test_parse_basic_front_matter(self):
        md = "---\ntitle: My Post\ndate: 2024-01-01\n---\n\nContent"
        meta = parse_front_matter(md)
        assert meta["title"] == "My Post"
        assert meta["date"] == "2024-01-01"

    def test_parse_front_matter_with_extra_whitespace(self):
        md = "---\n  title :  My Post  \n  date :  2024-01-01  \n---\n\nContent"
        meta = parse_front_matter(md)
        assert meta["title"] == "My Post"
        assert meta["date"] == "2024-01-01"

    def test_parse_front_matter_missing(self):
        md = "Just content, no front matter"
        meta = parse_front_matter(md)
        assert meta == {}

    def test_parse_front_matter_empty(self):
        md = "---\n---\n\nContent"
        meta = parse_front_matter(md)
        assert meta == {}

    def test_strip_front_matter(self):
        md = "---\ntitle: Hi\n---\n\nBody text"
        content = strip_front_matter(md)
        assert content == "Body text"

    def test_strip_front_matter_none(self):
        md = "No front matter here"
        content = strip_front_matter(md)
        assert content == md

    def test_front_matter_in_post_pipeline(self):
        md = "---\ntitle: Test\ndate: 2025-06-01\n---\n\n# Hello **World**"
        meta = parse_front_matter(md)
        content = strip_front_matter(md)
        html = markdown_to_html(content)
        assert meta["title"] == "Test"
        assert meta["date"] == "2025-06-01"
        assert "<h1>Hello <strong>World</strong></h1>" in html


# ── Excerpt ──────────────────────────────────────────────────────────

class TestExcerpt:
    def test_excerpt_short_text(self):
        result = excerpt("<p>Short</p>")
        assert result == "Short"

    def test_excerpt_long_text(self):
        text = "word " * 50
        html = f"<p>{text}</p>"
        result = excerpt(html, length=30)
        assert len(result) <= 33  # 30 + "..."
        assert result.endswith("...")

    def test_excerpt_strips_tags(self):
        result = excerpt("<h1>Title</h1><p>Content</p>")
        assert "Title" in result
        assert "Content" in result
        assert "<h1>" not in result

    def test_excerpt_empty(self):
        result = excerpt("")
        assert result == ""


# ── Mixed / Integration ──────────────────────────────────────────────

class TestIntegration:
    def test_full_document(self):
        md = """---
title: My Blog Post
date: 2024-06-15
---

# Welcome

This is a **blog post** with *formatting*.

## Section 1

- item one
- item two

Here is `inline code` and a [link](https://example.com).

![logo](logo.png)

```python
print("hello")
```
"""
        html = markdown_to_html(md)
        meta = parse_front_matter(md)

        assert meta["title"] == "My Blog Post"
        assert meta["date"] == "2024-06-15"
        assert "<h1>Welcome</h1>" in html
        assert "<h2>Section 1</h2>" in html
        assert "<strong>blog post</strong>" in html
        assert "<em>formatting</em>" in html
        assert "<code>inline code</code>" in html
        assert '<a href="https://example.com">link</a>' in html
        assert '<img src="logo.png" alt="logo">' in html
        assert "<li>item one</li>" in html
        assert "<li>item two</li>" in html
        assert 'class="language-python"' in html
        assert "print(&quot;hello&quot;)" in html or 'print("hello")' in html

    def test_no_front_matter_document(self):
        md = "# Just a title\n\nSome content."
        html = markdown_to_html(md)
        meta = parse_front_matter(md)
        assert meta == {}
        assert "<h1>Just a title</h1>" in html
        assert "<p>Some content.</p>" in html
