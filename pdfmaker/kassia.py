import neume_dict, font_reader
from glyphs import Glyph, GlyphLine

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter
import reportlab.lib.colors as colors

import sys
import xml.etree.ElementTree as ET
import re
from copy import deepcopy

class Cursor:
    def __init__(self,x=0,y=0):
        self.x = x
        self.y = y
        
class Kassia:
    """Base class for package"""
    def __init__(self,fileName,outFile = "out.pdf"):
        self.fileName = fileName # input file
        self.outFile = outFile # output file
        try:
            open(fileName,"r")
            fileReadable = True
        except IOError:
            fileReadable = False
            print "Not readable"
        
        if fileReadable:
            self.setDefaults()
            self.parseFile()
            self.createPDF()

    def setDefaults(self):
        # Set page defaults
        self.pageAttrib = {}
        self.pageAttrib['paper_size'] = letter
        self.pageAttrib['top_margin'] = 72
        self.pageAttrib['bottom_margin'] = 72
        self.pageAttrib['left_margin'] = 72
        self.pageAttrib['right_margin'] = 72
        self.pageAttrib['line_height'] = 72
        self.pageAttrib['line_width'] = self.pageAttrib['paper_size'][0] - (self.pageAttrib['left_margin'] + self.pageAttrib['right_margin'])

        font_reader.registerFonts()

        # Set title defaults
        self.titleAttrib = {}
        self.titleAttrib['font'] = 'Helvetica'
        self.titleAttrib['font_size'] = 18
        self.titleAttrib['color'] = colors.black
        self.titleAttrib['top_margin'] = 10

        # Set annotation defaults
        self.annotationAttrib = {}
        self.annotationAttrib['font'] = 'Helvetica'
        self.annotationAttrib['font_size'] = 12
        self.annotationAttrib['color'] = colors.black
        self.annotationAttrib['align'] = 'center'
        self.annotationAttrib['top_margin'] = 10

        # Set neume defaults
        self.neumeFont = {}
        self.neumeFont['font'] = 'Kassia Tsak Main'
        self.neumeFont['font_size'] = 20

        # Set dropcap defaults
        self.dropCap = {}
        #self.dropCap['font'] = 'EZOmega'
        #self.dropCap['font_size'] = 40

        # Set lyric defaults
        self.lyricFont = {}
        self.lyricFont['font'] = 'Helvetica'
        self.lyricFont['font_size'] = 12
        self.lyricFont['top_margin'] = 0

    def parseFile(self):
        try:
            bnmlTree = ET.parse(self.fileName)
            bnml = bnmlTree.getroot()
            self.bnml = bnml

        except ET.ParseError:
            print "Failed to parse XML file"

    def createPDF(self):
        """Create PDF output file"""

        # Parse page layout and formatting
        if (self.bnml is not None):
            margin_attrib = self.bnml.attrib
            temp_dict = self.fill_page_dict(margin_attrib)
            self.pageAttrib.update(temp_dict)

        c = canvas.Canvas(self.outFile,pagesize = letter)
        vert_pos = self.pageAttrib['paper_size'][1] - self.pageAttrib['top_margin']

        # For each tropar
        for troparion in self.bnml.iter('troparion'):
            # Draw title if there is one
            title_elem = troparion.find('title')
            if (title_elem is not None):
                title_text = title_elem.text.strip()
                title_attrib = title_elem.attrib
                settings_from_xml = self.fill_text_dict(title_attrib)
                self.titleAttrib.update(settings_from_xml)

                c.setFillColor(self.titleAttrib['color'])

                vert_pos -= (self.titleAttrib['font_size'] + self.titleAttrib['top_margin'])

                c.setFont(self.titleAttrib['font'],self.titleAttrib['font_size'])
                c.drawCentredString(self.pageAttrib['paper_size'][0]/2,vert_pos,title_text)

            # Draw annotations
            for annotation_elem in troparion.iter('annotation'):
                # Use a copy, since there could be multiple annotations
                annotationAttribCopy = deepcopy(self.annotationAttrib)

                annotation_attrib = annotation_elem.attrib
                settings_from_xml = self.fill_text_dict(annotation_attrib)
                annotationAttribCopy.update(settings_from_xml)

                # Translate text with neume_dict if specified (for EZ fonts)
                annotation_text = annotation_elem.text.strip()
                if annotationAttribCopy.has_key('translate'):
                    annotation_text = neume_dict.translate(annotation_text)

                vert_pos -= (annotationAttribCopy['font_size'] + annotationAttribCopy['top_margin'])

                c.setFillColor(annotationAttribCopy['color'])
                c.setFont(annotationAttribCopy['font'],annotationAttribCopy['font_size'])

                # Draw text, default to centered
                if annotationAttribCopy['align'] == 'left':
                    x_pos = self.pageAttrib['left_margin']
                    c.drawString(x_pos,vert_pos,annotation_text)
                elif annotationAttribCopy['align'] == 'right':
                    x_pos = self.pageAttrib['paper_size'][0] - self.pageAttrib['right_margin']
                    c.drawRightString(x_pos,vert_pos,annotation_text)
                else:
                    x_pos = self.pageAttrib['paper_size'][0]/2
                    c.drawCentredString(x_pos,vert_pos,annotation_text)

            # Get attributes for neumes
            neume_elem = troparion.find('neumes')
            if (neume_elem is not None):
                neumesText = " ".join(neume_elem.text.strip().split())
                neume_attrib = neume_elem.attrib
                settings_from_xml = self.fill_text_dict(neume_attrib)
                self.neumeFont.update(settings_from_xml)

            # Get attributes for drop cap
            dropcap_elem = troparion.find('dropcap')
            if (dropcap_elem is not None):
                dropcap_attrib = dropcap_elem.attrib
                settings_from_xml = self.fill_text_dict(dropcap_attrib)
                self.dropCap.update(settings_from_xml)

                self.dropCap['letter'] = dropcap_elem.text.strip()

            # Get attributes for lyrics
            lyric_elem = troparion.find('lyrics')
            if (lyric_elem is not None):
                lyricsText = " ".join(lyric_elem.text.strip().split())
                lyric_attrib = lyric_elem.attrib
                settings_from_xml = self.fill_text_dict(lyric_attrib)
                self.lyricFont.update(settings_from_xml)

            # Offset for dropcap char
            if self.dropCap.has_key('letter'):
                firstLineOffset = 5 + pdfmetrics.stringWidth(self.dropCap['letter'],self.dropCap['font'],self.dropCap['font_size'])
                # Remove first letter of lyrics, since it will be in drop cap
                lyricsText = lyricsText[1:]
            else:
                firstLineOffset = 0

            lineSpacing = self.pageAttrib['line_height']

            c.setFillColor(colors.black)

            neumeChunks = neume_dict.chunkNeumes(neumesText)
            gArray = self.makeGlyphArray(neumeChunks,lyricsText)
            gArray = self.line_break2(gArray,firstLineOffset)

            # Draw Drop Cap
            if self.dropCap.has_key('letter'):
                firstNeume = gArray[0]

                c.setFillColor(self.dropCap['color'])
                c.setFont(self.dropCap['font'],self.dropCap['font_size'])

                xpos = self.pageAttrib['left_margin']
                ypos = vert_pos - (lineSpacing + self.lyricFont['top_margin'])

                c.drawString(xpos,ypos,self.dropCap['letter'])

            for ga in gArray:
                # TO DO: check if cursor has reached the end of the page
                c.setFont(self.neumeFont['font'],self.neumeFont['font_size'])
                xpos = self.pageAttrib['left_margin'] + ga.neumePos
                ypos = vert_pos - (ga.lineNum + 1)*lineSpacing
                c.drawString(xpos,ypos, ga.neumes)

                lyricOffset = self.lyricFont['top_margin']

                if (ga.lyrics):
                    ypos -= lyricOffset
                    xpos = self.pageAttrib['left_margin'] + ga.lyricPos
                    c.setFont(self.lyricFont['font'],self.lyricFont['font_size'])
                    #if (ga.lyrics[-1] == "_"):
                    #    ga.lyrics += "_"
                    c.drawString(xpos,ypos,ga.lyrics)



            
        c.showPage()
        try:
            c.save()
        except IOError:
            print "Could not save file"
            
            
    def makeGlyphArray(self,neumeChunks,lyrics = None):
        lyricArray = re.split(' ',lyrics)
        i, lPtr = 0, 0
        gArray = []
        while(i < len(neumeChunks)):
            # Grab next chunk
            nc = neumeChunks[i]
            if (neume_dict.takesLyric(nc[0])):
                # chunk needs a lyric
                if (lPtr < len(lyricArray)):
                    lyr = lyricArray[lPtr]
                else:
                    lyr = ' '
                lPtr += 1
                g = Glyph(neumes=neume_dict.translate(nc),lyrics=lyr)
                # To Do: see if lyric ends with '_' and if lyrics are
                # wider than the neume, then combine with next chunk
            else: 
                # no lyric needed
                g = Glyph(neume_dict.translate(nc))
            g.calc_width(self.neumeFont['font'], self.neumeFont['font_size'], self.lyricFont['font'], self.lyricFont['font_size'])

            gArray.append(g)
            i += 1
        return gArray

        
    def line_break2(self,glyphArray,firstLineOffset):
        """Break neumes and lyrics into lines, currently greedy
        Rework this to return a list of lines!!!!"""
        cr = Cursor(firstLineOffset,0)

        # should be able to override these params in xml
        charSpace = 2 # avg spacing between characters
        lineWidth = self.pageAttrib['line_width']

        nlines = 0
        for g in glyphArray:
            if (cr.x + g.width) >= lineWidth:
                cr.x = 0
                nlines += 1
            g.lineNum = nlines
            adjLyricPos, adjNeumePos = 0, 0
            if g.nWidth >= g.lWidth:
                # center text
                adjLyricPos = (g.width - g.lWidth) / 2.
                
            else:
                # center neume
                adjNeumePos = (g.width - g.nWidth) / 2.

            g.neumePos = cr.x + adjNeumePos
            g.lyricPos = cr.x + adjLyricPos
            cr.x += g.width + charSpace

        return glyphArray

            
    def linebreak(self,neumes,lyrics = None):
        """Break neumes and lyrics into lines"""
        cr = Cursor(0,0)
        lyricArray = re.split(' ',lyrics)
        # If lyric spans multiple neumes
        #   then see if lyric is wider than span
        #   else see if width of glypch is max of neume and lyric
        charSpace = 4 # default space between characters
        textOffset = 20 # default space lyrics appear below neumes
        #neumeArray = neume_dict.translate(neumes).split(' ')
        neumeArray = neumes.split(' ')
        neumePos = []
        lyricPos = []
        lyricIdx = 0
        for neume in neumeArray:
            #print("Neume length: " + str(pdfmetrics.stringWidth(neume,'Kassia Tsak Main',24)))
            nWidth = pdfmetrics.stringWidth(neume_dict.translate(neume),'Kassia Tsak Main',self.nFontSize)
            if nWidth > 1.0: # if it's not a gorgon or other small symbol
                # Neume might take lyric
                if lyricIdx < len(lyricArray):
                    lyr = lyricArray[lyricIdx]
                else:
                    lyr = ""
                lWidth = pdfmetrics.stringWidth(lyr,lyric_attrib['font'],lyric_attrib['font_size'])
                # Glyph width will be the max of the two if lyric isn't stretched out
                # across multiple neumes
                addLyric = False
                #if (lyr[-1] != "_") & (neume_dict.takesLyric(neume)):
                if (neume_dict.takesLyric(neume)):
                    glWidth = max(nWidth,lWidth)
                    lyricIdx += 1
                    addLyric = True
                else:
                    glWidth = nWidth
                if (glWidth + cr.x) >= self.lineWidth: # line break
                    cr.x, cr.y = 0, cr.y - self.lineHeight
                    # does it take a lyric syllable?
                    neumePos.append((cr.x,cr.y,neume_dict.translate(neume)))
                else: # no line break
                    # does it take a lyric syllable?
                    neumePos.append((cr.x,cr.y,neume_dict.translate(neume)))
                if (addLyric):
                    lyricPos.append((cr.x,cr.y-textOffset,lyr))
                cr.x += glWidth + charSpace
                
            else:
                # offsets for gorgon
                # offsets for apli
                # offset for kentima
                # offsets for omalon
                # offsets for antikenoma
                # offsets for eteron
                neumePos.append((cr.x - charSpace,cr.y,neume_dict.translate(neume)))
            
        #print neumePos
        return neumePos, lyricPos

    def fill_page_dict(self, page_dict):
        # TO DO: better error handling; value could be empty string
        for attrib_name in page_dict:
            page_dict[attrib_name] = int(page_dict[attrib_name])
        return page_dict

    def fill_text_dict(self, title_dict):
        """parse the color"""
        if title_dict.has_key('color'):
            if title_dict['color'] == "blue":
                title_dict['color'] = colors.blue
            elif re.match("#[0-9a-fA-F]{6}",title_dict['color']):
                col = [z/255. for z in hex_to_rgb(title_dict['color'])]
                title_dict['color'] = colors.Color(col[0],col[1],col[2],1)
            else:
                title_dict.pop('color')

        """parse the font"""
        if title_dict.has_key('font'):
            if not font_reader.isRegisteredFont(title_dict['font']):
                print "{} not found, using Helvetica font instead".format(title_dict['font'])
                # Helvetica is built into ReportLab, so we know it's safe
                title_dict['font'] = "Helvetica"

        """parse the font size"""
        if title_dict.has_key('font_size'):
            try:
                title_dict['font_size'] = int(title_dict['font_size'])
            except ValueError as e:
                print "Font size error: {}".format(e)
                # Get rid of xml font size, will use default later
                title_dict.pop('font_size')

        """parse the top margin"""
        if title_dict.has_key('top_margin'):
            try:
                title_dict['top_margin'] = int(title_dict['top_margin'])
            except ValueError as e:
                print "Top margin error: {}".format(e)
                # Get rid of xml font size, will use default later
                title_dict.pop('top_margin')

        return title_dict

def hex_to_rgb(x):
    x = x.lstrip('#')
    lv = len(x)
    return tuple(int(x[i:i+lv // 3], 16) for i in range(0,lv,lv // 3))

def main(argv):
    if len(argv) == 1:
        kas = Kassia(argv[0])
    elif len(argv) > 1:
        kas = Kassia(argv[0],argv[1])
    
if __name__ == "__main__":
    print "Starting up..."
    if len(sys.argv) == 1:
        print "Input XML file required"
        sys.exit(1)
    main(sys.argv[1:])
            