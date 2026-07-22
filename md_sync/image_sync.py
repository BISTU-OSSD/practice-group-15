import re
import os
import shutil
from datetime import datetime


class MdImageSync:
    def __init__(self):
        # 正则匹配markdown图片语法 ![alt文字](图片路径)
        self.img_pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')
        # 保存所有修改记录
        self.change_records = []

    def is_network_url(self, path: str) -> bool:
        """判断是否是网络图片链接"""
        return path.startswith(("http://", "https://"))

    def normalize_image_path(self, original_path: str, md_file_dir: str) -> str:
        """本地图片路径标准化，转为markdown可用相对路径"""
        # 网络链接直接原样返回，不作修改
        if self.is_network_url(original_path):
            return original_path

        clean_path = original_path.strip()
        # 如果是绝对路径，转换成相对路径
        if os.path.isabs(clean_path):
            try:
                clean_path = os.path.relpath(clean_path, md_file_dir)
            except Exception:
                pass
        # Windows反斜杠统一换成 / 适配Markdown
        clean_path = clean_path.replace(os.sep, "/")
        return clean_path

    def process_md_content(self, md_text: str, md_file_path: str) -> str:
        """整篇md文本图片批量处理，记录改动"""
        md_abs_path = os.path.abspath(md_file_path)
        md_dir = os.path.dirname(md_abs_path)

        def replace_image(match):
            alt_text = match.group(1)
            old_path = match.group(2)
            new_path = self.normalize_image_path(old_path, md_dir)

            # 路径发生变化就存入日志
            if old_path != new_path:
                self.change_records.append({
                    "type": "图片路径修改",
                    "alt": alt_text,
                    "old_path": old_path,
                    "new_path": new_path
                })
            return f'![{alt_text}]({new_path})'

        return self.img_pattern.sub(replace_image, md_text)

    def safe_write_md(self, file_path: str, new_content: str):
        """写入新md内容，自动备份原始文件"""
        abs_path = os.path.abspath(file_path)
        # 文件不存在，直接新建
        if not os.path.exists(abs_path):
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return

        # 原始文件备份（带时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{abs_path.rsplit('.md', 1)[0]}_备份_{timestamp}.md"
        shutil.copy2(abs_path, backup_path)

        # 写入修改后的内容
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(new_content)

    def export_sync_log(self, log_path: str = "sync-log.md"):
        """导出图片修改日志 sync-log.md"""
        if not self.change_records:
            log_text = "# Markdown图片同步修改日志\n> 本次运行没有图片路径改动\n"
        else:
            log_text = "# Markdown图片同步修改日志\n\n"
            log_text += f"执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            for index, item in enumerate(self.change_records, start=1):
                log_text += f"### {index}. {item['type']}\n"
                log_text += f"- 图片备注：{item['alt']}\n"
                log_text += f"- 修改前路径：`{item['old_path']}`\n"
                log_text += f"- 修改后路径：`{item['new_path']}`\n\n"

        with open(log_path, "w", encoding="utf-8") as f:
            f.write(log_text)
        print(f"✅ 修改日志成功生成：{log_path}")


# ============ 程序运行入口（测试用，不要删除！）============
if __name__ == "__main__":
    # 【重点】test.md 就是我们用来测试的markdown文件
    target_file = "test.md"

    # 创建工具对象
    img_tool = MdImageSync()

    # 读取md文件
    with open(target_file, "r", encoding="utf-8") as f:
        md_content = f.read()

    # 处理图片路径
    new_md_content = img_tool.process_md_content(md_content, target_file)

    # 写入文件 + 自动备份原文件
    img_tool.safe_write_md(target_file, new_md_content)

    # 输出修改日志 sync-log.md
    img_tool.export_sync_log()
