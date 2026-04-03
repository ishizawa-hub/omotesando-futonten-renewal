<?php defined('ABSPATH') || exit; ?>
<div class="wrap oft-members">
    <h1>会員管理 <span class="oft-badge"><?php echo count($members); ?>名</span></h1>

    <table class="widefat striped">
        <thead>
            <tr>
                <th>ID</th>
                <th>氏名</th>
                <th>メール</th>
                <th>電話番号</th>
                <th>登録日</th>
                <th>注文数</th>
                <th>累計購入額</th>
            </tr>
        </thead>
        <tbody>
            <?php if (empty($members)) : ?>
                <tr><td colspan="7" style="text-align:center;padding:20px;">会員がまだいません</td></tr>
            <?php else : ?>
                <?php foreach ($members as $m) : ?>
                <tr>
                    <td><?php echo esc_html($m['id']); ?></td>
                    <td>
                        <a href="<?php echo get_edit_user_link($m['id']); ?>">
                            <?php echo esc_html($m['last_name'] . ' ' . $m['first_name']); ?>
                        </a>
                    </td>
                    <td><?php echo esc_html($m['email']); ?></td>
                    <td><?php echo esc_html($m['phone'] ?: '—'); ?></td>
                    <td><?php echo date('Y/m/d', strtotime($m['registered'])); ?></td>
                    <td><?php echo esc_html($m['order_count']); ?></td>
                    <td>¥<?php echo number_format($m['total_spent']); ?></td>
                </tr>
                <?php endforeach; ?>
            <?php endif; ?>
        </tbody>
    </table>
</div>
