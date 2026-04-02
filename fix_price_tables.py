#!/usr/bin/env python3
"""掛け布団の価格表テーブル内の「カバーなし」価格を修正"""
import re
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = r"C:\Users\ishiz\omotesando-futonten-renewal\site-a\products\comforter"

# サイズ名マッピング（テーブル内の日本語名 -> コード）
SIZE_MAP = {
    "シングル": "S",
    "セミダブル": "SD",
    "ダブル": "D",
    "クイーン": "Q",
    "キング": "K",
}

# 全サイズの正しい価格（購入ボタン用と同じデータ、S/Kも含む）
ALL_PRICES = {
    "ccd-winter": {"S": 53800, "SD": 53800, "D": 73800, "Q": 83800, "K": 93800},  # S/K already correct
    "ccd-spring": {"S": 42800, "SD": 50800, "D": 58800, "Q": 66800, "K": 74800},
    "ccd-summer": {"S": 27800, "SD": 32800, "D": 36800, "Q": 42800, "K": 48800},
    "flower-winter": {"S": 35800, "SD": 41800, "D": 47800, "Q": 53800, "K": 59800},
    "flower-spring": {"S": 30800, "SD": 35800, "D": 40800, "Q": 45800, "K": 50800},
    "flower-summer": {"S": 20800, "SD": 23800, "D": 26800, "Q": 29800, "K": 32800},
    "premium-rds-winter": {"S": 198000, "SD": 228000, "D": 258000, "Q": 288000, "K": 318000},
    "premium-rds-spring": {"S": 158000, "SD": 183000, "D": 208000, "Q": 233000, "K": 258000},
    "premium-rds-summer": {"S": 78000, "SD": 91000, "D": 104000, "Q": 117000, "K": 128000},
    "rds-goose-winter": {"S": 88000, "SD": 106000, "D": 124000, "Q": 142000, "K": 158000},
    "rds-goose-spring": {"S": 68000, "SD": 81000, "D": 94000, "Q": 107000, "K": 118000},
    "rds-goose-summer": {"S": 38800, "SD": 45800, "D": 52800, "Q": 59800, "K": 66800},
}

# カバー追加料金（本番: 一部¥14,000、リニューアルは¥13,800で統一 - ¥13,800のままにする）
COVER_ADDON = 13800

def fix_price_table(slug):
    filepath = os.path.join(BASE, slug, "index.html")
    if not os.path.exists(filepath):
        print(f"  SKIP: not found")
        return

    prices = ALL_PRICES.get(slug)
    if not prices:
        print(f"  SKIP: no price data")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    changes = 0

    for jp_name, size_code in SIZE_MAP.items():
        correct_price = prices.get(size_code)
        if correct_price is None:
            continue

        formatted = f"¥{correct_price:,}"
        cover_price = correct_price + COVER_ADDON
        formatted_cover = f"¥{cover_price:,}"

        # Match: <tr><td>セミダブル</td><td>170×210cm</td><td>X.Xkg</td><td>¥XX,XXX</td><td>¥XX,XXX</td></tr>
        pattern = (
            rf'(<tr><td>{jp_name}</td>'
            rf'<td>[^<]*</td>'   # dimensions
            rf'<td>[^<]*</td>'   # fill weight
            rf'<td>)(¥[\d,]+)(</td>'   # price without cover
            rf'<td>)(¥[\d,]+)(</td></tr>)'  # price with cover
        )

        def make_replacer(sz, fp, fcp):
            def replacer(m):
                nonlocal changes
                old_price = m.group(2)
                old_cover = m.group(4)
                new_str = m.group(0)
                if old_price != fp:
                    changes += 1
                    print(f"  {sz} table: {old_price} -> {fp}")
                    new_str = m.group(1) + fp + m.group(3) + fcp + m.group(5)
                elif old_cover != fcp:
                    changes += 1
                    print(f"  {sz} cover: {old_cover} -> {fcp}")
                    new_str = m.group(1) + fp + m.group(3) + fcp + m.group(5)
                return new_str
            return replacer

        content = re.sub(pattern, make_replacer(size_code, formatted, formatted_cover), content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  -> {changes} table changes saved")
    else:
        print(f"  -> no table changes needed")


if __name__ == "__main__":
    print("=== Price Table Fixes ===\n")
    for slug in sorted(ALL_PRICES.keys()):
        print(f"[{slug}]")
        fix_price_table(slug)
        print()
    print("Done!")
