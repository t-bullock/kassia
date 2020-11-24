#!/usr/bin/python
import sys
import logging
from copy import deepcopy
from typing import Any, Dict, List, Tuple

from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet, StyleSheet1
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import PageBreak, Paragraph, Spacer
from xml.etree.ElementTree import Element, ParseError, parse

import font_reader
from complex_doc_template import ComplexDocTemplate
from cursor import Cursor
from drop_cap import Dropcap
from enums import Line
from syllable_line import SyllableLine
from syllable import Syllable
from lyric import Lyric
from neume import Neume
from neume_chunk import NeumeChunk
from score import Score


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
        self.scoreStyleSheet = StyleSheet1()
        self.init_styles()
        self.input_filename = input_filename
        self.neume_info_dict = {}
        
        try:
            open(input_filename, "r")
        except IOError:
            logging.error("XML file not readable.")
            return

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
            sys.exit(1)

    def init_styles(self):
        """Add specific Kassia styles to stylesheet.
        """
        self.styleSheet.add(ParagraphStyle(name='Neumes',
                                           fontName="KA New Stathis",
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
        """Build a pdf document file with metadata.
        """
        self.doc = ComplexDocTemplate(filename=output_filename)

        metadata = self.bnml.find('identification')
        if metadata is not None:
            for meta_tag in ['title', 'author', 'subject']:
                meta_value = metadata.find(meta_tag)
                setattr(self.doc, meta_tag, meta_value.text)

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

            # Read and set default document styles
            default_styles = defaults.find('styles')
            for para_style in default_styles.findall('para-style'):
                self.parse_para_style(para_style)

            for score_style_tag in ['score-style', 'neume-style', 'lyric-style', 'dropcap-style']:
                style_tags = default_styles.findall(score_style_tag)
                for style in style_tags:
                    self.parse_score_style(style)

    def parse_para_style(self, para_style: Element):
        """Read paragraph-type styles and save them in stylesheet.

        Inherits style from, and then overrides specific styles specified in para_style element.

        :param para_style: A paragraph stylesheet specified in bnml.
        """
        style_name = para_style.attrib['name']
        style_attrs = self.fill_attribute_dict(para_style.attrib)
        if style_name in self.styleSheet:
            self.update_paragraph_style(self.styleSheet[style_name], style_attrs)
        elif len(style_attrs) >= 1:
            new_paragraph_style = self.merge_paragraph_styles(
                ParagraphStyle(style_name),
                style_attrs)
            try:
                self.styleSheet.add(new_paragraph_style, style_name)
            except KeyError as e:
                logging.warning("Couldn't add style to stylesheet: {}".format(e))

    def parse_score_style(self, style: Element):
        """Read and set score-type stylesheets.
        """
        style_name = style.tag.split('-')[0]
        if 'type' in style.attrib:
            style_name = '-'.join([style_name, style.attrib['type']])
        style_attrs = self.fill_attribute_dict(style.attrib)
        new_style = self.merge_paragraph_styles(
            ParagraphStyle(
                style_name),
            style_attrs)
        try:
            self.scoreStyleSheet.add(new_style, style_name)
        except KeyError as ke:
            logging.warning("Couldn't add style to stylesheet: {}".format(ke))

    def parse_music(self, bnml_file: Element):
        """Create a score and add it to story.
        """
        music = bnml_file.find('music')
        if music:
            for music_elem in music:
                if music_elem.tag in ['header-even', 'header']:
                    self._parse_header_even(music_elem)
                elif music_elem.tag == 'header-odd':
                    self._parse_header_odd(music_elem)
                elif music_elem.tag == 'footer':
                    self._parse_footer(music_elem)
                elif music_elem.tag == 'pagebreak':
                    self._parse_pagebreak(music_elem)
                elif music_elem.tag == 'linebreak':
                    self._parse_linebreak(music_elem)
                elif music_elem.tag in ['para', 'paragraph']:
                    self._parse_paragraph(music_elem)
                elif music_elem.tag == 'score':
                    self._parse_score(music_elem)

    def _parse_header_even(self, header_elem: Element):
        default_header_style = self.styleSheet['Header']
        header_attrib_dict = self.fill_attribute_dict(header_elem.attrib)
        if 'style' in header_attrib_dict:
            default_header_style = getattr(self.styleSheet, header_attrib_dict['style'], 'Header')
        header_style = self.merge_paragraph_styles(default_header_style, header_attrib_dict)
        header_text = header_elem.text.strip()
        self.header_even_paragraph: Paragraph = Paragraph(header_text, header_style)

        for embedded_attrib in header_elem:
            if embedded_attrib.tag is not None and embedded_attrib.tag == 'page-number':
                pagenum_attrib_dict = self.fill_attribute_dict(embedded_attrib.attrib)
                self.header_even_pagenum_style = self.merge_paragraph_styles(default_header_style, pagenum_attrib_dict)

    def _parse_header_odd(self, header_elem: Element):
        default_header_style = self.styleSheet['Header']
        header_attrib_dict = self.fill_attribute_dict(header_elem.attrib)
        if 'style' in header_attrib_dict:
            default_header_style = getattr(self.styleSheet, header_attrib_dict['style'], 'Header')
        header_style = self.merge_paragraph_styles(default_header_style, header_attrib_dict)
        header_text = header_elem.text.strip()
        self.header_odd_paragraph: Paragraph = Paragraph(header_text, header_style)

        for embedded_attrib in header_elem:
            if embedded_attrib.tag is not None and embedded_attrib.tag == 'page-number':
                pagenum_attrib_dict = self.fill_attribute_dict(embedded_attrib.attrib)
                self.header_odd_pagenum_style = self.merge_paragraph_styles(default_header_style, pagenum_attrib_dict)

    def _parse_footer(self, music_elem: Element):
        default_footer_style = self.styleSheet['Footer']
        footer_attrib_dict = self.fill_attribute_dict(music_elem.attrib)
        if 'style' in footer_attrib_dict:
            default_footer_style = getattr(self.styleSheet, footer_attrib_dict['style'], 'Footer')
        footer_style = self.merge_paragraph_styles(default_footer_style, footer_attrib_dict)
        footer_text = music_elem.text.strip()
        self.footer_paragraph: Paragraph = Paragraph(footer_text, footer_style)
        for embedded_attrib in music_elem:
            if embedded_attrib.tag is not None and embedded_attrib.tag == 'page-number':
                pagenum_attrib_dict = self.fill_attribute_dict(embedded_attrib.attrib)
                self.footer_pagenum_style = self.merge_paragraph_styles(default_footer_style, pagenum_attrib_dict)

    def _parse_pagebreak(self, music_elem: Element):
        self.story.append(PageBreak())

    def _parse_linebreak(self, linebreak_elem: Element):
        space = linebreak_elem.attrib.get('space', '30')
        space_amt = int(space)
        self.story.append(Spacer(0, space_amt))

    def _parse_paragraph(self, para_elem: Element):
        para_attrs = self.fill_attribute_dict(para_elem.attrib)
        # if 'style' in para_attrs and para_attrs['style'] in self.styleSheet:
        try:
            default_paragraph_style = self.styleSheet[para_attrs['style']]
        except KeyError:
            default_paragraph_style = self.styleSheet['Paragraph']

        paragraph_style = self.merge_paragraph_styles(default_paragraph_style, para_attrs)
        paragraph_text = self.get_embedded_paragraph_text(para_elem, paragraph_style)
        para = Paragraph(paragraph_text, paragraph_style)
        self.story.append(para)

    def _parse_score(self, score_elem: Element):
        syl_list: List[Syllable] = []
        dropcap = None
        dropcap_offset = 0

        for syl_elem in score_elem.findall('syllable'):
            syllable = self._parse_syllable(syl_elem)
            syl_list.append(syllable)

        dropcap_elem = score_elem.find('dropcap')
        if dropcap_elem is not None:
            dropcap = self._parse_dropcap(dropcap_elem)

        # Pop off first letter of lyrics, since it will be drawn as a dropcap
        if dropcap and syl_list[0].lyric:
            first_lyric = syl_list[0].lyric
            first_lyric.text = first_lyric.text[1:]
            first_lyric.recalc_width()
            dropcap_offset = dropcap.width + dropcap.x_padding

        lines_list: List[SyllableLine] = self.line_break(syl_list,
                                                         Cursor(dropcap_offset, 0),
                                                         self.doc.width,
                                                         self.scoreStyleSheet['score'].leading,
                                                         self.scoreStyleSheet['score'].wordSpace)

        # TODO: Dropcap space is wrong if this isn't called
        if self.scoreStyleSheet['score'].alignment == TA_JUSTIFY and len(lines_list) > 1:
            lines_list: List[SyllableLine] = self.line_justify(lines_list, self.doc.width, dropcap_offset)

        score = Score(lines_list, dropcap, self.doc.width)
        self.story.append(score)

    def _parse_dropcap(self, dc_elem: Element) -> Dropcap:
        dropcap_style = self.scoreStyleSheet['dropcap']
        if dc_elem.attrib:
            attribs_from_bnml = self.fill_attribute_dict(dc_elem.attrib)
            dropcap_style = self.merge_paragraph_styles(dropcap_style, attribs_from_bnml)
        dropcap_text = dc_elem.text.strip()
        return Dropcap(dropcap_text, dropcap_style.rightIndent, dropcap_style)

    def _parse_syllable(self, syl_elem: Element) -> Syllable:
        lyric = None
        neume_group = None

        lyric_elem = syl_elem.find('lyric')
        if lyric_elem is not None:
            lyric = self._parse_lyric(lyric_elem)

        neume_group_elem = syl_elem.find('neume-group')
        if neume_group_elem is not None:
            neume_group = self._parse_neume_group(neume_group_elem)

        return Syllable(neume_chunk=neume_group, lyric=lyric)

    def _parse_lyric(self, lyric_elem: Element) -> Lyric:
        lyrics_style = self.scoreStyleSheet['lyric']
        attribs_from_bnml = self.fill_attribute_dict(lyric_elem.attrib)
        lyrics_style = self.merge_paragraph_styles(lyrics_style, attribs_from_bnml)
        return Lyric(text=lyric_elem.text.strip(),
                     font_family=lyrics_style.fontName,
                     font_size=lyrics_style.fontSize,
                     color=lyrics_style.textColor,
                     top_margin=lyrics_style.spaceBefore)

    def _parse_neume_group(self, neume_group_elem: Element) -> NeumeChunk:
        """Read neume-group element in bnml and create NeumeChunk object.

        :param neume_group_elem: A neume-group element in bnml.
        :return: A NeumeChunk with ligatures and conditionals replaced using information from font config.
        """
        attribs_from_bnml = self.fill_attribute_dict(neume_group_elem.attrib)
        neumes_style = self.merge_paragraph_styles(self.scoreStyleSheet['score'], attribs_from_bnml)
        # Get font family name without 'Main', 'Martyria', etc.
        #font_family_name, _ = neumes_style.fontName.rsplit(' ', 1)
        # TODO: Fix this so family can be used
        font_family_name = neumes_style.fontName
        neume_config = self.neume_info_dict[font_family_name]

        # TODO: Replace this underscore logic?
        neume_name_list = []
        for neume_elem in neume_group_elem:
            #neume = self._parse_neume(neume_elem)
            neume_name_str = neume_elem.text.strip()
            neume_name_list.append(neume_name_str)
        neume_group_names = '_'.join(neume_name_list)

        # Check for ligatures and conditionals. If none, build from basic neume parts
        neume_name_list = self.find_neume_names(neume_group_names, neume_config)

        # Build neume chunk
        neume_chunk = NeumeChunk()
        for neume_name in neume_name_list:
            try:
                neume = self.create_neume(neume_name, neume_config, neumes_style)
                if neume:  # neume will be None if neume not found
                    neume_chunk.append(neume)
            except KeyError as ke:
                logging.error("Couldn't add neume: {}. Check bnml for bad symbol and verify glyphnames.yaml is correct.".format(ke))

        neume_chunk.finalize()
        return neume_chunk

    def create_pdf(self):
        try:
            self.doc.build(self.story,
                           onFirstPage=self.draw_header_footer,
                           onEvenPages=self.draw_header_footer,
                           onOddPages=self.draw_header_footer)
        except IOError:
            logging.error("Could not save XML file.")

    def find_neume_names(self, neume_chunk_name: str, neume_config: Dict) -> List[str]:
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
    def _replace_ligatures(neume_chunk_name: str, neume_config: Dict) -> List[str]:
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

    def create_neume(self, neume_name: str, neume_config: Dict, neume_style: ParagraphStyle) -> Neume:
        """Creates a neume object using neume name and font configuration.
        :param neume_name: Name of neume.
        :param neume_config: Font configuration information from yaml.
        :param neume_style: Neume style information.
        :return: A neume.
        """
        try:
            lyric_offset = neume_config['classes']['lyric_offsets'][neume_name] * neume_style.fontSize
        except KeyError:
            lyric_offset = None

        try:
            neume_char = neume_config['glyphnames'][neume_name]['codepoint']
        except KeyError as ke:
            logging.error("Couldn't add neume: {}. Name not found in font configuration.".format(ke))
            return None

        try:
            neume = Neume(name=neume_name,
                          char=neume_char,
                          font_family=neume_style.fontName,
                          font_fullname=neume_config['glyphnames'][neume_name]['family'],
                          font_size=neume_style.fontSize,
                          color=neume_style.textColor,
                          standalone=neume_name in neume_config['classes']['standalone'],
                          takes_lyric=neume_name in neume_config['classes']['takes_lyric'],
                          lyric_offset=lyric_offset,
                          keep_with_next=neume_name in neume_config['classes']['keep_with_next'])
        except KeyError as ke:
            logging.error("Couldn't create neume: {}. Check bnml and font config yaml.".format(ke))
            return None
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

    def line_break(self, syl_list: List[Syllable], starting_pos: Cursor, line_width: int, line_spacing: int,
                   syl_spacing: int) -> List[SyllableLine]:
        """Break continuous list of syllables into lines- currently greedy.
        :param syl_list: A list of syllables.
        :param starting_pos: Where to begin drawing syllables.
        :param line_width: Width of a line (usually page width minus margins).
        :param line_spacing: Vertical space between each line. Needed to create SyllableLine.
        :param syl_spacing: Minimum space between each syllable, from bnml.
        :return syl_line_list: A list of lines of Glyphs.
        """
        cr = starting_pos
        syl_line_list: List[SyllableLine] = []
        syl_line: SyllableLine = SyllableLine(line_spacing, syl_spacing)
        
        # Need to shift neumes and lyrics up by this amount, since syllable will be drawn aligned to bottom, and
        # lyrics are being added below neumes
        y_offset = max(getattr(syl.lyric, 'top_margin', 0) for syl in syl_list)

        for syl in syl_list:
            new_line = False
            if (cr.x + syl.width + syl_spacing) >= line_width:
                cr.x = 0
                new_line = True

            adj_lyric_pos, adj_neume_pos = 0, 0

            neume_width = getattr(syl.neume_chunk, 'width', 0)
            lyric_width = getattr(syl.lyric, 'width', 0)
            if neume_width >= lyric_width:
                # center lyrics
                adj_lyric_pos = (syl.width - lyric_width) / 2.

                # special cases
                primary_neume: Neume = syl.neume_chunk[0]
                if primary_neume.name == 'bare':
                    # If bareia, center lyric under neume chunk without bareia
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
                adj_neume_pos = (syl.width - neume_width) / 2.

            syl.neume_chunk_pos[0] = cr.x + adj_neume_pos
            syl.neume_chunk_pos[1] = y_offset/2.
            syl.lyric_pos[0] = cr.x + adj_lyric_pos
            syl.lyric_pos[1] = cr.y
            cr.x += syl.width + syl_spacing

            if new_line:
                syl_line_list.append(syl_line)
                syl_line = SyllableLine(line_spacing, syl_spacing)

            syl_line.append(syl)

        syl_line_list.append(syl_line)  # One more time to grab the last line

        return syl_line_list

    @staticmethod
    def line_justify(line_list: List[SyllableLine], max_line_width: int, first_line_x_offset: int) -> List[SyllableLine]:
        """Justify a line of neumes by adjusting space between each neume group.
        :param line_list: A list of syllables
        :param max_line_width: Max width a line of neumes can take up.
        :param first_line_x_offset: Offset of first line, usually from a dropcap.
        :return line_list: The modified line_list with neume spacing adjusted.
        """
        for line_index, line in enumerate(line_list):
            # Calc width of each chunk (and count how many chunks)
            total_chunk_width = sum(syl.width for syl in line)
            
            # Skip if last line
            if line_index + 1 == len(line_list):
                continue

            # Subtract total from line_width (gets space remaining)
            space_remaining = (max_line_width - first_line_x_offset) - total_chunk_width
            # Divide by number of chunks in line
            syl_spacing = space_remaining / len(line)

            cr = Cursor(0, 0)

            for syl in line:
                adj_lyric_pos, adj_neume_pos = 0, 0
                neume_width = getattr(syl.neume_chunk, 'width', 0)
                lyric_width = getattr(syl.lyric, 'width', 0)
                if neume_width >= lyric_width:
                    # center lyrics
                    adj_lyric_pos = (syl.width - lyric_width) / 2.

                    # special cases
                    primary_neume = syl.neume_chunk[0]
                    if primary_neume.name == 'bare':
                        # If bareia, center lyric under neume chunk excluding bareia
                        adj_lyric_pos += primary_neume.width / 2.
                    elif primary_neume.name == 'syne':
                        # If syneches elaphron, center lyric under elaphron
                        adj_lyric_pos += primary_neume.lyric_offset / 2.
                else:
                    # center neume
                    adj_neume_pos = (syl.width - neume_width) / 2.

                syl.neume_chunk_pos[0] = cr.x + adj_neume_pos
                syl.lyric_pos[0] = cr.x + adj_lyric_pos

                cr.x += syl.width + syl_spacing

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
