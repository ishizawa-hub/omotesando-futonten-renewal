<?php
/**
 * ページコンテンツ管理
 * - 各ページのテキスト・画像をカスタムフィールドで管理
 * - 画像アップロード時に推奨サイズを表示
 * - REST API経由で静的サイトに配信
 */

defined('ABSPATH') || exit;

class OFT_Page_Manager {

    // サイトの全ページ定義
    const PAGES = [
        'top' => [
            'label' => 'TOPページ',
            'sections' => [
                'hero_title'     => ['label' => 'ヒーロータイトル', 'type' => 'text', 'default' => '最高品質の眠りを、あなたに。'],
                'hero_subtitle'  => ['label' => 'ヒーローサブタイトル', 'type' => 'text', 'default' => 'Omotesando Futon Ten.'],
                'hero_video'     => ['label' => 'ヒーロー動画', 'type' => 'video', 'note' => '推奨: MP4, 1280×720px, 16:9, 15-20秒'],
                'concept_title'  => ['label' => 'コンセプトセクション見出し', 'type' => 'text', 'default' => '清潔という贅沢'],
                'concept_body'   => ['label' => 'コンセプト本文', 'type' => 'textarea'],
                'concept_image'  => ['label' => 'コンセプト画像', 'type' => 'image', 'note' => '推奨: 800×600px, JPG/WebP'],
                'products_title' => ['label' => '商品セクション見出し', 'type' => 'text', 'default' => 'Products'],
                'news_title'     => ['label' => 'ニュースセクション見出し', 'type' => 'text', 'default' => 'News'],
            ],
        ],
        'concept' => [
            'label' => 'CONCEPTページ',
            'sections' => [
                'hero_title'    => ['label' => 'ヒーロータイトル', 'type' => 'text', 'default' => 'Clean Cycle Down'],
                'hero_image'    => ['label' => 'ヒーロー画像', 'type' => 'image', 'note' => '推奨: 1920×1080px, JPG/WebP, 16:9'],
                'story_title'   => ['label' => 'ストーリー見出し', 'type' => 'text'],
                'story_body'    => ['label' => 'ストーリー本文', 'type' => 'textarea'],
                'values_title'  => ['label' => 'バリュー見出し', 'type' => 'text'],
                'values_body'   => ['label' => 'バリュー本文', 'type' => 'textarea'],
            ],
        ],
        'products' => [
            'label' => '商品一覧ページ',
            'sections' => [
                'hero_title'    => ['label' => 'ヒーロータイトル', 'type' => 'text', 'default' => 'Products'],
                'hero_image'    => ['label' => 'ヒーロー画像', 'type' => 'image', 'note' => '推奨: 1920×600px, JPG/WebP'],
                'lead_text'     => ['label' => 'リードテキスト', 'type' => 'textarea'],
            ],
        ],
        'showroom' => [
            'label' => 'ショールームページ',
            'sections' => [
                'hero_title'    => ['label' => 'ヒーロータイトル', 'type' => 'text', 'default' => 'Showroom'],
                'hero_image'    => ['label' => 'ヒーロー画像', 'type' => 'image', 'note' => '推奨: 1920×1080px, JPG/WebP'],
                'address'       => ['label' => '住所', 'type' => 'text'],
                'hours'         => ['label' => '営業時間', 'type' => 'text'],
                'tel'           => ['label' => '電話番号', 'type' => 'text'],
                'access_text'   => ['label' => 'アクセス説明', 'type' => 'textarea'],
                'map_embed'     => ['label' => 'Google Map埋め込みURL', 'type' => 'url'],
            ],
        ],
        'magazine' => [
            'label' => 'MAGAZINEページ',
            'sections' => [
                'hero_title'    => ['label' => 'ヒーロータイトル', 'type' => 'text', 'default' => 'Magazine'],
                'hero_image'    => ['label' => 'ヒーロー画像', 'type' => 'image', 'note' => '推奨: 1920×600px, JPG/WebP'],
                'lead_text'     => ['label' => 'リードテキスト', 'type' => 'textarea'],
            ],
        ],
        'faq' => [
            'label' => 'FAQページ',
            'sections' => [
                'hero_title'    => ['label' => 'ヒーロータイトル', 'type' => 'text', 'default' => 'FAQ'],
                'lead_text'     => ['label' => 'リードテキスト', 'type' => 'textarea'],
            ],
        ],
        'contact' => [
            'label' => 'お問い合わせページ',
            'sections' => [
                'hero_title'    => ['label' => 'ヒーロータイトル', 'type' => 'text', 'default' => 'Contact'],
                'lead_text'     => ['label' => 'リードテキスト', 'type' => 'textarea'],
                'email'         => ['label' => '受付メールアドレス', 'type' => 'email'],
            ],
        ],
        'about' => [
            'label' => 'ABOUTページ',
            'sections' => [
                'hero_title'    => ['label' => 'ヒーロータイトル', 'type' => 'text', 'default' => 'About'],
                'hero_image'    => ['label' => 'ヒーロー画像', 'type' => 'image', 'note' => '推奨: 1920×1080px, JPG/WebP'],
                'company_name'  => ['label' => '会社名', 'type' => 'text'],
                'company_body'  => ['label' => '会社概要', 'type' => 'textarea'],
            ],
        ],
        'global' => [
            'label' => '共通設定（ヘッダー・フッター）',
            'sections' => [
                'site_logo'         => ['label' => 'サイトロゴ', 'type' => 'image', 'note' => '推奨: SVG or 400×100px PNG（透過）'],
                'footer_copyright'  => ['label' => 'フッターコピーライト', 'type' => 'text', 'default' => '© Omotesando Futon Ten.'],
                'footer_sns_x'      => ['label' => 'X (Twitter) URL', 'type' => 'url'],
                'footer_sns_ig'     => ['label' => 'Instagram URL', 'type' => 'url'],
                'footer_sns_line'   => ['label' => 'LINE公式 URL', 'type' => 'url'],
                'announcement'      => ['label' => 'お知らせバナー（空欄で非表示）', 'type' => 'text'],
                'announcement_link' => ['label' => 'お知らせリンクURL', 'type' => 'url'],
            ],
        ],
    ];

    // 画像タイプ別推奨サイズ
    const IMAGE_GUIDELINES = [
        'hero'    => ['w' => 1920, 'h' => 1080, 'ratio' => '16:9', 'format' => 'JPG/WebP', 'max_kb' => 500],
        'product' => ['w' => 800,  'h' => 1000, 'ratio' => '4:5',  'format' => 'JPG/WebP', 'max_kb' => 200],
        'thumb'   => ['w' => 400,  'h' => 400,  'ratio' => '1:1',  'format' => 'JPG/WebP', 'max_kb' => 100],
        'logo'    => ['w' => 400,  'h' => 100,  'ratio' => '4:1',  'format' => 'SVG/PNG',  'max_kb' => 50],
    ];

    public static function init() {
        add_action('wp_ajax_oft_save_page_content', [__CLASS__, 'ajax_save']);
        add_action('wp_ajax_oft_get_page_content', [__CLASS__, 'ajax_get']);
    }

    /**
     * デフォルトページデータ作成
     */
    public static function create_default_pages() {
        foreach (self::PAGES as $page_id => $page) {
            foreach ($page['sections'] as $field_id => $field) {
                $key = "oft_page_{$page_id}_{$field_id}";
                if (get_option($key) === false && isset($field['default'])) {
                    update_option($key, $field['default']);
                }
            }
        }
    }

    /**
     * ページエディタ画面レンダリング
     */
    public static function render_page_editor() {
        $current_page = sanitize_key($_GET['page_id'] ?? 'top');
        if (!isset(self::PAGES[$current_page])) {
            $current_page = 'top';
        }

        $page_def = self::PAGES[$current_page];
        $values = [];
        foreach ($page_def['sections'] as $field_id => $field) {
            $values[$field_id] = get_option("oft_page_{$current_page}_{$field_id}", $field['default'] ?? '');
        }

        include OFT_PLUGIN_DIR . 'admin/views/page-editor.php';
    }

    /**
     * AJAX: ページコンテンツ保存
     */
    public static function ajax_save() {
        check_ajax_referer('oft_admin_nonce', 'nonce');
        if (!current_user_can('manage_options')) {
            wp_send_json_error('権限がありません');
        }

        $page_id = sanitize_key($_POST['page_id'] ?? '');
        if (!isset(self::PAGES[$page_id])) {
            wp_send_json_error('無効なページ');
        }

        $saved = [];
        foreach (self::PAGES[$page_id]['sections'] as $field_id => $field) {
            $key = "oft_page_{$page_id}_{$field_id}";
            $value = $_POST["field_{$field_id}"] ?? '';

            switch ($field['type']) {
                case 'textarea':
                    $value = wp_kses_post($value);
                    break;
                case 'url':
                case 'email':
                    $value = sanitize_text_field($value);
                    break;
                case 'image':
                case 'video':
                    $value = absint($value); // attachment ID
                    break;
                default:
                    $value = sanitize_text_field($value);
            }

            update_option($key, $value);
            $saved[$field_id] = $value;
        }

        wp_send_json_success(['saved' => $saved, 'message' => '保存しました']);
    }

    /**
     * AJAX: ページコンテンツ取得
     */
    public static function ajax_get() {
        check_ajax_referer('oft_admin_nonce', 'nonce');

        $page_id = sanitize_key($_GET['page_id'] ?? 'top');
        if (!isset(self::PAGES[$page_id])) {
            wp_send_json_error('無効なページ');
        }

        $data = [];
        foreach (self::PAGES[$page_id]['sections'] as $field_id => $field) {
            $value = get_option("oft_page_{$page_id}_{$field_id}", $field['default'] ?? '');
            if (in_array($field['type'], ['image', 'video']) && $value) {
                $data[$field_id] = [
                    'id'  => $value,
                    'url' => wp_get_attachment_url($value),
                ];
            } else {
                $data[$field_id] = $value;
            }
        }

        wp_send_json_success($data);
    }

    /**
     * 全ページデータをまとめて取得（REST API用）
     */
    public static function get_all_content() {
        $result = [];
        foreach (self::PAGES as $page_id => $page) {
            $result[$page_id] = ['label' => $page['label'], 'fields' => []];
            foreach ($page['sections'] as $field_id => $field) {
                $value = get_option("oft_page_{$page_id}_{$field_id}", $field['default'] ?? '');
                if (in_array($field['type'], ['image', 'video']) && $value) {
                    $result[$page_id]['fields'][$field_id] = [
                        'value' => $value,
                        'url'   => wp_get_attachment_url($value),
                        'type'  => $field['type'],
                    ];
                } else {
                    $result[$page_id]['fields'][$field_id] = [
                        'value' => $value,
                        'type'  => $field['type'],
                    ];
                }
            }
        }
        return $result;
    }
}
