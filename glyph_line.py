import collections
from typing import List

from reportlab.pdfbase import pdfmetrics
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
        self.draw_underscore(canvas)

    def draw_underscore(self, canvas):
        for i, glyph in enumerate(self.list):
            if glyph.lyric and glyph.lyric.text == '_':
                canvas.setStrokeColor(glyph.lyric.color)
                canvas.setFont(glyph.lyric.font_family, glyph.lyric.font_size)

                # Check if glyph with underscore is on a new line or not
                if i-1 >= 0:
                    prev_glyph = self.list[i-1]
                    lyric_space_width = pdfmetrics.stringWidth(' ', glyph.lyric.font_family, glyph.lyric.font_size)
                    x1 = prev_glyph.lyric_pos[0] + prev_glyph.lyric.width + lyric_space_width
                else:
                    x1 = glyph.lyric_pos[0]

                # Check if next neume is syneches elaphron (special extend beneath next neume)
                if i+1 < len(self.list) and self.list[i+1].neume_chunk[0].char == '_':
                    next_glyph = self.list[i+1]
                    apostrophos_width = pdfmetrics.stringWidth('!', glyph.neume_chunk[0].font_family, glyph.neume_chunk[0].font_size)
                    x2 = next_glyph.neume_chunk_pos[0] + apostrophos_width
                else:
                    j = i
                    while j < len(self.list) and self.list[j].lyric and self.list[j].lyric.text == '_':
                        j += 1
                    x2 = self.list[j-1].neume_chunk_pos[0] + self.list[j-1].width

                y1, y2 = (glyph.lyric_pos[1], glyph.lyric_pos[1])

                canvas.line(x1, y1, x2, y2)

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
