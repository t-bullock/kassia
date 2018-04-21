#!/usr/bin/python
from reportlab.lib import fontfinder
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont, TTFError
import os
import inspect
from sys import platform
import logging


def register_fonts():
    ff = fontfinder.FontFinder(useCache=False)

    kassia_local_font_path = inspect.stack()[0][1].rsplit('/', 1)[0] + "/fonts"
    ff.addDirectory(kassia_local_font_path, recur=True)
    if platform.startswith("darwin"):
        ff.addDirectories(['/Library/Fonts', os.path.expanduser("~/Library/Fonts")])
    elif platform.startswith("win") or platform.startswith("cygwin"):
        ff.addDirectory(os.path.join(os.environ['WINDIR'], 'Fonts'))
    # elif platform.startswith("linux"):
        # implement something for linux

    try:
        ff.search()
    except KeyError as ke:
        logging.warning("Problem parsing font: {}".format(ke))
    except Exception as e:
        logging.warning(e)

    for family_name in ff.getFamilyNames():
        fonts_in_family = ff.getFontsInFamily(family_name)
        for font in fonts_in_family:
            if len(fonts_in_family) == 1:
                try:
                    ttfont = TTFont(family_name.decode("utf-8"), font.fileName)
                    pdfmetrics.registerFont(ttfont)
                    pdfmetrics.registerFontFamily(family_name)
                except TTFError as e:
                    logging.warning("Could not register {}, {}".format(family_name, e))
                    continue
            elif len(fonts_in_family) > 1:
                '''If font family has multiple weights/styles'''
                font_name = family_name + "-".encode() + font.styleName
                font_name = font_name.decode("utf-8")
                try:
                    ttfont = TTFont(font_name, font.fileName)
                    pdfmetrics.registerFont(ttfont)
                    addMapping(font.familyName, font.isBold, font.isItalic, font_name)
                except TTFError as e:
                    logging.warning("Could not register {}, {}".format(family_name, e))
                    continue
    print(pdfmetrics.getRegisteredFontNames())


def is_registered_font(font_name):
    return font_name in pdfmetrics.getRegisteredFontNames()
