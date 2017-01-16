from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors


class Neume:
    def __init__(self, text, font_family='Ephesios Main', font_size=30, color=colors.black):
        self.text = text
        self.font_family = font_family
        self.font_size = font_size
        self.color = color
        self.width = pdfmetrics.stringWidth(self.text, self.font_family, self.font_size)
