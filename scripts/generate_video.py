"""Gemini Veo APIで動画を生成するスクリプト"""
import time
import os
import json
from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyBmVE75M0WVjJy_-PvZrTtxJE_T3_RGOO4")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "site-a", "videos")

prompt = (
    "A stylish businessman in a dark suit sitting on a luxurious white down comforter on a modern bed, "
    "filmed from behind showing only his back and shoulders, no face visible. "
    "Elegant minimalist bedroom with soft natural morning light streaming through sheer curtains. "
    "The comforter is fluffy and pristine white. Cinematic slow motion, warm neutral tones, 4K quality. "
    "6 seconds, gentle camera movement."
)

print("Veo動画生成を開始します...")

operation = client.models.generate_videos(
    model="veo-3.0-generate-001",
    prompt=prompt,
    config=types.GenerateVideosConfig(
        person_generation="allow_all",
        aspect_ratio="16:9",
        number_of_videos=1,
    ),
)

print("生成中... (2-5分かかります)")

while not operation.done:
    time.sleep(20)
    operation = client.operations.get(operation)
    print("  処理中...")

print("生成完了！")
print(f"operation.result = {operation.result}")
print(f"operation type = {type(operation)}")
print(f"operation attrs = {[a for a in dir(operation) if not a.startswith('_')]}")

result = operation.result
if result is None:
    # responseを直接確認
    print(f"operation dict = {operation.__dict__}")
else:
    print(f"result type = {type(result)}")
    print(f"result attrs = {[a for a in dir(result) if not a.startswith('_')]}")

    if hasattr(result, 'generated_videos') and result.generated_videos:
        for video in result.generated_videos:
            print(f"video attrs = {[a for a in dir(video) if not a.startswith('_')]}")
            v = video.video
            print(f"video.video attrs = {[a for a in dir(v) if not a.startswith('_')]}")
            if hasattr(v, 'uri') and v.uri:
                import requests
                fname = os.path.join(OUTPUT_DIR, "comforter_hero_veo.mp4")
                resp = requests.get(v.uri)
                with open(fname, "wb") as f:
                    f.write(resp.content)
                print(f"保存: {fname} ({os.path.getsize(fname)//1024} KB)")
