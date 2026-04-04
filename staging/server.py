# -*- coding: utf-8 -*-
"""
表参道布団店 ステージングサーバー
Flask ベースの REST API + 静的ファイル配信
"""

import json
import os
import time
import hashlib
import secrets
from datetime import datetime
from pathlib import Path
from functools import wraps

from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS

# ============================================================
# 設定
# ============================================================
BASE_DIR = Path(__file__).parent
SITE_DIR = BASE_DIR.parent / 'site-a'
DATA_DIR = BASE_DIR / 'data'
CONFIG_PATH = BASE_DIR / 'staging-config.json'

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

config = load_config()

app = Flask(__name__, static_folder=None)
CORS(app, supports_credentials=True)

# ============================================================
# JSONファイルDB ヘルパー
# ============================================================
def db_path(name: str) -> Path:
    return DATA_DIR / f'{name}.json'

def db_read(name: str):
    p = db_path(name)
    if p.exists():
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    return [] if name != 'page-content' and name != 'settings' else {}

def db_write(name: str, data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(db_path(name), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def gen_id(prefix=''):
    return f"{prefix}{int(time.time())}_{secrets.token_hex(4)}"

# ============================================================
# 認証
# ============================================================
TOKENS = {}  # token -> user_info

def create_token(user_info):
    token = secrets.token_hex(32)
    TOKENS[token] = {**user_info, 'created_at': time.time()}
    return token

def get_current_user():
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        token = auth[7:]
        return TOKENS.get(token)
    return None

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': '認証が必要です'}), 401
        return f(*args, **kwargs)
    return decorated

# ============================================================
# 静的ファイル配信
# ============================================================
@app.route('/')
@app.route('/<path:filepath>')
def serve_static(filepath='index.html'):
    """site-a/ 配下の静的ファイルを配信"""
    full_path = SITE_DIR / filepath
    if full_path.is_dir():
        full_path = full_path / 'index.html'
        filepath = str(Path(filepath) / 'index.html')
    if full_path.exists():
        directory = str(full_path.parent)
        filename = full_path.name
        return send_from_directory(directory, filename)
    abort(404)

# ============================================================
# 認証 API
# ============================================================
@app.route('/oft/v1/admin/auth/login', methods=['POST'])
def api_login():
    data = request.get_json(force=True) or {}
    username = data.get('username') or data.get('email', '')
    password = data.get('password', '')

    # ステージング: 任意の認証情報で許可
    if not username:
        return jsonify({'error': 'ユーザー名を入力してください'}), 400

    user_info = {
        'id': 1,
        'name': '管理者',
        'email': username,
        'role': 'administrator'
    }
    token = create_token(user_info)
    return jsonify({
        'token': token,
        'user': user_info
    })

@app.route('/oft/v1/auth/register', methods=['POST'])
def api_register():
    data = request.get_json(force=True) or {}
    email = data.get('email', '')
    name = data.get('name', data.get('last_name', '') + data.get('first_name', ''))

    if not email:
        return jsonify({'error': 'メールアドレスが必要です'}), 400

    # 顧客データに追加
    customers = db_read('customers')
    new_customer = {
        'id': gen_id('c_'),
        'name': name,
        'email': email,
        'phone': data.get('phone', ''),
        'registeredAt': datetime.now().isoformat(),
        'status': 'アクティブ',
        'newsletter': True,
        'orders': 0,
        'totalSpent': 0,
        'memo': ''
    }
    customers.append(new_customer)
    db_write('customers', customers)

    # メール送信
    try:
        from email_sender import send_registration_emails
        send_registration_emails(new_customer, config)
    except Exception as e:
        print(f'[Email] 送信失敗: {e}')

    token = create_token({'id': new_customer['id'], 'name': name, 'email': email})
    return jsonify({
        'token': token,
        'user': {'id': new_customer['id'], 'name': name, 'email': email}
    })

# ============================================================
# 商品 API
# ============================================================
@app.route('/oft/v1/products', methods=['GET'])
def api_get_products():
    products = db_read('products')
    category = request.args.get('category')
    if category:
        products = [p for p in products if p.get('category') == category]
    return jsonify(products)

@app.route('/oft/v1/admin/products', methods=['POST'])
@require_admin
def api_create_product():
    data = request.get_json(force=True) or {}
    data['id'] = gen_id('p_')
    data['createdAt'] = datetime.now().isoformat()
    data['updatedAt'] = datetime.now().isoformat()
    products = db_read('products')
    products.append(data)
    db_write('products', products)
    return jsonify(data), 201

@app.route('/oft/v1/admin/products/<product_id>', methods=['PUT'])
@require_admin
def api_update_product(product_id):
    data = request.get_json(force=True) or {}
    products = db_read('products')
    for i, p in enumerate(products):
        if str(p.get('id')) == str(product_id):
            data['id'] = product_id
            data['updatedAt'] = datetime.now().isoformat()
            data['createdAt'] = p.get('createdAt', '')
            products[i] = {**p, **data}
            db_write('products', products)
            return jsonify(products[i])
    return jsonify({'error': '商品が見つかりません'}), 404

@app.route('/oft/v1/admin/products/<product_id>', methods=['DELETE'])
@require_admin
def api_delete_product(product_id):
    products = db_read('products')
    products = [p for p in products if str(p.get('id')) != str(product_id)]
    db_write('products', products)
    return jsonify({'success': True})

# ============================================================
# マガジン API
# ============================================================
@app.route('/oft/v1/admin/magazine', methods=['GET'])
def api_get_magazines():
    return jsonify(db_read('magazine'))

@app.route('/oft/v1/admin/magazine', methods=['POST'])
@require_admin
def api_create_magazine():
    data = request.get_json(force=True) or {}
    data['id'] = gen_id('m_')
    data['createdAt'] = datetime.now().isoformat()
    data['updatedAt'] = datetime.now().isoformat()
    articles = db_read('magazine')
    articles.append(data)
    db_write('magazine', articles)
    return jsonify(data), 201

@app.route('/oft/v1/admin/magazine/<article_id>', methods=['PUT'])
@require_admin
def api_update_magazine(article_id):
    data = request.get_json(force=True) or {}
    articles = db_read('magazine')
    for i, a in enumerate(articles):
        if str(a.get('id')) == str(article_id):
            data['id'] = article_id
            data['updatedAt'] = datetime.now().isoformat()
            articles[i] = {**a, **data}
            db_write('magazine', articles)
            return jsonify(articles[i])
    return jsonify({'error': '記事が見つかりません'}), 404

@app.route('/oft/v1/admin/magazine/<article_id>', methods=['DELETE'])
@require_admin
def api_delete_magazine(article_id):
    articles = db_read('magazine')
    articles = [a for a in articles if str(a.get('id')) != str(article_id)]
    db_write('magazine', articles)
    return jsonify({'success': True})

# ============================================================
# 注文 API
# ============================================================
@app.route('/oft/v1/admin/orders', methods=['GET'])
def api_get_orders():
    return jsonify(db_read('orders'))

@app.route('/oft/v1/admin/orders/<order_id>', methods=['PUT'])
@require_admin
def api_update_order(order_id):
    data = request.get_json(force=True) or {}
    orders = db_read('orders')
    for i, o in enumerate(orders):
        if str(o.get('id')) == str(order_id):
            orders[i] = {**o, **data, 'updatedAt': datetime.now().isoformat()}
            db_write('orders', orders)
            return jsonify(orders[i])
    return jsonify({'error': '注文が見つかりません'}), 404

# ============================================================
# 顧客 API
# ============================================================
@app.route('/oft/v1/admin/customers', methods=['GET'])
def api_get_customers():
    return jsonify(db_read('customers'))

@app.route('/oft/v1/admin/customers', methods=['POST'])
@require_admin
def api_create_customer():
    data = request.get_json(force=True) or {}
    data['id'] = gen_id('c_')
    data['registeredAt'] = datetime.now().isoformat()
    customers = db_read('customers')
    customers.append(data)
    db_write('customers', customers)
    return jsonify(data), 201

@app.route('/oft/v1/admin/customers/<customer_id>', methods=['PUT'])
@require_admin
def api_update_customer(customer_id):
    data = request.get_json(force=True) or {}
    customers = db_read('customers')
    for i, c in enumerate(customers):
        if str(c.get('id')) == str(customer_id):
            customers[i] = {**c, **data}
            db_write('customers', customers)
            return jsonify(customers[i])
    return jsonify({'error': '顧客が見つかりません'}), 404

@app.route('/oft/v1/admin/customers/<customer_id>', methods=['DELETE'])
@require_admin
def api_delete_customer(customer_id):
    customers = db_read('customers')
    customers = [c for c in customers if str(c.get('id')) != str(customer_id)]
    db_write('customers', customers)
    return jsonify({'success': True})

# ============================================================
# お問い合わせ API
# ============================================================
@app.route('/oft/v1/admin/inquiries', methods=['GET'])
def api_get_inquiries():
    return jsonify(db_read('inquiries'))

@app.route('/oft/v1/admin/inquiries/<inquiry_id>', methods=['PUT'])
@require_admin
def api_update_inquiry(inquiry_id):
    data = request.get_json(force=True) or {}
    inquiries = db_read('inquiries')
    for i, inq in enumerate(inquiries):
        if str(inq.get('id')) == str(inquiry_id):
            inquiries[i] = {**inq, **data}
            db_write('inquiries', inquiries)
            return jsonify(inquiries[i])
    return jsonify({'error': 'お問い合わせが見つかりません'}), 404

@app.route('/oft/v1/admin/inquiries/<inquiry_id>', methods=['DELETE'])
@require_admin
def api_delete_inquiry(inquiry_id):
    inquiries = db_read('inquiries')
    inquiries = [inq for inq in inquiries if str(inq.get('id')) != str(inquiry_id)]
    db_write('inquiries', inquiries)
    return jsonify({'success': True})

# ============================================================
# ページコンテンツ API
# ============================================================
@app.route('/oft/v1/page-content', methods=['GET'])
def api_get_page_content():
    """公開エンドポイント: フロントエンド用"""
    return jsonify(db_read('page-content'))

@app.route('/oft/v1/admin/pages/<page_id>', methods=['PUT'])
@require_admin
def api_update_page_content(page_id):
    data = request.get_json(force=True) or {}
    content = db_read('page-content')
    content[page_id] = data
    db_write('page-content', content)
    return jsonify(content)

# ============================================================
# 設定 API
# ============================================================
@app.route('/oft/v1/admin/settings', methods=['GET'])
@require_admin
def api_get_settings():
    return jsonify(db_read('settings'))

@app.route('/oft/v1/admin/settings', methods=['PUT'])
@require_admin
def api_update_settings():
    data = request.get_json(force=True) or {}
    settings = db_read('settings')
    settings.update(data)
    db_write('settings', settings)
    return jsonify(settings)

# ============================================================
# 在庫 API
# ============================================================
@app.route('/oft/v1/admin/inventory', methods=['GET'])
def api_get_inventory():
    """商品データから在庫情報を抽出"""
    products = db_read('products')
    inventory = []
    for p in products:
        inventory.append({
            'id': p.get('id'),
            'name': p.get('name', ''),
            'stock': p.get('stock', 0),
            'status': p.get('status', '公開')
        })
    return jsonify(inventory)

@app.route('/oft/v1/admin/inventory/<product_id>', methods=['PUT'])
@require_admin
def api_update_inventory(product_id):
    data = request.get_json(force=True) or {}
    products = db_read('products')
    for i, p in enumerate(products):
        if str(p.get('id')) == str(product_id):
            products[i]['stock'] = data.get('quantity', data.get('stock', p.get('stock', 0)))
            db_write('products', products)
            return jsonify(products[i])
    return jsonify({'error': '商品が見つかりません'}), 404

# ============================================================
# チェックアウト API (Stripe テストモード)
# ============================================================
@app.route('/oft/v1/checkout/create-session', methods=['POST'])
def api_create_checkout():
    data = request.get_json(force=True) or {}
    items = data.get('items', [])
    shipping = data.get('shipping', {})
    email = data.get('email', '')

    stripe_key = config.get('stripe_secret_key', '')

    if stripe_key and stripe_key != 'sk_test_REPLACE_ME':
        # Stripe テストモードでセッション作成
        try:
            import stripe
            stripe.api_key = stripe_key

            line_items = []
            for item in items:
                line_items.append({
                    'price_data': {
                        'currency': 'jpy',
                        'product_data': {'name': item.get('name', '商品')},
                        'unit_amount': int(item.get('price', 0)),
                    },
                    'quantity': int(item.get('qty', 1)),
                })

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=request.host_url + 'checkout/complete.html?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.host_url + 'checkout/',
                customer_email=email,
                metadata={'shipping': json.dumps(shipping, ensure_ascii=False)},
            )

            return jsonify({'url': session.url, 'session_id': session.id})
        except Exception as e:
            print(f'[Stripe] エラー: {e}')
            # Stripe失敗時はダミーフローにフォールバック

    # ダミー購入完了フロー（Stripeキー未設定時）
    order_id = gen_id('ord_')
    order_total = sum(int(item.get('price', 0)) * int(item.get('qty', 1)) for item in items)

    new_order = {
        'id': order_id,
        'orderNumber': f'OFT-{int(time.time()) % 100000:05d}',
        'customer': {
            'name': f"{shipping.get('last_name', '')} {shipping.get('first_name', '')}".strip(),
            'email': email,
            'phone': shipping.get('phone', ''),
        },
        'shipping': shipping,
        'items': items,
        'subtotal': order_total,
        'shipping_fee': 0 if order_total >= 30000 else 880,
        'total': order_total + (0 if order_total >= 30000 else 880),
        'status': '処理待ち',
        'payment': 'クレジットカード',
        'orderedAt': datetime.now().isoformat(),
        'updatedAt': datetime.now().isoformat(),
    }

    # 注文データ保存
    orders = db_read('orders')
    orders.append(new_order)
    db_write('orders', orders)

    # 顧客データ更新/作成
    _update_customer_from_order(new_order)

    # メール送信
    try:
        from email_sender import send_order_emails
        send_order_emails(new_order, config)
    except Exception as e:
        print(f'[Email] 送信失敗: {e}')

    return jsonify({
        'url': f'/checkout/complete.html?order_id={order_id}',
        'order_id': order_id,
        'demo': True
    })

def _update_customer_from_order(order):
    """注文データから顧客データを更新/作成"""
    customers = db_read('customers')
    email = order['customer']['email']

    found = False
    for i, c in enumerate(customers):
        if c.get('email') == email:
            customers[i]['orders'] = c.get('orders', 0) + 1
            customers[i]['totalSpent'] = c.get('totalSpent', 0) + order['total']
            customers[i]['lastOrderAt'] = order['orderedAt']
            found = True
            break

    if not found:
        customers.append({
            'id': gen_id('c_'),
            'name': order['customer']['name'],
            'email': email,
            'phone': order['customer'].get('phone', ''),
            'registeredAt': datetime.now().isoformat(),
            'status': 'アクティブ',
            'newsletter': False,
            'orders': 1,
            'totalSpent': order['total'],
            'lastOrderAt': order['orderedAt'],
            'memo': '購入経由で自動登録',
        })

    db_write('customers', customers)

# ============================================================
# Stripe Webhook (テスト用)
# ============================================================
@app.route('/oft/v1/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Stripe Webhook: 決済完了時の処理"""
    payload = request.get_data(as_text=True)

    try:
        event = json.loads(payload)
    except Exception:
        return jsonify({'error': 'Invalid payload'}), 400

    if event.get('type') == 'checkout.session.completed':
        session = event['data']['object']
        # 注文データ生成
        shipping = json.loads(session.get('metadata', {}).get('shipping', '{}'))
        order_id = gen_id('ord_')

        new_order = {
            'id': order_id,
            'orderNumber': f'OFT-{int(time.time()) % 100000:05d}',
            'customer': {
                'name': session.get('customer_details', {}).get('name', ''),
                'email': session.get('customer_email', ''),
            },
            'shipping': shipping,
            'total': session.get('amount_total', 0),
            'status': '処理待ち',
            'payment': 'クレジットカード (Stripe)',
            'stripeSessionId': session.get('id'),
            'orderedAt': datetime.now().isoformat(),
        }

        orders = db_read('orders')
        orders.append(new_order)
        db_write('orders', orders)

        _update_customer_from_order(new_order)

        try:
            from email_sender import send_order_emails
            send_order_emails(new_order, config)
        except Exception as e:
            print(f'[Email] Webhook送信失敗: {e}')

    return jsonify({'received': True})

# ============================================================
# ダッシュボード API
# ============================================================
@app.route('/oft/v1/admin/dashboard', methods=['GET'])
@require_admin
def api_dashboard():
    products = db_read('products')
    orders = db_read('orders')
    customers = db_read('customers')
    magazines = db_read('magazine')

    return jsonify({
        'products': {'count': len(products)},
        'orders': {
            'count': len(orders),
            'totalSales': sum(o.get('total', 0) for o in orders),
            'pending': len([o for o in orders if o.get('status') in ['処理待ち', '未処理']]),
        },
        'customers': {'count': len(customers)},
        'magazines': {'count': len(magazines)},
    })

# ============================================================
# 売上分析 API
# ============================================================
@app.route('/oft/v1/admin/sales/summary', methods=['GET'])
@require_admin
def api_sales_summary():
    """売上サマリー（日/月/年/累計）"""
    orders = db_read('orders')
    # キャンセル除外
    valid = [o for o in orders if o.get('status') != 'キャンセル']

    period = request.args.get('period', 'monthly')  # daily, monthly, yearly, cumulative
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))

    from datetime import timedelta

    if period == 'daily':
        target = datetime.fromisoformat(date_str).date()
        current = [o for o in valid if datetime.fromisoformat(o['orderedAt']).date() == target]
        prev_target = target.replace(year=target.year - 1)
        prev = [o for o in valid if datetime.fromisoformat(o['orderedAt']).date() == prev_target]
    elif period == 'monthly':
        parts = date_str.split('-')
        y, m = int(parts[0]), int(parts[1])
        current = [o for o in valid if datetime.fromisoformat(o['orderedAt']).year == y and datetime.fromisoformat(o['orderedAt']).month == m]
        prev = [o for o in valid if datetime.fromisoformat(o['orderedAt']).year == y-1 and datetime.fromisoformat(o['orderedAt']).month == m]
    elif period == 'yearly':
        y = int(date_str.split('-')[0])
        current = [o for o in valid if datetime.fromisoformat(o['orderedAt']).year == y]
        prev = [o for o in valid if datetime.fromisoformat(o['orderedAt']).year == y-1]
    else:  # cumulative
        start = request.args.get('start', '2024-01-01')
        end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
        s = datetime.fromisoformat(start).date()
        e = datetime.fromisoformat(end).date()
        current = [o for o in valid if s <= datetime.fromisoformat(o['orderedAt']).date() <= e]
        # 前年同期間
        ps = s.replace(year=s.year - 1)
        pe = e.replace(year=e.year - 1)
        prev = [o for o in valid if ps <= datetime.fromisoformat(o['orderedAt']).date() <= pe]

    def calc_summary(olist):
        total = sum(o.get('total', 0) for o in olist)
        count = len(olist)
        avg = round(total / count) if count else 0
        # 商品別
        items = {}
        colors = {}
        for o in olist:
            for it in o.get('items', []):
                name = it.get('name', '不明')
                color = it.get('color', '未設定')
                qty = int(it.get('qty', 1))
                price = int(it.get('price', 0))
                sales = price * qty
                items.setdefault(name, {'name': name, 'qty': 0, 'sales': 0})
                items[name]['qty'] += qty
                items[name]['sales'] += sales
                colors.setdefault(color, {'color': color, 'qty': 0, 'sales': 0})
                colors[color]['qty'] += qty
                colors[color]['sales'] += sales
        item_ranking = sorted(items.values(), key=lambda x: -x['sales'])
        color_ranking = sorted(colors.values(), key=lambda x: -x['sales'])
        return {
            'total': total, 'count': count, 'avg': avg,
            'itemRanking': item_ranking, 'colorRanking': color_ranking
        }

    return jsonify({
        'current': calc_summary(current),
        'previous': calc_summary(prev),
        'currentOrders': current,
        'previousOrders': prev
    })

# ============================================================
# サンプルデータ初期化
# ============================================================
def _init_sample_data():
    """初回起動時のサンプルデータ生成"""
    print('[Init] サンプルデータを生成中...')

    # 商品
    db_write('products', [
        {
            'id': 'p_001', 'name': 'Premium RDS Down 冬用本掛け',
            'series': 'Premium RDS Down Series', 'category': '掛け布団',
            'season': '冬用', 'status': '公開', 'stock': 12,
            'subtitle': '最高級リサイクルダウンの暖かさ',
            'catchcopy': '新品羽毛を超える美しさ',
            'description': 'RDS認証リサイクルダウンを使用した最高級掛け布団。白州の天然水で徹底洗浄。',
            'sizes': [
                {'name': 'S', 'dimensions': '150×210cm', 'fill': '1.3kg', 'price': 198000},
                {'name': 'D', 'dimensions': '190×210cm', 'fill': '1.7kg', 'price': 268000}
            ],
            'images': [
                {'url': '/images/generated/premium-rds-winter-hero.jpg', 'alt': 'Premium RDS Down', 'color': '共通'}
            ],
            'colors': [{'name': 'White', 'code': '#FFFFFF', 'border': True}],
            'specs': [
                {'key': '羽毛種', 'value': 'ホワイトグースダウン95%'},
                {'key': 'ダウンパワー', 'value': '440dp'},
                {'key': '洗浄', 'value': '白州天然水洗浄'}
            ],
            'createdAt': '2024-01-15T00:00:00'
        },
        {
            'id': 'p_002', 'name': 'Clean Cycle Down 冬用本掛け',
            'series': 'Clean Cycle Down Series', 'category': '掛け布団',
            'season': '冬用', 'status': '公開', 'stock': 25,
            'description': 'リサイクルダウンで環境に優しい掛け布団。',
            'sizes': [
                {'name': 'S', 'dimensions': '150×210cm', 'fill': '1.2kg', 'price': 53800},
                {'name': 'SD', 'dimensions': '170×210cm', 'fill': '1.4kg', 'price': 63800},
                {'name': 'D', 'dimensions': '190×210cm', 'fill': '1.6kg', 'price': 73800}
            ],
            'images': [
                {'url': '/images/generated/clean-cycle-winter-hero.jpg', 'alt': 'Clean Cycle Down', 'color': '共通'}
            ],
            'colors': [{'name': 'White', 'code': '#FFFFFF', 'border': True}],
            'createdAt': '2024-02-01T00:00:00'
        },
        {
            'id': 'p_003', 'name': 'ホワイトグースダウン枕',
            'series': 'Pillow Series', 'category': '枕',
            'status': '公開', 'stock': 20,
            'description': '最高品質のグースダウンを贅沢に使用した枕。',
            'sizes': [{'name': 'M', 'dimensions': '43×63cm', 'fill': '0.5kg', 'price': 27800}],
            'images': [],
            'createdAt': '2024-03-01T00:00:00'
        }
    ])

    # マガジン
    db_write('magazine', [
        {
            'id': 'm_001', 'title': '合い掛け布団の魅力 ～春秋の眠りを快適に～',
            'category': 'コラム', 'date': '2024-03-15', 'status': '公開',
            'slug': 'aigake', 'heroImage': '/images/mag-01.jpg',
            'body': '<p>合い掛け布団は春と秋に最適な寝具です。</p>',
            'tags': ['羽毛布団', '春秋'],
            'createdAt': '2024-03-15T00:00:00'
        },
        {
            'id': 'm_002', 'title': '羽毛布団のお手入れガイド',
            'category': 'ケアガイド', 'date': '2024-04-01', 'status': '公開',
            'slug': 'care-guide', 'heroImage': '/images/mag-02.jpg',
            'body': '<p>羽毛布団を長く使うためのお手入れ方法をご紹介します。</p>',
            'tags': ['お手入れ', '羽毛布団'],
            'createdAt': '2024-04-01T00:00:00'
        }
    ])

    # 注文
    db_write('orders', [
        # --- 既存 ord_001 ---
        {
            'id': 'ord_001',
            'orderNumber': 'OFT-00001',
            'customer': {'name': '山田 太郎', 'email': 'yamada@example.com', 'phone': '03-1234-5678'},
            'shipping': {'last_name': '山田', 'first_name': '太郎', 'zip': '150-0001', 'prefecture': '東京都', 'city': '渋谷区神宮前'},
            'items': [{'name': 'Clean Cycle Down 冬用本掛け S', 'price': 53800, 'qty': 1, 'color': 'White', 'image': ''}],
            'subtotal': 53800, 'shipping_fee': 0, 'total': 53800,
            'status': '処理待ち', 'payment': 'クレジットカード',
            'orderedAt': '2024-12-01T10:30:00'
        },
        # --- 2024年 (10件: ord_002〜ord_011) ---
        {
            'id': 'ord_002', 'orderNumber': 'OFT-00002',
            'customer': {'name': '佐藤 花子', 'email': 'sato@example.com', 'phone': '090-9876-5432'},
            'shipping': {'last_name': '佐藤', 'first_name': '花子', 'zip': '107-0062', 'prefecture': '東京都', 'city': '港区南青山'},
            'items': [{'name': 'Premium RDS Down 冬用本掛け S', 'price': 82500, 'qty': 1, 'color': 'White', 'image': ''}],
            'subtotal': 82500, 'shipping_fee': 0, 'total': 82500,
            'status': '完了', 'payment': 'クレジットカード',
            'orderedAt': '2024-01-15T11:20:00'
        },
        {
            'id': 'ord_003', 'orderNumber': 'OFT-00003',
            'customer': {'name': '田中 美咲', 'email': 'tanaka@example.com', 'phone': '080-1111-2222'},
            'shipping': {'last_name': '田中', 'first_name': '美咲', 'zip': '150-0033', 'prefecture': '東京都', 'city': '渋谷区猿楽町'},
            'items': [
                {'name': 'オリジナル枕', 'price': 16500, 'qty': 2, 'color': 'White', 'image': ''},
                {'name': 'シルクピローケース', 'price': 8800, 'qty': 2, 'color': 'Navy', 'image': ''}
            ],
            'subtotal': 50600, 'shipping_fee': 0, 'total': 50600,
            'status': '完了', 'payment': 'クレジットカード',
            'orderedAt': '2024-02-20T14:45:00'
        },
        {
            'id': 'ord_004', 'orderNumber': 'OFT-00004',
            'customer': {'name': '鈴木 健一', 'email': 'suzuki.k@example.com', 'phone': '03-5555-6666'},
            'shipping': {'last_name': '鈴木', 'first_name': '健一', 'zip': '160-0022', 'prefecture': '東京都', 'city': '新宿区新宿'},
            'items': [{'name': 'Clean Cycle Down 冬用本掛け D', 'price': 64800, 'qty': 1, 'color': 'White', 'image': ''}],
            'subtotal': 64800, 'shipping_fee': 0, 'total': 64800,
            'status': '完了', 'payment': 'クレジットカード',
            'orderedAt': '2024-03-10T09:30:00'
        },
        {
            'id': 'ord_005', 'orderNumber': 'OFT-00005',
            'customer': {'name': '佐藤 花子', 'email': 'sato@example.com', 'phone': '090-9876-5432'},
            'shipping': {'last_name': '佐藤', 'first_name': '花子', 'zip': '107-0062', 'prefecture': '東京都', 'city': '港区南青山'},
            'items': [{'name': 'シルクピローケース', 'price': 8800, 'qty': 1, 'color': 'Ivory', 'image': ''}],
            'subtotal': 8800, 'shipping_fee': 880, 'total': 9680,
            'status': '完了', 'payment': 'クレジットカード',
            'orderedAt': '2024-04-22T16:10:00'
        },
        {
            'id': 'ord_006', 'orderNumber': 'OFT-00006',
            'customer': {'name': '高橋 直子', 'email': 'takahashi@example.com', 'phone': '090-3333-4444'},
            'shipping': {'last_name': '高橋', 'first_name': '直子', 'zip': '158-0083', 'prefecture': '東京都', 'city': '世田谷区奥沢'},
            'items': [
                {'name': 'Clean Cycle Down 合掛け S', 'price': 38500, 'qty': 1, 'color': 'Beige', 'image': ''},
                {'name': 'オリジナル枕', 'price': 16500, 'qty': 1, 'color': 'White', 'image': ''}
            ],
            'subtotal': 55000, 'shipping_fee': 0, 'total': 55000,
            'status': '完了', 'payment': 'クレジットカード',
            'orderedAt': '2024-05-18T10:00:00'
        },
        {
            'id': 'ord_007', 'orderNumber': 'OFT-00007',
            'customer': {'name': '山田 太郎', 'email': 'yamada@example.com', 'phone': '03-1234-5678'},
            'shipping': {'last_name': '山田', 'first_name': '太郎', 'zip': '150-0001', 'prefecture': '東京都', 'city': '渋谷区神宮前'},
            'items': [{'name': 'Premium RDS Down 合掛け S', 'price': 60500, 'qty': 1, 'color': 'Gray', 'image': ''}],
            'subtotal': 60500, 'shipping_fee': 0, 'total': 60500,
            'status': '完了', 'payment': 'クレジットカード',
            'orderedAt': '2024-07-05T13:15:00'
        },
        {
            'id': 'ord_008', 'orderNumber': 'OFT-00008',
            'customer': {'name': '伊藤 裕子', 'email': 'ito@example.com', 'phone': '080-7777-8888'},
            'shipping': {'last_name': '伊藤', 'first_name': '裕子', 'zip': '106-0032', 'prefecture': '東京都', 'city': '港区六本木'},
            'items': [{'name': 'Premium RDS Down 冬用本掛け D', 'price': 99000, 'qty': 1, 'color': 'White', 'image': ''}],
            'subtotal': 99000, 'shipping_fee': 0, 'total': 99000,
            'status': '完了', 'payment': 'クレジットカード',
            'orderedAt': '2024-09-12T11:00:00'
        },
        {
            'id': 'ord_009', 'orderNumber': 'OFT-00009',
            'customer': {'name': '田中 美咲', 'email': 'tanaka@example.com', 'phone': '080-1111-2222'},
            'shipping': {'last_name': '田中', 'first_name': '美咲', 'zip': '150-0033', 'prefecture': '東京都', 'city': '渋谷区猿楽町'},
            'items': [{'name': 'オーガニックコットン カバーセット S', 'price': 22000, 'qty': 1, 'color': 'Natural', 'image': ''}],
            'subtotal': 22000, 'shipping_fee': 880, 'total': 22880,
            'status': 'キャンセル', 'payment': 'クレジットカード',
            'orderedAt': '2024-10-03T18:30:00'
        },
        {
            'id': 'ord_010', 'orderNumber': 'OFT-00010',
            'customer': {'name': '渡辺 翔太', 'email': 'watanabe@example.com', 'phone': '090-5555-9999'},
            'shipping': {'last_name': '渡辺', 'first_name': '翔太', 'zip': '153-0064', 'prefecture': '東京都', 'city': '目黒区下目黒'},
            'items': [
                {'name': 'Clean Cycle Down 冬用本掛け S', 'price': 53800, 'qty': 1, 'color': 'White', 'image': ''},
                {'name': 'オリジナル枕', 'price': 16500, 'qty': 1, 'color': 'White', 'image': ''}
            ],
            'subtotal': 70300, 'shipping_fee': 0, 'total': 70300,
            'status': '完了', 'payment': 'クレジットカード',
            'orderedAt': '2024-11-08T15:45:00'
        },
        {
            'id': 'ord_011', 'orderNumber': 'OFT-00011',
            'customer': {'name': '高橋 直子', 'email': 'takahashi@example.com', 'phone': '090-3333-4444'},
            'shipping': {'last_name': '高橋', 'first_name': '直子', 'zip': '158-0083', 'prefecture': '東京都', 'city': '世田谷区奥沢'},
            'items': [{'name': 'Premium RDS Down 肌掛け S', 'price': 44000, 'qty': 1, 'color': 'White', 'image': ''}],
            'subtotal': 44000, 'shipping_fee': 0, 'total': 44000,
            'status': '完了', 'payment': 'クレジットカード',
            'orderedAt': '2024-11-25T12:00:00'
        },
        # --- 2025年 (12件: ord_012〜ord_023) ---
        {
            'id': 'ord_012', 'orderNumber': 'OFT-00012',
            'customer': {'name': '佐藤 花子', 'email': 'sato@example.com', 'phone': '090-9876-5432'},
            'shipping': {'last_name': '佐藤', 'first_name': '花子', 'zip': '107-0062', 'prefecture': '東京都', 'city': '港区南青山'},
            'items': [{'name': 'オーガニックコットン カバーセット D', 'price': 27500, 'qty': 1, 'color': 'Natural', 'image': ''}],
            'subtotal': 27500, 'shipping_fee': 880, 'total': 28380,
            'status': '完了', 'payment': 'クレジットカード',
            'orderedAt': '2025-01-10T10:20:00'
        },
        {
            'id': 'ord_013', 'orderNumber': 'OFT-00013',
            'customer': {'name': '伊藤 裕子', 'email': 'ito@example.com', 'phone': '080-7777-8888'},
            'shipping': {'last_name': '伊藤', 'first_name': '裕子', 'zip': '106-0032', 'prefecture': '東京都', 'city': '港区六本木'},
            'items': [
                {'name': 'シルクピローケース', 'price': 8800, 'qty': 2, 'color': 'Ivory', 'image': ''},
                {'name': 'オリジナル枕', 'price': 16500, 'qty': 1, 'color': 'White', 'image': ''}
            ],
            'subtotal': 34100, 'shipping_fee': 0, 'total': 34100,
            'status': '完了', 'payment': 'クレジットカード',
            'orderedAt': '2025-01-28T14:00:00'
        },
        {
            'id': 'ord_014', 'orderNumber': 'OFT-00014',
            'customer': {'name': '鈴木 健一', 'email': 'suzuki.k@example.com', 'phone': '03-5555-6666'},
            'shipping': {'last_name': '鈴木', 'first_name': '健一', 'zip': '160-0022', 'prefecture': '東京都', 'city': '新宿区新宿'},
            'items': [{'name': 'Premium RDS Down 冬用本掛け S', 'price': 82500, 'qty': 1, 'color': 'White', 'image': ''}],
            'subtotal': 82500, 'shipping_fee': 0, 'total': 82500,
            'status': '完了', 'payment': 'クレジットカード',
            'orderedAt': '2025-02-14T09:45:00'
        },
        {
            'id': 'ord_015', 'orderNumber': 'OFT-00015',
            'customer': {'name': '中村 恵', 'email': 'nakamura@example.com', 'phone': '03-2222-3333'},
            'shipping': {'last_name': '中村', 'first_name': '恵', 'zip': '152-0035', 'prefecture': '東京都', 'city': '目黒区自由が丘'},
            'items': [
                {'name': 'Clean Cycle Down 合掛け S', 'price': 38500, 'qty': 1, 'color': 'Beige', 'image': ''},
                {'name': 'シルクピローケース', 'price': 8800, 'qty': 1, 'color': 'Navy', 'image': ''}
            ],
            'subtotal': 47300, 'shipping_fee': 0, 'total': 47300,
            'status': '完了', 'payment': 'クレジットカード',
            'orderedAt': '2025-03-05T17:30:00'
        },
        {
            'id': 'ord_016', 'orderNumber': 'OFT-00016',
            'customer': {'name': '山田 太郎', 'email': 'yamada@example.com', 'phone': '03-1234-5678'},
            'shipping': {'last_name': '山田', 'first_name': '太郎', 'zip': '150-0001', 'prefecture': '東京都', 'city': '渋谷区神宮前'},
            'items': [{'name': 'オーガニックコットン カバーセット S', 'price': 22000, 'qty': 2, 'color': 'Natural', 'image': ''}],
            'subtotal': 44000, 'shipping_fee': 0, 'total': 44000,
            'status': '完了', 'payment': 'クレジットカード',
            'orderedAt': '2025-04-12T11:10:00'
        },
        {
            'id': 'ord_017', 'orderNumber': 'OFT-00017',
            'customer': {'name': '田中 美咲', 'email': 'tanaka@example.com', 'phone': '080-1111-2222'},
            'shipping': {'last_name': '田中', 'first_name': '美咲', 'zip': '150-0033', 'prefecture': '東京都', 'city': '渋谷区猿楽町'},
            'items': [{'name': 'Premium RDS Down 合掛け S', 'price': 60500, 'qty': 1, 'color': 'Gray', 'image': ''}],
            'subtotal': 60500, 'shipping_fee': 0, 'total': 60500,
            'status': '完了', 'payment': 'クレジットカード',
            'orderedAt': '2025-05-20T13:00:00'
        },
        {
            'id': 'ord_018', 'orderNumber': 'OFT-00018',
            'customer': {'name': '高橋 直子', 'email': 'takahashi@example.com', 'phone': '090-3333-4444'},
            'shipping': {'last_name': '高橋', 'first_name': '直子', 'zip': '158-0083', 'prefecture': '東京都', 'city': '世田谷区奥沢'},
            'items': [
                {'name': 'Premium RDS Down 冬用本掛け D', 'price': 99000, 'qty': 1, 'color': 'White', 'image': ''},
                {'name': 'オリジナル枕', 'price': 16500, 'qty': 2, 'color': 'White', 'image': ''}
            ],
            'subtotal': 132000, 'shipping_fee': 0, 'total': 132000,
            'status': '発送済み', 'payment': 'クレジットカード',
            'orderedAt': '2025-06-15T10:30:00'
        },
        {
            'id': 'ord_019', 'orderNumber': 'OFT-00019',
            'customer': {'name': '渡辺 翔太', 'email': 'watanabe@example.com', 'phone': '090-5555-9999'},
            'shipping': {'last_name': '渡辺', 'first_name': '翔太', 'zip': '153-0064', 'prefecture': '東京都', 'city': '目黒区下目黒'},
            'items': [{'name': 'シルクピローケース', 'price': 8800, 'qty': 1, 'color': 'Navy', 'image': ''}],
            'subtotal': 8800, 'shipping_fee': 880, 'total': 9680,
            'status': 'キャンセル', 'payment': 'クレジットカード',
            'orderedAt': '2025-07-22T19:00:00'
        },
        {
            'id': 'ord_020', 'orderNumber': 'OFT-00020',
            'customer': {'name': '中村 恵', 'email': 'nakamura@example.com', 'phone': '03-2222-3333'},
            'shipping': {'last_name': '中村', 'first_name': '恵', 'zip': '152-0035', 'prefecture': '東京都', 'city': '目黒区自由が丘'},
            'items': [{'name': 'Clean Cycle Down 冬用本掛け S', 'price': 53800, 'qty': 1, 'color': 'White', 'image': ''}],
            'subtotal': 53800, 'shipping_fee': 0, 'total': 53800,
            'status': '完了', 'payment': 'クレジットカード',
            'orderedAt': '2025-08-30T15:20:00'
        },
        {
            'id': 'ord_021', 'orderNumber': 'OFT-00021',
            'customer': {'name': '佐藤 花子', 'email': 'sato@example.com', 'phone': '090-9876-5432'},
            'shipping': {'last_name': '佐藤', 'first_name': '花子', 'zip': '107-0062', 'prefecture': '東京都', 'city': '港区南青山'},
            'items': [
                {'name': 'Premium RDS Down 肌掛け S', 'price': 44000, 'qty': 1, 'color': 'White', 'image': ''},
                {'name': 'シルクピローケース', 'price': 8800, 'qty': 1, 'color': 'Ivory', 'image': ''}
            ],
            'subtotal': 52800, 'shipping_fee': 0, 'total': 52800,
            'status': '完了', 'payment': 'クレジットカード',
            'orderedAt': '2025-09-18T12:45:00'
        },
        {
            'id': 'ord_022', 'orderNumber': 'OFT-00022',
            'customer': {'name': '伊藤 裕子', 'email': 'ito@example.com', 'phone': '080-7777-8888'},
            'shipping': {'last_name': '伊藤', 'first_name': '裕子', 'zip': '106-0032', 'prefecture': '東京都', 'city': '港区六本木'},
            'items': [{'name': 'オーガニックコットン カバーセット D', 'price': 27500, 'qty': 2, 'color': 'Natural', 'image': ''}],
            'subtotal': 55000, 'shipping_fee': 0, 'total': 55000,
            'status': '発送済み', 'payment': 'クレジットカード',
            'orderedAt': '2025-11-03T10:15:00'
        },
        {
            'id': 'ord_023', 'orderNumber': 'OFT-00023',
            'customer': {'name': '山田 太郎', 'email': 'yamada@example.com', 'phone': '03-1234-5678'},
            'shipping': {'last_name': '山田', 'first_name': '太郎', 'zip': '150-0001', 'prefecture': '東京都', 'city': '渋谷区神宮前'},
            'items': [{'name': 'Premium RDS Down 冬用本掛け D', 'price': 99000, 'qty': 1, 'color': 'White', 'image': ''}],
            'subtotal': 99000, 'shipping_fee': 0, 'total': 99000,
            'status': '完了', 'payment': 'クレジットカード',
            'orderedAt': '2025-12-20T09:00:00'
        },
        # --- 2026年 (5件: ord_024〜ord_028) ---
        {
            'id': 'ord_024', 'orderNumber': 'OFT-00024',
            'customer': {'name': '渡辺 翔太', 'email': 'watanabe@example.com', 'phone': '090-5555-9999'},
            'shipping': {'last_name': '渡辺', 'first_name': '翔太', 'zip': '153-0064', 'prefecture': '東京都', 'city': '目黒区下目黒'},
            'items': [
                {'name': 'Clean Cycle Down 冬用本掛け D', 'price': 64800, 'qty': 1, 'color': 'White', 'image': ''},
                {'name': 'オーガニックコットン カバーセット D', 'price': 27500, 'qty': 1, 'color': 'Natural', 'image': ''}
            ],
            'subtotal': 92300, 'shipping_fee': 0, 'total': 92300,
            'status': '完了', 'payment': 'クレジットカード',
            'orderedAt': '2026-01-08T11:30:00'
        },
        {
            'id': 'ord_025', 'orderNumber': 'OFT-00025',
            'customer': {'name': '中村 恵', 'email': 'nakamura@example.com', 'phone': '03-2222-3333'},
            'shipping': {'last_name': '中村', 'first_name': '恵', 'zip': '152-0035', 'prefecture': '東京都', 'city': '目黒区自由が丘'},
            'items': [{'name': 'Premium RDS Down 合掛け S', 'price': 60500, 'qty': 1, 'color': 'Gray', 'image': ''}],
            'subtotal': 60500, 'shipping_fee': 0, 'total': 60500,
            'status': '完了', 'payment': 'クレジットカード',
            'orderedAt': '2026-01-25T16:00:00'
        },
        {
            'id': 'ord_026', 'orderNumber': 'OFT-00026',
            'customer': {'name': '田中 美咲', 'email': 'tanaka@example.com', 'phone': '080-1111-2222'},
            'shipping': {'last_name': '田中', 'first_name': '美咲', 'zip': '150-0033', 'prefecture': '東京都', 'city': '渋谷区猿楽町'},
            'items': [
                {'name': 'オリジナル枕', 'price': 16500, 'qty': 1, 'color': 'White', 'image': ''},
                {'name': 'シルクピローケース', 'price': 8800, 'qty': 1, 'color': 'Navy', 'image': ''}
            ],
            'subtotal': 25300, 'shipping_fee': 880, 'total': 26180,
            'status': '発送済み', 'payment': 'クレジットカード',
            'orderedAt': '2026-02-14T13:20:00'
        },
        {
            'id': 'ord_027', 'orderNumber': 'OFT-00027',
            'customer': {'name': '高橋 直子', 'email': 'takahashi@example.com', 'phone': '090-3333-4444'},
            'shipping': {'last_name': '高橋', 'first_name': '直子', 'zip': '158-0083', 'prefecture': '東京都', 'city': '世田谷区奥沢'},
            'items': [{'name': 'Clean Cycle Down 合掛け S', 'price': 38500, 'qty': 2, 'color': 'Beige', 'image': ''}],
            'subtotal': 77000, 'shipping_fee': 0, 'total': 77000,
            'status': '処理待ち', 'payment': 'クレジットカード',
            'orderedAt': '2026-03-22T10:45:00'
        },
        {
            'id': 'ord_028', 'orderNumber': 'OFT-00028',
            'customer': {'name': '伊藤 裕子', 'email': 'ito@example.com', 'phone': '080-7777-8888'},
            'shipping': {'last_name': '伊藤', 'first_name': '裕子', 'zip': '106-0032', 'prefecture': '東京都', 'city': '港区六本木'},
            'items': [{'name': 'Premium RDS Down 冬用本掛け S', 'price': 82500, 'qty': 1, 'color': 'White', 'image': ''}],
            'subtotal': 82500, 'shipping_fee': 0, 'total': 82500,
            'status': '処理待ち', 'payment': 'クレジットカード',
            'orderedAt': '2026-04-02T09:15:00'
        },
    ])

    # 顧客
    db_write('customers', [
        {
            'id': 'c_001', 'name': '山田 太郎', 'email': 'yamada@example.com',
            'phone': '03-1234-5678', 'registeredAt': '2024-06-10T00:00:00',
            'status': 'アクティブ', 'newsletter': True,
            'orders': 4, 'totalSpent': 257300
        },
        {
            'id': 'c_002', 'name': '佐藤 花子', 'email': 'sato@example.com',
            'phone': '090-9876-5432', 'registeredAt': '2024-01-05T00:00:00',
            'status': 'アクティブ', 'newsletter': True,
            'orders': 4, 'totalSpent': 173360
        },
        {
            'id': 'c_003', 'name': '田中 美咲', 'email': 'tanaka@example.com',
            'phone': '080-1111-2222', 'registeredAt': '2024-02-15T00:00:00',
            'status': 'アクティブ', 'newsletter': True,
            'orders': 4, 'totalSpent': 160160
        },
        {
            'id': 'c_004', 'name': '鈴木 健一', 'email': 'suzuki.k@example.com',
            'phone': '03-5555-6666', 'registeredAt': '2024-03-01T00:00:00',
            'status': 'アクティブ', 'newsletter': False,
            'orders': 2, 'totalSpent': 147300
        },
        {
            'id': 'c_005', 'name': '高橋 直子', 'email': 'takahashi@example.com',
            'phone': '090-3333-4444', 'registeredAt': '2024-05-10T00:00:00',
            'status': 'アクティブ', 'newsletter': True,
            'orders': 4, 'totalSpent': 308000
        },
        {
            'id': 'c_006', 'name': '伊藤 裕子', 'email': 'ito@example.com',
            'phone': '080-7777-8888', 'registeredAt': '2024-09-01T00:00:00',
            'status': 'アクティブ', 'newsletter': True,
            'orders': 4, 'totalSpent': 270600
        },
        {
            'id': 'c_007', 'name': '渡辺 翔太', 'email': 'watanabe@example.com',
            'phone': '090-5555-9999', 'registeredAt': '2024-10-20T00:00:00',
            'status': 'アクティブ', 'newsletter': False,
            'orders': 3, 'totalSpent': 172280
        },
        {
            'id': 'c_008', 'name': '中村 恵', 'email': 'nakamura@example.com',
            'phone': '03-2222-3333', 'registeredAt': '2025-02-20T00:00:00',
            'status': 'アクティブ', 'newsletter': True,
            'orders': 3, 'totalSpent': 161600
        }
    ])

    # お問い合わせ
    db_write('inquiries', [
        {
            'id': 'inq_001', 'name': '鈴木 一郎', 'email': 'suzuki@example.com',
            'phone': '', 'category': '商品について',
            'subject': 'Clean Cycle Downのサイズについて',
            'body': 'ダブルサイズの在庫はありますか？',
            'status': '新規', 'priority': '通常',
            'receivedAt': '2024-12-10T14:00:00',
            'memo': '', 'timeline': []
        }
    ])

    # ページコンテンツ（空 - 管理画面から設定）
    db_write('page-content', {})

    # 設定
    db_write('settings', {
        'siteName': '表参道布団店。',
        'siteUrl': 'https://omotesando-futon.jp',
        'adminEmail': 'admin@omotesando-futon.jp',
        'freeShippingThreshold': 30000,
        'taxRate': 10
    })

    print('[Init] サンプルデータ生成完了')


# ============================================================
# メイン
# ============================================================
if __name__ == '__main__':
    import sys
    # 初期データがなければサンプル生成
    if not db_path('products').exists():
        _init_sample_data()

    # ポート: 環境変数 PORT > コマンドライン引数 > デフォルト5000
    port = int(os.environ.get('PORT', 5000))
    for arg in sys.argv[1:]:
        if arg.isdigit():
            port = int(arg)

    print('=' * 60)
    print('  表参道布団店 ステージングサーバー')
    print(f'  http://localhost:{port}/')
    print(f'  管理画面: http://localhost:{port}/admin/login.html')
    print('=' * 60)

    app.run(host='0.0.0.0', port=port, debug=True)
