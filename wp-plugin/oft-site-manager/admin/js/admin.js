/**
 * 表参道布団店 管理画面JavaScript
 * ページエディターAJAX保存 / メディアピッカー / 在庫管理
 */
(function ($) {
    'use strict';

    /* ============================================================
     *  ページエディター: AJAX保存
     * ============================================================ */
    $('#oft-page-form').on('submit', function (e) {
        e.preventDefault();
        var $form = $(this);
        var $btn = $form.find('.button-hero');
        var $status = $form.find('.oft-save-status');
        var pageId = $form.data('page');

        // フォームデータ収集
        var fields = {};
        $form.find('[name^="field_"]').each(function () {
            var key = this.name.replace('field_', '');
            fields[key] = $(this).val();
        });

        $btn.prop('disabled', true);
        $form.addClass('oft-loading');

        $.post(oftAdmin.ajaxUrl, {
            action: 'oft_save_page',
            _oft_nonce: $form.find('[name="_oft_nonce"]').val(),
            page_id: pageId,
            fields: fields
        })
        .done(function (res) {
            if (res.success) {
                $status.text('保存しました').addClass('show');
                setTimeout(function () { $status.removeClass('show'); }, 3000);
            } else {
                alert('保存エラー: ' + (res.data || '不明なエラー'));
            }
        })
        .fail(function () {
            alert('通信エラーが発生しました');
        })
        .always(function () {
            $btn.prop('disabled', false);
            $form.removeClass('oft-loading');
        });
    });

    /* ============================================================
     *  メディアピッカー (画像・動画)
     * ============================================================ */
    var mediaFrame;

    $(document).on('click', '.oft-select-media', function (e) {
        e.preventDefault();
        var $container = $(this).closest('.oft-media-field');
        var $input = $container.find('input[type="hidden"]');
        var $preview = $container.find('.oft-media-preview');
        var $removeBtn = $container.find('.oft-remove-media');
        var isVideo = $container.data('type') === 'video';

        mediaFrame = wp.media({
            title: isVideo ? '動画を選択' : '画像を選択',
            library: { type: isVideo ? 'video' : 'image' },
            button: { text: '選択する' },
            multiple: false
        });

        mediaFrame.on('select', function () {
            var attachment = mediaFrame.state().get('selection').first().toJSON();
            $input.val(attachment.id);

            if (isVideo) {
                $preview.html('<video src="' + attachment.url + '" controls width="320"></video>');
            } else {
                var thumbUrl = attachment.sizes && attachment.sizes.medium
                    ? attachment.sizes.medium.url
                    : attachment.url;
                $preview.html('<img src="' + thumbUrl + '" alt="">');
            }

            $removeBtn.show();
        });

        mediaFrame.open();
    });

    $(document).on('click', '.oft-remove-media', function (e) {
        e.preventDefault();
        var $container = $(this).closest('.oft-media-field');
        $container.find('input[type="hidden"]').val('');
        $container.find('.oft-media-preview').empty();
        $(this).hide();
    });

    /* ============================================================
     *  在庫管理: 変更検知
     * ============================================================ */
    $(document).on('input', '.oft-stock-input', function () {
        var orig = $(this).data('original');
        var current = $(this).val();
        $(this).toggleClass('changed', String(orig) !== String(current));
    });

    /* ============================================================
     *  在庫管理: 一括保存
     * ============================================================ */
    $('#oft-bulk-save').on('click', function () {
        var $btn = $(this);
        var updates = [];

        $('.oft-stock-input.changed').each(function () {
            updates.push({
                product_id: $(this).data('product-id'),
                stock_qty: parseInt($(this).val(), 10) || 0
            });
        });

        if (updates.length === 0) {
            alert('変更された在庫はありません');
            return;
        }

        $btn.prop('disabled', true).text('保存中...');

        $.post(oftAdmin.ajaxUrl, {
            action: 'oft_bulk_update_stock',
            _ajax_nonce: oftAdmin.nonce,
            updates: JSON.stringify(updates)
        })
        .done(function (res) {
            if (res.success) {
                // 変更状態リセット
                $('.oft-stock-input.changed').each(function () {
                    $(this).data('original', $(this).val()).removeClass('changed');
                });
                // ステータスバッジ更新
                updates.forEach(function (u) {
                    var $row = $('[data-id="' + u.product_id + '"]');
                    var $badge = $row.find('.oft-status');
                    if (u.stock_qty <= 0) {
                        $badge.attr('class', 'oft-status oft-danger').text('在庫切れ');
                        $row.data('status', 'outofstock');
                    } else if (u.stock_qty <= 5) {
                        $badge.attr('class', 'oft-status oft-warn').text('残りわずか');
                        $row.data('status', 'instock');
                    } else {
                        $badge.attr('class', 'oft-status oft-ok').text('在庫あり');
                        $row.data('status', 'instock');
                    }
                });
                alert('在庫を更新しました (' + updates.length + '件)');
            } else {
                alert('更新エラー: ' + (res.data || '不明なエラー'));
            }
        })
        .fail(function () {
            alert('通信エラーが発生しました');
        })
        .always(function () {
            $btn.prop('disabled', false).html('<span class="dashicons dashicons-saved"></span> 一括保存');
        });
    });

    /* ============================================================
     *  在庫管理: 検索フィルター
     * ============================================================ */
    var $searchInput = $('#oft-stock-search');
    var $filterSelect = $('#oft-stock-filter');

    function filterInventory() {
        var query = ($searchInput.val() || '').toLowerCase();
        var status = $filterSelect.val();

        $('#oft-stock-table tbody tr').each(function () {
            var $row = $(this);
            var name = $row.find('td:first').text().toLowerCase();
            var rowStatus = $row.data('status');
            var stockQty = parseInt($row.find('.oft-stock-input').val(), 10);

            var matchSearch = !query || name.indexOf(query) !== -1;
            var matchFilter = true;

            if (status === 'low') {
                matchFilter = stockQty > 0 && stockQty <= 5;
            } else if (status === 'out') {
                matchFilter = rowStatus === 'outofstock' || stockQty <= 0;
            } else if (status === 'in') {
                matchFilter = rowStatus !== 'outofstock' && stockQty > 0;
            }

            $row.toggleClass('oft-row-hidden', !(matchSearch && matchFilter));
        });
    }

    $searchInput.on('input', filterInventory);
    $filterSelect.on('change', filterInventory);

})(jQuery);
