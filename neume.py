# -*- coding: utf-8 -*-
from reportlab.pdfbase import pdfmetrics


class Neume:
    def __init__(self, name: str,
                 char: str,
                 font_family: str,
                 font_size: int,
                 color: str,
                 standalone: bool,
                 takes_lyric: bool,
                 keep_with_next: bool,
                 offset: (float, float) = (0.0, 0.0)):
        self.name: str = name  # The name in standard BNML
        self.char: str = char  # The character in a TTF
        if font_family not in pdfmetrics.getRegisteredFontNames():
            raise Exception("Neume font is not registered")
        self.font_family: str = font_family
        self.font_size: int = font_size
        self.color: str = color
        self.width: float = pdfmetrics.stringWidth(self.char, self.font_family, self.font_size)
        ascent, descent = pdfmetrics.getAscentDescent(self.font_family, self.font_size)
        self.height: float = ascent - descent
        self.standalone: bool = standalone
        self.takes_lyric: bool = takes_lyric
        self.keep_with_next: bool = keep_with_next
        self.offset = offset
