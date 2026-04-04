# -*- coding: utf-8 -*-
"""
HTMLメール送信モジュール
Gmail SMTP経由でHTMLメールを送信
"""

import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

EMAILS_DIR = Path(__file__).parent.parent / 'site-a' / 'emails'


def render_template(template_name: str, variables: dict) -> str:
    """HTMLテンプレートを読み込み、{{変数}} を置換して返す"""
    template_path = EMAILS_DIR / template_name
    if not template_path.exists():
        raise FileNotFoundError(f'テンプレートが見つかりません: {template_path}')

    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    for key, value in variables.items():
        html = html.replace(f'{{{{{key}}}}}', str(value))

    return html


def send_email(to: str, subject: str, html_body: str, config: dict) -> bool:
    """Gmail SMTP経由でHTMLメールを送信"""
    smtp_host = config.get('smtp_host', 'smtp.gmail.com')
    smtp_port = config.get('smtp_port', 587)
    smtp_user = config.get('smtp_user', '')
    smtp_password = config.get('smtp_password', '')
    from_name = config.get('from_name', '表参道布団店。')
    from_email = config.get('from_email', smtp_user)

    if not smtp_user or not smtp_password:
        print(f'[Email] SMTP未設定 → スキップ (to: {to}, subject: {subject})')
        print(f'[Email] staging-config.json の smtp_user / smtp_password を設定してください')
        return False

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f'{from_name} <{from_email}>'
    msg['To'] = to

    # テキスト版（HTMLからタグを除去）
    text_body = re.sub(r'<[^>]+>', '', html_body)
    text_body = re.sub(r'\s+', ' ', text_body).strip()

    msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print(f'[Email] 送信成功: {to} ({subject})')
        return True
    except Exception as e:
        print(f'[Email] 送信失敗: {to} ({subject}) - {e}')
        return False


def send_order_emails(order: dict, config: dict):
    """購入完了メールを送信（購入者 + 運営）"""
    customer_name = order.get('customer', {}).get('name', 'お客様')
    customer_email = order.get('customer', {}).get('email', '')
    order_number = order.get('orderNumber', order.get('id', ''))
    order_total = f"¥{order.get('total', 0):,}"

    # 注文商品のHTML生成
    items = order.get('items', [])
    items_html = ''
    for item in items:
        qty = item.get('qty', 1)
        price = item.get('price', 0)
        items_html += f'''
        <tr>
            <td style="padding:8px 12px;border-bottom:1px solid #EAEDF3;font-size:14px;">{item.get('name', '商品')}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #EAEDF3;font-size:14px;text-align:center;">{qty}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #EAEDF3;font-size:14px;text-align:right;">¥{price:,}</td>
        </tr>'''

    # 配送先
    shipping = order.get('shipping', {})
    shipping_addr = f"{shipping.get('prefecture', '')}{shipping.get('city', '')}{shipping.get('address1', '')}"

    # 1. 購入者へのメール
    try:
        html = render_template('order-confirmation.html', {
            'customer_name': customer_name,
            'order_number': order_number,
            'order_items_html': items_html,
            'order_total': order_total,
            'shipping_address': shipping_addr,
        })
        send_email(
            customer_email,
            f'【表参道布団店。】ご注文確認 #{order_number}',
            html, config
        )
    except FileNotFoundError:
        print('[Email] order-confirmation.html テンプレート未作成 → スキップ')

    # 2. 運営への通知メール
    admin_email = config.get('admin_email', '')
    if admin_email:
        try:
            html = render_template('admin-new-order.html', {
                'order_number': order_number,
                'customer_name': customer_name,
                'customer_email': customer_email,
                'order_total': order_total,
                'order_items_html': items_html,
            })
            send_email(
                admin_email,
                f'【運営通知】新規注文 #{order_number}',
                html, config
            )
        except FileNotFoundError:
            print('[Email] admin-new-order.html テンプレート未作成 → スキップ')


def send_registration_emails(customer: dict, config: dict):
    """会員登録メールを送信（登録者 + 運営）"""
    customer_name = customer.get('name', 'お客様')
    customer_email = customer.get('email', '')

    # 1. 登録者への歓迎メール
    try:
        html = render_template('register-welcome.html', {
            'customer_name': customer_name,
        })
        send_email(
            customer_email,
            '【表参道布団店。】会員登録完了のお知らせ',
            html, config
        )
    except FileNotFoundError:
        print('[Email] register-welcome.html テンプレート未作成 → スキップ')

    # 2. 運営への通知メール
    admin_email = config.get('admin_email', '')
    if admin_email:
        try:
            html = render_template('admin-new-member.html', {
                'customer_name': customer_name,
                'customer_email': customer_email,
                'registered_at': customer.get('registeredAt', ''),
            })
            send_email(
                admin_email,
                f'【運営通知】新規会員登録: {customer_name}',
                html, config
            )
        except FileNotFoundError:
            print('[Email] admin-new-member.html テンプレート未作成 → スキップ')
