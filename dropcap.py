from reportlab.lib.colors import Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics


class Dropcap:
    def __init__(self, text: str, style: ParagraphStyle):
        self.text = text
        self.style = style
        self.width = pdfmetrics.stringWidth(self.text, self.style.fontName, self.style.fontSize)
