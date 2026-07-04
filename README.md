# 🐼 PandaPress

> 极简 Markdown 静态博客引擎

## 快速开始

```bash
# 安装
pip install pandapress

# 新建文章
pandapress new "我的第一篇文章"

# 构建博客
pandapress build

# 实时预览
pandapress build --watch
```

## 特性

- ✨ **零依赖** — 纯 Python，无需 Node.js 或 Ruby
- ⚡ **毫秒构建** — 即使上百篇文章也瞬间完成
- 📝 **Markdown 写作** — 专注内容，不操心排版
- 🎨 **主题系统** — 内置优雅主题，支持自定义
- 🔥 **实时预览** — `--watch` 模式，改完即看
- 🚀 **一键部署** — 输出纯静态 HTML，GitHub Pages 友好

## 使用

```
usage: pandapress [-h] [--version] {build,new} ...

PandaPress - 极简 Markdown 静态博客引擎

命令:
  build      构建静态博客
  new        新建文章
```

### 构建

```bash
pandapress build -i ./blog -o ./dist --watch
```

### 新建文章

```bash
pandapress new "我的新文章"
```

生成 `我的新文章.md`，编辑后重新 build 即可。

## 项目结构

```
.
├── pandapress/          # 源码
│   ├── __init__.py
│   ├── __main__.py      # CLI 入口
│   ├── builder.py       # 构建引擎
│   ├── server.py        # 预览服务器 + 文件变更监听
│   ├── template.py      # 模板引擎（Markdown 渲染、主题加载）
│   └── themes/          # 内置主题
├── setup.py
├── .gitignore
└── README.md
```

## 许可证

MIT
