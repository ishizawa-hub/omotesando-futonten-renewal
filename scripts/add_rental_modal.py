#!/usr/bin/env python3
"""
レンタル商品ページにカート追加前の確認モーダルを追加。
対象: trial, rental-ccd, rental-premium
- 「こちらは月額サブスクリプション支払い型のレンタル商品となりますが大丈夫ですか？」
- はい/いいえボタン
- カートアイテムに isRental:true を付与
"""
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

SITE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'site-a')

RENTAL_PAGES = [
    os.path.join(SITE_DIR, 'products', 'service', 'trial', 'index.html'),
    os.path.join(SITE_DIR, 'products', 'service', 'rental-ccd', 'index.html'),
    os.path.join(SITE_DIR, 'products', 'service', 'rental-premium', 'index.html'),
]

# モーダルCSS
MODAL_CSS = """
/* Rental Confirmation Modal */
.rental-modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:9000;display:flex;align-items:center;justify-content:center;opacity:0;visibility:hidden;transition:opacity 0.3s,visibility 0.3s}
.rental-modal-overlay.active{opacity:1;visibility:visible}
.rental-modal{background:#fff;max-width:440px;width:90%;padding:40px 32px;text-align:center;position:relative}
.rental-modal-icon{width:56px;height:56px;margin:0 auto 20px;background:rgba(201,169,110,0.12);border-radius:50%;display:flex;align-items:center;justify-content:center}
.rental-modal-icon svg{width:28px;height:28px;color:#C9A96E}
.rental-modal-title{font-family:var(--font-jp);font-size:16px;font-weight:600;margin-bottom:12px;line-height:1.7}
.rental-modal-text{font-family:var(--font-jp);font-size:14px;color:var(--text-light);line-height:1.8;margin-bottom:28px}
.rental-modal-actions{display:flex;gap:12px;justify-content:center}
.rental-modal-actions button{padding:14px 32px;font-size:14px;font-weight:600;letter-spacing:0.08em;border:none;cursor:pointer;transition:all 0.3s;font-family:var(--font-jp)}
.btn-rental-yes{background:#C9A96E;color:#fff}
.btn-rental-yes:hover{background:#B8975A}
.btn-rental-no{background:none;border:1px solid var(--border)!important;color:var(--text)}
.btn-rental-no:hover{border-color:var(--text)!important}
.rental-badge{display:inline-block;background:#C9A96E;color:#fff;font-size:10px;font-weight:700;letter-spacing:0.1em;padding:2px 8px;border-radius:2px;margin-left:8px;vertical-align:middle}
"""

# モーダルHTML
MODAL_HTML = """
<!-- Rental Confirmation Modal -->
<div class="rental-modal-overlay" id="rentalModal">
  <div class="rental-modal">
    <div class="rental-modal-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 9v3m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
    </div>
    <h3 class="rental-modal-title">レンタル商品の確認</h3>
    <p class="rental-modal-text">こちらは月額サブスクリプション支払い型の<br>レンタル商品となりますが大丈夫ですか？</p>
    <div class="rental-modal-actions">
      <button class="btn-rental-no" id="rentalModalNo">いいえ</button>
      <button class="btn-rental-yes" id="rentalModalYes">はい</button>
    </div>
  </div>
</div>
"""

# カートJS修正: purchase-cartクリック時にモーダルを表示→はいで実際にカート追加
# 既存のcartBtn.addEventListener('click',...) を置換
OLD_CART_HANDLER = """    cartBtn.addEventListener('click',function(e){
      e.preventDefault();
      // Get product info
      var nameEl=document.querySelector('.purchase-name')||document.querySelector('.purchase-series');
      var productName=nameEl?nameEl.textContent.trim():'商品';
      var priceEl=document.querySelector('.purchase-price-num');
      var price=priceEl?priceEl.textContent.trim():'';
      var qtyEl=document.querySelector('.purchase-qty input');
      var qty=qtyEl?parseInt(qtyEl.value)||1:1;

      // Check gift mode
      var giftCheck=document.getElementById('giftToggle');
      var isGift=giftCheck&&giftCheck.checked;
      var giftInfo=null;

      if(isGift){
        var gn=document.getElementById('giftName');
        var gt=document.getElementById('giftTel');
        var gz=document.getElementById('giftZip');
        var ga=document.getElementById('giftAddr');
        if(!gn.value||!gt.value||!gz.value||!ga.value){
          alert('ギフト送付先の必須項目をすべてご入力ください。');
          return;
        }
        giftInfo={
          name:gn.value,
          tel:gt.value,
          zip:gz.value,
          addr:ga.value,
          bldg:(document.getElementById('giftBldg')||{}).value||'',
          time:(document.getElementById('giftTime')||{}).value||'',
          msg:(document.getElementById('giftMsg')||{}).value||''
        };
      }

      // Add to cart
      var cart=getCart();
      var item={
        id:location.pathname,
        name:productName,
        price:price,
        qty:qty,
        isGift:isGift,
        giftInfo:giftInfo,
        addedAt:new Date().toISOString()
      };
      // Check if same product already in cart
      var found=false;
      for(var i=0;i<cart.length;i++){
        if(cart[i].id===item.id&&cart[i].isGift===item.isGift){
          cart[i].qty+=qty;
          if(isGift) cart[i].giftInfo=giftInfo;
          found=true;
          break;
        }
      }
      if(!found) cart.push(item);
      saveCart(cart);

      // Show confirmation
      var msg=isGift?'ギフトとしてカートに追加しました':'カートに追加しました';
      var toast=document.createElement('div');
      toast.style.cssText='position:fixed;bottom:32px;left:50%;transform:translateX(-50%);background:#2D2D2D;color:#fff;padding:16px 32px;border-radius:4px;font-size:14px;font-family:inherit;z-index:9999;box-shadow:0 8px 32px rgba(0,0,0,0.2);display:flex;align-items:center;gap:10px;animation:fadeInUp .3s';
      toast.innerHTML='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#C9A96E" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>'+msg;
      document.body.appendChild(toast);
      setTimeout(function(){toast.style.opacity='0';toast.style.transition='opacity .3s';setTimeout(function(){toast.remove()},300)},2500);

      // If gift, redirect to gift checkout
      if(isGift){
        setTimeout(function(){
          var base=location.pathname.split('/products/')[0]||'';
          location.href=base+'/checkout-gift/';
        },1500);
      }
    });"""

NEW_CART_HANDLER = """    // レンタル確認モーダル制御
    var rentalModal=document.getElementById('rentalModal');
    var rentalYes=document.getElementById('rentalModalYes');
    var rentalNo=document.getElementById('rentalModalNo');
    function showRentalModal(){rentalModal.classList.add('active')}
    function hideRentalModal(){rentalModal.classList.remove('active')}
    if(rentalNo)rentalNo.addEventListener('click',hideRentalModal);
    rentalModal.addEventListener('click',function(e){if(e.target===rentalModal)hideRentalModal()});

    function addRentalToCart(){
      var nameEl=document.querySelector('.purchase-name')||document.querySelector('.purchase-series');
      var productName=nameEl?nameEl.textContent.trim():'商品';
      var priceEl=document.querySelector('.purchase-price-num');
      var price=priceEl?priceEl.textContent.trim():'';
      var qtyEl=document.querySelector('.purchase-qty input');
      var qty=qtyEl?parseInt(qtyEl.value)||1:1;
      var sizeBtn=document.querySelector('.purchase-size.active');
      var size=sizeBtn?sizeBtn.querySelector('span:first-child').textContent.trim():'';
      var colorBtn=document.querySelector('.purchase-color.active');
      var color=colorBtn?colorBtn.dataset.color:'';

      var cart=getCart();
      var item={
        id:location.pathname,
        name:'【レンタル】'+productName,
        price:price,
        qty:qty,
        size:size,
        color:color,
        isRental:true,
        addedAt:new Date().toISOString()
      };
      var found=false;
      for(var i=0;i<cart.length;i++){
        if(cart[i].id===item.id&&cart[i].size===item.size&&cart[i].color===item.color){
          cart[i].qty+=qty;
          found=true;
          break;
        }
      }
      if(!found) cart.push(item);
      saveCart(cart);

      hideRentalModal();
      var toast=document.createElement('div');
      toast.style.cssText='position:fixed;bottom:32px;left:50%;transform:translateX(-50%);background:#2D2D2D;color:#fff;padding:16px 32px;border-radius:4px;font-size:14px;font-family:inherit;z-index:9999;box-shadow:0 8px 32px rgba(0,0,0,0.2);display:flex;align-items:center;gap:10px;animation:fadeInUp .3s';
      toast.innerHTML='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#C9A96E" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg><span>レンタル商品をカートに追加しました <span class="rental-badge">レンタル</span></span>';
      document.body.appendChild(toast);
      setTimeout(function(){toast.style.opacity='0';toast.style.transition='opacity .3s';setTimeout(function(){toast.remove()},300)},2500);
    }
    if(rentalYes)rentalYes.addEventListener('click',addRentalToCart);

    cartBtn.addEventListener('click',function(e){
      e.preventDefault();
      showRentalModal();
    });"""

modified = 0

for fpath in RENTAL_PAGES:
    if not os.path.exists(fpath):
        print(f'[SKIP] {fpath}: ファイルが存在しません')
        continue

    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'rental-modal-overlay' in content:
        print(f'[SKIP] {os.path.basename(os.path.dirname(fpath))}: 適用済み')
        continue

    # 1. CSSを追加
    style_pos = content.rfind('</style>')
    if style_pos == -1:
        print(f'[ERR] {fpath}: </style> not found')
        continue
    content = content[:style_pos] + MODAL_CSS + content[style_pos:]

    # 2. モーダルHTMLを追加（</body>の前）
    body_end = content.rfind('</body>')
    if body_end == -1:
        print(f'[ERR] {fpath}: </body> not found')
        continue
    content = content[:body_end] + MODAL_HTML + '\n' + content[body_end:]

    # 3. カートハンドラを置換
    if OLD_CART_HANDLER in content:
        content = content.replace(OLD_CART_HANDLER, NEW_CART_HANDLER)
    else:
        print(f'[WARN] {os.path.basename(os.path.dirname(fpath))}: カートハンドラの置換パターン不一致。手動確認してください。')
        # 書き込みは続行（CSS/HTMLは追加）

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)

    dirname = os.path.basename(os.path.dirname(fpath))
    print(f'[OK] {dirname}')
    modified += 1

print(f'\n完了: {modified}件修正')
