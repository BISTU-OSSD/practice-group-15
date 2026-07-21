# 使用示例

## 示例1：扫描整个文档目录

python main.py ./docs

输出：
> 扫描完成，共处理 5 个文件
> 标题修复：3 处
> 图片路径修复：2 处
> 日志已生成：sync-log.md

## 示例2：预览模式（只看不改）

python main.py ./docs --dry-run

输出：
> [预览模式] 以下文件将被修改：
> - docs/guide.md：标题格式异常
> - docs/api.md：图片路径需要修复

## 示例3：查看修改日志

cat sync-log.md