<?php defined('ABSPATH') || exit; ?>
<div class="wrap oft-dashboard">
    <h1>表参道布団店 ダッシュボード</h1>

    <div class="oft-cards">
        <?php
        // 注文サマリー
        $recent_orders = [];
        $order_stats = ['pending' => 0, 'processing' => 0, 'completed' => 0];
        if (class_exists('WooCommerce')) {
            $recent_orders = wc_get_orders(['limit' => 5, 'orderby' => 'date', 'order' => 'DESC']);
            foreach (['pending', 'processing', 'completed'] as $status) {
                $order_stats[$status] = count(wc_get_orders(['status' => $status, 'return' => 'ids', 'limit' => -1]));
            }
        }
        $inventory = OFT_Inventory::get_summary();
        $members = OFT_Member_Manager::get_summary();
        ?>

        <!-- 注文状況 -->
        <div class="oft-card">
            <div class="oft-card-header">
                <span class="dashicons dashicons-cart"></span>
                <h2>注文状況</h2>
            </div>
            <div class="oft-card-body">
                <div class="oft-stat-row">
                    <span class="oft-stat-label">未処理</span>
                    <span class="oft-stat-value oft-warn"><?php echo esc_html($order_stats['pending']); ?></span>
                </div>
                <div class="oft-stat-row">
                    <span class="oft-stat-label">処理中</span>
                    <span class="oft-stat-value"><?php echo esc_html($order_stats['processing']); ?></span>
                </div>
                <div class="oft-stat-row">
                    <span class="oft-stat-label">完了</span>
                    <span class="oft-stat-value oft-ok"><?php echo esc_html($order_stats['completed']); ?></span>
                </div>
            </div>
            <div class="oft-card-footer">
                <a href="<?php echo admin_url('edit.php?post_type=shop_order'); ?>">注文一覧を見る →</a>
            </div>
        </div>

        <!-- 在庫状況 -->
        <div class="oft-card">
            <div class="oft-card-header">
                <span class="dashicons dashicons-archive"></span>
                <h2>在庫状況</h2>
            </div>
            <div class="oft-card-body">
                <div class="oft-stat-row">
                    <span class="oft-stat-label">商品数</span>
                    <span class="oft-stat-value"><?php echo esc_html($inventory['total']); ?></span>
                </div>
                <div class="oft-stat-row">
                    <span class="oft-stat-label">在庫あり</span>
                    <span class="oft-stat-value oft-ok"><?php echo esc_html($inventory['in_stock']); ?></span>
                </div>
                <div class="oft-stat-row">
                    <span class="oft-stat-label">残りわずか</span>
                    <span class="oft-stat-value oft-warn"><?php echo esc_html($inventory['low_stock']); ?></span>
                </div>
                <div class="oft-stat-row">
                    <span class="oft-stat-label">在庫切れ</span>
                    <span class="oft-stat-value oft-danger"><?php echo esc_html($inventory['out_of_stock']); ?></span>
                </div>
            </div>
            <div class="oft-card-footer">
                <a href="<?php echo admin_url('admin.php?page=oft-inventory'); ?>">在庫管理 →</a>
            </div>
        </div>

        <!-- 会員 -->
        <div class="oft-card">
            <div class="oft-card-header">
                <span class="dashicons dashicons-groups"></span>
                <h2>会員</h2>
            </div>
            <div class="oft-card-body">
                <div class="oft-stat-row">
                    <span class="oft-stat-label">総会員数</span>
                    <span class="oft-stat-value"><?php echo esc_html($members['total']); ?></span>
                </div>
                <div class="oft-stat-row">
                    <span class="oft-stat-label">今月の新規</span>
                    <span class="oft-stat-value oft-ok"><?php echo esc_html($members['new_this_month']); ?></span>
                </div>
            </div>
            <div class="oft-card-footer">
                <a href="<?php echo admin_url('admin.php?page=oft-members'); ?>">会員一覧 →</a>
            </div>
        </div>

        <!-- サイト管理 -->
        <div class="oft-card">
            <div class="oft-card-header">
                <span class="dashicons dashicons-admin-site-alt3"></span>
                <h2>サイト管理</h2>
            </div>
            <div class="oft-card-body">
                <p>各ページのテキストや画像を管理画面から直接編集できます。</p>
                <ul class="oft-page-links">
                    <?php foreach (OFT_Page_Manager::PAGES as $id => $page) : ?>
                        <li>
                            <a href="<?php echo admin_url('admin.php?page=oft-pages&page_id=' . $id); ?>">
                                <?php echo esc_html($page['label']); ?>
                            </a>
                        </li>
                    <?php endforeach; ?>
                </ul>
            </div>
        </div>
    </div>

    <!-- 最近の注文 -->
    <?php if (!empty($recent_orders)) : ?>
    <div class="oft-section">
        <h2>最近の注文</h2>
        <table class="widefat striped">
            <thead>
                <tr>
                    <th>注文番号</th>
                    <th>日時</th>
                    <th>顧客</th>
                    <th>合計</th>
                    <th>ステータス</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($recent_orders as $order) : ?>
                <tr>
                    <td><a href="<?php echo $order->get_edit_order_url(); ?>">#<?php echo $order->get_id(); ?></a></td>
                    <td><?php echo $order->get_date_created() ? $order->get_date_created()->format('Y/m/d H:i') : '-'; ?></td>
                    <td><?php echo esc_html($order->get_billing_last_name() . ' ' . $order->get_billing_first_name()); ?></td>
                    <td>¥<?php echo number_format($order->get_total()); ?></td>
                    <td><span class="oft-status oft-status-<?php echo $order->get_status(); ?>"><?php echo wc_get_order_status_name($order->get_status()); ?></span></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
    <?php endif; ?>
</div>
