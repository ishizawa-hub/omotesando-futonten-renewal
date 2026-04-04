/**
 * 表参道布団店 WP REST API クライアント
 * WooCommerce + oft-site-manager プラグインとの通信
 */
(function () {
  'use strict';

  // ステージング(Flask)時は同一オリジンAPI、本番時はWP REST API
  var isStaging = (location.hostname === 'localhost' || location.hostname === '127.0.0.1'
    || location.hostname.indexOf('ngrok') !== -1
    || location.hostname.indexOf('onrender.com') !== -1
    || location.hostname.indexOf('railway.app') !== -1);
  var BASE = isStaging
    ? location.origin + '/oft/v1'
    : 'https://omotesando-futonten.com/wp/wp-json/oft/v1';

  /**
   * 共通fetch
   */
  function request(path, opts) {
    opts = opts || {};
    var url = BASE + path;
    var headers = { 'Content-Type': 'application/json' };
    var token = window.OFTAuth && window.OFTAuth.getToken();
    if (token) headers['Authorization'] = 'Bearer ' + token;
    if (opts.headers) {
      Object.keys(opts.headers).forEach(function (k) { headers[k] = opts.headers[k]; });
    }
    return fetch(url, {
      method: opts.method || 'GET',
      headers: headers,
      body: opts.body ? JSON.stringify(opts.body) : undefined,
      credentials: 'include',
    }).then(function (res) {
      if (!res.ok) {
        return res.json().then(function (err) {
          throw new Error(err.message || 'API Error ' + res.status);
        });
      }
      return res.json();
    });
  }

  var OFTApi = {
    /**
     * ページコンテンツ取得
     */
    getPageContent: function (pageId) {
      return request('/pages/' + pageId);
    },

    getAllPages: function () {
      return request('/pages');
    },

    /**
     * 商品一覧取得
     */
    getProducts: function (category) {
      var q = category ? '?category=' + encodeURIComponent(category) : '';
      return request('/products' + q);
    },

    /**
     * Stripe Checkout セッション作成
     * items: [{product_id, quantity}]
     * shipping: {last_name, first_name, postcode, state, city, address1, address2, phone}
     * email: string
     */
    createCheckoutSession: function (items, shipping, email) {
      return request('/checkout/create-session', {
        method: 'POST',
        body: { items: items, shipping: shipping, email: email },
      });
    },

    /**
     * 注文履歴取得（要認証）
     */
    getOrders: function () {
      return request('/orders');
    },
  };

  window.OFTApi = OFTApi;
})();
