#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标题自动生成与补全模块
功能：
1. 调用 DeepSeek API 根据文档内容生成标题
2. 自动补全到 Front Matter 的 title: 字段
3. 如果文档没有一级标题，同时补充为根标题
"""
import re
import sys
import os
import argparse
from typing import List, Dict, Any, Optional, Tuple
import requests

# ---------- Front Matter 处理 ----------
def extract_front_matter(text: str) -> Tuple[Optional[Dict[str, str]], str, bool]:
    """提取 Markdown 开头的 YAML Front Matter"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != '---':
        return None, text, False

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_idx = i
            break
    if end_idx is None:
        return None, text, False

    front_matter_lines = lines[1:end_idx]
    body_lines = lines[end_idx+1:]

    # 解析 key: value
    data = {}
    for line in front_matter_lines:
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip()
    return data, '\n'.join(body_lines), True

def build_front_matter(data: Dict[str, str]) -> str:
    """构建 YAML Front Matter 块"""
    lines = ['---']
    for k, v in data.items():
        lines.append(f"{k}: {v}")
    lines.append('---')
    return '\n'.join(lines)

def update_or_add_title(text: str, new_title: str) -> str:
    """
    更新或添加 title 字段到 Front Matter
    如果文档没有 Front Matter，则创建一个
    """
    data, body, has_fm = extract_front_matter(text)
    
    if has_fm:
        # 更新现有 Front Matter
        data['title'] = new_title
        new_fm = build_front_matter(data)
        return new_fm + '\n' + body
    else:
        # 创建新的 Front Matter
        new_fm = f"---\ntitle: {new_title}\n---\n"
        return new_fm + text

# ---------- 标题修正（简化版） ----------
def fix_headings(text: str, default_title: str) -> Dict[str, Any]:
    """修正标题层级，并确保有一级标题"""
    lines = text.splitlines()
    changes = []

    # 统一空格
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

    # 修复跳级
    def parse_headings(text_lines: List[str]) -> List[Dict]:
        headings = []
        for idx, line in enumerate(text_lines):
            match = re.match(r'^(#{1,6})\s+(.*)', line)
            if match:
                headings.append({
                    'line': idx,
                    'level': len(match.group(1)),
                    'text': match.group(2).strip()
                })
        return headings

    headings = parse_headings(new_lines)
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

    # 补充根标题（如果没有一级标题）
    final_headings = parse_headings(final_lines)
    has_h1 = any(h['level'] == 1 for h in final_headings)
    if not has_h1:
        insert_line = f"# {default_title}"
        final_lines.insert(0, insert_line)
        changes.append({'line': 0, 'original': '(无一级标题)', 'fixed': insert_line, 'type': 'add-root'})

    return {'fixed_text': '\n'.join(final_lines), 'changes': changes}

# ---------- DeepSeek API 调用 ----------
def generate_title_with_deepseek(content: str, api_key: str) -> str:
    """调用 DeepSeek API 生成标题"""
    # 截取前 3000 字符
    truncated = content[:3000]
    prompt = f"""请根据以下文档内容生成一个简洁、准确的标题（不超过20个字），只输出标题，不要有其他内容：

{truncated}"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    try:
        # 修复：正确的 API 地址是 /v1/chat/completions
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",  # 修正了这里
            headers=headers,
            json=payload,
            timeout=30
        )
        resp.raise_for_status()
        result = resp.json()
        title = result['choices'][0]['message']['content'].strip()
        # 清理可能的引号和多余符号
        title = re.sub(r'^["\']|["\']$', '', title)
        # 如果标题为空或过长，截断
        if len(title) > 50:
            title = title[:50]
        return title if title else "文档标题"
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print(f"❌ API 密钥无效或已过期，请检查您的 API Key")
            print(f"  提示：DeepSeek API Key 格式为 'sk-xxx'")
        else:
            print(f"⚠️  HTTP 错误: {e}")
        return "文档标题"
    except Exception as e:
        print(f"⚠️  调用 DeepSeek API 失败: {e}")
        print("  将使用默认标题: 文档标题")
        return "文档标题"

# ---------- 主函数 ----------
def main():
    parser = argparse.ArgumentParser(
        description="自动生成 Markdown 标题并补全到 title: 字段",
        epilog="示例: python issue-title-fixer.py input.md --api-key sk-xxx"
    )
    parser.add_argument('input_file', help='要处理的 .md 文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径（不指定则覆盖原文件）')
    parser.add_argument('--api-key', help='DeepSeek API 密钥（也可通过环境变量 DEEPSEEK_API_KEY 设置）')
    parser.add_argument('--test', action='store_true', help='运行自测')
    args = parser.parse_args()

    if args.test:
        _run_tests()
        return

    # 获取 API Key（优先使用命令行参数，其次环境变量）
    api_key = args.api_key or os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ 错误：请提供 API Key")
        print("  方式1: --api-key sk-xxx")
        print("  方式2: 设置环境变量 DEEPSEEK_API_KEY=sk-xxx")
        sys.exit(1)

    # 读取文件
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            original = f.read()
    except FileNotFoundError:
        print(f"❌ 错误：文件 '{args.input_file}' 不存在")
        sys.exit(1)

    print(f"📖 正在处理: {args.input_file}")

    # 1. 提取正文（去除 Front Matter）
    _, body, has_fm = extract_front_matter(original)
    content_to_analyze = body if body else original

    # 2. 调用 API 生成标题
    print("🤖 正在调用 DeepSeek API 生成标题...")
    generated_title = generate_title_with_deepseek(content_to_analyze, api_key)
    print(f"✅ 生成标题: {generated_title}")

    # 3. 修正标题层级（补充根标题）
    print("🔧 修正标题层级...")
    result = fix_headings(original, default_title=generated_title)
    fixed_text = result['fixed_text']

    # 4. 更新 Front Matter 的 title 字段
    print("📝 更新 Front Matter 的 title 字段...")
    final_text = update_or_add_title(fixed_text, generated_title)

    # 5. 输出文件
    output_path = args.output if args.output else args.input_file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_text)

    # 6. 打印摘要
    print(f"\n✨ 处理完成！")
    print(f"📂 输出文件: {output_path}")
    print(f"📌 标题: {generated_title}")
    print(f"🔄 共修改 {len(result['changes'])} 处")
    for c in result['changes']:
        print(f"   - 行 {c['line']} [{c['type']}]: {c['original']} -> {c['fixed']}")

# ---------- 测试 ----------
def _run_tests():
    print("🧪 运行测试...\n")
    
    # 测试 Front Matter 提取
    test_text = "---\ntitle: 旧标题\n---\n# 正文内容"
    data, body, has = extract_front_matter(test_text)
    assert has, "应该检测到 Front Matter"
    assert data['title'] == '旧标题', "title 提取错误"
    assert body == '# 正文内容', "正文提取错误"
    print("✅ 测试1: Front Matter 提取通过")

    # 测试更新 title
    updated = update_or_add_title(test_text, "新标题")
    assert "title: 新标题" in updated, "title 更新失败"
    assert "旧标题" not in updated, "旧标题未删除"
    print("✅ 测试2: title 更新通过")

    # 测试没有 Front Matter 时添加
    test_no_fm = "# 只有正文"
    updated = update_or_add_title(test_no_fm, "自动生成标题")
    assert "---\ntitle: 自动生成标题\n---" in updated, "未创建 Front Matter"
    print("✅ 测试3: 无 Front Matter 时创建通过")

    # 测试标题修正
    test_headings = "## 二级标题\n### 三级标题"
    result = fix_headings(test_headings, "根标题")
    assert "# 根标题" in result['fixed_text'], "根标题未添加"
    assert "## 二级标题" in result['fixed_text'], "层级错误"
    assert "## 三级标题" in result['fixed_text'], "跳级未修复"
    print("✅ 测试4: 标题修正通过")

    print("\n🎉 所有测试通过！")

if __name__ == '__main__':
    main()