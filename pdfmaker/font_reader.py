#!/usr/bin/python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont, TTFError
from PIL import ImageFont
from glob import glob


def register_fonts():
    root_dir = "fonts"

    ftypes = ('/*.ttf', '/*.otf')
    files_grabbed = []

    # Get all font files in fonts directory
    for ftype in ftypes:
        temp = glob(root_dir + ftype)
        files_grabbed.extend(temp)

    # Try to register them
    for fontLoc in files_grabbed:
        font_name = ImageFont.truetype(fontLoc, 1)
        try:
            pdfmetrics.registerFont(TTFont(font_name.font.family, fontLoc))
        except TTFError as e:
            print("Error: {}".format(e))
            raise SystemExit

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
