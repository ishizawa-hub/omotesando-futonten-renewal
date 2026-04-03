<?php
/**
 * 管理メニュー整理 + カスタムダッシュボード
 * - WP不要メニューを非表示
 * - 表参道布団店専用メニューを追加
 */

defined('ABSPATH') || exit;

class OFT_Admin_Menu {

    public static function init() {
        add_action('admin_menu', [__CLASS__, 'register_menus'], 5);
        add_action('admin_menu', [__CLASS__, 'remove_unused_menus'], 999);
        add_action('admin_bar_menu', [__CLASS__, 'customize_admin_bar'], 999);
        add_filter('admin_footer_text', [__CLASS__, 'admin_footer']);
    }

    /**
     * カスタムメニュー登録
     */
    public static function register_menus() {
        // メインダッシュボード
        add_menu_page(
            '表参道布団店',
            '布団店ダッシュボード',
            'manage_options',
            'oft-dashboard',
            [__CLASS__, 'render_dashboard'],
            'dashicons-store',
            2
        );

        // サイトコンテンツ管理
        add_submenu_page(
            'oft-dashboard',
            'ページコンテンツ管理',
            'ページ管理',
            'manage_options',
            'oft-pages',
            ['OFT_Page_Manager', 'render_page_editor']
        );

        // 在庫管理
        add_submenu_page(
            'oft-dashboard',
            '在庫管理',
            '在庫管理',
            'manage_woocommerce',
            'oft-inventory',
            ['OFT_Inventory', 'render_inventory_page']
        );

        // 会員管理
        add_submenu_page(
            'oft-dashboard',
            '会員管理',
            '会員管理',
            'manage_options',
            'oft-members',
            ['OFT_Member_Manager', 'render_members_page']
        );

        // 設定
        add_submenu_page(
            'oft-dashboard',
            'サイト設定',
            '設定',
            'manage_options',
            'oft-settings',
            [__CLASS__, 'render_settings']
        );
    }

    /**
     * 不要なWPデフォルトメニューを削除
     */
    public static function remove_unused_menus() {
        // 投稿（ブログ不使用）
        remove_menu_page('edit.php');
        // コメント
        remove_menu_page('edit-comments.php');
        // デフォルトダッシュボード（カスタムに置換）
        remove_submenu_page('index.php', 'index.php');
        // カスタマイザー（静的サイトなので不要）
        remove_submenu_page('themes.php', 'customize.php?return=' . urlencode($_SERVER['REQUEST_URI'] ?? ''));
        // テーマエディタ（セキュリティリスク）
        remove_submenu_page('themes.php', 'theme-editor.php');
        // プラグインエディタ
        remove_submenu_page('plugins.php', 'plugin-editor.php');
    }

    /**
     * ダッシュボード表示
     */
    public static function render_dashboard() {
        include OFT_PLUGIN_DIR . 'admin/views/dashboard.php';
    }

    /**
     * 設定ページ表示
     */
    public static function render_settings() {
        if (isset($_POST['oft_save_settings']) && wp_verify_nonce($_POST['_wpnonce'] ?? '', 'oft_settings')) {
            update_option('oft_static_site_url', sanitize_url($_POST['oft_static_site_url'] ?? ''));
            update_option('oft_stripe_mode', sanitize_text_field($_POST['oft_stripe_mode'] ?? 'test'));
            update_option('oft_github_repo', sanitize_text_field($_POST['oft_github_repo'] ?? ''));
            echo '<div class="notice notice-success"><p>設定を保存しました。</p></div>';
        }
        include OFT_PLUGIN_DIR . 'admin/views/settings.php';
    }

    /**
     * 管理バーカスタマイズ
     */
    public static function customize_admin_bar($wp_admin_bar) {
        $wp_admin_bar->remove_node('wp-logo');
        $wp_admin_bar->remove_node('comments');
        $wp_admin_bar->add_node([
            'id'    => 'oft-site',
            'title' => '🛏 表参道布団店サイト',
            'href'  => get_option('oft_static_site_url', 'https://ishizawa-hub.github.io/omotesando-futonten-renewal/site-a/'),
            'meta'  => ['target' => '_blank'],
        ]);
    }

    public static function admin_footer() {
        return '表参道布団店 サイトマネージャー v' . OFT_VERSION;
    }
}
