# Markdown 文档扫描修复工具

> 自动扫描 Markdown 文件，修复标题格式、图片路径，生成修改日志。

## 功能

- 📂 批量扫描指定目录下所有 .md 文件
- ✏️ 标题自动补全与格式统一
- 🖼️ 图片路径标准化（相对路径）
- 📝 自动生成修改日志 sync-log.md
- 🔄 原始文件自动备份

## 安装

git clone https://github.com/你的用户名/你的仓库名.git
cd 你的仓库名
pip install -r requirements.txt

## 使用方法

python main.py ./docs

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| 目录 | 要扫描的文件夹路径 | ./docs |
| --dry-run | 只预览不修改 | python main.py ./docs --dry-run |

## 项目结构

├── .github/workflows/ci.yml   # CI 配置
├── docs/                      # 示例文档
├── tests/                     # 测试文件
├── main.py                    # 入口文件
├── requirements.txt           # 依赖
├── LICENSE                    # 开源协议
└── README.md                  # 项目说明

## 贡献指南

请阅读 CONTRIBUTING.md

## 开源协议

MIT License