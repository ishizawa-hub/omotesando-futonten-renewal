/**
 * ページコンテンツ動的反映スクリプト
 * 管理画面（admin/pages.html）で編集したテキストをフロントエンドに反映する
 * データソース: localStorage（将来的にはWP REST API）
 */
(function() {
  'use strict';

  var STORAGE_KEY = 'oft_page_content';

  function getData() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; }
    catch(e) { return {}; }
  }

  function setText(selector, text) {
    if (!text) return;
    var els = document.querySelectorAll(selector);
    els.forEach(function(el) {
      // brタグを保持: \nを<br>に変換
      el.innerHTML = text.replace(/\n/g, '<br>');
    });
  }

  function setTextContent(selector, text) {
    if (!text) return;
    var els = document.querySelectorAll(selector);
    els.forEach(function(el) { el.textContent = text; });
  }

  // ページパスからページIDを判定
  var path = location.pathname;

  // パスの正規化（末尾スラッシュ統一、index.html除去）
  path = path.replace(/index\.html$/, '').replace(/\/$/, '/');

  var data = getData();

  // ============================================================
  // TOPページ
  // ============================================================
  if (path === '/' || path.match(/\/site-a\/?$/) || path.match(/\/site-a\/index\.html$/)) {
    var top = data.top;
    if (top) {
      // Hero
      setTextContent('.hero-en', top.hero_badge);
      setText('.hero-catch', top.hero_catch);
      setText('.hero-sub', top.hero_sub);
      setTextContent('.hero-cta', top.hero_cta);

      // Brand Story
      setTextContent('.brand-section .section-heading', top.story_heading);
      setText('.brand-section .section-heading-jp-accent', top.story_heading_jp);
      setTextContent('.brand-story-founder', top.story_founder);
      setText('.brand-story-quote', top.story_quote);
      setText('.brand-story-desc', top.story_desc);

      // Brand story points
      var points = document.querySelectorAll('.brand-story-point-text');
      if (points.length >= 3) {
        if (top.story_point1) points[0].textContent = top.story_point1;
        if (top.story_point2) points[1].textContent = top.story_point2;
        if (top.story_point3) points[2].textContent = top.story_point3;
      }

      // Products section
      setTextContent('.collection-section .section-heading', top.products_heading);
      setTextContent('.collection-section .section-heading-jp-accent', top.products_sub);

      // Experience
      setTextContent('.experience-header .section-heading', top.exp_heading);
      setTextContent('.experience-header .section-heading-jp-accent', top.exp_sub);

      var expCards = document.querySelectorAll('.exp-card');
      if (expCards.length >= 4) {
        var expData = [
          { title: top.exp1_title, desc: top.exp1_desc },
          { title: top.exp2_title, desc: top.exp2_desc },
          { title: top.exp3_title, desc: top.exp3_desc },
          { title: top.exp4_title, desc: top.exp4_desc }
        ];
        expCards.forEach(function(card, i) {
          if (expData[i]) {
            if (expData[i].title) {
              var t = card.querySelector('.exp-card-title');
              if (t) t.textContent = expData[i].title;
            }
            if (expData[i].desc) {
              var d = card.querySelector('.exp-card-desc');
              if (d) d.innerHTML = expData[i].desc.replace(/\n/g, '<br>');
            }
          }
        });
      }

      // Craftsmanship
      setTextContent('.craft-section .section-heading', top.craft_heading);
      setText('.craft-section .section-heading-jp-accent', top.craft_heading_jp);
      setText('.craft-section .brand-story-desc, .craft-section p', top.craft_desc);
    }
  }

  // ============================================================
  // ブランドストーリー
  // ============================================================
  if (path.indexOf('/concept/brand-story') !== -1) {
    var bs = data.brand_story;
    if (bs) {
      setTextContent('.hero-label', bs.hero_label);
      setTextContent('.hero-title', bs.hero_title);
      setTextContent('.hero-subtitle', bs.hero_subtitle);

      setTextContent('.philosophy-en', bs.phil_label);
      setText('.philosophy-title', bs.phil_title);
      setText('.philosophy-body', bs.phil_body);

      // Values
      var valueCards = document.querySelectorAll('.value-card');
      var valData = [
        { name: bs.value1_name, desc: bs.value1_desc },
        { name: bs.value2_name, desc: bs.value2_desc },
        { name: bs.value3_name, desc: bs.value3_desc }
      ];
      valueCards.forEach(function(card, i) {
        if (valData[i]) {
          if (valData[i].name) {
            var n = card.querySelector('.value-name');
            if (n) n.textContent = valData[i].name;
          }
          if (valData[i].desc) {
            var d = card.querySelector('.value-desc');
            if (d) d.innerHTML = valData[i].desc.replace(/\n/g, '<br>');
          }
        }
      });

      // Team
      setText('.team-title', bs.team_title);
      setText('.team-text', bs.team_text);
      setTextContent('.team-founder-name', bs.team_founder_name);
      setTextContent('.team-founder-role', bs.team_founder_role);
    }
  }

  // ============================================================
  // Clean Cycle Down
  // ============================================================
  if (path.indexOf('/concept/clean-cycle-down') !== -1) {
    var ccd = data.clean_cycle_down;
    if (ccd) {
      setTextContent('.hero-title', ccd.hero_title);
      setText('.hero-subtitle', ccd.hero_subtitle);

      setTextContent('.intro-en', ccd.intro_label);
      setText('.intro-title', ccd.intro_title);
      setText('.intro-body', ccd.intro_body);

      // Process steps
      var steps = document.querySelectorAll('.process-step');
      var stepData = [
        { title: ccd.step1_title, desc: ccd.step1_desc },
        { title: ccd.step2_title, desc: ccd.step2_desc },
        { title: ccd.step3_title, desc: ccd.step3_desc },
        { title: ccd.step4_title, desc: ccd.step4_desc }
      ];
      steps.forEach(function(step, i) {
        if (stepData[i]) {
          if (stepData[i].title) {
            var t = step.querySelector('.process-step-title');
            if (t) t.textContent = stepData[i].title;
          }
          if (stepData[i].desc) {
            var d = step.querySelector('.process-step-desc');
            if (d) d.innerHTML = stepData[i].desc.replace(/\n/g, '<br>');
          }
        }
      });
    }
  }

  // ============================================================
  // 素材のこだわり
  // ============================================================
  if (path.indexOf('/concept/material') !== -1) {
    var mat = data.material;
    if (mat) {
      setTextContent('.hero-title', mat.hero_title);
      setTextContent('.hero-title-en', mat.hero_title_en);

      setTextContent('.lineup-title', mat.lineup_title);
      setTextContent('.lineup-subtitle', mat.lineup_subtitle);

      setTextContent('.rds-title', mat.rds_title);
      setText('.rds-desc', mat.rds_desc);

      setTextContent('.fabric-title', mat.fabric_title);

      var fabricItems = document.querySelectorAll('.fabric-item');
      if (fabricItems.length >= 2) {
        if (mat.fabric1_title) {
          var t1 = fabricItems[0].querySelector('.fabric-item-title');
          if (t1) t1.textContent = mat.fabric1_title;
        }
        if (mat.fabric1_desc) {
          var d1 = fabricItems[0].querySelector('.fabric-item-desc');
          if (d1) d1.innerHTML = mat.fabric1_desc.replace(/\n/g, '<br>');
        }
        if (mat.fabric2_title) {
          var t2 = fabricItems[1].querySelector('.fabric-item-title');
          if (t2) t2.textContent = mat.fabric2_title;
        }
        if (mat.fabric2_desc) {
          var d2 = fabricItems[1].querySelector('.fabric-item-desc');
          if (d2) d2.innerHTML = mat.fabric2_desc.replace(/\n/g, '<br>');
        }
      }
    }
  }

  // ============================================================
  // 会社概要
  // ============================================================
  if (path.indexOf('/about') !== -1) {
    var about = data.about;
    if (about) {
      setTextContent('.hero-title, .page-hero-title', about.hero_title);
      setTextContent('.hero-subtitle, .page-hero-jp', about.hero_subtitle);
      setText('.company-desc', about.company_desc);
    }
  }

  // ============================================================
  // FAQ
  // ============================================================
  if (path.indexOf('/faq') !== -1) {
    var faq = data.faq;
    if (faq) {
      setTextContent('.hero-title, .page-hero-title', faq.hero_title);
      setTextContent('.hero-subtitle, .page-hero-jp', faq.hero_subtitle);
    }
  }

  // ============================================================
  // ショッピングガイド
  // ============================================================
  if (path.indexOf('/shopping-guide') !== -1) {
    var sg = data.shopping_guide;
    if (sg) {
      setTextContent('.hero-title, .page-hero-title', sg.hero_title);
      setTextContent('.hero-subtitle, .page-hero-jp', sg.hero_subtitle);
      setText('.shipping-text', sg.shipping_text);
      setText('.return-text', sg.return_text);
      setText('.payment-text', sg.payment_text);
    }
  }

})();
