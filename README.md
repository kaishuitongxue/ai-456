# 🤖 全自动内容站

纯代码驱动的内容站点，AI 自动写作 + 自动构建部署，目标是验证"代码能否创造持续被动收入"。

## 项目结构

```
auto-content-site/
├── content/              # AI 生成的文章 (JSON)
├── templates/            # Jinja2 页面模板
│   ├── base.html         # 基础布局 (SEO 元标签)
│   ├── index.html        # 首页 (分页)
│   ├── post.html         # 文章详情页
│   └── topic.html        # 主题分类页
├── scripts/
│   └── generate.py       # AI 内容生成器
├── build.py              # 静态站点构建器
├── pipeline.py           # 一键流水线
├── config.json           # 站点配置
└── .github/workflows/    # 自动部署 CI/CD
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置 API Key
export OPENAI_API_KEY="sk-xxx"

# 3. 生成内容 + 构建站点
python pipeline.py

# 4. 本地预览
python pipeline.py --serve
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `python scripts/generate.py` | 生成一篇新文章 |
| `python scripts/generate.py --count 5` | 批量生成 5 篇 |
| `python scripts/generate.py --topic 人工智能` | 指定主题生成 |
| `python build.py` | 构建静态站点 |
| `python pipeline.py --count 3 --serve` | 生成 3 篇 + 构建 + 预览 |

## 部署方案

### 方案 A：GitHub Pages（免费）

1. Fork 此仓库到你的 GitHub
2. 在仓库 Settings → Secrets 添加 `OPENAI_API_KEY`
3. 在 Settings → Pages 启用 GitHub Pages，选择 `gh-pages` 分支
4. GitHub Actions 每天自动生成内容并部署
5. 到 Cloudflare 添加你自己的域名，挂 AdSense

### 方案 B：Vercel（免费）

1. 本地运行 `python pipeline.py --count 10` 生成初始内容
2. 推送到 GitHub，在 Vercel 导入项目
3. 设置 Output Directory 为 `output`
4. 本地每天运行一次 pipeline 并推送更新

### 方案 C：本地定时任务

```bash
# 每天早 8 点自动执行
crontab -e
# 添加：
0 8 * * * cd /path/to/project && python pipeline.py && git push
```

## 变现路径

1. **Google AdSense** — 访问量起来后挂广告，修改 `config.json` 中 `ads.enabled: true`
2. **亚马逊联盟** — 文章里嵌入商品链接
3. **推广软文** — 接受付费投稿
4. **卖站** — 站点有流量后有买家收购（通常按月收入 x20-30 倍估值）

## 配置说明

编辑 `config.json`：

- `topics` — 文章主题列表
- `content.posts_per_run` — 每次生成数量
- `ads` — 广告位配置
- `build.posts_per_page` — 每页文章数
