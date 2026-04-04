/**
 * 商品一覧・詳細の動的描画
 * 管理画面で更新した商品データをAPIから取得しフロントに反映
 * ステージング環境でのみ動作（本番は静的HTMLのまま）
 */
(function() {
  'use strict';

  // ステージング判定
  var isStaging = (location.hostname === 'localhost' || location.hostname === '127.0.0.1'
    || location.hostname.indexOf('ngrok') !== -1
    || location.hostname.indexOf('onrender.com') !== -1
    || location.hostname.indexOf('railway.app') !== -1);
  if (!isStaging) return;

  function escHtml(s) {
    var d = document.createElement('div');
    d.textContent = s || '';
    return d.innerHTML;
  }

  function formatPrice(n) {
    return '¥' + Number(n).toLocaleString('ja-JP');
  }

  // 画像URLの解決
  function resolveImg(url) {
    if (!url) return '';
    if (url.startsWith('http') || url.startsWith('data:') || url.startsWith('/')) return url;
    return '/' + url;
  }

  // ============================================================
  // カテゴリ別商品一覧（comforter/index.html 等）
  // ============================================================
  function renderProductGrid(products) {
    var grid = document.getElementById('productGrid') || document.querySelector('.comforter-grid, .product-grid');
    if (!grid) return;

    if (!products.length) {
      grid.innerHTML = '<p style="text-align:center;padding:60px;color:#999;">該当する商品がありません</p>';
      return;
    }

    var html = '';
    products.forEach(function(p) {
      var imgUrl = (p.images && p.images[0]) ? resolveImg(p.images[0].url) : '';
      var minPrice = Infinity;
      if (p.sizes && p.sizes.length) {
        p.sizes.forEach(function(s) { if (s.price < minPrice) minPrice = s.price; });
      }
      var priceStr = minPrice < Infinity ? formatPrice(minPrice) : '';
      var slug = (p.slug || p.id || '').replace(/[^a-zA-Z0-9-_]/g, '');

      html += '<a href="' + slug + '/" class="comforter-card" data-product-id="' + escHtml(p.id) + '">' +
        '<div class="comforter-card-img">' +
          (imgUrl ? '<img src="' + escHtml(imgUrl) + '" alt="' + escHtml(p.name) + '" loading="lazy">' : '<div style="width:100%;height:100%;background:#F0EFEC;display:flex;align-items:center;justify-content:center;color:#999;">No Image</div>') +
        '</div>' +
        '<div class="comforter-card-body">' +
          '<p class="comforter-card-series">' + escHtml(p.series || '') + '</p>' +
          '<h3 class="comforter-card-name">' + escHtml(p.name) + '</h3>' +
          '<p class="comforter-card-catch">' + escHtml(p.catchcopy || p.subtitle || '') + '</p>' +
          (priceStr ? '<p class="comforter-card-price">' + priceStr + '<span class="comforter-card-tax">〜（税込）</span></p>' : '') +
        '</div>' +
      '</a>';
    });
    grid.innerHTML = html;
  }

  // ============================================================
  // 商品詳細ページの動的更新
  // ============================================================
  function updateProductDetail(product) {
    var p = product;

    // 商品名
    var nameEl = document.querySelector('.purchase-name, h1.product-title');
    if (nameEl) nameEl.textContent = p.name;

    // シリーズ名
    var seriesEl = document.querySelector('.purchase-series');
    if (seriesEl) seriesEl.textContent = p.series || '';

    // キャッチコピー
    var catchEl = document.querySelector('.purchase-catch');
    if (catchEl) catchEl.textContent = p.catchcopy || p.subtitle || '';

    // 価格
    var priceEl = document.querySelector('.purchase-price');
    if (priceEl && p.sizes && p.sizes.length) {
      var minPrice = Math.min.apply(null, p.sizes.map(function(s) { return s.price; }));
      priceEl.innerHTML = formatPrice(minPrice) + '<span class="purchase-price-tax">〜（税込）</span>';
    }

    // 説明
    var descEl = document.querySelector('.product-description, .purchase-description');
    if (descEl) descEl.textContent = p.description || '';

    // ギャラリー画像
    var galleryMain = document.querySelector('.gallery-main .swiper-wrapper');
    var galleryThumbs = document.querySelector('.gallery-thumbs');
    if (galleryMain && p.images && p.images.length) {
      var mainHtml = '';
      var thumbHtml = '';
      p.images.forEach(function(img, idx) {
        var url = resolveImg(img.url);
        mainHtml += '<div class="swiper-slide"><img src="' + escHtml(url) + '" alt="' + escHtml(img.alt || p.name) + '" loading="lazy"></div>';
        thumbHtml += '<div class="gallery-thumb' + (idx === 0 ? ' active' : '') + '" data-index="' + idx + '"><img src="' + escHtml(url) + '" alt="" loading="lazy"></div>';
      });
      galleryMain.innerHTML = mainHtml;
      if (galleryThumbs) galleryThumbs.innerHTML = thumbHtml;
    }

    // サイズ選択ボタン
    var sizeWrap = document.querySelector('.size-buttons, .purchase-sizes');
    if (sizeWrap && p.sizes && p.sizes.length) {
      var sizeHtml = '';
      p.sizes.forEach(function(s, idx) {
        sizeHtml += '<button class="size-btn' + (idx === 0 ? ' active' : '') + '" data-price="' + s.price + '" data-size="' + escHtml(s.name) + '">' +
          escHtml(s.name) + (s.dimensions ? ' (' + escHtml(s.dimensions) + ')' : '') +
        '</button>';
      });
      sizeWrap.innerHTML = sizeHtml;
    }

    // カラー選択
    var colorWrap = document.querySelector('.color-buttons, .purchase-colors');
    if (colorWrap && p.colors && p.colors.length) {
      var colorHtml = '<span class="purchase-color-label">カラー</span>';
      p.colors.forEach(function(c, idx) {
        var border = c.border ? 'border:1px solid #ddd;' : '';
        colorHtml += '<button class="color-btn' + (idx === 0 ? ' active' : '') + '" data-color="' + escHtml(c.name) + '" style="background:' + escHtml(c.code) + ';width:28px;height:28px;border-radius:50%;' + border + '" title="' + escHtml(c.name) + '"></button>';
      });
      colorWrap.innerHTML = colorHtml;
    }

    // スペック表
    var specTable = document.querySelector('.spec-table tbody, .spec-section table tbody');
    if (specTable && p.specs && p.specs.length) {
      var specHtml = '';
      p.specs.forEach(function(s) {
        specHtml += '<tr><th>' + escHtml(s.key) + '</th><td>' + escHtml(s.value) + '</td></tr>';
      });
      specTable.innerHTML = specHtml;
    }

    // 価格表
    var priceTable = document.querySelector('.price-table tbody, .price-section table tbody');
    if (priceTable && p.sizes && p.sizes.length) {
      var ptHtml = '';
      p.sizes.forEach(function(s) {
        ptHtml += '<tr><td>' + escHtml(s.name) + '</td><td>' + (s.dimensions || '') + '</td><td>' + (s.fill || '') + '</td><td style="text-align:right;font-weight:600;">' + formatPrice(s.price) + '</td></tr>';
      });
      priceTable.innerHTML = ptHtml;
    }
  }

  // ============================================================
  // メイン商品一覧ページ（/products/）のカテゴリカード更新
  // ============================================================
  function updateCategoryCards(products) {
    var cards = document.querySelectorAll('.category-card');
    if (!cards.length) return;

    // カテゴリ別に集計
    var cats = {};
    products.forEach(function(p) {
      var cat = p.category || '未分類';
      if (!cats[cat]) cats[cat] = { count: 0, minPrice: Infinity, maxPrice: 0 };
      cats[cat].count++;
      if (p.sizes) p.sizes.forEach(function(s) {
        if (s.price < cats[cat].minPrice) cats[cat].minPrice = s.price;
        if (s.price > cats[cat].maxPrice) cats[cat].maxPrice = s.price;
      });
    });

    // 既存カードの件数・価格を更新
    cards.forEach(function(card) {
      var jp = card.querySelector('.category-card-jp');
      if (!jp) return;
      var catName = jp.textContent.trim();
      var info = cats[catName];
      if (!info) return;
      var countEl = card.querySelector('.category-card-count');
      if (countEl) countEl.textContent = info.count + ' 商品';
      var priceEl = card.querySelector('.category-card-price');
      if (priceEl && info.minPrice < Infinity) {
        priceEl.textContent = formatPrice(info.minPrice) + ' – ' + formatPrice(info.maxPrice);
      }
    });
  }

  // ============================================================
  // 初期化
  // ============================================================
  function init() {
    if (typeof OFTApi === 'undefined') {
      setTimeout(init, 100);
      return;
    }

    var path = location.pathname;

    // /products/ メインページ → カテゴリカード更新
    if (path.match(/\/products\/(index\.html)?$/)) {
      OFTApi.getProducts().then(updateCategoryCards).catch(function() {});
      return;
    }

    // /products/comforter/ 等 → カテゴリ商品一覧
    var catMatch = path.match(/\/products\/([^\/]+)\/(index\.html)?$/);
    if (catMatch) {
      var catMap = {
        'comforter': '掛け布団',
        'pillow': '枕',
        'bedding': '寝装品',
        'apparel': 'アパレル',
        'baby': 'ベビー',
        'collaboration': 'コラボレーション',
        'service': 'サービス'
      };
      var category = catMap[catMatch[1]] || '';
      OFTApi.getProducts(category || undefined).then(function(products) {
        if (category) {
          products = products.filter(function(p) { return p.category === category; });
        }
        renderProductGrid(products);
      }).catch(function() {});
      return;
    }

    // /products/comforter/xxx/ → 商品詳細
    var detailMatch = path.match(/\/products\/[^\/]+\/([^\/]+)\/(index\.html)?$/);
    if (detailMatch) {
      var slug = detailMatch[1];
      // まず全商品から名前やslugで検索
      OFTApi.getProducts().then(function(products) {
        var found = products.find(function(p) {
          return p.slug === slug || (p.id && p.id === slug);
        });
        if (found) updateProductDetail(found);
      }).catch(function() {});
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
