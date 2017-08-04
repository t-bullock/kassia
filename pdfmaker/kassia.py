import neume_dict
import font_reader
from glyphs import Glyph
from neume import Neume
from lyric import Lyric

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
        self.pageAttrib['char_spacing'] = 2

        font_reader.register_fonts()

        # Set title defaults
        self.titleAttrib = {}
        self.titleAttrib['font_family'] = 'Helvetica'
        self.titleAttrib['font_size'] = 18
        self.titleAttrib['color'] = colors.black
        self.titleAttrib['top_margin'] = 0
        self.titleAttrib['bottom_margin'] = 0
        self.titleAttrib['left_margin'] = 0
        self.titleAttrib['right_margin'] = 0
        self.titleAttrib['text'] = ''

        # Set annotation defaults
        self.annotationAttrib = {}
        self.annotationAttrib['font_family'] = 'Helvetica'
        self.annotationAttrib['font_size'] = 12
        self.annotationAttrib['color'] = colors.black
        self.annotationAttrib['align'] = 'center'
        self.annotationAttrib['top_margin'] = 0
        self.annotationAttrib['bottom_margin'] = 0
        self.annotationAttrib['left_margin'] = 0
        self.annotationAttrib['right_margin'] = 0
        self.annotationAttrib['text'] = ''

        # Set neume defaults
        self.defaultNeumeAttrib = {}
        self.defaultNeumeAttrib['font_family'] = 'Kassia Tsak Main'
        self.defaultNeumeAttrib['font_size'] = 30
        self.defaultNeumeAttrib['color'] = colors.black

        # Set dropcap defaults
        self.dropCap = {}
        self.dropCap['font_family'] = 'EZ Omega'
        self.dropCap['font_size'] = 40
        self.dropCap['color'] = colors.black
        self.dropCap['text'] = ''

        # Set lyric defaults
        self.lyricAttrib = {}
        self.lyricAttrib['font_family'] = 'Helvetica'
        self.lyricAttrib['font_size'] = 12
        self.lyricAttrib['color'] = colors.black
        self.lyricAttrib['top_margin'] = 0
        self.lyricAttrib['text'] = ''

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

        # Parse page defaults
        defaults = self.bnml.find('defaults')
        if defaults is not None:

            page_layout = defaults.find('page-layout')
            if page_layout is not None:
                lyric_offset = page_layout.find('lyric-y-offset').text
                if lyric_offset is not None:
                    self.lyricAttrib['top_margin'] = int(lyric_offset)

            neume_font_defaults = defaults.find('neume-font')
            if neume_font_defaults is not None:
                temp_dict = self.fill_text_dict(neume_font_defaults.attrib)
                self.defaultNeumeAttrib.update(temp_dict)

            lyric_font_defaults = defaults.find('lyric-font')
            if lyric_font_defaults is not None:
                temp_dict = self.fill_text_dict(lyric_font_defaults.attrib)
                self.lyricAttrib.update(temp_dict)

            dropcap_font_defaults = defaults.find('dropcap-font')
            if dropcap_font_defaults is not None:
                temp_dict = self.fill_text_dict(dropcap_font_defaults.attrib)
                self.dropCap.update(temp_dict)

        self.canvas = canvas.Canvas(self.out_file, pagesize=self.pageAttrib['paper_size'])
        self.vert_pos = self.pageAttrib['paper_size'][1] - self.pageAttrib['top_margin']

        for child_elem in self.bnml:
            if child_elem.tag == 'pagebreak':
                self.draw_newpage()

            if child_elem.tag == 'linebreak':
                self.draw_newline(self.pageAttrib['line_height'], self.lyricAttrib['top_margin'] + self.lyricAttrib['font_size'])

            # TODO: Test this
            if child_elem.tag == 'blankline':
                self.draw_blankline(self.pageAttrib['line_height'])

            if child_elem.tag == 'title':
                current_title_attrib = self.get_title_attributes(child_elem, self.titleAttrib)
                self.draw_title(current_title_attrib)

            if child_elem.tag == 'annotation':
                current_annotation_attrib = self.get_annotation_attributes(child_elem, self.annotationAttrib)
                self.draw_annotation(current_annotation_attrib)

            if child_elem.tag == 'troparion':
                neumes_list = []
                current_annotation_attrib = {}
                lyrics_list = []
                current_dropcap_attrib = {}

                for troparion_child_elem in child_elem:
                    if troparion_child_elem.tag == 'pagebreak':
                        self.draw_newpage()

                    # TODO: Test this
                    if troparion_child_elem.tag == 'linebreak':
                        self.draw_newline(self.pageAttrib['line_height'])

                    # TODO: Test this
                    if troparion_child_elem.tag == 'blankline':
                        self.draw_blankline(self.pageAttrib['line_height'])

                    if troparion_child_elem.tag == 'annotation':
                        current_annotation_attrib = self.get_annotation_attributes(troparion_child_elem, self.annotationAttrib)
                        self.draw_annotation(current_annotation_attrib)

                    if troparion_child_elem.tag == 'neumes':
                        neumeAttrib = {}
                        neumes_elem = troparion_child_elem
                        if neumes_elem is not None:
                            temp_neumes_attrib = neumes_elem.attrib
                            settings_from_xml = self.fill_text_dict(temp_neumes_attrib)
                            neumeAttrib.update(settings_from_xml)

                            neume_attrib = neumes_elem.attrib

                            for neume_text in neumes_elem.text.strip().split():
                                n = Neume(text=neume_text,
                                          font_family=neume_attrib['font_family'] if neume_attrib.has_key('font_family') else self.defaultNeumeAttrib['font_family'],
                                          font_size=neume_attrib['font_size'] if neume_attrib.has_key('font_size') else self.defaultNeumeAttrib['font_size'],
                                          color=neume_attrib['color'] if neume_attrib.has_key('color') else self.defaultNeumeAttrib['color'],
                                          )
                                neumes_list.append(n)

                    if troparion_child_elem.tag == 'lyrics':
                        lyrics_elem = troparion_child_elem
                        if lyrics_elem is not None:
                            lyrics_default_attrib = lyrics_elem.attrib
                            settings_from_xml = self.fill_text_dict(lyrics_default_attrib)
                            self.lyricAttrib.update(settings_from_xml)

                            lyric_attrib = lyrics_elem.attrib

                            for lyric_text in lyrics_elem.text.strip().split():
                                l = Lyric(text=lyric_text,
                                          font_family=lyric_attrib['font_family'] if lyric_attrib.has_key('font_family') else self.lyricAttrib['font_family'],
                                          font_size=lyric_attrib['font_size'] if lyric_attrib.has_key('font_size') else self.lyricAttrib['font_size'],
                                          color=lyric_attrib['color'] if lyric_attrib.has_key('color') else self.lyricAttrib['color'],
                                          top_margin=lyric_attrib['top_margin'] if lyric_attrib.has_key('top_margin') else self.lyricAttrib['top_margin'],
                                          )
                                lyrics_list.append(l)

                # Get attributes for drop cap
                dropcap_elem = child_elem.find('dropcap')
                first_line_offset = 0
                if dropcap_elem is not None:
                    current_dropcap_attrib = self.get_dropcap_attributes(dropcap_elem, self.dropCap)
                    first_line_offset = 5 + pdfmetrics.stringWidth(current_dropcap_attrib['text'], current_dropcap_attrib['font_family'],
                                                                   current_dropcap_attrib['font_size'])

                # Draw Drop Cap
                if current_dropcap_attrib is not None and len(lyrics_list) > 0:
                    # Pop off first letter of lyrics (since it will be in dropcap)
                    # and pass it to draw function
                    self.draw_dropcap(current_dropcap_attrib, lyrics_list[0])
                    lyrics_list[0].text = lyrics_list[0].text[1:]

                neume_chunks = neume_dict.chunk_neumes(neumes_list)
                g_array = self.make_glyph_array(neume_chunks, lyrics_list)
                line_list = self.line_break2(g_array, first_line_offset, self.pageAttrib['line_width'], self.pageAttrib['char_spacing'])
                line_list = self.line_justify(line_list, self.pageAttrib['line_width'], first_line_offset)

                line_counter = 0
                for line_of_chunks in line_list:
                    # Make sure not at end of page
                    calculated_ypos = self.vert_pos - (line_counter + 1)*self.pageAttrib['line_height']
                    if not self.is_space_for_another_line(calculated_ypos, line_of_chunks):
                        self.draw_newpage()
                        line_counter = 0

                    for ga in line_of_chunks:
                        self.canvas.setFillColor(self.defaultNeumeAttrib['color'])
                        ypos = self.vert_pos - (line_counter + 1)*self.pageAttrib['line_height']
                        xpos = self.pageAttrib['left_margin'] + ga.neumePos

                        for i, neume in enumerate(ga.neumeChunk):
                            self.canvas.setFont(neume.font_family, neume.font_size)
                            self.canvas.setFillColor(neume.color)
                            # Move over width of last neume before writing next nueme in chunk
                            # TODO: Change font kerning and remove this logic
                            if i > 0:
                                xpos += ga.neumeChunk[i-1].width

                            self.canvas.drawString(xpos, ypos, neume.text)

                        if ga.lyricsText:
                            ypos -= ga.lyricsTopMargin
                            xpos = self.pageAttrib['left_margin'] + ga.lyricPos

                            # TODO: Put this elafrom offset logic somewhere else
                            for neumeWithLyricOffset in neume_dict.neumesWithLyricOffset:
                                if neumeWithLyricOffset[0] == ga.neumeChunk[0].text:
                                    xpos += neumeWithLyricOffset[1]

                            self.canvas.setFont(ga.lyricsFontFamily, ga.lyricsFontSize)
                            self.canvas.setFillColor(ga.lyricsFontColor)
                            #if (ga.lyrics[-1] == "_"):
                            #    ga.lyrics += "_"
                            self.canvas.drawString(xpos, ypos, ga.lyricsText)

                    self.vert_pos = self.vert_pos - (line_counter + 1) * self.pageAttrib['line_height']# - current_lyric_attrib['top_margin']

                line_counter += 1

        try:
            self.canvas.save()
        except IOError:
            print "Could not save file"

    def get_title_attributes(self, title_elem, default_title_attrib):
        current_title_attrib = deepcopy(default_title_attrib)
        settings_from_xml = self.fill_text_dict(title_elem.attrib)
        current_title_attrib.update(settings_from_xml)
        current_title_attrib['text'] = title_elem.text.strip()
        return current_title_attrib

    def draw_title(self, current_title_attrib):
        self.vert_pos -= (current_title_attrib['font_size'] + current_title_attrib['top_margin'])
        self.canvas.setFillColor(current_title_attrib['color'])
        self.canvas.setFont(current_title_attrib['font_family'], current_title_attrib['font_size'])
        self.canvas.drawCentredString(self.pageAttrib['paper_size'][0]/2, self.vert_pos, current_title_attrib['text'])
        # move down by the height of the text string
        self.vert_pos -= (current_title_attrib['font_size'] + current_title_attrib['bottom_margin'])

    def get_annotation_attributes(self, annotation_elem, default_annotation_attrib):
        current_annotation_attrib = deepcopy(default_annotation_attrib)
        settings_from_xml = self.fill_text_dict(annotation_elem.attrib)
        current_annotation_attrib.update(settings_from_xml)
        # Translate text with neume_dict if specified (for EZ fonts)
        # text = annotation_elem.text.strip()
        # if 'translate' in current_annotation_attrib:
        #    text = neume_dict.translate(text)
        current_annotation_attrib['text'] = annotation_elem.text.strip()
        return current_annotation_attrib

    def draw_annotation(self, current_annotation_attrib):
        self.vert_pos -= (current_annotation_attrib['font_size'] + current_annotation_attrib['top_margin'])
        self.canvas.setFillColor(current_annotation_attrib['color'])
        self.canvas.setFont(current_annotation_attrib['font_family'], current_annotation_attrib['font_size'])

        if current_annotation_attrib['align'] == 'left':
            x_pos = self.pageAttrib['left_margin'] - current_annotation_attrib['left_margin']
            # Check for wrapping
            '''text_width = pdfmetrics.stringWidth(current_annotation_attrib['text'], current_annotation_attrib['font_family'], current_annotation_attrib['font_size'])

            for line in wrap(current_annotation_attrib['text'], self.pageAttrib['line_width'] - 50):
                self.canvas.drawString(x_pos, self.vert_pos, line)
                self.vert_pos += 15'''

            self.canvas.drawString(x_pos, self.vert_pos, current_annotation_attrib['text'])
        elif current_annotation_attrib['align'] == 'right':
            x_pos = self.pageAttrib['paper_size'][0] - self.pageAttrib['right_margin'] - current_annotation_attrib['right_margin']
            self.canvas.drawRightString(x_pos, self.vert_pos, current_annotation_attrib['text'])
        else:
            x_pos = (self.pageAttrib['paper_size'][0]/2) + current_annotation_attrib['left_margin'] - current_annotation_attrib['right_margin']
            self.canvas.drawCentredString(x_pos, self.vert_pos, current_annotation_attrib['text'])

        self.vert_pos -= (current_annotation_attrib['font_size'] + current_annotation_attrib['bottom_margin'])

    def get_dropcap_attributes(self, dropcap_elem, default_dropcap_attrib):
        current_dropcap_attrib = deepcopy(default_dropcap_attrib)
        settings_from_xml = self.fill_text_dict(dropcap_elem.attrib)
        current_dropcap_attrib.update(settings_from_xml)
        current_dropcap_attrib['text'] = dropcap_elem.text.strip()
        return current_dropcap_attrib

    def draw_dropcap(self, current_dropcap_attrib, lyric):
        xpos = self.pageAttrib['left_margin']
        ypos = self.vert_pos - (self.pageAttrib['line_height'] + lyric.top_margin)

        # If at edge of page, start new line
        if not self.is_space_for_another_line(ypos):#, lyrics_list):
            self.draw_newpage()
            ypos = self.vert_pos - (self.pageAttrib['line_height'] + lyric.top_margin)

        self.canvas.setFillColor(current_dropcap_attrib['color'])
        self.canvas.setFont(current_dropcap_attrib['font_family'], current_dropcap_attrib['font_size'])
        self.canvas.drawString(xpos, ypos, current_dropcap_attrib['text'])

    def get_lyric_attributes(self, lyric_elem, default_lyric_attrib):
        current_lyric_attrib = deepcopy(default_lyric_attrib)
        settings_from_xml = self.fill_text_dict(lyric_elem.attrib)
        current_lyric_attrib.update(settings_from_xml)
        text = " ".join(lyric_elem.text.strip().split())
        current_lyric_attrib['text'] = text
        return current_lyric_attrib

    def draw_newpage(self):
        self.canvas.showPage()
        self.vert_pos = self.pageAttrib['paper_size'][1] - self.pageAttrib['top_margin']

    def draw_newline(self, line_height, top_margin=0):
        self.vert_pos -= (line_height + top_margin)
        if not self.is_space_for_another_line(self.vert_pos):
            self.draw_newpage()

    def draw_blankline(self, line_height):
        ypos = self.vert_pos - line_height
        self.canvas.setFont(self.defaultNeumeAttrib['font_family'], self.defaultNeumeAttrib['font_size'])
        self.canvas.drawString(50, ypos, "")

        ypos -= self.lyricAttrib['top_margin']

        self.canvas.setFont(self.lyricAttrib['font_family'], self.lyricAttrib['font_size'])
        self.canvas.drawString(50, ypos, "")

        ypos -= line_height/2

        self.vert_pos = ypos

    def is_space_for_another_line(self, cursor_y_pos, line_list=[]):
        max_height = 0
        for ga in line_list:
            if ga.lyricsTopMargin > max_height:
                max_height = ga.lyricsTopMargin
        return (cursor_y_pos - max_height) > self.pageAttrib['bottom_margin']

    def make_glyph_array(self, neume_chunks, lyrics_list):
        i, l_ptr = 0, 0
        g_array = []
        while i < len(neume_chunks):
            # Grab next chunk
            nc = neume_chunks[i]
            if neume_dict.takes_lyric(nc[0]):
                # chunk needs a lyric
                if l_ptr < len(lyrics_list):
                    lyric = lyrics_list[l_ptr]
                    g = Glyph(neume_chunk=nc,
                              lyrics_text=lyric.text,
                              lyrics_font_family=lyric.font_family,
                              lyrics_size=lyric.font_size,
                              lyrics_color=lyric.color,
                              lyrics_top_margin=lyric.top_margin)
                else:
                    g = Glyph(nc)
                l_ptr += 1

                # To Do: see if lyric ends with '_' and if lyrics are
                # wider than the neume, then combine with next chunk
            else:
                # no lyric needed
                 g = Glyph(nc)

            g.calc_chunk_width()
            g_array.append(g)
            i += 1
        return g_array

    def line_break2(self, glyph_array, first_line_offset, line_width, char_spacing):
        """Break neumes and lyrics into lines, currently greedy
        Returns a list of lines"""
        cr = Cursor(first_line_offset, 0)

        g_line_list = []
        g_line = []

        for g in glyph_array:
            new_line = False
            if (cr.x + g.width + char_spacing) >= line_width:
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
            cr.x += g.width + char_spacing

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
                l_width = pdfmetrics.stringWidth(lyr, lyric_attrib['font_family'], lyric_attrib['font_size'])
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

    def line_justify(self, line_list, line_width, first_line_offset):
        """Takes a list of lines and justifies each one"""
        for i, line in enumerate(line_list):
            # Calc width of each chunk (and count how many chunks)
            total_chunk_width = 0
            for i, chunk in enumerate(line):
                total_chunk_width += chunk.width

            # Skip current line is short
            # or if last line
            if total_chunk_width < (line_width * 0.75):
                continue
            # TODO: figure out why the second part is needed here
            if (i + 1 == len(line_list) or len(line_list) == 1):
                continue

            # Subtract total from line_width (gets space remaining)
            space_remaining = (line_width - first_line_offset) - total_chunk_width
            # Divine by num of chunks
            chunk_spacing = space_remaining / i

            cr = Cursor(first_line_offset, 0)

            for chunk in line:
                adj_lyric_pos, adj_neume_pos = 0, 0
                if chunk.nWidth >= chunk.lWidth:
                    # center text
                    adj_lyric_pos = (chunk.width - chunk.lWidth) / 2.
                else:
                    # center neume
                    adj_neume_pos = (chunk.width - chunk.nWidth) / 2.

                chunk.neumePos = cr.x + adj_neume_pos
                chunk.lyricPos = cr.x + adj_lyric_pos
                #chunk.neumePos += chunk_spacing
                #chunk.lyricPos += chunk_spacing

                cr.x += chunk.width + chunk_spacing

            # After first line (dropcap), set first line offset to zero
            first_line_offset = 0

        return line_list

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

        """parse the font family"""
        if 'font_family' in title_dict:
            if not font_reader.is_registered_font(title_dict['font_family']):
                print "{} not found, using Helvetica font instead".format(title_dict['font_family'])
                # Helvetica is built into ReportLab, so we know it's safe
                title_dict['font_family'] = "Helvetica"

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
