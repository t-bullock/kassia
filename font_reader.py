#!/usr/bin/python
from typing import List

from reportlab.lib import fontfinder
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont, TTFError
import os
import inspect
from sys import platform
import logging


def register_fonts(system_fonts: bool = False):
    """
    Build a list of paths to search for fonts, and register all fonts found in those paths.
    Currently assumes that Kassia fonts will be in /fonts.
    :param system_fonts: Whether to use system installed fonts.
    """
    # Platform specific paths to search for additional fonts
    dirs: List[str] = []
    if platform.startswith("darwin"):
        # Always check local kassia font folder first, so those fonts have precedence
        dirs = [inspect.stack()[0][1].rsplit('/', 1)[0] + "/fonts"]
        if system_fonts:
            dirs.extend(['/Library/Fonts', os.path.expanduser("~/Library/Fonts")])
    elif platform.startswith("win") or platform.startswith("cygwin"):
        dirs = [inspect.stack()[0][1].rsplit('\\', 1)[0] + "\\fonts"]
        if system_fonts:
            dirs.append(os.path.join(os.environ['WINDIR'], 'Fonts'))
    elif platform.startswith("linux"):
        dirs = [inspect.stack()[0][1].rsplit('/', 1)[0] + "/fonts"]
        if system_fonts:
            logging.warning("Support for system fonts is not implemented for Linux.")
    for folder in dirs:
        _register_fonts_in_path(folder)


def _register_fonts_in_path(font_path: str):
    """
    Register all fonts in the given font_path.
    :param font_path: A path to a folder containing font files.
    """
    ff = fontfinder.FontFinder(useCache=False)  # Caching seems to cause problems. Disable for now.
    ff.addDirectory(font_path, recur=True)

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
                _register_single_weight_font(family_name, font)
            elif len(fonts_in_family) > 1:
                '''If font family has multiple weights/styles'''
                _register_multi_weight_font(family_name, font)


def _register_single_weight_font(family_name: str, font):
    try:
        ttfont = TTFont(family_name.decode("utf-8"), font.fileName)
        pdfmetrics.registerFont(ttfont)
        pdfmetrics.registerFontFamily(family_name)
    except TTFError as e:
        logging.warning("Could not register font {}: {}".format(family_name, e))


def _register_multi_weight_font(family_name: str, font):
    font_name = family_name + "-".encode() + font.styleName
    font_name = font_name.decode("utf-8")
    try:
        ttfont = TTFont(font_name, font.fileName)
        pdfmetrics.registerFont(ttfont)
        addMapping(font.familyName, font.isBold, font.isItalic, font_name)
    except TTFError as e:
        logging.warning("Could not register font {}: {}".format(family_name, e))


def is_font_registered(font_name):
    return font_name in pdfmetrics.getRegisteredFontNames()
