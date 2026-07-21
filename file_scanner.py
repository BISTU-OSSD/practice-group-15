import os

def scan_md_files(root_path: str) -> list:
    """递归遍历文件夹，返回所有md文件绝对路径"""
    md_file_list = []
    for dirpath, _, filenames in os.walk(root_path):
        for file in filenames:
            if file.endswith(".md"):
                full_path = os.path.abspath(os.path.join(dirpath, file))
                md_file_list.append(full_path)
    return md_file_list

if __name__ == "__main__":
    res = scan_md_files("./docs-demo")
    print("扫描到的md文件：", res)
