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
# SWE implementation details also reflect the user's project-specific confirmations.
SWE_PROJECTS = [
    ('NIER / Android neural video', 'NIER / Android 神经视频',
     'Contributed to rebuilding NIER\'s neural video-conferencing model for Android phones.',
     '参与面向 Android 手机的 NIER 神经视频会议模型重新构建工作。'),
    ('WebRTC video measurement', 'WebRTC 视频测量',
     'Developed a WebRTC-based system to record real-time video-call quality over satellite networks; used Docker in the project.',
     '开发基于 WebRTC 的卫星网络实时视频通话质量测量系统，并在项目中使用 Docker。'),
    ('Multipath networking / Raspberry Pi', '多路径网络 / Raspberry Pi',
     'Built client, server, and proxy components for a Raspberry Pi multipath system; increased throughput by 50-80% and reduced packet-loss rate to about one-tenth of a single satellite connection.',
     '构建 Raspberry Pi 多路径系统的客户端、服务端与代理组件；相比单条卫星连接，吞吐量提高 50%-80%，丢包率降至约十分之一。'),
    ('Android network measurement', 'Android 网络测量',
     'Contributed to Android client development for network experiments measuring latency and packet loss; used Python, C++, and Java across these systems projects.',
     '参与测量时延与丢包率的 Android 实验客户端开发；在上述系统项目中使用 Python、C++ 与 Java。'),
    ('Data pipelines & PyTorch prediction', '数据处理与 PyTorch 预测',
     'Collected and synchronized network measurements and satellite information, preprocessed training data, and built PyTorch models for network and satellite prediction.',
     '采集并同步网络测量数据与卫星信息，预处理训练数据，使用 PyTorch 构建网络与卫星预测模型。'),
    ('Self-supervised network modeling', '自监督网络建模',
     'Contribute to Net-JEPA, a 4M-parameter world model for adaptive streaming and congestion control; framework evaluation uses 450,000+ Puffer streams and 20-trace transfer calibration.',
     '参与 Net-JEPA 研究：约 400 万参数的世界模型，用于自适应流媒体与拥塞控制；框架评估使用逾 45 万条 Puffer 流记录及 20 条迁移校准轨迹。'),
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
    subtitle = ('系统软件与网络 | 南加州大学博士研究生' if zh else
                'Systems Software &amp; Networking | Ph.D. Student, USC') if pages == 1 else (
                '网络系统与机器学习 | 南加州大学博士研究生' if zh else
                'Networked Systems &amp; Machine Learning | Ph.D. Student, USC')
    story.append(p(subtitle, contact))
    story.append(p('Los Angeles, CA | +1 6124563527 | <link href="mailto:hubin@usc.edu">hubin@usc.edu</link>'
                   ' | <link href="https://Hbbbba.github.io/Resume/">Hbbbba.github.io/Resume</link>', contact))
    sec('Education', '教育经历')
    for index in [0, 2, 4]:
        e = DATA['education'][index]
        if pages == 2 or index != 4:
            story.append(p(text(e['institution']), heading))
        period = text(e['period'])
        if pages == 1 and index == 0:
            period = period.replace('May 2028', '05/2028').replace('2028年5月', '05/2028')
        story.append(p(text(e['degree']) + ' | ' + period))
        if index == 0:
            if pages == 2:
                story.append(p('导师：钱风教授。预计毕业：05/2028。' if zh else 'Advisor: Prof. Feng Qian. Expected graduation: 05/2028.'))
            story.append(p('明尼苏达大学计算机科学与工程博士阶段学习，2022.08-2023.08；随导师转至 USC。' if zh else
                           'Prior doctoral studies: University of Minnesota, CSE, Aug. 2022-Aug. 2023; transferred with advisor.'))
    sec('Technical Skills', '技术技能')
    story.append(p(('编程：' if zh else '<b>Programming:</b> ') + 'Python, C/C++, Java, MATLAB.'))
    if pages == 1:
        story.append(p(('系统与网络：' if zh else '<b>Systems &amp; networking:</b> ') +
                       ('Linux、WebRTC、Android、Raspberry Pi、TCP/UDP 套接字、多路径网络。' if zh else
                        'Linux, WebRTC, Android, Raspberry Pi, TCP/UDP sockets, multipath networking.')))
        story.append(p(('开发与分析工具：' if zh else '<b>Development &amp; analysis:</b> ') +
                       'Git, Docker, Wireshark, tcpdump, PyTorch, GNURadio.'))
    else:
        story.append(p(('工具与平台：' if zh else '<b>Tools &amp; platforms:</b> ') +
                   ('PyTorch、Linux、WebRTC、Android、Git、Docker、Wireshark/tcpdump、TCP/UDP 套接字、Raspberry Pi、GNURadio、SDR。' if zh else
                    'PyTorch, Linux, WebRTC, Android, Git, Docker, Wireshark/tcpdump, TCP/UDP sockets, Raspberry Pi, GNURadio, SDR.')))
    sec('Engineering & Research Experience' if pages == 1 else 'Research & Engineering Experience',
        '工程与科研经历' if pages == 1 else '科研与工程经历')
    # Keep the research version concise while retaining methods, results, and implementation.
    research_details = DATA['experience'][0]['details']
    two_page_details = [research_details[i] for i in [0, 2, 3, 4, 5, 7, 8, 9, 10, 11]]
    job(0, [] if pages == 1 else two_page_details)
    if pages == 1:
        for en_label, zh_label, en_detail, zh_detail in SWE_PROJECTS:
            story.append(p('- <b>' + text(zh_label if zh else en_label) + ':</b> ' +
                           text(zh_detail if zh else en_detail), bullet))
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
    selected = [1, 3] if pages == 1 else [1, 0, 3, 4, 6]
    venues = {0: 'IEEE INFOCOM Poster, 2026', 1: 'ACM HotMobile, 2026',
              3: 'USENIX NSDI, 2024', 4: 'ACM CoNEXT Companion, 2023', 6: 'IEEE ICNP, 2020'}
    for i in selected:
        pub = DATA['publications'][i]
        author = 'Bin Hu et al.' if pub['authors'][0] == 'Bin Hu' else 'Jiazhao Wang et al. (co-author: Bin Hu)'
        story.append(p(text(pub['title']) + '. <b>' + venues[i] + '.</b> ' + author))
    sec('Industry Experience', '工业界经历')
    e = DATA['industry_experience'][0]
    story.append(p(text(e['organization']), heading))
    story.append(p(text(e['role']) + ' | ' + text(e['period'])))
    bullets(e['details'])
    if pages == 2:
        sec('Selected Honors', '部分荣誉')
        awards = DATA['honors_awards']
        story.append(p('; '.join(text(awards[i]) for i in [0, 1, 2])))
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
