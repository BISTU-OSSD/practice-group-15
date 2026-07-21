import re

class MdTitleFixer:
    def __init__(self):
        # 匹配行首Markdown标题，最多六级标题
        self.title_pattern = re.compile(r'^(#{1,6})\s*(.+)$')

    def extract_titles(self, md_text: str):
        """【任务1】解析MD文本，提取全部标题信息
        :param md_text: 完整Markdown字符串
        :return: 所有文本行、标题信息列表
        """
        lines = md_text.splitlines()
        titles = []
        for idx, line in enumerate(lines):
            match = self.title_pattern.match(line)
            if match:
                level = len(match.group(1))
                title_content = match.group(2).strip()
                titles.append({
                    "row_index": idx,
                    "old_level": level,
                    "title_text": title_content
                })
        return lines, titles

    def fix_hierarchy(self, lines: list, titles: list):
        """【任务2】核心算法：修复跳级、统一格式、补充一级标题
        :return: 修正后文本行, 修改变更记录
        """
        change_records = []
        # 判断是否存在一级标题，无则自动添加根标题
        has_h1 = any(item["old_level"] == 1 for item in titles)
        if not has_h1:
            lines.insert(0, "# 文档根标题")
            change_records.append({
                "type": "title_add",
                "line_number": 1,
                "before": None,
                "after": "# 文档根标题"
            })

        prev_level = 1
        new_lines = lines.copy()
        for title_info in titles:
            line_idx = title_info["row_index"]
            curr_level = title_info["old_level"]
            text = title_info["title_text"]

            # 修复标题跳级
            if curr_level > prev_level + 1:
                curr_level = prev_level + 1
            # 标准化标题格式 #后保留单个空格
            new_title = "#" * curr_level + " " + text
            old_text = new_lines[line_idx]

            if old_text != new_title:
                change_records.append({
                    "type": "title_modify",
                    "line_number": line_idx + 1,
                    "before": old_text,
                    "after": new_title
                })
                new_lines[line_idx] = new_title
            prev_level = curr_level
        return new_lines, change_records

    def process_document(self, md_text: str):
        """对外统一接口【组员1调用入口】
        输入原始md字符串，返回结构化结果
        """
        origin_lines, title_list = self.extract_titles(md_text)
        fixed_lines, change_list = self.fix_hierarchy(origin_lines, title_list)
        fixed_content = "\n".join(fixed_lines)

        #【任务4】输出标准化数据，交给组员3日志模块
        result = {
            "origin_content": md_text,    # 原始文档文本
            "fixed_content": fixed_content,# 修正完成文本
            "change_list": change_list,    # 所有修改记录（日志数据源）
            "module": "title_fixer"        # 标记模块来源，方便组员3区分标题/图片修改
        }
        return result


# =========【任务3 单元测试】独立测试模块功能 =========
if __name__ == "__main__":
    # 模拟存在跳级问题的Markdown文本
    test_md = """
# MkDocs博客介绍
### 部署方式说明
##### GitHub Actions配置
## 网站优化方案
普通正文内容，不属于标题，不会被处理
    """
    tool = MdTitleFixer()
    output = tool.process_document(test_md)

    print("====原始文档====")
    print(output["origin_content"])
    print("\n====修正后文档====")
    print(output["fixed_content"])
    print("\n====变更记录（提供组员3生成日志）====")
    for item in output["change_list"]:
        print(item)
