<?php defined('ABSPATH') || exit; ?>
<div class="wrap oft-inventory">
    <h1>在庫管理</h1>

    <?php if (!empty($low_stock)) : ?>
    <div class="notice notice-warning">
        <p><strong>在庫アラート:</strong> <?php echo count($low_stock); ?>件の商品が残りわずかです。</p>
    </div>
    <?php endif; ?>

    <div class="oft-toolbar">
        <input type="text" id="oft-stock-search" placeholder="商品名で検索..." class="regular-text">
        <select id="oft-stock-filter">
            <option value="all">すべて</option>
            <option value="low">残りわずか</option>
            <option value="out">在庫切れ</option>
            <option value="in">在庫あり</option>
        </select>
        <button type="button" class="button button-primary" id="oft-bulk-save">
            <span class="dashicons dashicons-saved"></span> 一括保存
        </button>
    </div>

    <table class="widefat striped oft-stock-table" id="oft-stock-table">
        <thead>
            <tr>
                <th>商品名</th>
                <th>バリエーション</th>
                <th>SKU</th>
                <th>価格</th>
                <th style="width:120px">在庫数</th>
                <th>ステータス</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($products as $p) :
                $status_class = 'oft-ok';
                $status_label = '在庫あり';
                if ($p['stock_status'] === 'outofstock') {
                    $status_class = 'oft-danger';
                    $status_label = '在庫切れ';
                } elseif ($p['stock_qty'] !== null && $p['stock_qty'] <= OFT_Inventory::LOW_STOCK_THRESHOLD) {
                    $status_class = 'oft-warn';
                    $status_label = '残りわずか';
                }
            ?>
            <tr data-id="<?php echo esc_attr($p['id']); ?>" data-status="<?php echo esc_attr($p['stock_status']); ?>">
                <td>
                    <strong><?php echo esc_html($p['name']); ?></strong>
                    <?php if ($p['parent_id']) : ?>
                        <a href="<?php echo get_edit_post_link($p['parent_id']); ?>" class="row-actions" target="_blank">編集</a>
                    <?php endif; ?>
                </td>
                <td><?php echo esc_html($p['variation'] ?: '—'); ?></td>
                <td><code><?php echo esc_html($p['sku'] ?: '—'); ?></code></td>
                <td>¥<?php echo number_format($p['price']); ?></td>
                <td>
                    <input type="number"
                           class="oft-stock-input"
                           data-product-id="<?php echo esc_attr($p['id']); ?>"
                           data-original="<?php echo esc_attr($p['stock_qty'] ?? ''); ?>"
                           value="<?php echo esc_attr($p['stock_qty'] ?? ''); ?>"
                           min="0" step="1"
                           style="width:80px">
                </td>
                <td><span class="oft-status <?php echo $status_class; ?>"><?php echo esc_html($status_label); ?></span></td>
            </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
</div>
