<?php defined('ABSPATH') || exit; ?>
<div class="wrap oft-settings">
    <h1>サイト設定</h1>

    <form method="post">
        <?php wp_nonce_field('oft_settings'); ?>

        <table class="form-table">
            <tr>
                <th scope="row">静的サイトURL</th>
                <td>
                    <input type="url" name="oft_static_site_url"
                           value="<?php echo esc_attr(get_option('oft_static_site_url', 'https://ishizawa-hub.github.io/omotesando-futonten-renewal/site-a')); ?>"
                           class="regular-text">
                    <p class="description">GitHub Pagesの公開URL</p>
                </td>
            </tr>
            <tr>
                <th scope="row">GitHubリポジトリ</th>
                <td>
                    <input type="text" name="oft_github_repo"
                           value="<?php echo esc_attr(get_option('oft_github_repo', 'ishizawa-hub/omotesando-futonten-renewal')); ?>"
                           class="regular-text">
                    <p class="description">owner/repo形式</p>
                </td>
            </tr>
            <tr>
                <th scope="row">Stripe動作モード</th>
                <td>
                    <select name="oft_stripe_mode">
                        <option value="test" <?php selected(get_option('oft_stripe_mode', 'test'), 'test'); ?>>テストモード</option>
                        <option value="live" <?php selected(get_option('oft_stripe_mode'), 'live'); ?>>本番モード</option>
                    </select>
                </td>
            </tr>
        </table>

        <h2>画像アップロードガイドライン</h2>
        <table class="widefat">
            <thead>
                <tr><th>用途</th><th>推奨サイズ</th><th>比率</th><th>形式</th><th>最大容量</th></tr>
            </thead>
            <tbody>
                <?php foreach (OFT_Page_Manager::IMAGE_GUIDELINES as $type => $g) : ?>
                <tr>
                    <td><strong><?php echo esc_html(ucfirst($type)); ?></strong></td>
                    <td><?php echo esc_html("{$g['w']}×{$g['h']}px"); ?></td>
                    <td><?php echo esc_html($g['ratio']); ?></td>
                    <td><?php echo esc_html($g['format']); ?></td>
                    <td><?php echo esc_html($g['max_kb'] . 'KB'); ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>

        <p class="submit">
            <input type="submit" name="oft_save_settings" class="button-primary" value="設定を保存">
        </p>
    </form>
</div>
