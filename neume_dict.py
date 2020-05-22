#!/usr/bin/python
# -*- coding: utf-8 -*-
from ruamel.yaml import safe_load, YAMLError

from neume import Neume

neume_class_dict = {}


class NeumeDict:
    """Open a font configuration file and serialize its contents.
    """
    def __init__(self, filepath: str = "fonts/KA New Stathis/classes.yaml"):
        self.dict = None
        #  font_dir = [inspect.stack()[0][1].rsplit('/', 1)[0] + "/fonts"]
        with open(filepath, 'r') as fp:
            try:
                font_class_dict = safe_load(fp)
            except YAMLError as exc:
                raise exc
            self.dict = font_class_dict

    def is_standalone(self, neume: Neume):
        if neume.font_family.endswith("Main"):
            return neume.name in self.dict['standAloneNeumes']
        if neume.font_family.endswith("Combo"):
            return neume.name in self.dict['standAloneNeumesCombo']
        if neume.font_family.endswith("Martyria"):
            return neume.name in self.dict['standAloneNeumesMartyria']
        else:
            return False
    
    def is_nonPreBreakingNeume(self, name: str = None):
        return name in self.dict['nonPreBreakingNeumes']
    
    def is_nonPostBreakingNeume(self, name: str = None):
        return name in self.dict['nonPreBreakingNeumes']

    def takes_lyric(self, neume: Neume, name: str = None):
        if neume.font_family.endswith("Main"):
            return neume.name in self.dict['neumesWithLyrics']
        if neume.font_family.endswith("Combo"):
            return neume.name in self.dict['neumesWithLyricsCombo']
        else:
            return False
