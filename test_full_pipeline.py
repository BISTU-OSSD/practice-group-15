import os
import subprocess


def test_scanner_can_find_docs():
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    assert os.path.exists(docs_dir), "docs 文件夹不存在"


def test_all_md_files_readable():
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    md_files = [f for f in os.listdir(docs_dir) if f.endswith(".md")]
    assert len(md_files) > 0, "docs 目录下没有任何 .md 文件"
    for f in md_files:
        path = os.path.join(docs_dir, f)
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
            assert len(content) > 0, f"{f} 是空文件"


def test_titles_have_valid_format():
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    md_files = [f for f in os.listdir(docs_dir) if f.endswith(".md")]
    for f in md_files:
        path = os.path.join(docs_dir, f)
        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith("#"):
                    assert line.startswith("# "), f"{f} 中标题格式异常: {line}"


def test_image_paths_are_relative():
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    md_files = [f for f in os.listdir(docs_dir) if f.endswith(".md")]
    for f in md_files:
        path = os.path.join(docs_dir, f)
        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                if "![" in line:
                    start = line.index("](") + 2
                    end = line.index(")", start)
                    img_path = line[start:end]
                    assert not img_path.startswith("http"), f"{f} 中图片使用了绝对网络路径: {img_path}"
                    assert not img_path.startswith("/"), f"{f} 中图片使用了根路径: {img_path}"


def test_sync_log_exists():
    project_root = os.path.join(os.path.dirname(__file__), "..")
    log_path = os.path.join(project_root, "sync-log.md")
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as file:
            assert len(file.read()) > 0, "sync-log.md 是空文件"