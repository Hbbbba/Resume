#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from pathlib import Path
import subprocess
import sys
import re

try:
    import yaml  # type: ignore
except Exception:
    print("Missing dependency: PyYAML. Install with: pip install pyyaml", file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content.yml"
OUT_DIR = ROOT / "site"
BUILD_DIR = ROOT / "build_pdf"
TEX = BUILD_DIR / "cv.tex"
PDF = BUILD_DIR / "cv.pdf"
OUT_PDF = OUT_DIR / "cv.pdf"

def latex_escape(s: str) -> str:
    """
    Escape LaTeX special chars for normal text.
    """
    if s is None:
        return ""
    s = str(s)
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(repl.get(ch, ch) for ch in s)

def bold_my_name(author: str, my_name: str = "Bin Hu") -> str:
    a = latex_escape(author)
    if author.strip() == my_name:
        return r"\textbf{" + a + "}"
    return a

def section(title: str) -> str:
    return r"\section*{" + latex_escape(title).upper() + "}\n" + r"\vspace{-2pt}\hrule\vspace{8pt}" + "\n"

def itemize(lines: list[str]) -> str:
    if not lines:
        return ""
    out = [r"\begin{itemize}"]
    for x in lines:
        out.append(r"\item " + latex_escape(x))
    out.append(r"\end{itemize}")
    return "\n".join(out) + "\n"

def latex_doc(data: dict) -> str:
    name = latex_escape(data.get("name", ""))
    location = latex_escape(data.get("location", ""))

    emails = data.get("email", []) or []
    phones = data.get("phone", []) or []
    links = data.get("links", {}) or {}

    website = links.get("website", "")
    pdf_link = links.get("pdf", "")

    def href(url: str, text: str) -> str:
        if not url:
            return latex_escape(text)
        return r"\href{" + latex_escape(url) + "}{" + latex_escape(text) + "}"

    email_line = " / ".join([latex_escape(e) for e in emails if e])
    phone_line = " / ".join([latex_escape(p) for p in phones if p])

    link_parts = []
    if website:
        show = re.sub(r"^https?://", "", website)
        link_parts.append("Website: " + href(website, show))
    if pdf_link:
        link_parts.append("PDF: " + href(pdf_link, "Download CV (PDF)"))
    link_line = " \\quad ".join(link_parts)

    header_lines = []
    if location:
        header_lines.append(location)
    if email_line:
        header_lines.append(r"E-mail: " + email_line)
    if phone_line:
        header_lines.append(r"Tel: " + phone_line)
    if link_line:
        header_lines.append(link_line)

    header = "\n".join([r"\centerline{" + x + r"}" for x in header_lines])

    # ---- build body (same as before) ----
    edu = data.get("education", []) or []
    pubs = data.get("publications", []) or []
    exp = data.get("experience", []) or []
    funded = data.get("funded_projects", []) or []
    industry = data.get("industry_experience", []) or []
    honors = data.get("honors_awards", []) or []
    skills = data.get("skills", {}) or {}
    refs = data.get("references", []) or []

    parts: list[str] = []

    if edu:
        parts.append(section("Education"))
        for e in edu:
            inst = latex_escape(e.get("institution", ""))
            period = latex_escape(e.get("period", ""))
            degree = latex_escape(e.get("degree", ""))
            dept = latex_escape(e.get("department", ""))
            loc = latex_escape(e.get("location", ""))
            gpa = latex_escape(e.get("gpa", ""))
            area = latex_escape(e.get("Research Area", ""))
            advisor = latex_escape(e.get("Advisor", ""))

            # 第一行：学校 + 右侧时间
            parts.append(r"\textbf{" + inst + r"}" + (r"\hfill " + period if period else "") + r"\\[-0.5pt]")

            # 下面几行：用 \\[-2pt] 把行距压紧一点
            if degree:
                parts.append(r"\textbf{" + degree + r"}\\[-0.5pt]")
            if dept:
                parts.append(dept + r"\\[-0.5pt]")
            if loc:
                parts.append(loc + r"\\[-0.5pt]")
            #if gpa:
            #    parts.append(r"GPA: " + gpa + r"\\[-2pt]")
            if area:
                parts.append(r"\textbf{Research Area:} " + area + r"\\[-0.5pt]")
            if advisor:
                parts.append(r"\textbf{Advisor:} " + advisor + r"\\[+10pt]")

            # 原来是 \vspace{4pt}，这里改小（或者直接删掉这一行）
            #parts.append(r"\vspace{12pt}")

    if pubs:
        parts.append(section("Publications"))
        parts.append(r"\begin{enumerate}")
        for p in pubs:
            title = latex_escape(p.get("title", ""))
            authors = p.get("authors", []) or []
            venue = latex_escape(p.get("venue", ""))
            year = p.get("year", "")
            note = latex_escape(p.get("note", "")) if p.get("note", "") else ""
            volume = latex_escape(p.get("volume", "")) if p.get("volume", "") else ""
            pages = latex_escape(p.get("pages", "")) if p.get("pages", "") else ""
            doi = latex_escape(p.get("doi", "")) if p.get("doi", "") else ""

            author_str = ", ".join([bold_my_name(a, "Bin Hu") for a in authors])

            meta_bits = []
            if venue:
                meta_bits.append(venue)
            if year:
                meta_bits.append(str(year))
            if volume:
                meta_bits.append("Volume " + volume)
            if pages:
                meta_bits.append(pages)
            if note:
                meta_bits.append(note)

            meta = ", ".join(meta_bits)

            parts.append(r"\item " + r"\textbf{" + title + r"}\\")
            if author_str:
                parts.append(author_str + r"\\")
            if meta:
                parts.append(r"\textbf{" + meta + r"}\\")
            if doi:
                parts.append(r"DOI: " + href("https://doi.org/" + doi, doi) + r"\\")
            parts.append(r"\vspace{2pt}")
        parts.append(r"\end{enumerate}")

    if exp:
        parts.append(section("Research & Experience"))
        for e in exp:
            org = latex_escape(e.get("organization", ""))
            role = latex_escape(e.get("role", ""))
            period = latex_escape(e.get("period", ""))
            details = e.get("details", []) or []
            parts.append(r"\textbf{" + org + r"}" + (r"\hfill " + period if period else "") + r"\\")
            if role:
                parts.append(r"\textbf{" + role + r"}\\")
            if details:
                parts.append(itemize(details))
            parts.append(r"\vspace{4pt}")

    if funded:
        parts.append(section("Funded Projects"))
        items = []
        for fp in funded:
            sponsor = fp.get("sponsor", "")
            title = fp.get("title", "")
            projects = fp.get("projects", []) or []
            if title:
                items.append(f"{sponsor} — {title}")
            else:
                if sponsor and projects:
                    items.append(f"{sponsor}: " + "; ".join(projects))
                elif sponsor:
                    items.append(str(sponsor))
        parts.append(itemize(items))

    if industry:
        parts.append(section("Industry Experience"))
        for e in industry:
            org = latex_escape(e.get("organization", ""))
            role = latex_escape(e.get("role", ""))
            period = latex_escape(e.get("period", ""))
            details = e.get("details", []) or []
            parts.append(r"\textbf{" + org + r"}" + (r"\hfill " + period if period else "") + r"\\")
            if role:
                parts.append(r"\textbf{" + role + r"}\\")
            if details:
                parts.append(itemize(details))
            parts.append(r"\vspace{4pt}")

    if honors:
        parts.append(section("Honors & Awards"))
        parts.append(itemize([str(x) for x in honors]))

    if skills:
        parts.append(section("Skills"))
        for k, arr in skills.items():
            title = latex_escape(k.replace("_", " ").title())
            vals = arr or []
            if not vals:
                continue
            parts.append(r"\textbf{" + title + r"}\\")
            parts.append(itemize([str(v) for v in vals]))
            parts.append(r"\vspace{2pt}")

    if refs:
        parts.append(section("References"))
        for r in refs:
            nm = latex_escape(r.get("name", ""))
            tt = latex_escape(r.get("title", ""))
            aff = latex_escape(r.get("affiliation", ""))
            em = latex_escape(r.get("email", ""))
            parts.append(r"\textbf{" + nm + r"}\\")
            line = " — ".join([x for x in [tt, aff] if x])
            if line:
                parts.append(line + r"\\")
            if em:
                parts.append(r"E-mail: " + href("mailto:" + em, em) + r"\\")
            parts.append(r"\vspace{6pt}")

    body = "\n".join(parts)

    # ===== IMPORTANT: NOT an f-string =====
    tex_template = r"""
\documentclass[10pt,letterpaper]{article}
\usepackage[margin=0.75in]{geometry}
\usepackage[hidelinks]{hyperref}

% ===== Font: Times New Roman (XeLaTeX) =====
\usepackage{fontspec}
\IfFontExistsTF{Times New Roman}{
  \setmainfont{Times New Roman}
}{
  \setmainfont{TeX Gyre Termes}
}

\setlength{\parindent}{0pt}
\setlength{\parskip}{3pt}

\makeatletter
\renewcommand\thesection{}
\renewcommand\section{\@startsection{section}{1}{0pt}%
  {-0.8ex}{0.6ex}{\normalfont\bfseries\MakeUppercase}}
\makeatother

% Compact lists
\usepackage{enumitem}
\setlist[itemize]{leftmargin=*, itemsep=1pt, topsep=2pt}
\setlist[enumerate]{leftmargin=*, itemsep=2pt, topsep=2pt}

\begin{document}

\begin{center}
{\LARGE\bfseries __NAME__}\par
\vspace{4pt}
__HEADER__
\end{center}

\vspace{10pt}

__BODY__

\end{document}
""".strip() + "\n"

    return (
        tex_template
        .replace("__NAME__", name)
        .replace("__HEADER__", header)
        .replace("__BODY__", body)
    )


def run(cmd: list[str], cwd: Path) -> None:
    p = subprocess.run(cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(p.stdout)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")

def main() -> None:
    data = yaml.safe_load(CONTENT.read_text(encoding="utf-8"))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    TEX.write_text(latex_doc(data), encoding="utf-8")
    print(f"Wrote {TEX}")

    # Ensure xelatex exists
    try:
        subprocess.run(["xelatex", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception:
        print("xelatex not found. Install TeX Live XeLaTeX, e.g.: sudo apt-get install texlive-xetex", file=sys.stderr)
        sys.exit(2)

    # Compile twice for stable references
    run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", TEX.name], cwd=BUILD_DIR)
    run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", TEX.name], cwd=BUILD_DIR)

    if not PDF.exists():
        print(f"Expected PDF not found: {PDF}", file=sys.stderr)
        sys.exit(3)

    OUT_PDF.write_bytes(PDF.read_bytes())
    print(f"Wrote {OUT_PDF}")

if __name__ == "__main__":
    main()
