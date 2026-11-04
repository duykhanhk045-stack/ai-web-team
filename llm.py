import os
from openai import OpenAI

PROVIDERS = [
    ("https://generativelanguage.googleapis.com/v1beta/openai/", "GEMINI_API_KEY", "gemini-2.5-flash"),
    ("https://api.groq.com/openai/v1", "GROQ_API_KEY", "openai/gpt-oss-120b"),
]

def ask(system, prompt, max_tokens=6000):
    for base_url, key_env, model in PROVIDERS:
        key = os.environ.get(key_env)
        if not key:
            continue
        try:
            print(f"Đang gọi {model}...", flush=True)
            client = OpenAI(base_url=base_url, api_key=key, timeout=120, max_retries=0)
            r = client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            )
            print(f"[OK] dùng {model}", flush=True)
            return r.choices[0].message.content
        except Exception as e:
            print(f"[LỖI] {model}: {e}", flush=True)
    raise RuntimeError("Tất cả provider đều lỗi hoặc hết quota")
