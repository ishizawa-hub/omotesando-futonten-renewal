/**
 * 表参道布団店 認証モジュール
 * トークンベース認証（oft-site-manager REST API）
 */
(function () {
  'use strict';

  var TOKEN_KEY = 'oft_auth_token';
  var USER_KEY = 'oft_auth_user';
  var BASE = 'https://omotesando-futonten.com/wp/wp-json/oft/v1';

  function post(path, body) {
    return fetch(BASE + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      credentials: 'include',
    }).then(function (res) {
      return res.json().then(function (data) {
        if (!res.ok) throw new Error(data.message || 'Error');
        return data;
      });
    });
  }

  var OFTAuth = {
    /**
     * ログイン
     * @returns Promise<{token, user}>
     */
    login: function (email, password) {
      return post('/auth/login', { email: email, password: password }).then(function (data) {
        localStorage.setItem(TOKEN_KEY, data.token);
        localStorage.setItem(USER_KEY, JSON.stringify(data.user));
        OFTAuth._notify();
        return data;
      });
    },

    /**
     * 新規会員登録
     */
    register: function (params) {
      return post('/auth/register', params).then(function (data) {
        if (data.token) {
          localStorage.setItem(TOKEN_KEY, data.token);
          localStorage.setItem(USER_KEY, JSON.stringify(data.user));
          OFTAuth._notify();
        }
        return data;
      });
    },

    /**
     * ログアウト
     */
    logout: function () {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      OFTAuth._notify();
    },

    /**
     * トークン取得
     */
    getToken: function () {
      return localStorage.getItem(TOKEN_KEY);
    },

    /**
     * ログインユーザー情報
     */
    getUser: function () {
      try {
        return JSON.parse(localStorage.getItem(USER_KEY));
      } catch (e) {
        return null;
      }
    },

    /**
     * ログイン中かどうか
     */
    isLoggedIn: function () {
      return !!OFTAuth.getToken();
    },

    /**
     * ヘッダーUI更新
     */
    _notify: function () {
      var ev = new CustomEvent('oft:auth-change', {
        detail: { loggedIn: OFTAuth.isLoggedIn(), user: OFTAuth.getUser() },
      });
      document.dispatchEvent(ev);
    },

    /**
     * ヘッダーのログインリンクを状態に応じて切替
     */
    updateHeaderUI: function () {
      var links = document.querySelectorAll('.header-actions a');
      links.forEach(function (a) {
        if (a.textContent.trim() === 'LOGIN' || a.textContent.trim() === 'MYPAGE') {
          if (OFTAuth.isLoggedIn()) {
            a.textContent = 'MYPAGE';
            a.href = a.href.replace(/login\/?$/, '');
          } else {
            a.textContent = 'LOGIN';
          }
        }
      });
    },
  };

  // ページロード時にヘッダーUI更新
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', OFTAuth.updateHeaderUI);
  } else {
    OFTAuth.updateHeaderUI();
  }

  window.OFTAuth = OFTAuth;
})();
