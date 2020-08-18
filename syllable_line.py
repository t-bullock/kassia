import collections
from typing import List, Tuple

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Flowable

from syllable import Syllable


class SyllableLine(Flowable, collections.MutableSequence):
    """This class is a collection of Syllables.
    """
    def __init__(self, leading=0, syllable_spacing=0, *args):
        super().__init__(*args)
        self.list: List[Syllable] = list()
        self.extend(list(args))
        self.leading = leading
        self.syllableSpacing = syllable_spacing

    def wrap(self, *args):
        self.set_size()  # This might not be needed
        return self.width, self.height

    def draw(self, canvas: Canvas = None):
        """This class is overloaded from Flowable's draw function.
        :param canvas: The canvas. This only gets passed to draw when called by Score directly.
        If a troparion gets split, platypus will treat the syllableLine as a Flowable and call draw without
        any parameters.
        """
        if not canvas:
            canvas = self.canv

        for syl in self.list:
            syl.draw(canvas)
        self.draw_underscore(canvas)

    def draw_underscore(self, canvas):
        for i in range(0, len(self.list)-1):
            syl = self.list[i]
            next_syl = self.list[i+1]
            x1, x2 = None, None  # Starting x pos for underscore

            # Starting line with underscore
            if i == 0 and syl.has_lyric_text('_'):
                x1 = syl.neume_chunk_pos[0]
            # When next syllable will be underscore
            elif next_syl.has_lyric_text('_'):
                # Make sure not a martyria or other special case
                if syl.lyric:
                    lyric_space_width = pdfmetrics.stringWidth(' ', syl.lyric.font_family, syl.lyric.font_size)
                    x1 = syl.lyric_pos[0] + syl.lyric.width + lyric_space_width
                else:
                    x1 = syl.neume_chunk_pos[0]

            if x1 is not None:
                x2, i = self.recurse_last_underscore_pos(i)
                y1, y2 = (syl.lyric_pos[1], syl.lyric_pos[1])
                if syl.lyric:
                    canvas.setStrokeColor(syl.lyric.color)
                    canvas.setFont(syl.lyric.font_family, syl.lyric.font_size)
                canvas.line(x1, y1, x2, y2)

    def recurse_last_underscore_pos(self, index: int) -> Tuple[float, int]:
        curr_syl = self.list[index]

        # Check if at end of line
        if index + 1 >= len(self.list):
            x2 = curr_syl.neume_chunk_pos[0] + curr_syl.width
            return x2, index

        next_syl = self.list[index+1]
        next_neume = next_syl.get_base_neume()

        # Check if next neume is syneches elaphron
        # Underscore should extend beneath apostrophos part of neume
        if next_neume.name == "syne":
            x2 = next_syl.neume_chunk_pos[0] + next_neume.lyric_offset
            return x2, index

        # Check for end of underscores
        if not next_syl.has_lyric_text('_'):
            x2 = curr_syl.neume_chunk_pos[0] + curr_syl.width
            return x2, index
        else:
            index += 1
            return self.recurse_last_underscore_pos(index)

    def set_size(self):
        if self.list:
            width = (self.list[-1].neume_chunk_pos[0] + self.list[-1].width) - self.list[0].neume_chunk_pos[0]
            self.width = width
            max_syl_height = max(syl.height for syl in self.list)
            self.height = max(max_syl_height, self.leading)

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
