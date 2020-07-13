#!/usr/bin/python
import sys
import logging
from copy import deepcopy
from typing import Any, Dict, List

from reportlab.lib.enums import *
from reportlab.lib.styles import *
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import PageBreak, Paragraph, Spacer
from xml.etree.ElementTree import Element, ParseError, parse

import font_reader
from complex_doc_template import ComplexDocTemplate
from cursor import Cursor
from drop_cap import Dropcap
from enums import *
from glyph_line import GlyphLine
from glyphs import Glyph
from lyric import Lyric
from neume import Neume
from neume_chunk import NeumeChunk
from troparion import Troparion


class Kassia:
    """Base class for package"""

    def __init__(self, input_filename, output_file="examples/sample.pdf"):
        self.bnml = None
        self.doc = None  # SimpleDocTemplate()
        self.story = []
        self.styleSheet = getSampleStyleSheet()
        self.header_even_paragraph = None
        self.header_even_pagenum_style = None
        self.header_odd_paragraph = None
        self.header_odd_pagenum_style = None
        self.footer_paragraph = None
        self.footer_pagenum_style = None
        self.init_styles()
        self.input_filename = input_filename
        self.neume_info_dict = {}
        try:
            open(input_filename, "r")
            file_readable = True
        except IOError:
            file_readable = False
            logging.error("XML file not readable.")

        if file_readable:
            self.neume_info_dict = font_reader.register_fonts()
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
        self.doc = ComplexDocTemplate(filename=output_filename)

        identification = self.bnml.find('identification')
        if identification is not None:
            title = identification.find('work-title')
            if title is not None:
                setattr(self.doc, 'title', title.text)
            author = identification.find('author')
            if author is not None:
                setattr(self.doc, 'author', author.text)
            subject = identification.find('subject')
            if subject is not None:
                setattr(self.doc, 'subject', subject.text)

        defaults = self.bnml.find('defaults')
        if defaults is not None:
            page_layout = defaults.find('page-layout')
            if page_layout is not None:
                page_size_elem = page_layout.find('paper-size')
                if page_size_elem is not None:
                    self.doc.set_pagesize_by_name(page_size_elem.text)
                page_margins = page_layout.find('page-margins')
                if page_margins is not None:
                    margin_dict = self.fill_attribute_dict(page_margins.attrib)
                    self.doc.set_margins(margin_dict)

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

    def create_pdf(self):
        """Create a PDF output file."""
        for child_elem in self.bnml:
            if child_elem.tag in ['header-even', 'header']:
                default_header_style = self.styleSheet['Header']
                header_attrib_dict = self.fill_attribute_dict(child_elem.attrib)
                if 'style' in header_attrib_dict:
                    default_header_style = getattr(self.styleSheet, header_attrib_dict['style'], 'Header')
                header_style = self.merge_paragraph_styles(default_header_style, header_attrib_dict)
                header_text = child_elem.text.strip()
                self.header_even_paragraph: Paragraph = Paragraph(header_text, header_style)

                for embedded_attrib in child_elem:
                    if embedded_attrib.tag is not None and embedded_attrib.tag == 'page-number':
                        pagenum_attrib_dict = self.fill_attribute_dict(embedded_attrib.attrib)
                        self.header_even_pagenum_style = self.merge_paragraph_styles(default_header_style, pagenum_attrib_dict)

            if child_elem.tag == 'header-odd':
                default_header_style = self.styleSheet['Header']
                header_attrib_dict = self.fill_attribute_dict(child_elem.attrib)
                if 'style' in header_attrib_dict:
                    default_header_style = getattr(self.styleSheet, header_attrib_dict['style'], 'Header')
                header_style = self.merge_paragraph_styles(default_header_style, header_attrib_dict)
                header_text = child_elem.text.strip()
                self.header_odd_paragraph: Paragraph = Paragraph(header_text, header_style)

                for embedded_attrib in child_elem:
                    if embedded_attrib.tag is not None and embedded_attrib.tag == 'page-number':
                        pagenum_attrib_dict = self.fill_attribute_dict(embedded_attrib.attrib)
                        self.header_odd_pagenum_style = self.merge_paragraph_styles(default_header_style, pagenum_attrib_dict)

            if child_elem.tag == 'footer':
                default_footer_style = self.styleSheet['Footer']
                footer_attrib_dict = self.fill_attribute_dict(child_elem.attrib)
                if 'style' in footer_attrib_dict:
                    default_footer_style = getattr(self.styleSheet, footer_attrib_dict['style'], 'Footer')
                footer_style = self.merge_paragraph_styles(default_footer_style, footer_attrib_dict)
                footer_text = child_elem.text.strip()
                self.footer_paragraph: Paragraph = Paragraph(footer_text, footer_style)
                for embedded_attrib in child_elem:
                    if embedded_attrib.tag is not None and embedded_attrib.tag == 'page-number':
                        pagenum_attrib_dict = self.fill_attribute_dict(embedded_attrib.attrib)
                        self.footer_pagenum_style = self.merge_paragraph_styles(default_footer_style, pagenum_attrib_dict)

            if child_elem.tag == 'pagebreak':
                self.story.append(PageBreak())

            if child_elem.tag == 'linebreak':
                space = child_elem.attrib.get('space', '30')
                space_amt = int(space)
                self.story.append(Spacer(0, space_amt))

            if child_elem.tag == 'paragraph':
                paragraph_attrib_dict = self.fill_attribute_dict(child_elem.attrib)
                self.draw_paragraph(child_elem, paragraph_attrib_dict)

            if child_elem.tag == 'troparion':
                neumes_list = []
                lyrics_list = []
                dropcap = None

                for troparion_child_elem in child_elem:
                    if troparion_child_elem.tag == 'pagebreak':
                        self.story.append((PageBreak()))

                    if troparion_child_elem.tag == 'neumes':
                        neumes_elem = troparion_child_elem
                        attribs_from_bnml = self.fill_attribute_dict(neumes_elem.attrib)
                        neumes_style = self.merge_paragraph_styles(self.styleSheet['Neumes'], attribs_from_bnml)
                        # Get font family name without 'Main', 'Martyria', etc.
                        font_family_name, font_family_type = neumes_style.fontName.rsplit(' ', 1)
                        neume_config = self.neume_info_dict[font_family_name]

                        for neume_chunk in neumes_elem.text.strip().split():
                            # Check for ligatures and conditionals, if none, build from basic neume parts
                            neume_name_list = self.find_neume_names(neume_chunk, neume_config)
                            for neume_name in neume_name_list:
                                neume = self.create_neume(neume_name, neume_config, font_family_name, neumes_style)
                                if neume:  # neume will be None if neume not found
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
                        dropcap = Dropcap(dropcap_text, 10, dropcap_style)

                if neumes_list:
                    self.draw_troparion(neumes_list, lyrics_list, dropcap)

        try:
            self.doc.build(self.story,
                           onFirstPage=self.draw_header_footer,
                           onEvenPages=self.draw_header_footer,
                           onOddPages=self.draw_header_footer)
        except IOError:
            logging.error("Could not save XML file.")

    def find_neume_names(self, neume_chunk_name, neume_config) -> List[str]:
        """Check for conditional neumes and replace them if necessary."""
        if neume_chunk_name.count('_') == 0:
            return [neume_chunk_name]

        base_neume, possible_cond_neumes = neume_chunk_name.split('_', 1)
        for conditional in neume_config['classes']['conditional_neumes'].values():
            if base_neume in conditional['base_neume'] and possible_cond_neumes in conditional['component_glyphs']:
                neume_chunk_name = neume_chunk_name.replace(conditional['replace_glyph'], conditional['draw_glyph'])
                break

        return self._replace_ligatures(neume_chunk_name, neume_config)

    @staticmethod
    def _replace_ligatures(neume_chunk_name, neume_config) -> List[str]:
        """Tries to replace ligatures in a neume_chunk. Works by chopping off the last neume in the chunk and checking
        the remainder to see if it matches any ligatures in the neume config list."""
        possible_lig = neume_chunk_name
        neume_list = []
        while possible_lig.count('_') >= 1:
            if possible_lig in neume_config['glyphnames']:
                neume_list.insert(0, possible_lig)
                return neume_list
            possible_lig, remainder = possible_lig.rsplit('_', 1)
            neume_list.insert(0, remainder)

        neume_list.insert(0, possible_lig)

        return neume_list

    @staticmethod
    def create_neume(neume_name: str, neume_config: Dict, font_family: str, neume_style: ParagraphStyle):
        neume = None
        try:
            lyric_offset = None
            if 'lyric_offsets' in neume_config['classes'] and neume_name in neume_config['classes']['lyric_offsets']:
                lyric_offset = neume_config['classes']['lyric_offsets'][neume_name] * neume_style.fontSize
            neume = Neume(name=neume_name,
                          char=neume_config['glyphnames'][neume_name]['codepoint'],
                          font_family=font_family,
                          font_fullname=neume_config['glyphnames'][neume_name]['family'],
                          font_size=neume_style.fontSize,
                          color=neume_style.textColor,
                          standalone=neume_name in neume_config['classes']['standalone'],
                          takes_lyric=neume_name in neume_config['classes']['takes_lyric'],
                          lyric_offset=lyric_offset,
                          keep_with_next=neume_name in neume_config['classes']['keep_with_next'])
        except KeyError as e:
            logging.error("Couldn't add neume: {}. Check font config yaml.".format(e))
        return neume

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
        p = Paragraph(paragraph_text, paragraph_style)
        self.story.append(p)

    def draw_troparion(self, neumes_list: List[Neume], lyrics_list: List[Lyric], dropcap: Dropcap):
        """Draws a troparion with the passed text attributes.
        :param neumes_list: A list of neumes.
        :param lyrics_list: A list of Lyrics.
        :param dropcap: A dropcap object.
        """
        dropcap_offset = 0

        # Pop off first letter of lyrics, since it will be drawn as a dropcap
        if dropcap and len(lyrics_list) > 0:
            lyrics_list[0].text = lyrics_list[0].text[1:]
            lyrics_list[0].recalc_width()
            dropcap_offset = dropcap.width + dropcap.x_padding

        if neumes_list:
            neume_chunks = self.make_neume_chunks(neumes_list)
            glyph_line: List[Glyph] = self.make_glyph_list(neume_chunks, lyrics_list)
            lines_list: List[GlyphLine] = self.line_break(glyph_line,
                                                          Cursor(dropcap_offset, 0),
                                                          self.doc.width,
                                                          self.styleSheet['Neumes'].leading,
                                                          self.styleSheet['Neumes'].wordSpace)
            if len(lines_list) > 1 or self.styleSheet['Neumes'].alignment is TA_JUSTIFY:
                lines_list: List[GlyphLine] = self.line_justify(lines_list, self.doc.width, dropcap_offset)

            tropar = Troparion(lines_list, dropcap, self.doc.width)
            self.story.append(tropar)

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
        if 'border_width' in bnml_style:
            new_style.borderWidth = bnml_style['border_width']
        if 'border_color' in bnml_style:
            new_style.borderColor = bnml_style['border_color']
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
        if 'border_width' in bnml_style:
            default_style.borderWidth = bnml_style['border_width']
        if 'border_color' in bnml_style:
            default_style.borderColor = bnml_style['border_color']
        return default_style

    def draw_header_footer(self, canvas, doc):
        if doc.pageTemplate.id == 'Even':
            self.draw_header(canvas, doc, self.header_even_paragraph, self.header_even_pagenum_style)
        elif doc.pageTemplate.id == 'Odd':
            self.draw_header(canvas, doc, self.header_odd_paragraph, self.header_odd_pagenum_style)

        self.draw_footer(canvas, doc, self.footer_pagenum_style)

    def draw_header(self, canvas, doc, paragraph: Paragraph, pagenum_style: ParagraphStyle):
        """Draws the header onto the canvas.
        :param canvas: Canvas, passed from document.build.
        :param doc: SimpleDocTemplate, passed from document.build.
        :param paragraph: Paragraph of header text/style to draw.
        :param pagenum_style: The style of page number to draw.
        """
        if not paragraph:
            return

        style = paragraph.style

        if style.borderWidth:
            canvas.setStrokeColor(style.borderColor)
            canvas.setLineWidth(style.borderWidth)
            canvas.line(
                self.doc.left,
                self.doc.top,
                self.doc.right,
                self.doc.top)

        canvas.setFont(style.fontName, style.fontSize)
        canvas.setFillColor(style.textColor)

        y_pos = self.doc.pagesize[1] - (self.doc.topMargin * 0.85)

        if style.alignment == TA_LEFT:
            x_pos = self.doc.left
            canvas.drawString(x_pos, y_pos, paragraph.text)
        elif style.alignment == TA_RIGHT:
            x_pos = self.doc.right
            canvas.drawRightString(x_pos, y_pos, paragraph.text)
        elif style.alignment == TA_CENTER:
            x_pos = self.doc.center
            canvas.drawCentredString(x_pos, y_pos, paragraph.text)

        if pagenum_style is not None:
            if pagenum_style.alignment == TA_LEFT:
                canvas.drawString(self.doc.left, y_pos, str(canvas.getPageNumber()))
            elif pagenum_style.alignment == TA_RIGHT:
                canvas.drawRightString(self.doc.right, y_pos, str(canvas.getPageNumber()))
            elif pagenum_style.alignment == TA_CENTER:
                canvas.drawCentredString(self.doc.center, y_pos, str(canvas.getPageNumber()))

    def draw_footer(self, canvas, doc, pagenum_style: ParagraphStyle):
        """Draws the footer onto the canvas.
        :param canvas: Canvas, passed from document.build.
        :param doc: SimpleDocTemplate, passed from document.build.
        :param pagenum_style: The style of page number to draw.
        """
        if not self.footer_paragraph:
            return
            
        style = self.footer_paragraph.style

        if style.borderWidth:
            canvas.setStrokeColor(style.borderColor)
            canvas.setLineWidth(style.borderWidth)
            canvas.line(
                self.doc.left,
                self.doc.bottom,
                self.doc.right,
                self.doc.bottom)

        canvas.setFont(style.fontName, style.fontSize)
        canvas.setFillColor(style.textColor)

        y_pos = self.doc.bottomMargin / 2

        if style.alignment == TA_LEFT:
            x_pos = self.doc.left
            canvas.drawString(x_pos, y_pos, self.footer_paragraph.text)
        elif style.alignment == TA_RIGHT:
            x_pos = self.doc.right
            canvas.drawRightString(x_pos, y_pos, self.footer_paragraph.text)
        elif style.alignment == TA_CENTER:
            x_pos = self.doc.center
            canvas.drawCentredString(x_pos, y_pos, self.footer_paragraph.text)

        if pagenum_style is not None:
            if pagenum_style.alignment == TA_LEFT:
                canvas.drawString(self.doc.left, y_pos, str(canvas.getPageNumber()))
            elif pagenum_style.alignment == TA_RIGHT:
                canvas.drawRightString(self.doc.right, y_pos, str(canvas.getPageNumber()))
            elif pagenum_style.alignment == TA_CENTER:
                canvas.drawCentredString(self.doc.center, y_pos, str(canvas.getPageNumber()))

    @staticmethod
    def make_neume_chunks(neume_list: List[Neume]) -> List[NeumeChunk]:
        """Break a list of neumes into logical chunks based on whether a linebreak can occur between them
        :param neume_list: Iterable of type Neume
        """
        chunks_list: List[NeumeChunk] = []
        i = 0
        while i < len(neume_list):
            # Grab next neume
            neume = neume_list[i]
            chunk = NeumeChunk(neume)

            # Special case for Vareia, since it's non-breaking but comes before the next neume, unlike a fthora.
            # So attach the next neume and increment the counter.
            if neume.keep_with_next and (i + 1) < len(neume_list):
                chunk.append(neume_list[i+1])
                chunk.base_neume = neume_list[i+1]
                i += 1
            else:
                chunk.base_neume = neume

            # Add more neumes to chunk like fthora, ison, etc.
            j = 1
            if (i+1) < len(neume_list):
                while not neume_list[i + j].standalone:
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

    @staticmethod
    def make_glyph_list(neume_chunk_list: List[NeumeChunk], lyrics_list: List[Lyric]) -> List[Glyph]:
        """Takes a list of neume chunks and a list of lyrics and combines them into a single glyph list.
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
            lyrical_chunk: bool = False
            for neume in neume_chunk:
                if neume.takes_lyric:
                    lyrical_chunk = True

            if lyrical_chunk:
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

            glyph.set_size()
            glyph_line.append(glyph)
            i += 1
        return glyph_line

    def line_break(self, glyph_list: List[Glyph], starting_pos: Cursor, line_width: int, line_spacing: int,
                   glyph_spacing: int) -> List[GlyphLine]:
        """Break continuous list of glyphs into lines- currently greedy.
        :param glyph_list: A list of glyphs.
        :param starting_pos: Where to begin drawing glyphs.
        :param line_width: Width of a line (usually page width minus margins).
        :param line_spacing: Vertical space between each line. Needed to create GlyphLine.
        :param glyph_spacing: Minimum space between each glyph, from bnml.
        :return glyph_line_list: A list of lines of Glyphs.
        """
        cr = starting_pos
        glyph_line_list: List[GlyphLine] = []
        glyph_line: GlyphLine = GlyphLine(line_spacing, glyph_spacing)
        
        # Need to shift nuemes and lyrics up by this amount, since glyph will be drawn aligned to bottom, and
        # lyrics are being added below neumes
        y_offset = max(getattr(glyph.lyric, 'top_margin', 0) for glyph in glyph_list)

        for glyph in glyph_list:
            new_line = False
            if (cr.x + glyph.width + glyph_spacing) >= line_width:
                cr.x = 0
                new_line = True

            adj_lyric_pos, adj_neume_pos = 0, 0

            neume_width = getattr(glyph.neume_chunk, 'width', 0)
            lyric_width = getattr(glyph.lyric, 'width', 0)
            if neume_width >= lyric_width:
                # center lyrics
                adj_lyric_pos = (glyph.width - lyric_width) / 2.

                # special cases
                primary_neume: Neume = glyph.neume_chunk[0]
                if primary_neume.name == 'vare':
                    # If variea, center lyric under neume chunk without vareia
                    adj_lyric_pos += primary_neume.width / 2.
                elif primary_neume.name == 'syne':
                    # If syneches elaphron, center lyric under elaphron
                    # Calculate if wasn't specified in neume font config
                    if primary_neume.lyric_offset is None:
                        apos_char = self.neume_info_dict[primary_neume.font_family]['glyphnames']['apos']['codepoint']
                        primary_neume.lyric_offset = pdfmetrics.stringWidth(apos_char, primary_neume.font_fullname, primary_neume.font_size)
                    adj_lyric_pos += primary_neume.lyric_offset / 2.
            else:
                # center neume
                adj_neume_pos = (glyph.width - neume_width) / 2.

            glyph.neume_chunk_pos[0] = cr.x + adj_neume_pos
            glyph.neume_chunk_pos[1] = y_offset/2.
            glyph.lyric_pos[0] = cr.x + adj_lyric_pos
            glyph.lyric_pos[1] = cr.y
            cr.x += glyph.width + glyph_spacing

            if new_line:
                glyph_line_list.append(glyph_line)
                glyph_line = GlyphLine(line_spacing, glyph_spacing)

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
            total_chunk_width = sum(glyph.width for glyph in line)
            
            # Skip if last line
            if line_index + 1 == len(line_list):
                continue

            # Subtract total from line_width (gets space remaining)
            space_remaining = (max_line_width - first_line_x_offset) - total_chunk_width
            # Divide by number of chunks in line
            glyph_spacing = space_remaining / len(line)

            cr = Cursor(0, 0)

            for glyph in line:
                adj_lyric_pos, adj_neume_pos = 0, 0
                neume_width = getattr(glyph.neume_chunk, 'width', 0)
                lyric_width = getattr(glyph.lyric, 'width', 0)
                if neume_width >= lyric_width:
                    # center lyrics
                    adj_lyric_pos = (glyph.width - lyric_width) / 2.

                    # special cases
                    primary_neume = glyph.neume_chunk[0]
                    if primary_neume.name == 'vare':
                        # If variea, center lyric under neume chunk excluding vareia
                        adj_lyric_pos += primary_neume.width / 2.
                    elif primary_neume.name == 'syne':
                        # If syneches elaphron, center lyric under elaphron
                        adj_lyric_pos += primary_neume.lyric_offset / 2.
                else:
                    # center neume
                    adj_neume_pos = (glyph.width - neume_width) / 2.

                glyph.neume_chunk_pos[0] = cr.x + adj_neume_pos
                glyph.lyric_pos[0] = cr.x + adj_lyric_pos

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

    def fill_attribute_dict(self, attribute_dict: Dict[str, str]) -> Dict[str, Any]:
        new_attr_dict: Dict[str, Any] = deepcopy(attribute_dict)
        if 'align' in attribute_dict:
            new_attr_dict['align'] = self.str_to_align(attribute_dict['align'])

        if 'font_family' in attribute_dict and not font_reader.is_registered_font(
            attribute_dict['font_family']
        ):
            logging.warning("{} not found, using default instead".format(attribute_dict['font_family']))

        for font_attr in ['font_size', 'first_line_indent', 'left_indent', 'right_indent', 'leading', 'space_before',
                          'space_after', 'ending_cursor_pos', 'word_spacing']:
            if font_attr in attribute_dict:
                try:
                    new_attr_dict[font_attr] = int(attribute_dict[font_attr])
                except ValueError as e:
                    logging.warning("{} warning: {}".format(font_attr, e))
                    # Get rid of xml font attribute, will use default later
                    attribute_dict.pop(font_attr)

        for float_attr in ['border_width']:
            if float_attr in attribute_dict:
                try:
                    new_attr_dict[float_attr] = float(attribute_dict[float_attr])
                except ValueError as e:
                    logging.warning("{} warning: {}".format(float_attr, e))
                    attribute_dict.pop(float_attr)

        for margin_attr in ['top_margin', 'bottom_margin', 'left_margin', 'right_margin']:
            if margin_attr in attribute_dict:
                try:
                    new_attr_dict[margin_attr] = int(attribute_dict[margin_attr])
                except ValueError as e:
                    logging.warning("{} warning: {}".format(margin_attr, e))
                    attribute_dict.pop(margin_attr)
        return new_attr_dict


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
