<?php
/**
 * 在庫管理
 * - WooCommerce商品の在庫状況をダッシュボード表示
 * - 一括在庫更新
 * - 在庫アラート
 */

defined('ABSPATH') || exit;

class OFT_Inventory {

    const LOW_STOCK_THRESHOLD = 5;

    public static function init() {
        add_action('wp_ajax_oft_update_stock', [__CLASS__, 'ajax_update_stock']);
        add_action('wp_ajax_oft_bulk_update_stock', [__CLASS__, 'ajax_bulk_update']);
    }

    /**
     * 在庫管理ページ表示
     */
    public static function render_inventory_page() {
        $products = self::get_inventory_data();
        $low_stock = array_filter($products, function ($p) {
            return $p['stock_qty'] !== null && $p['stock_qty'] <= self::LOW_STOCK_THRESHOLD;
        });
        include OFT_PLUGIN_DIR . 'admin/views/inventory.php';
    }

    /**
     * 全商品の在庫データ取得
     */
    public static function get_inventory_data() {
        if (!class_exists('WooCommerce')) return [];

        $args = [
            'post_type'      => 'product',
            'posts_per_page' => -1,
            'post_status'    => 'publish',
            'orderby'        => 'title',
            'order'          => 'ASC',
        ];
        $query = new WP_Query($args);
        $products = [];

        foreach ($query->posts as $post) {
            $product = wc_get_product($post->ID);
            if (!$product) continue;

            if ($product->is_type('variable')) {
                foreach ($product->get_children() as $child_id) {
                    $variation = wc_get_product($child_id);
                    if (!$variation) continue;
                    $products[] = [
                        'id'            => $child_id,
                        'parent_id'     => $post->ID,
                        'name'          => $product->get_name(),
                        'variation'     => implode(' / ', $variation->get_variation_attributes()),
                        'sku'           => $variation->get_sku(),
                        'price'         => $variation->get_price(),
                        'stock_qty'     => $variation->get_stock_quantity(),
                        'stock_status'  => $variation->get_stock_status(),
                        'manage_stock'  => $variation->get_manage_stock(),
                    ];
                }
            } else {
                $products[] = [
                    'id'            => $post->ID,
                    'parent_id'     => null,
                    'name'          => $product->get_name(),
                    'variation'     => '',
                    'sku'           => $product->get_sku(),
                    'price'         => $product->get_price(),
                    'stock_qty'     => $product->get_stock_quantity(),
                    'stock_status'  => $product->get_stock_status(),
                    'manage_stock'  => $product->get_manage_stock(),
                ];
            }
        }

        return $products;
    }

    /**
     * AJAX: 個別在庫更新
     */
    public static function ajax_update_stock() {
        check_ajax_referer('oft_admin_nonce', 'nonce');
        if (!current_user_can('manage_woocommerce')) {
            wp_send_json_error('権限がありません');
        }

        $product_id = absint($_POST['product_id'] ?? 0);
        $new_qty    = intval($_POST['stock_qty'] ?? 0);
        $product    = wc_get_product($product_id);

        if (!$product) {
            wp_send_json_error('商品が見つかりません');
        }

        $product->set_manage_stock(true);
        $product->set_stock_quantity($new_qty);
        $product->set_stock_status($new_qty > 0 ? 'instock' : 'outofstock');
        $product->save();

        wp_send_json_success([
            'product_id' => $product_id,
            'stock_qty'  => $new_qty,
            'message'    => '在庫を更新しました',
        ]);
    }

    /**
     * AJAX: 一括在庫更新
     */
    public static function ajax_bulk_update() {
        check_ajax_referer('oft_admin_nonce', 'nonce');
        if (!current_user_can('manage_woocommerce')) {
            wp_send_json_error('権限がありません');
        }

        $updates = json_decode(stripslashes($_POST['updates'] ?? '[]'), true);
        if (!is_array($updates)) {
            wp_send_json_error('無効なデータ');
        }

        $results = [];
        foreach ($updates as $item) {
            $product_id = absint($item['id'] ?? 0);
            $new_qty    = intval($item['qty'] ?? 0);
            $product    = wc_get_product($product_id);
            if (!$product) continue;

            $product->set_manage_stock(true);
            $product->set_stock_quantity($new_qty);
            $product->set_stock_status($new_qty > 0 ? 'instock' : 'outofstock');
            $product->save();
            $results[] = ['id' => $product_id, 'qty' => $new_qty];
        }

        wp_send_json_success(['updated' => count($results), 'message' => count($results) . '件の在庫を更新しました']);
    }

    /**
     * 在庫サマリー取得（ダッシュボード用）
     */
    public static function get_summary() {
        $products = self::get_inventory_data();
        $total = count($products);
        $in_stock = count(array_filter($products, fn($p) => $p['stock_status'] === 'instock'));
        $low_stock = count(array_filter($products, fn($p) => $p['stock_qty'] !== null && $p['stock_qty'] <= self::LOW_STOCK_THRESHOLD && $p['stock_qty'] > 0));
        $out_of_stock = count(array_filter($products, fn($p) => $p['stock_status'] === 'outofstock'));

        return compact('total', 'in_stock', 'low_stock', 'out_of_stock');
    }
}
