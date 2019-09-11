from typing import Dict, Tuple

from reportlab.lib.pagesizes import LETTER


class Page:
    def __init__(self, size: Tuple = LETTER,
                 top_margin: int = 72,
                 bottom_margin: int = 72,
                 left_margin: int = 72,
                 right_margin: int = 72,
                 ):
        self.size = size
        self.top_margin = top_margin
        self.bottom_margin = bottom_margin
        self.left_margin = left_margin
        self.right_margin = right_margin

    @property
    def width(self) -> int:
        """Get the page width, minus margins."""
        return self.size[0] - (self.left_margin + self.right_margin)

    @property
    def height(self) -> int:
        """Get the position at the bottom of the page, taking into account margins.
        :return: Position at bottom of the page.
        """
        return self.size[1] - self.bottom_margin

    @property
    def top(self) -> int:
        """Get the position at the top of the page, taking into account margins.
        The top of the page is the page height. When moving down the page, the position decreases.
        :return: Position at top of the page.
        """
        return self.size[1] - self.top_margin

    @property
    def bottom(self) -> int:
        """Get the position at the bottom of the page, taking into account margins.
        The bottom of the page is basically 0 (plus any bottom margins).
        :return: Position at bottom of the page.
        """
        return self.bottom_margin

    @property
    def left(self) -> int:
        """Get the position at the left size of the page, taking into account margins.
        :return: Position at the left of the page.
        """
        return self.left_margin

    @property
    def right(self) -> int:
        """Get the position at the right size of the page, taking into account margins.
        :return: Position at the right of the page.
        """
        return self.size[0] - self.right_margin

    @property
    def center(self) -> int:
        """Get the position at the center of the page.
        :return: Position at the center of the page.
        """
        return self.size[0]/2

    def is_top_of_page(self, cur_pos_y: int) -> bool:
        """Checks whether the cursor is at the top of the page, taking margins into consideration.
        :return: Whether passed y position is at top of page.
        """
        return cur_pos_y == self.top

    def is_bottom_of_page(self, cur_pos_y: int) -> bool:
        """Checks whether the cursor is at (or past) the bottom of the page, taking margins into consideration.
        :return: Whether passed y position is at top of page.
        """
        return cur_pos_y <= self.bottom
    def set_margins(self, margins: Dict[str, int] = None):
        """Sets the page margins.
        :param margins: A dictionary of page margins.
        """
        if not margins:
            margins = {self.top_margin: 72,
                       self.bottom_margin: 72,
                       self.left_margin: 72,
                       self.right_margin: 72}
        self.top_margin = margins['top_margin']
        self.bottom_margin = margins['bottom_margin']
        self.left_margin = margins['left_margin']
        self.right_margin = margins['right_margin']
