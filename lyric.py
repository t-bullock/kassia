from reportlab.pdfbase import pdfmetrics


class Lyric:
    def __init__(self, text, font_family, font_size, color, top_margin):
        self.text = text
        self.font_family = font_family
        self.font_size = font_size
        self.color = color
        self.top_margin = top_margin
        self.width = pdfmetrics.stringWidth(self.text, self.font_family, self.font_size)
        ascent, descent = pdfmetrics.getAscentDescent(self.font_family, self.font_size)
        self.height = ascent - descent

    def recalc_width(self):
        self.width = pdfmetrics.stringWidth(self.text, self.font_family, self.font_size)
