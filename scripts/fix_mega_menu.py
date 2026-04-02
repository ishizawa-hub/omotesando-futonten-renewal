#!/usr/bin/env python3
"""
全ページのPRODUCTSメガメニューを修正:
1. 画像aspect-ratioを4/3に、パディング縮小で高さを低く
2. ALL ITEMカードを先頭に追加
3. メガメニューのpadding/gapを縮小
"""
import sys
import os
import re
import glob

sys.stdout.reconfigure(encoding='utf-8')

SITE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'site-a')

pattern = os.path.join(SITE_DIR, '**', 'index.html')
files = glob.glob(pattern, recursive=True)

modified = 0
skipped = 0

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'nav-mega' not in content:
        continue

    changed = False

    # Already processed (has ALL ITEM)
    if 'ALL ITEM' in content:
        # Still need CSS fixes if not done
        pass

    # 1. CSS: aspect-ratio 1/1 → 4/3, padding縮小
    if 'aspect-ratio:1/1' in content and 'nav-mega-card img' in content:
        content = content.replace(
            'nav-mega-card img{width:100%;aspect-ratio:1/1;object-fit:cover;display:block}',
            'nav-mega-card img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block}'
        )
        changed = True

    if 'padding:8px 4px 6px' in content and 'nav-mega-card-label' in content:
        content = content.replace(
            'padding:8px 4px 6px;font-family:\'DM Sans\',\'Noto Sans JP\',sans-serif;font-size:12px',
            'padding:6px 4px 4px;font-family:\'DM Sans\',\'Noto Sans JP\',sans-serif;font-size:11px'
        )
        changed = True

    if 'padding:0 4px 10px' in content and 'nav-mega-card-name' in content:
        content = content.replace(
            'padding:0 4px 10px;white-space:nowrap;font-family:\'Noto Sans JP\',sans-serif;font-size:12px',
            'padding:0 4px 6px;white-space:nowrap;font-family:\'Noto Sans JP\',sans-serif;font-size:11px'
        )
        changed = True

    # メガメニューpadding/gap縮小
    if 'padding:20px;z-index:100;display:grid' in content:
        content = content.replace(
            'padding:20px;z-index:100;display:grid;grid-template-columns:repeat(4,1fr);gap:12px',
            'padding:16px;z-index:100;display:grid;grid-template-columns:repeat(4,1fr);gap:10px'
        )
        changed = True

    # 2. ALL ITEMカード追加（未追加のページのみ）
    if 'ALL ITEM' not in content and '<div class="nav-mega">' in content:
        # 相対パスを特定（products/comforter/ccd-winter → ../../../）
        rel = os.path.relpath(fpath, SITE_DIR).replace('\\', '/')
        depth = rel.count('/')
        prefix = '../' * depth if depth > 0 else './'
        # index.htmlの場合は1つ減らす
        if rel.endswith('/index.html'):
            prefix = '../' * (depth - 0)  # depth already accounts for file

        # 実際のパスから判定
        # site-a直下 → ./products/, images/site/...
        # site-a/faq/ → ../products/, ../images/site/...
        # site-a/products/comforter/ccd-winter/ → ../../../products/, ../../../images/site/...
        dir_path = os.path.dirname(fpath)
        rel_dir = os.path.relpath(dir_path, SITE_DIR).replace('\\', '/')
        if rel_dir == '.':
            img_prefix = ''
            link_prefix = ''
        else:
            levels = len(rel_dir.split('/'))
            img_prefix = '../' * levels
            link_prefix = '../' * levels

        # 最初のnav-mega-cardの前にALL ITEMを挿入
        # パターン: comforter or SLEEP DOWN が最初のカードの場合
        patterns_to_try = [
            # ../images パターン
            (f'<div class="nav-mega">\n          <a href="{img_prefix}products/comforter/"',
             f'<div class="nav-mega">\n          <a href="{img_prefix}products/" class="nav-mega-card">\n            <img src="{img_prefix}images/site/futon_hero.jpg" alt="全商品" loading="lazy" style="background:#F7F6F3">\n            <span class="nav-mega-card-label">ALL ITEM</span>\n            <span class="nav-mega-card-name">全商品一覧</span>\n          </a>\n          <a href="{img_prefix}products/comforter/"'),
        ]

        for old, new in patterns_to_try:
            if old in content:
                content = content.replace(old, new)
                changed = True
                break
        else:
            # 汎用: nav-megaの直後の最初のリンクを検出
            mega_match = re.search(
                r'(<div class="nav-mega">\s*\n\s*)<a href="([^"]*products/comforter/)"',
                content
            )
            if mega_match:
                prefix_path = mega_match.group(2).replace('products/comforter/', '')
                all_item_card = (
                    f'<a href="{prefix_path}products/" class="nav-mega-card">\n'
                    f'            <img src="{prefix_path}images/site/futon_hero.jpg" alt="全商品" loading="lazy" style="background:#F7F6F3">\n'
                    f'            <span class="nav-mega-card-label">ALL ITEM</span>\n'
                    f'            <span class="nav-mega-card-name">全商品一覧</span>\n'
                    f'          </a>\n          '
                )
                insert_pos = mega_match.end(1)
                content = content[:insert_pos] + all_item_card + content[insert_pos:]
                changed = True

    if changed:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        rel = os.path.relpath(fpath, SITE_DIR)
        print(f'[OK] {rel}')
        modified += 1

print(f'\n完了: {modified}件修正')
