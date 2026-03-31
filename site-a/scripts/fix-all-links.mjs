/**
 * Comprehensive fix for all HTML pages in site-a:
 * 1. Standardize header (logo, nav, mega menu) with correct relative paths
 * 2. Standardize footer with correct relative paths
 * 3. Add consistent mobile menu to ALL pages
 * 4. Fix all breadcrumbs with correct links
 * 5. Add JSON-LD structured data for breadcrumbs
 * 6. Fix broken image references
 * 7. Fix all internal link references
 */
import { readFile, writeFile, readdir, stat } from 'fs/promises';
import { join, relative, dirname, basename } from 'path';
import { existsSync } from 'fs';

const SITE_A = join(import.meta.dirname, '..');
const BASE_URL = 'https://ishizawa-hub.github.io/omotesando-futonten-renewal/site-a';

// =============================================
// PAGE HIERARCHY FOR BREADCRUMBS
// =============================================
const BREADCRUMBS = {
  'index.html': [{ name: 'TOP', path: '' }],
  'about/index.html': [
    { name: 'TOP', path: '' },
    { name: 'ABOUT', path: 'about/' }
  ],
  'concept/index.html': [
    { name: 'TOP', path: '' },
    { name: 'CONCEPT', path: 'concept/' }
  ],
  'concept/clean-cycle-down/index.html': [
    { name: 'TOP', path: '' },
    { name: 'CONCEPT', path: 'concept/' },
    { name: 'Clean Cycle Down', path: 'concept/clean-cycle-down/' }
  ],
  'concept/material/index.html': [
    { name: 'TOP', path: '' },
    { name: 'CONCEPT', path: 'concept/' },
    { name: '素材のこだわり', path: 'concept/material/' }
  ],
  'products/index.html': [
    { name: 'TOP', path: '' },
    { name: '商品一覧', path: 'products/' }
  ],
  'products/comforter/index.html': [
    { name: 'TOP', path: '' },
    { name: '商品一覧', path: 'products/' },
    { name: '掛け布団', path: 'products/comforter/' }
  ],
  'products/pillow/index.html': [
    { name: 'TOP', path: '' },
    { name: '商品一覧', path: 'products/' },
    { name: '枕', path: 'products/pillow/' }
  ],
  'products/bedding/index.html': [
    { name: 'TOP', path: '' },
    { name: '商品一覧', path: 'products/' },
    { name: '寝具', path: 'products/bedding/' }
  ],
  'products/apparel/index.html': [
    { name: 'TOP', path: '' },
    { name: '商品一覧', path: 'products/' },
    { name: 'アパレル', path: 'products/apparel/' }
  ],
  'products/collaboration/index.html': [
    { name: 'TOP', path: '' },
    { name: '商品一覧', path: 'products/' },
    { name: 'コラボレーション', path: 'products/collaboration/' }
  ],
  'products/baby/index.html': [
    { name: 'TOP', path: '' },
    { name: '商品一覧', path: 'products/' },
    { name: 'ベビー', path: 'products/baby/' }
  ],
  'products/service/index.html': [
    { name: 'TOP', path: '' },
    { name: '商品一覧', path: 'products/' },
    { name: 'サービス', path: 'products/service/' }
  ],
  'service/index.html': [
    { name: 'TOP', path: '' },
    { name: 'サービス', path: 'service/' }
  ],
  'magazine/index.html': [
    { name: 'TOP', path: '' },
    { name: 'マガジン', path: 'magazine/' }
  ],
  'cart/index.html': [
    { name: 'TOP', path: '' },
    { name: 'カート', path: 'cart/' }
  ],
  'checkout/index.html': [
    { name: 'TOP', path: '' },
    { name: 'カート', path: 'cart/' },
    { name: 'お会計', path: 'checkout/' }
  ],
  'checkout/success/index.html': [
    { name: 'TOP', path: '' },
    { name: 'カート', path: 'cart/' },
    { name: '注文完了', path: 'checkout/success/' }
  ],
  'gift/index.html': [
    { name: 'TOP', path: '' },
    { name: 'ギフト', path: 'gift/' }
  ],
  'faq/index.html': [
    { name: 'TOP', path: '' },
    { name: 'FAQ', path: 'faq/' }
  ],
  'contact/index.html': [
    { name: 'TOP', path: '' },
    { name: 'お問い合わせ', path: 'contact/' }
  ],
  'subscription/index.html': [
    { name: 'TOP', path: '' },
    { name: 'サブスクリプション', path: 'subscription/' }
  ],
  'glossary/index.html': [
    { name: 'TOP', path: '' },
    { name: '用語集', path: 'glossary/' }
  ],
  'privacy-policy/index.html': [
    { name: 'TOP', path: '' },
    { name: 'プライバシーポリシー', path: 'privacy-policy/' }
  ],
  'terms/index.html': [
    { name: 'TOP', path: '' },
    { name: '利用規約', path: 'terms/' }
  ],
  'inventory-view/index.html': [
    { name: 'TOP', path: '' },
    { name: '在庫状況', path: 'inventory-view/' }
  ],
  'account/index.html': [
    { name: 'TOP', path: '' },
    { name: 'マイアカウント', path: 'account/' }
  ],
  'account/login/index.html': [
    { name: 'TOP', path: '' },
    { name: 'マイアカウント', path: 'account/' },
    { name: 'ログイン', path: 'account/login/' }
  ],
  'account/register/index.html': [
    { name: 'TOP', path: '' },
    { name: 'マイアカウント', path: 'account/' },
    { name: '新規登録', path: 'account/register/' }
  ],
  'account/forgot-password/index.html': [
    { name: 'TOP', path: '' },
    { name: 'マイアカウント', path: 'account/' },
    { name: 'パスワード再設定', path: 'account/forgot-password/' }
  ],
  'down/index.html': [
    { name: 'TOP', path: '' },
    { name: 'ダウンについて', path: 'down/' }
  ],
  'down/material/index.html': [
    { name: 'TOP', path: '' },
    { name: 'ダウンについて', path: 'down/' },
    { name: '素材', path: 'down/material/' }
  ],
  'down/technology/index.html': [
    { name: 'TOP', path: '' },
    { name: 'ダウンについて', path: 'down/' },
    { name: '技術', path: 'down/technology/' }
  ],
};

// Product detail pages - auto-generate breadcrumbs
const PRODUCT_CATEGORIES = {
  'comforter': '掛け布団',
  'pillow': '枕',
  'bedding': '寝具',
  'apparel': 'アパレル',
  'collaboration': 'コラボレーション',
  'baby': 'ベビー',
  'service': 'サービス',
};

const PRODUCT_NAMES = {
  'ccd-winter': 'Clean Cycle Down 冬用本掛け',
  'ccd-spring': 'Clean Cycle Down 春秋用合掛け',
  'ccd-summer': 'Clean Cycle Down 夏用肌掛け',
  'premium-rds-winter': 'Premium RDS Down 冬用本掛け',
  'premium-rds-spring': 'Premium RDS Down 春秋用合掛け',
  'premium-rds-summer': 'Premium RDS Down 夏用肌掛け',
  'rds-goose-winter': 'RDS Down 冬用本掛け',
  'rds-goose-spring': 'RDS Down 春秋用合掛け',
  'rds-goose-summer': 'RDS Down 夏用肌掛け',
  'flower-winter': 'Flower Down 冬用本掛け',
  'flower-spring': 'Flower Down 春秋用合掛け',
  'flower-summer': 'Flower Down 夏用肌掛け',
  'ccd-pillow': 'Clean Cycle Down ピロー',
  'duck-pillow': 'ダックダウンピロー',
  'goose-pillow': 'グースダウンピロー',
  'bed-pad': 'ベッドパッド',
  'cover': '掛け布団カバー',
  'mattress': 'マットレス',
  'pillow-case': 'ピローケース',
  'sheets': 'シーツ',
  'down-jacket': 'ダウンジャケット',
  'down-vest': 'ダウンベスト',
  'inoue-blanket': '井上ブランケット',
  'inoue-pajamas': '井上パジャマ',
  'baby-comforter': 'ベビー掛け布団',
  'baby-set': 'ベビー布団セット',
  'reform': 'リフォーム',
  'rental-ccd': 'レンタル CCD',
  'rental-premium': 'レンタル Premium',
  'trial': 'お試し体験',
};

const MAGAZINE_NAMES = {
  'care-guide': 'お手入れガイド',
  'ccd-story': 'CCD ストーリー',
  'futon-guide': '布団ガイド',
  'mother-goose': 'マザーグース',
  'netflix': 'Netflix特集',
};

// =============================================
// GENERATE HEADER HTML
// =============================================
function generateHeader(prefix) {
  const p = prefix;
  return `<header class="header" id="header">
  <div class="header-inner">
    <a href="${p}index.html" class="header-logo"><img src="${p}images/logo.svg" alt="表参道布団店。| Clean Cycle Down"></a>
    <nav class="header-nav" id="headerNav">
      <div class="header-nav-item">
        <a href="${p}concept/">CONCEPT</a>
        <div class="nav-dropdown">
          <a href="${p}concept/">ブランドコンセプト</a>
          <a href="${p}concept/clean-cycle-down/">Clean Cycle Down</a>
          <a href="${p}concept/material/">素材のこだわり</a>
        </div>
      </div>
      <div class="header-nav-item">
        <a href="${p}products/">PRODUCTS</a>
        <div class="nav-mega">
          <a href="${p}products/comforter/" class="nav-mega-card">
            <img src="${p}images/site/comforter_hero.jpg" alt="掛け布団" loading="lazy">
            <span class="nav-mega-card-label">COMFORTER</span>
            <span class="nav-mega-card-name">掛け布団</span>
          </a>
          <a href="${p}products/pillow/" class="nav-mega-card">
            <img src="${p}images/site/pillow_hero2.jpg" alt="枕" loading="lazy">
            <span class="nav-mega-card-label">PILLOW</span>
            <span class="nav-mega-card-name">枕</span>
          </a>
          <a href="${p}products/bedding/" class="nav-mega-card">
            <img src="${p}images/site/bedding_hero.jpg" alt="寝具" loading="lazy">
            <span class="nav-mega-card-label">BEDDING</span>
            <span class="nav-mega-card-name">寝具</span>
          </a>
          <a href="${p}products/apparel/" class="nav-mega-card">
            <img src="${p}images/site/apparel_hero.jpg" alt="アパレル" loading="lazy">
            <span class="nav-mega-card-label">APPAREL</span>
            <span class="nav-mega-card-name">アパレル</span>
          </a>
          <a href="${p}products/collaboration/" class="nav-mega-card">
            <img src="${p}images/site/collab_hero.jpg" alt="コラボ" loading="lazy">
            <span class="nav-mega-card-label">COLLABORATION</span>
            <span class="nav-mega-card-name">コラボ</span>
          </a>
          <a href="${p}products/baby/" class="nav-mega-card">
            <img src="${p}images/site/baby_hero.jpg" alt="ベビー" loading="lazy">
            <span class="nav-mega-card-label">BABY</span>
            <span class="nav-mega-card-name">ベビー</span>
          </a>
          <a href="${p}products/service/" class="nav-mega-card">
            <img src="${p}images/site/service_hero2.png" alt="サービス" loading="lazy">
            <span class="nav-mega-card-label">SERVICE</span>
            <span class="nav-mega-card-name">サービス</span>
          </a>
        </div>
      </div>
      <div class="header-nav-item">
        <a href="${p}magazine/">MAGAZINE</a>
      </div>
      <div class="header-nav-item">
        <a href="${p}about/">ABOUT</a>
      </div>
    </nav>
    <div class="header-actions">
      <a href="${p}cart/">CART(0)</a>
      <button class="hamburger" id="hamburgerBtn" aria-label="メニュー"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>`;
}

// =============================================
// GENERATE MOBILE MENU HTML
// =============================================
function generateMobileMenu(prefix) {
  const p = prefix;
  return `
<!-- MOBILE MENU -->
<div class="mobile-menu" id="mobileMenu">
  <button class="mobile-menu-close" id="menuClose"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M18 6L6 18"/><path d="M6 6l12 12"/></svg></button>
  <nav>
    <a href="${p}index.html">TOP</a>
    <a href="${p}concept/">CONCEPT</a>
    <a href="${p}products/">PRODUCTS</a>
    <a href="${p}concept/clean-cycle-down/">CLEAN CYCLE DOWN</a>
    <a href="${p}magazine/">MAGAZINE</a>
    <a href="${p}about/">ABOUT</a>
    <a href="${p}gift/">GIFT</a>
    <a href="${p}contact/">CONTACT</a>
    <a href="${p}faq/">FAQ</a>
    <a href="${p}subscription/">サブスクリプション</a>
    <a href="${p}cart/">CART</a>
  </nav>
</div>`;
}

// =============================================
// GENERATE FOOTER HTML
// =============================================
function generateFooter(prefix) {
  const p = prefix;
  return `<footer class="footer">
  <div class="footer-inner">
    <div class="footer-brand">
      <div class="footer-logo"><img src="${p}images/logo.svg" alt="表参道布団店。"></div>
      <p class="footer-desc">眠りの質を、人生の質へ。<br>Clean Cycle Down</p>
      <div class="footer-newsletter" style="margin-top:24px">
        <p style="font-size:13px;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;color:#C9A96E;margin-bottom:10px">NEWSLETTER</p>
        <p style="font-size:14px;color:rgba(255,255,255,0.4);margin-bottom:12px;line-height:1.6">新商品やキャンペーン情報をお届けします</p>
        <form onsubmit="event.preventDefault();this.querySelector('button').textContent='登録完了';this.querySelector('input').value='';setTimeout(function(){document.querySelector('.footer-newsletter button').textContent='登録'},2000)" style="display:flex;gap:0">
          <input type="email" placeholder="メールアドレス" required style="flex:1;padding:10px 14px;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);border-right:none;color:#fff;font-size:13px;outline:none;font-family:inherit;transition:border-color 0.3s" onfocus="this.style.borderColor='#C9A96E'" onblur="this.style.borderColor='rgba(255,255,255,0.15)'">
          <button type="submit" style="padding:10px 20px;background:#C9A96E;color:#fff;border:none;font-size:14px;font-weight:600;letter-spacing:0.08em;cursor:pointer;transition:background 0.3s;white-space:nowrap" onmouseover="this.style.background='#B8975A'" onmouseout="this.style.background='#C9A96E'">登録</button>
        </form>
      </div>
    </div>
    <div>
      <h4 class="footer-nav-title">PRODUCTS</h4>
      <nav class="footer-nav">
        <a href="${p}products/comforter/">掛け布団</a>
        <a href="${p}products/pillow/">枕</a>
        <a href="${p}products/bedding/">寝具</a>
        <a href="${p}products/apparel/">アパレル</a>
        <a href="${p}products/collaboration/">コラボレーション</a>
        <a href="${p}products/baby/">ベビー</a>
        <a href="${p}products/service/">サービス</a>
      </nav>
    </div>
    <div>
      <h4 class="footer-nav-title">CONCEPT</h4>
      <nav class="footer-nav">
        <a href="${p}concept/">ブランドコンセプト</a>
        <a href="${p}concept/clean-cycle-down/">Clean Cycle Down</a>
        <a href="${p}concept/material/">素材のこだわり</a>
        <a href="${p}down/">ダウンについて</a>
      </nav>
    </div>
    <div>
      <h4 class="footer-nav-title">INFORMATION</h4>
      <nav class="footer-nav">
        <a href="${p}magazine/">マガジン</a>
        <a href="${p}about/">ブランドストーリー</a>
        <a href="${p}gift/">ギフト</a>
        <a href="${p}faq/">FAQ</a>
        <a href="${p}contact/">お問い合わせ</a>
        <a href="${p}subscription/">サブスクリプション</a>
        <a href="${p}inventory-view/">在庫状況</a>
        <a href="${p}privacy-policy/">プライバシーポリシー</a>
        <a href="${p}terms/">利用規約</a>
      </nav>
    </div>
  </div>
  <p class="footer-copy">&copy; 2026 Omotesando Futon Ten. All rights reserved.</p>
</footer>`;
}

// =============================================
// GENERATE BREADCRUMB HTML
// =============================================
function generateBreadcrumb(crumbs, prefix) {
  if (!crumbs || crumbs.length <= 1) return '';

  const items = crumbs.map((c, i) => {
    if (i === crumbs.length - 1) {
      return `<span>${c.name}</span>`;
    }
    const href = c.path === '' ? `${prefix}index.html` : `${prefix}${c.path}`;
    return `<a href="${href}">${c.name}</a>`;
  });

  return `<nav class="breadcrumb" aria-label="パンくずリスト"><div class="bc-inner">${items.join(' <span class="bc-sep">/</span> ')}</div></nav>`;
}

// =============================================
// GENERATE JSON-LD BREADCRUMB
// =============================================
function generateJsonLd(crumbs) {
  if (!crumbs || crumbs.length <= 1) return '';

  const items = crumbs.map((c, i) => ({
    '@type': 'ListItem',
    'position': i + 1,
    'name': c.name,
    'item': c.path === '' ? `${BASE_URL}/` : `${BASE_URL}/${c.path}`
  }));

  return `<script type="application/ld+json">
${JSON.stringify({ '@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': items }, null, 2)}
</script>`;
}

// =============================================
// MOBILE MENU CSS (standardized)
// =============================================
const MOBILE_MENU_CSS = `/* Mobile Menu */
.mobile-menu{position:fixed;top:0;right:0;width:320px;height:100vh;background:#2D2D2D;z-index:2000;transform:translateX(100%);transition:transform 0.4s cubic-bezier(0.16,1,0.3,1);padding:80px 40px 40px;overflow-y:auto}
.mobile-menu.active{transform:translateX(0)}
.mobile-menu-close{position:absolute;top:20px;right:20px;width:40px;height:40px;background:none;border:none;color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center}
.mobile-menu-close svg{width:24px;height:24px}
.mobile-menu nav{display:flex;flex-direction:column;gap:0}
.mobile-menu nav a{display:block;padding:16px 0;font-family:'DM Sans','Noto Sans JP',sans-serif;font-size:15px;font-weight:600;letter-spacing:0.1em;color:rgba(255,255,255,0.8);text-decoration:none;border-bottom:1px solid rgba(255,255,255,0.08);transition:color 0.3s}
.mobile-menu nav a:hover{color:#C9A96E}
.mobile-menu-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:1999;opacity:0;pointer-events:none;transition:opacity 0.4s}
.mobile-menu-overlay.active{opacity:1;pointer-events:all}`;

// =============================================
// MOBILE MENU JS (standardized)
// =============================================
const MOBILE_MENU_JS = `
// Mobile menu
(function(){
  var btn=document.getElementById('hamburgerBtn');
  var menu=document.getElementById('mobileMenu');
  var close=document.getElementById('menuClose');
  var overlay=document.getElementById('mobileMenuOverlay');
  if(!btn||!menu)return;
  function openMenu(){menu.classList.add('active');if(overlay)overlay.classList.add('active');document.body.style.overflow='hidden';}
  function closeMenu(){menu.classList.remove('active');if(overlay)overlay.classList.remove('active');document.body.style.overflow='';}
  btn.addEventListener('click',openMenu);
  if(close)close.addEventListener('click',closeMenu);
  if(overlay)overlay.addEventListener('click',closeMenu);
  menu.querySelectorAll('a').forEach(function(a){a.addEventListener('click',closeMenu);});
})();`;

// BREADCRUMB CSS
const BREADCRUMB_CSS = `/* Breadcrumb */
.breadcrumb{max-width:1320px;margin:0 auto;padding:16px 40px;display:flex;align-items:center;font-size:13px;color:#6B6B6B}
.bc-inner{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.breadcrumb a{transition:color 0.3s;text-decoration:none;color:#6B6B6B}
.breadcrumb a:hover{color:#1A1A1A}
.bc-sep{color:#E5E5E5}
@media(max-width:768px){.breadcrumb{padding:12px 20px}}`;

// =============================================
// HELPER: Get relative prefix
// =============================================
function getPrefix(relPath) {
  const dir = dirname(relPath);
  if (dir === '.') return '';
  const depth = dir.split('/').length;
  return '../'.repeat(depth);
}

// =============================================
// HELPER: Get breadcrumbs for a page
// =============================================
function getBreadcrumbs(relPath) {
  // Direct match
  if (BREADCRUMBS[relPath]) return BREADCRUMBS[relPath];

  // Product detail pages: products/{category}/{product}/index.html
  const parts = relPath.split('/');
  if (parts[0] === 'products' && parts.length === 4 && parts[3] === 'index.html') {
    const cat = parts[1];
    const prod = parts[2];
    const catName = PRODUCT_CATEGORIES[cat] || cat;
    const prodName = PRODUCT_NAMES[prod] || prod;
    return [
      { name: 'TOP', path: '' },
      { name: '商品一覧', path: 'products/' },
      { name: catName, path: `products/${cat}/` },
      { name: prodName, path: `products/${cat}/${prod}/` }
    ];
  }

  // Magazine articles: magazine/{slug}/index.html
  if (parts[0] === 'magazine' && parts.length === 3 && parts[2] === 'index.html') {
    const slug = parts[1];
    const name = MAGAZINE_NAMES[slug] || slug;
    return [
      { name: 'TOP', path: '' },
      { name: 'マガジン', path: 'magazine/' },
      { name: name, path: `magazine/${slug}/` }
    ];
  }

  return null;
}

// =============================================
// PROCESS A SINGLE HTML FILE
// =============================================
async function processFile(filePath) {
  const relPath = relative(SITE_A, filePath).replace(/\\/g, '/');

  // Skip admin pages, products.html (legacy), showroom.html, ccd.html, concept.html, product-detail.html
  const skipFiles = ['admin.html', 'admin/', 'showroom.html', 'product-detail.html'];
  if (skipFiles.some(s => relPath.startsWith(s) && s.endsWith('/')) ||
      skipFiles.includes(relPath)) {
    // For admin pages, still fix basic links but don't add breadcrumbs
    if (relPath.startsWith('admin')) {
      console.log(`  [admin] ${relPath}`);
      return;
    }
  }

  let html = await readFile(filePath, 'utf-8');
  const prefix = getPrefix(relPath);
  const crumbs = getBreadcrumbs(relPath);
  const isHomePage = relPath === 'index.html';

  // Skip non-public pages
  if (relPath.startsWith('admin')) {
    console.log(`  [skip-admin] ${relPath}`);
    return;
  }

  let modified = false;

  // ---- 1. Replace header ----
  const headerRegex = /<header\s+class="header"[^>]*>[\s\S]*?<\/header>/;
  if (headerRegex.test(html)) {
    const newHeader = generateHeader(prefix);
    html = html.replace(headerRegex, newHeader);
    modified = true;
  }

  // ---- 2. Remove old mobile menus (nav-overlay or mobile-menu) and add new one ----
  // Remove old nav-overlay
  html = html.replace(/<!--[\s\S]*?FULLSCREEN NAV OVERLAY[\s\S]*?-->\s*<div class="nav-overlay"[\s\S]*?<\/div>\s*<\/div>/g, '');
  // Remove old mobile-menu divs
  html = html.replace(/<!--\s*MOBILE\s*MENU\s*-->\s*<div class="mobile-menu"[\s\S]*?<\/div>\s*<\/div>/gi, '');
  html = html.replace(/<div class="mobile-menu"[\s\S]*?<\/nav>\s*<\/div>/gi, '');
  // Remove mobile-menu-overlay if exists
  html = html.replace(/<div class="mobile-menu-overlay"[^>]*><\/div>/g, '');

  // Insert new mobile menu + overlay after </header>
  const mobileMenuHtml = `\n<div class="mobile-menu-overlay" id="mobileMenuOverlay"></div>${generateMobileMenu(prefix)}`;
  html = html.replace('</header>', '</header>' + mobileMenuHtml);
  modified = true;

  // ---- 3. Replace footer ----
  const footerRegex = /<footer\s+class="footer"[^>]*>[\s\S]*?<\/footer>/;
  if (footerRegex.test(html)) {
    html = html.replace(footerRegex, generateFooter(prefix));
    modified = true;
  }

  // ---- 4. Fix/Add breadcrumbs ----
  if (!isHomePage && crumbs) {
    const bcHtml = generateBreadcrumb(crumbs, prefix);
    // Remove existing breadcrumbs
    html = html.replace(/<nav\s+class="breadcrumb"[^>]*>[\s\S]*?<\/nav>/g, '');

    // Insert breadcrumb after the first main section hero or after mobile menu
    // Find the right insertion point - after the mobile menu div
    const insertAfterMobileMenu = '</div>\n\n';
    const mobileMenuEndIdx = html.indexOf('</div>', html.indexOf('id="mobileMenu"'));
    if (mobileMenuEndIdx > -1) {
      // Find the close of the mobile menu parent
      const afterMobile = html.indexOf('\n', mobileMenuEndIdx + 6);
      if (afterMobile > -1) {
        // Check if there's a hero section right after
        const nextContent = html.substring(afterMobile, afterMobile + 200);
        const heroMatch = nextContent.match(/(<(?:section|div)\s+class="[^"]*hero[^"]*")/);
        if (heroMatch) {
          // Insert breadcrumb after the hero section
          const heroStart = html.indexOf(heroMatch[0], afterMobile);
          // Find closing of hero section
          const heroClose = html.indexOf('</section>', heroStart);
          if (heroClose > -1) {
            html = html.substring(0, heroClose + 10) + '\n\n' + bcHtml + html.substring(heroClose + 10);
          }
        } else {
          // Insert right after mobile menu
          html = html.substring(0, afterMobile + 1) + '\n' + bcHtml + '\n' + html.substring(afterMobile + 1);
        }
      }
    }
    modified = true;
  }

  // ---- 5. Add/Replace JSON-LD breadcrumb structured data ----
  if (crumbs && crumbs.length > 1) {
    // Remove existing JSON-LD breadcrumb
    html = html.replace(/<script\s+type="application\/ld\+json">\s*\{[\s\S]*?"BreadcrumbList"[\s\S]*?\}\s*<\/script>/g, '');

    const jsonLd = generateJsonLd(crumbs);
    // Insert before </head>
    html = html.replace('</head>', jsonLd + '\n</head>');
    modified = true;
  }

  // ---- 6. Add mobile menu CSS if not present ----
  if (!html.includes('.mobile-menu{') && !html.includes('.mobile-menu {')) {
    // Insert before /* === END GLOBAL NAV === */ or before closing </style>
    const endNavMarker = '/* === END GLOBAL NAV === */';
    if (html.includes(endNavMarker)) {
      html = html.replace(endNavMarker, MOBILE_MENU_CSS + '\n' + endNavMarker);
    } else {
      // Insert before first </style>
      html = html.replace('</style>', MOBILE_MENU_CSS + '\n</style>');
    }
    modified = true;
  } else {
    // Replace existing mobile menu CSS with standardized version
    // Remove old mobile-menu CSS and replace
    html = html.replace(/\/\*\s*Mobile Menu\s*\*\/[\s\S]*?(?=\/\*|<\/style>)/, MOBILE_MENU_CSS + '\n');
    // Also fix old mobile-menu styles that don't have the comment header
    html = html.replace(/\.mobile-menu\{position:fixed;inset:0[\s\S]*?\.mobile-menu nav a:hover\{color:#C9A96E\}/, MOBILE_MENU_CSS.replace('/* Mobile Menu */\n', ''));
    html = html.replace(/\.mobile-menu\{position:fixed;top:0;right:0[\s\S]*?\.mobile-menu nav a:hover\{color:#C9A96E\}/, MOBILE_MENU_CSS.replace('/* Mobile Menu */\n', ''));
  }

  // ---- 7. Add breadcrumb CSS if not present ----
  if (crumbs && crumbs.length > 1 && !html.includes('.bc-inner')) {
    const endNavMarker = '/* === END GLOBAL NAV === */';
    if (html.includes(endNavMarker)) {
      html = html.replace(endNavMarker, BREADCRUMB_CSS + '\n' + endNavMarker);
    }
  }

  // ---- 8. Add mobile menu JS ----
  // Remove old mobile menu JS patterns
  html = html.replace(/\/\/\s*Mobile menu\s*\n\s*\(function\(\)\{[\s\S]*?btn\.addEventListener[\s\S]*?\}\)\(\);/g, '');
  html = html.replace(/const\s+mm\s*=\s*document\.getElementById\('mobileMenu'\)[\s\S]*?mm\.querySelectorAll[\s\S]*?\}\)\(\);/g, '');

  // Remove old nav overlay JS
  html = html.replace(/\/\*\s*--+\s*Mobile\s*nav\s*--+\s*\*\/[\s\S]*?navClose[\s\S]*?;/g, '');
  html = html.replace(/document\.getElementById\('hamburgerBtn'\)\.addEventListener[\s\S]*?navOverlay[\s\S]*?\);/g, '');

  // Add standardized mobile menu JS before </body>
  if (!html.includes('mobileMenuOverlay') || html.indexOf('mobileMenuOverlay') === html.lastIndexOf('mobileMenuOverlay')) {
    html = html.replace('</body>', `<script>${MOBILE_MENU_JS}\n</script>\n</body>`);
  }

  // ---- 9. Fix remaining relative link issues ----
  // Fix links like href="index.html" that should be href="../index.html" on subpages
  // Fix service/index.html to products/service/ in nav (already handled by header replacement)

  // Fix any remaining references to products.html -> products/
  html = html.replace(/href="products\.html"/g, `href="${prefix}products/"`);

  // Fix favicon paths
  html = html.replace(/href="images\/favicon\.svg"/g, `href="${prefix}images/favicon.svg"`);
  if (prefix) {
    html = html.replace(/href="\.\.\/images\/favicon\.svg"/g, `href="${prefix}images/favicon.svg"`);
    html = html.replace(/href="\.\.\/\.\.\/images\/favicon\.svg"/g, `href="${prefix}images/favicon.svg"`);
    html = html.replace(/href="\.\.\/\.\.\/\.\.\/images\/favicon\.svg"/g, `href="${prefix}images/favicon.svg"`);
  }

  // Fix cart.js paths
  html = html.replace(/src="js\/cart\.js"/g, `src="${prefix}js/cart.js"`);
  html = html.replace(/src="\.\.\/js\/cart\.js"/g, `src="${prefix}js/cart.js"`);
  html = html.replace(/src="\.\.\/\.\.\/js\/cart\.js"/g, `src="${prefix}js/cart.js"`);
  html = html.replace(/src="\.\.\/\.\.\/\.\.\/js\/cart\.js"/g, `src="${prefix}js/cart.js"`);

  if (modified) {
    await writeFile(filePath, html, 'utf-8');
    console.log(`  ✓ ${relPath}`);
  } else {
    console.log(`  - ${relPath} (no changes)`);
  }
}

// =============================================
// FIND ALL HTML FILES RECURSIVELY
// =============================================
async function findHtmlFiles(dir) {
  const results = [];
  const entries = await readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === 'scripts' || entry.name === 'node_modules' || entry.name === '.git') continue;
      results.push(...await findHtmlFiles(fullPath));
    } else if (entry.name.endsWith('.html')) {
      results.push(fullPath);
    }
  }
  return results;
}

// =============================================
// MAIN
// =============================================
async function main() {
  console.log('=== Fixing all site-a links, nav, footer, breadcrumbs ===\n');

  const allFiles = await findHtmlFiles(SITE_A);
  const publicFiles = allFiles.filter(f => {
    const rel = relative(SITE_A, f).replace(/\\/g, '/');
    // Skip admin pages for now (they have different layouts)
    if (rel.startsWith('admin/') || rel === 'admin.html') return false;
    // Skip legacy standalone pages that are duplicates
    if (rel === 'ccd.html' || rel === 'concept.html' || rel === 'showroom.html' || rel === 'product-detail.html' || rel === 'products.html') return false;
    return true;
  });

  console.log(`Found ${publicFiles.length} public HTML files to process\n`);

  for (const file of publicFiles) {
    try {
      await processFile(file);
    } catch (err) {
      console.error(`  ✗ ${relative(SITE_A, file)}: ${err.message}`);
    }
  }

  // Also fix the legacy products.html to redirect to products/
  const productsHtml = join(SITE_A, 'products.html');
  if (existsSync(productsHtml)) {
    const redirectHtml = `<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0;url=products/">
<link rel="canonical" href="${BASE_URL}/products/">
<title>商品一覧 | 表参道布団店。</title>
</head>
<body>
<p>リダイレクト中... <a href="products/">商品一覧はこちら</a></p>
</body>
</html>`;
    await writeFile(productsHtml, redirectHtml, 'utf-8');
    console.log('\n  ✓ products.html → redirect to products/');
  }

  // Fix ccd.html → redirect to concept/clean-cycle-down/
  const ccdHtml = join(SITE_A, 'ccd.html');
  if (existsSync(ccdHtml)) {
    const redirectHtml = `<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0;url=concept/clean-cycle-down/">
<link rel="canonical" href="${BASE_URL}/concept/clean-cycle-down/">
<title>Clean Cycle Down | 表参道布団店。</title>
</head>
<body>
<p>リダイレクト中... <a href="concept/clean-cycle-down/">Clean Cycle Downはこちら</a></p>
</body>
</html>`;
    await writeFile(ccdHtml, redirectHtml, 'utf-8');
    console.log('  ✓ ccd.html → redirect to concept/clean-cycle-down/');
  }

  // Fix concept.html → redirect to concept/
  const conceptHtml = join(SITE_A, 'concept.html');
  if (existsSync(conceptHtml)) {
    const redirectHtml = `<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0;url=concept/">
<link rel="canonical" href="${BASE_URL}/concept/">
<title>コンセプト | 表参道布団店。</title>
</head>
<body>
<p>リダイレクト中... <a href="concept/">コンセプトはこちら</a></p>
</body>
</html>`;
    await writeFile(conceptHtml, redirectHtml, 'utf-8');
    console.log('  ✓ concept.html → redirect to concept/');
  }

  console.log('\n=== Done! ===');
}

main().catch(console.error);
