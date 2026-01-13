from pathlib import Path
import os, re, sys

print("=== clean_for_pdf.py START ===", flush=True)
print("CWD:", os.getcwd(), flush=True)
print("Files in CWD:", [p.name for p in Path(".").iterdir()], flush=True)

src_path = Path("cv.md")
print("cv.md exists?", src_path.exists(), flush=True)
if not src_path.exists():
    raise FileNotFoundError(f"cv.md not found in {Path.cwd()}")

text = src_path.read_text(encoding="utf-8")
print("cv.md length:", len(text), flush=True)

text = re.sub(r"[📍📧📞🔗📄]", "", text)
text = "\n".join(line.rstrip() for line in text.splitlines()).strip() + "\n"

out_path = Path("cv_pdf.md")
out_path.write_text(text, encoding="utf-8")

print("Wrote:", out_path.resolve(), flush=True)
print("Output exists after write?", out_path.exists(), flush=True)
print("Output size:", out_path.stat().st_size if out_path.exists() else -1, flush=True)
print("=== clean_for_pdf.py END ===", flush=True)
