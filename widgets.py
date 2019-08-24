import sys
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QSizePolicy

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation


from poker_utils import load_poker, poker_distance, annotate_poker
from complex import Ui_MainWindow
import forcelayout as fl


class PlotCanvas(FigureCanvas):
    progress_signal = QtCore.pyqtSignal(str, int)  # stage, progress

    def __init__(self, parent=None, width=5, height=4, dpi=100, title=None):

        FigureCanvas.__init__(self,
                              figure=Figure(
                                  figsize=(width, height),
                                  dpi=dpi,
                                  # tight_layout=True
                                    )
                              )
        self.ax = self.figure.add_subplot(111)
        self._title = title
        if isinstance(self._title, str) and self._title.strip():
            self.ax.set_title(self._title)

        self.ani = None

        self.setParent(parent)
        FigureCanvas.setSizePolicy(
            self,
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        FigureCanvas.updateGeometry(self)
        self.draw()

    def plot(self, dataset, algorithm, distance):
        self.ax.cla()
        if isinstance(self._title, str) and self._title.strip():
            self.ax.set_title(self._title)

        self.ani = fl.draw_spring_layout_animated(
            dataset=dataset,
            algorithm=algorithm,
            distance=distance,
            size=10,
            alpha=0.7,
            color_by=lambda d: d[10],
            annotate=annotate_poker,
            algorithm_highlights=True,
            figure=self.figure,
            ax=self.ax
        )
        self.draw()

    def clear(self):
        self.ax.cla()
        if isinstance(self._title, str) and self._title.strip():
            self.ax.set_title(self._title)
        self.draw()

    def stop_plot(self):
        if isinstance(self.ani, FuncAnimation):
            self.ani.event_source.stop()

    def start_plot(self):
        if isinstance(self.ani, FuncAnimation):
            self.ani.event_source.start()
