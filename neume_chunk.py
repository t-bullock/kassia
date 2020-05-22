import collections
from typing import List

from reportlab.pdfbase import pdfmetrics

from neume import Neume
from neume_dict import NeumeDict


class NeumeChunk(collections.MutableSequence):
    """A collection of Neumes, but with a calculated width and height.
    """
    def __init__(self, *args):
        self.width = 0
        self.height = 0
        self.base_neume = None
        self.list = []
        self.extend(list(args))
        self.neume_dict = NeumeDict()

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
            if self.neume_dict.is_nonPostBreakingNeume(neume.name):
                neume_width += pdfmetrics.stringWidth('1', neume.font_family, neume.font_size)

            # If vareia (or similar), add width of next neume.
            # This prevents vareia from being at the end of a line.
            if self.neume_dict.is_keepWithNext(neume.name) and (i + 1) < len(self.list):
                next_neume = self.list[i + 1]
                neume_width += pdfmetrics.stringWidth(next_neume.char, next_neume.font_family, next_neume.font_size)

            if max_neume_width < neume_width:
                max_neume_width = neume_width

        self.width = max_neume_width

    def set_height(self, neume):
        ascent, descent = pdfmetrics.getAscentDescent(neume.font_family, neume.font_size)
        self.height = ascent - descent

    def add_width(self, neume):
        self.width += neume.width


def build_chunks(neume_list: List[Neume]) -> List[NeumeChunk]:
    """Break a list of neumes into logical chunks based on whether a linebreak can occur between them
    :param neume_list: Iterable of type Neume
    """
    neume_dict: NeumeDict = NeumeDict()
    chunks_list: List[NeumeChunk] = []
    i = 0
    while i < len(neume_list):
        # Grab next neume
        neume = neume_list[i]
        chunk = NeumeChunk(neume)

        # Special case for Vareia, since it's non-breaking but comes before the next neume, unlike a fthora.
        # So attach the next neume and increment the counter.
        if neume_dict.is_keepWithNext(neume.name) and (i + 1) < len(neume_list):
            chunk.append(neume_list[i+1])
            chunk.base_neume = neume_list[i+1]
            i += 1
        else:
            chunk.base_neume = neume

        # Add more neumes to chunk like fthora, ison, etc.
        j = 1
        if (i+1) < len(neume_list):
            while not neume_dict.is_standalone(neume_list[i + j]):
                chunk.append(neume_list[i+j])
                j += 1
                if i+j >= len(neume_list):
                    break
        i += j
        chunks_list.append(chunk)
        # Check if we're at the end of the array
        if i >= len(neume_list):
            break

    return chunks_list
