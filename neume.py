# -*- coding: utf-8 -*-
from typing import List

from reportlab.pdfbase import pdfmetrics

from neume_type import NeumeType


class NeumeBnml:
    def __init__(self,
                 name: str,
                 category: NeumeType):
        self.name: str = name  # The name in standard BNML
        self.category: NeumeType = category


class Neume:
    def __init__(self, name: str,
                 char: str,
                 font_family: str,
                 font_fullname: str,
                 font_size: int,
                 color: str,
                 standalone: bool,
                 takes_lyric: bool,
                 lyric_offset: float,
                 keep_with_next: bool,
                 category: NeumeType,
                 offset: List[float] = (0.0, 0.0)):
        self.name: str = name  # The name in standard BNML
        self.char: str = char  # The character in a TTF
        self.font_family: str = font_family  # The font family name
        self.font_fullname: str = font_fullname  # The specific font file name
        self.font_size: int = font_size
        self.color: str = color
        self.width: float = pdfmetrics.stringWidth(self.char, self.font_fullname, self.font_size)
        ascent, descent = pdfmetrics.getAscentDescent(self.font_fullname, self.font_size)
        self.height: float = ascent - descent
        self.standalone: bool = standalone
        self.takes_lyric: bool = takes_lyric
        self.lyric_offset: float = lyric_offset
        self.keep_with_next: bool = keep_with_next
        self.offset: List[float] = offset
        self.category: NeumeType = category

        if self.font_fullname not in pdfmetrics.getRegisteredFontNames():
            raise Exception("Neume font {} is not registered".format(self.font_fullname))
