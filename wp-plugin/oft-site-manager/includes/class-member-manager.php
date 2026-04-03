<?php
/**
 * 会員管理
 * - 新規会員登録（REST API）
 * - ログイン（JWT発行）
 * - 会員一覧ダッシュボード
 */

defined('ABSPATH') || exit;

class OFT_Member_Manager {

    public static function init() {
        // 会員ロール追加
        add_action('init', [__CLASS__, 'register_customer_role']);
    }

    /**
     * 顧客ロール確認
     */
    public static function register_customer_role() {
        if (!get_role('oft_customer')) {
            add_role('oft_customer', '表参道布団店 会員', [
                'read' => true,
            ]);
        }
    }

    /**
     * 会員管理ページ
     */
    public static function render_members_page() {
        $members = self::get_members();
        include OFT_PLUGIN_DIR . 'admin/views/members.php';
    }

    /**
     * 会員一覧取得
     */
    public static function get_members() {
        $users = get_users([
            'role__in' => ['customer', 'oft_customer'],
            'orderby'  => 'registered',
            'order'    => 'DESC',
            'number'   => 100,
        ]);

        $members = [];
        foreach ($users as $user) {
            $order_count = 0;
            $total_spent = 0;
            if (class_exists('WooCommerce')) {
                $customer = new WC_Customer($user->ID);
                $order_count = $customer->get_order_count();
                $total_spent = $customer->get_total_spent();
            }

            $members[] = [
                'id'           => $user->ID,
                'email'        => $user->user_email,
                'name'         => $user->display_name,
                'first_name'   => get_user_meta($user->ID, 'first_name', true),
                'last_name'    => get_user_meta($user->ID, 'last_name', true),
                'phone'        => get_user_meta($user->ID, 'billing_phone', true),
                'registered'   => $user->user_registered,
                'order_count'  => $order_count,
                'total_spent'  => $total_spent,
            ];
        }

        return $members;
    }

    /**
     * REST API: ログイン
     */
    public static function api_login($request) {
        $email    = sanitize_email($request->get_param('email'));
        $password = $request->get_param('password');

        if (empty($email) || empty($password)) {
            return new WP_Error('missing_fields', 'メールアドレスとパスワードは必須です', ['status' => 400]);
        }

        $user = wp_authenticate($email, $password);
        if (is_wp_error($user)) {
            return new WP_Error('auth_failed', 'メールアドレスまたはパスワードが正しくありません', ['status' => 401]);
        }

        // シンプルトークン生成（本番はJWTプラグイン推奨）
        $token = self::generate_token($user->ID);

        return rest_ensure_response([
            'token'   => $token,
            'user'    => [
                'id'    => $user->ID,
                'email' => $user->user_email,
                'name'  => $user->display_name,
            ],
        ]);
    }

    /**
     * REST API: 新規会員登録
     */
    public static function api_register($request) {
        $email      = sanitize_email($request->get_param('email'));
        $password   = $request->get_param('password');
        $last_name  = sanitize_text_field($request->get_param('last_name') ?? '');
        $first_name = sanitize_text_field($request->get_param('first_name') ?? '');
        $phone      = sanitize_text_field($request->get_param('phone') ?? '');

        if (empty($email) || empty($password)) {
            return new WP_Error('missing_fields', 'メールアドレスとパスワードは必須です', ['status' => 400]);
        }

        if (email_exists($email)) {
            return new WP_Error('email_exists', 'このメールアドレスは既に登録されています', ['status' => 409]);
        }

        if (strlen($password) < 8) {
            return new WP_Error('weak_password', 'パスワードは8文字以上で設定してください', ['status' => 400]);
        }

        $user_id = wp_create_user($email, $password, $email);
        if (is_wp_error($user_id)) {
            return new WP_Error('registration_failed', '登録に失敗しました', ['status' => 500]);
        }

        $user = get_user_by('id', $user_id);
        $user->set_role('customer');

        update_user_meta($user_id, 'first_name', $first_name);
        update_user_meta($user_id, 'last_name', $last_name);
        update_user_meta($user_id, 'billing_phone', $phone);
        update_user_meta($user_id, 'billing_email', $email);
        wp_update_user(['ID' => $user_id, 'display_name' => $last_name . ' ' . $first_name]);

        $token = self::generate_token($user_id);

        // 管理者へ新規会員登録通知メール
        self::send_registration_notification($user_id, $email, $last_name, $first_name, $phone);

        return rest_ensure_response([
            'token'   => $token,
            'user'    => [
                'id'    => $user_id,
                'email' => $email,
                'name'  => $last_name . ' ' . $first_name,
            ],
            'message' => '会員登録が完了しました',
        ]);
    }

    /**
     * 新規会員登録通知メール送信
     */
    private static function send_registration_notification($user_id, $email, $last_name, $first_name, $phone) {
        $admin_email = get_option('oft_notification_email', 'ishizawa@epoch-inc.jp');
        $subject = '【表参道布団店】新規会員登録がありました';
        $body = "新規会員登録がありました。\n\n"
              . "━━━━━━━━━━━━━━━━━━━━━━━\n"
              . "会員ID: {$user_id}\n"
              . "氏名: {$last_name} {$first_name}\n"
              . "メール: {$email}\n"
              . "電話番号: {$phone}\n"
              . "登録日時: " . current_time('Y年m月d日 H:i') . "\n"
              . "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
              . "管理画面で確認: " . admin_url('admin.php?page=oft-members') . "\n";

        $headers = ['Content-Type: text/plain; charset=UTF-8'];
        wp_mail($admin_email, $subject, $body, $headers);
    }

    /**
     * トークン生成
     */
    private static function generate_token($user_id) {
        $secret = defined('AUTH_KEY') ? AUTH_KEY : wp_generate_password(64);
        $payload = $user_id . '|' . time() . '|' . wp_generate_password(16, false);
        $token = hash_hmac('sha256', $payload, $secret);

        // トークンをユーザーメタに保存（有効期限: 30日）
        update_user_meta($user_id, '_oft_auth_token', $token);
        update_user_meta($user_id, '_oft_auth_token_expires', time() + (30 * DAY_IN_SECONDS));

        return $token;
    }

    /**
     * トークン検証
     */
    public static function validate_token($token) {
        $users = get_users([
            'meta_key'   => '_oft_auth_token',
            'meta_value' => $token,
            'number'     => 1,
        ]);

        if (empty($users)) return false;

        $user = $users[0];
        $expires = get_user_meta($user->ID, '_oft_auth_token_expires', true);

        if ($expires < time()) {
            delete_user_meta($user->ID, '_oft_auth_token');
            return false;
        }

        return $user;
    }

    /**
     * 会員サマリー（ダッシュボード用）
     */
    public static function get_summary() {
        $total = count_users();
        $customers = count(get_users(['role__in' => ['customer', 'oft_customer'], 'fields' => 'ID']));
        $new_this_month = count(get_users([
            'role__in'   => ['customer', 'oft_customer'],
            'date_query' => [['after' => '1 month ago']],
            'fields'     => 'ID',
        ]));

        return [
            'total'          => $customers,
            'new_this_month' => $new_this_month,
        ];
    }
}
