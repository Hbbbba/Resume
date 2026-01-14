#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from pathlib import Path
import html
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

DEFAULT_CSS = """
:root { --maxw: 900px; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
  margin: 0;
  padding: 0;
  background: #fff;
  color: #111;
}
.container {
  max-width: var(--maxw);
  margin: 42px auto;
  padding: 0 18px;
}
.header {
  text-align: center;
  margin-bottom: 18px;
}
.name { font-size: 40px; font-weight: 700; margin: 0; }
.meta { margin-top: 10px; font-size: 14px; line-height: 1.7; }
.meta a { color: inherit; text-decoration: underline; }
hr { border: 0; border-top: 1px solid #ddd; margin: 18px 0 22px; }
.section { margin: 20px 0 18px; }
.section h2 {
  font-size: 16px;
  letter-spacing: 0.02em;
  margin: 0 0 10px;
  text-transform: uppercase;
}
.item { margin: 10px 0 14px; }
.item .row { display: flex; justify-content: space-between; gap: 12px; align-items: baseline; }
.item .title { font-weight: 700; }
.item .period { white-space: nowrap; font-size: 13px; color: #333; }
.item .sub { margin-top: 2px; font-size: 14px; }
.item ul { margin: 6px 0 0 18px; padding: 0; }
.item li { margin: 3px 0; }
.small { font-size: 13px; color: #333; }
"""

def h(s: str) -> str:
    return html.escape(s, quote=True)

def join_with_sep(items: list[str], sep: str = " | ") -> str:
    items = [x for x in items if x]
    return sep.join(items)

def render_header(data: dict) -> str:
    name = h(data.get("name", ""))
    location = h(data.get("location", ""))

    emails = data.get("email", []) or []
    phones = data.get("phone", []) or []
    links = data.get("links", {}) or {}

    email_html = join_with_sep([f'<a href="mailto:{h(e)}">{h(e)}</a>' for e in emails])
    phone_html = join_with_sep([h(p) for p in phones])

    website = links.get("website", "")
    pdf = links.get("pdf", "")

    link_html_parts = []
    if website:
        link_html_parts.append(f'Website: <a href="{h(website)}">{h(website)}</a>')
    if pdf:
        link_html_parts.append(f'PDF: <a href="{h(pdf)}">Download CV (PDF)</a>')
    links_html = "<br/>".join(link_html_parts)

    lines = []
    if location:
        lines.append(location)
    if email_html:
        lines.append(email_html)
    if phone_html:
        lines.append(phone_html)
    if links_html:
        lines.append(links_html)

    meta = "<br/>".join(lines)

    return f"""
    <div class="header">
      <h1 class="name">{name}</h1>
      <div class="meta">{meta}</div>
    </div>
    """

def render_education(data: dict) -> str:
    items = data.get("education", []) or []
    if not items:
        return ""

    out = ['<div class="section"><h2>Education</h2>']
    for ed in items:
        inst = h(ed.get("institution", ""))
        loc = h(ed.get("location", ""))
        degree = h(ed.get("degree", ""))
        dept = h(ed.get("department", ""))
        period = h(ed.get("period", ""))
        #gpa = h(ed.get("gpa", ""))
        area = h(ed.get("Research Area", ""))
        advisor = h(ed.get("Advisor", ""))

        out.append('<div class="item">')
        out.append(f'<div class="row"><div class="title">{inst}</div><div class="period">{period}</div></div>')
        subparts = []
        if degree:
            subparts.append(f"<div><b>{degree}</b></div>")
        if dept:
            subparts.append(f"<div>{dept}</div>")
        if loc:
            subparts.append(f'<div class="small">{loc}</div>')
        #if gpa:
        #    subparts.append(f'<div class="small">GPA: {gpa}</div>')
        # if advisor:
        #     subparts.append(f"<div><b>Advisor:</b> {advisor}</div>")

        if subparts:
            out.append(f'<div class="sub">{"".join(subparts)}</div>')

        if area:
            out.append(f"<div><b>Research Area:</b> {area}</div>")
        if advisor:
            out.append(f"<div><b>Advisor:</b> {advisor}</div>")

        # if project_title:
        #     out.append("<div class='sub'><b>Project:</b> " + project_title + "</div>")

        out.append("</div>")
    out.append("</div>")
    return "\n".join(out)

def render_publications(data: dict) -> str:
    pubs = data.get("publications", []) or []
    if not pubs:
        return ""

    out = ['<div class="section"><h2>Publications</h2>']
    out.append("<ol>")
    for p in pubs:
        title = h(p.get("title", ""))
        authors = p.get("authors", []) or []
        authors_html = ", ".join(h(a) for a in authors)

        venue = h(p.get("venue", ""))
        year = p.get("year", "")
        note = h(p.get("note", "")) if p.get("note", "") else ""
        vol = h(p.get("volume", "")) if p.get("volume", "") else ""
        pages = h(p.get("pages", "")) if p.get("pages", "") else ""
        doi = h(p.get("doi", "")) if p.get("doi", "") else ""

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
        extra = []
        if doi:
            extra.append(f'DOI: <a href="https://doi.org/{doi}">{doi}</a>')

        out.append("<li>")
        out.append(f"<div><b>{title}</b></div>")
        out.append(f"<div class='small'>{authors_html}</div>")
        if meta:
            out.append(f"<div class='small'><b>{meta}</b></div>")
        if extra:
            out.append(f"<div class='small'>{' '.join(extra)}</div>")
        out.append("</li>")
    out.append("</ol></div>")
    return "\n".join(out)

def render_experience(data: dict) -> str:
    exp = data.get("experience", []) or []
    if not exp:
        return ""

    out = ['<div class="section"><h2>Research &amp; Experience</h2>']
    for e in exp:
        org = h(e.get("organization", ""))
        role = h(e.get("role", ""))
        period = h(e.get("period", ""))
        details = e.get("details", []) or []

        out.append('<div class="item">')
        out.append(f'<div class="row"><div class="title">{org}</div><div class="period">{period}</div></div>')
        if role:
            out.append(f'<div class="sub"><b>{role}</b></div>')
        if details:
            out.append("<ul>")
            for d in details:
                out.append(f"<li>{h(d)}</li>")
            out.append("</ul>")
        out.append("</div>")
    out.append("</div>")
    return "\n".join(out)

def render_list_section(title: str, items: list[str]) -> str:
    if not items:
        return ""
    out = [f'<div class="section"><h2>{h(title)}</h2><ul>']
    for it in items:
        out.append(f"<li>{h(it)}</li>")
    out.append("</ul></div>")
    return "\n".join(out)

def render_industry(data: dict) -> str:
    inds = data.get("industry_experience", []) or []
    if not inds:
        return ""

    out = ['<div class="section"><h2>Industry Experience</h2>']
    for e in inds:
        org = h(e.get("organization", ""))
        role = h(e.get("role", ""))
        period = h(e.get("period", ""))
        details = e.get("details", []) or []
        out.append('<div class="item">')
        out.append(f'<div class="row"><div class="title">{org}</div><div class="period">{period}</div></div>')
        if role:
            out.append(f'<div class="sub"><b>{role}</b></div>')
        if details:
            out.append("<ul>")
            for d in details:
                out.append(f"<li>{h(d)}</li>")
            out.append("</ul>")
        out.append("</div>")
    out.append("</div>")
    return "\n".join(out)

def render_funded_projects(data: dict) -> str:
    fps = data.get("funded_projects", []) or []
    if not fps:
        return ""

    out = ['<div class="section"><h2>Funded Projects</h2><ul>']
    for fp in fps:
        sponsor = h(fp.get("sponsor", ""))
        title = h(fp.get("title", ""))
        projects = fp.get("projects", []) or []
        if title:
            out.append(f"<li><b>{sponsor}</b> — {title}</li>")
        else:
            # sponsor with sub-project list
            out.append(f"<li><b>{sponsor}</b>")
            if projects:
                out.append("<ul>")
                for p in projects:
                    out.append(f"<li>{h(p)}</li>")
                out.append("</ul>")
            out.append("</li>")
    out.append("</ul></div>")
    return "\n".join(out)

def render_skills(data: dict) -> str:
    skills = data.get("skills", {}) or {}
    if not skills:
        return ""

    out = ['<div class="section"><h2>Skills</h2>']
    for k, arr in skills.items():
        title = k.replace("_", " ").title()
        vals = arr or []
        if not vals:
            continue
        out.append(f"<div class='item'><div class='title'>{h(title)}</div>")
        out.append("<ul>")
        for v in vals:
            out.append(f"<li>{h(v)}</li>")
        out.append("</ul></div>")
    out.append("</div>")
    return "\n".join(out)

def render_references(data: dict) -> str:
    refs = data.get("references", []) or []
    if not refs:
        return ""

    out = ['<div class="section"><h2>References</h2>']
    for r in refs:
        name = h(r.get("name", ""))
        title = h(r.get("title", ""))
        aff = h(r.get("affiliation", ""))
        email = h(r.get("email", ""))
        out.append("<div class='item'>")
        out.append(f"<div class='title'>{name}</div>")
        sub = " — ".join([x for x in [title, aff] if x])
        if sub:
            out.append(f"<div class='small'>{sub}</div>")
        if email:
            out.append(f"<div class='small'>Email: <a href='mailto:{email}'>{email}</a></div>")
        out.append("</div>")
    out.append("</div>")
    return "\n".join(out)

def main() -> None:
    data = yaml.safe_load(CONTENT.read_text(encoding="utf-8"))

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    body_parts = [
        render_header(data),
        "<hr/>",
        render_education(data),
        render_publications(data),
        render_experience(data),
        render_funded_projects(data),
        render_industry(data),
        render_list_section("Honors & Awards", data.get("honors_awards", []) or []),
        #render_skills(data),
        render_references(data),
    ]
    body = "\n".join([p for p in body_parts if p])

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{h(data.get("name","Resume"))} | Resume</title>
  <style>{DEFAULT_CSS}</style>
</head>
<body>
  <div class="container">
    {body}
  </div>
</body>
</html>
"""
    OUT_HTML.write_text(html_doc, encoding="utf-8")
    print(f"Wrote {OUT_HTML}")

if __name__ == "__main__":
    main()
