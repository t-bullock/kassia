#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import Iterable, List

from reportlab.pdfbase import pdfmetrics

from neume import Neume
from neume_chunk import NeumeChunk


def takes_lyric(neume: Neume):
    if neume.font_family.endswith("Main"):
        return neume.char in neumesWithLyrics
    if neume.font_family.endswith("Combo"):
        return neume.char in neumesWithLyricsCombo
    else:
        return False


def stand_alone(neume: Neume):
    if neume.font_family.endswith("Main"):
        return neume.char in standAloneNeumes
    if neume.font_family.endswith("Combo"):
        return neume.char in standAloneNeumesCombo
    if neume.font_family.endswith("Martyria"):
        return neume.char in standAloneNeumesMartyria
    else:
        return False


def chunk_neumes(neume_list: List[Neume]) -> List[NeumeChunk]:
    """Break a list of neumes into logical chunks based on whether a linebreak can occur between them
    :param neume_list: Iterable of type Neume
    """
    chunks_list: List[NeumeChunk] = []
    i = 0
    while i < len(neume_list):
        # Grab next neume
        chunk = NeumeChunk(neume_list[i])

        # Special case for Vareia, since it's non-breaking but comes before the next neume, unlike a fthora.
        # So attach the next neume and increment the counter.
        if neume_list[i].char in nonPreBreakingNeumes and (i+1) < len(neume_list):
            chunk.append(neume_list[i+1])
            i += 1

        # Add more neumes to chunk like fthora, ison, etc.
        j = 1
        if (i+1) < len(neume_list):
            while not stand_alone(neume_list[i + j]):
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



neumesWithLyrics = ['B', 'C', 'E', 'I', 'L', 'O', 'P', 'Q', 'R', 'T',
                    'U', 'V', 'W', 'X', 'Y', 'Z', 'b', 'c', 'e', 'i',
                    'o', 'p', 'q', 'r', 't', 'u', 'v', 'w', 'x', 'y',
                    'z', u'Ω', u'™',
                    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                    '!', '@', '#', '$', '%', '^', '&', '*', '(',
                    '-', '_', '`']

standAloneNeumes = ['B', 'C', 'E', 'I', 'L', 'O', 'P', 'Q', 'R', 'T',
                    'U', 'V', 'W', 'X', 'Y', 'Z', 'b', 'c', 'e', 'i',
                    'o', 'p', 'q', 'r', 't', 'u', 'v', 'w', 'x', 'y',
                    'z', u'Ω', u'™',
                    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                    '!', '@', '#', '$', '%', '^', '&', '*', '(',
                    '-', '_', '`',
                    '+', '=', '<', ',', '>', '.', '/', '?',
                    '\\']

# Neumes like a vareia. Don't break right after a vareia;
# it goes with neume after it
nonPreBreakingNeumes = ['/']

# Neumes like a kentima. Don't break right befire a vareia;
# it goes with the oligon before it
nonPostBreakingNeumes = ['~']

standAloneNeumesMartyria = ['1', '2', '3', '4', '5', '6', '7',
                            'q', 'w', 'e', 'r', 't', 'y', 'u',
                            'a', 's', 'd', 'f', 'g', 'h', 'j',
                            'z', 'x', 'c', 'v', 'b', 'n', ',',
                            '8', '9', '0', '-', '=',
                            'i', 'I', 'o', 'O', 'p', 'P', '[', '{',
                            '.', '/']

neumesWithLyricsCombo = ['u', 'i',
                         '1', '2', '3', '4', '5', '6', '7',
                         'x', 'X', 'c', 'C', 'v', 'V',
                         '-', '_']

standAloneNeumesCombo = ['u', 'i',
                         '1', '2', '3', '4', '5', '6', '7',
                         'x', 'X', 'c', 'C', 'v', 'V',
                         '-', '_']

neumesWithLyricOffset = [('_', 11)]
