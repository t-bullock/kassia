from typing import List, Tuple

from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Flowable

import neume_dict
from lyric import Lyric
from neume_chunk import NeumeChunk


class Glyph(Flowable):
    def __init__(self,
                 neume_chunk: NeumeChunk = None,
                 neume_chunk_pos: Tuple[float, float] = None,
                 lyric: Lyric = None,
                 lyric_pos: Tuple[float, float] = None,
                 # fthora: Fthora = None,
                 # fthora_pos: Tuple = [float, float]
                 ):
        super().__init__()
        self.neume_chunk = neume_chunk  # A list of neumes, one base neume and some zero width supporting characters
        self.neume_chunk_pos = neume_chunk_pos if neume_chunk_pos is not None else [0, 0]

        self.lyric: Lyric = lyric
        self.lyric_pos = lyric_pos if lyric_pos is not None else [0, 0]

        # self.fthora = fthora
        # self.fthora_pos = fthora_pos if fthora_pos is not None else [0, 0]

        self.width = max(getattr(self.neume_chunk, 'width', 0), getattr(self.lyric, 'width', 0))
        self.height = 0

        # self.height = max(self.neume_chunk.height, self.lyric.height + self.lyric.top_margin)

    def set_width(self):
        self.width = max(getattr(self.neume_chunk, 'width', 0), getattr(self.lyric, 'width', 0))

    def wrap(self, *args):
        # ascent, descent = pdfmetrics.getAscentDescent(self.style.fontName, self.style.fontSize)
        # height = max(ascent - descent, self.style.leading)
        return self.width, self.height

    def draw(self):
        canvas: Canvas = self.canv

        canvas.saveState()
        canvas.translate(self.neume_chunk_pos[0], self.neume_chunk_pos[1])
        pos_x: float = 0
        for i, neume in enumerate(self.neume_chunk):
            canvas.setFillColor(neume.color)
            canvas.setFont(neume.font_family, neume.font_size)
            if i > 0:
                pos_x += self.neume_chunk[i - 1].width
            canvas.drawString(pos_x, self.neume_chunk_pos[1], neume.char)
        canvas.restoreState()

        if self.lyric:
            #canvas.saveState()
            #canvas.translate(self.lyric_pos[0], self.lyric_pos[1])
            canvas.setFillColor(self.lyric.color)
            canvas.setFont(self.lyric.font_family, self.lyric.font_size)
            canvas.drawString(self.lyric_pos[0], self.lyric_pos[1], self.lyric.text)
            #canvas.restoreState()


# class GlyphLine:
#    def __init__(self, glyphs, spacing):
#        self.glyphs = glyphs
#        self.spacing = spacing

GlyphLine = List[Glyph]
