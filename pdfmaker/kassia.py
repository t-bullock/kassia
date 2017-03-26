import neume_dict
import font_reader
from glyphs import Glyph
from neume import Neume

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

import sys
import xml.etree.ElementTree as ET
import re
from copy import deepcopy


class Cursor:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class Kassia:
    """Base class for package"""
    def __init__(self, file_name, out_file="out.pdf"):
        self.file_name = file_name  # input file
        self.out_file = out_file  # output file
        try:
            open(file_name, "r")
            file_readable = True
        except IOError:
            file_readable = False
            print "Not readable"
        
        if file_readable:
            self.set_defaults()
            self.parse_file()
            self.create_pdf()

    def set_defaults(self):
        # Set page defaults
        self.pageAttrib = {}
        self.pageAttrib['paper_size'] = letter
        self.pageAttrib['top_margin'] = 72
        self.pageAttrib['bottom_margin'] = 72
        self.pageAttrib['left_margin'] = 72
        self.pageAttrib['right_margin'] = 72
        self.pageAttrib['line_height'] = 72
        self.pageAttrib['line_width'] = self.pageAttrib['paper_size'][0] - (self.pageAttrib['left_margin'] + self.pageAttrib['right_margin'])

        font_reader.register_fonts()

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
        self.neumeFont['font_size'] = 30
        self.neumeFont['color'] = colors.black

        # Set dropcap defaults
        self.dropCap = {}
        #self.dropCap['font'] = 'EZOmega'
        #self.dropCap['font_size'] = 40

        # Set lyric defaults
        self.lyricFont = {}
        self.lyricFont['font'] = 'Helvetica'
        self.lyricFont['font_size'] = 12
        self.lyricFont['color'] = colors.black
        self.lyricFont['top_margin'] = 0

    def parse_file(self):
        try:
            bnml_tree = ET.parse(self.file_name)
            bnml = bnml_tree.getroot()
            self.bnml = bnml

        except ET.ParseError:
            print "Failed to parse XML file"

    def create_pdf(self):
        """Create PDF output file"""

        # Parse page layout and formatting
        if self.bnml is not None:
            margin_attrib = self.bnml.attrib
            temp_dict = self.fill_page_dict(margin_attrib)
            self.pageAttrib.update(temp_dict)

        c = canvas.Canvas(self.out_file, pagesize=letter)
        vert_pos = self.pageAttrib['paper_size'][1] - self.pageAttrib['top_margin']

        # For each troparion
        for troparion in self.bnml.iter('troparion'):
            # Draw title if there is one
            title_elem = troparion.find('title')
            if title_elem is not None:
                title_text = title_elem.text.strip()
                title_attrib = title_elem.attrib
                settings_from_xml = self.fill_text_dict(title_attrib)
                self.titleAttrib.update(settings_from_xml)

                c.setFillColor(self.titleAttrib['color'])

                vert_pos -= (self.titleAttrib['font_size'] + self.titleAttrib['top_margin'])

                c.setFont(self.titleAttrib['font'], self.titleAttrib['font_size'])
                c.drawCentredString(self.pageAttrib['paper_size'][0]/2, vert_pos, title_text)

            # Draw annotations
            for annotation_elem in troparion.iter('annotation'):
                # Use a copy, since there could be multiple annotations
                annotation_attrib_copy = deepcopy(self.annotationAttrib)

                annotation_attrib = annotation_elem.attrib
                settings_from_xml = self.fill_text_dict(annotation_attrib)
                annotation_attrib_copy.update(settings_from_xml)

                # Translate text with neume_dict if specified (for EZ fonts)
                annotation_text = annotation_elem.text.strip()
                if 'translate' in annotation_attrib_copy:
                    annotation_text = neume_dict.translate(annotation_text)

                vert_pos -= (annotation_attrib_copy['font_size'] + annotation_attrib_copy['top_margin'])

                c.setFillColor(annotation_attrib_copy['color'])
                c.setFont(annotation_attrib_copy['font'], annotation_attrib_copy['font_size'])

                # Draw text, default to centered
                if annotation_attrib_copy['align'] == 'left':
                    x_pos = self.pageAttrib['left_margin']
                    c.drawString(x_pos, vert_pos, annotation_text)
                elif annotation_attrib_copy['align'] == 'right':
                    x_pos = self.pageAttrib['paper_size'][0] - self.pageAttrib['right_margin']
                    c.drawRightString(x_pos, vert_pos, annotation_text)
                else:
                    x_pos = self.pageAttrib['paper_size'][0]/2
                    c.drawCentredString(x_pos, vert_pos, annotation_text)

            neumes_list = []

            # Get attributes for neumes
            for neumes_elem in troparion.iter('neumes'):
                if neumes_elem is not None:
                    neumes_default_attrib = neumes_elem.attrib
                    settings_from_xml = self.fill_text_dict(neumes_default_attrib)
                    self.neumeFont.update(settings_from_xml)

                    neume_attrib = neumes_elem.attrib

                    for neume_text in neumes_elem.text.strip().split():
                        n = Neume(text=neume_text,
                                      font_family=neume_attrib['font'] if neume_attrib.has_key('font') else self.neumeFont['font'],
                                      font_size=neume_attrib['font_size'] if neume_attrib.has_key('font_size') else self.neumeFont['font_size'],
                                      color=neume_attrib['color'] if neume_attrib.has_key('color') else self.neumeFont['color'],
                                      )
                            neumes_list.append(n)

            # Get attributes for drop cap
            dropcap_elem = troparion.find('dropcap')
            if dropcap_elem is not None:
                dropcap_attrib = dropcap_elem.attrib
                settings_from_xml = self.fill_text_dict(dropcap_attrib)
                self.dropCap.update(settings_from_xml)

                self.dropCap['letter'] = dropcap_elem.text.strip()

            # Get attributes for lyrics
            lyric_elem = troparion.find('lyrics')
            if lyric_elem is not None:
                lyrics_text = " ".join(lyric_elem.text.strip().split())
                lyric_attrib = lyric_elem.attrib
                settings_from_xml = self.fill_text_dict(lyric_attrib)
                self.lyricFont.update(settings_from_xml)

            # Offset for dropcap char
            if 'letter' in self.dropCap:
                first_line_offset = 5 + pdfmetrics.stringWidth(self.dropCap['letter'], self.dropCap['font'], self.dropCap['font_size'])
                # Remove first letter of lyrics, since it will be in drop cap
                lyrics_text = lyrics_text[1:]
            else:
                first_line_offset = 0

            line_spacing = self.pageAttrib['line_height']

            neume_chunks = neume_dict.chunk_neumes(neumes_list)
            g_array = self.make_glyph_array(neume_chunks, lyrics_text)
            line_list = self.line_break2(g_array, first_line_offset)

            # Draw Drop Cap
            if 'letter' in self.dropCap:
                calculated_ypos = vert_pos - (line_spacing + self.lyricFont['top_margin'])
                if not self.is_space_for_another_line(calculated_ypos):
                    c.showPage()
                    vert_pos = self.pageAttrib['paper_size'][1] - self.pageAttrib['top_margin']

                c.setFillColor(self.dropCap['color'])
                c.setFont(self.dropCap['font'], self.dropCap['font_size'])

                xpos = self.pageAttrib['left_margin']
                ypos = vert_pos - (line_spacing + self.lyricFont['top_margin'])

                c.drawString(xpos, ypos, self.dropCap['letter'])

            line_counter = 0
            for line_of_chunks in line_list:

                # Make sure not at end of page
                calculated_ypos = vert_pos - (line_counter + 1)*line_spacing
                if not self.is_space_for_another_line(calculated_ypos):
                    c.showPage()
                    vert_pos = self.pageAttrib['paper_size'][1] - self.pageAttrib['top_margin']
                    line_counter = 0

                for ga in line_of_chunks:
                c.setFillColor(self.neumeFont['color'])
                    ypos = vert_pos - (line_counter + 1)*line_spacing
                xpos = self.pageAttrib['left_margin'] + ga.neumePos

                for i, neume in enumerate(ga.neumeChunk):
                    c.setFont(neume.font_family, neume.font_size)
                    c.setFillColor(neume.color)
                    # Move over width of last neume before writing next nueme in chunk
                        # TODO: Change font kerning and remove this logic
                    if i > 0:
                        xpos += ga.neumeChunk[i-1].width

                        c.drawString(xpos, ypos, neume.text)

                lyric_offset = self.lyricFont['top_margin']

                if ga.lyrics:
                    ypos -= lyric_offset
                    xpos = self.pageAttrib['left_margin'] + ga.lyricPos

                    # TODO: Put this elafrom offset logic somewhere else
                    for neumeWithLyricOffset in neume_dict.neumesWithLyricOffset:
                        if neumeWithLyricOffset[0] == ga.neumeChunk[0].text:
                            xpos += neumeWithLyricOffset[1]

                    c.setFont(self.lyricFont['font'], self.lyricFont['font_size'])
                    c.setFillColor(self.lyricFont['color'])
                    #if (ga.lyrics[-1] == "_"):
                    #    ga.lyrics += "_"
                    c.drawString(xpos, ypos, ga.lyrics)

                vert_pos = vert_pos - (line_counter + 1) * line_spacing - lyric_offset

            line_counter += 1

        try:
            c.save()
        except IOError:
            print "Could not save file"

    def is_space_for_another_line(self, cursor_vpos):
        return (cursor_vpos - self.lyricFont['top_margin']) > self.pageAttrib['bottom_margin']

    def make_glyph_array(self, neume_chunks, lyrics=None):
        lyric_array = re.split(' ', lyrics)
        i, l_ptr = 0, 0
        g_array = []
        while i < len(neume_chunks):
            # Grab next chunk
            nc = neume_chunks[i]
            if neume_dict.takes_lyric(nc[0]):
                # chunk needs a lyric
                if l_ptr < len(lyric_array):
                    lyr = lyric_array[l_ptr]
                else:
                    lyr = ' '
                l_ptr += 1
                g = Glyph(neume_chunk=nc, lyrics=lyr)
                # To Do: see if lyric ends with '_' and if lyrics are
                # wider than the neume, then combine with next chunk
            else: 
                # no lyric needed
                 g = Glyph(nc)
            g.calc_chunk_width(self.lyricFont['font'], self.lyricFont['font_size'])

            g_array.append(g)
            i += 1
        return g_array

    def line_break2(self, glyph_array, first_line_offset):
        """Break neumes and lyrics into lines, currently greedy
        Returns a list of lines"""
        cr = Cursor(first_line_offset, 0)

        # should be able to override these params in xml
        char_space = 2  # avg spacing between characters
        line_width = self.pageAttrib['line_width']

        g_line_list = []
        g_line = []

        for g in glyph_array:
            new_line = False
            if (cr.x + g.width) >= line_width:
                cr.x = 0
                new_line = True

            adj_lyric_pos, adj_neume_pos = 0, 0
            if g.nWidth >= g.lWidth:
                # center text
                adj_lyric_pos = (g.width - g.lWidth) / 2.
                
            else:
                # center neume
                adj_neume_pos = (g.width - g.nWidth) / 2.

            g.neumePos = cr.x + adj_neume_pos
            g.lyricPos = cr.x + adj_lyric_pos
            cr.x += g.width + char_space

            if new_line:
                g_line_list.append(g_line)
                g_line = []
            g_line.append(g)

        # One more time to grab the last line
        g_line_list.append(g_line)

        return g_line_list

    def linebreak(self, neumes, lyrics=None):
        """Break neumes and lyrics into lines"""
        cr = Cursor(0,0)
        lyric_array = re.split(' ', lyrics)
        # If lyric spans multiple neumes
        #   then see if lyric is wider than span
        #   else see if width of glypch is max of neume and lyric
        char_space = 4 # default space between characters
        text_offset = 20 # default space lyrics appear below neumes
        # neume_array = neume_dict.translate(neumes).split(' ')
        neume_array = neumes.split(' ')
        neume_pos = []
        lyric_pos = []
        lyric_index = 0
        for neume in neume_array:
            # print("Neume length: " + str(pdfmetrics.stringWidth(neume,'Kassia Tsak Main',24)))
            n_width = pdfmetrics.stringWidth(neume_dict.translate(neume), 'Kassia Tsak Main', self.nFontSize)
            if n_width > 1.0: # if it's not a gorgon or other small symbol
                # Neume might take lyric
                if lyric_index < len(lyric_array):
                    lyr = lyric_array[lyric_index]
                else:
                    lyr = ""
                l_width = pdfmetrics.stringWidth(lyr, lyric_attrib['font'], lyric_attrib['font_size'])
                # Glyph width will be the max of the two if lyric isn't stretched out
                # across multiple neumes
                add_lyric = False
                # if (lyr[-1] != "_") & (neume_dict.takesLyric(neume)):
                if neume_dict.takes_lyric(neume):
                    gl_width = max(n_width, l_width)
                    lyric_index += 1
                    add_lyric = True
                else:
                    gl_width = n_width
                if (gl_width + cr.x) >= self.lineWidth:  # line break
                    cr.x, cr.y = 0, cr.y - self.lineHeight
                    # does it take a lyric syllable?
                    neume_pos.append((cr.x, cr.y, neume_dict.translate(neume)))
                else:  # no line break
                    # does it take a lyric syllable?
                    neume_pos.append((cr.x, cr.y, neume_dict.translate(neume)))
                if add_lyric:
                    lyric_pos.append((cr.x, cr.y-text_offset, lyr))
                cr.x += gl_width + char_space
                
            else:
                # offsets for gorgon
                # offsets for apli
                # offset for kentima
                # offsets for omalon
                # offsets for antikenoma
                # offsets for eteron
                neume_pos.append((cr.x - char_space, cr.y, neume_dict.translate(neume)))

        return neume_pos, lyric_pos

    @staticmethod
    def fill_page_dict(page_dict):
        # TODO: better error handling; value could be empty string
        for attrib_name in page_dict:
            page_dict[attrib_name] = int(page_dict[attrib_name])
        return page_dict

    @staticmethod
    def fill_text_dict(title_dict):
        """parse the color"""
        if 'color' in title_dict:
            if title_dict['color'] == "blue":
                title_dict['color'] = colors.blue
            elif re.match("#[0-9a-fA-F]{6}", title_dict['color']):
                col = [z/255. for z in hex_to_rgb(title_dict['color'])]
                title_dict['color'] = colors.Color(col[0], col[1], col[2], 1)
            else:
                title_dict.pop('color')

        """parse the font"""
        if 'font' in title_dict:
            if not font_reader.is_registered_font(title_dict['font']):
                print "{} not found, using Helvetica font instead".format(title_dict['font'])
                # Helvetica is built into ReportLab, so we know it's safe
                title_dict['font'] = "Helvetica"

        """parse the font size"""
        if 'font_size' in title_dict:
            try:
                title_dict['font_size'] = int(title_dict['font_size'])
            except ValueError as e:
                print "Font size error: {}".format(e)
                # Get rid of xml font size, will use default later
                title_dict.pop('font_size')

        """parse the margins"""
        for margin_attr in ['top_margin', 'bottom_margin', 'left_margin', 'right_margin']:
            if margin_attr in title_dict:
            try:
                    title_dict[margin_attr] = int(title_dict[margin_attr])
            except ValueError as e:
                    print "{} error: {}".format(margin_attr,e)
                # Get rid of xml font size, will use default later
                    title_dict.pop(margin_attr)
        return title_dict


def hex_to_rgb(x):
    x = x.lstrip('#')
    lv = len(x)
    return tuple(int(x[i:i+lv // 3], 16) for i in range(0, lv, lv // 3))


def main(argv):
    if len(argv) == 1:
        Kassia(argv[0])
    elif len(argv) > 1:
        Kassia(argv[0], argv[1])
    
if __name__ == "__main__":
    # print "Starting up..."
    if len(sys.argv) == 1:
        print "Input XML file required"
        sys.exit(1)
    main(sys.argv[1:])
