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

def latex_escape(s: str) -> str:
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

def pick_lang_value(v, lang: str):
    if isinstance(v, dict):
        return v.get(lang, v.get("en", ""))
    return v

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

def href(url: str, text: str) -> str:
    if not url:
        return latex_escape(text)
    return r"\href{" + latex_escape(url) + "}{" + latex_escape(text) + "}"

def latex_doc(data: dict, lang: str) -> str:
    labels = {
        "en": {
            "website": "Website",
            "pdf": "PDF",
            "download": "Download CV (PDF)",
            "email": "E-mail",
            "tel": "Tel",
            "education": "Education",
            "publications": "Publications",
            "experience": "Research & Experience",
            "funded_projects": "Funded Projects",
            "industry_experience": "Industry Experience",
            "honors_awards": "Honors & Awards",
            "references": "References",
            "research_area": "Research Area",
            "advisor": "Advisor",
        },
        "zh": {
            "website": "主页",
            "pdf": "PDF",
            "download": "下载简历（PDF）",
            "email": "邮箱",
            "tel": "电话",
            "education": "教育经历",
            "publications": "论文发表",
            "experience": "科研与经历",
            "funded_projects": "科研项目",
            "industry_experience": "工业界经历",
            "honors_awards": "荣誉奖项",
            "references": "推荐人",
            "research_area": "研究方向",
            "advisor": "导师",
        },
    }[lang]

    profile = data["profile"][lang]

    name = latex_escape(profile.get("name", ""))
    location = latex_escape(profile.get("location", ""))

    emails = profile.get("email", []) or []
    phones = profile.get("phone", []) or []
    links = profile.get("links", {}) or {}

    website = links.get("website", "")
    pdf_link = links.get("pdf", "")

    email_line = " / ".join([latex_escape(e) for e in emails if e])
    phone_line = " / ".join([latex_escape(p) for p in phones if p])

    link_parts = []
    if website:
        show = re.sub(r"^https?://", "", website)
        link_parts.append(labels["website"] + ": " + href(website, show))
    if pdf_link:
        link_parts.append(labels["pdf"] + ": " + href(pdf_link, labels["download"]))
    link_line = " \\quad ".join(link_parts)

    header_lines = []
    if location:
        header_lines.append(location)
    if email_line:
        header_lines.append(labels["email"] + ": " + email_line)
    if phone_line:
        header_lines.append(labels["tel"] + ": " + phone_line)
    if link_line:
        header_lines.append(link_line)

    header = "\n".join([r"\centerline{" + x + r"}" for x in header_lines])

    parts = []

    edu = data.get("education", []) or []
    if edu:
        parts.append(section(labels["education"]))
        for e in edu:
            inst = latex_escape(pick_lang_value(e.get("institution", ""), lang))
            period = latex_escape(pick_lang_value(e.get("period", ""), lang))
            degree = latex_escape(pick_lang_value(e.get("degree", ""), lang))
            dept = latex_escape(pick_lang_value(e.get("department", ""), lang))
            loc = latex_escape(pick_lang_value(e.get("location", ""), lang))
            area = latex_escape(pick_lang_value(e.get("research_area", ""), lang))
            advisor = latex_escape(pick_lang_value(e.get("advisor", ""), lang))

            parts.append(r"\textbf{" + inst + r"}" + (r"\hfill " + period if period else "") + r"\\[-0.5pt]")
            if degree:
                parts.append(r"\textbf{" + degree + r"}\\[-0.5pt]")
            if dept:
                parts.append(dept + r"\\[-0.5pt]")
            if loc:
                parts.append(loc + r"\\[-0.5pt]")
            if area:
                parts.append(r"\textbf{" + latex_escape(labels["research_area"]) + r":} " + area + r"\\[-0.5pt]")
            if advisor:
                parts.append(r"\textbf{" + latex_escape(labels["advisor"]) + r":} " + advisor + r"\\[+10pt]")

    pubs = data.get("publications", []) or []
    if pubs:
        parts.append(section(labels["publications"]))
        parts.append(r"\begin{enumerate}")
        for p in pubs:
            title = latex_escape(pick_lang_value(p.get("title", ""), lang))
            authors = p.get("authors", []) or []
            venue = latex_escape(pick_lang_value(p.get("venue", ""), lang))
            year = p.get("year", "")
            note = latex_escape(pick_lang_value(p.get("note", ""), lang)) if p.get("note") else ""
            volume = latex_escape(str(p.get("volume", ""))) if p.get("volume") else ""
            pages = latex_escape(str(p.get("pages", ""))) if p.get("pages") else ""
            doi = latex_escape(str(p.get("doi", ""))) if p.get("doi") else ""

            author_str = ", ".join([
                bold_my_name(pick_lang_value(a, lang), "Bin Hu") for a in authors
            ])

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

    exp = data.get("experience", []) or []
    if exp:
        parts.append(section(labels["experience"]))
        for e in exp:
            org = latex_escape(pick_lang_value(e.get("organization", ""), lang))
            role = latex_escape(pick_lang_value(e.get("role", ""), lang))
            period = latex_escape(pick_lang_value(e.get("period", ""), lang))
            details = e.get("details", []) or []
            parts.append(r"\textbf{" + org + r"}" + (r"\hfill " + period if period else "") + r"\\")
            if role:
                parts.append(r"\textbf{" + role + r"}\\")
            if details:
                parts.append(itemize([pick_lang_value(x, lang) for x in details]))
            parts.append(r"\vspace{4pt}")

    funded = data.get("funded_projects", []) or []
    if funded:
        parts.append(section(labels["funded_projects"]))
        items = []
        for fp in funded:
            sponsor = pick_lang_value(fp.get("sponsor", ""), lang)
            title = pick_lang_value(fp.get("title", ""), lang)
            projects = fp.get("projects", []) or []
            if title:
                items.append(f"{sponsor} — {title}")
            else:
                if sponsor and projects:
                    items.append(f"{sponsor}: " + "; ".join(pick_lang_value(x, lang) for x in projects))
                elif sponsor:
                    items.append(str(sponsor))
        parts.append(itemize(items))

    industry = data.get("industry_experience", []) or []
    if industry:
        parts.append(section(labels["industry_experience"]))
        for e in industry:
            org = latex_escape(pick_lang_value(e.get("organization", ""), lang))
            role = latex_escape(pick_lang_value(e.get("role", ""), lang))
            period = latex_escape(pick_lang_value(e.get("period", ""), lang))
            details = e.get("details", []) or []
            parts.append(r"\textbf{" + org + r"}" + (r"\hfill " + period if period else "") + r"\\")
            if role:
                parts.append(r"\textbf{" + role + r"}\\")
            if details:
                parts.append(itemize([pick_lang_value(x, lang) for x in details]))
            parts.append(r"\vspace{4pt}")

    honors = data.get("honors_awards", []) or []
    if honors:
        parts.append(section(labels["honors_awards"]))
        parts.append(itemize([pick_lang_value(x, lang) for x in honors]))

    refs = data.get("references", []) or []
    if refs:
        parts.append(section(labels["references"]))
        for r in refs:
            nm = latex_escape(pick_lang_value(r.get("name", ""), lang))
            tt = latex_escape(pick_lang_value(r.get("title", ""), lang))
            aff = latex_escape(pick_lang_value(r.get("affiliation", ""), lang))
            em = r.get("email", "")

            parts.append(r"\noindent\textbf{" + nm + r"}\par")
            if tt:
                parts.append(r"\noindent " + tt + r"\par")
            if aff:
                parts.append(r"\noindent " + aff + r"\par")
            if em:
                parts.append(
                    r"\noindent " + latex_escape(labels["email"]) + ": " + href("mailto:" + em, em) + r"\par"
                )

            parts.append(r"\addvspace{10pt}")
    body = "\n".join(parts)

    if lang == "zh":
        extra_font = r"""
\usepackage{xeCJK}
\IfFontExistsTF{Songti SC}{
  \setCJKmainfont{Songti SC}
}{
  \IfFontExistsTF{SimSun}{
    \setCJKmainfont{SimSun}
  }{
    \setCJKmainfont{Noto Serif CJK SC}
  }
}
"""
    else:
        extra_font = ""

    tex_template = r"""
\documentclass[10pt,letterpaper]{article}
\usepackage[margin=0.75in]{geometry}
\usepackage[hidelinks]{hyperref}
\usepackage{fontspec}
__EXTRA_FONT__
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
        .replace("__EXTRA_FONT__", extra_font)
        .replace("__NAME__", name)
        .replace("__HEADER__", header)
        .replace("__BODY__", body)
    )

def run(cmd: list[str], cwd: Path) -> None:
    p = subprocess.run(cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(p.stdout)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")

def build_one(data: dict, lang: str, out_name: str) -> None:
    tex_path = BUILD_DIR / f"cv_{lang}.tex"
    pdf_path = BUILD_DIR / f"cv_{lang}.pdf"
    out_pdf = OUT_DIR / out_name

    tex_path.write_text(latex_doc(data, lang), encoding="utf-8")
    print(f"Wrote {tex_path}")

    run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name], cwd=BUILD_DIR)
    run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name], cwd=BUILD_DIR)

    if not pdf_path.exists():
        print(f"Expected PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(3)

    out_pdf.write_bytes(pdf_path.read_bytes())
    print(f"Wrote {out_pdf}")

def main() -> None:
    data = yaml.safe_load(CONTENT.read_text(encoding="utf-8"))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(["xelatex", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception:
        print("xelatex not found. Install TeX Live XeLaTeX.", file=sys.stderr)
        sys.exit(2)

    build_one(data, "en", "cv_en.pdf")
    build_one(data, "zh", "cv_zh.pdf")

if __name__ == "__main__":
    main()