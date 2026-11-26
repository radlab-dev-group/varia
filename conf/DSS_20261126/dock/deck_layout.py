import re
from textwrap import wrap

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.util import Inches, Pt


PAPER = 'F5F3EB'
INK = '142E2B'
GREEN = '006B56'
MINT = 'B0F3CA'
ORANGE = 'FFAA78'
MUTED = '4E635C'
LINE = 'C9D4C9'
MONO = 'Liberation Mono'
SANS = 'Liberation Sans'
W, H = 13 + 1 / 3, 7.5
M = .67


def block(slide, x, y, w, h, color, kind=MSO_SHAPE.RECTANGLE):
    shape = slide.shapes.add_shape(kind, *map(Inches, (x, y, w, h)))
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor.from_string(color)
    shape.line.fill.background()
    shape.shadow.inherit = False
    return shape


def label(slide, x, y, w, h, text, size, color=INK, bold=False, font=SANS,
          wrap_text=True, align=PP_ALIGN.LEFT, center=False):
    frame = slide.shapes.add_textbox(*map(Inches, (x, y, w, h))).text_frame
    frame.margin_top = frame.margin_bottom = frame.margin_left = frame.margin_right = 0
    frame.auto_size = MSO_AUTO_SIZE.NONE
    frame.word_wrap = wrap_text
    frame.vertical_anchor = MSO_ANCHOR.MIDDLE if center else MSO_ANCHOR.TOP
    frame.text = text
    for p in frame.paragraphs:
        p.alignment = align
        p.space_after = Pt(0)
        p.font.name, p.font.size, p.font.bold = font, Pt(size), bold
        p.font.color.rgb = RGBColor.from_string(color)
    return frame


class Deck:
    def __init__(self):
        self.file = Presentation()
        self.file.slide_width, self.file.slide_height = Inches(W), Inches(H)
        self.section = 0

    def sheet(self, tag, dark=False):
        slide = self.file.slides.add_slide(self.file.slide_layouts[6])
        fill = slide.background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor.from_string(INK if dark else PAPER)
        fg, rule = (MINT, '416159') if dark else (GREEN, LINE)
        block(slide, M, .39, .11, .11, ORANGE if dark else GREEN)
        label(slide, .90, .35, 11.3, .24, tag.upper(), 11, fg, True, MONO)
        block(slide, M, 6.99, 12, .014, rule)
        label(slide, M, 7.10, 8, .24, 'DSS 2026   /   PAWEŁ KĘDZIA', 10, fg, font=MONO)
        label(slide, 10.45, 7.10, 2.21, .24, f'LLMROUTER   /   {len(self.file.slides):02}',
              10, fg, font=MONO, align=PP_ALIGN.RIGHT)
        return slide

    def title_slide(self, title, subtitle, author):
        slide = self.sheet('Data Science Summit 2026   /   Warsztat online', True)
        label(slide, M, 1.22, 7.2, 2.46, title.replace(': ', ':\n'), 43, PAPER, True)
        label(slide, M, 3.97, 7.08, 1.27, subtitle, 22, MINT)
        label(slide, M, 5.88, 6.0, .48, author, 24, PAPER, True)
        label(slide, M, 6.46, 7.1, .27, '26 LISTOPADA 2026', 12, MINT, font=MONO)
        # A simple branching circuit doubles as a map of the workshop.
        block(slide, 8.28, 1.18, 4.39, 5.44, '203C36')
        label(slide, 8.61, 1.52, 3.75, .32, 'FIG. 01  /  TRASA ŻĄDANIA', 11, MINT, font=MONO)
        block(slide, 8.96, 2.35, .026, 3.53, MINT)
        for y, name, root in [(2.32, 'LLMRouter', True), (3.66, 'Ollama', False),
                              (4.70, 'llama.cpp', False), (5.74, 'vLLM', False)]:
            block(slide, 8.87, y + .055, .21, .21, ORANGE if root else MINT, MSO_SHAPE.OVAL)
            if not root:
                block(slide, 9.06, y + .145, .36, .025, MINT)
            label(slide, 9.52, y - .04, 2.94, .44, name, 22, PAPER, root, MONO)
        props = self.file.core_properties
        props.title, props.subject, props.author = ' '.join(title.split()), ' '.join(subtitle.split()), author

    def head(self, title, subtitle, tag):
        slide = self.sheet(tag)
        size = 32 if len(title) <= 56 else 27 if len(title) <= 74 else 23
        label(slide, M, .80, 12, .75, title, size, bold=True)
        if subtitle:
            label(slide, M, 1.61, 12, .60, subtitle, 17, MUTED)
        return slide, 2.35 if subtitle else 1.82

    def section_slide(self, title, subtitle=''):
        self.section += 1
        slide = self.sheet('Warsztat   /   Nowy rozdział', True)
        label(slide, M, 1.45, 3, 1.26, f'{self.section:02}', 74, ORANGE, font=MONO)
        block(slide, M, 3.0, 12, .023, '416159')
        label(slide, M, 3.35, 12, 1.55, title, 43, PAPER, True)
        label(slide, M, 5.18, 11.4, 1.02, subtitle, 22, MINT)

    def content_slide(self, title, bullets, subtitle='', note=''):
        slide, top = self.head(title, subtitle, 'Notatnik warsztatowy')
        rows = [b if isinstance(b, str) else b[1] for b in bullets]
        end = 6.12 if note else 6.69
        row_h = (end - top) / len(rows)
        size = 18 if len(rows) >= 6 or max(map(len, rows)) > 110 else 22
        for i, text in enumerate(rows):
            y = top + i * row_h
            block(slide, M, y, 12, .013, LINE)
            label(slide, M, y + .02, .72, row_h - .04, f'{i + 1:02}', 14, GREEN,
                  font=MONO, center=True)
            frame = label(slide, 1.54, y + .02, 11.12, row_h - .04,
                          re.sub(r'^\d+\. ', '', text), size, center=True)
            url = re.search(r'https?://\S+', text)
            if url:
                frame.paragraphs[0].runs[0].hyperlink.address = url.group()
        self.note(slide, note)

    @staticmethod
    def note(slide, note):
        if note:
            block(slide, M, 6.27, .052, .51, GREEN)
            label(slide, .91, 6.22, 11.75, .62, note, 15, MUTED, center=True)

    def code_slide(self, title, code, subtitle='', note='', excerpt=None):
        slide, y = self.head(title, subtitle, 'Laboratorium   /   Kod i konfiguracja')
        bottom = 6.12 if note else 6.74
        block(slide, M, y, 12, bottom - y, INK)
        block(slide, M, y, 12, .43, '25443D')
        tag = '>_   SESJA LOKALNA'
        if excerpt:
            slide.notes_slide.notes_text_frame.text = code
            tag = '>_   FRAGMENT   /   PEŁNY PRZYKŁAD W NOTATKACH SLAJDU'
        label(slide, .94, y + .09, 11.3, .24, tag, 11, MINT, True, MONO)
        lines = (excerpt or code).strip('\n').expandtabs(4).splitlines()
        size = min(22, (bottom - y - .84) * 72 / (1.22 * len(lines)),
                   11.30 * 72 / (.61 * max(map(len, lines))))
        frame = label(slide, .99, y + .62, 11.32, bottom - y - .69, '\n'.join(lines),
                      size, PAPER, font=MONO, wrap_text=False)
        for p in frame.paragraphs:
            p.line_spacing = Pt(size * 1.22)
            if p.text.lstrip().startswith('#'):
                p.font.color.rgb = RGBColor.from_string(MINT)
        self.note(slide, note)

    def two_col_slide(self, title, left_title, left_bullets, right_title, right_bullets, subtitle=''):
        slide, top = self.head(title, subtitle, 'Zestawienie')
        for i, (heading, rows) in enumerate([(left_title, left_bullets), (right_title, right_bullets)]):
            x = M + 6.14 * i
            fg = PAPER if i == 0 else INK
            block(slide, x, top, 5.86, 6.74 - top, INK if i == 0 else 'DDE8DD')
            label(slide, x + .29, top + .25, 5.28, .85, heading, 23, fg, True)
            start = top + 1.11
            weights = [max(1, len(wrap(text, width=42))) for text in rows]
            unit = (6.53 - start) / sum(w + .60 for w in weights)
            for text, weight in zip(rows, weights):
                h = unit * (weight + .60)
                block(slide, x + .29, start, 5.25, .011, '476159' if i == 0 else 'B8C9BC')
                label(slide, x + .29, start + .025, 5.28, h - .05, text, 16 if len(rows) > 4 else 17,
                      fg, center=True)
                start += h

    def architecture_slide(self):
        slide, _ = self.head('Jak żądanie trafia do lokalnego modelu?',
                             'Agent zna adres routera. Wybór modelu i jego instancji odbywa się po stronie serwera.',
                             'Architektura   /   Przepływ żądania')
        cols = [(M, 3.13, '01  /  KLIENT'), (4.15, 4.88, '02  /  LLMROUTER'),
                (9.39, 3.28, '03  /  SILNIK')]
        for x, width, heading in cols:
            label(slide, x, 2.43, width, .28, heading, 13, GREEN, True, MONO)
        for x in (3.80, 9.03):
            block(slide, x, 4.11, .36, .18, GREEN, MSO_SHAPE.RIGHT_ARROW)
        for x, width, rows in [(M, 3.13, [('Codex CLI', '/v1/responses'), ('Claude Code', '/v1/messages')]),
                               (9.39, 3.28, [('Ollama', 'Serwer lokalny'), ('llama.cpp', 'Serwer lokalny'),
                                             ('vLLM', 'Serwer lokalny')])]:
            h = 2.64 / len(rows)
            for i, (name, desc) in enumerate(rows):
                y = 2.87 + i * h
                block(slide, x, y, width, h - .09, 'DDE8DD')
                label(slide, x + .20, y + .10, width - .40, .37, name, 20, bold=True)
                label(slide, x + .20, y + .50, width - .40, .25, desc, 12, MUTED, font=MONO)
        block(slide, 4.15, 2.87, 4.88, 2.55, INK)
        for i, (name, desc) in enumerate([('Wtyczka routingu', 'Dobiera model do zadania.'),
                                          ('Strategia równoważenia', 'Wybiera instancję z wolnym slotem.')]):
            y = 3.11 + i * 1.17
            label(slide, 4.42, y, 4.40, .42, name, 21, MINT, True)
            label(slide, 4.42, y + .49, 4.40, .42, desc, 16, PAPER)
        block(slide, 6.56, 5.42, .025, .39, GREEN)
        block(slide, 4.15, 5.81, 4.88, .68, 'F4D8BF')
        label(slide, 4.33, 5.83, 4.52, .59, 'Redis  /  wspólny stan slotów', 16, bold=True, center=True)