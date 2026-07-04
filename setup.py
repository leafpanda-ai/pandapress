from setuptools import setup, find_packages

setup(
    name="pandapress",
    version="0.2.0",
    description="🐼 PandaPress - 极简 Markdown 静态博客引擎",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/leafpanda-ai/pandapress",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["pandapress=pandapress.__main__:main"],
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
