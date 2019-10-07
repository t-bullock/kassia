import collections

from reportlab.pdfbase import pdfmetrics

import neume_dict
from neume import Neume


class NeumeChunk(collections.MutableSequence):
    """This class is a collection of Neumes, but with a calculated width
    """
    def __init__(self, *args):
        self.width = 0
        self.height = 0
        self.list = list()
        self.extend(list(args))

    def __len__(self):
        return len(self.list)

    def __getitem__(self, i):
        return self.list[i]

    def __delitem__(self, i):
        del self.list[i]
        self.set_width()

    def __setitem__(self, i, v):
        self.set_width()
        self.list[i] = v

    def insert(self, i, v):
        self.add_width(v)
        if self.height == 0:
            self.set_height(v)
        self.list.insert(i, v)

    def __str__(self):
        return str(self.list)

    def set_width(self):
        max_neume_width = 0
        for i, neume in enumerate(self.list):
            neume_width = pdfmetrics.stringWidth(neume.char, neume.font_family, neume.font_size)

            if neume_width == 0:
                continue

            # If kentima (or similar), add width of oligon that came before it.
            # Kentima may come at the end of the chunk, after a psefeston, etc.,
            # so we can't just check i-1.
            # Just add oligon and assume it is part of the chunk.
            # TODO: Find a better way to do this
            if neume.char in neume_dict.nonPostBreakingNeumes:
                neume_width += pdfmetrics.stringWidth('1', neume.font_family, neume.font_size)

            # If vareia (or similar), add width of next neume.
            # This prevents vareia from being at the end of a line.
            if neume.char in neume_dict.nonPreBreakingNeumes and (i + 1) < len(self.list):
                next_neume = self.list[i + 1]
                neume_width += pdfmetrics.stringWidth(next_neume.char, next_neume.font_family, next_neume.font_size)

            if max_neume_width < neume_width:
                max_neume_width = neume_width

        self.width = max_neume_width

    def set_height(self, neume):
        ascent, descent = pdfmetrics.getAscentDescent(neume.font_family, neume.font_size)
        #self.height = max(ascent - descent, neume.leading)
        self.height = ascent - descent

    def add_width(self, neume):
        neume_width = pdfmetrics.stringWidth(neume.char, neume.font_family, neume.font_size)
        self.width += neume_width
