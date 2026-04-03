<?php
/**
 * Stripe決済連携
 * - WooCommerce Stripe Gatewayと連携
 * - REST API経由でCheckout Session作成
 */

defined('ABSPATH') || exit;

class OFT_Stripe_Checkout {

    public static function init() {
        add_action('wp_ajax_oft_create_checkout', [__CLASS__, 'ajax_create_session']);
        add_action('wp_ajax_nopriv_oft_create_checkout', [__CLASS__, 'ajax_create_session']);
    }

    /**
     * Stripe Checkout Session作成（REST API用）
     */
    public static function api_create_session($request) {
        $items = $request->get_param('items');
        $customer_email = sanitize_email($request->get_param('email') ?? '');
        $shipping = $request->get_param('shipping');

        if (empty($items) || !is_array($items)) {
            return new WP_Error('invalid_items', 'カートが空です', ['status' => 400]);
        }

        // Stripe APIキー取得（WooCommerce Stripe設定から）
        $stripe_settings = get_option('woocommerce_stripe_settings', []);
        $test_mode = ($stripe_settings['testmode'] ?? 'yes') === 'yes';
        $secret_key = $test_mode
            ? ($stripe_settings['test_secret_key'] ?? '')
            : ($stripe_settings['secret_key'] ?? '');

        if (empty($secret_key)) {
            // プラグイン設定から取得
            $secret_key = get_option('oft_stripe_secret_key', '');
        }

        if (empty($secret_key)) {
            return new WP_Error('stripe_config', 'Stripe APIキーが設定されていません', ['status' => 500]);
        }

        // 注文をWooCommerceに作成
        $order = wc_create_order();

        foreach ($items as $item) {
            $product_id = absint($item['product_id'] ?? 0);
            $quantity = max(1, absint($item['quantity'] ?? 1));
            $product = wc_get_product($product_id);

            if (!$product) continue;

            $order->add_product($product, $quantity);
        }

        // 配送先設定
        if ($shipping) {
            $order->set_shipping_first_name(sanitize_text_field($shipping['last_name'] ?? ''));
            $order->set_shipping_last_name(sanitize_text_field($shipping['first_name'] ?? ''));
            $order->set_shipping_postcode(sanitize_text_field($shipping['postcode'] ?? ''));
            $order->set_shipping_state(sanitize_text_field($shipping['state'] ?? ''));
            $order->set_shipping_city(sanitize_text_field($shipping['city'] ?? ''));
            $order->set_shipping_address_1(sanitize_text_field($shipping['address1'] ?? ''));
            $order->set_shipping_address_2(sanitize_text_field($shipping['address2'] ?? ''));
            $order->set_billing_phone(sanitize_text_field($shipping['phone'] ?? ''));
            $order->set_billing_email($customer_email);
        }

        $order->set_payment_method('stripe');
        $order->calculate_totals();
        $order->save();

        // Stripe Checkout Session作成
        $line_items = [];
        foreach ($order->get_items() as $item) {
            $product = $item->get_product();
            $line_items[] = [
                'price_data' => [
                    'currency'     => 'jpy',
                    'product_data' => [
                        'name'   => $item->get_name(),
                        'images' => $product ? [wp_get_attachment_url($product->get_image_id())] : [],
                    ],
                    'unit_amount' => intval($item->get_total() / $item->get_quantity()),
                ],
                'quantity' => $item->get_quantity(),
            ];
        }

        $site_url = get_option('oft_static_site_url', 'https://ishizawa-hub.github.io/omotesando-futonten-renewal/site-a');

        $response = wp_remote_post('https://api.stripe.com/v1/checkout/sessions', [
            'headers' => [
                'Authorization' => 'Bearer ' . $secret_key,
                'Content-Type'  => 'application/x-www-form-urlencoded',
            ],
            'body' => http_build_query([
                'payment_method_types' => ['card'],
                'line_items'           => $line_items,
                'mode'                 => 'payment',
                'success_url'          => $site_url . '/checkout/complete.html?order_id=' . $order->get_id(),
                'cancel_url'           => $site_url . '/checkout/',
                'customer_email'       => $customer_email,
                'metadata'             => ['order_id' => $order->get_id()],
                'shipping_address_collection' => ['allowed_countries' => ['JP']],
            ]),
        ]);

        if (is_wp_error($response)) {
            return new WP_Error('stripe_error', $response->get_error_message(), ['status' => 500]);
        }

        $body = json_decode(wp_remote_retrieve_body($response), true);

        if (isset($body['error'])) {
            return new WP_Error('stripe_error', $body['error']['message'], ['status' => 400]);
        }

        // 注文にStripeセッションIDを保存
        $order->update_meta_data('_stripe_session_id', $body['id']);
        $order->set_status('pending');
        $order->save();

        // 管理者へ注文通知メール
        self::send_order_notification($order, $customer_email);

        return rest_ensure_response([
            'session_id' => $body['id'],
            'url'        => $body['url'],
            'order_id'   => $order->get_id(),
        ]);
    }

    /**
     * 注文通知メール送信
     */
    private static function send_order_notification($order, $customer_email) {
        $admin_email = get_option('oft_notification_email', 'ishizawa@epoch-inc.jp');
        $order_id = $order->get_id();
        $total = $order->get_total();
        $items_text = '';
        foreach ($order->get_items() as $item) {
            $items_text .= "  - {$item->get_name()} × {$item->get_quantity()}\n";
        }

        $subject = "【表参道布団店】新規注文 #{$order_id}";
        $body = "新規注文がありました。\n\n"
              . "━━━━━━━━━━━━━━━━━━━━━━━\n"
              . "注文番号: #{$order_id}\n"
              . "注文日時: " . current_time('Y年m月d日 H:i') . "\n"
              . "顧客メール: {$customer_email}\n"
              . "合計金額: ¥" . number_format($total) . "\n\n"
              . "【注文内容】\n{$items_text}"
              . "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
              . "管理画面で確認: " . admin_url('admin.php?page=oft-dashboard') . "\n";

        $headers = ['Content-Type: text/plain; charset=UTF-8'];
        wp_mail($admin_email, $subject, $body, $headers);
    }

    /**
     * AJAX版
     */
    public static function ajax_create_session() {
        $request = new WP_REST_Request('POST');
        $request->set_param('items', json_decode(stripslashes($_POST['items'] ?? '[]'), true));
        $request->set_param('email', $_POST['email'] ?? '');
        $request->set_param('shipping', json_decode(stripslashes($_POST['shipping'] ?? '{}'), true));

        $result = self::api_create_session($request);

        if (is_wp_error($result)) {
            wp_send_json_error($result->get_error_message());
        } else {
            wp_send_json_success($result->get_data());
        }
    }
}
