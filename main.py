from cli_parser import get_args
from file_scanner import scan_md_files

def main():
    args = get_args()
    target = args.target_dir
    print(f"开始扫描目录 {target} 下所有Markdown文件")
    md_files = scan_md_files(target)
    print(f"共扫描到 {len(md_files)} 个md文件")
    # 预留接口，后续对接标题修正、图片处理模块
    return md_files

if __name__ == "__main__":
    main()
