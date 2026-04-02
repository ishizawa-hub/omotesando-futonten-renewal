#!/usr/bin/env python3
"""
レンタル商品ページに、対応する通常商品の画像を追加するスクリプト。
- rental-ccd → CCD冬用の画像
- rental-premium → Premium RDS冬用の画像
- trial → CCD冬用の画像（トライアルはCCD商品）
"""
import sys
import os
import re

sys.stdout.reconfigure(encoding='utf-8')

SITE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'site-a')

# 各レンタルページの設定
RENTAL_CONFIG = {
    'trial': {
        'path': os.path.join(SITE_DIR, 'products', 'service', 'trial', 'index.html'),
        'alt_prefix': '本掛け布団 1week トライアル',
        'images': [
            '../../../images/products/semidouble_720x610.webp',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/single_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/double_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/bedsetside_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/front_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/compact_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/color_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2015/06/1102_0983-Edit.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2022/02/cleancycledown.jpg',
        ],
    },
    'rental-ccd': {
        'path': os.path.join(SITE_DIR, 'products', 'service', 'rental-ccd', 'index.html'),
        'alt_prefix': '掛け布団マンスリーレンタル／CCD',
        'images': [
            '../../../images/products/rental-ccd/rental-ccd01.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/single_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/double_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/queen_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/bedsetside_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/front_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/compact_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/color_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2015/06/1102_0983-Edit.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2022/02/cleancycledown.jpg',
        ],
    },
    'rental-premium': {
        'path': os.path.join(SITE_DIR, 'products', 'service', 'rental-premium', 'index.html'),
        'alt_prefix': '掛け布団マンスリーレンタル／プレミアムマザーグース',
        'images': [
            '../../../images/products/monthly_lease/monthly_lease01.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/single_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/double_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/queen_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/bedset_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/bedsetside_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/front_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/compact_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2018/08/color_720x610.jpg',
            'https://omotesando-futonten.com/wp/wp-content/uploads/2015/06/1102_0983-Edit.jpg',
        ],
    },
}

modified = 0

for name, config in RENTAL_CONFIG.items():
    fpath = config['path']
    if not os.path.exists(fpath):
        print(f'[SKIP] {name}: ファイルが存在しません')
        continue

    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    alt = config['alt_prefix']
    images = config['images']

    # サムネイルHTML生成
    thumbs_html = ''
    for i, img_url in enumerate(images):
        active = ' active' if i == 0 else ''
        thumbs_html += f'      <div class="gallery-thumb{active}" data-index="{i}"><img src="{img_url}" alt="{alt} {i+1}" loading="lazy"></div>\n'

    # スライドHTML生成
    slides_html = ''
    for i, img_url in enumerate(images):
        slides_html += f'          <div class="swiper-slide"><img src="{img_url}" alt="{alt} {i+1}" loading="lazy"></div>\n'

    # 既存のサムネイル部分を置換
    thumb_pattern = re.compile(
        r'(<div class="gallery-thumbs">)\s*\n(.*?)(</div>\s*\n\s*<div class="gallery-main">)',
        re.DOTALL
    )
    match = thumb_pattern.search(content)
    if match:
        new_thumbs = match.group(1) + '\n' + thumbs_html + '    ' + match.group(3)
        content = content[:match.start()] + new_thumbs + content[match.end():]
    else:
        print(f'[WARN] {name}: サムネイル部分が見つかりません')
        continue

    # 既存のスライド部分を置換
    slide_pattern = re.compile(
        r'(<div class="swiper-wrapper">)\s*\n(.*?)(</div>\s*\n\s*</div>\s*\n\s*</div>\s*\n\s*</div>)',
        re.DOTALL
    )
    match = slide_pattern.search(content)
    if match:
        new_slides = match.group(1) + '\n' + slides_html + '        ' + match.group(3)
        content = content[:match.start()] + new_slides + content[match.end():]
    else:
        print(f'[WARN] {name}: スライド部分が見つかりません')
        continue

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'[OK] {name}: {len(images)}枚の画像を設定')
    modified += 1

print(f'\n完了: {modified}件修正')
