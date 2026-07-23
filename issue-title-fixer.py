#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标题自动补全与层级修正模块（组员2） 
功能：
  - 解析 Markdown 标题（# 层级）
  
  - 统一 # 后空格
  - 修复跳级标题（如 # 后直接 ### → 补为 ##）
  - 若文档无一级标题，在开头补充根标题
  - 生成修改前后对比数据，供日志模块调用

本文件为单文件版本，包含所有代码及内置测试。
运行 python issue-title-fixer.py 即可执行自测。
"""

import re
from typing import List, Dict, Any


def parse_headings(text: str) -> List[Dict[str, Any]]:
    """解析 Markdown 文本，提取所有标题及其行号、层级、内容"""
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
    """
    修正标题层级和空格，补充根标题
    返回: {'fixed_text': str, 'changes': list}
    """
    lines = text.splitlines()
    changes = []

    # ---------- 第1步：统一 # 后空格 ----------
    space_pattern = re.compile(r'^(#{1,6})(\s*)(.*)')
    new_lines = []
    for idx, line in enumerate(lines):
        m = space_pattern.match(line)
        if m:
            hashes, spaces, content = m.groups()
            content = content.strip()
            corrected = f"{hashes} {content}"
            if line != corrected:
                changes.append({
                    'line': idx,
                    'original': line,
                    'fixed': corrected,
                    'type': 'fix-space'
                })
                new_lines.append(corrected)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    # ---------- 第2步：修复跳级标题 ----------
    headings = parse_headings('\n'.join(new_lines))
    prev_level = 0
    level_map = {}  # 行号 -> 修正后的级别
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
        changes.append({
            'line': line_idx,
            'original': old_line,
            'fixed': corrected,
            'type': 'fix-level'
        })

    # ---------- 第3步：补充根标题（若没有一级标题） ----------
    final_headings = parse_headings('\n'.join(final_lines))
    has_h1 = any(h['level'] == 1 for h in final_headings)
    if not has_h1:
        insert_line = f"# {default_title}"
        final_lines.insert(0, insert_line)
        changes.append({
            'line': 0,
            'original': "(无一级标题)",
            'fixed': insert_line,
            'type': 'add-root'
        })

    return {
        'fixed_text': '\n'.join(final_lines),
        'changes': changes
    }


def generate_diff(original: str, fixed: str, changes: List[Dict]) -> Dict[str, Any]:
    """生成修改前后对比数据（供日志模块调用）"""
    return {
        'original': original,
        'fixed': fixed,
        'diff': [
            {
                'line': c['line'],
                'type': c['type'],
                'before': c['original'],
                'after': c['fixed']
            }
            for c in changes
        ]
    }


# ---------- 内置自测（运行该文件时自动执行） ----------
def _run_tests():
    """运行所有单元测试，使用断言验证"""
    print("=== 运行标题修正模块自测 ===\n")

    # 测试1：解析标题
    text = "# 一\n## 二\n### 三"
    hs = parse_headings(text)
    assert len(hs) == 3
    assert hs[0]['level'] == 1
    assert hs[1]['level'] == 2
    assert hs[2]['level'] == 3
    print("✅ 测试1 解析标题通过")

    # 测试2：统一空格
    result = fix_headings("#一级\n##  二级")
    assert result['fixed_text'] == "# 一级\n## 二级"
    assert any(c['type'] == 'fix-space' for c in result['changes'])
    print("✅ 测试2 统一空格通过")

    # 测试3：修复跳级
    result = fix_headings("# 一\n### 三（跳级）")
    expected = "# 一\n## 三（跳级）"
    assert result['fixed_text'] == expected
    assert any(c['type'] == 'fix-level' for c in result['changes'])
    print("✅ 测试3 修复跳级通过")

    # 测试4：补充根标题
    result = fix_headings("## 没有根标题")
    assert result['fixed_text'].startswith("# 文档标题")
    assert any(c['type'] == 'add-root' for c in result['changes'])
    print("✅ 测试4 补充根标题通过")

    # 测试5：综合场景
    raw = "## 二级\n# 一级\n#### 四级"
    result = fix_headings(raw, "根")
    expected = "# 根\n## 二级\n# 一级\n## 四级"
    assert result['fixed_text'] == expected
    print("✅ 测试5 综合场景通过")

    # 测试6：生成差异数据
    orig = "# 旧"
    result = fix_headings(orig, "新根")
    diff = generate_diff(orig, result['fixed_text'], result['changes'])
    assert 'original' in diff and 'fixed' in diff and 'diff' in diff
    assert len(diff['diff']) > 0
    print("✅ 测试6 差异生成通过")

    print("\n🎉 所有测试通过！")


if __name__ == '__main__':
    # 运行自测
    _run_tests()

    # 额外演示：打印一个示例修正结果
    print("\n--- 演示示例 ---")
    sample = "## 二级（无根）\n### 三级跳级\n# 一级"
    result = fix_headings(sample, "项目根标题")
    print("原始文本：")
    print(sample)
    print("\n修正后文本：")
    print(result['fixed_text'])
    print("\n修改记录：")
    for c in result['changes']:
        print(f"  行{c['line']} [{c['type']}]: {c['original']} -> {c['fixed']}")
