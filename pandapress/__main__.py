import sys
import argparse

from . import __version__
from .builder import build
from .server import serve


def main():
    parser = argparse.ArgumentParser(prog="pandapress", description="PandaPress - 极简 Markdown 静态博客引擎")
    parser.add_argument("--version", action="version", version=f"PandaPress v{__version__}")

    sub = parser.add_subparsers(dest="command")

    # build
    build_p = sub.add_parser("build", help="构建静态博客")
    build_p.add_argument("-i", "--input", default=".", help="文章目录")
    build_p.add_argument("-o", "--output", default="dist", help="输出目录")
    build_p.add_argument("-t", "--theme", default="default", help="主题名称")
    build_p.add_argument("--port", type=int, default=8080, help="预览服务器端口")
    build_p.add_argument("--watch", action="store_true", help="实时预览（监听文件变更自动重构建）")

    # new
    new_p = sub.add_parser("new", help="新建文章")
    new_p.add_argument("title", help="文章标题")

    args = parser.parse_args()
    if args.command == "build":

        def _rebuild():
            build(args.input, args.output, args.theme)

        _rebuild()
        if args.watch:
            serve(args.output, port=args.port, input_dir=args.input, rebuild=_rebuild)
    elif args.command == "new":
        from .template import new_post
        new_post(args.title)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
