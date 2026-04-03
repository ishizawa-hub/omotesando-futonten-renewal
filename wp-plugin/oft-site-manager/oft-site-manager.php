<?php
/**
 * Plugin Name: 表参道布団店 サイトマネージャー
 * Description: 表参道布団店の静的サイト管理・EC連携・在庫管理プラグイン
 * Version: 1.0.0
 * Author: Omotesando Futon Ten
 * Text Domain: oft-manager
 * Requires Plugins: woocommerce
 */

defined('ABSPATH') || exit;

define('OFT_VERSION', '1.0.0');
define('OFT_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('OFT_PLUGIN_URL', plugin_dir_url(__FILE__));

// WooCommerce依存チェック
add_action('admin_init', function () {
    if (!class_exists('WooCommerce')) {
        add_action('admin_notices', function () {
            echo '<div class="notice notice-error"><p>表参道布団店サイトマネージャーにはWooCommerceが必要です。</p></div>';
        });
    }
});

// プラグインファイル読み込み
require_once OFT_PLUGIN_DIR . 'includes/class-admin-menu.php';
require_once OFT_PLUGIN_DIR . 'includes/class-page-manager.php';
require_once OFT_PLUGIN_DIR . 'includes/class-inventory.php';
require_once OFT_PLUGIN_DIR . 'includes/class-rest-api.php';
require_once OFT_PLUGIN_DIR . 'includes/class-stripe-checkout.php';
require_once OFT_PLUGIN_DIR . 'includes/class-member-manager.php';

// 初期化
add_action('plugins_loaded', function () {
    OFT_Admin_Menu::init();
    OFT_Page_Manager::init();
    OFT_Inventory::init();
    OFT_REST_API::init();
    OFT_Stripe_Checkout::init();
    OFT_Member_Manager::init();
});

// 管理画面CSS/JS
add_action('admin_enqueue_scripts', function ($hook) {
    if (strpos($hook, 'oft-') === false && strpos($hook, 'toplevel_page_oft') === false) {
        return;
    }
    wp_enqueue_style('oft-admin', OFT_PLUGIN_URL . 'admin/css/admin-style.css', [], OFT_VERSION);
    wp_enqueue_script('oft-admin', OFT_PLUGIN_URL . 'admin/js/admin.js', ['jquery'], OFT_VERSION, true);
    wp_localize_script('oft-admin', 'oftAdmin', [
        'ajaxUrl' => admin_url('admin-ajax.php'),
        'nonce'   => wp_create_nonce('oft_admin_nonce'),
        'restUrl' => rest_url('oft/v1/'),
    ]);
});

// プラグイン有効化時
register_activation_hook(__FILE__, function () {
    OFT_Page_Manager::create_default_pages();
    flush_rewrite_rules();
});
