#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标题自动补全与层级修正模块（组员2）
支持命令行处理单个 Markdown 文件：
    python issue-title-fixer.py input.md -o output.md [--title "根标题"]
"""
import re
import sys
import argparse
from typing import List, Dict, Any

# ---------- 核心函数（不变） ----------
def parse_headings(text: str) -> List[Dict[str, Any]]:
    lines = text.splitlines()
    headings = []
    for idx, line in enumerate(lines):
        match = re.match(r'^(#{1,6})\s+(.*)', line)
        if match:
            headings.append({
                'line': idx,
                'level': len(match.group(1)),
                'raw': line,
                'text': match.group(2).strip()
            })
    return headings

def fix_headings(text: str, default_title: str = "文档标题") -> Dict[str, Any]:
    lines = text.splitlines()
    changes = []

    # 第1步：统一空格
    space_pattern = re.compile(r'^(#{1,6})(\s*)(.*)')
    new_lines = []
    for idx, line in enumerate(lines):
        m = space_pattern.match(line)
        if m:
            hashes, spaces, content = m.groups()
            content = content.strip()
            corrected = f"{hashes} {content}"
            if line != corrected:
                changes.append({'line': idx, 'original': line, 'fixed': corrected, 'type': 'fix-space'})
                new_lines.append(corrected)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    # 第2步：修复跳级
    headings = parse_headings('\n'.join(new_lines))
    prev_level = 0
    level_map = {}
    for h in headings:
        expected = prev_level + 1
        if h['level'] > expected and prev_level > 0:
            level_map[h['line']] = expected
            prev_level = expected
        else:
            prev_level = h['level']

    final_lines = new_lines[:]
    for line_idx, new_level in level_map.items():
        old_line = final_lines[line_idx]
        content = re.sub(r'^#{1,6}\s*', '', old_line).strip()
        corrected = '#' * new_level + ' ' + content
        final_lines[line_idx] = corrected
        changes.append({'line': line_idx, 'original': old_line, 'fixed': corrected, 'type': 'fix-level'})

    # 第3步：补充根标题
    final_headings = parse_headings('\n'.join(final_lines))
    has_h1 = any(h['level'] == 1 for h in final_headings)
    if not has_h1:
        insert_line = f"# {default_title}"
        final_lines.insert(0, insert_line)
        changes.append({'line': 0, 'original': '(无一级标题)', 'fixed': insert_line, 'type': 'add-root'})

    return {'fixed_text': '\n'.join(final_lines), 'changes': changes}

def generate_diff(original: str, fixed: str, changes: List[Dict]) -> Dict[str, Any]:
    return {
        'original': original,
        'fixed': fixed,
        'diff': [{'line': c['line'], 'type': c['type'], 'before': c['original'], 'after': c['fixed']} for c in changes]
    }

# ---------- 新增：文件处理命令行入口 ----------
def main():
    parser = argparse.ArgumentParser(description="修正 Markdown 文件的标题层级")
    parser.add_argument('input_file', help='要处理的 .md 文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径（不指定则覆盖原文件）')
    parser.add_argument('--title', default='文档标题', help='若文档无一级标题，补充的根标题名称')
    parser.add_argument('--test', action='store_true', help='运行自测（此时忽略其他参数）')
    args = parser.parse_args()

    # 如果指定 --test，执行内置测试并退出
    if args.test:
        _run_tests()
        return

    # 读取文件
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            original = f.read()
    except FileNotFoundError:
        print(f"错误：文件 '{args.input_file}' 不存在")
        sys.exit(1)

    # 执行修正
    result = fix_headings(original, args.title)
    fixed_text = result['fixed_text']
    changes = result['changes']

    # 输出到文件
    output_path = args.output if args.output else args.input_file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(fixed_text)

    # 打印修改摘要
    print(f"处理完成！共修改 {len(changes)} 处")
    for c in changes:
        print(f"  行{c['line']} [{c['type']}]: {c['original']} -> {c['fixed']}")

    # 同时生成差异数据（可选，供日志模块使用）
    diff = generate_diff(original, fixed_text, changes)
    # 如果希望保存 diff 到 JSON，可在此处增加写入逻辑

# ---------- 内置自测（保持不变） ----------
def _run_tests():
    print("=== 运行标题修正模块自测 ===\n")
    text = "# 一\n## 二\n### 三"
    hs = parse_headings(text)
    assert len(hs) == 3
    assert hs[0]['level'] == 1
    assert hs[1]['level'] == 2
    assert hs[2]['level'] == 3
    print("测试1 解析标题通过")

    result = fix_headings("#一级\n##  二级")
    assert result['fixed_text'] == "# 一级\n## 二级"
    assert any(c['type'] == 'fix-space' for c in result['changes'])
    print(" 测试2 统一空格通过")

    result = fix_headings("# 一\n### 三（跳级）")
    expected = "# 一\n## 三（跳级）"
    assert result['fixed_text'] == expected
    assert any(c['type'] == 'fix-level' for c in result['changes'])
    print(" 测试3 修复跳级通过")

    result = fix_headings("## 没有根标题")
    assert result['fixed_text'].startswith("# 文档标题")
    assert any(c['type'] == 'add-root' for c in result['changes'])
    print(" 测试4 补充根标题通过")

    raw = "## 二级\n# 一级\n#### 四级"
    result = fix_headings(raw, "根")
    expected = "# 根\n## 二级\n# 一级\n## 四级"
    assert result['fixed_text'] == expected
    print(" 测试5 综合场景通过")

    orig = "# 旧"
    result = fix_headings(orig, "新根")
    diff = generate_diff(orig, result['fixed_text'], result['changes'])
    assert 'original' in diff and 'fixed' in diff and 'diff' in diff
    assert len(diff['diff']) > 0
    print("测试6 差异生成通过")
    print("\n🎉 所有测试通过！")

if __name__ == '__main__':
    main()
