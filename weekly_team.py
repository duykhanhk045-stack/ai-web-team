import os, json, re
from openai import OpenAI

# Thử lần lượt từ trên xuống; bên nào lỗi/hết quota thì chuyển bên tiếp theo
PROVIDERS = [
    ("https://generativelanguage.googleapis.com/v1beta/openai/", "GEMINI_API_KEY", "gemini-2.5-flash"),
    ("https://api.groq.com/openai/v1", "GROQ_API_KEY", "openai/gpt-oss-120b"),
]

def ask(system, prompt):
    for base_url, key_env, model in PROVIDERS:
        key = os.environ.get(key_env)
        if not key:
            continue
        try:
            print(f"Đang gọi {model}...", flush=True)
            client = OpenAI(base_url=base_url, api_key=key, timeout=60, max_retries=0)
            r = client.chat.completions.create(
                model=model,
                max_tokens=3000,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            )
            print(f"[OK] dùng {model}")
            return r.choices[0].message.content
        except Exception as e:
            print(f"[LỖI] {model}: {e}")
    raise RuntimeError("Tất cả provider đều lỗi hoặc hết quota")

ROLES = {
    "frontend": "Bạn là dev frontend. Đề xuất thay đổi cụ thể kèm code.",
    "backend": "Bạn là dev backend. Đề xuất thay đổi cụ thể kèm code.",
    "seo": "Bạn là chuyên gia SEO và nội dung website.",
    "qa": "Bạn là QA. Review kỹ và chỉ ra lỗi hoặc rủi ro.",
}

def extract_json(text):
    m = re.search(r"\{.*\}", text, re.DOTALL)
    return json.loads(m.group(0)) if m else {}

def weekly_run(backlog):
    plan_text = ask(
        'Bạn là tech lead. CHỈ trả về JSON dạng {"frontend": ["việc 1"], "seo": ["việc 2"]}, không giải thích.',
        f"Backlog tuần này:\n{backlog}\nCác vai trò có thể giao: {list(ROLES)}",
    )
    tasks = extract_json(plan_text)

    results = {}
    for role, task_list in tasks.items():
        if role in ROLES:
            results[role] = ask(ROLES[role], "\n".join(task_list))

    review = ask(
        ROLES["qa"],
        "Review kết quả của team:\n" + json.dumps(results, ensure_ascii=False),
    )

    report = "# Báo cáo tuần\n\n## Kế hoạch\n" + json.dumps(tasks, ensure_ascii=False, indent=2)
    for role, out in results.items():
        report += f"\n\n## {role}\n{out}"
    report += f"\n\n## QA review\n{review}"
    return report

if __name__ == "__main__":
    with open("backlog.md", encoding="utf-8") as f:
        backlog = f.read()
    with open("weekly_report.md", "w", encoding="utf-8") as f:
        f.write(weekly_run(backlog))
    print("Đã tạo weekly_report.md")
