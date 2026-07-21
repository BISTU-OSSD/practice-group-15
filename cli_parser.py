import argparse

def get_args():
    parser = argparse.ArgumentParser(description="md-sync Markdown批量格式化工具")
    parser.add_argument("command", choices=["format"], help="执行指令，仅支持format")
    parser.add_argument("target_dir", help="需要批量处理的md文件夹路径")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    print(f"指令：{args.command}，目标目录：{args.target_dir}")
