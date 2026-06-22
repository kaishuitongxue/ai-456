#!/bin/bash
# ============================================
# 每日自动更新脚本
# 1. 生成新文章 (DeepSeek API)
# 2. 构建静态站点
# 3. 只推送纯静态 HTML 到 GitHub Pages
# 
# API Key 从 ~/.auto-content-site.env 读取，绝不上传
# ============================================
set -e

PROJECT_DIR="/Users/maoyunqiao/Documents/Codex/2026-06-22/q/auto-content-site"
LOG_FILE="$PROJECT_DIR/logs/auto-update.log"

mkdir -p "$PROJECT_DIR/logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========== 开始每日更新 =========="

# 加载 API Key
if [ -f "$HOME/.auto-content-site.env" ]; then
    source "$HOME/.auto-content-site.env"
    log "✅ API Key 已加载"
else
    log "❌ 找不到 ~/.auto-content-site.env"
    exit 1
fi

cd "$PROJECT_DIR"

# 确保在 main 分支
git checkout main 2>/dev/null || true
git pull origin main 2>/dev/null || true

# 1. 生成一篇新文章
log "🤖 生成新文章..."
if python3 scripts/generate.py --provider deepseek --count 1 2>&1 | tee -a "$LOG_FILE"; then
    log "✅ 文章生成成功"
else
    log "⚠️  文章生成失败，但继续构建"
fi

# 2. 构建站点
log "🔨 构建静态站点..."
python3 build.py 2>&1 | tee -a "$LOG_FILE"
log "✅ 构建完成"

# 3. 提交 content 变更到 main 分支
git add content/ 2>/dev/null || true
if git diff --staged --quiet 2>/dev/null; then
    log "📝 没有新内容，跳过 main 提交"
else
    git commit -m "Auto: daily content - $(date '+%Y-%m-%d')" 2>&1 | tee -a "$LOG_FILE"
    git push origin main 2>&1 | tee -a "$LOG_FILE"
    log "✅ main 分支已更新"
fi

# 4. 部署纯静态 output/ 到 gh-pages
log "🚀 部署到 GitHub Pages..."
TMPDIR=$(mktemp -d)
cp -r output/* "$TMPDIR/"
touch "$TMPDIR/.nojekyll"
cd "$TMPDIR"
git init
git checkout -b gh-pages
git config user.email "autocontent@local.dev"
git config user.name "AutoContent"
git add -A
git commit -m "🚀 Daily deploy - $(date '+%Y-%m-%d %H:%M')"
git remote add origin git@github.com:kaishuitongxue/ai-456.git
git push origin gh-pages --force
cd /
rm -rf "$TMPDIR"

log "✅ 部署完成！"
log "========== 更新结束 =========="
echo ""
