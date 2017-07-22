from reportlab.pdfbase import pdfmetrics
import neume_dict


class Glyph:
    def __init__(self, neume_chunk=None, neume_pos=[], lyrics_text=None, lyrics_font_family=None, lyrics_size=0,
                 lyrics_color=None, lyrics_top_margin=0, lyrics_pos=[], fthora='', fthora_pos=[]):
        self.neumeChunk = neume_chunk
        self.neumePos = neume_pos
        self.lyricsText = lyrics_text
        #self.lyricsPos = lyrics_pos
        self.lyricsFontFamily = lyrics_font_family
        self.lyricsFontSize = lyrics_size
        self.lyricsFontColor = lyrics_color
        self.lyricsTopMargin = lyrics_top_margin
        self.fthora = fthora
        self.fthoraPos = fthora_pos

        self.nWidth = 0     # neume width
        self.lWidth = 0     # lyric width
        self.width = 0      # glyph width

        self.height = 0     # glyph height

    def calc_chunk_width(self):
        max_neumue_width = 0
        for neume in self.neumeChunk:
            neume_width = pdfmetrics.stringWidth(neume.text, neume.font_family, neume.font_size)

            # If kentima, add width of oligon
            # Kentima may come at the end of the chunk, after
            # a psefeston, etc., so can't just check i-1
            # TODO: Find a better way to do this
            if neume.text in neume_dict.nonBreakingNeumesWithWidth:
                neume_width += pdfmetrics.stringWidth('1', neume.font_family, neume.font_size)

            if max_neumue_width < neume_width:
                max_neumue_width = neume_width

        self.nWidth = max_neumue_width
        if self.lyricsText is not None:
            self.lWidth = pdfmetrics.stringWidth(self.lyricsText, self.lyricsFontFamily, self.lyricsFontSize)
        else:
            self.lWidth = 0
        self.width = max(self.nWidth, self.lWidth)


class GlyphLine:
    def __init__(self, glyphs, spacing):
        self.glyphs = glyphs
        self.spacing = spacing
