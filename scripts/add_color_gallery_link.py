#!/usr/bin/env python3
"""
全商品ページにカラー選択→ギャラリー連動機能を追加するスクリプト。
- カラー変更時にギャラリーを先頭スライドに戻す
- 選択カラーのインジケーターをギャラリー上に表示
- data-images-{color} が gallery に設定されていれば画像を差し替える
"""
import sys
import os
import re
import glob

sys.stdout.reconfigure(encoding='utf-8')

SITE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'site-a')

# カラーセレクターがあるページを探す
pattern = os.path.join(SITE_DIR, 'products', '**', 'index.html')
files = glob.glob(pattern, recursive=True)

# カラー連動用CSS
COLOR_LINK_CSS = """
/* Color-Gallery Link */
.gallery{position:relative}
.color-indicator{position:absolute;top:12px;right:12px;z-index:10;display:flex;align-items:center;gap:6px;background:rgba(45,45,45,0.85);backdrop-filter:blur(6px);padding:6px 12px;border-radius:2px;font-size:11px;font-weight:600;letter-spacing:0.08em;color:#fff;opacity:0;transition:opacity 0.4s;pointer-events:none}
.color-indicator.show{opacity:1}
.color-indicator-dot{width:14px;height:14px;border-radius:50%;border:1.5px solid rgba(255,255,255,0.5);flex-shrink:0}
"""

# カラー連動用JS（既存のcolorクリックハンドラを拡張）
COLOR_LINK_JS = """
  // カラー選択→ギャラリー連動
  (function(){
    var gallery=document.querySelector('.gallery');
    if(!gallery)return;
    // インジケーター要素を追加
    var indicator=document.createElement('div');
    indicator.className='color-indicator';
    indicator.innerHTML='<span class="color-indicator-dot"></span><span class="color-indicator-label"></span>';
    gallery.appendChild(indicator);
    var indTimer=null;

    document.querySelectorAll('.purchase-color').forEach(function(btn){
      btn.addEventListener('click',function(){
        var color=this.dataset.color;
        // ギャラリーを先頭に戻す
        if(typeof swiper!=='undefined') swiper.slideTo(0,300);
        // インジケーター表示
        var dot=indicator.querySelector('.color-indicator-dot');
        var label=indicator.querySelector('.color-indicator-label');
        var swatch=this.querySelector('.purchase-color-swatch');
        if(dot&&swatch){
          dot.style.background=swatch.style.background||swatch.style.backgroundColor;
          if(swatch.style.border) dot.style.border=swatch.style.border;
        }
        var colorLabel=this.querySelector('.purchase-color-label');
        if(label&&colorLabel) label.textContent=colorLabel.textContent;
        indicator.classList.add('show');
        clearTimeout(indTimer);
        indTimer=setTimeout(function(){indicator.classList.remove('show')},2000);

        // data-images-{color} がある場合は画像差し替え
        var key='images'+color.charAt(0).toUpperCase()+color.slice(1);
        var imgData=gallery.dataset[key];
        if(imgData){
          try{
            var imgs=JSON.parse(imgData);
            document.querySelectorAll('#mainSwiper .swiper-slide img').forEach(function(img,i){
              if(imgs[i]) img.src=imgs[i];
            });
            document.querySelectorAll('.gallery-thumb img').forEach(function(img,i){
              if(imgs[i]) img.src=imgs[i];
            });
          }catch(e){}
        }
      });
    });
  })();
"""

modified = 0
skipped = 0

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # カラーセレクターがあるページのみ
    if 'purchase-color' not in content or 'data-color=' not in content:
        continue

    # 既に適用済みならスキップ
    if 'color-indicator' in content:
        skipped += 1
        continue

    # 1. CSSを追加（</style>の直前に挿入。最初のstyleタグの閉じを見つける）
    # 最後の</style>の前に追加
    style_pos = content.rfind('</style>')
    if style_pos == -1:
        print(f'[SKIP] {fpath}: </style> not found')
        continue

    content = content[:style_pos] + COLOR_LINK_CSS + content[style_pos:]

    # 2. JSを追加（既存のカラークリックハンドラの後に挿入）
    # swiper初期化のIIFEの閉じの直前に挿入
    # パターン: })(); の後、hamburgerの前
    # 実際は最初の (function(){ ... })(); ブロックの閉じを探す

    # 方法: "var fc=document.querySelector('.purchase-color')" の行の後に挿入
    fc_marker = "var fc=document.querySelector('.purchase-color');if(fc)fc.classList.add('active');"
    if fc_marker in content:
        content = content.replace(
            fc_marker,
            fc_marker + COLOR_LINK_JS
        )
    else:
        # フォールバック: </script>の最初の出現の前に挿入
        # cart.jsの後のscriptブロックを探す
        cart_script_end = content.find("})();\n(function(){var btn=document.getElementById('hamburgerBtn')")
        if cart_script_end > 0:
            content = content[:cart_script_end] + COLOR_LINK_JS + '\n' + content[cart_script_end:]
        else:
            print(f'[WARN] {fpath}: Could not find insertion point for JS')
            continue

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)

    rel = os.path.relpath(fpath, SITE_DIR)
    print(f'[OK] {rel}')
    modified += 1

print(f'\n完了: {modified}件修正, {skipped}件スキップ（適用済み）')
