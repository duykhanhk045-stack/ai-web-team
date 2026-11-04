import os, re
from llm import ask

body = os.environ["ISSUE_BODY"]
num = os.environ["ISSUE_NUMBER"]

# Issue form có dạng: "### Nhãn" rồi đến giá trị; lấy giá trị theo thứ tự
vals = [v.strip() for v in re.split(r"^###\s+.*$", body, flags=re.M)[1:]]
vals += [""] * (4 - len(vals))
ten, mo_ta, trang, phong_cach = [("" if v == "_No response_" else v) for v in vals[:4]]

ten = re.sub(r"[^a-z0-9-]", "-", ten.lower()).strip("-") or f"web-{num}"

system = (
    "Bạn là lập trình viên web. Hãy tạo website tĩnh hoàn chỉnh bằng HTML và CSS, "
    "responsive (dùng tốt trên điện thoại), không dùng thư viện hay ảnh bên ngoài, "
    "nội dung tiếng Việt, tối đa 3 trang. Trả về MỖI file đúng định dạng:\n"
    "=== FILE: index.html ===\n<nội dung file>\n=== END ===\n"
    "Chỉ gồm các file .html và style.css. Trang nào cũng liên kết tới style.css "
    "và có menu dẫn tới các trang khác. Không giải thích gì thêm."
)
prompt = (
    f"Mô tả web: {mo_ta}\n"
    f"Các trang cần có: {trang or 'tự đề xuất'}\n"
    f"Phong cách: {phong_cach or 'tự chọn, hiện đại, dễ đọc'}"
)

out = ask(system, prompt)
files = re.findall(r"=== FILE: ([\w\-]+\.(?:html|css)) ===\n(.*?)\n=== END ===", out, re.S)
if not any(name == "index.html" for name, _ in files):
    raise RuntimeError("AI không trả về file index.html. Nội dung nhận được:\n" + out[:1500])

folder = f"sites/{ten}"
os.makedirs(folder, exist_ok=True)
for name, content in files:
    content = re.sub(r"^```\w*\n|\n```$", "", content.strip())
    with open(f"{folder}/{name}", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Đã ghi {folder}/{name}")
