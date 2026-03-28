#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from pathlib import Path
import html
import json
import sys

try:
    import yaml  # type: ignore
except Exception:
    print("Missing dependency: PyYAML. Install with: pip install pyyaml", file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content.yml"
OUT_DIR = ROOT / "site"
OUT_HTML = OUT_DIR / "index.html"
STYLE_CSS = ROOT / "style.css"

I18N = {
    "en": {
        "lang_label": "中文",
        "page_title_suffix": "Resume",
        "website_label": "Website",
        "pdf_label": "PDF",
        "download_pdf": "Download CV (PDF)",
        "email_label": "Email",
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
        "lang_label": "EN",
        "page_title_suffix": "简历",
        "website_label": "主页",
        "pdf_label": "PDF",
        "download_pdf": "下载简历（PDF）",
        "email_label": "邮箱",
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
}

def h(s: str) -> str:
    return html.escape("" if s is None else str(s), quote=True)

def load_css() -> str:
    if STYLE_CSS.exists():
        return STYLE_CSS.read_text(encoding="utf-8")
    return ""

def pick_lang_value(v, lang: str):
    if isinstance(v, dict):
        return v.get(lang, v.get("en", ""))
    return v

def build_header(profile: dict, lang: str) -> str:
    t = I18N[lang]

    name = h(profile.get("name", ""))
    location = h(profile.get("location", ""))

    emails = profile.get("email", []) or []
    phones = profile.get("phone", []) or []
    links = profile.get("links", {}) or {}

    email_html = " | ".join(
        f'<a href="mailto:{h(e)}">{h(e)}</a>' for e in emails if e
    )
    phone_html = " | ".join(h(p) for p in phones if p)

    website = links.get("website", "")
    pdf = links.get("pdf", "")

    link_html_parts = []
    if website:
        link_html_parts.append(
            f'{h(t["website_label"])}: <a href="{h(website)}">{h(website)}</a>'
        )
    if pdf:
        link_html_parts.append(
            f'{h(t["pdf_label"])}: <a id="cv-link" href="{h(pdf)}">{h(t["download_pdf"])}</a>'
        )

    lines = []
    if location:
        lines.append(location)
    if email_html:
        lines.append(email_html)
    if phone_html:
        lines.append(phone_html)
    if link_html_parts:
        lines.append("<br/>".join(link_html_parts))

    meta = "<br/>".join(lines)

    return f"""
    <div class="header">
      <h1 class="name">{name}</h1>
      <div class="meta">{meta}</div>
    </div>
    """

def build_education(items: list[dict], lang: str) -> str:
    t = I18N[lang]
    if not items:
        return ""

    out = [f'<div class="section"><h2>{h(t["education"])}</h2>']
    for ed in items:
        inst = h(pick_lang_value(ed.get("institution", ""), lang))
        loc = h(pick_lang_value(ed.get("location", ""), lang))
        degree = h(pick_lang_value(ed.get("degree", ""), lang))
        dept = h(pick_lang_value(ed.get("department", ""), lang))
        period = h(pick_lang_value(ed.get("period", ""), lang))
        area = h(pick_lang_value(ed.get("research_area", ""), lang))
        advisor = h(pick_lang_value(ed.get("advisor", ""), lang))

        out.append('<div class="item">')
        out.append(f'<div class="row"><div class="title">{inst}</div><div class="period">{period}</div></div>')

        subparts = []
        if degree:
            subparts.append(f"<div><b>{degree}</b></div>")
        if dept:
            subparts.append(f"<div>{dept}</div>")
        if loc:
            subparts.append(f'<div class="small">{loc}</div>')
        if subparts:
            out.append(f'<div class="sub">{"".join(subparts)}</div>')

        if area:
            out.append(f"<div><b>{h(t['research_area'])}:</b> {area}</div>")
        if advisor:
            out.append(f"<div><b>{h(t['advisor'])}:</b> {advisor}</div>")

        out.append("</div>")
    out.append("</div>")
    return "\n".join(out)

def build_publications(items: list[dict], lang: str) -> str:
    t = I18N[lang]
    if not items:
        return ""

    out = [f'<div class="section"><h2>{h(t["publications"])}</h2>', "<ol>"]
    for p in items:
        title = h(pick_lang_value(p.get("title", ""), lang))
        authors = p.get("authors", []) or []
        authors_html = ", ".join(h(pick_lang_value(a, lang)) for a in authors)

        venue = h(pick_lang_value(p.get("venue", ""), lang))
        year = p.get("year", "")
        note = h(pick_lang_value(p.get("note", ""), lang)) if p.get("note") else ""
        vol = h(str(p.get("volume", ""))) if p.get("volume") else ""
        pages = h(str(p.get("pages", ""))) if p.get("pages") else ""
        doi = h(str(p.get("doi", ""))) if p.get("doi") else ""

        tail = []
        if venue:
            tail.append(venue)
        if year:
            tail.append(str(year))
        if vol:
            tail.append(f"Vol. {vol}")
        if pages:
            tail.append(pages)
        if note:
            tail.append(note)

        meta = ", ".join(tail)

        out.append("<li>")
        out.append(f"<div><b>{title}</b></div>")
        if authors_html:
            out.append(f"<div class='small'>{authors_html}</div>")
        if meta:
            out.append(f"<div class='small'><b>{meta}</b></div>")
        if doi:
            out.append(f"<div class='small'>DOI: <a href='https://doi.org/{doi}'>{doi}</a></div>")
        out.append("</li>")

    out.append("</ol></div>")
    return "\n".join(out)

def build_exp_section(title_key: str, items: list[dict], lang: str) -> str:
    t = I18N[lang]
    if not items:
        return ""

    out = [f'<div class="section"><h2>{h(t[title_key])}</h2>']
    for e in items:
        org = h(pick_lang_value(e.get("organization", ""), lang))
        role = h(pick_lang_value(e.get("role", ""), lang))
        period = h(pick_lang_value(e.get("period", ""), lang))
        details = e.get("details", []) or []

        out.append('<div class="item">')
        out.append(f'<div class="row"><div class="title">{org}</div><div class="period">{period}</div></div>')
        if role:
            out.append(f'<div class="sub"><b>{role}</b></div>')
        if details:
            out.append("<ul>")
            for d in details:
                out.append(f"<li>{h(pick_lang_value(d, lang))}</li>")
            out.append("</ul>")
        out.append("</div>")
    out.append("</div>")
    return "\n".join(out)

def build_funded_projects(items: list[dict], lang: str) -> str:
    t = I18N[lang]
    if not items:
        return ""

    out = [f'<div class="section"><h2>{h(t["funded_projects"])}</h2><ul>']
    for fp in items:
        sponsor = h(pick_lang_value(fp.get("sponsor", ""), lang))
        title = h(pick_lang_value(fp.get("title", ""), lang))
        projects = fp.get("projects", []) or []
        if title:
            out.append(f"<li><b>{sponsor}</b> — {title}</li>")
        else:
            out.append(f"<li><b>{sponsor}</b>")
            if projects:
                out.append("<ul>")
                for p in projects:
                    out.append(f"<li>{h(pick_lang_value(p, lang))}</li>")
                out.append("</ul>")
            out.append("</li>")
    out.append("</ul></div>")
    return "\n".join(out)

def build_list_section(title_key: str, items: list, lang: str) -> str:
    t = I18N[lang]
    if not items:
        return ""
    out = [f'<div class="section"><h2>{h(t[title_key])}</h2><ul>']
    for it in items:
        out.append(f"<li>{h(pick_lang_value(it, lang))}</li>")
    out.append("</ul></div>")
    return "\n".join(out)

def build_references(items: list[dict], lang: str) -> str:
    t = I18N[lang]
    if not items:
        return ""
    out = [f'<div class="section"><h2>{h(t["references"])}</h2>']
    for r in items:
        name = h(pick_lang_value(r.get("name", ""), lang))
        title = h(pick_lang_value(r.get("title", ""), lang))
        aff = h(pick_lang_value(r.get("affiliation", ""), lang))
        email = h(r.get("email", ""))
        out.append("<div class='item'>")
        out.append(f"<div class='title'>{name}</div>")
        sub = " — ".join([x for x in [title, aff] if x])
        if sub:
            out.append(f"<div class='small'>{sub}</div>")
        if email:
            out.append(f"<div class='small'>{h(t['email_label'])}: <a href='mailto:{email}'>{email}</a></div>")
        out.append("</div>")
    out.append("</div>")
    return "\n".join(out)

def build_page(data: dict, lang: str) -> str:
    profile = data["profile"][lang]

    body_parts = [
        build_header(profile, lang),
        "<hr/>",
        build_education(data.get("education", []) or [], lang),
        build_publications(data.get("publications", []) or [], lang),
        build_exp_section("experience", data.get("experience", []) or [], lang),
        build_funded_projects(data.get("funded_projects", []) or [], lang),
        build_exp_section("industry_experience", data.get("industry_experience", []) or [], lang),
        build_list_section("honors_awards", data.get("honors_awards", []) or [], lang),
        build_references(data.get("references", []) or [], lang),
    ]
    return "\n".join([p for p in body_parts if p])

def main() -> None:
    data = yaml.safe_load(CONTENT.read_text(encoding="utf-8"))
    css = load_css()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pages = {
        "en": build_page(data, "en"),
        "zh": build_page(data, "zh"),
    }

    profile_en = data["profile"]["en"]
    profile_zh = data["profile"]["zh"]

    page_title_en = f'{profile_en.get("name", "Resume")} | {I18N["en"]["page_title_suffix"]}'
    page_title_zh = f'{profile_zh.get("name", "简历")} | {I18N["zh"]["page_title_suffix"]}'

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{h(page_title_en)}</title>
  <style>{css}</style>
  <style>
    .topbar {{
      display: flex;
      justify-content: flex-end;
      margin-bottom: 16px;
    }}
    .lang-switch {{
      display: inline-flex;
      border: 1px solid #ddd;
      border-radius: 999px;
      overflow: hidden;
    }}
    .lang-switch button {{
      border: 0;
      background: white;
      padding: 8px 14px;
      cursor: pointer;
      font-size: 14px;
    }}
    .lang-switch button.active {{
      background: #111;
      color: #fff;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="topbar">
      <div class="lang-switch">
        <button id="btn-en" onclick="setLanguage('en')">EN</button>
        <button id="btn-zh" onclick="setLanguage('zh')">中文</button>
      </div>
    </div>

    <div id="page-content"></div>
  </div>

  <script>
    const pages = {json.dumps(pages, ensure_ascii=False)};
    const titles = {{
      en: {json.dumps(page_title_en, ensure_ascii=False)},
      zh: {json.dumps(page_title_zh, ensure_ascii=False)}
    }};

    function setLanguage(lang) {{
      document.documentElement.lang = lang;
      document.title = titles[lang];
      document.getElementById("page-content").innerHTML = pages[lang];

      document.getElementById("btn-en").classList.toggle("active", lang === "en");
      document.getElementById("btn-zh").classList.toggle("active", lang === "zh");

      localStorage.setItem("language", lang);
    }}

    setLanguage(localStorage.getItem("language") || "en");
  </script>
</body>
</html>
"""
    OUT_HTML.write_text(html_doc, encoding="utf-8")
    print(f"Wrote {OUT_HTML}")

if __name__ == "__main__":
    main()