from matplotlib.widgets import RectangleSelector
import numpy as np
import matplotlib.pyplot as plt
from surveyline import SurveyLine
from matplotlib import collections  as mc
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.text import Text
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QPushButton
from gui import Ui_MainWindow

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

import sys

list_of_lines = []  # contains all SurveyLines objects read from the text file


class Mywindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.fig1 = Figure()  # creates the main Figure container for plot
        self.ax = self.ui.fig1.add_subplot(111)  # adds actual plot to the figure and returns Axes object
        self.ax.grid(True)

        self.ui.mplfigs.itemClicked.connect(
            self.toggle_line)  # connects the itemClicked signal to a highlight_line method
        self.selected_line = None  # represents selected lien from the List widget

        self.ui.actionDisplay_line_name.triggered.connect(self.display_line_names)
        self.line_labels = []  # initialisation instance variable for the line name

        self.ui.mplfigs.installEventFilter(self)

    def eventFilter(self, source, event):
        """
        Creates a context menu on each item of teh QListWidget
        """
        if event.type() == QtCore.QEvent.ContextMenu and source is self.ui.mplfigs:
            menu = QtWidgets.QMenu()
            çompleted =  menu.addAction('Completed')
            not_run = menu.addAction('Not run')
            re_run = menu.addAction('To be re-run')
            action = menu.exec_(event.globalPos())
            if action == çompleted:
                item = source.itemAt(event.pos())
                print(item.text())
                print('Completed')
            elif action == not_run:
                print('Not run')
            elif action == re_run:
                print('Re-run')
            return True
        return super(Mywindow, self).eventFilter(source, event)

    def toggle_line(self, item):
        """
        Highlights the line that corresponds to the one selected from the list and changes its color
        and thickness
        """
        print(f'Selected line {self.find_line(item.text()).line_name}')

        if self.selected_line is not None:
            print(self.selected_line.get_color())
            self.selected_line.set_color(color='C0')  # default colour is C0
            self.selected_line.set_linewidth(1.5)  # default linewidth is 1.5
            self.ui.canvas.draw()

        self.selected_line = self.find_line(item.text())

        self.selected_line.set_color(color='orange')
        self.selected_line.set_linewidth(2.5)

        self.ui.canvas.draw()

    def display_line_names(self, state):
        """
        Display a label next to each plotted line with its name or remove them depending on the checkbox state
        """
        print(state)

        if state is True:
            for each in list_of_lines:
                p1 = self.ax.transData.transform_point(
                    (each.get_xdata()[0], each.get_ydata()[0]))
                p2 = self.ax.transData.transform_point(
                    (each.get_xdata()[1], each.get_ydata()[1]))

                dy = (p2[1] - p1[1])
                dx = (p2[0] - p1[0])
                trans_angle = np.degrees(np.arctan2(dy, dx))

                single_label = self.ax.text(each.get_xdata()[1], each.get_ydata()[1],
                                            each.line_name,
                                            rotation=trans_angle, rotation_mode='anchor', va='center')
                self.line_labels.append(single_label)  # add each text object to a list so then can be deleted
        else:
            for each in self.line_labels:
                each.remove()  # removes each Text object from the plot
            self.line_labels.clear()  # removes or references from the list

        self.ui.canvas.draw()

    def addmpl(self, fig):
        self.ui.canvas = FigureCanvas(fig)  # always use self.ui to refere to the components
        self.ui.mplvl.addWidget(self.ui.canvas)
        self.ui.canvas.show()
        self.ui.toolbar = NavigationToolbar(self.ui.canvas,
                                            self.ui.mplwindow, coordinates=True)
        self.ui.mplvl.addWidget(self.ui.toolbar)

    def display(self):
        # all_lines = []

        # self.ui.fig1 = Figure()

        # ax = self.ui.fig1.add_subplot(111)
        # ax.grid(True)

        for each in list_of_lines:
            print(
                "Line name : {}, starting coord {} E, {} N, ending coords {} E, {} N".format(each.line_name,
                                                                                             each.get_xdata()[0],
                                                                                             each.get_ydata()[0],
                                                                                             each.get_xdata()[1],
                                                                                             each.get_ydata()[1]),
                end='\n')

            a_line = self.ax.add_line(each)
            # all_lines.append(a_line)    #a list with all lines for the given survey project
            self.ui.mplfigs.addItem(each.line_name)

        self.ax.autoscale()
        # ax.margins(0.1)

        print("Found {} lines".format(len(list_of_lines)))
        print("Length of the first line {}m".format(list_of_lines[0].length_of_line))

        def onpick1(event):
            print('I am clicked')
            print(event.artist)
            test = event.artist
            print(test.co)
            if isinstance(event.artist, Line2D):
                thisline = event.artist
                xdata = thisline.get_xdata()
                ydata = thisline.get_ydata()
                ind = event.ind
                print('onpick1 line:', np.column_stack([xdata[ind], ydata[ind]]))
            elif isinstance(event.artist, Rectangle):
                patch = event.artist
                print('onpick1 patch:', patch.get_path())
            elif isinstance(event.artist, Text):
                text = event.artist
                print('onpick1 text:', text.get_text())

        # plt.legend()
        # fig.canvas.mpl_connect('pick_event', onpick1)
        # plt.grid()

        # plt.show()

    def find_line(self, line_name):
        """
            Searches for the line with the same name as the one provided as a parameter.
            Its purpose is to return a SurveyLine object that can be manipulated on the plot
            """
        for each in list_of_lines:
            if each.line_name == line_name:
                return each


def load_lines():
    """
    Loads the lines from the txt file. A required format uses tab delimiter and 5 columns. First is the line name which
    then follows on to SOL Easting and Nrthing and EOL Easting and Northings.
    """
    filename = 'AkerBP_NSG_V6_Int.txt'

    with open(filename, 'r') as reader:
        for line in reader:
            list_of_lines.append(
                SurveyLine([float(line.split(sep='\t')[1]), float(line.split(sep='\t')[3])],
                           [float(line.split(sep='\t')[2]), float(line.split(sep='\t')[4].strip())],
                           line.split(sep='\t')[0])
            )


def main():
    load_lines()

    app = QtWidgets.QApplication([])

    application = Mywindow()
    application.display()
    application.addmpl(application.ui.fig1)

    application.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
