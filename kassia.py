#!/usr/bin/python
import sys
import logging
from copy import deepcopy
from typing import Any, Dict, List

from reportlab.lib.enums import *
from reportlab.lib.styles import *
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer
from xml.etree.ElementTree import Element, ParseError, parse

import font_reader
import neume_dict
from cursor import Cursor
from drop_cap import Dropcap
from enums import *
from glyph_line import GlyphLine
from glyphs import Glyph
from lyric import Lyric
from neume import Neume
from neume_chunk import NeumeChunk
from page import Page


class Kassia:
    """Base class for package"""

    def __init__(self, input_filename, output_file="sample.pdf"):
        self.bnml = None
        self.doc = None  # SimpleDocTemplate()
        self.canvas = None
        self.page = Page()
        self.story = []
        self.styleSheet = getSampleStyleSheet()
        self.init_styles()
        self.input_filename = input_filename
        try:
            open(input_filename, "r")
            file_readable = True
        except IOError:
            file_readable = False
            logging.error("XML file not readable.")

        if file_readable:
            font_reader.register_fonts()
            self.parse_file()
            self.build_document(output_file)
            self.create_pdf()

    def parse_file(self):
        try:
            bnml_tree = parse(self.input_filename)
            self.bnml = bnml_tree.getroot()
        except ParseError as e:
            logging.error("Failed to parse XML file: {}".format(e))

    def init_styles(self):
        """Add specific Kassia styles to stylesheet.
        """
        self.styleSheet.add(ParagraphStyle(name='Neumes',
                                           fontName="KA New Stathis Main",
                                           fontSize=30,
                                           leading=70,
                                           wordSpace=4),
                            "neum")
        self.styleSheet.add(ParagraphStyle(name='Lyrics',
                                           fontName="Alegreya-Medium",
                                           fontSize=14,
                                           leading=12,
                                           spaceBefore=25),
                            "lyr")
        self.styleSheet.add(ParagraphStyle(name='Paragraph',
                                           fontName="Alegreya-Medium",
                                           fontSize=14,
                                           leading=12),
                            "p")
        self.styleSheet.add(ParagraphStyle(name='Dropcap',
                                           fontName="Alegreya-Bold",
                                           fontSize=30,
                                           leading=12),
                            "dc")
        self.styleSheet.add(ParagraphStyle(name='Header',
                                           fontName="Alegreya-Italic",
                                           fontSize=12,
                                           leading=12),
                            "header")
        self.styleSheet.add(ParagraphStyle(name='Footer',
                                           fontName="Alegreya-Italic",
                                           fontSize=12,
                                           leading=12),
                            "footer")

    def build_document(self, output_filename: str):
        """Builds a pdf document file.
        """
        identification = self.bnml.find('identification')
        if identification:
            title = identification.find('work-title')
            if title:
                self.page.title = title.text
            author = identification.find('author')
            if author:
                self.page.author = author.text
            subject = identification.find('subject')
            if subject:
                self.page.subject = subject.text

        defaults = self.bnml.find('defaults')
        if defaults:
            page_layout = defaults.find('page-layout')
            if page_layout:
                paper_size = page_layout.find('paper-size')
                if paper_size:
                    self.page.set_size(paper_size.text)
                page_margins = page_layout.find('page-margins')
                if page_margins:
                    margin_dict = self.fill_page_dict(page_margins.attrib)
                    self.page.set_margins(margin_dict)

            score_styles = defaults.find('styles')
            for style in score_styles or []:
                style_name = style.tag.capitalize()
                local_attrs_from_score = self.fill_attribute_dict(style.attrib)
                if style_name in self.styleSheet:
                    self.update_paragraph_style(self.styleSheet[style_name], local_attrs_from_score)
                elif len(local_attrs_from_score) != 0:
                    new_paragraph_style = self.merge_paragraph_styles(
                        ParagraphStyle(style_name),
                        local_attrs_from_score)
                    try:
                        self.styleSheet.add(new_paragraph_style, style_name.lower())
                    except KeyError as e:
                        logging.warning("Couldn't add style to stylesheet: {}".format(e))

        self.doc = SimpleDocTemplate(
            filename=output_filename,
            pagesize=self.page.size,
            leftMargin=self.page.left_margin,
            rightMargin=self.page.right_margin,
            topMargin=self.page.top_margin,
            bottomMargin=self.page.bottom_margin,
            title=self.page.title,
            author=self.page.author,
            subject=self.page.subject
        )

    def create_pdf(self):
        """Create a PDF output file."""
        # Read main xml content
        for child_elem in self.bnml:
            if child_elem.tag == 'pagebreak':
                self.draw_newpage()

            if child_elem.tag == 'linebreak':
                space_amount = 30
                if 'space' in child_elem.attrib:
                    try:
                        space_amount = int(child_elem.attrib['space'])
                    except ValueError as e:
                        logging.error("Linebreak space error: {}".format(e))
                self.story.append(Spacer(0, space_amount))

            if child_elem.tag == 'paragraph':
                paragraph_attrib_dict = self.fill_attribute_dict(child_elem.attrib)
                self.draw_paragraph(child_elem, paragraph_attrib_dict)

            if child_elem.tag == 'troparion':
                neumes_list = []
                lyrics_list = []
                neume_line_height = self.styleSheet['Neumes'].leading
                dropcap = None
                dropcap_offset = 0

                for troparion_child_elem in child_elem:
                    if troparion_child_elem.tag == 'pagebreak':
                        self.story.append((PageBreak()))

                    # TODO: Test this
                    if troparion_child_elem.tag == 'linebreak':
                        self.story.append(Spacer(0, 30))

                    # TODO: Use this to draw strings before, after, or between neumes
                    # if troparion_child_elem.tag == 'string':
                    #    current_string_attrib = self.get_string_attributes(troparion_child_elem,
                    #                                                       self.defaultStringAttrib)
                    #    self.draw_paragraph(current_string_attrib)

                    if troparion_child_elem.tag == 'neumes':
                        neumes_elem = troparion_child_elem
                        attribs_from_bnml = self.fill_attribute_dict(neumes_elem.attrib)
                        neumes_style = self.merge_paragraph_styles(self.styleSheet['Neumes'], attribs_from_bnml)

                        for neume_char in neumes_elem.text.strip().split():
                            neume = Neume(char=neume_char,
                                          font_family=neumes_style.fontName,
                                          font_size=neumes_style.fontSize,
                                          color=neumes_style.textColor)
                            neumes_list.append(neume)

                    if troparion_child_elem.tag == 'lyrics':
                        lyrics_elem = troparion_child_elem
                        lyrics_style = self.styleSheet['Lyrics']
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
                        dropcap_style = self.styleSheet['Dropcap']
                        if dropcap_elem.attrib:
                            attribs_from_bnml = self.fill_attribute_dict(dropcap_elem.attrib)
                            dropcap_style = self.merge_paragraph_styles(dropcap_style, attribs_from_bnml)
                        dropcap_text = dropcap_elem.text.strip()

                        dropcap_offset = 5 + pdfmetrics.stringWidth(dropcap_text,
                                                                    dropcap_style.fontName,
                                                                    dropcap_style.fontSize)
                        dropcap = Dropcap(dropcap_text, dropcap_offset, dropcap_style)

                self.story.append(dropcap)

                # Pop off first letter of lyrics, since it will be drawn as a dropcap
                if dropcap and len(lyrics_list) > 0:
                    lyrics_list[0].text = lyrics_list[0].text[1:]

                neume_chunks = neume_dict.chunk_neumes(neumes_list)
                glyph_line: List[Glyph] = self.make_glyph_list(neume_chunks, lyrics_list)
                lines_list: List[GlyphLine] = self.line_break(glyph_line,
                                                              Cursor(dropcap_offset, 0),
                                                              self.page.width,
                                                              self.styleSheet['Neumes'].wordSpace)
                lines_list: List[GlyphLine] = self.line_justify(lines_list, self.page.width, dropcap_offset)

                for glyph_line in lines_list:
                    self.story.append(glyph_line)

        try:
            self.doc.build(self.story)
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

    def draw_paragraph(self, bnml_elem: Element, current_attribs: Dict[str, Any], ending_cursor_pos: int = Line.NEXT):
        """Draws a paragraph of text with the passed text attributes.

        :param bnml_elem: The bnml paragraph element.
        :param current_attribs: A dictionary of style attributes from a Kassia bnml file.
        :param ending_cursor_pos: Indicates where the cursor should be after
                             drawing the paragraph. Values are LN_RIGHT (to the
                             right), LN_NEXT (to the beginning of the next line),
                             and LN_BELOW (below the current paragraph).
        """
        if 'style' in current_attribs and current_attribs['style'] in self.styleSheet:
            default_paragraph_style = self.styleSheet[current_attribs['style']]
        else:
            default_paragraph_style = self.styleSheet['Paragraph']

        paragraph_style = self.merge_paragraph_styles(default_paragraph_style, current_attribs)
        paragraph_text = self.get_embedded_paragraph_text(bnml_elem, paragraph_style)
        self.story.append(Paragraph(paragraph_text, paragraph_style))

        '''paragraph = Paragraph(paragraph_text, paragraph_style)

        __, paragraph_height = paragraph.wrap(self.page.width, self.page.height)
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
            self.vert_pos -= (paragraph_height + paragraph_style.spaceAfter)
        elif ending_cursor_pos == Line.BELOW:
            self.vert_pos -= (paragraph_height + paragraph_style.leading + paragraph_style.spaceAfter)'''

    @staticmethod
    def merge_paragraph_styles(default_style: ParagraphStyle, bnml_style: Dict[str, Any]) -> ParagraphStyle:
        """Merges ReportLab ParagraphStyle attributes with Kassia bnml attributes and returns the new style

        :param default_style: The default ParagraphStyle (a ReportLab class).
        :param bnml_style: A dictionary of styles read a Kassia bnml file. The bnml_style needs to have ben already run
                           through fill_dict_attributes().
        :return new_style: A new ParagraphStyle of default_style with attributes updated by bnml_style
        """
        new_style = deepcopy(default_style)
        if 'font_family' in bnml_style and font_reader.is_registered_font(bnml_style['font_family']):
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
        if 'auto_leading' in bnml_style:
            new_style.autoLeading = bnml_style['auto_leading']
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
        if 'word_spacing' in bnml_style:
            new_style.wordSpace = bnml_style['word_spacing']
        return new_style

    @staticmethod
    def update_paragraph_style(default_style: ParagraphStyle, bnml_style: Dict[str, Any]):
        """Replaces ReportLab ParagraphStyle attributes with Kassia bnml attributes.

        :param default_style: The default ParagraphStyle (a ReportLab class).
        :param bnml_style: A dictionary of styles read a Kassia bnml file. The bnml_style needs to have ben already run
                           through fill_dict_attributes().
        """
        if 'font_family' in bnml_style and font_reader.is_registered_font(bnml_style['font_family']):
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
        if 'auto_leading' in bnml_style:
            default_style.autoLeading = bnml_style['auto_leading']
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
        if 'word_spacing' in bnml_style:
            default_style.wordSpace = bnml_style['word_spacing']
        return default_style

    def get_lyric_attributes(self, lyric_elem, default_lyric_attrib):
        current_lyric_attrib = deepcopy(default_lyric_attrib)
        settings_from_xml = self.fill_attribute_dict(lyric_elem.attrib)
        current_lyric_attrib.update(settings_from_xml)
        text = " ".join(lyric_elem.text.strip().split())
        current_lyric_attrib['text'] = text
        return current_lyric_attrib

    def draw_newpage(self):
        self.story.append(PageBreak())
        #self.draw_header("", style=self.styleSheet['header'])
        #self.draw_footer("", style=self.styleSheet['footer'])

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

        y_pos = self.page.bottom_margin / 2

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

    # TODO: Only check for lyricTopMargin? Do we know the proposed lyric_pos?
    def is_space_for_another_line(self, cursor_y_pos: int, glyph_list: List[Glyph] = None):
        """Returns whether there is space for a line of neumes and lyrics."""
        if glyph_list is None:
            glyph_list = []
        max_height = 0
        for glyph in glyph_list:
            lyric_height = getattr(glyph.lyric, 'top_margin', 0)
            if lyric_height > max_height:
                max_height = lyric_height > max_height
        return not self.page.is_bottom_of_page(cursor_y_pos - max_height)

    @staticmethod
    def make_glyph_list(neume_chunk_list: List[NeumeChunk], lyrics_list: List[Lyric]) -> List[Glyph]:
        """Takes a list of neumes and a list of lyrics and combines them into a single glyph list.
        :param neume_chunk_list: A list of neume chunks.
        :param lyrics_list: A list of lyrics.
        :return glyph_list: A list of glyphs.
        """
        i, l_ptr = 0, 0
        glyph_line: List[Glyph] = []
        while i < len(neume_chunk_list):
            # Grab next chunk
            neume_chunk = neume_chunk_list[i]

            # If any neumes within chunk take lyrics
            neume_takes_lyric: bool = False
            for neume in neume_chunk:
                if neume_dict.takes_lyric(neume):
                    neume_takes_lyric = True

            if neume_takes_lyric:
                if l_ptr < len(lyrics_list):
                    lyric = lyrics_list[l_ptr]
                    glyph = Glyph(neume_chunk=neume_chunk,
                                  lyric=lyric)
                else:
                    glyph = Glyph(neume_chunk)
                l_ptr += 1

                # Todo: See if lyric ends with '_' and if lyrics are wider than the neume, then combine with next chunk
            else:
                # no lyric needed
                glyph = Glyph(neume_chunk)

            glyph.set_width()
            glyph_line.append(glyph)
            i += 1
        return glyph_line

    @staticmethod
    def line_break(glyph_list: List[Glyph], starting_pos: Cursor, line_width: int, glyph_spacing: int) -> List[GlyphLine]:
        """Break continuous list of glyphs into lines- currently greedy.
        :param glyph_list: A list of glyphs.
        :param starting_pos: Where to begin drawing glyphs.
        :param line_width: Width of a line (usually page width minus margins).
        :param glyph_spacing: Minimum space between each glyph, from bnml.
        :return glyph_line_list: A list of lines of Glyphs.
        """
        cr = starting_pos
        glyph_line_list: List[GlyphLine] = []
        glyph_line: GlyphLine = GlyphLine()

        for glyph in glyph_list:
            new_line = False
            if (cr.x + glyph.width + glyph_spacing) >= line_width:
                cr.x = 0
                new_line = True

            adj_lyric_pos, adj_neume_pos = 0, 0

            neume_width = getattr(glyph.neume_chunk, 'width', 0)
            lyric_width = getattr(glyph.lyric, 'width', 0)
            if neume_width >= lyric_width:
                # center text
                adj_lyric_pos = (glyph.width - lyric_width) / 2.
            else:
                # center neume
                adj_neume_pos = (glyph.width - neume_width) / 2.

            glyph.neume_chunk_pos[0] = cr.x + adj_neume_pos
            glyph.neume_chunk_pos[1] = cr.y
            glyph.lyric_pos[0] = cr.x + adj_lyric_pos
            glyph.lyric_pos[1] = cr.y - getattr(glyph.lyric, 'top_margin', 0)  # New
            cr.x += glyph.width + glyph_spacing

            if new_line:
                glyph_line_list.append(glyph_line)
                glyph_line = GlyphLine()

            glyph_line.append(glyph)

        glyph_line_list.append(glyph_line)  # One more time to grab the last line

        return glyph_line_list

    @staticmethod
    def line_justify(line_list: List[GlyphLine], max_line_width: int, first_line_x_offset: int) -> List[GlyphLine]:
        """Justify a line of neumes by adjusting space between each neume group.
        :param line_list: A list of glyphs
        :param max_line_width: Max width a line of neumes can take up.
        :param first_line_x_offset: Offset of first line, usually from a dropcap.
        :return line_list: The modified line_list with neume spacing adjusted.
        """
        for line_index, line in enumerate(line_list):
            # Calc width of each chunk (and count how many chunks)
            total_chunk_width = 0
            for glyph in line:
                total_chunk_width += glyph.width

            # Skip if last line
            if line_index + 1 == len(line_list):
                continue

            # Subtract total from line_width (gets space remaining)
            space_remaining = (max_line_width - first_line_x_offset) - total_chunk_width
            # Divide by number of chunks in line
            glyph_spacing = space_remaining / len(line)

            cr = Cursor(first_line_x_offset, 0)

            for glyph in line:
                adj_lyric_pos, adj_neume_pos = 0, 0
                neume_width = getattr(glyph.neume_chunk, 'width', 0)
                lyric_width = getattr(glyph.lyric, 'width', 0)
                if neume_width >= lyric_width:
                    # center text
                    adj_lyric_pos = (glyph.width - lyric_width) / 2.
                else:
                    # center neume
                    adj_neume_pos = (glyph.width - neume_width) / 2.

                glyph.neume_chunk_pos[0] = cr.x + adj_neume_pos
                glyph.lyric_pos[0] = cr.x + adj_lyric_pos
                # glyph.neume_chunk_pos[0] += glyph_spacing
                # glyph.lyric_pos[0] += glyph_spacing

                cr.x += glyph.width + glyph_spacing

            # After first line (dropcap), set first line offset to zero
            first_line_x_offset = 0

        return line_list

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
    def fill_page_dict(page_dict: Dict[str, str]) -> Dict[str, int]:

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
                          'space_after', 'ending_cursor_pos', 'word_spacing']:
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
