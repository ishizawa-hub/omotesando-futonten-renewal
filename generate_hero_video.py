#!/usr/bin/env python3
"""7カットのヒーロー動画をVeo 3.0で生成し、ffmpegで結合する"""

import time
import os
import sys
from google import genai
from google.genai import types

API_KEY = 'AIzaSyCt7J1pzqihcIIp2pFdLK2xgFnB9zPkj24'
MODEL = 'veo-3.0-fast-generate-001'
OUT_DIR = 'site-a/videos/hero_cuts'

# 7カットのプロンプト（統一カラーグレード指示付き）
COLOR_GRADE = "Color grade: cool-neutral tones, desaturated with subtle blue undertone, high contrast, clean and cinematic. No warm yellow or green cast. Professional commercial footage, 24fps."

CUTS = [
    {
        'name': 'cut1_feathers',
        'prompt': f"Cinematic extreme close-up of pure white goose down feathers floating weightlessly in soft diffused backlight against a clean dark charcoal background. Individual delicate barbs catching cool light. Macro lens, shallow depth of field, slow motion. {COLOR_GRADE}",
    },
    {
        'name': 'cut2_river',
        'prompt': f"Cinematic wide shot of a pristine crystal-clear mountain river in Hakushu Japan, sunlight reflecting off the water surface creating beautiful lens flares and light streaks. Shallow rapids over smooth river stones, lush green forest in background. Golden hour light with anamorphic lens flare. Slow motion water movement. {COLOR_GRADE}",
    },
    {
        'name': 'cut3_washer',
        'prompt': f"Cinematic tracking shot pushing into a front-loading industrial drum washing machine with a transparent glass door. Camera slowly tracks forward through the glass into the churning water inside. White goose down feathers swirling and tumbling in clear blue-tinted water with air bubbles. Underwater photography look. Dramatic slow motion. {COLOR_GRADE}",
    },
    {
        'name': 'cut4_quilting',
        'prompt': f"Cinematic close-up of an industrial sewing machine needle stitching a baffle-box quilted pattern on a premium white down comforter. The needle moves precisely along straight lines creating 3D box compartments. Clean white fabric with subtle texture. Shallow depth of field, smooth camera movement. {COLOR_GRADE}",
    },
    {
        'name': 'cut5_logo_embroidery',
        'prompt': f"Cinematic extreme close-up of a sewing machine embroidering a minimalist Japanese brand logo in dark thread onto a white fabric label tag attached to a premium down comforter. The needle moves precisely creating clean typography. Shallow depth of field, macro lens. {COLOR_GRADE}",
    },
    {
        'name': 'cut6_bedroom',
        'prompt': f"Cinematic slow motion shot in a stylish modern masculine bedroom with dark walls and warm ambient lighting. A premium white baffle-box quilted down comforter with black piping trim is being gently laid onto a double bed. The comforter billows and settles softly in slow motion. Clean minimalist interior design. {COLOR_GRADE}",
    },
]


def generate_cut(client, cut):
    """1カットの動画を生成"""
    out_path = os.path.join(OUT_DIR, f"{cut['name']}.mp4")

    # すでに存在するならスキップ
    if os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
        print(f"  SKIP {cut['name']} (already exists)")
        return out_path

    print(f"  Requesting {cut['name']}...")
    try:
        op = client.models.generate_videos(
            model=MODEL,
            prompt=cut['prompt'],
            config=types.GenerateVideosConfig(
                person_generation="dont_allow",
                aspect_ratio="16:9",
            ),
        )
        print(f"  Operation: {op.name}")

        # ポーリング
        attempts = 0
        while not op.done:
            time.sleep(15)
            op = client.operations.get(op)
            attempts += 1
            if attempts % 4 == 0:
                print(f"    ...waiting ({attempts * 15}s)")

        if op.result and op.result.generated_videos:
            video = op.result.generated_videos[0]
            client.files.download(file=video.video, download_path=out_path)
            print(f"  OK {cut['name']} -> {out_path}")
            return out_path
        else:
            err = getattr(op, 'error', 'Unknown error')
            print(f"  FAIL {cut['name']}: {err}")
            return None
    except Exception as e:
        print(f"  ERROR {cut['name']}: {e}")
        return None


def main():
    client = genai.Client(api_key=API_KEY)

    print(f"=== Generating {len(CUTS)} cuts with {MODEL} ===\n")

    results = {}
    for i, cut in enumerate(CUTS):
        print(f"\n[Cut {i+1}/6] {cut['name']}")
        path = generate_cut(client, cut)
        results[cut['name']] = path

    # 結果サマリー
    print("\n=== Results ===")
    for name, path in results.items():
        status = "OK" if path else "FAILED"
        print(f"  {name}: {status}")

    ok_count = sum(1 for p in results.values() if p)
    print(f"\n{ok_count}/{len(CUTS)} cuts generated successfully")


if __name__ == '__main__':
    main()
