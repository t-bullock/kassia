import sys
from typing import Dict

from reportlab.platypus import SimpleDocTemplate


class ComplexDocTemplate(SimpleDocTemplate):
    """A SimpleDocTemplate with special helper functions to make life easier.
    """

    def set_pagesize_by_name(self, name: str):
        """Sets a ReportLab page size with the passed name.
        :param name: The name of the page size.
        """
        try:
            self.pagesize = getattr(sys.modules[__name__], name)
        except AttributeError as e:
            pass

    def set_margins(self, margins: Dict[str, int] = None):
        """Sets the page margins.
        :param margins: A dictionary of page margins.
        """
        '''if not margins:
            margins = {self.top_margin: 72,
                       self.bottom_margin: 72,
                       self.left_margin: 72,
                       self.right_margin: 72}'''
        self.topMargin = margins['top_margin']
        self.bottomMargin = margins['bottom_margin']
        self.leftMargin = margins['left_margin']
        self.rightMargin = margins['right_margin']
        self._calc()

    '''def _calc(self):
        self._rightMargin = self.pagesize[0] - self.rightMargin
        self._topMargin = self.pagesize[1] - self.topMargin
        self.width = self._rightMargin - self.leftMargin
        self.height = self._topMargin - self.bottomMargin'''

    @property
    def top(self) -> int:
        """Get the position at the top of the page, taking into account margins.
        The top of the page is the page height. When moving down the page, the position decreases.
        :return: Position at top of the page.
        """
        return self.pagesize[1] - self.topMargin

    @property
    def bottom(self) -> int:
        """Get the position at the bottom of the page, taking into account margins.
        The bottom of the page is essentially 0 (plus any bottom margins).
        :return: Position at bottom of the page.
        """
        return self.bottomMargin

    @property
    def left(self) -> int:
        """Get the position at the left size of the page, taking into account margins.
        :return: Position at the left of the page.
        """
        return self.leftMargin

    @property
    def right(self) -> int:
        """Get the position at the right size of the page, taking into account margins.
        :return: Position at the right of the page.
        """
        #return self.pagesize[0] - self.rightMargin
        return self._rightMargin

    @property
    def center(self) -> int:
        """Get the position at the center of the page.
        :return: Position at the center of the page.
        """
        return self.pagesize[0]/2
