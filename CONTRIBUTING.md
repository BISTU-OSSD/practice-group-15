# 贡献指南

感谢参与本项目！请按以下步骤提交代码。

## 开发流程

1. Fork 本仓库
2. 创建分支：`git checkout -b feature/你的功能名`
3. 编写代码，确保通过测试：`python -m pytest`
4. 提交代码：`git commit -m "描述你的改动"`
5. 推送分支：`git push origin feature/你的功能名`
6. 在 GitHub 上发起 Pull Request

## Commit 规范

| 前缀 | 含义 | 示例 |
|------|------|------|
| feat | 新功能 | feat: 添加标题补全功能 |
| fix | 修复Bug | fix: 修复图片路径判断逻辑 |
| docs | 文档修改 | docs: 更新 README |
| test | 测试相关 | test: 添加集成测试 |
| ci | CI配置 | ci: 配置 GitHub Actions |

## PR 要求

- 必须通过 CI 自动化测试
- 至少一名组员 Review 通过
- Commit 信息符合上述规范