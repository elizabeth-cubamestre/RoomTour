"""Check your Google/Gemini key.
  python check_gemini.py                 -> lists models you can use
  python check_gemini.py MODEL_NAME      -> sends a tiny image to MODEL_NAME
Copy the model name exactly as printed (without the 'models/' prefix).
"""
import base64, os, struct, sys, zlib

import httpx
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("GEMINI_API_KEY")
BASE = "https://generativelanguage.googleapis.com/v1beta"
if not KEY:
    sys.exit("GEMINI_API_KEY is empty. Put your key in .env first.")
H = {"x-goog-api-key": KEY}


def red_png(size=32):
    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
    row = b"\x00" + b"\xff\x00\x00" * size
    raw = zlib.compress(row * size)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", raw) + chunk(b"IEND", b""))


if len(sys.argv) == 1:
    r = httpx.get(f"{BASE}/models", headers=H, params={"pageSize": 200}, timeout=30)
    print("HTTP", r.status_code)
    if r.status_code != 200:
        sys.exit(r.text[:500])
    for m in r.json().get("models", []):
        if "generateContent" in m.get("supportedGenerationMethods", []):
            print(m["name"].removeprefix("models/"))
else:
    model = sys.argv[1]
    body = {"contents": [{"parts": [
        {"text": "What color is this image? Answer in one word."},
        {"inline_data": {"mime_type": "image/png",
                         "data": base64.b64encode(red_png()).decode()}}]}]}
    r = httpx.post(f"{BASE}/models/{model}:generateContent", headers=H, json=body, timeout=60)
    print("HTTP", r.status_code)
    print(r.text[:800])
