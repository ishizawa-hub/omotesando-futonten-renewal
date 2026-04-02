#!/usr/bin/env python3
"""
ギフト複数送り先JSの挿入位置を修正。
カートクリックハンドラ内部ではなく、DOMContentLoaded直後に移動。
"""
import sys
import os
import re
import glob

sys.stdout.reconfigure(encoding='utf-8')

SITE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'site-a')

# 移動対象のJSブロック（先頭と末尾で特定）
JS_START = '    // ギフト複数送り先対応\n    function giftFormHtml'
JS_END = "    if (giftToggle && giftToggle.checked) updateGiftForms();\n"

pattern = os.path.join(SITE_DIR, 'products', '**', 'index.html')
files = glob.glob(pattern, recursive=True)

modified = 0

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'giftDestContainer' not in content:
        continue
    if JS_START not in content:
        continue

    # JSブロックを抽出
    start_idx = content.index(JS_START)
    end_marker_idx = content.index(JS_END, start_idx)
    end_idx = end_marker_idx + len(JS_END)
    js_block = content[start_idx:end_idx]

    # 元の位置から削除
    content = content[:start_idx] + content[end_idx:]

    # DOMContentLoaded内のupdateBadge();の直後に挿入
    insert_marker = "    updateBadge();\n    var cartBtn"
    if insert_marker in content:
        content = content.replace(
            insert_marker,
            "    updateBadge();\n\n" + js_block + "\n    var cartBtn"
        )
    else:
        # フォールバック: document.addEventListener('DOMContentLoaded',function(){ の直後
        marker2 = "  document.addEventListener('DOMContentLoaded',function(){\n    updateBadge();"
        if marker2 in content:
            content = content.replace(
                marker2,
                marker2 + "\n\n" + js_block
            )
        else:
            dirname = os.path.basename(os.path.dirname(fpath))
            print(f'[SKIP] {dirname}: 挿入位置が見つかりません')
            continue

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)

    dirname = os.path.basename(os.path.dirname(fpath))
    print(f'[OK] {dirname}')
    modified += 1

print(f'\n完了: {modified}件修正')
