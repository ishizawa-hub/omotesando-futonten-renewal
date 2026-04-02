#!/usr/bin/env python3
"""
ギフト対応：数量が複数の場合に個別送り先を入力できる機能を全商品ページに追加。
- 数量 > 1 の場合、「全て同じ送り先」/「個別に送り先を指定」の選択肢を表示
- 「個別に送り先を指定」選択時、数量分の住所フォームを動的に生成
- カートアイテムに giftAddresses 配列を持たせる
"""
import sys
import os
import re
import glob

sys.stdout.reconfigure(encoding='utf-8')

SITE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'site-a')

# 追加CSS
GIFT_MULTI_CSS = """
/* Gift Multi-Destination */
.gift-dest-mode{display:none;margin-bottom:14px;padding:10px;background:var(--gold-faint,rgba(201,169,110,0.06));border-radius:4px}
.gift-dest-mode.show{display:flex;gap:16px;flex-wrap:wrap}
.gift-mode-option{display:flex;align-items:center;gap:6px;cursor:pointer;font-size:12px;font-weight:500;font-family:'Noto Sans JP',sans-serif;color:var(--text,#1A1A1A)}
.gift-mode-option input[type="radio"]{accent-color:#C9A96E;width:14px;height:14px}
.gift-dest-group{border:1px solid var(--border,#E5E5E5);padding:14px;margin-bottom:12px;position:relative}
.gift-dest-group-title{font-size:11px;font-weight:700;letter-spacing:0.1em;color:#C9A96E;margin-bottom:10px;font-family:'DM Sans',sans-serif}
@media(max-width:640px){.gift-dest-mode{flex-direction:column;gap:8px}}
"""

# 既存のギフトフィールドHTMLを、動的生成用のコンテナに置換
OLD_GIFT_FIELDS_PATTERN = r'''(<div class="gift-fields" id="giftFields">)\s*<div class="gift-fields-inner">\s*<p class="gift-note">.*?</p>\s*<div class="gift-row">.*?</div>\s*<div class="gift-row">.*?</div>\s*<div class="gift-field"><label>住所.*?</div>\s*<div class="gift-field"><label>建物名.*?</div>\s*<div class="gift-field"><label>メッセージカード.*?</div>\s*</div>\s*(</div>)'''

NEW_GIFT_FIELDS = r'''\1
        <div class="gift-fields-inner">
          <p class="gift-note">ギフトラッピング（無料）でお届けします。送付先をご入力ください。</p>
          <div class="gift-dest-mode" id="giftDestMode">
            <label class="gift-mode-option"><input type="radio" name="giftMode" value="same" checked> 全て同じ送り先</label>
            <label class="gift-mode-option"><input type="radio" name="giftMode" value="different"> 個別に送り先を指定</label>
          </div>
          <div id="giftDestContainer"></div>
        </div>
      \2'''

# JSの新しいギフトフォーム生成コード（cart scriptブロック内に追加）
GIFT_MULTI_JS = '''
    // ギフト複数送り先対応
    function giftFormHtml(idx, total) {
      var prefix = total > 1 ? '<div class="gift-dest-group-title">送り先 ' + (idx+1) + ' / ' + total + '</div>' : '';
      var sid = idx > 0 ? idx : '';
      return '<div class="gift-dest-group" data-dest-idx="'+idx+'">' + prefix
        + '<div class="gift-row">'
        + '<div class="gift-field"><label>お届け先氏名 <span style="color:#C9A96E">*</span></label><input type="text" class="giftName" placeholder="山田 太郎" required></div>'
        + '<div class="gift-field"><label>電話番号 <span style="color:#C9A96E">*</span></label><input type="tel" class="giftTel" placeholder="090-0000-0000" required></div>'
        + '</div>'
        + '<div class="gift-row">'
        + '<div class="gift-field"><label>郵便番号 <span style="color:#C9A96E">*</span></label><input type="text" class="giftZip" placeholder="000-0000" required></div>'
        + '<div class="gift-field"><label>配達希望時間</label>'
        + '<select class="giftTime" style="width:100%;padding:10px 12px;border:1px solid #E5E5E5;font-size:13px;font-family:Noto Sans JP,sans-serif;color:#1A1A1A;outline:none;border-radius:2px;background:#fff">'
        + '<option value="">指定なし</option><option value="am">午前中</option><option value="12-14">12:00〜14:00</option><option value="14-16">14:00〜16:00</option><option value="16-18">16:00〜18:00</option><option value="18-20">18:00〜20:00</option><option value="20-21">20:00〜21:00</option>'
        + '</select></div></div>'
        + '<div class="gift-field"><label>住所 <span style="color:#C9A96E">*</span></label><input type="text" class="giftAddr" placeholder="都道府県 市区町村 番地" required></div>'
        + '<div class="gift-field"><label>建物名・部屋番号（任意）</label><input type="text" class="giftBldg" placeholder="マンション名 000号室"></div>'
        + '<div class="gift-field"><label>メッセージカード（任意）</label><textarea class="giftMsg" placeholder="メッセージを入力してください（100文字以内）" maxlength="100"></textarea></div>'
        + '</div>';
    }

    var destContainer = document.getElementById('giftDestContainer');
    var destModeEl = document.getElementById('giftDestMode');
    var giftToggle = document.getElementById('giftToggle');
    var qtyInput = document.querySelector('.purchase-qty input');

    function updateGiftForms() {
      if (!destContainer || !giftToggle || !giftToggle.checked) return;
      var qty = qtyInput ? parseInt(qtyInput.value) || 1 : 1;
      var mode = 'same';
      var modeRadio = document.querySelector('input[name="giftMode"]:checked');
      if (modeRadio) mode = modeRadio.value;

      // 数量モード表示切替
      if (destModeEl) {
        if (qty > 1) destModeEl.classList.add('show');
        else { destModeEl.classList.remove('show'); mode = 'same'; }
      }

      var count = (mode === 'different') ? qty : 1;
      destContainer.innerHTML = '';
      for (var i = 0; i < count; i++) {
        destContainer.innerHTML += giftFormHtml(i, count);
      }
    }

    // イベント設定
    if (giftToggle) {
      giftToggle.addEventListener('change', function() {
        document.getElementById('giftFields').classList.toggle('open', this.checked);
        if (this.checked) updateGiftForms();
      });
    }
    if (qtyInput) {
      var qtyObserver = new MutationObserver(function(){ updateGiftForms(); });
      qtyObserver.observe(qtyInput, { attributes: true, attributeFilter: ['value'] });
      // ボタンクリック・手動入力にも対応
      qtyInput.addEventListener('input', updateGiftForms);
      qtyInput.addEventListener('change', updateGiftForms);
      // 数量ボタンのクリック後にも発火
      document.querySelectorAll('.purchase-qty button').forEach(function(btn){
        btn.addEventListener('click', function(){ setTimeout(updateGiftForms, 50); });
      });
    }
    if (destModeEl) {
      destModeEl.querySelectorAll('input[name="giftMode"]').forEach(function(r){
        r.addEventListener('change', updateGiftForms);
      });
    }
    // 初期表示
    if (giftToggle && giftToggle.checked) updateGiftForms();
'''

# カートに追加する際のギフト情報収集ロジックを更新
# 既存のギフトバリデーション＆情報収集部分を置換
OLD_GIFT_CART = '''      // Check gift mode
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
      }'''

NEW_GIFT_CART = '''      // Check gift mode
      var giftCheck=document.getElementById('giftToggle');
      var isGift=giftCheck&&giftCheck.checked;
      var giftInfo=null;
      var giftAddresses=[];

      if(isGift){
        var destGroups=document.querySelectorAll('.gift-dest-group');
        var valid=true;
        destGroups.forEach(function(g){
          var gn=g.querySelector('.giftName');
          var gt=g.querySelector('.giftTel');
          var gz=g.querySelector('.giftZip');
          var ga=g.querySelector('.giftAddr');
          if(!gn||!gn.value||!gt||!gt.value||!gz||!gz.value||!ga||!ga.value){valid=false;return;}
          giftAddresses.push({
            name:gn.value,tel:gt.value,zip:gz.value,addr:ga.value,
            bldg:(g.querySelector('.giftBldg')||{value:''}).value,
            time:(g.querySelector('.giftTime')||{value:''}).value,
            msg:(g.querySelector('.giftMsg')||{value:''}).value
          });
        });
        if(!valid||giftAddresses.length===0){
          alert('ギフト送付先の必須項目をすべてご入力ください。');
          return;
        }
        giftInfo=giftAddresses[0];
      }'''

# カートアイテムにgiftAddressesを追加
OLD_ITEM_OBJ = '''        id:location.pathname,
        name:productName,
        price:price,
        qty:qty,
        isGift:isGift,
        giftInfo:giftInfo,
        addedAt:new Date().toISOString()'''

NEW_ITEM_OBJ = '''        id:location.pathname,
        name:productName,
        price:price,
        qty:qty,
        isGift:isGift,
        giftInfo:giftInfo,
        giftAddresses:giftAddresses.length>1?giftAddresses:null,
        addedAt:new Date().toISOString()'''

pattern = os.path.join(SITE_DIR, 'products', '**', 'index.html')
files = glob.glob(pattern, recursive=True)

modified = 0
skipped = 0

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # ギフトオプションがあるページのみ
    if 'giftToggle' not in content:
        continue

    # 既に適用済みならスキップ
    if 'giftDestContainer' in content:
        skipped += 1
        continue

    # 1. CSS追加
    style_pos = content.rfind('</style>')
    if style_pos == -1:
        continue
    content = content[:style_pos] + GIFT_MULTI_CSS + content[style_pos:]

    # 2. ギフトフィールドHTMLを置換
    new_content = re.sub(OLD_GIFT_FIELDS_PATTERN, NEW_GIFT_FIELDS, content, flags=re.DOTALL)
    if new_content == content:
        dirname = os.path.basename(os.path.dirname(fpath))
        print(f'[WARN] {dirname}: ギフトフィールドHTMLパターン不一致')
        continue
    content = new_content

    # 3. ギフトカート処理のJS置換
    if OLD_GIFT_CART in content:
        content = content.replace(OLD_GIFT_CART, NEW_GIFT_CART)
    else:
        dirname = os.path.basename(os.path.dirname(fpath))
        print(f'[WARN] {dirname}: ギフトカートJSパターン不一致')

    # 4. カートアイテムオブジェクトにgiftAddresses追加
    if OLD_ITEM_OBJ in content:
        content = content.replace(OLD_ITEM_OBJ, NEW_ITEM_OBJ)

    # 5. ギフト複数送り先JS追加（</script>の最後の前）
    # カートスクリプトの閉じ直前に追加
    insert_marker = "    // If gift, redirect to gift checkout"
    if insert_marker in content:
        content = content.replace(insert_marker, GIFT_MULTI_JS + '\n' + insert_marker)
    else:
        # フォールバック: ギフトチェックアウトリダイレクトがない場合、})();の前に
        pass

    # 6. giftToggleの既存onchangeを削除（JSで管理するため）
    content = content.replace(
        '''onchange="document.getElementById('giftFields').classList.toggle('open',this.checked)"''',
        ''
    )

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)

    dirname = os.path.basename(os.path.dirname(fpath))
    print(f'[OK] {dirname}')
    modified += 1

print(f'\n完了: {modified}件修正, {skipped}件スキップ（適用済み）')
