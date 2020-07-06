#!/usr/bin/python
from pathlib import Path

from reportlab.lib import fontfinder
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont, TTFError
import os
from sys import platform
import logging

from ruamel.yaml import safe_load, YAMLError
from schema import Schema, And, Optional, SchemaError

font_class_schema = Schema({
            'family_name': str,
            'takes_lyric': [str],
            'standalone': [str],
            Optional('keep_with_next'): [str],
            Optional('neumes_with_lyric_offset'): {str: float},
            Optional('optional_ligatures'): {str: {And('component_glyphs'): [str]}},
            Optional('conditional_neumes'): {str: {And('base_neume'): list, And('component_glyphs'): list, And('replace_glyph'): str, And('draw_glyph'): str}},
        })

font_glyphnames_schema = Schema({
            str: {
                And('family'): str,
                And('codepoint'): str,
                Optional('component_glyphs'): [str],
                Optional('description'): str,
            },
        })


def register_fonts(check_sys_fonts=False):
    """Registers fonts by checking the local /font directory, and system installed fonts.
    """
    dirs = []

    # Always check local kassia font folder first, so included fonts have precedence
    internal_font_path = os.path.join(str(Path.cwd()), 'fonts')

    neume_font_configs = get_neume_dict(internal_font_path)
    dirs.append(internal_font_path)

    if check_sys_fonts:
        dirs.extend(_get_system_font_paths())

    for path in dirs:
        register_font_path(path)

    return neume_font_configs


def _get_system_font_paths():
    if platform.startswith("darwin"):
        return ['/Library/Fonts', os.path.expanduser("~/Library/Fonts")]
    elif platform.startswith("win") or platform.startswith("cygwin"):
        return [os.path.join(os.environ['WINDIR'], 'Fonts')]
    elif platform.startswith("linux"):
        logging.warning("Logic for checking system fonts in Linux is not implemented.")
        return None


def get_neume_dict(font_folder_path):
    font_config = {}
    for path in Path(font_folder_path).rglob('*.yaml'):
        file = path.name
        with open(str(path), 'r') as fp:
            try:
                font_config[path.name.strip('.yaml')] = safe_load(fp)
            except YAMLError as exc:
                raise exc
            if file == "glyphnames.yaml":
                try:
                    font_glyphnames_schema.validate(font_config['glyphnames'])
                except SchemaError as schema_error:
                    raise schema_error
            elif file == "classes.yaml":
                try:
                    font_class_schema.validate(font_config['classes'])
                except SchemaError as schema_error:
                    raise schema_error
                if not font_config['classes']['family_name'] == path.parent.name:
                    logging.warning("Family name {} in font configuration file doesn't match containing folder.".format(path.parent.name))
    font_config_dict = {path.parent.name: font_config}
    return font_config_dict


def register_font_path(font_path):
    # Caching seems to cause problems. Disable for now
    ff = fontfinder.FontFinder(useCache=False)
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


def is_registered_font(font_name):
    return font_name in pdfmetrics.getRegisteredFontNames()
