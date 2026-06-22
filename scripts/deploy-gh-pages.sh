#!/usr/bin/env bash
# ============================================
# 一键部署到 GitHub Pages (纯静态，无 API Key)
# 用法: bash scripts/deploy-gh-pages.sh
# 
# 原理：只把 output/ 目录推送到 gh-pages 分支
# 源代码、API Key 完全不会出现在 GitHub 上
# ============================================
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUTPUT_DIR="$ROOT/output"

# 检查 output 是否存在
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "❌ output/ 目录不存在，请先运行: python3 build.py"
    exit 1
fi

# 检查是否有远程仓库
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
if [ -z "$REMOTE_URL" ]; then
    echo "❌ 未配置 git remote"
    echo ""
    echo "请先在 GitHub 创建仓库，然后运行："
    echo "  git remote add origin git@github.com:你的用户名/仓库名.git"
    exit 1
fi

echo "🚀 开始部署到 GitHub Pages..."
echo "   远程仓库: $REMOTE_URL"
echo "   只推送 output/ 纯静态文件（不含 API Key）"
echo ""

cd "$ROOT"

# 保存当前分支
CURRENT_BRANCH=$(git branch --show-current)

# 创建/切换到 gh-pages 分支
if git rev-parse --verify gh-pages >/dev/null 2>&1; then
    git checkout gh-pages
else
    git checkout --orphan gh-pages
    git rm -rf --quiet . 2>/dev/null || true
fi

# 清空当前内容（保留 .git）
find . -maxdepth 1 -not -name '.git' -not -name '.' -not -name '..' -exec rm -rf {} + 2>/dev/null || true

# 把 output 内容复制到根
cp -r "$OUTPUT_DIR"/* .

# .nojekyll 确保 GitHub Pages 正确处理
touch .nojekyll

# 提交并推送
git add -A
git commit -m "🚀 Deploy static site - $(date '+%Y-%m-%d %H:%M')" || echo "⚠️  没有新变更，跳过提交"

echo "📤 推送到 gh-pages..."
git push origin gh-pages --force

# 切回原分支
git checkout "$CURRENT_BRANCH"

echo ""
echo "✅ 部署完成！"
