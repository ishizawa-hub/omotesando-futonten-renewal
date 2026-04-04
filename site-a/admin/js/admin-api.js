/**
 * 管理画面共通 API モジュール
 * WP REST API (oft/v1/admin/*) との通信を担当
 */
(function () {
  'use strict';

  var BASE = 'https://omotesando-futonten.com/wp/wp-json/oft/v1';
  var TOKEN_KEY = 'oft_admin_token';
  var USER_KEY = 'oft_admin_user';

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function headers() {
    var h = { 'Content-Type': 'application/json' };
    var t = getToken();
    if (t) h['Authorization'] = 'Bearer ' + t;
    return h;
  }

  function request(method, path, body) {
    var opts = {
      method: method,
      headers: headers(),
      credentials: 'include'
    };
    if (body) opts.body = JSON.stringify(body);
    return fetch(BASE + path, opts).then(function (res) {
      return res.json().then(function (data) {
        if (!res.ok) throw new Error(data.message || 'APIエラー (' + res.status + ')');
        return data;
      });
    });
  }

  var AdminAPI = {
    // === 認証 ===
    login: function (email, password) {
      return request('POST', '/admin/auth/login', { username: email, password: password })
        .then(function (data) {
          localStorage.setItem(TOKEN_KEY, data.token);
          localStorage.setItem(USER_KEY, JSON.stringify(data.user));
          return data;
        });
    },
    logout: function () {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      location.href = 'login.html';
    },
    isLoggedIn: function () { return !!getToken(); },
    getUser: function () {
      try { return JSON.parse(localStorage.getItem(USER_KEY)); }
      catch (e) { return null; }
    },
    requireAuth: function () {
      if (!getToken()) { location.href = 'login.html'; return false; }
      return true;
    },

    // === 商品 ===
    getProducts: function (category) {
      var q = category ? '?category=' + encodeURIComponent(category) : '';
      return request('GET', '/products' + q);
    },
    createProduct: function (data) {
      return request('POST', '/admin/products', data);
    },
    updateProduct: function (id, data) {
      return request('PUT', '/admin/products/' + id, data);
    },
    deleteProduct: function (id) {
      return request('DELETE', '/admin/products/' + id);
    },

    // === マガジン ===
    getMagazines: function () {
      return request('GET', '/admin/magazine');
    },
    createMagazine: function (data) {
      return request('POST', '/admin/magazine', data);
    },
    updateMagazine: function (id, data) {
      return request('PUT', '/admin/magazine/' + id, data);
    },
    deleteMagazine: function (id) {
      return request('DELETE', '/admin/magazine/' + id);
    },

    // === 注文 ===
    getOrders: function () {
      return request('GET', '/admin/orders');
    },
    updateOrderStatus: function (id, status) {
      return request('PUT', '/admin/orders/' + id, { status: status });
    },

    // === 在庫 ===
    getInventory: function () {
      return request('GET', '/admin/inventory');
    },
    updateStock: function (id, quantity) {
      return request('PUT', '/admin/inventory/' + id, { stock_quantity: quantity });
    },

    // === ページコンテンツ ===
    getPageContent: function (pageId) {
      return request('GET', '/pages/' + pageId);
    },
    getAllPageContent: function () {
      return request('GET', '/page-content');
    },
    updatePageContent: function (pageId, data) {
      return request('PUT', '/admin/pages/' + pageId, data);
    },

    // === 顧客 ===
    getCustomers: function () {
      return request('GET', '/admin/customers');
    },
    createCustomer: function (data) {
      return request('POST', '/admin/customers', data);
    },
    updateCustomer: function (id, data) {
      return request('PUT', '/admin/customers/' + id, data);
    },
    deleteCustomer: function (id) {
      return request('DELETE', '/admin/customers/' + id);
    },

    // === お問い合わせ ===
    getInquiries: function () {
      return request('GET', '/admin/inquiries');
    },
    updateInquiry: function (id, data) {
      return request('PUT', '/admin/inquiries/' + id, data);
    },
    deleteInquiry: function (id) {
      return request('DELETE', '/admin/inquiries/' + id);
    },

    // === 設定 ===
    getSettings: function () {
      return request('GET', '/admin/settings');
    },
    updateSettings: function (data) {
      return request('PUT', '/admin/settings', data);
    },

    // === ダッシュボード ===
    getDashboard: function () {
      return Promise.all([
        AdminAPI.getProducts().catch(function () { return []; }),
        AdminAPI.getOrders().catch(function () { return []; }),
        AdminAPI.getInventory().catch(function () { return []; }),
        AdminAPI.getMagazines().catch(function () { return []; })
      ]).then(function (results) {
        return { products: results[0], orders: results[1], inventory: results[2], magazines: results[3] };
      });
    }
  };

  window.AdminAPI = AdminAPI;
})();
