# 🤖 全自动内容站 (知晓一刻)

纯代码驱动的内容站点，AI 自动写作 + 自动构建部署，目标是验证"代码能否创造持续被动收入"。

**当前状态**：使用 DeepSeek API，已生成 4 篇中文科技文章。

## 项目结构

```
auto-content-site/
├── content/              # AI 生成的文章 (JSON)
├── templates/            # Jinja2 页面模板
├── scripts/
│   └── generate.py       # AI 内容生成器 (支持 OpenAI/DeepSeek/OpenRouter)
├── build.py              # 静态站点构建器
├── pipeline.py           # 一键流水线
├── config.json           # 站点配置
└── .github/workflows/    # 自动部署 CI/CD
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置 DeepSeek API Key
export DEEPSEEK_API_KEY="sk-xxx"

# 3. 生成内容 + 构建站点
python pipeline.py --provider deepseek --count 1

# 4. 本地预览 (生成后)
open output/index.html
```

## 🚀 部署到 GitHub Pages

### 第 1 步：创建 GitHub 仓库
在 [github.com/new](https://github.com/new) 创建一个**公开**仓库，命名为 `auto-content-site`

### 第 2 步：推送代码
```bash
cd auto-content-site
git remote add origin git@github.com:你的用户名/auto-content-site.git
git push -u origin main
```

### 第 3 步：设置 Secrets
在仓库 Settings → Secrets and variables → Actions 中添加：
- `DEEPSEEK_API_KEY` = 你的 DeepSeek API Key

### 第 4 步：启用 GitHub Pages
Settings → Pages → Source 选择 `Deploy from a branch`，分支选 `gh-pages`，保存。

### 第 5 步：触发首次部署
Actions 标签 → 选择 `Daily Auto Content & Deploy` → `Run workflow`

部署完成后，网站将在 `https://你的用户名.github.io/auto-content-site` 上线！

### 第 6 步：更新 URL
编辑 `config.json`，将 `YOUR_GITHUB_USERNAME` 替换为你的 GitHub 用户名，提交推送。

## 常用命令

| 命令 | 说明 |
|------|------|
| `python scripts/generate.py --provider deepseek` | 生成一篇新文章 |
| `python scripts/generate.py --provider deepseek --count 5` | 批量生成 |
| `python scripts/generate.py --topic 人工智能` | 指定主题 |
| `python build.py` | 构建静态站点 |
| `python pipeline.py --provider deepseek --count 3` | 生成 + 构建 |

## 🔒 安全说明

- API Key **不会**出现在代码中，通过 GitHub Secrets 安全存储
- `.env` 文件和 `output/` 构建产物不会上传到仓库
- 如需本地使用，通过环境变量 `DEEPSEEK_API_KEY` 传入

## 变现路径

1. **Google AdSense** — 访问量起来后挂广告
2. **亚马逊/京东联盟** — 文章里嵌入商品链接
3. **付费投稿** — 接受软文推广
4. **卖站** — 有流量后可出售（估值约月收入 x20-30 倍）
