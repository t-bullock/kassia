#!/usr/bin/python
import sys
import logging
from copy import deepcopy
from typing import Any, Dict, Iterable, List

from reportlab.lib.enums import *
from reportlab.lib.pagesizes import *
from reportlab.lib.styles import *
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from xml.etree.ElementTree import Element, ParseError, parse

import font_reader
import neume_dict
from cursor import Cursor
from dropcap import Dropcap
from enums import *
from glyphs import Glyph, GlyphLine
from lyric import Lyric
from neume import Neume
from page import Page


class Kassia:
    """Base class for package"""
    def __init__(self, input_filename, output_file="sample.pdf"):
        self.bnml = None
        self.canvas = None
        self.defaultPageAttrib = {'line_height': 72,
                                  'char_spacing': 3}
        self.page = Page()
        self.styleSheet = getSampleStyleSheet()
        self.vert_pos = None
        self.input_filename = input_filename
        self.output_file = output_file
        try:
            open(input_filename, "r")
            file_readable = True
        except IOError:
            file_readable = False
            logging.error("XML file not readable.")

        if file_readable:
            self.set_defaults()
            self.parse_file()
            self.create_pdf()

    def set_defaults(self):
        # Set page defaults
        self.defaultPageAttrib['line_width'] = self.page.width
        font_reader.register_fonts()

    def parse_file(self):
        try:
            bnml_tree = parse(self.input_filename)
            self.bnml = bnml_tree.getroot()
        except ParseError as e:
            logging.error("Failed to parse XML file: {}".format(e))

    def create_pdf(self):
        """Create PDF output file"""

        # Parse page layout and formatting
        if self.bnml is not None:
            margin_attrib = self.bnml.attrib
            temp_dict = self.fill_page_dict(margin_attrib)
            self.defaultPageAttrib.update(temp_dict)

        # Parse page defaults
        defaults = self.bnml.find('defaults')
        if defaults is not None:
            page_layout = defaults.find('page-layout')
            if page_layout is not None:
                paper_size = page_layout.find('paper-size')
                if paper_size is not None:
                    self.page.size = self.str_to_class(paper_size.text)
                    self.defaultPageAttrib['line_width'] = self.page.width

            score_styles = defaults.find('styles')
            for style in score_styles:
                style_name = style.tag
                local_attrs_from_score = self.fill_attribute_dict(style.attrib)
                if style_name in self.styleSheet:
                    self.update_paragraph_style(self.styleSheet[style_name], local_attrs_from_score)
                elif len(local_attrs_from_score) != 0:
                    new_paragraph_style = self.merge_paragraph_styles(
                        ParagraphStyle(style_name),
                        local_attrs_from_score)
                    # Special alias for paragraph, since this isn't included as a ReportLab by default
                    if style_name == 'paragraph':
                        self.styleSheet.add(new_paragraph_style, 'p')
                    else:
                        self.styleSheet.add(new_paragraph_style, style_name.lower())

        self.canvas = canvas.Canvas(self.output_file, pagesize=self.page.size)
        self.vert_pos = self.page.top

        # Set pdf title and author
        identification = self.bnml.find('identification')
        if identification is not None:
            title = identification.find('work-title')
            if title is not None:
                self.canvas.setTitle(title.text)
            author = identification.find('author')
            if author is not None:
                self.canvas.setAuthor(author.text)
            subject = identification.find('subject')
            if subject is not None:
                self.canvas.setSubject(subject.text)

        # Read main xml content
        for child_elem in self.bnml:
            if child_elem.tag == 'pagebreak':
                self.draw_newpage()

            if child_elem.tag == 'linebreak':
                # TODO: if not self.page.is_at_top_of_page(self.vert_pos):
                if self.page.is_top_of_page(self.vert_pos) is False:
                    # Default to line_height if no space is specified
                    space_amount = self.defaultPageAttrib['line_height'] +\
                                   self.styleSheet['lyrics'].spaceBefore +\
                                   self.styleSheet['lyrics'].fontSize

                    if 'space' in child_elem.attrib:
                        try:
                            space_amount = int(child_elem.attrib['space'])
                        except ValueError as e:
                            logging.warning("{} warning: {}".format('space', e))
                            # Get rid of xml margin attribute, will use default later

                    self.draw_newline(space_amount)

            if child_elem.tag == 'paragraph':
                paragraph_attrib_dict = self.fill_attribute_dict(child_elem.attrib)
                self.draw_paragraph(child_elem, paragraph_attrib_dict)

            if child_elem.tag == 'troparion':
                neumes_list = []
                lyrics_list = []
                dropcap = None
                dropcap_offset = 0

                for troparion_child_elem in child_elem:
                    if troparion_child_elem.tag == 'pagebreak':
                        self.draw_newpage()

                    # TODO: Test this
                    if troparion_child_elem.tag == 'linebreak':
                        # TODO: if not self.page.is_top_of_page(self.vert_pos):
                        if self.page.is_top_of_page(self.vert_pos) is False:
                            self.draw_newline(self.defaultPageAttrib['line_height'])

                    # TODO: Use this to draw strings before, after, or between neumes
                    # if troparion_child_elem.tag == 'string':
                    #    current_string_attrib = self.get_string_attributes(troparion_child_elem,
                    #                                                       self.defaultStringAttrib)
                    #    self.draw_paragraph(current_string_attrib)

                    if troparion_child_elem.tag == 'neumes':
                        neumes_elem = troparion_child_elem
                        attribs_from_bnml = self.fill_attribute_dict(neumes_elem.attrib)
                        neumes_style = self.merge_paragraph_styles(self.styleSheet['neumes'], attribs_from_bnml)

                        for neume_text in neumes_elem.text.strip().split():
                            neume = Neume(text=neume_text,
                                          font_family=neumes_style.fontName,
                                          font_size=neumes_style.fontSize,
                                          color=neumes_style.textColor)
                            neumes_list.append(neume)

                    if troparion_child_elem.tag == 'lyrics':
                        lyrics_elem = troparion_child_elem
                        lyrics_style = self.styleSheet['lyrics']
                        attribs_from_bnml = self.fill_attribute_dict(lyrics_elem.attrib)
                        lyrics_style = self.merge_paragraph_styles(lyrics_style, attribs_from_bnml)

                        for lyric_text in lyrics_elem.text.strip().split():
                            lyric = Lyric(text=lyric_text,
                                          font_family=lyrics_style.fontName,
                                          font_size=lyrics_style.fontSize,
                                          color=lyrics_style.textColor,
                                          top_margin=lyrics_style.spaceBefore)
                            lyrics_list.append(lyric)

                    if troparion_child_elem.tag == 'dropcap':
                        dropcap_elem = troparion_child_elem
                        dropcap_style = self.styleSheet['dropcap']
                        attribs_from_bnml = self.fill_attribute_dict(dropcap_elem.attrib)
                        dropcap_style = self.merge_paragraph_styles(dropcap_style, attribs_from_bnml)
                        dropcap_text = dropcap_elem.text.strip()

                        dropcap_offset = 5 + pdfmetrics.stringWidth(dropcap_text,
                                                                    dropcap_style.fontName,
                                                                    dropcap_style.fontSize)
                        dropcap = Dropcap(text=dropcap_text,
                                          style=dropcap_style)

                neume_chunks = neume_dict.chunk_neumes(neumes_list)
                g_array = self.make_glyph_array(neume_chunks, lyrics_list)
                line_list = self.line_break(g_array, dropcap_offset, self.defaultPageAttrib['line_width'], self.defaultPageAttrib['char_spacing'])
                line_list = self.line_justify(line_list, self.defaultPageAttrib['line_width'], dropcap_offset)

                if dropcap is not None:
                    # TODO: Replace hard-coded value with calculated glyph height
                    self.draw_dropcap(dropcap.text, dropcap.style, self.defaultPageAttrib['line_height'] + self.styleSheet['lyrics'].spaceBefore)
                    # Pop off first letter of lyrics, since it will be drawn as a dropcap
                    if len(lyrics_list) > 0:
                        lyrics_list[0].text = lyrics_list[0].text[1:]

                line_counter = 0
                for line_of_chunks in line_list:
                    # Make sure not at end of page
                    calculated_ypos = self.vert_pos - (line_counter + 1) * self.defaultPageAttrib['line_height']
                    if not self.is_space_for_another_line(calculated_ypos, line_of_chunks):
                        self.draw_newpage()
                        line_counter = 0

                    for ga in line_of_chunks:
                        self.canvas.setFillColor(self.styleSheet['neumes'].textColor)
                        ypos = self.vert_pos - (line_counter + 1) * self.defaultPageAttrib['line_height']
                        xpos = self.page.left_margin + ga.neumePos

                        for i, neume in enumerate(ga.neumeChunk):
                            self.canvas.setFont(neume.font_family, neume.font_size)
                            self.canvas.setFillColor(neume.color)
                            # Move over width of last neume before writing next neume in chunk
                            # TODO: Change font kerning and remove this logic?
                            if i > 0:
                                xpos += ga.neumeChunk[i-1].width

                            self.canvas.drawString(xpos, ypos, neume.text)

                        if ga.lyricsText:
                            self.canvas.setFillColor(self.styleSheet['lyrics'].textColor)
                            ypos -= ga.lyricsTopMargin
                            xpos = self.page.left_margin + ga.lyricPos

                            # TODO: Put this elaphron offset logic somewhere else
                            for neumeWithLyricOffset in neume_dict.neumesWithLyricOffset:
                                if neumeWithLyricOffset[0] == ga.neumeChunk[0].text:
                                    xpos += neumeWithLyricOffset[1]

                            self.canvas.setFont(ga.lyricsFontFamily, ga.lyricsFontSize)
                            self.canvas.setFillColor(ga.lyricsFontColor)
                            #if (ga.lyrics[-1] == "_"):
                            #    ga.lyrics += "_"
                            self.canvas.drawString(xpos, ypos, ga.lyricsText)

                    self.vert_pos -= (line_counter + 1) * self.defaultPageAttrib['line_height']# - current_lyric_attrib['top_margin']

                line_counter += 1

        try:
            self.canvas.save()
        except IOError:
            logging.error("Could not save XML file.")

    @staticmethod
    def get_embedded_paragraph_text(para_tag_attribs: Element, default_style: ParagraphStyle) -> str:
        """Merges Returns a text string with pre-formatted text.

        :param para_tag_attribs: The current paragraph tag style attributes.
        :param default_style: The default paragraph style.
        :return: A string of pre-formatted text.
        """
        embedded_args = ""
        for embedded_font_attrib in para_tag_attribs:
            temp_font_family = default_style.fontName
            temp_font_size = default_style.fontSize
            temp_font_color = default_style.textColor
            if embedded_font_attrib.attrib is not None:
                if 'font_family' in embedded_font_attrib.attrib:
                    temp_font_family = embedded_font_attrib.attrib['font_family']
                if 'font_size' in embedded_font_attrib.attrib:
                    temp_font_size = embedded_font_attrib.attrib['font_size']
                if 'color' in embedded_font_attrib.attrib:
                    temp_font_color = embedded_font_attrib.attrib['color']
            embedded_args += '<font face="{0}" size="{1}" color="{2}">'.format(temp_font_family,
                                                                               temp_font_size,
                                                                               temp_font_color) +\
                             embedded_font_attrib.text.strip() + '</font>' + embedded_font_attrib.tail

        return para_tag_attribs.text.strip() + embedded_args

    def draw_paragraph(self, bnml_elem, current_attribs: Dict[str, Any], ending_cursor_pos: int = Line.NEXT):
        """Draws a paragraph of text with the passed text attributes.

        :param bnml_elem: The bnml paragraph element.
        :param current_attribs: A dictionary of style attributes from a Kassia bnml file.
        :param ending_cursor_pos: indicates where the cursor should be after
                             drawing the paragraph. Values are LN_RIGHT (to the
                             right), LN_NEXT (to the beginning of the next line),
                             and LN_BELOW (below the current paragraph).
        """
        if len(current_attribs) is 0:
            paragraph_style = self.styleSheet['paragraph']
        elif current_attribs['style'] is not None:
            paragraph_style = self.styleSheet[current_attribs['style']]
        else:
            paragraph_style = ParagraphStyle('defaults')

        paragraph_style = self.merge_paragraph_styles(paragraph_style, current_attribs)
        paragraph_text = self.get_embedded_paragraph_text(bnml_elem, paragraph_style)
        paragraph = Paragraph(paragraph_text, paragraph_style)

        __, paragraph_height = paragraph.wrap(self.defaultPageAttrib['line_width'], self.page.height)
        if (self.vert_pos - paragraph_height) <= self.page.bottom_margin:
            self.draw_newpage()

        # self.canvas.saveState()
        paragraph.drawOn(self.canvas, self.page.left_margin, self.vert_pos)
        # self.canvas.restoreState()

        if 'ending_cursor_pos' in current_attribs:
            ending_cursor_pos = current_attribs['ending_cursor_pos']

        if ending_cursor_pos == Line.RIGHT:
            return
        if ending_cursor_pos == Line.NEXT:
            self.vert_pos -= (paragraph_style.leading + paragraph_style.spaceAfter)
        elif ending_cursor_pos == Line.BELOW:
            self.vert_pos -= (paragraph_height + paragraph_style.leading + paragraph_style.spaceAfter)

    @staticmethod
    def merge_paragraph_styles(default_style: ParagraphStyle, bnml_style: Dict[str, Any]) -> ParagraphStyle:
        """Merges ReportLab ParagraphStyle attributes with Kassia bnml attributes and returns the new style

        :param default_style: The default ParagraphStyle (a ReportLab class).
        :param bnml_style: A dictionary of styles read a Kassia bnml file. The bnml_style needs to have ben already run
                           through fill_dict_attributes().
        :return new_style: A new ParagraphStyle of default_style with attributes updated by bnml_style
        """
        new_style = deepcopy(default_style)
        if 'font_family' in bnml_style:
            new_style.fontName = bnml_style['font_family']
        if 'font_size' in bnml_style:
            new_style.fontSize = bnml_style['font_size']
        if 'color' in bnml_style:
            new_style.textColor = bnml_style['color']
        if 'bgcolor' in bnml_style:
            new_style.backColor = bnml_style['bgcolor']
        if 'align' in bnml_style:
            new_style.alignment = bnml_style['align']
        if 'first_line_indent' in bnml_style:
            new_style.firstLineIndent = bnml_style['first_line_indent']
        if 'auto-leading' in bnml_style:
            new_style.autoLeading = bnml_style['auto-leading']
        if 'leading' in bnml_style:
            new_style.leading = bnml_style['leading']
        if 'left_indent' in bnml_style:
            new_style.leftIndent = bnml_style['left_indent']
        if 'right_indent' in bnml_style:
            new_style.rightIndent = bnml_style['right_indent']
        if 'space_before' in bnml_style:
            new_style.spaceBefore = bnml_style['space_before']
        if 'space_after' in bnml_style:
            new_style.spaceAfter = bnml_style['space_after']
        return new_style

    @staticmethod
    def update_paragraph_style(default_style: ParagraphStyle, bnml_style: Dict[str, Any]):
        """Replaces ReportLab ParagraphStyle attributes with Kassia bnml attributes.

        :param default_style: The default ParagraphStyle (a ReportLab class).
        :param bnml_style: A dictionary of styles read a Kassia bnml file. The bnml_style needs to have ben already run
                           through fill_dict_attributes().
        """
        if 'font_family' in bnml_style:
            default_style.fontName = bnml_style['font_family']
        if 'font_size' in bnml_style:
            default_style.fontSize = bnml_style['font_size']
        if 'color' in bnml_style:
            default_style.textColor = bnml_style['color']
        if 'bgcolor' in bnml_style:
            default_style.backColor = bnml_style['bgcolor']
        if 'align' in bnml_style:
            default_style.alignment = bnml_style['align']
        if 'first_line_indent' in bnml_style:
            default_style.firstLineIndent = bnml_style['first_line_indent']
        if 'auto-leading' in bnml_style:
            default_style.autoLeading = bnml_style['auto-leading']
        if 'leading' in bnml_style:
            default_style.leading = bnml_style['leading']
        if 'left_indent' in bnml_style:
            default_style.leftIndent = bnml_style['left_indent']
        if 'right_indent' in bnml_style:
            default_style.rightIndent = bnml_style['right_indent']
        if 'space_before' in bnml_style:
            default_style.spaceBefore = bnml_style['space_before']
        if 'space_after' in bnml_style:
            default_style.spaceAfter = bnml_style['space_after']
        return default_style

    def draw_dropcap(self, text: str, style_attrib: ParagraphStyle, glyph_height: int):
        """Draws a dropcap with passed text and style.
        :param text: The text to draw.
        :param style_attrib: The style to draw the text in.
        :param glyph_height: The height of a glyph (neume chunk + lyrics)
        """
        xpos = self.page.left_margin
        ypos = self.vert_pos - glyph_height

        if not self.is_space_for_another_line(ypos):
            self.draw_newpage()
            ypos = self.vert_pos - self.defaultPageAttrib['line_height']

        self.canvas.setFillColor(style_attrib.textColor)
        self.canvas.setFont(style_attrib.fontName, style_attrib.fontSize)
        self.canvas.drawString(xpos, ypos, text)

    def get_lyric_attributes(self, lyric_elem, default_lyric_attrib):
        current_lyric_attrib = deepcopy(default_lyric_attrib)
        settings_from_xml = self.fill_attribute_dict(lyric_elem.attrib)
        current_lyric_attrib.update(settings_from_xml)
        text = " ".join(lyric_elem.text.strip().split())
        current_lyric_attrib['text'] = text
        return current_lyric_attrib

    def draw_newpage(self):
        self.canvas.showPage()
        self.vert_pos = self.page.top
        self.draw_header("", style=self.styleSheet['header'])
        self.draw_footer("", style=self.styleSheet['footer'])

    def draw_newline(self, line_height, top_margin=0):
        self.vert_pos -= (line_height + top_margin)
        if not self.is_space_for_another_line(self.vert_pos):
            self.draw_newpage()

    def draw_header(self, text: str, style: ParagraphStyle, border: bool = False):
        """Draws the header onto the canvas with the given text and style.
        :param text: Text to draw in header.
        :param style: Style to draw text in.
        :param border: Whether to draw a border or not.
        """
        if border:
            self.canvas.setStrokeColorRGB(0, 0, 0)
            self.canvas.setLineWidth(0.5)
            self.canvas.line(
                self.page.left,
                self.page.bottom,
                self.page.right,
                self.page.bottom)

        self.canvas.setFont(self.styleSheet['header'].fontName, self.styleSheet['header'].fontSize)

        # Vertically centered within top margin
        y_pos = self.page.top_margin / 2

        # TODO: Support margins on string?
        if style.alignment == TA_LEFT:
            x_pos = self.page.left
            self.canvas.drawString(x_pos, y_pos, text)
        elif style.alignment == TA_RIGHT:
            x_pos = self.page.right
            self.canvas.drawRightString(x_pos, y_pos, text)
        elif style.alignment == TA_CENTER:
            x_pos = self.page.center
            self.canvas.drawCentredString(x_pos, y_pos, text)

    def draw_footer(self, text, style: ParagraphStyle, page_number: bool = True, border: bool = False):
        """Draws the header onto the canvas with the given text and style. Defaults to drawing page number.
        :param text: Text to draw in header.
        :param style: Style to draw text in.
        :param page_number: Whether to draw page number.
        :param border: Whether to draw a border or not.
        """
        if border:
            self.canvas.setStrokeColorRGB(0, 0, 0)
            self.canvas.setLineWidth(0.5)
            self.canvas.line(
                self.page.left,
                self.page.bottom,
                self.page.right,
                self.page.bottom)

        self.canvas.setFont(style.fontName, style.fontSize)

        if page_number:
            footer_text = str(self.canvas.getPageNumber())
        else:
            footer_text = text

        y_pos = self.defaultPageAttrib['bottom_margin'] / 2

        # TODO: Support margins on string?
        if style.alignment == TA_LEFT:
            x_pos = self.page.left
            self.canvas.drawString(x_pos, y_pos, footer_text)
        elif style.alignment == TA_RIGHT:
            x_pos = self.page.right
            self.canvas.drawRightString(x_pos, y_pos, footer_text)
        elif style.alignment == TA_CENTER:
            x_pos = self.page.center
            self.canvas.drawCentredString(x_pos, y_pos, footer_text)

    # TODO: Only check for lyricTopMargin? Do we know the proposed lyricPos?
    def is_space_for_another_line(self, cursor_y_pos: int, line_list=None):
        """Returns whether there is space for a line of neumes and lyrics."""
        if line_list is None:
            line_list = []
        max_height = 0
        for ga in line_list:
            if ga.lyricsTopMargin > max_height:
                max_height = ga.lyricsTopMargin
        return not self.page.is_bottom_of_page(cursor_y_pos - max_height)

    @staticmethod
    def make_glyph_array(neume_chunk_list: List[Iterable], lyrics_list: List[Lyric]) -> GlyphLine:
        """Takes a list of neumes and a list of lyrics and combines them into a single glyph list.
        :param neume_chunk_list: A list of neume chunks.
        :param lyrics_list: A list of lyrics.
        :return glyph_array: A list of glyphs.
        """
        i, l_ptr = 0, 0
        glyph_array = []
        while i < len(neume_chunk_list):
            # Grab next chunk
            neume_chunk = neume_chunk_list[i]

            # If any neumes within chunk take lyrics
            neume_takes_lyric = False
            for neume in neume_chunk:
                if neume_dict.takes_lyric(neume):
                    neume_takes_lyric = True

            if neume_takes_lyric:
                # Chunk needs a lyric
                if l_ptr < len(lyrics_list):
                    lyric = lyrics_list[l_ptr]
                    glyph = Glyph(neume_chunk=neume_chunk,
                                  lyrics_text=lyric.text,
                                  lyrics_font_family=lyric.font_family,
                                  lyrics_size=lyric.font_size,
                                  lyrics_color=lyric.color,
                                  lyrics_top_margin=lyric.top_margin)
                else:
                    glyph = Glyph(neume_chunk)
                l_ptr += 1

                # Todo: see if lyric ends with '_' and if lyrics are
                # wider than the neume, then combine with next chunk
            else:
                # no lyric needed
                glyph = Glyph(neume_chunk)

            glyph.calc_chunk_width()
            glyph_array.append(glyph)
            i += 1
        return glyph_array

    @staticmethod
    def line_break(glyph_array: GlyphLine, first_line_offset: int, line_width: int, char_spacing: int)\
            -> List[Iterable]:
        """Break continuous list of glyphs into lines- currently greedy.
        :param glyph_array: A list of glyphs.
        :param first_line_offset: Where to start first line of neumes (usually due to dropcap).
        :param line_width: Width of a line (usually page width minus margins).
        :param char_spacing: Space between each neume group, from bnml.
        :return g_line_list: A list of lines of Glyphs.
        """
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

    @staticmethod
    def line_justify(line_list: List, max_line_width: int, first_line_x_offset: int) -> List:
        """Justify a line of neumes by adjusting space between each neume group.
        :param line_list: A list of neume groups.
        :param max_line_width: Max width a line of neumes can take up.
        :param first_line_x_offset: Offset of first line, usually from a dropcap.
        :return line_list: The modified line_list with neume spacing adjusted.
        """
        for line_index, line in enumerate(line_list):
            # Calc width of each chunk (and count how many chunks)
            total_chunk_width = 0
            for chunk in line:
                total_chunk_width += chunk.width

            # Skip if last line
            if line_index + 1 == len(line_list):
                continue

            # Subtract total from line_width (gets space remaining)
            space_remaining = (max_line_width - first_line_x_offset) - total_chunk_width
            # Divide by number of chunks in line
            chunk_spacing = space_remaining / len(line)

            cr = Cursor(first_line_x_offset, 0)

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
            first_line_x_offset = 0

        return line_list

    @staticmethod
    def str_to_class(class_name_str):
        class_obj = None
        try:
            class_obj = getattr(sys.modules[__name__], class_name_str)
        except ValueError as e:
            logging.warning("Could not convert class {}: {}".format(class_name_str, e))
        return class_obj

    @staticmethod
    def str_to_align(align_str):
        align = TA_LEFT
        if align_str == 'right':
            align = TA_RIGHT
        elif align_str == 'center':
            align = TA_CENTER
        elif align_str == 'justify':
            align = TA_JUSTIFY
        elif align_str != 'left':
            logging.warning("Alignment {} is not a proper value".format(align_str))
        return align

    @staticmethod
    def fill_page_dict(page_dict):
        # TODO: better error handling; value could be empty string
        for attrib_name in page_dict:
            try:
                page_dict[attrib_name] = int(page_dict[attrib_name])
            except ValueError as e:
                logging.warning("{} warning: {}".format(attrib_name, e))
                page_dict.pop(attrib_name)
        return page_dict

    def fill_attribute_dict(self, attribute_dict: Dict[str, str]) -> Dict[str, Any]:
        if 'align' in attribute_dict:
            attribute_dict['align'] = self.str_to_align(attribute_dict['align'])

        """parse the font family"""
        if 'font_family' in attribute_dict:
            if not font_reader.is_registered_font(attribute_dict['font_family']):
                logging.warning("{} not found, using Helvetica instead".format(attribute_dict['font_family']))
                # Helvetica is built into ReportLab, so we know it's safe
                attribute_dict['font_family'] = "Helvetica"

        """parse the font attributes"""
        for font_attr in ['font_size', 'first_line_indent', 'left_indent', 'right_indent', 'leading', 'space_before',
                          'space_after', 'ending_cursor_pos']:
            if font_attr in attribute_dict:
                try:
                    attribute_dict[font_attr] = int(attribute_dict[font_attr])
                except ValueError as e:
                    logging.warning("{} warning: {}".format(font_attr, e))
                    # Get rid of xml font attribute, will use default later
                    attribute_dict.pop(font_attr)

        """parse the margins"""
        for margin_attr in ['top_margin', 'bottom_margin', 'left_margin', 'right_margin']:
            if margin_attr in attribute_dict:
                try:
                    attribute_dict[margin_attr] = int(attribute_dict[margin_attr])
                except ValueError as e:
                    logging.warning("{} warning: {}".format(margin_attr, e))
                    # Get rid of xml margin attribute, will use default later
                    attribute_dict.pop(margin_attr)
        return attribute_dict


def main(argv):
    if len(argv) == 1:
        Kassia(argv[0])
    elif len(argv) > 1:
        Kassia(argv[0], argv[1])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    if len(sys.argv) == 1:
        logging.error("Input XML file required.")
        sys.exit(1)
    main(sys.argv[1:])
