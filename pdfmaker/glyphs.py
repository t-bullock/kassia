from reportlab.pdfbase import pdfmetrics

class Glyph:
    def __init__(self,neumes='',neumePos=[],lyrics='',
                 lyricsPos=[],fthora='',fthoraPos=[]):
        self.neumes = neumes
        self.neumePos = neumePos
        self.lyrics = lyrics
        self.lyricsPos = lyricsPos
        self.fthora = fthora
        self.fthoraPos = fthoraPos
        
        self.nWidth = 0     # neume width
        self.lWidth = 0     # lyric width
        self.width  = 0     # glyph width

        self.lineNum = 0    # line number, to be determined by linebreaking algorithm

    def calc_width(self,neumeFont="Kassia Tsak Main",neumeFontSize=20,
                   lyricFont="Helvetica",lyricFontSize=12):
        self.nWidth = pdfmetrics.stringWidth(self.neumes,neumeFont,neumeFontSize)
        self.lWidth = pdfmetrics.stringWidth(self.lyrics,lyricFont,lyricFontSize)
        self.width = max(self.nWidth,self.lWidth)

class GlyphLine:
    def init(self,glyphs,spacing):
        self.glyphs = glyphs
        self.spacing = spacing 

