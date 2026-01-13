from pathlib import Path
import re

src = Path("cv.md").read_text(encoding="utf-8").splitlines()

# Expect the top of cv.md like:
# # Bin Hu
# blank
# 📍 ...
# 📧 ...
# 📞 ...
# 🔗 Website: ...
# 📄 PDF: ...
#
# We will extract name + email line + tel line, then remove those header lines
# from the body for PDF, so PDF header is controlled by template.

name = None
email_line = ""
tel_line = ""

body_start = 0

# Find name
for i, line in enumerate(src):
    if line.strip().startswith("# "):
        name = line.strip()[2:].strip()
        body_start = i + 1
        break

if not name:
    raise RuntimeError("Cannot find '# Name' in cv.md")

# Collect the next few non-empty lines as header candidates
header_lines = []
i = body_start
while i < len(src) and len(header_lines) < 10:
    if src[i].strip() != "":
        header_lines.append(src[i].strip())
    i += 1

# Extract email(s)
for line in header_lines:
    if "mailto:" in line or "hubin@" in line or "E-mail" in line or "Email" in line or "📧" in line:
        # Remove emoji and leading label
        s = re.sub(r"[📧]", "", line).strip()
        s = re.sub(r"^E-?mail:\s*", "", s, flags=re.I)
        s = re.sub(r"^Email:\s*", "", s, flags=re.I)
        email_line = s
        break

# Extract phone(s)
for line in header_lines:
    if "📞" in line or "Tel" in line or "Phone" in line or "+1" in line or "+86" in line:
        s = re.sub(r"[📞]", "", line).strip()
        s = re.sub(r"^Tel:\s*", "", s, flags=re.I)
        s = re.sub(r"^Phone:\s*", "", s, flags=re.I)
        tel_line = s
        break

# Clean markdown link syntax for PDF header (keep clickable text as plain, template can keep link in body)
def mdlinks_to_text(s: str) -> str:
    # [text](url) -> text
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)

email_line = mdlinks_to_text(email_line)
tel_line = mdlinks_to_text(tel_line)

# Build YAML for PDF template to use
yaml = [
    "---",
    f"title: {name}",
    "pdf_email: \"" + email_line.replace('"', '\\"') + "\"",
    "pdf_tel: \"" + tel_line.replace('"', '\\"') + "\"",
    "---",
    "",
]

# Remove the original header block from body:
# We drop from '# Name' down to the first section header '## ...'
body = []
seen_first_section = False
for line in src:
    if line.strip().startswith("## "):
        seen_first_section = True
    if seen_first_section:
        body.append(line)

out = "\n".join(yaml + body).strip() + "\n"
Path("cv_pdf.md").write_text(out, encoding="utf-8")
print("Generated cv_pdf.md")
