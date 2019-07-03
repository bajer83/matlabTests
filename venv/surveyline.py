import math
from matplotlib.lines import Line2D


class SurveyLine(Line2D):

    def __init__(self, xdata, ydata, name):
        super().__init__(xdata, ydata)  # initialises constructor fo the parent class Line2D which requires xdata, ydata
        self._line_name = name          # name of the line

    @property
    def line_name(self):
        return self._line_name

    @property
    def length_of_line(self):
        difference_eastings = math.fabs(float(self.get_xdata()[0]) - float(self.get_xdata()[1]))
        difference_northings = math.fabs(float(self.get_ydata()[0]) - float(self.get_ydata()[1]))
        hypotenues = math.hypot(difference_eastings, difference_northings)
        return round(hypotenues, 2)
