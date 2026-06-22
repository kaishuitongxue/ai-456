#!/usr/bin/env python3
"""
一键全流程：生成内容 → 构建站点 → （可选）部署
用法:
    python pipeline.py              # 生成一篇 + 构建
    python pipeline.py --count 3    # 批量生成后构建
    python pipeline.py --deploy     # 生成 + 构建 + 推送部署
"""

import os, sys, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def run(cmd, desc=""):
    label = f"▶ {desc}" if desc else f"▶ {cmd}"
    print(f"\n{'='*50}")
    print(label)
    print("=" * 50)
    result = subprocess.run(cmd, shell=True, cwd=str(ROOT))
    if result.returncode != 0:
        print(f"❌ 步骤失败: {desc or cmd}")
        sys.exit(1)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="自动内容站一键流水线")
    parser.add_argument("--count", type=int, default=1, help="生成文章数量")
    parser.add_argument("--deploy", action="store_true", help="构建后执行部署")
    parser.add_argument("--skip-generate", action="store_true", help="跳过内容生成")
    parser.add_argument("--serve", action="store_true", help="构建后启动预览")
    args = parser.parse_args()

    if not args.skip_generate:
        run(f"python scripts/generate.py --count {args.count}", "AI 内容生成")

    run("python build.py", "静态站点构建")

    if args.deploy:
        run("bash scripts/deploy.sh", "部署到服务器")

    if args.serve:
        from build import serve
        serve()

    print("\n🎉 流水线完成！")

if __name__ == "__main__":
    main()
