#!/usr/bin/env python3
"""Check one built blog post. Usage: check_post.py SITE_DIR YEAR/SLUG BIBKEY"""
import html
import os
import re
import sys


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    site, path, bibkey = sys.argv[1:]
    page = os.path.join(site, "blog", path, "index.html")
    ok = True

    def check(cond, label):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + label)
        ok = ok and cond

    check(os.path.isfile(page), f"page exists: {page}")
    if not os.path.isfile(page):
        return 1
    t = open(page, encoding="utf-8").read()

    check(not re.search(r"\{%|\{\{", t), "no leftover Liquid tags")
    check("tex-mml-chtml" in t, "MathJax script present")
    check("<h2>References</h2>" in t, "References heading present")
    check(bibkey in t, f"bibliography entry {bibkey} present")

    art = re.search(r'<div id="markdown-content">(.*?)</article>', t, re.S)
    body = art.group(1) if art else ""
    text = html.unescape(re.sub(r"<[^>]+>", " ", body))
    words = len(re.findall(r"\b\w+\b", text))
    check(900 <= words <= 1900, f"body word count {words} in 900..1900")

    imgs = re.findall(r'<img[^>]+src="([^"]+)"', body)
    figs = [i for i in imgs if "/assets/img/blog/" in i]
    check(4 <= len(figs) <= 6, f"figure count {len(figs)} in 4..6")
    for src in figs:
        f = os.path.join(site, src.lstrip("/"))
        check(os.path.isfile(f), f"figure file exists: {src}")
    caps = body.count('class="caption"')
    check(caps == len(figs), f"caption count {caps} equals figure count {len(figs)}")

    check(not re.search(r'class="caption">[^<]*\$\$', body), "no $$ math inside captions")
    check(len(re.findall(r"<h2[^>]*>", body)) >= 3, "at least three h2 sections")
    check("arxiv.org/abs/" in body, "arXiv link in body")
    check(not re.search(r"—", text), "no em-dashes")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
