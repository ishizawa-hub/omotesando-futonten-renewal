/**
 * 管理画面共通: トースト通知 + バリデーション
 */
(function() {
  'use strict';

  // ============================================================
  // トースト通知
  // ============================================================
  var toastContainer;

  function ensureContainer() {
    if (toastContainer) return;
    toastContainer = document.createElement('div');
    toastContainer.id = 'adminToastContainer';
    toastContainer.style.cssText = 'position:fixed;top:24px;right:24px;z-index:99999;display:flex;flex-direction:column;gap:8px;pointer-events:none;';
    document.body.appendChild(toastContainer);
  }

  /**
   * トースト表示
   * @param {string} message - メッセージ
   * @param {string} type - 'success' | 'error' | 'warning' | 'info'
   * @param {number} duration - 表示時間ms（デフォルト3000）
   */
  function showToast(message, type, duration) {
    ensureContainer();
    type = type || 'success';
    duration = duration || 3000;

    var icons = { success: '\u2714', error: '\u2718', warning: '\u26A0', info: '\u2139' };
    var colors = {
      success: { bg: '#E8F5E9', border: '#4CAF50', text: '#2E7D32', icon: '#4CAF50' },
      error:   { bg: '#FFEBEE', border: '#E53935', text: '#C62828', icon: '#E53935' },
      warning: { bg: '#FFF8E1', border: '#F9A825', text: '#E65100', icon: '#F9A825' },
      info:    { bg: '#E3F2FD', border: '#1976D2', text: '#0D47A1', icon: '#1976D2' }
    };
    var c = colors[type] || colors.info;

    var toast = document.createElement('div');
    toast.style.cssText = 'pointer-events:auto;display:flex;align-items:center;gap:10px;padding:14px 20px;border-radius:10px;border:1px solid ' + c.border + ';background:' + c.bg + ';color:' + c.text + ';font-size:14px;font-weight:500;box-shadow:0 4px 20px rgba(0,0,0,0.12);opacity:0;transform:translateX(40px);transition:all 0.3s ease;min-width:280px;max-width:420px;';
    toast.innerHTML = '<span style="font-size:18px;color:' + c.icon + ';">' + (icons[type] || '') + '</span><span>' + message + '</span>';
    toastContainer.appendChild(toast);

    // アニメーション
    requestAnimationFrame(function() {
      toast.style.opacity = '1';
      toast.style.transform = 'translateX(0)';
    });

    setTimeout(function() {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(40px)';
      setTimeout(function() {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      }, 300);
    }, duration);
  }

  // ============================================================
  // バリデーション
  // ============================================================

  /**
   * 必須フィールドのバリデーション
   * @param {Array} fields - [{id: 'elementId', label: '項目名'}, ...]
   * @returns {Object} { valid: bool, missing: [{id, label}], count: number }
   */
  function validateRequired(fields) {
    var missing = [];
    fields.forEach(function(f) {
      var el = document.getElementById(f.id);
      if (!el) return;
      var val = (el.value || el.textContent || '').trim();
      if (!val || val === '選択してください' || val === '---') {
        missing.push(f);
        // 未入力フィールドをハイライト
        el.style.borderColor = '#E53935';
        el.style.boxShadow = '0 0 0 2px rgba(229,57,53,0.15)';
      } else {
        el.style.borderColor = '';
        el.style.boxShadow = '';
      }
    });

    return {
      valid: missing.length === 0,
      missing: missing,
      count: missing.length
    };
  }

  /**
   * バリデーション結果のアラート表示
   * @param {Object} result - validateRequiredの戻り値
   * @returns {boolean} valid
   */
  function showValidationAlert(result) {
    if (result.valid) return true;

    if (result.count === 1) {
      // 最後の1個の場合は具体的な項目名を表示
      showToast('「' + result.missing[0].label + '」が未入力です', 'error', 4000);
    } else {
      showToast('必須項目が ' + result.count + ' 件未入力です', 'warning', 4000);
    }
    return false;
  }

  /**
   * 公開/下書きの制御
   * 未入力項目がある場合は公開ボタンを無効化
   * @param {string} publishBtnId - 公開ボタンのID
   * @param {string} draftBtnId - 下書きボタンのID（オプション）
   * @param {Array} requiredFields - 必須フィールド配列
   */
  function enforcePublishRestriction(publishBtnId, draftBtnId, requiredFields) {
    var publishBtn = document.getElementById(publishBtnId);
    if (!publishBtn) return;

    function check() {
      var result = validateRequired(requiredFields);
      if (result.valid) {
        publishBtn.disabled = false;
        publishBtn.style.opacity = '1';
        publishBtn.title = '';
      } else {
        publishBtn.disabled = true;
        publishBtn.style.opacity = '0.5';
        if (result.count === 1) {
          publishBtn.title = '「' + result.missing[0].label + '」が未入力のため公開できません';
        } else {
          publishBtn.title = '必須項目が ' + result.count + ' 件未入力のため公開できません';
        }
      }
    }

    // 初期チェック
    check();

    // フォーム入力時にリアルタイムチェック
    requiredFields.forEach(function(f) {
      var el = document.getElementById(f.id);
      if (el) {
        el.addEventListener('input', check);
        el.addEventListener('change', check);
      }
    });

    return check;
  }

  // グローバル公開
  window.AdminToast = {
    show: showToast,
    success: function(msg) { showToast(msg, 'success'); },
    error: function(msg) { showToast(msg, 'error', 5000); },
    warning: function(msg) { showToast(msg, 'warning', 4000); },
    info: function(msg) { showToast(msg, 'info'); },
    validateRequired: validateRequired,
    showValidationAlert: showValidationAlert,
    enforcePublishRestriction: enforcePublishRestriction
  };
})();
