import collections
from typing import List

from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Flowable

from glyphs import Glyph


class GlyphLine(Flowable, collections.MutableSequence):
    """This class is a collection of Glyphs.
    """
    def __init__(self, space_after=0, *args):
        super().__init__()
        self.list: List[Glyph] = list()
        self.extend(list(args))
        self.spaceAfter = space_after
        self._showBoundary = True

    def wrap(self, *args):
        width = sum(glyph.width for glyph in self.list)
        self.width = width
        if self.list:
            height = max(glyph.height for glyph in self.list)
            self.height = height
        return width, self.height + self.spaceAfter

    def draw(self):
        canvas: Canvas = self.canv
        for glyph in self.list:
            glyph.draw(canvas)

    def set_size(self):
        width = sum(glyph.width for glyph in self.list)
        self.width = width
        if self.list:
            height = max(glyph.height for glyph in self.list)
            self.height = height

    def __len__(self):
        return len(self.list)

    def __getitem__(self, i):
        return self.list[i]

    def __delitem__(self, i):
        self.set_size()
        del self.list[i]

    def __setitem__(self, i, v):
        self.set_size()
        self.list[i] = v

    def insert(self, i, v):
        self.set_size()
        self.list.insert(i, v)

    def __str__(self):
        return str(self.list)
