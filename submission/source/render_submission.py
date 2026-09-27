import json
import html
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, Preformatted, KeepTogether, KeepInFrame)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FONT = Path('C:/Windows/Fonts/segoeui.ttf')
FONT_B = Path('C:/Windows/Fonts/segoeuib.ttf')
if FONT.exists():
    pdfmetrics.registerFont(TTFont('Segoe', str(FONT)))
    pdfmetrics.registerFont(TTFont('Segoe-Bold', str(FONT_B)))
    BASE, BOLD = 'Segoe', 'Segoe-Bold'
else:
    BASE, BOLD = 'Helvetica', 'Helvetica-Bold'

navy = colors.HexColor('#102235')
teal = colors.HexColor('#0E8F87')
ink = colors.HexColor('#20303D')
muted = colors.HexColor('#5A6A73')
line = colors.HexColor('#D8E2E2')
soft = colors.HexColor('#F1F6F5')

styles = getSampleStyleSheet()
styles.add(ParagraphStyle('DocTitle', fontName=BOLD, fontSize=22, leading=26, textColor=navy, spaceAfter=5))
styles.add(ParagraphStyle('Kicker', fontName=BOLD, fontSize=7.5, leading=10, textColor=teal, tracking=1.2, spaceAfter=7))
styles.add(ParagraphStyle('Deck', fontName=BASE, fontSize=9.4, leading=13, textColor=muted, spaceAfter=14))
styles.add(ParagraphStyle('H2x', fontName=BOLD, fontSize=12.5, leading=15, textColor=navy, spaceBefore=7, spaceAfter=4))
styles.add(ParagraphStyle('Bodyx', fontName=BASE, fontSize=9, leading=13, textColor=ink, spaceAfter=5))
styles.add(ParagraphStyle('Bulletx', fontName=BASE, fontSize=8.7, leading=12.5, leftIndent=12, firstLineIndent=-7, bulletIndent=2, textColor=ink, spaceAfter=3))
styles.add(ParagraphStyle('Sourcex', fontName=BASE, fontSize=7.2, leading=9.2, textColor=muted, spaceBefore=6))
styles.add(ParagraphStyle('Cellx', fontName=BASE, fontSize=7.3, leading=9.3, textColor=ink))
styles.add(ParagraphStyle('CellHead', fontName=BOLD, fontSize=7.2, leading=9, textColor=colors.white))
styles.add(ParagraphStyle('Codex', fontName='Courier', fontSize=6.8, leading=8.5, textColor=ink, backColor=soft, borderPadding=5))

def P(text, style='Bodyx'):
    # Preserve literal text while allowing only explicit line breaks.
    text = html.escape(str(text)).replace('\n', '<br/>')
    return Paragraph(text, styles[style])

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(line)
    canvas.line(18*mm, 15*mm, 192*mm, 15*mm)
    canvas.setFont(BASE, 7)
    canvas.setFillColor(muted)
    canvas.drawString(18*mm, 10.5*mm, 'ATLAS OFFICE  /  SP-D ORGANIZATIONAL COLLABORATION OFFICE')
    canvas.drawRightString(192*mm, 10.5*mm, f'{doc.page}')
    canvas.restoreState()

def table_flow(table_obj):
    headers = table_obj.get('headers', [])
    rows = table_obj.get('rows', [])
    data = [[Paragraph(html.escape(str(x)), styles['CellHead']) for x in headers]]
    data += [[Paragraph(html.escape(str(x)), styles['Cellx']) for x in row] for row in rows]
    widths = [174*mm/len(headers)] * len(headers) if headers else None
    t = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('VALIGN', (0,0), (-1,-1), 'TOP'), ('GRID', (0,0), (-1,-1), 0.35, line),
        ('BACKGROUND', (0,1), (-1,-1), colors.white), ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, soft]),
        ('LEFTPADDING', (0,0), (-1,-1), 5), ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    return t

def section_flow(section):
    f = [P(section.get('heading',''), 'H2x')]
    for para in section.get('paragraphs', []): f.append(P(para))
    if section.get('bullets'):
        for item in section['bullets']:
            f.append(Paragraph('• ' + html.escape(str(item)), styles['Bulletx']))
    if section.get('table'):
        f += [Spacer(1, 2), table_flow(section['table']), Spacer(1, 4)]
    if section.get('code'):
        f += [Spacer(1, 2), Preformatted(section['code'], styles['Codex'], maxLineLength=102), Spacer(1, 4)]
    return f

def render_json(src, out, max_pages=None):
    data = json.loads(Path(src).read_text(encoding='utf-8'))
    doc = SimpleDocTemplate(str(out), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=16*mm, bottomMargin=20*mm, title=data.get('title','Atlas Office'))
    story = []
    pages = data['pages'][:max_pages] if max_pages else data['pages']
    for idx, page in enumerate(pages):
        content=[]
        content.append(P(page.get('kicker',''), 'Kicker'))
        content.append(P(page.get('title',''), 'DocTitle'))
        if idx == 0:
            content.append(P(data.get('subtitle','') + '  |  ' + data.get('version',''), 'Deck'))
        for section in page.get('sections', []):
            content.extend(section_flow(section))
        if page.get('sources'):
            content.append(P('Sources: ' + '  |  '.join(page['sources']), 'Sourcex'))
        story.append(KeepInFrame(174*mm,257*mm,content,mode='shrink',hAlign='LEFT',vAlign='TOP'))
        if idx < len(pages)-1: story.append(PageBreak())
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return len(pages)

paths = [
    (HERE/'skill_description.json', ROOT/'01-skill-function-description.pdf', None),
    (HERE/'api_complete.json', ROOT/'02-api-documentation.pdf', None),
    (HERE/'enterprise_fit.json', ROOT/'04-enterprise-challenge-fit.pdf', None),
]
for source, output, limit in paths:
    count = render_json(source, output, limit)
    print(output.name, count, output.stat().st_size)
