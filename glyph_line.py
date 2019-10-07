import collections
from typing import List

from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Flowable

from glyphs import Glyph


class GlyphLine(Flowable, collections.MutableSequence):
    """This class is a collection of Glyphs.
    """
    def __init__(self, line_spacing=0, *args):
        super().__init__()
        self.list: List[Glyph] = list()
        self.extend(list(args))
        self.height = 70
        self.line_spacing = line_spacing

    def wrap(self, *args):
        width = sum(glyph.width for glyph in self.list)
        return width, self.height + self.line_spacing

    def draw(self):
        canvas: Canvas = self.canv
        canvas.saveState()
        for glyph in self.list:
            glyph.draw(canvas)
        canvas.restoreState()

    def __len__(self):
        return len(self.list)

    def __getitem__(self, i):
        return self.list[i]

    def __delitem__(self, i):
        del self.list[i]

    def __setitem__(self, i, v):
        self.list[i] = v

    def insert(self, i, v):
        self.list.insert(i, v)

    def __str__(self):
        return str(self.list)
