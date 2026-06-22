#!/usr/bin/env python3
"""
静态站点构建器 — 把 content/*.json 渲染成完整的静态 HTML 网站
用法:
    python build.py              # 构建站点
    python build.py --serve       # 构建并启动本地预览服务器
"""

import os, sys, json, re, shutil
from datetime import datetime
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent
CONTENT_DIR = ROOT / "content"
TEMPLATES_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "output"
CONFIG_PATH = ROOT / "config.json"

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("❌ 需要安装 jinja2: pip install jinja2")
    sys.exit(1)

try:
    import markdown
except ImportError:
    print("❌ 需要安装 markdown: pip install markdown")
    sys.exit(1)

# ---- Jinja2 环境 ----
env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_articles():
    """加载所有文章，按日期倒序"""
    articles = []
    if CONTENT_DIR.exists():
        for fpath in sorted(CONTENT_DIR.glob("*.json"), reverse=True):
            with open(fpath, "r", encoding="utf-8") as f:
                articles.append(json.load(f))
    articles.sort(key=lambda a: a.get("date", ""), reverse=True)
    return articles

def md_to_html(md_text: str) -> str:
    """Markdown 转 HTML，添加一些扩展处理"""
    html = markdown.markdown(
        md_text,
        extensions=["fenced_code", "codehilite", "tables", "nl2br"]
    )
    return html

def render_page(template_name: str, context: dict, output_path: Path):
    """渲染模板并写入文件"""
    template = env.get_template(template_name)
    html = template.render(**context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

def build_site():
    config = load_config()
    site = config["site"]
    build_cfg = config.get("build", {})
    posts_per_page = build_cfg.get("posts_per_page", 10)
    ad_enabled = config.get("ads", {}).get("enabled", False)

    articles = load_articles()
    print(f"📄 共加载 {len(articles)} 篇文章")

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)

    # 按主题分组
    topic_articles = defaultdict(list)
    for a in articles:
        topic_articles[a.get("topic", "未分类")].append(a)

    base_context = {
        "site_name": site["name"],
        "tagline": site["tagline"],
        "site_url": site["url"],
        "author": site.get("author", ""),
        "lang": site.get("language", "zh-CN"),
        "topics": list(topic_articles.keys()),
        "current_year": datetime.now().year,
        "ad_enabled": ad_enabled,
    }

    # ---- 生成文章详情页 ----
    post_dir = OUTPUT_DIR / "post"
    post_dir.mkdir(parents=True, exist_ok=True)
    for article in articles:
        ctx = {**base_context}
        ctx.update({
            "title": article["title"],
            "date": article["date"],
            "topic": article.get("topic", "未分类"),
            "excerpt": article.get("excerpt", ""),
            "content_html": md_to_html(article.get("content_md", "")),
            "tags": article.get("tags", []),
            "slug": article["slug"],
            "canonical_path": f"/post/{article['slug']}.html",
        })
        render_page("post.html", ctx, post_dir / f"{article['slug']}.html")
    print(f"✅ 已生成 {len(articles)} 篇文章页")

    # ---- 生成首页（分页）----
    total_pages = max(1, (len(articles) + posts_per_page - 1) // posts_per_page)
    for page in range(1, total_pages + 1):
        start = (page - 1) * posts_per_page
        end = start + posts_per_page
        page_posts = articles[start:end]

        page_file = "index.html" if page == 1 else f"page-{page}.html"
        page_prefix = "" if page == 1 else "page-"

        ctx = {**base_context}
        ctx.update({
            "posts": page_posts,
            "current_page": page,
            "total_pages": total_pages,
            "page_prefix": page_prefix,
            "canonical_path": f"/{page_file}" if page > 1 else "/",
        })
        render_page("index.html", ctx, OUTPUT_DIR / page_file)
    print(f"✅ 已生成 {total_pages} 个首页分页")

    # ---- 生成主题页 ----
    topic_dir = OUTPUT_DIR / "topic"
    topic_dir.mkdir(parents=True, exist_ok=True)
    for topic, t_articles in topic_articles.items():
        ctx = {**base_context}
        ctx.update({
            "topic": topic,
            "posts": t_articles,
            "canonical_path": f"/topic/{topic}.html",
        })
        render_page("topic.html", ctx, topic_dir / f"{topic}.html")
    print(f"✅ 已生成 {len(topic_articles)} 个主题页")

    # ---- 生成 RSS ----
    rss_items = []
    for a in articles[:20]:
        url = f"{site['url']}/post/{a['slug']}.html"
        rss_items.append(f"""    <item>
      <title><![CDATA[{a['title']}]]></title>
      <link>{url}</link>
      <description><![CDATA[{a.get('excerpt','')}]]></description>
      <pubDate>{a['date']}</pubDate>
      <guid>{url}</guid>
    </item>""")

    rss_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{site['name']}</title>
    <link>{site['url']}</link>
    <description>{site['tagline']}</description>
    <language>zh-CN</language>
    <lastBuildDate>{datetime.now().isoformat()}</lastBuildDate>
{chr(10).join(rss_items)}
  </channel>
</rss>"""
    with open(OUTPUT_DIR / "rss.xml", "w", encoding="utf-8") as f:
        f.write(rss_xml)
    print("✅ 已生成 RSS 订阅")

    # ---- 复制静态资源 ----
    static_src = ROOT / "static"
    if static_src.exists():
        static_dst = OUTPUT_DIR / "static"
        shutil.copytree(static_src, static_dst)

    # ---- 生成 sitemap ----
    sitemap_urls = [
        f"  <url><loc>{site['url']}/</loc><priority>1.0</priority></url>"
    ]
    for a in articles:
        sitemap_urls.append(
            f"  <url><loc>{site['url']}/post/{a['slug']}.html</loc><priority>0.8</priority></url>"
        )
    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(sitemap_urls)}
</urlset>"""
    with open(OUTPUT_DIR / "sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_xml)
    print("✅ 已生成 Sitemap")

    print(f"\n🎉 构建完成！站点目录: {OUTPUT_DIR}")
    print(f"   文章数: {len(articles)}")
    print(f"   主题数: {len(topic_articles)}")


def serve():
    """本地预览服务器"""
    import http.server
    import socketserver

    class MyHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(OUTPUT_DIR), **kwargs)

        def log_message(self, format, *args):
            print(f"  {args[0]}")

    port = 8080
    with socketserver.TCPServer(("", port), MyHandler) as httpd:
        print(f"\n🌐 本地预览: http://localhost:{port}")
        print("  按 Ctrl+C 停止")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 已停止")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="静态站点构建器")
    parser.add_argument("--serve", action="store_true", help="构建后启动本地预览")
    args = parser.parse_args()

    build_site()

    if args.serve:
        serve()
