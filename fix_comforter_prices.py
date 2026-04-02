#!/usr/bin/env python3
"""掛け布団12商品の価格・充填量を本番サイトの値に修正するスクリプト"""
import re
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = r"C:\Users\ishiz\omotesando-futonten-renewal\site-a\products\comforter"

# 本番サイトの正しい価格データ (slug -> {size: price})
CORRECT_PRICES = {
    "ccd-spring": {"SD": 50800, "D": 58800, "Q": 66800},
    "ccd-summer": {"SD": 32800, "D": 36800},
    "flower-winter": {"SD": 41800, "D": 47800, "Q": 53800, "K": 59800},
    "flower-spring": {"SD": 35800, "D": 40800, "Q": 45800, "K": 50800},
    "flower-summer": {"SD": 23800, "D": 26800, "Q": 29800, "K": 32800},
    "premium-rds-winter": {"SD": 228000, "D": 258000, "Q": 288000},
    "premium-rds-spring": {"SD": 183000, "D": 208000, "Q": 233000},
    "premium-rds-summer": {"SD": 91000, "D": 104000, "Q": 117000},
    "rds-goose-winter": {"SD": 106000, "D": 124000, "Q": 142000},
    "rds-goose-spring": {"SD": 81000, "D": 94000, "Q": 107000},
    "rds-goose-summer": {"SD": 45800, "D": 52800, "Q": 59800},
}

# 本番サイトの正しい充填量
CORRECT_FILL = {
    "ccd-spring": {"S": "0.85", "SD": "0.96", "D": "1.08", "Q": "1.19", "K": "1.30"},
    "flower-spring": {"S": "0.85", "SD": "0.96", "D": "1.08", "Q": "1.19", "K": "1.30"},
    "rds-goose-spring": {"S": "0.85", "SD": "0.96", "D": "1.08", "Q": "1.19", "K": "1.30"},
    "premium-rds-spring": {"S": "0.80", "SD": "0.88", "D": "0.97", "Q": "1.05", "K": "1.19"},
    "ccd-summer": {"S": "0.25", "SD": "0.28", "D": "0.32", "Q": "0.35", "K": "0.38"},
    "rds-goose-summer": {"S": "0.25", "SD": "0.28", "D": "0.32", "Q": "0.35", "K": "0.38"},
    "flower-summer": {"S": "0.25", "SD": "0.28", "D": "0.32", "Q": "0.35", "K": "0.38"},
    "premium-rds-summer": {"S": "0.23", "SD": "0.25", "D": "0.28", "Q": "0.32", "K": "0.35"},
}


def fix_prices(slug, size_prices):
    """data-price属性と表示テキストを修正"""
    filepath = os.path.join(BASE, slug, "index.html")
    if not os.path.exists(filepath):
        print(f"  SKIP: {filepath} not found")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    changes = 0

    for size, correct_price in size_prices.items():
        formatted_correct = f"\u00a5{correct_price:,}"  # ¥XX,XXX

        # Fix purchase button: <button class="purchase-size" data-price="52800"><span>SD</span><span class="purchase-size-price">¥52,800</span></button>
        pattern = (
            rf'(<button\s+class="purchase-size"\s+data-price=")(\d+)'
            rf'("><span>{size}</span><span class="purchase-size-price">)'
            rf'([^<]+)'
            rf'(</span></button>)'
        )

        def make_replacer(sz, cp, fc):
            def replacer(m):
                nonlocal changes
                old_price = int(m.group(2))
                old_display = m.group(4)
                if old_price != cp:
                    changes += 1
                    print(f"  {sz}: data-price {old_price} -> {cp}, display {old_display} -> {fc}")
                    return m.group(1) + str(cp) + m.group(3) + fc + m.group(5)
                return m.group(0)
            return replacer

        content = re.sub(pattern, make_replacer(size, correct_price, formatted_correct), content)

        # Fix price table: <td>&yen;XX,XXX</td> in rows containing the size
        # Pattern: row like <tr><td>SD</td><td>&yen;52,800</td>...
        yen_correct = f"&yen;{correct_price:,}"
        table_pattern = rf'(<tr>\s*<td>{size}</td>\s*<td>)(&yen;[\d,]+)(</td>)'
        def table_replacer(m):
            nonlocal changes
            old = m.group(2)
            if old != yen_correct:
                changes += 1
                print(f"  {size} table: {old} -> {yen_correct}")
                return m.group(1) + yen_correct + m.group(3)
            return m.group(0)
        content = re.sub(table_pattern, table_replacer, content)

        # Also try without <tr> wrapper
        table_pattern2 = rf'(<td>\s*{size}\s*</td>\s*<td[^>]*>)(&yen;[\d,]+)'
        def table_replacer2(m):
            nonlocal changes
            old = m.group(2)
            if old != yen_correct:
                changes += 1
                print(f"  {size} table2: {old} -> {yen_correct}")
                return m.group(1) + yen_correct
            return m.group(0)
        content = re.sub(table_pattern2, table_replacer2, content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  -> {changes} price changes saved")
        return True
    else:
        print(f"  -> no price changes needed")
        return False


def fix_fill_weights(slug, size_weights):
    """充填量を修正"""
    filepath = os.path.join(BASE, slug, "index.html")
    if not os.path.exists(filepath):
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    changes = 0

    # Fix spec table fill weight for S size
    s_weight = size_weights.get("S", "")
    if s_weight:
        # Pattern: 充填量 ... S or シングル ... X.XXkg
        pattern = r'(充填量.*?(?:S|シングル)[^0-9]*?)(\d+\.\d+)\s*kg'
        def replace_spec(m):
            nonlocal changes
            old = m.group(2)
            if old != s_weight:
                changes += 1
                print(f"  spec S: {old}kg -> {s_weight}kg")
                return m.group(1) + s_weight + "kg"
            return m.group(0)
        content = re.sub(pattern, replace_spec, content, count=1)

    # Fix price table fill weights
    for size, correct_weight in size_weights.items():
        # In price table rows: <td>S</td><td>..price..</td><td>..price..</td><td>X.XXkg</td>
        # or <td>S</td><td>..price..</td><td>X.XXkg</td>
        pattern = rf'(<td>\s*{size}\s*</td>(?:\s*<td[^>]*>[^<]*</td>)*?\s*<td[^>]*>\s*)(\d+\.\d+)(kg\s*</td>)'
        def make_fill_replacer(sz, cw):
            def replacer(m):
                nonlocal changes
                old = m.group(2)
                if old != cw:
                    changes += 1
                    print(f"  table {sz}: {old}kg -> {cw}kg")
                    return m.group(1) + cw + m.group(3)
                return m.group(0)
            return replacer
        content = re.sub(pattern, make_fill_replacer(size, correct_weight), content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  -> {changes} fill changes saved")
        return True
    else:
        print(f"  -> no fill changes needed")
        return False


if __name__ == "__main__":
    print("=== Price Fixes ===\n")
    total = 0
    for slug, prices in CORRECT_PRICES.items():
        print(f"[{slug}]")
        if fix_prices(slug, prices):
            total += 1
        print()

    print(f"\n=== Fill Weight Fixes ===\n")
    for slug, weights in CORRECT_FILL.items():
        print(f"[{slug}]")
        if fix_fill_weights(slug, weights):
            total += 1
        print()

    print(f"\nTotal files modified: {total}")
