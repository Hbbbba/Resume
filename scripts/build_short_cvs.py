#!/usr/bin/env python3
"""Build curated bilingual internship resumes from the authoritative CV content."""
from pathlib import Path
from html import escape
import yaml
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
DATA = yaml.safe_load((ROOT / 'content.yml').read_text(encoding='utf-8'))
chinese_font = next(p for p in [Path('C:/Windows/Fonts/simsun.ttc'),
                               Path('/usr/share/fonts/truetype/arphic/uming.ttc')] if p.exists())
pdfmetrics.registerFont(TTFont('Chinese', str(chinese_font), subfontIndex=0))
pdfmetrics.registerFontFamily('Chinese', normal='Chinese', bold='Chinese', italic='Chinese', boldItalic='Chinese')

# Short versions deliberately omit references, full funding lists, and older awards.
# Do not strengthen contribution verbs beyond the evidence in content.yml.
COMPACT = [
    ('Contribute to Net-JEPA, a 4M-parameter self-supervised network world model for adaptive bitrate streaming and congestion control, combining latent prediction, linear readouts, and model predictive control.',
     '参与 Net-JEPA 研究：约 400 万参数的自监督网络世界模型，结合潜在动态预测、线性读出与模型预测控制，支持自适应码率流媒体与拥塞控制。'),
    ('Framework evaluation: pretraining on 450,000+ Puffer streams; frozen-model transfer to congestion control with 20 calibration traces achieved capacity forecast MSLE of 0.84 vs. 1.93 for random initialization in fluid-queue emulation.',
     '框架评估：使用逾 45 万条 Puffer 流记录预训练；冻结模型后用 20 条轨迹校准读出，在流体队列仿真中容量预测 MSLE 为 0.84，随机初始化基线为 1.93。'),
    ('Co-authored a satellite-link prediction framework combining geometry and telemetry (HotMobile 2026). Real-Starlink evaluation reported throughput/latency MAE of 8.37 Mbps/14.25 ms vs. 29.54 Mbps/26.31 ms for a self-similar baseline.',
     '合作提出融合卫星几何信息与遥测的链路预测框架（HotMobile 2026）。真实 Starlink 评估中吞吐量/时延 MAE 为 8.37 Mbps/14.25 ms，自相似基线为 29.54 Mbps/26.31 ms。'),
    ('Co-authored prediction-driven video transmission and reconstruction over LEO links (INFOCOM 2026 Poster); developed WebRTC video-quality measurement, Raspberry Pi multipath relays, and an Android latency/packet-loss measurement app.',
     '合作提出面向低轨卫星的视频传输与重建设计（INFOCOM 2026 海报）；开发 WebRTC 视频质量测量系统、Raspberry Pi 多路径中继及 Android 时延与丢包测量应用。'),
]

def value(v, lang):
    return v.get(lang, v.get('en', '')) if isinstance(v, dict) else str(v)

def build(lang, pages):
    zh = lang == 'zh'
    font, bold = ('Chinese', 'Chinese') if zh else ('Times-Roman', 'Times-Bold')
    size = 10.2 if pages == 1 else 11
    normal = ParagraphStyle('body', fontName=font, fontSize=size, leading=size * 1.22,
                            spaceAfter=3 if pages == 1 else 5, wordWrap='CJK' if zh else None)
    title = ParagraphStyle('name', parent=normal, fontName=bold, fontSize=23, leading=27, alignment=TA_CENTER)
    contact = ParagraphStyle('contact', parent=normal, fontSize=9.5, leading=12, alignment=TA_CENTER)
    section = ParagraphStyle('section', parent=normal, fontName=bold, fontSize=11.5, leading=15,
                             spaceBefore=7, spaceAfter=5, borderWidth=0.4,
                             borderColor=colors.HexColor('#bcc7d3'), borderPadding=3,
                             backColor=colors.HexColor('#f1f4f7'), keepWithNext=True)
    heading = ParagraphStyle('heading', parent=normal, fontName=bold, keepWithNext=True)
    bullet = ParagraphStyle('bullet', parent=normal, leftIndent=9, firstLineIndent=-7)
    story = []
    def p(text, style=normal):
        return Paragraph(text, style)
    def text(s):
        return escape(value(s, lang)).replace('–', '-').replace('—', '-')
    def sec(en, cn):
        story.append(p(cn if zh else en.upper(), section))
    def bullets(items):
        story.extend(p('- ' + text(s), bullet) for s in items)
    def job(index, details=None):
        e = DATA['experience'][index]
        story.append(p(text(e['organization']), heading))
        story.append(p(text(e['role']) + ' | ' + text(e['period'])))
        bullets(e['details'] if details is None else details)
    profile = DATA['profile'][lang]
    story.append(p(text(profile['name']), title))
    story.append(p('网络系统与机器学习 | 南加州大学博士研究生' if zh else
                   'Networked Systems &amp; Machine Learning | Ph.D. Student, USC', contact))
    story.append(p('Los Angeles, CA | +1 6124563527 | <link href="mailto:hubin@usc.edu">hubin@usc.edu</link>'
                   ' | <link href="https://Hbbbba.github.io/Resume/">Hbbbba.github.io/Resume</link>', contact))
    sec('Education', '教育经历')
    for index in [0, 2, 4]:
        e = DATA['education'][index]
        story.append(p(text(e['institution']), heading))
        story.append(p(text(e['degree']) + ' | ' + text(e['period'])))
        if index == 0:
            story.append(p('导师：钱风教授。预计毕业：05/2028。' if zh else 'Advisor: Prof. Feng Qian. Expected graduation: 05/2028.'))
            story.append(p('明尼苏达大学计算机科学与工程博士阶段学习，2022.08-2023.08；随导师转至 USC。' if zh else
                           'Prior doctoral studies: University of Minnesota, CSE, Aug. 2022-Aug. 2023; transferred with advisor.'))
    sec('Technical Skills', '技术技能')
    story.append(p(('编程：' if zh else '<b>Programming:</b> ') + 'Python, C/C++, Java, MATLAB.'))
    story.append(p(('工具与平台：' if zh else '<b>Tools &amp; platforms:</b> ') +
                   ('PyTorch、Linux、WebRTC、Android 网络测量、数据包捕获与分析、GNURadio、SDR。' if zh else
                    'PyTorch, Linux, WebRTC, Android network measurement, packet capture/analysis, GNURadio, SDR.')))
    sec('Research & Engineering Experience', '科研与工程经历')
    job(0, [s[1 if zh else 0] for s in COMPACT] if pages == 1 else DATA['experience'][0]['details'])
    if pages == 2:
        story.append(PageBreak())
        sec('Research Experience (continued)', '科研经历（续）')
        # Preserve the source's separate appointments and dates.
        job(1)
        job(2)
        job(3)
        job(4)
    else:
        story.append(p('SUTD | Research Assistant | May 2021-Apr. 2022; Jul. 2021' if not zh else
                       '新加坡科技设计大学 | 研究助理 | 2021.05-2022.04；2021.07', heading))
        bullets([('Developed interpretable ML models for modulation classification and implemented an AI-based software modulator.',
                  '开发调制分类的可解释机器学习模型，并设计实现基于人工智能的软件调制器。')[zh]])
        story.append(p('Southeast University | Graduate Researcher | Sept. 2019-Oct. 2020; Jun. 2021' if not zh else
                       '东南大学 | 研究生科研人员 | 2019.09-2020.10；2021.06', heading))
        bullets([('Designed and evaluated a multidimensional LoRa demodulator and implemented a fine-grained self-correlation collision detector (ICNP 2020; WASA 2021).',
                  '设计评估 LoRa 多维解调器，实现细粒度自相关冲突检测器（ICNP 2020；WASA 2021）。')[zh]])
    sec('Selected Publications', '代表论文')
    selected = [1, 0, 3, 6] if pages == 1 else [1, 0, 3, 4, 6]
    venues = {0: 'IEEE INFOCOM Poster, 2026', 1: 'ACM HotMobile, 2026',
              3: 'USENIX NSDI, 2024', 4: 'ACM CoNEXT Companion, 2023', 6: 'IEEE ICNP, 2020'}
    for i in selected:
        pub = DATA['publications'][i]
        author = 'Bin Hu et al.' if pub['authors'][0] == 'Bin Hu' else 'Jiazhao Wang et al. (co-author: Bin Hu)'
        story.append(p(text(pub['title']) + '. <b>' + venues[i] + '.</b> ' + author))
    if pages == 2:
        sec('Industry Experience', '工业界经历')
        e = DATA['industry_experience'][0]
        story.append(p(text(e['organization']), heading))
        story.append(p(text(e['role']) + ' | ' + text(e['period'])))
        bullets(e['details'])
    sec('Selected Honors', '部分荣誉')
    awards = DATA['honors_awards']
    story.append(p('; '.join(text(awards[i]) for i in ([0] if pages == 1 else [0, 1, 2]))))
    out = ROOT / 'site' / f'cv_{lang}_{pages}page.pdf'
    def footer(canvas, doc):
        if pages == 2:
            canvas.setFont(font, 9)
            canvas.setFillColor(colors.HexColor('#657080'))
            canvas.drawString(39, 25, profile['name'])
            canvas.drawRightString(573, 25, f'{doc.page} / {pages}')
    doc = SimpleDocTemplate(str(out), pagesize=letter, rightMargin=39, leftMargin=39,
                            topMargin=31, bottomMargin=35, title=f'{profile["name"]} - {pages}-page resume',
                            author='Bin Hu')
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    actual = len(PdfReader(out).pages)
    if actual != pages:
        raise ValueError(f'{out.name}: expected {pages} pages, got {actual}; edit content or spacing.')
    print(f'{out}: {actual} page(s)')

if __name__ == '__main__':
    (ROOT / 'site').mkdir(exist_ok=True)
    for language in ['en', 'zh']:
        for count in [1, 2]:
            build(language, count)
