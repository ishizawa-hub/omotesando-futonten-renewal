#!/usr/bin/env python3
"""全ページのPC/スマホスクリーンショットを撮影するスクリプト"""

import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

SITE_ROOT = 'site-a'
BASE_URL = 'http://localhost:8080'
PROD_BASE = 'https://ishizawa-hub.github.io/omotesando-futonten-renewal/site-a'
OUT_DIR = 'screenshots'
SKIP_DIRS = {'admin', 'emails', 'account', 'cart', 'checkout', 'images', 'videos', 'js', 'css', 'fonts'}

# ページ一覧を生成
def get_pages():
    pages = []
    for root, dirs, files in os.walk(SITE_ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if not f.endswith('.html'):
                continue
            rel = os.path.relpath(os.path.join(root, f), SITE_ROOT).replace(os.sep, '/')

            # ページ名の生成
            if rel == 'index.html':
                name = 'TOP'
                url_path = ''
            elif rel.endswith('/index.html'):
                path_parts = rel.replace('/index.html', '').split('/')
                name = ' / '.join(p.replace('-', ' ').title() for p in path_parts)
                url_path = rel.replace('/index.html', '/')
            else:
                name = rel.replace('.html', '').replace('-', ' ').replace('/', ' / ').title()
                url_path = rel

            # ファイル名用のsafe name
            safe = rel.replace('/', '_').replace('.html', '')

            pages.append({
                'name': name,
                'prod_url': f'{PROD_BASE}/{url_path}',
                'local_url': f'{BASE_URL}/{rel}',
                'safe': safe,
            })

    # ソート: TOPを先頭に
    pages.sort(key=lambda p: ('0' if p['name'] == 'TOP' else p['name']))
    return pages


def capture_all(pages, viewport, label):
    out = os.path.join(OUT_DIR, label)
    os.makedirs(out, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport=viewport,
            device_scale_factor=1,
        )
        page = context.new_page()

        total = len(pages)
        for i, pg in enumerate(pages):
            fname = f"{pg['safe']}.jpg"
            fpath = os.path.join(out, fname)

            # すでにキャプチャ済みならスキップ
            if os.path.exists(fpath):
                print(f"[{label}] ({i+1}/{total}) SKIP {pg['name']}")
                continue

            try:
                page.goto(pg['local_url'], wait_until='networkidle', timeout=15000)
                # 動画要素を非表示に（タイムアウト防止）
                page.evaluate("""
                    document.querySelectorAll('video').forEach(v => {
                        v.pause();
                        v.style.background = '#2D2D2D';
                    });
                """)
                time.sleep(0.5)
                page.screenshot(path=fpath, full_page=True, type='jpeg', quality=80)
                print(f"[{label}] ({i+1}/{total}) OK {pg['name']}")
            except Exception as e:
                print(f"[{label}] ({i+1}/{total}) ERR {pg['name']}: {e}")

        browser.close()


def main():
    pages = get_pages()
    print(f"Total pages: {len(pages)}")

    # ページリストを保存（PDF生成で使う）
    with open(os.path.join(OUT_DIR, 'pages.json'), 'w', encoding='utf-8') as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)

    # PC版 (1280x800)
    print("\n=== PC Screenshots ===")
    capture_all(pages, {'width': 1280, 'height': 800}, 'pc')

    # スマホ版 (375x812)
    print("\n=== Mobile Screenshots ===")
    capture_all(pages, {'width': 375, 'height': 812}, 'mobile')

    print("\nDone!")


if __name__ == '__main__':
    main()
