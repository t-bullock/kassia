import collections
from typing import List, Tuple

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Flowable

from glyphs import Glyph


class GlyphLine(Flowable, collections.MutableSequence):
    """This class is a collection of Glyphs.
    """
    def __init__(self, leading=0, glyph_spacing=0, *args):
        super().__init__(*args)
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
        for i in range(0, len(self.list)-1):
            glyph = self.list[i]
            next_glyph = self.list[i+1]
            x1, x2 = None, None  # Starting x pos for underscore

            # Starting line with underscore
            if i == 0 and glyph.has_lyric_text('_'):
                x1 = glyph.neume_chunk_pos[0]
            # When next glyph will be underscore
            elif next_glyph.has_lyric_text('_'):
                # Make sure not a martyria or other special case
                if glyph.lyric:
                    lyric_space_width = pdfmetrics.stringWidth(' ', glyph.lyric.font_family, glyph.lyric.font_size)
                    x1 = glyph.lyric_pos[0] + glyph.lyric.width + lyric_space_width
                else:
                    x1 = glyph.neume_chunk_pos[0]

            if x1 is not None:
                x2, i = self.recurse_last_underscore_pos(i)
                y1, y2 = (glyph.lyric_pos[1], glyph.lyric_pos[1])
                if glyph.lyric:
                    canvas.setStrokeColor(glyph.lyric.color)
                    canvas.setFont(glyph.lyric.font_family, glyph.lyric.font_size)
                canvas.line(x1, y1, x2, y2)

    def recurse_last_underscore_pos(self, index: int) -> Tuple[float, int]:
        curr_glyph = self.list[index]
        curr_neume = curr_glyph.get_base_neume()

        # Check if at end of line
        if index + 1 >= len(self.list):
            x2 = curr_glyph.neume_chunk_pos[0] + curr_glyph.width
            return x2, index

        next_glyph = self.list[index+1]
        next_neume = next_glyph.get_base_neume()

        # Check if next neume is syneches elaphron
        # Underscore should extend beneath apostrophos part of neume
        if next_neume.name == "syne":
            x2 = next_glyph.neume_chunk_pos[0] + next_neume.lyric_offset
            return x2, index

        # Check for end of underscores
        if not next_glyph.has_lyric_text('_'):
            x2 = curr_glyph.neume_chunk_pos[0] + curr_glyph.width
            return x2, index
        else:
            index += 1
            return self.recurse_last_underscore_pos(index)

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
