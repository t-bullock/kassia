import collections
from typing import List

from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Flowable

from glyphs import Glyph


class GlyphLine(Flowable, collections.MutableSequence):
    """This class is a collection of Glyphs.
    """
    def __init__(self, leading=0, glyph_spacing=0, *args):
        super().__init__()
        self.list: List[Glyph] = list()
        self.extend(list(args))
        self.leading = leading
        self.glyphSpacing = glyph_spacing

    def wrap(self, *args):
        self.set_size()  # This might not be needed
        return self.width, self.height

    def draw(self):
        canvas: Canvas = self.canv
        for glyph in self.list:
            glyph.draw(canvas)

    def set_size(self):
        if self.list:
            width = (self.list[-1].neume_chunk_pos[0] + self.list[-1].width) - self.list[0].neume_chunk_pos[0]
            self.width = width
            glyphs_height = max(glyph.height for glyph in self.list)
            self.height = max(glyphs_height, self.leading)

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
