#!/usr/bin/env python3
"""
AI 内容自动生成器
用法:
    python scripts/generate.py              # 生成一篇新文章
    python scripts/generate.py --topic 人工智能  # 指定主题
    python scripts/generate.py --count 5     # 批量生成
    python scripts/generate.py --dry-run     # 预览 prompt，不调用 API
    python scripts/generate.py --provider deepseek  # 使用 DeepSeek

环境变量:
    OPENAI_API_KEY     默认 provider 的 API 密钥
    OPENAI_BASE_URL    默认 provider 的 API 地址

DeepSeek:
    DEEPSEEK_API_KEY   DeepSeek API 密钥
    或直接 OPENAI_API_KEY + OPENAI_BASE_URL=https://api.deepseek.com
"""

import os, sys, json, re, time, argparse
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
CONFIG_PATH = ROOT / "config.json"

PROVIDERS = {
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "env_key": "DEEPSEEK_API_KEY",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "env_key": "OPENAI_API_KEY",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "model": "deepseek/deepseek-chat",
        "env_key": "OPENROUTER_API_KEY",
    },
}

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_openai_client(provider: str = "openai"):
    from openai import OpenAI

    provider_info = PROVIDERS.get(provider, PROVIDERS["openai"])

    base_url = os.environ.get("OPENAI_BASE_URL") or provider_info["base_url"]
    api_key = (
        os.environ.get(provider_info["env_key"])
        or os.environ.get("OPENAI_API_KEY")
    )

    if not api_key:
        print(f"❌ 请设置 {provider_info['env_key']} 或 OPENAI_API_KEY")
        sys.exit(1)

    return OpenAI(api_key=api_key, base_url=base_url), provider_info["model"]

def build_prompt(topic: str) -> str:
    return f"""你是一个专业中文科技博主。请写一篇高质量的博客文章。

【主题】{topic}
【要求】
1. 写一篇信息丰富的文章，字数 800-1200 字
2. 包含具体案例、数据或实际操作建议，拒绝空话
3. 用 Markdown 格式写作（标题用 ##，小标题用 ###）
4. 至少使用一个小标题分段
5. 语气亲切专业，面向普通读者
6. 如有代码示例，确保准确可运行

请按以下 JSON 格式返回（不要有其他内容）：
{{
  "title": "吸引人的中文标题（15-25字）",
  "excerpt": "文章摘要，100字以内，吸引点击",
  "content_md": "完整的 Markdown 正文",
  "tags": ["标签1", "标签2", "标签3"]
}}"""

def generate_article(client, topic: str, model: str) -> dict:
    prompt = build_prompt(topic)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个专业中文科技博主，擅长写通俗易懂、信息量大的科技文章。只返回合法 JSON。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=3000
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        title_m = re.search(r'"title"\s*:\s*"([^"]*)"', raw)
        excerpt_m = re.search(r'"excerpt"\s*:\s*"([^"]*)"', raw)
        content_m = re.search(r'"content_md"\s*:\s*"((?:[^"\\]|\\.)*)"', raw, re.DOTALL)
        if title_m:
            data = {
                "title": title_m.group(1),
                "excerpt": excerpt_m.group(1) if excerpt_m else "",
                "content_md": content_m.group(1) if content_m else raw,
                "tags": []
            }
        else:
            raise ValueError(f"无法解析 AI 返回内容: {raw[:200]}")
    return data

def sanitize_filename(s: str) -> str:
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[-\s]+', '-', s)
    return s.strip('-').lower()[:60]

def save_article(data: dict, topic: str):
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = sanitize_filename(data["title"])
    if not slug:
        slug = "article"
    slug = f"{date_str}-{slug}"

    article = {
        "title": data["title"],
        "slug": slug,
        "date": date_str,
        "topic": topic,
        "excerpt": data.get("excerpt", ""),
        "content_md": data.get("content_md", ""),
        "tags": data.get("tags", []),
    }

    filepath = CONTENT_DIR / f"{slug}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(article, f, ensure_ascii=False, indent=2)
    print(f"✅ 文章已保存: {filepath}")
    return article

def main():
    config = load_config()
    topics = config.get("topics", ["科技数码"])

    parser = argparse.ArgumentParser(description="AI 内容自动生成器")
    parser.add_argument("--topic", type=str, help="指定文章主题")
    parser.add_argument("--count", type=int, default=1, help="批量生成数量")
    parser.add_argument("--dry-run", action="store_true", help="只显示 prompt，不调用 API")
    parser.add_argument("--provider", type=str, default="openai",
                        choices=list(PROVIDERS.keys()), help="AI 服务商")
    args = parser.parse_args()

    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        t = args.topic or topics[0]
        print("=" * 60)
        print(f"Provider: {args.provider}")
        print(f"主题: {t}")
        print("=" * 60)
        print(build_prompt(t))
        return

    client, model = get_openai_client(args.provider)
    print(f"🔌 使用 {args.provider} / {model}")

    for i in range(args.count):
        topic = args.topic if args.topic else topics[i % len(topics)]
        print(f"\n🤖 正在生成第 {i+1}/{args.count} 篇: 【{topic}】")

        try:
            data = generate_article(client, topic, model)
            article = save_article(data, topic)
            print(f"   标题: {article['title']}")
            print(f"   标签: {', '.join(article['tags'])}")
        except Exception as e:
            print(f"❌ 生成失败: {e}")
            if args.count > 1:
                time.sleep(2)
                continue
            else:
                sys.exit(1)

        if i < args.count - 1:
            time.sleep(1)

    print(f"\n🎉 完成！共生成 {args.count} 篇文章")

if __name__ == "__main__":
    main()
