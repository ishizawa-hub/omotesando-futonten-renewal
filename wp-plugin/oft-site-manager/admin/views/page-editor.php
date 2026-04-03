<?php defined('ABSPATH') || exit; ?>
<div class="wrap oft-page-editor">
    <h1>ページコンテンツ管理: <?php echo esc_html($page_def['label']); ?></h1>

    <!-- ページ切り替えタブ -->
    <nav class="nav-tab-wrapper">
        <?php foreach (OFT_Page_Manager::PAGES as $id => $page) : ?>
            <a href="<?php echo admin_url('admin.php?page=oft-pages&page_id=' . $id); ?>"
               class="nav-tab <?php echo $current_page === $id ? 'nav-tab-active' : ''; ?>">
                <?php echo esc_html($page['label']); ?>
            </a>
        <?php endforeach; ?>
    </nav>

    <form id="oft-page-form" class="oft-form" data-page="<?php echo esc_attr($current_page); ?>">
        <?php wp_nonce_field('oft_admin_nonce', '_oft_nonce'); ?>

        <?php foreach ($page_def['sections'] as $field_id => $field) : ?>
            <div class="oft-field-group">
                <label for="field_<?php echo esc_attr($field_id); ?>">
                    <?php echo esc_html($field['label']); ?>
                </label>

                <?php if (!empty($field['note'])) : ?>
                    <p class="oft-field-note">
                        <span class="dashicons dashicons-info-outline"></span>
                        <?php echo esc_html($field['note']); ?>
                    </p>
                <?php endif; ?>

                <?php switch ($field['type']) :
                    case 'text':
                    case 'email':
                    case 'url': ?>
                        <input type="<?php echo esc_attr($field['type']); ?>"
                               id="field_<?php echo esc_attr($field_id); ?>"
                               name="field_<?php echo esc_attr($field_id); ?>"
                               value="<?php echo esc_attr($values[$field_id] ?? ''); ?>"
                               class="regular-text">
                        <?php break;

                    case 'textarea': ?>
                        <textarea id="field_<?php echo esc_attr($field_id); ?>"
                                  name="field_<?php echo esc_attr($field_id); ?>"
                                  rows="5"
                                  class="large-text"><?php echo esc_textarea($values[$field_id] ?? ''); ?></textarea>
                        <?php break;

                    case 'image': ?>
                        <div class="oft-media-field" data-field="field_<?php echo esc_attr($field_id); ?>">
                            <input type="hidden"
                                   id="field_<?php echo esc_attr($field_id); ?>"
                                   name="field_<?php echo esc_attr($field_id); ?>"
                                   value="<?php echo esc_attr($values[$field_id] ?? ''); ?>">
                            <div class="oft-media-preview">
                                <?php if (!empty($values[$field_id])) :
                                    $img_url = wp_get_attachment_url($values[$field_id]);
                                    if ($img_url) : ?>
                                        <img src="<?php echo esc_url($img_url); ?>" alt="">
                                    <?php endif;
                                endif; ?>
                            </div>
                            <button type="button" class="button oft-select-media">画像を選択</button>
                            <button type="button" class="button oft-remove-media" <?php echo empty($values[$field_id]) ? 'style="display:none"' : ''; ?>>削除</button>
                        </div>
                        <?php break;

                    case 'video': ?>
                        <div class="oft-media-field" data-field="field_<?php echo esc_attr($field_id); ?>" data-type="video">
                            <input type="hidden"
                                   id="field_<?php echo esc_attr($field_id); ?>"
                                   name="field_<?php echo esc_attr($field_id); ?>"
                                   value="<?php echo esc_attr($values[$field_id] ?? ''); ?>">
                            <div class="oft-media-preview">
                                <?php if (!empty($values[$field_id])) :
                                    $vid_url = wp_get_attachment_url($values[$field_id]);
                                    if ($vid_url) : ?>
                                        <video src="<?php echo esc_url($vid_url); ?>" controls width="320"></video>
                                    <?php endif;
                                endif; ?>
                            </div>
                            <button type="button" class="button oft-select-media">動画を選択</button>
                            <button type="button" class="button oft-remove-media" <?php echo empty($values[$field_id]) ? 'style="display:none"' : ''; ?>>削除</button>
                        </div>
                        <?php break;

                endswitch; ?>
            </div>
        <?php endforeach; ?>

        <div class="oft-form-actions">
            <button type="submit" class="button button-primary button-hero">
                <span class="dashicons dashicons-saved"></span> 保存する
            </button>
            <span class="oft-save-status"></span>
        </div>
    </form>
</div>
