#!/usr/bin/env python3
"""把 Reddit 帖子的全量评论抓成结构化文本，用于更新社区知识库。

用法:
    python scripts/fetch_reddit_thread.py 1wtyglf --out _fetch/reddit_full.txt

说明:
  - 走 pullpush.io 的公开归档 API（单次上限 100 条，靠 before 游标翻页）。
  - 只读取、不写入任何 Reddit 数据；不需要 Reddit 账号或令牌。
  - 输出为缩进评论树，含评论 ID / 作者 / 时间 / score，便于人工核对与溯源。
"""
import argparse
import datetime
import html
import json
import sys
import time
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0"


def get(url):
    r = urllib.request.Request(url)
    r.add_header("User-Agent", UA)
    return json.loads(urllib.request.urlopen(r, timeout=60).read().decode())


def fetch_comments(link_id):
    seen, before = {}, None
    for _ in range(30):
        url = f"https://api.pullpush.io/reddit/search/comment/?link_id={link_id}&limit=100"
        if before:
            url += f"&before={before}"
        data = get(url).get("data", [])
        if not data:
            break
        new = sum(1 for x in data if x["id"] not in seen)
        for x in data:
            seen.setdefault(x["id"], x)
        before = int(min(x["created_utc"] for x in data))
        if new == 0:
            break
        time.sleep(1)
    return sorted(seen.values(), key=lambda x: x["created_utc"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("link_id")
    ap.add_argument("--out", default="reddit_thread.txt")
    args = ap.parse_args()

    comments = fetch_comments(args.link_id)
    subs = get(f"https://api.pullpush.io/reddit/search/submission/?ids={args.link_id}")["data"]

    byid = {c["id"]: c for c in comments}
    kids = {}
    for c in comments:
        p = c["parent_id"]
        if p.startswith("t1_") and p[3:] in byid:
            kids.setdefault(p[3:], []).append(c)

    def dt(u):
        return datetime.datetime.fromtimestamp(u, datetime.UTC).strftime("%Y-%m-%d %H:%M")

    out = []
    for s in subs:
        out.append(f"# {s.get('title')}")
        out.append(f"author={s.get('author')} · {dt(s['created_utc'])} · score={s.get('score')}")
        out.append(f"https://reddit.com{s.get('permalink', '')}")
        out.append("")
        out.append(html.unescape(s.get("selftext") or ""))
        out.append("")

    def walk(c, depth):
        body = html.unescape(c.get("body") or "").replace("\n", "\n" + "  " * (depth + 1)).strip()
        out.append(f"{'  ' * depth}[{c['id']}] {c['author']} · {dt(c['created_utc'])} · score={c.get('score')}")
        out.append(f"{'  ' * depth}{body}")
        out.append("")
        for k in kids.get(c["id"], []):
            walk(k, depth + 1)

    for c in comments:
        if c["parent_id"].startswith("t3_"):
            walk(c, 0)

    open(args.out, "w", encoding="utf-8").write("\n".join(out))
    print(f"帖子 {len(subs)} 条, 评论 {len(comments)} 条 -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
