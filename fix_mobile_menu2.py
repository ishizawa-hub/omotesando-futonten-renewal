import os, re, glob

def get_mobile_menu(prefix):
    return (
        '<div class="mobile-menu-overlay" id="mobileMenuOverlay"></div>\n'
        '<!-- MOBILE MENU -->\n'
        '<div class="mobile-menu" id="mobileMenu">\n'
        '  <button class="mobile-menu-close" id="menuClose"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M18 6L6 18"/><path d="M6 6l12 12"/></svg></button>\n'
        '  <nav class="mm-nav">\n'
        f'    <a href="{prefix}index.html" class="mm-link">TOP</a>\n'
        '    <div class="mm-accordion">\n'
        '      <button class="mm-link mm-toggle">CONCEPT<svg class="mm-arrow" width="12" height="12" viewBox="0 0 12 12"><polyline points="2,4 6,8 10,4" fill="none" stroke="currentColor" stroke-width="1.5"/></svg></button>\n'
        '      <div class="mm-sub">\n'
        f'        <a href="{prefix}concept/">ブランドコンセプト</a>\n'
        f'        <a href="{prefix}concept/brand-story/">ブランドストーリー</a>\n'
        f'        <a href="{prefix}concept/clean-cycle-down/">Clean Cycle Down</a>\n'
        f'        <a href="{prefix}concept/material/">素材のこだわり</a>\n'
        '      </div>\n'
        '    </div>\n'
        '    <div class="mm-accordion">\n'
        '      <button class="mm-link mm-toggle">PRODUCTS<svg class="mm-arrow" width="12" height="12" viewBox="0 0 12 12"><polyline points="2,4 6,8 10,4" fill="none" stroke="currentColor" stroke-width="1.5"/></svg></button>\n'
        '      <div class="mm-sub">\n'
        f'        <a href="{prefix}products/">全商品一覧</a>\n'
        f'        <a href="{prefix}products/comforter/">掛け布団</a>\n'
        f'        <a href="{prefix}products/pillow/">枕</a>\n'
        f'        <a href="{prefix}products/bedding/">カバー・シーツ・寝具</a>\n'
        f'        <a href="{prefix}products/apparel/">アパレル</a>\n'
        f'        <a href="{prefix}products/collaboration/">コラボレーション</a>\n'
        f'        <a href="{prefix}products/baby/">ベビー</a>\n'
        f'        <a href="{prefix}products/service/">サービス</a>\n'
        '      </div>\n'
        '    </div>\n'
        f'    <a href="{prefix}magazine/" class="mm-link">MAGAZINE</a>\n'
        f'    <a href="{prefix}about/" class="mm-link">ABOUT</a>\n'
        '    <div class="mm-divider"></div>\n'
        f'    <a href="{prefix}gift/" class="mm-link mm-sub-link">GIFT</a>\n'
        f'    <a href="{prefix}faq/" class="mm-link mm-sub-link">FAQ</a>\n'
        f'    <a href="{prefix}contact/" class="mm-link mm-sub-link">CONTACT</a>\n'
        f'    <a href="{prefix}subscription/" class="mm-link mm-sub-link">サブスクリプション</a>\n'
        '    <div class="mm-divider"></div>\n'
        '    <div class="mm-bottom">\n'
        f'      <a href="{prefix}account/login/" class="mm-btn-outline">ログイン</a>\n'
        f'      <a href="{prefix}cart/" class="mm-btn-gold">カート</a>\n'
        '    </div>\n'
        '  </nav>\n'
        '</div>'
    )

MOBILE_CSS = (
    '.mobile-menu{position:fixed;top:0;right:0;width:320px;height:100vh;background:#2D2D2D;z-index:2000;transform:translateX(100%);transition:transform 0.4s cubic-bezier(0.16,1,0.3,1);padding:80px 0 40px;overflow-y:auto}\n'
    '.mobile-menu.active{transform:translateX(0)}\n'
    '.mobile-menu-close{position:absolute;top:20px;right:20px;width:40px;height:40px;background:none;border:none;color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center}\n'
    '.mobile-menu-close svg{width:24px;height:24px}\n'
    '.mobile-menu-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:1999;opacity:0;pointer-events:none;transition:opacity 0.4s}\n'
    '.mobile-menu-overlay.active{opacity:1;pointer-events:all}\n'
    '.mm-nav{display:flex;flex-direction:column;padding:0 28px}\n'
    ".mm-link{display:flex;align-items:center;justify-content:space-between;padding:15px 0;font-family:'DM Sans','Noto Sans JP',sans-serif;font-size:15px;font-weight:700;letter-spacing:0.12em;color:rgba(255,255,255,0.9);text-decoration:none;border-bottom:1px solid rgba(255,255,255,0.06);transition:color 0.3s;background:none;border-top:none;border-left:none;border-right:none;width:100%;text-align:left;cursor:pointer}\n"
    '.mm-link:hover{color:#C9A96E}\n'
    '.mm-sub-link{font-size:13px;font-weight:500;letter-spacing:0.06em;color:rgba(255,255,255,0.5);padding:12px 0}\n'
    '.mm-sub-link:hover{color:#C9A96E}\n'
    '.mm-toggle{position:relative}\n'
    '.mm-arrow{transition:transform 0.3s;color:rgba(255,255,255,0.4)}\n'
    '.mm-accordion.open .mm-arrow{transform:rotate(180deg)}\n'
    '.mm-sub{max-height:0;overflow:hidden;transition:max-height 0.35s ease}\n'
    '.mm-accordion.open .mm-sub{max-height:500px}\n'
    ".mm-sub a{display:block;padding:10px 0 10px 16px;font-family:'Noto Sans JP',sans-serif;font-size:13px;font-weight:500;color:rgba(255,255,255,0.5);text-decoration:none;letter-spacing:0.04em;transition:color 0.3s;border-bottom:1px solid rgba(255,255,255,0.03)}\n"
    '.mm-sub a:hover{color:#C9A96E}\n'
    '.mm-divider{height:1px;background:rgba(255,255,255,0.1);margin:8px 0}\n'
    '.mm-bottom{display:flex;gap:10px;margin-top:16px}\n'
    '.mm-btn-outline{flex:1;text-align:center;padding:12px;border:1px solid rgba(255,255,255,0.2);border-radius:6px;font-size:13px;font-weight:600;letter-spacing:0.06em;color:rgba(255,255,255,0.7);text-decoration:none;transition:all 0.3s}\n'
    '.mm-btn-outline:hover{border-color:#C9A96E;color:#C9A96E}\n'
    '.mm-btn-gold{flex:1;text-align:center;padding:12px;background:#C9A96E;border-radius:6px;font-size:13px;font-weight:600;letter-spacing:0.06em;color:#fff;text-decoration:none;transition:background 0.3s}\n'
    '.mm-btn-gold:hover{background:#B8975A}\n'
)

MOBILE_JS = (
    "var hamburger=document.getElementById('hamburgerBtn');\n"
    "var mobileMenu=document.getElementById('mobileMenu');\n"
    "var menuClose=document.getElementById('menuClose');\n"
    "var menuOverlay=document.getElementById('mobileMenuOverlay');\n"
    "function openMenu(){mobileMenu.classList.add('active');menuOverlay.classList.add('active');document.body.style.overflow='hidden'}\n"
    "function closeMenu(){mobileMenu.classList.remove('active');menuOverlay.classList.remove('active');document.body.style.overflow=''}\n"
    "if(hamburger)hamburger.addEventListener('click',openMenu);\n"
    "if(menuClose)menuClose.addEventListener('click',closeMenu);\n"
    "if(menuOverlay)menuOverlay.addEventListener('click',closeMenu);\n"
    "document.querySelectorAll('.mm-toggle').forEach(function(btn){btn.addEventListener('click',function(){this.parentElement.classList.toggle('open')})});\n"
)

site_root = 'site-a'
top_index = 'site-a/index.html'
count = 0
no_match = []

for f in glob.glob('site-a/**/index.html', recursive=True):
    f = f.replace('\\', '/')
    if f == top_index:
        continue

    try:
        with open(f, 'r', encoding='utf-8') as fh:
            content = fh.read()
    except:
        continue

    # Skip if already has mm-nav
    if 'class="mm-nav"' in content:
        continue

    # Must have mobile menu
    if '<div class="mobile-menu"' not in content:
        continue

    rel = os.path.relpath(site_root, os.path.dirname(f)).replace('\\', '/') + '/'
    new_menu = get_mobile_menu(rel)

    # Try pattern: <div class="mobile-menu" ...> ... </nav>\n</div>
    pattern = re.compile(
        r'<div class="mobile-menu" id="mobileMenu">.*?</nav>\s*</div>',
        re.DOTALL
    )

    match = pattern.search(content)
    if match:
        content = content[:match.start()] + new_menu + content[match.end():]
    else:
        no_match.append(f)
        continue

    # Remove old mobile-menu CSS and replace
    # Remove old .mobile-menu CSS block (fullscreen style)
    old_css_patterns = [
        re.compile(r'\.mobile-menu\{position:fixed;inset:0.*?\}', re.DOTALL),
        re.compile(r'\.mobile-menu\.active\{opacity:1;pointer-events:all\}'),
        re.compile(r'\.mobile-menu nav\{display:flex;flex-direction:column;align-items:center;gap:32px\}'),
        re.compile(r'\.mobile-menu nav a\{[^}]+\}'),
    ]
    for p in old_css_patterns:
        content = p.sub('', content)

    # Add mm-nav CSS if not present
    if '.mm-nav{' not in content:
        content = content.replace('</style>', MOBILE_CSS + '</style>', 1)

    # Replace old mobile menu JS
    old_js = re.compile(
        r'\(function\(\)\{var btn=document\.getElementById\(\'hamburgerBtn\'\).*?\}\)\(\);',
        re.DOTALL
    )
    content = old_js.sub('', content)

    # Add new JS if not present
    if "document.querySelectorAll('.mm-toggle')" not in content:
        last_script = content.rfind('</script>')
        if last_script != -1:
            content = content[:last_script] + MOBILE_JS + content[last_script:]

    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(content)
    count += 1

print(f"Updated: {count} files")
if no_match:
    print(f"No match ({len(no_match)}): {no_match[:10]}")
