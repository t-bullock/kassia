#!/usr/bin/python
# -*- coding: utf-8 -*-


def translate(text):
    split_text = text.split(" ")
    tmp_text = [ezPsaltica[t] if ezPsaltica.has_key(t) else t for t in split_text]
    # might need to add in a str replace for two vareia in a row
    return u''.join(tmp_text)


def takes_lyric(neume):
    if neume.font_family == "Kassia Tsak Main":
        return neume.text in neumesWithLyrics
    else:
        return False


def stand_alone(neume):
    if neume.font_family == "Kassia Tsak Main":
        return neume.text in standAloneNeumes
    if neume.font_family == "Kassia Tsak Martyria":
        return True
    else:
        return False


def chunk_neumes(neumeList):
    """Breaks neumeArray into logical chunks based on whether a linebreak
    can occur between them"""
    chunks_list = []
    i = 0
    while i < len(neumeList):
        chunk = []
        # Grab next neume
        chunk.append(neumeList[i])
        # Add more neumes to chunk like fthora, ison, etc
        j = 1
        if (i+1) < len(neumeList):
            while not stand_alone(neumeList[i + j]):
                chunk.append(neumeList[i+j])
                j += 1
                if i+j >= len(neumeList):
                    print "At the end!"
                    break
        i += j
        chunks_list.append(list(chunk))
        # Check if we're at the end of the array
        if i >= len(neumeList):
            break

    return chunks_list


ezPsaltica = {
    # ' ' : u'\uF020',
    '0': u'\uF030',
    'p': u'\uF070',
    '1': u'\uF031',
    '2': u'\uF032',
    '3': u'\uF033',
    '4': u'\uF034',
    '5': u'\uF035',
    '6': u'\uF036',
    '7': u'\uF037',
    '8': u'\uF038',
    '9': u'\uF039',
    '`': u'\uF060',
    '~': u'\uF07E',
    '=': u'\uF03D',
    'q': u'\uF071',
    'w': u'\uF077',
    'e': u'\uF065',
    'r': u'\uF072',
    't': u'\uF074',
    'y': u'\uF079',
    'u': u'\uF075',
    'i': u'\uF069',
    '!': u'\uF021',
    '@': u'\uF040',
    '_': u'\uF05F',
    ')': u'\uF029',
    '-': u'\uF02D',
    '#': u'\uF023',
    '$': u'\uF024',
    '%': u'\uF025',
    '^': u'\uF05E',
    '&': u'\uF026',
    '*': u'\uF02A',
    '(': u'\uF028',
    'Q': u'\uF051',
    'W': u'\uF057',
    'E': u'\uF045',
    'O': u'\uF04F',
    'o': u'\uF0CE',
    'l': u'\uF06C',
    'L': u'\uF04C',
    'P': u'\uF050',
    'I': u'\uF049',
    'U': u'\uF055',
    'Y': u'\uF059',
    'T': u'\uF054',
    'R': u'\uF052',
    'S': u'\uF053',
    's': u'\uF073',
    'x': u'\uF078',
    'X': u'\uF058',
    'h': u'\uF068',
    'H': u'\uF048',
    'd': u'\uF064',
    'D': u'\uF044',
    'f': u'\uF066',
    'F': u'\uF046',
    'g': u'\uF067',
    'G': u'\uF047',
    ';': u'\uF03B',
    ':': u'\uF03A',
    'k': u'\uF06B',
    'K': u'\uF04B',
    'a': u'\uF061',
    'A': u'\uF041',
    'z': u'\uF07A',
    'Z': u'\uF05A',
    '\\': u'\uF05C',
    '\'': u'\uF027',
    '"': u'\uF022',
    '}': u'\uF07D',
    '[': u'\uF05B',
    '{': u'\uF07B',
    ']': u'\uF05D',
    'J': u'\uF04A',
    'j': u'\uF06A',
    # '' : u'', # place holder for CtrlAlt-C character
    'c': u'\uF063',
    'v': u'\uF076',
    'b': u'\uF062',
    'n': u'\uF06E',
    'm': u'\uF06D',
    ',': u'\uF02C',
    '.': u'\uF02E',
    '/': u'\uF02F',
    '+': u'\uF02B',
    # '' : u'', # Place holder for Alt 0186
    '|': u'\uF07C',
    'C': u'\uF043',
    'V': u'\uF056',
    'B': u'\uF042',
    'N': u'\uF04E',
    'M': u'\uF04D',
    '>': u'\uF03E',
    '?': u'\uF03F',
    '<': u'\uF03C'}


neumesWithLyrics = ['a', 'A', u'å', u'Å', 'e', 'E', 'h', 'H', u'˙',
                    u'Ó', 'i', 'I', u'ˆ', 'j', 'J', u'∆', u'Ô', 'k', 'K', u'˚', u'', 'l', 'm',
                    'M', u'µ', u'Â', 'n', 'o', 'O', u'ø', 'p', 'P', u'π', u'∏', 'q', 'Q', u'œ',
                    u'Œ', 's', 'S', u'ß', u'Í', 'U', u'¨', 'v', 'V', u'√', u'◊', 'w', 'W',
                    u'∑', u'„', u'˛', 'y', 'Y', u'Á', '(', '_', u'±', u'”', u'«',
                    u'≤', u'Æ', '>', u'è', u'é', u'á', u'ü', u'¨', u'ê', u'û',
                    u'ã', u'À', u'Õ', u'Ã', u'Ö', u'Ü', u'Ô', u'Â']

standAloneNeumes = ['a', 'A', u'å', u'Å', 'b', 'B', u'∫', u'ı', 'e', 'E', 'h', 'H', u'˙',
                    u'Ó', 'i', 'I', u'ˆ', 'j', 'J', u'∆', u'Ô', 'k', 'K', u'˚', u'', 'l', 'm',
                    'M', u'µ', u'Â', 'n', 'o', 'O', u'ø', 'p', 'P', u'π', u'∏', 'q', 'Q', u'œ',
                    u'Œ', 's', 'S', u'ß', u'Í', u'†', 'U', u'¨', 'v', 'V', u'√', u'◊', 'w', 'W',
                    u'∑', u'„', u'˛', 'y', 'Y', u'Á', u'Ω', '(', '_', u'±', u'”', '\\', '|', u'«',
                    u'≤', u'Æ', '.', '>', '?', u'÷', u'è', u'é', u'á', u'ü', u'¨', u'ê', u'û',
                    u'ã', u'À', u'Õ', u'Ã', u'Ö', u'Ü', u'Ô', u'Â']

# Format: (neume, x-offset)
neumesWithLyricOffset = [(u'é', 12),
                         (u'á', 12)]
