#!/usr/bin/python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont, TTFError
from PIL import ImageFont
from glob import glob
import os
import inspect


def register_fonts():
    # Fonts folder within the current directory
    root_dir = inspect.stack()[0][1].rsplit('/', 1)[0] + "/fonts"

    file_types = ('/*.ttf', '/*.otf')
    files_grabbed = []

    # Get all font files in fonts directory
    for f_type in file_types:
        temp = glob(root_dir + f_type)
        files_grabbed.extend(temp)

    # Try to register them
    for fontLoc in files_grabbed:
        font_name = ImageFont.truetype(fontLoc, 1)
        try:
            pdfmetrics.registerFont(TTFont(font_name.font.family, fontLoc))
        except TTFError as e:
            print("Error: {}".format(e))
            raise SystemExit

    # Get all folders, used for families with bold, italic, etc.
    for folders in next(os.walk(root_dir))[1]:
        files_grabbed = []
        for f_type in file_types:
            temp = glob(root_dir + '/' + folders + '/' + f_type)
            files_grabbed.extend(temp)

        # Try to register them
        for fontLoc in files_grabbed:
            font_name = ImageFont.truetype(fontLoc, 1)
            try:
                new_font_name = font_name.font.family + font_name.font.style
                new_font_name = new_font_name.replace(" ", "")
                pdfmetrics.registerFont(TTFont(new_font_name, fontLoc))
            except TTFError as e:
                print("Error: {}".format(e))
                raise SystemExit

        pdfmetrics.registerFontFamily(font_name.font.family,
                                      normal=font_name.font.family,
                                      bold=font_name.font.family + '-Bold',
                                      italic=font_name.font.family + '-Italic',
                                      boldItalic=font_name.font.family + '-BoldItalic')

    # Check that default fonts are registered
    #registered_fonts = pdfmetrics.getRegisteredFontNames()
    #if "Kassia Tsak Main" not in registered_fonts:
    #    print "Warning: Default font 'Kassia Tsak Main' is missing from the fonts directory"


def is_registered_font(font_name):
    return font_name in pdfmetrics.getRegisteredFontNames()


FONT_SPECIFIER_NAME_ID = 4
FONT_SPECIFIER_FAMILY_ID = 1


def short_name(font):
    """Get the short name from the font's names table"""
    name = ""
    family = ""
    for record in font['name'].names:
        if b'\x00' in record.string:
            name_str = record.string.decode('utf-16-be')
        else:
            name_str = record.string.decode('utf-8')
        if record.nameID == FONT_SPECIFIER_NAME_ID and not name:
            name = name_str
        elif record.nameID == FONT_SPECIFIER_FAMILY_ID and not family:
            family = name_str
        if name and family:
            break
    return [name, family]
