from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus.flowables import Flowable


class Dropcap(Flowable):
    def __init__(self, text: str = None, x_padding: int = 0, style: ParagraphStyle = ParagraphStyle('defaults')):
        super().__init__()
        self.text = text
        self.x_padding = x_padding
        self.style = style
        self.width = pdfmetrics.stringWidth(self.text, self.style.fontName, self.style.fontSize)
        ascent, descent = pdfmetrics.getAscentDescent(self.style.fontName, self.style.fontSize)
        self.height = max(ascent - descent, self.style.leading)
        #self.page_settings = page_settings
        #self.y_offset = -glyph_height

    def wrap(self, *args):
        return self.width + self.x_padding, self.height

    def draw(self):
        if not self.text:
            return

        canvas = self.canv
        canvas.setFillColor(self.style.textColor)
        canvas.setFont(self.style.fontName, self.style.fontSize)

        # Use this to bypass possibly unnecessary string stuff
        # tx = canvas.beginText(text=self.text)
        # canvas.drawText(tx)
        canvas.drawString(0, 0, self.text)

    '''def _draw_background(self):
        bw = getattr(style, 'borderWidth', None)
        bc = getattr(style, 'borderColor', None)
        bg = style.backColor

        if bg or (bc and bw):
            canvas.saveState()
            op = canvas.rect
            kwds = dict(fill=0, stroke=0)
            if bc and bw:
                canvas.setStrokeColor(bc)
                canvas.setLineWidth(bw)
                kwds['stroke'] = 1
                br = getattr(style, 'borderRadius', 0)
                if br and not debug:
                    op = canvas.roundRect
                    kwds['radius'] = br
            if bg:
                canvas.setFillColor(bg)
                kwds['fill'] = 1
            bp = getattr(style, 'borderPadding', 0)
            tbp, rbp, bbp, lbp = normalizeTRBL(bp)
            op(leftIndent - lbp,
               -bbp,
               self.width - (leftIndent + style.rightIndent) + lbp + rbp,
               self.height + tbp + bbp,
               **kwds)
            canvas.restoreState()
            '''
