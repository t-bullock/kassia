from typing import List

from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Flowable

from drop_cap import Dropcap
from glyph_line import GlyphLine


class Troparion(Flowable):
    def __init__(self, glyphlines: List[GlyphLine] = None,
                 dropcap: Dropcap = None,
                 available_width: float = 0):
        super().__init__()
        self.dropcap: Dropcap = dropcap
        self.glyphlines: List[GlyphLine] = glyphlines
        self.width: float = self._calc_width(available_width)
        self.height: float = self._calc_height()

    def _calc_width(self, available_width: float) -> float:
        width: float = available_width
        if len(self.glyphlines) == 1:
            width = self.glyphlines[0].width + getattr(self.dropcap, 'width', 0) + getattr(self.dropcap, 'x_padding', 0)
        return width

    def _calc_height(self):
        height: float = sum(line.height for line in self.glyphlines)
        return height

    def wrap(self, *args):
        return self.width, self.height

    def draw(self):
        canvas: Canvas = self.canv
        canvas.saveState()
        canvas.translate(0, self.height-self.glyphlines[0].height)

        iter_lines = iter(self.glyphlines)

        if self.dropcap:
            canvas.saveState()
            self.dropcap.draw(canvas)
            canvas.translate(self.dropcap.width + self.dropcap.x_padding, 0)
            self.glyphlines[0].draw(canvas)
            canvas.restoreState()
            canvas.translate(0, -self.glyphlines[0].height)
            next(iter_lines)

        for line in iter_lines:
            line.draw(canvas)
            canvas.translate(0, -line.height)

        canvas.restoreState()

    def split(self, avail_width, avail_height):
        # If no actual lines, or there's not enough space for even the first line, force new page
        # We shouldn't have to check if the first line can fit (ReportLab Flowable code should handle
        # that), but RL throws errors if we don't manually check for it here.
        if len(self.glyphlines) <= 0 or avail_height < self.glyphlines[0].height:
            return []

        if avail_height >= self.height:
            return [self]

        if self.dropcap:
            first_line = Troparion([self.glyphlines.pop(0)], self.dropcap, avail_width)
            return [first_line, *self.glyphlines]
        else:
            return self.glyphlines
