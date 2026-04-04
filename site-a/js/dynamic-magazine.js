/**
 * マガジン一覧の動的描画
 * 管理画面で更新した記事データをAPIから取得しフロントに反映
 * ステージング環境でのみ動作
 */
(function() {
  'use strict';

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

  function resolveImg(url) {
    if (!url) return '';
    if (url.startsWith('http') || url.startsWith('data:') || url.startsWith('/')) return url;
    return '/' + url;
  }

  // カテゴリカラーマッピング
  var catColors = {
    'お手入れ': '#4A7C59',
    'ダウンの基礎知識': '#2D6B8A',
    '素材・製法': '#8B6914',
    'お知らせ': '#8A3B5E',
    'メディア掲載': '#5B4A8A',
    'イベント': '#C9A96E',
    'コラム': '#555555'
  };

  function getCatColor(cat) {
    return catColors[cat] || '#888';
  }

  // ============================================================
  // マガジン一覧 グリッド描画
  // ============================================================
  function renderMagazineGrid(articles) {
    var grid = document.querySelector('.view-grid');
    if (!grid) return;

    if (!articles.length) {
      grid.innerHTML = '<p style="text-align:center;padding:60px;color:#999;">記事が見つかりません</p>';
      return;
    }

    var html = '';
    articles.forEach(function(a) {
      var imgUrl = resolveImg(a.heroImage || (a.listThumbnail && a.listThumbnail.url) || '');
      var slug = a.slug || a.id || '';
      var dateStr = a.date ? a.date.replace(/-/g, '.') : '';
      var color = getCatColor(a.category);
      var excerpt = a.excerpt || (a.body ? a.body.replace(/<[^>]+>/g, '').substring(0, 80) + '...' : '');

      html += '<a href="../magazine/' + escHtml(slug) + '/" class="mg-card" data-category="' + escHtml(a.category) + '">' +
        '<div class="mg-card-img">' +
          (imgUrl ? '<img src="' + escHtml(imgUrl) + '" alt="' + escHtml(a.title) + '" loading="lazy">' : '<div style="width:100%;height:100%;background:#F0EFEC;display:flex;align-items:center;justify-content:center;color:#999;font-size:14px;">No Image</div>') +
        '</div>' +
        '<div class="mg-card-body">' +
          '<div class="mg-card-meta">' +
            '<span class="mg-card-cat" style="color:' + color + ';border-color:' + color + '">' + escHtml(a.category) + '</span>' +
            '<span class="mg-card-date">' + escHtml(dateStr) + '</span>' +
          '</div>' +
          '<h3 class="mg-card-title">' + escHtml(a.title) + '</h3>' +
          '<p class="mg-card-excerpt">' + escHtml(excerpt) + '</p>' +
        '</div>' +
      '</a>';
    });
    grid.innerHTML = html;
  }

  // リスト表示
  function renderMagazineList(articles) {
    var list = document.querySelector('.view-list');
    if (!list) return;

    var html = '';
    articles.forEach(function(a) {
      var imgUrl = resolveImg(a.heroImage || '');
      var slug = a.slug || a.id || '';
      var dateStr = a.date ? a.date.replace(/-/g, '.') : '';
      var color = getCatColor(a.category);
      var excerpt = a.excerpt || (a.body ? a.body.replace(/<[^>]+>/g, '').substring(0, 120) + '...' : '');

      html += '<a href="../magazine/' + escHtml(slug) + '/" class="ml-card" data-category="' + escHtml(a.category) + '">' +
        '<div class="ml-card-img">' +
          (imgUrl ? '<img src="' + escHtml(imgUrl) + '" alt="' + escHtml(a.title) + '" loading="lazy">' : '') +
        '</div>' +
        '<div class="ml-card-body">' +
          '<div class="mg-card-meta">' +
            '<span class="mg-card-cat" style="color:' + color + ';border-color:' + color + '">' + escHtml(a.category) + '</span>' +
            '<span class="mg-card-date">' + escHtml(dateStr) + '</span>' +
          '</div>' +
          '<h3 class="ml-card-title">' + escHtml(a.title) + '</h3>' +
          '<p class="ml-card-excerpt">' + escHtml(excerpt) + '</p>' +
        '</div>' +
      '</a>';
    });
    list.innerHTML = html;
  }

  // 注目記事
  function renderFeatured(article) {
    var featured = document.querySelector('.mag-featured-card');
    if (!featured || !article) return;

    var a = article;
    var imgUrl = resolveImg(a.heroImage || '');
    var slug = a.slug || a.id || '';
    var color = getCatColor(a.category);
    var excerpt = a.excerpt || (a.body ? a.body.replace(/<[^>]+>/g, '').substring(0, 120) + '...' : '');

    featured.setAttribute('href', '../magazine/' + slug + '/');
    var imgEl = featured.querySelector('.mf-img img');
    if (imgEl && imgUrl) imgEl.src = imgUrl;
    var titleEl = featured.querySelector('.mf-title');
    if (titleEl) titleEl.textContent = a.title;
    var excerptEl = featured.querySelector('.mf-excerpt');
    if (excerptEl) excerptEl.textContent = excerpt;
    var catEl = featured.querySelector('.mg-card-cat');
    if (catEl) {
      catEl.textContent = a.category;
      catEl.style.color = color;
      catEl.style.borderColor = color;
    }
  }

  // ============================================================
  // カテゴリフィルタリングの再バインド
  // ============================================================
  function bindCategoryFilter(allArticles) {
    var catButtons = document.querySelectorAll('.mag-cats button, .mag-cats a, [data-filter-cat]');
    catButtons.forEach(function(btn) {
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        var cat = this.getAttribute('data-filter-cat') || this.textContent.trim();
        catButtons.forEach(function(b) { b.classList.remove('active'); });
        this.classList.add('active');

        var filtered = cat === 'すべて' || cat === 'ALL'
          ? allArticles
          : allArticles.filter(function(a) { return a.category === cat; });
        renderMagazineGrid(filtered);
        renderMagazineList(filtered);
      });
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

    // /magazine/ または /magazine/index.html
    if (!path.match(/\/magazine\/(index\.html)?$/)) return;

    OFTApi.getMagazines().then(function(articles) {
      if (!articles || !articles.length) return;

      // 注目記事（最新）
      renderFeatured(articles[0]);

      // 一覧描画
      renderMagazineGrid(articles);
      renderMagazineList(articles);

      // フィルタ再バインド
      bindCategoryFilter(articles);
    }).catch(function(err) {
      console.log('[dynamic-magazine] API取得失敗、静的表示のまま:', err.message);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
