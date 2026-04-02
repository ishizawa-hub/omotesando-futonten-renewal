#!/usr/bin/env python3
"""
全ページのフッターをTOPページのフッターに統一する。
相対パスは各ページのディレクトリ深さに応じて調整。
"""
import sys
import os
import re
import glob

sys.stdout.reconfigure(encoding='utf-8')

SITE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'site-a')

# TOPページのフッターHTML（相対パスはプレースホルダー {P} で表現）
FOOTER_TEMPLATE = '''<footer class="footer">
  <div class="footer-inner">
    <div class="footer-brand">
      <div class="footer-logo"><img src="{P}images/logo.svg" alt="表参道布団店。"></div>
      <p class="footer-desc">眠りの質を、人生の質へ。<br>Clean Cycle Down</p>
      <div class="footer-sns" style="display:flex;gap:16px;margin-top:20px">
        <a href="https://www.instagram.com/omotesando_futonten/" target="_blank" rel="noopener" aria-label="Instagram" style="color:rgba(255,255,255,0.5);transition:color 0.3s" onmouseover="this.style.color='#C9A96E'" onmouseout="this.style.color='rgba(255,255,255,0.5)'"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg></a>
        <a href="https://lin.ee/omotesandofutonten" target="_blank" rel="noopener" aria-label="LINE" style="color:rgba(255,255,255,0.5);transition:color 0.3s" onmouseover="this.style.color='#C9A96E'" onmouseout="this.style.color='rgba(255,255,255,0.5)'"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M19.365 9.863c.349 0 .63.285.63.631 0 .345-.281.63-.63.63H17.61v1.125h1.755c.349 0 .63.283.63.63 0 .344-.281.629-.63.629h-2.386c-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.627-.63h2.386c.349 0 .63.285.63.63 0 .349-.281.63-.63.63H17.61v1.125h1.755zm-3.855 3.016c0 .27-.174.51-.432.596-.064.021-.133.031-.199.031-.211 0-.391-.09-.51-.25l-2.443-3.317v2.94c0 .344-.279.629-.631.629-.346 0-.626-.285-.626-.629V8.108c0-.271.173-.51.43-.595.06-.023.136-.033.194-.033.195 0 .375.104.495.254l2.462 3.33V8.108c0-.345.282-.63.63-.63.345 0 .63.285.63.63v4.771zm-5.741 0c0 .344-.282.629-.631.629-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.627-.63.349 0 .631.285.631.63v4.771zm-2.466.629H4.917c-.345 0-.63-.285-.63-.629V8.108c0-.345.285-.63.63-.63.349 0 .63.285.63.63v4.141h1.756c.348 0 .629.283.629.63 0 .344-.281.629-.629.629M24 10.314C24 4.943 18.615.572 12 .572S0 4.943 0 10.314c0 4.811 4.27 8.842 10.035 9.608.391.082.923.258 1.058.59.12.301.079.766.038 1.08l-.164 1.02c-.045.301-.24 1.186 1.049.645 1.291-.539 6.916-4.078 9.436-6.975C23.176 14.393 24 12.458 24 10.314"/></svg></a>
      </div>
      <div class="footer-newsletter" style="margin-top:24px">
        <p style="font-size:13px;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;color:#C9A96E;margin-bottom:10px">NEWSLETTER</p>
        <p style="font-size:14px;color:rgba(255,255,255,0.4);margin-bottom:12px;line-height:1.6">新商品やキャンペーン情報をお届けします</p>
        <form onsubmit="event.preventDefault();var inp=this.querySelector('input'),btn=this.querySelector('button');var e=inp.value.trim().toLowerCase();if(!e)return;var a=JSON.parse(localStorage.getItem('oft_newsletter')||'[]');var dup=a.some(function(x){return x.toLowerCase()===e});var msg,col;if(dup){msg='\\u3053\\u306e\\u30e1\\u30fc\\u30eb\\u30a2\\u30c9\\u30ec\\u30b9\\u306f\\u65e2\\u306b\\u767b\\u9332\\u6e08\\u307f\\u3067\\u3059';col='#999'}else{a.push(e);localStorage.setItem('oft_newsletter',JSON.stringify(a));msg='\\u30e1\\u30eb\\u30de\\u30ac\\u767b\\u9332\\u304c\\u5b8c\\u4e86\\u3057\\u307e\\u3057\\u305f\\u3002\\u3042\\u308a\\u304c\\u3068\\u3046\\u3054\\u3056\\u3044\\u307e\\u3059\\uff01';col='#C9A96E'}btn.textContent='\\u767b\\u9332\\u5b8c\\u4e86 \\u2713';inp.value='';setTimeout(function(){btn.textContent='\\u767b\\u9332'},3000);var t=document.createElement('div');t.textContent=msg;t.style.cssText='position:fixed;bottom:32px;left:50%;transform:translateX(-50%);background:#1a1a1a;color:'+col+';padding:16px 32px;border-radius:8px;font-size:14px;z-index:99999;box-shadow:0 4px 24px rgba(0,0,0,0.4);border:1px solid '+col+';opacity:1;transition:opacity 0.5s';document.body.appendChild(t);setTimeout(function(){t.style.opacity='0'},2500);setTimeout(function(){t.remove()},3000)" style="display:flex;gap:0">
          <input type="email" placeholder="メールアドレス" required style="flex:1;padding:10px 14px;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);border-right:none;color:#fff;font-size:13px;outline:none;font-family:inherit;transition:border-color 0.3s" onfocus="this.style.borderColor='#C9A96E'" onblur="this.style.borderColor='rgba(255,255,255,0.15)'">
          <button type="submit" style="padding:10px 20px;background:#C9A96E;color:#fff;border:none;font-size:14px;font-weight:600;letter-spacing:0.08em;cursor:pointer;transition:background 0.3s;white-space:nowrap" onmouseover="this.style.background='#B8975A'" onmouseout="this.style.background='#C9A96E'">登録</button>
        </form>
      </div>
    </div>
    <div>
      <h4 class="footer-nav-title">PRODUCTS</h4>
      <nav class="footer-nav">
        <a href="{P}products/comforter/">掛け布団</a>
        <a href="{P}products/pillow/">枕</a>
        <a href="{P}products/bedding/">カバー・シーツ・寝具</a>
        <a href="{P}products/apparel/">アパレル</a>
        <a href="{P}products/collaboration/">コラボレーション</a>
        <a href="{P}products/baby/">ベビー</a>
        <a href="{P}products/service/">サービス</a>
      </nav>
    </div>
    <div>
      <h4 class="footer-nav-title">CONCEPT</h4>
      <nav class="footer-nav">
        <a href="{P}concept/">ブランドコンセプト</a>
        <a href="{P}concept/brand-story/">ブランドストーリー</a>
        <a href="{P}concept/clean-cycle-down/">Clean Cycle Down</a>
        <a href="{P}concept/material/">素材のこだわり</a>
      </nav>
      <h4 class="footer-nav-title" style="margin-top:28px">MAGAZINE</h4>
      <nav class="footer-nav">
        <a href="{P}magazine/">記事一覧</a>
        <a href="{P}down/">ダウンについて</a>
      </nav>
    </div>
    <div class="footer-col-last">
      <div>
        <h4 class="footer-nav-title">CONTACT</h4>
        <nav class="footer-nav">
          <a href="{P}about/">会社概要</a>
          <a href="{P}faq/">よくあるご質問</a>
          <a href="{P}contact/">お問い合わせ</a>
        </nav>
      </div>
      <div>
        <h4 class="footer-nav-title">ACCOUNT</h4>
        <nav class="footer-nav">
          <a href="{P}account/login/">ログイン</a>
          <a href="{P}account/register/">新規会員登録</a>
          <a href="{P}cart/">カート</a>
        </nav>
      </div>
    </div>
  </div>
  <div class="footer-bottom">
    <nav class="footer-legal">
      <a href="{P}order/">特定商取引法に基づく表記</a>
      <a href="{P}privacy-policy/">プライバシーポリシー</a>
      <a href="{P}terms/">利用規約</a>
      <a href="{P}shopping-guide/">ショッピングガイド</a>
    </nav>
    <p class="footer-copy">&copy; 2026 Omotesando Futon Ten. All rights reserved.</p>
  </div>
</footer>'''

# フッターCSS（必要なスタイルが欠落しているページ用）
FOOTER_CSS_REQUIRED = '.footer-col-last{display:grid;grid-template-columns:1.2fr 1fr;gap:24px}'
FOOTER_NAV_SUB_CSS = ".footer-nav-sub a{display:block;font-size:13px;color:rgba(255,255,255,0.35);padding:4px 0;letter-spacing:0.03em;transition:color 0.3s;text-decoration:none}\n.footer-nav-sub a:hover{color:#C9A96E}"

pattern = os.path.join(SITE_DIR, '**', 'index.html')
files = glob.glob(pattern, recursive=True)
# Also include admin.html etc at root
root_htmls = glob.glob(os.path.join(SITE_DIR, '*.html'))
files = list(set(files + root_htmls))

modified = 0
skipped = 0

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    if '<footer' not in content:
        continue

    # TOPページ自体はスキップ
    rel_path = os.path.relpath(fpath, SITE_DIR).replace('\\', '/')
    if rel_path == 'index.html':
        skipped += 1
        continue

    # 相対パスのプレフィックスを計算
    dir_path = os.path.dirname(fpath)
    rel_dir = os.path.relpath(dir_path, SITE_DIR).replace('\\', '/')
    if rel_dir == '.':
        prefix = './'
    else:
        levels = len(rel_dir.split('/'))
        prefix = '../' * levels

    # フッターHTMLを生成
    footer_html = FOOTER_TEMPLATE.replace('{P}', prefix)

    # 既存のフッターを置換
    footer_pattern = re.compile(
        r'<footer class="footer">.*?</footer>',
        re.DOTALL
    )
    match = footer_pattern.search(content)
    if not match:
        continue

    new_content = content[:match.start()] + footer_html + content[match.end():]

    # footer-col-last CSSが欠落していれば追加
    if 'footer-col-last' not in new_content.split('<footer')[0]:
        # CSSがない → .footer-bottomの前に追加
        if '.footer-bottom{' in new_content:
            new_content = new_content.replace(
                '.footer-bottom{',
                FOOTER_CSS_REQUIRED + '\n' + FOOTER_NAV_SUB_CSS + '\n.footer-bottom{',
                1
            )

    # footer-nav-sub CSSが欠落していれば追加
    if 'footer-nav-sub' not in new_content.split('<footer')[0]:
        if FOOTER_CSS_REQUIRED in new_content and FOOTER_NAV_SUB_CSS not in new_content:
            new_content = new_content.replace(
                FOOTER_CSS_REQUIRED,
                FOOTER_CSS_REQUIRED + '\n' + FOOTER_NAV_SUB_CSS,
                1
            )

    if new_content != content:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'[OK] {rel_path}')
        modified += 1
    else:
        skipped += 1

print(f'\n完了: {modified}件修正, {skipped}件スキップ')
