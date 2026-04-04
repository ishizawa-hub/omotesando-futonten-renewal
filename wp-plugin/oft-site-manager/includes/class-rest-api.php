<?php
/**
 * REST API
 * - 静的サイトからWPデータを取得するエンドポイント
 * - CORS対応（GitHub Pages → WP）
 * - JWT認証対応
 */

defined('ABSPATH') || exit;

class OFT_REST_API {

    const NAMESPACE = 'oft/v1';

    public static function init() {
        add_action('rest_api_init', [__CLASS__, 'register_routes']);
        add_filter('rest_pre_serve_request', [__CLASS__, 'cors_headers'], 10, 4);
    }

    /**
     * CORS対応
     */
    public static function cors_headers($served, $result, $request, $server) {
        $origin = get_http_origin();
        $allowed = [
            'https://ishizawa-hub.github.io',
            'http://localhost:8080',
            'http://localhost:3000',
        ];

        if (in_array($origin, $allowed)) {
            header("Access-Control-Allow-Origin: {$origin}");
            header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
            header('Access-Control-Allow-Headers: Authorization, Content-Type, X-WP-Nonce');
            header('Access-Control-Allow-Credentials: true');
        }

        return $served;
    }

    /**
     * ルート登録
     */
    public static function register_routes() {
        // ページコンテンツ取得（公開）
        register_rest_route(self::NAMESPACE, '/pages', [
            'methods'  => 'GET',
            'callback' => [__CLASS__, 'get_pages'],
            'permission_callback' => '__return_true',
        ]);

        register_rest_route(self::NAMESPACE, '/pages/(?P<page_id>[a-z_]+)', [
            'methods'  => 'GET',
            'callback' => [__CLASS__, 'get_page'],
            'permission_callback' => '__return_true',
        ]);

        // 商品一覧（公開）
        register_rest_route(self::NAMESPACE, '/products', [
            'methods'  => 'GET',
            'callback' => [__CLASS__, 'get_products'],
            'permission_callback' => '__return_true',
        ]);

        // カート操作（公開）
        register_rest_route(self::NAMESPACE, '/cart', [
            'methods'  => ['GET', 'POST'],
            'callback' => [__CLASS__, 'handle_cart'],
            'permission_callback' => '__return_true',
        ]);

        // 会員認証
        register_rest_route(self::NAMESPACE, '/auth/login', [
            'methods'  => 'POST',
            'callback' => ['OFT_Member_Manager', 'api_login'],
            'permission_callback' => '__return_true',
        ]);

        register_rest_route(self::NAMESPACE, '/auth/register', [
            'methods'  => 'POST',
            'callback' => ['OFT_Member_Manager', 'api_register'],
            'permission_callback' => '__return_true',
        ]);

        // チェックアウト（Stripe）
        register_rest_route(self::NAMESPACE, '/checkout/create-session', [
            'methods'  => 'POST',
            'callback' => ['OFT_Stripe_Checkout', 'api_create_session'],
            'permission_callback' => '__return_true',
        ]);

        // 注文履歴（認証済み）
        register_rest_route(self::NAMESPACE, '/orders', [
            'methods'  => 'GET',
            'callback' => [__CLASS__, 'get_orders'],
            'permission_callback' => function () {
                return is_user_logged_in();
            },
        ]);

        // ====================================
        // 管理者専用エンドポイント
        // ====================================

        // 管理者認証
        register_rest_route(self::NAMESPACE, '/admin/auth/login', [
            'methods'  => 'POST',
            'callback' => [__CLASS__, 'admin_login'],
            'permission_callback' => '__return_true',
        ]);

        // 商品管理（WooCommerce）
        register_rest_route(self::NAMESPACE, '/admin/products', [
            'methods'  => 'POST',
            'callback' => [__CLASS__, 'admin_create_product'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);

        register_rest_route(self::NAMESPACE, '/admin/products/(?P<id>\d+)', [
            'methods'  => 'PUT',
            'callback' => [__CLASS__, 'admin_update_product'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);

        register_rest_route(self::NAMESPACE, '/admin/products/(?P<id>\d+)', [
            'methods'  => 'DELETE',
            'callback' => [__CLASS__, 'admin_delete_product'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);

        // マガジン管理（投稿 + categoryで管理）
        register_rest_route(self::NAMESPACE, '/admin/magazine', [
            'methods'  => 'GET',
            'callback' => [__CLASS__, 'admin_get_magazine'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);

        register_rest_route(self::NAMESPACE, '/admin/magazine', [
            'methods'  => 'POST',
            'callback' => [__CLASS__, 'admin_create_magazine'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);

        register_rest_route(self::NAMESPACE, '/admin/magazine/(?P<id>\d+)', [
            'methods'  => 'PUT',
            'callback' => [__CLASS__, 'admin_update_magazine'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);

        register_rest_route(self::NAMESPACE, '/admin/magazine/(?P<id>\d+)', [
            'methods'  => 'DELETE',
            'callback' => [__CLASS__, 'admin_delete_magazine'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);

        // 注文管理（管理者用）
        register_rest_route(self::NAMESPACE, '/admin/orders', [
            'methods'  => 'GET',
            'callback' => [__CLASS__, 'admin_get_orders'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);

        register_rest_route(self::NAMESPACE, '/admin/orders/(?P<id>\d+)', [
            'methods'  => 'PUT',
            'callback' => [__CLASS__, 'admin_update_order'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);

        // 在庫管理
        register_rest_route(self::NAMESPACE, '/admin/inventory', [
            'methods'  => 'GET',
            'callback' => [__CLASS__, 'admin_get_inventory'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);

        register_rest_route(self::NAMESPACE, '/admin/inventory/(?P<id>\d+)', [
            'methods'  => 'PUT',
            'callback' => [__CLASS__, 'admin_update_inventory'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);

        // ページコンテンツ（公開読み取り）
        register_rest_route(self::NAMESPACE, '/page-content', [
            'methods'  => 'GET',
            'callback' => [__CLASS__, 'get_all_page_content'],
            'permission_callback' => '__return_true',
        ]);

        // ページコンテンツ（管理者書き込み）
        register_rest_route(self::NAMESPACE, '/admin/pages/(?P<page_id>[a-z_]+)', [
            'methods'  => 'PUT',
            'callback' => [__CLASS__, 'admin_update_page_content'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);

        // 顧客管理
        register_rest_route(self::NAMESPACE, '/admin/customers', [
            'methods'  => 'GET',
            'callback' => [__CLASS__, 'admin_get_customers'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);

        register_rest_route(self::NAMESPACE, '/admin/customers', [
            'methods'  => 'POST',
            'callback' => [__CLASS__, 'admin_create_customer'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);

        register_rest_route(self::NAMESPACE, '/admin/customers/(?P<id>[a-zA-Z0-9_-]+)', [
            'methods'  => 'PUT',
            'callback' => [__CLASS__, 'admin_update_customer'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);

        register_rest_route(self::NAMESPACE, '/admin/customers/(?P<id>[a-zA-Z0-9_-]+)', [
            'methods'  => 'DELETE',
            'callback' => [__CLASS__, 'admin_delete_customer'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);

        // お問い合わせ管理
        register_rest_route(self::NAMESPACE, '/admin/inquiries', [
            'methods'  => 'GET',
            'callback' => [__CLASS__, 'admin_get_inquiries'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);

        register_rest_route(self::NAMESPACE, '/admin/inquiries/(?P<id>[a-zA-Z0-9_-]+)', [
            'methods'  => 'PUT',
            'callback' => [__CLASS__, 'admin_update_inquiry'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);

        register_rest_route(self::NAMESPACE, '/admin/inquiries/(?P<id>[a-zA-Z0-9_-]+)', [
            'methods'  => 'DELETE',
            'callback' => [__CLASS__, 'admin_delete_inquiry'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);

        // 設定管理
        register_rest_route(self::NAMESPACE, '/admin/settings', [
            'methods'  => 'GET',
            'callback' => [__CLASS__, 'admin_get_settings'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);

        register_rest_route(self::NAMESPACE, '/admin/settings', [
            'methods'  => 'PUT',
            'callback' => [__CLASS__, 'admin_update_settings'],
            'permission_callback' => [__CLASS__, 'admin_permission_check'],
        ]);
    }

    /**
     * 全ページコンテンツ取得
     */
    public static function get_pages($request) {
        return rest_ensure_response(OFT_Page_Manager::get_all_content());
    }

    /**
     * 個別ページコンテンツ取得
     */
    public static function get_page($request) {
        $page_id = $request->get_param('page_id');
        $all = OFT_Page_Manager::get_all_content();
        if (!isset($all[$page_id])) {
            return new WP_Error('not_found', 'ページが見つかりません', ['status' => 404]);
        }
        return rest_ensure_response($all[$page_id]);
    }

    /**
     * 商品一覧（WooCommerce連携）
     */
    public static function get_products($request) {
        if (!class_exists('WooCommerce')) {
            return new WP_Error('wc_missing', 'WooCommerceが必要です', ['status' => 500]);
        }

        $category = $request->get_param('category');
        $args = [
            'post_type'      => 'product',
            'posts_per_page' => -1,
            'post_status'    => 'publish',
        ];

        if ($category) {
            $args['tax_query'] = [[
                'taxonomy' => 'product_cat',
                'field'    => 'slug',
                'terms'    => $category,
            ]];
        }

        $query = new WP_Query($args);
        $products = [];

        foreach ($query->posts as $post) {
            $product = wc_get_product($post->ID);
            if (!$product) continue;

            $data = [
                'id'          => $product->get_id(),
                'slug'        => $product->get_slug(),
                'name'        => $product->get_name(),
                'price'       => $product->get_price(),
                'description' => $product->get_short_description(),
                'image'       => wp_get_attachment_url($product->get_image_id()),
                'stock_status' => $product->get_stock_status(),
                'stock_qty'   => $product->get_stock_quantity(),
                'categories'  => wp_get_post_terms($post->ID, 'product_cat', ['fields' => 'slugs']),
            ];

            if ($product->is_type('variable')) {
                $data['variations'] = [];
                foreach ($product->get_children() as $child_id) {
                    $variation = wc_get_product($child_id);
                    if (!$variation) continue;
                    $data['variations'][] = [
                        'id'         => $child_id,
                        'attributes' => $variation->get_variation_attributes(),
                        'price'      => $variation->get_price(),
                        'stock_qty'  => $variation->get_stock_quantity(),
                    ];
                }
            }

            $products[] = $data;
        }

        return rest_ensure_response($products);
    }

    /**
     * カート操作（WooCommerce Cart API互換）
     */
    public static function handle_cart($request) {
        if ($request->get_method() === 'POST') {
            $action     = $request->get_param('action');
            $product_id = absint($request->get_param('product_id'));
            $quantity   = max(1, absint($request->get_param('quantity') ?? 1));

            if (!class_exists('WC')) {
                return new WP_Error('wc_missing', 'WooCommerce未インストール', ['status' => 500]);
            }

            WC()->frontend_includes();
            if (!WC()->session) {
                WC()->session = new WC_Session_Handler();
                WC()->session->init();
            }
            if (!WC()->cart) {
                WC()->cart = new WC_Cart();
                WC()->cart->get_cart_from_session();
            }

            switch ($action) {
                case 'add':
                    $cart_key = WC()->cart->add_to_cart($product_id, $quantity);
                    break;
                case 'remove':
                    $cart_item_key = $request->get_param('cart_item_key');
                    WC()->cart->remove_cart_item($cart_item_key);
                    break;
                case 'update':
                    $cart_item_key = $request->get_param('cart_item_key');
                    WC()->cart->set_quantity($cart_item_key, $quantity);
                    break;
                case 'clear':
                    WC()->cart->empty_cart();
                    break;
            }
        }

        // カート内容を返す
        $items = [];
        if (class_exists('WC') && WC()->cart) {
            foreach (WC()->cart->get_cart() as $key => $item) {
                $product = $item['data'];
                $items[] = [
                    'key'      => $key,
                    'id'       => $item['product_id'],
                    'name'     => $product->get_name(),
                    'price'    => $product->get_price(),
                    'quantity' => $item['quantity'],
                    'subtotal' => $item['line_subtotal'],
                    'image'    => wp_get_attachment_url($product->get_image_id()),
                ];
            }
        }

        return rest_ensure_response([
            'items' => $items,
            'total' => WC()->cart ? WC()->cart->get_cart_contents_total() : 0,
            'count' => WC()->cart ? WC()->cart->get_cart_contents_count() : 0,
        ]);
    }

    /**
     * 注文履歴取得
     */
    public static function get_orders($request) {
        $user_id = get_current_user_id();
        $orders = wc_get_orders([
            'customer_id' => $user_id,
            'limit'       => 20,
            'orderby'     => 'date',
            'order'       => 'DESC',
        ]);

        $data = [];
        foreach ($orders as $order) {
            $items = [];
            foreach ($order->get_items() as $item) {
                $items[] = [
                    'name'     => $item->get_name(),
                    'quantity' => $item->get_quantity(),
                    'total'    => $item->get_total(),
                ];
            }
            $data[] = [
                'id'         => $order->get_id(),
                'status'     => $order->get_status(),
                'date'       => $order->get_date_created()->format('Y-m-d H:i'),
                'total'      => $order->get_total(),
                'items'      => $items,
            ];
        }

        return rest_ensure_response($data);
    }

    // ====================================
    // 管理者権限チェック
    // ====================================

    /**
     * 管理者権限チェック（permission_callback用）
     * Authorization: Bearer {token} ヘッダーを検証し、manage_options権限を確認
     */
    public static function admin_permission_check($request) {
        $auth_header = $request->get_header('Authorization');
        if (!$auth_header || strpos($auth_header, 'Bearer ') !== 0) {
            return new WP_Error('rest_forbidden', '認証トークンが必要です', ['status' => 401]);
        }

        $token = substr($auth_header, 7);

        if (!class_exists('OFT_Member_Manager') || !method_exists('OFT_Member_Manager', 'validate_token')) {
            return new WP_Error('auth_unavailable', '認証機能が利用できません', ['status' => 500]);
        }

        $user_id = OFT_Member_Manager::validate_token($token);
        if (is_wp_error($user_id) || !$user_id) {
            return new WP_Error('rest_forbidden', '無効なトークンです', ['status' => 401]);
        }

        wp_set_current_user($user_id);

        if (!current_user_can('manage_options')) {
            return new WP_Error('rest_forbidden', '管理者権限が必要です', ['status' => 403]);
        }

        return true;
    }

    // ====================================
    // 管理者認証
    // ====================================

    /**
     * 管理者ログイン
     * ユーザー認証後、manage_options権限を確認してトークンを返す
     */
    public static function admin_login($request) {
        $username = sanitize_text_field($request->get_param('username'));
        $password = $request->get_param('password');

        if (empty($username) || empty($password)) {
            return new WP_Error('missing_fields', 'ユーザー名とパスワードは必須です', ['status' => 400]);
        }

        $user = wp_authenticate($username, $password);
        if (is_wp_error($user)) {
            return new WP_Error('invalid_credentials', 'ユーザー名またはパスワードが正しくありません', ['status' => 401]);
        }

        if (!user_can($user, 'manage_options')) {
            return new WP_Error('rest_forbidden', '管理者権限が必要です', ['status' => 403]);
        }

        // OFT_Member_Managerのトークン生成を利用
        if (!class_exists('OFT_Member_Manager') || !method_exists('OFT_Member_Manager', 'generate_token')) {
            return new WP_Error('auth_unavailable', 'トークン生成機能が利用できません', ['status' => 500]);
        }

        $token = OFT_Member_Manager::generate_token($user->ID);

        return rest_ensure_response([
            'token'    => $token,
            'user'     => [
                'id'           => $user->ID,
                'display_name' => $user->display_name,
                'email'        => $user->user_email,
                'role'         => 'administrator',
            ],
        ]);
    }

    // ====================================
    // 商品管理（WooCommerce）
    // ====================================

    /**
     * 商品作成
     */
    public static function admin_create_product($request) {
        if (!class_exists('WooCommerce')) {
            return new WP_Error('wc_missing', 'WooCommerceが必要です', ['status' => 500]);
        }

        $name        = sanitize_text_field($request->get_param('name'));
        $price       = $request->get_param('price');
        $description = wp_kses_post($request->get_param('description'));
        $category    = sanitize_text_field($request->get_param('category'));
        $stock       = $request->get_param('stock');
        $status      = sanitize_text_field($request->get_param('status') ?? 'draft');
        $image_id    = absint($request->get_param('image_id'));

        if (empty($name)) {
            return new WP_Error('missing_name', '商品名は必須です', ['status' => 400]);
        }

        $product = new WC_Product_Simple();
        $product->set_name($name);
        if ($price !== null) {
            $product->set_regular_price($price);
        }
        if ($description) {
            $product->set_short_description($description);
        }
        if ($status) {
            $product->set_status($status);
        }
        if ($image_id) {
            $product->set_image_id($image_id);
        }
        if ($stock !== null) {
            $product->set_manage_stock(true);
            $product->set_stock_quantity(absint($stock));
        }

        $product_id = $product->save();

        // カテゴリ設定
        if ($category) {
            $term = get_term_by('slug', $category, 'product_cat');
            if (!$term) {
                $term = wp_insert_term($category, 'product_cat');
                $term_id = is_array($term) ? $term['term_id'] : $term;
            } else {
                $term_id = $term->term_id;
            }
            wp_set_object_terms($product_id, [$term_id], 'product_cat');
        }

        // 管理者へ商品登録通知メール
        self::send_admin_notification(
            "【表参道布団店】新規商品が登録されました",
            "新規商品が管理画面から登録されました。\n\n"
            . "━━━━━━━━━━━━━━━━━━━━━━━\n"
            . "商品ID: {$product_id}\n"
            . "商品名: {$name}\n"
            . "価格: ¥" . number_format(intval($price ?? 0)) . "\n"
            . "カテゴリ: {$category}\n"
            . "ステータス: {$status}\n"
            . "登録日時: " . current_time('Y年m月d日 H:i') . "\n"
            . "━━━━━━━━━━━━━━━━━━━━━━━\n"
        );

        return rest_ensure_response([
            'id'      => $product_id,
            'message' => '商品を作成しました',
        ]);
    }

    /**
     * 商品更新
     */
    public static function admin_update_product($request) {
        if (!class_exists('WooCommerce')) {
            return new WP_Error('wc_missing', 'WooCommerceが必要です', ['status' => 500]);
        }

        $id = absint($request->get_param('id'));
        $product = wc_get_product($id);
        if (!$product) {
            return new WP_Error('not_found', '商品が見つかりません', ['status' => 404]);
        }

        $params = $request->get_json_params();

        if (isset($params['name'])) {
            $product->set_name(sanitize_text_field($params['name']));
        }
        if (isset($params['price'])) {
            $product->set_regular_price($params['price']);
        }
        if (isset($params['description'])) {
            $product->set_short_description(wp_kses_post($params['description']));
        }
        if (isset($params['status'])) {
            $product->set_status(sanitize_text_field($params['status']));
        }
        if (isset($params['image_id'])) {
            $product->set_image_id(absint($params['image_id']));
        }
        if (isset($params['stock'])) {
            $product->set_manage_stock(true);
            $product->set_stock_quantity(absint($params['stock']));
        }

        $product->save();

        // カテゴリ更新
        if (isset($params['category'])) {
            $category = sanitize_text_field($params['category']);
            $term = get_term_by('slug', $category, 'product_cat');
            if (!$term) {
                $term = wp_insert_term($category, 'product_cat');
                $term_id = is_array($term) ? $term['term_id'] : $term;
            } else {
                $term_id = $term->term_id;
            }
            wp_set_object_terms($id, [$term_id], 'product_cat');
        }

        return rest_ensure_response([
            'id'      => $id,
            'message' => '商品を更新しました',
        ]);
    }

    /**
     * 商品削除（ゴミ箱へ）
     */
    public static function admin_delete_product($request) {
        if (!class_exists('WooCommerce')) {
            return new WP_Error('wc_missing', 'WooCommerceが必要です', ['status' => 500]);
        }

        $id = absint($request->get_param('id'));
        $product = wc_get_product($id);
        if (!$product) {
            return new WP_Error('not_found', '商品が見つかりません', ['status' => 404]);
        }

        $product->set_status('trash');
        $product->save();

        return rest_ensure_response([
            'id'      => $id,
            'message' => '商品をゴミ箱に移動しました',
        ]);
    }

    // ====================================
    // マガジン管理（投稿 + category: magazine）
    // ====================================

    /**
     * マガジンカテゴリIDを取得（なければ作成）
     */
    private static function get_magazine_category_id() {
        $term = get_term_by('slug', 'magazine', 'category');
        if ($term) {
            return $term->term_id;
        }
        $result = wp_insert_term('Magazine', 'category', ['slug' => 'magazine']);
        return is_array($result) ? $result['term_id'] : 0;
    }

    /**
     * マガジン一覧取得（下書き含む）
     */
    public static function admin_get_magazine($request) {
        $cat_id = self::get_magazine_category_id();

        $args = [
            'post_type'      => 'post',
            'posts_per_page' => -1,
            'post_status'    => ['publish', 'draft', 'pending', 'private'],
            'cat'            => $cat_id,
            'orderby'        => 'date',
            'order'          => 'DESC',
        ];

        $query = new WP_Query($args);
        $posts = [];

        foreach ($query->posts as $post) {
            $posts[] = [
                'id'           => $post->ID,
                'title'        => $post->post_title,
                'content'      => $post->post_content,
                'excerpt'      => $post->post_excerpt,
                'status'       => $post->post_status,
                'date'         => $post->post_date,
                'modified'     => $post->post_modified,
                'author'       => get_the_author_meta('display_name', $post->post_author),
                'thumbnail'    => get_the_post_thumbnail_url($post->ID, 'full'),
                'thumbnail_id' => get_post_thumbnail_id($post->ID),
                'categories'   => wp_get_post_categories($post->ID, ['fields' => 'slugs']),
            ];
        }

        return rest_ensure_response($posts);
    }

    /**
     * マガジン記事作成
     */
    public static function admin_create_magazine($request) {
        $title        = sanitize_text_field($request->get_param('title'));
        $content      = wp_kses_post($request->get_param('content'));
        $status       = sanitize_text_field($request->get_param('status') ?? 'draft');
        $thumbnail_id = absint($request->get_param('thumbnail_id'));
        $category     = sanitize_text_field($request->get_param('category'));

        if (empty($title)) {
            return new WP_Error('missing_title', 'タイトルは必須です', ['status' => 400]);
        }

        $cat_id = self::get_magazine_category_id();
        $categories = [$cat_id];

        // 追加カテゴリがあれば設定
        if ($category) {
            $extra_term = get_term_by('slug', $category, 'category');
            if (!$extra_term) {
                $extra_result = wp_insert_term($category, 'category');
                if (is_array($extra_result)) {
                    $categories[] = $extra_result['term_id'];
                }
            } else {
                $categories[] = $extra_term->term_id;
            }
        }

        $post_data = [
            'post_title'   => $title,
            'post_content' => $content,
            'post_status'  => $status,
            'post_type'    => 'post',
            'post_author'  => get_current_user_id(),
            'post_category' => $categories,
        ];

        $post_id = wp_insert_post($post_data, true);
        if (is_wp_error($post_id)) {
            return $post_id;
        }

        if ($thumbnail_id) {
            set_post_thumbnail($post_id, $thumbnail_id);
        }

        // 管理者へマガジン記事登録通知メール
        self::send_admin_notification(
            "【表参道布団店】新規マガジン記事が登録されました",
            "新規マガジン記事が管理画面から登録されました。\n\n"
            . "━━━━━━━━━━━━━━━━━━━━━━━\n"
            . "記事ID: {$post_id}\n"
            . "タイトル: {$title}\n"
            . "ステータス: {$status}\n"
            . "登録日時: " . current_time('Y年m月d日 H:i') . "\n"
            . "━━━━━━━━━━━━━━━━━━━━━━━\n"
        );

        return rest_ensure_response([
            'id'      => $post_id,
            'message' => 'マガジン記事を作成しました',
        ]);
    }

    /**
     * マガジン記事更新
     */
    public static function admin_update_magazine($request) {
        $id = absint($request->get_param('id'));
        $post = get_post($id);
        if (!$post || $post->post_type !== 'post') {
            return new WP_Error('not_found', '記事が見つかりません', ['status' => 404]);
        }

        $params = $request->get_json_params();
        $post_data = ['ID' => $id];

        if (isset($params['title'])) {
            $post_data['post_title'] = sanitize_text_field($params['title']);
        }
        if (isset($params['content'])) {
            $post_data['post_content'] = wp_kses_post($params['content']);
        }
        if (isset($params['status'])) {
            $post_data['post_status'] = sanitize_text_field($params['status']);
        }

        $result = wp_update_post($post_data, true);
        if (is_wp_error($result)) {
            return $result;
        }

        if (isset($params['thumbnail_id'])) {
            $thumb_id = absint($params['thumbnail_id']);
            if ($thumb_id) {
                set_post_thumbnail($id, $thumb_id);
            } else {
                delete_post_thumbnail($id);
            }
        }

        // 追加カテゴリの更新
        if (isset($params['category'])) {
            $cat_id = self::get_magazine_category_id();
            $categories = [$cat_id];
            $category = sanitize_text_field($params['category']);
            if ($category) {
                $extra_term = get_term_by('slug', $category, 'category');
                if (!$extra_term) {
                    $extra_result = wp_insert_term($category, 'category');
                    if (is_array($extra_result)) {
                        $categories[] = $extra_result['term_id'];
                    }
                } else {
                    $categories[] = $extra_term->term_id;
                }
            }
            wp_set_post_categories($id, $categories);
        }

        return rest_ensure_response([
            'id'      => $id,
            'message' => 'マガジン記事を更新しました',
        ]);
    }

    /**
     * マガジン記事削除（ゴミ箱へ）
     */
    public static function admin_delete_magazine($request) {
        $id = absint($request->get_param('id'));
        $post = get_post($id);
        if (!$post || $post->post_type !== 'post') {
            return new WP_Error('not_found', '記事が見つかりません', ['status' => 404]);
        }

        wp_trash_post($id);

        return rest_ensure_response([
            'id'      => $id,
            'message' => 'マガジン記事をゴミ箱に移動しました',
        ]);
    }

    // ====================================
    // 注文管理（管理者用）
    // ====================================

    /**
     * 全注文一覧取得（管理者用）
     */
    public static function admin_get_orders($request) {
        if (!class_exists('WooCommerce')) {
            return new WP_Error('wc_missing', 'WooCommerceが必要です', ['status' => 500]);
        }

        $page     = absint($request->get_param('page') ?? 1);
        $per_page = absint($request->get_param('per_page') ?? 20);
        $status   = $request->get_param('status');

        $args = [
            'limit'   => $per_page,
            'page'    => $page,
            'orderby' => 'date',
            'order'   => 'DESC',
        ];

        if ($status) {
            $args['status'] = sanitize_text_field($status);
        }

        $orders = wc_get_orders($args);
        $data = [];

        foreach ($orders as $order) {
            $items = [];
            foreach ($order->get_items() as $item) {
                $items[] = [
                    'id'          => $item->get_id(),
                    'product_id'  => $item->get_product_id(),
                    'name'        => $item->get_name(),
                    'quantity'    => $item->get_quantity(),
                    'total'       => $item->get_total(),
                    'subtotal'    => $item->get_subtotal(),
                ];
            }

            $data[] = [
                'id'               => $order->get_id(),
                'status'           => $order->get_status(),
                'date_created'     => $order->get_date_created() ? $order->get_date_created()->format('Y-m-d H:i:s') : null,
                'date_modified'    => $order->get_date_modified() ? $order->get_date_modified()->format('Y-m-d H:i:s') : null,
                'total'            => $order->get_total(),
                'subtotal'         => $order->get_subtotal(),
                'shipping_total'   => $order->get_shipping_total(),
                'tax_total'        => $order->get_total_tax(),
                'payment_method'   => $order->get_payment_method_title(),
                'customer_id'      => $order->get_customer_id(),
                'billing'          => [
                    'first_name' => $order->get_billing_first_name(),
                    'last_name'  => $order->get_billing_last_name(),
                    'email'      => $order->get_billing_email(),
                    'phone'      => $order->get_billing_phone(),
                    'address_1'  => $order->get_billing_address_1(),
                    'address_2'  => $order->get_billing_address_2(),
                    'city'       => $order->get_billing_city(),
                    'state'      => $order->get_billing_state(),
                    'postcode'   => $order->get_billing_postcode(),
                ],
                'shipping'         => [
                    'first_name' => $order->get_shipping_first_name(),
                    'last_name'  => $order->get_shipping_last_name(),
                    'address_1'  => $order->get_shipping_address_1(),
                    'address_2'  => $order->get_shipping_address_2(),
                    'city'       => $order->get_shipping_city(),
                    'state'      => $order->get_shipping_state(),
                    'postcode'   => $order->get_shipping_postcode(),
                ],
                'items'            => $items,
                'customer_note'    => $order->get_customer_note(),
            ];
        }

        return rest_ensure_response([
            'orders' => $data,
            'page'   => $page,
            'per_page' => $per_page,
        ]);
    }

    /**
     * 注文ステータス更新
     */
    public static function admin_update_order($request) {
        if (!class_exists('WooCommerce')) {
            return new WP_Error('wc_missing', 'WooCommerceが必要です', ['status' => 500]);
        }

        $id = absint($request->get_param('id'));
        $order = wc_get_order($id);
        if (!$order) {
            return new WP_Error('not_found', '注文が見つかりません', ['status' => 404]);
        }

        $params = $request->get_json_params();

        if (isset($params['status'])) {
            $new_status = sanitize_text_field($params['status']);
            $order->update_status($new_status, '管理画面APIから更新');
        }

        return rest_ensure_response([
            'id'      => $id,
            'status'  => $order->get_status(),
            'message' => '注文ステータスを更新しました',
        ]);
    }

    // ====================================
    // 在庫管理
    // ====================================

    /**
     * 在庫一覧取得
     */
    public static function admin_get_inventory($request) {
        if (!class_exists('WooCommerce')) {
            return new WP_Error('wc_missing', 'WooCommerceが必要です', ['status' => 500]);
        }

        $args = [
            'post_type'      => 'product',
            'posts_per_page' => -1,
            'post_status'    => ['publish', 'draft', 'private'],
        ];

        $query = new WP_Query($args);
        $inventory = [];

        foreach ($query->posts as $post) {
            $product = wc_get_product($post->ID);
            if (!$product) continue;

            $item = [
                'id'            => $product->get_id(),
                'name'          => $product->get_name(),
                'sku'           => $product->get_sku(),
                'status'        => $product->get_status(),
                'stock_status'  => $product->get_stock_status(),
                'manage_stock'  => $product->get_manage_stock(),
                'stock_quantity' => $product->get_stock_quantity(),
                'low_stock_amount' => $product->get_low_stock_amount(),
                'backorders'    => $product->get_backorders(),
                'price'         => $product->get_price(),
                'categories'    => wp_get_post_terms($post->ID, 'product_cat', ['fields' => 'slugs']),
            ];

            // バリエーション商品の在庫
            if ($product->is_type('variable')) {
                $item['variations'] = [];
                foreach ($product->get_children() as $child_id) {
                    $variation = wc_get_product($child_id);
                    if (!$variation) continue;
                    $item['variations'][] = [
                        'id'             => $child_id,
                        'attributes'     => $variation->get_variation_attributes(),
                        'sku'            => $variation->get_sku(),
                        'stock_status'   => $variation->get_stock_status(),
                        'stock_quantity' => $variation->get_stock_quantity(),
                        'manage_stock'   => $variation->get_manage_stock(),
                    ];
                }
            }

            $inventory[] = $item;
        }

        return rest_ensure_response($inventory);
    }

    /**
     * 在庫数量更新
     */
    public static function admin_update_inventory($request) {
        if (!class_exists('WooCommerce')) {
            return new WP_Error('wc_missing', 'WooCommerceが必要です', ['status' => 500]);
        }

        $id = absint($request->get_param('id'));
        $product = wc_get_product($id);
        if (!$product) {
            return new WP_Error('not_found', '商品が見つかりません', ['status' => 404]);
        }

        $params = $request->get_json_params();

        if (isset($params['stock_quantity'])) {
            $product->set_manage_stock(true);
            $product->set_stock_quantity(absint($params['stock_quantity']));
        }
        if (isset($params['stock_status'])) {
            $product->set_stock_status(sanitize_text_field($params['stock_status']));
        }
        if (isset($params['backorders'])) {
            $product->set_backorders(sanitize_text_field($params['backorders']));
        }

        $product->save();

        return rest_ensure_response([
            'id'             => $id,
            'stock_quantity' => $product->get_stock_quantity(),
            'stock_status'   => $product->get_stock_status(),
            'message'        => '在庫を更新しました',
        ]);
    }

    // ====================================
    // ページコンテンツ管理
    // ====================================

    /**
     * 全ページコンテンツ取得（公開・フロントエンド用）
     */
    public static function get_all_page_content($request) {
        $data = get_option('oft_page_content', []);
        return rest_ensure_response($data);
    }

    /**
     * ページコンテンツ更新（管理者用）
     */
    public static function admin_update_page_content($request) {
        $page_id = sanitize_text_field($request->get_param('page_id'));
        $params = $request->get_json_params();

        $all_data = get_option('oft_page_content', []);
        $all_data[$page_id] = $params;
        update_option('oft_page_content', $all_data);

        return rest_ensure_response([
            'page_id' => $page_id,
            'message' => 'ページコンテンツを更新しました',
        ]);
    }

    // ====================================
    // 顧客管理
    // ====================================

    /**
     * 顧客一覧取得
     */
    public static function admin_get_customers($request) {
        $data = get_option('oft_customers_data', []);
        return rest_ensure_response($data);
    }

    /**
     * 顧客作成
     */
    public static function admin_create_customer($request) {
        $params = $request->get_json_params();
        $data = get_option('oft_customers_data', []);

        $id = isset($params['id']) ? sanitize_text_field($params['id']) : 'cust_' . wp_generate_password(8, false);
        $params['id'] = $id;
        $params['createdAt'] = current_time('Y-m-d');
        $data[] = $params;

        update_option('oft_customers_data', $data);

        return rest_ensure_response([
            'id'      => $id,
            'message' => '顧客を作成しました',
        ]);
    }

    /**
     * 顧客更新
     */
    public static function admin_update_customer($request) {
        $id = sanitize_text_field($request->get_param('id'));
        $params = $request->get_json_params();
        $data = get_option('oft_customers_data', []);

        $found = false;
        foreach ($data as &$customer) {
            if (isset($customer['id']) && $customer['id'] === $id) {
                $customer = array_merge($customer, $params);
                $found = true;
                break;
            }
        }
        unset($customer);

        if (!$found) {
            return new WP_Error('not_found', '顧客が見つかりません', ['status' => 404]);
        }

        update_option('oft_customers_data', $data);

        return rest_ensure_response([
            'id'      => $id,
            'message' => '顧客情報を更新しました',
        ]);
    }

    /**
     * 顧客削除
     */
    public static function admin_delete_customer($request) {
        $id = sanitize_text_field($request->get_param('id'));
        $data = get_option('oft_customers_data', []);

        $data = array_values(array_filter($data, function ($c) use ($id) {
            return !isset($c['id']) || $c['id'] !== $id;
        }));

        update_option('oft_customers_data', $data);

        return rest_ensure_response([
            'id'      => $id,
            'message' => '顧客を削除しました',
        ]);
    }

    // ====================================
    // お問い合わせ管理
    // ====================================

    /**
     * お問い合わせ一覧取得
     */
    public static function admin_get_inquiries($request) {
        $data = get_option('oft_inquiries_data', []);
        return rest_ensure_response($data);
    }

    /**
     * お問い合わせ更新（ステータス・メモ等）
     */
    public static function admin_update_inquiry($request) {
        $id = sanitize_text_field($request->get_param('id'));
        $params = $request->get_json_params();
        $data = get_option('oft_inquiries_data', []);

        $found = false;
        foreach ($data as &$inquiry) {
            if (isset($inquiry['id']) && $inquiry['id'] === $id) {
                $inquiry = array_merge($inquiry, $params);
                $found = true;
                break;
            }
        }
        unset($inquiry);

        if (!$found) {
            return new WP_Error('not_found', 'お問い合わせが見つかりません', ['status' => 404]);
        }

        update_option('oft_inquiries_data', $data);

        return rest_ensure_response([
            'id'      => $id,
            'message' => 'お問い合わせを更新しました',
        ]);
    }

    /**
     * お問い合わせ削除
     */
    public static function admin_delete_inquiry($request) {
        $id = sanitize_text_field($request->get_param('id'));
        $data = get_option('oft_inquiries_data', []);

        $data = array_values(array_filter($data, function ($i) use ($id) {
            return !isset($i['id']) || $i['id'] !== $id;
        }));

        update_option('oft_inquiries_data', $data);

        return rest_ensure_response([
            'id'      => $id,
            'message' => 'お問い合わせを削除しました',
        ]);
    }

    // ====================================
    // 設定管理
    // ====================================

    /**
     * 設定取得
     */
    public static function admin_get_settings($request) {
        $data = get_option('oft_site_settings', []);
        return rest_ensure_response($data);
    }

    /**
     * 設定更新
     */
    public static function admin_update_settings($request) {
        $params = $request->get_json_params();
        update_option('oft_site_settings', $params);

        return rest_ensure_response([
            'message' => '設定を更新しました',
        ]);
    }

    /**
     * 管理者通知メール送信ヘルパー
     */
    private static function send_admin_notification($subject, $body) {
        $admin_email = get_option('oft_notification_email', 'ishizawa@epoch-inc.jp');
        $headers = ['Content-Type: text/plain; charset=UTF-8'];
        wp_mail($admin_email, $subject, $body, $headers);
    }
}
