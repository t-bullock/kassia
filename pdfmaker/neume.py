from reportlab.pdfbase import pdfmetrics


class Neume:
    def __init__(self, text, font_family, font_size, color):
        self.text = text
        self.font_family = font_family
        self.font_size = font_size
        self.color = color
        self.width = pdfmetrics.stringWidth(self.text, self.font_family, self.font_size)
