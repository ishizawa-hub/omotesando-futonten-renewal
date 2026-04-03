#!/usr/bin/env python3
"""スクリーンショットをPDFにまとめるスクリプト
- PC版PDF: 1ページ = 1ページ分のスクリーンショット + ページ名 + URL + 修正指示欄
- スマホ版PDF: 同上
"""

import os
import json
from fpdf import FPDF
from PIL import Image

OUT_DIR = 'screenshots'
PAGES_JSON = os.path.join(OUT_DIR, 'pages.json')

# 日本語フォントパス（Windows）
JP_FONT = None
for path in [
    'C:/Windows/Fonts/meiryo.ttc',
    'C:/Windows/Fonts/msgothic.ttc',
    'C:/Windows/Fonts/YuGothM.ttc',
]:
    if os.path.exists(path):
        JP_FONT = path
        break


class PagePDF(FPDF):
    def __init__(self, title_text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title_text = title_text

    def header(self):
        self.set_font('Gothic', '', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 5, self.title_text, align='R', new_x='LMARGIN', new_y='NEXT')
        self.line(10, 12, self.w - 10, 12)
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font('Gothic', '', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'{self.page_no()} / {{nb}}', align='C')


def create_pdf(pages, device, label):
    """PCまたはスマホ用のPDFを生成"""
    img_dir = os.path.join(OUT_DIR, device)
    pdf = PagePDF(f'表参道布団店 サイトリニューアル - {label}キャプチャ一覧', orientation='L' if device == 'pc' else 'P', unit='mm', format='A4')
    pdf.alias_nb_pages()

    # フォント登録
    if JP_FONT:
        pdf.add_font('Gothic', '', JP_FONT, uni=True)
    else:
        pdf.add_font('Gothic', '', '', uni=True)

    pdf.set_auto_page_break(auto=False)

    for pg in pages:
        img_path = os.path.join(img_dir, f"{pg['safe']}.jpg")
        if not os.path.exists(img_path):
            continue

        pdf.add_page()

        # A4サイズ
        if device == 'pc':
            page_w, page_h = 297, 210  # 横向き
        else:
            page_w, page_h = 210, 297  # 縦向き

        margin = 10
        usable_w = page_w - margin * 2
        header_h = 14  # ヘッダー分

        # --- ページ名とURL ---
        pdf.set_font('Gothic', '', 12)
        pdf.set_text_color(45, 45, 45)
        pdf.cell(0, 6, pg['name'], new_x='LMARGIN', new_y='NEXT')

        pdf.set_font('Gothic', '', 7)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 4, pg['prod_url'], new_x='LMARGIN', new_y='NEXT')
        pdf.ln(2)

        info_h = pdf.get_y() - header_h

        # --- スクリーンショット画像 ---
        # 画像サイズ取得
        with Image.open(img_path) as img:
            img_w, img_h = img.size

        # 画像の表示領域
        if device == 'pc':
            # PC: 横向きA4の左側に画像、右側に修正指示欄
            img_area_w = usable_w * 0.62
            img_area_h = page_h - header_h - info_h - margin - 8
            note_area_w = usable_w * 0.35
        else:
            # スマホ: 縦向きA4の上部に画像、下部に修正指示欄
            img_area_w = usable_w * 0.4  # スマホは幅を抑える
            img_area_h = page_h - header_h - info_h - margin - 60  # 下に修正欄スペース
            note_area_w = usable_w

        # アスペクト比を維持してフィット
        scale_w = img_area_w / img_w
        scale_h = img_area_h / img_h
        scale = min(scale_w, scale_h)
        disp_w = img_w * scale
        disp_h = img_h * scale

        # 画像が長すぎる場合はクロップ（上部のみ表示）
        max_display_h = img_area_h
        if disp_h > max_display_h:
            disp_h = max_display_h
            disp_w = min(disp_w, img_area_w)

        img_x = margin
        img_y = pdf.get_y()

        # 画像の枠線
        pdf.set_draw_color(200, 200, 200)
        pdf.rect(img_x - 0.5, img_y - 0.5, disp_w + 1, disp_h + 1)

        pdf.image(img_path, x=img_x, y=img_y, w=disp_w, h=disp_h)

        # --- 修正指示記入欄 ---
        if device == 'pc':
            # PC: 画像の右側
            note_x = img_x + disp_w + 8
            note_y = img_y
            note_h = disp_h
        else:
            # スマホ: 画像の下
            note_x = margin
            note_y = img_y + disp_h + 4
            note_h = page_h - note_y - margin

        # 修正指示欄のタイトル
        pdf.set_xy(note_x, note_y)
        pdf.set_font('Gothic', '', 9)
        pdf.set_text_color(201, 169, 110)  # ゴールド
        pdf.cell(note_area_w, 5, '修正指示:', new_x='LMARGIN', new_y='NEXT')

        # 罫線付きの記入欄
        pdf.set_draw_color(220, 220, 220)
        line_spacing = 7
        start_y = note_y + 7
        lines = int((note_h - 7) / line_spacing)
        for i in range(lines):
            y = start_y + i * line_spacing
            if y < page_h - margin:
                pdf.line(note_x, y, note_x + note_area_w, y)

    # PDF保存
    output_path = os.path.join(OUT_DIR, f'site_capture_{device}.pdf')
    pdf.output(output_path)
    print(f"Generated: {output_path} ({pdf.page_no()} pages)")
    return output_path


def main():
    with open(PAGES_JSON, 'r', encoding='utf-8') as f:
        pages = json.load(f)

    print(f"Total pages: {len(pages)}")

    # PC版PDF（横向きA4）
    print("\n=== Generating PC PDF ===")
    create_pdf(pages, 'pc', 'PC')

    # スマホ版PDF（縦向きA4）
    print("\n=== Generating Mobile PDF ===")
    create_pdf(pages, 'mobile', 'スマホ')

    print("\nDone!")
    print(f"Output: {os.path.abspath(os.path.join(OUT_DIR, 'site_capture_pc.pdf'))}")
    print(f"Output: {os.path.abspath(os.path.join(OUT_DIR, 'site_capture_mobile.pdf'))}")


if __name__ == '__main__':
    main()
