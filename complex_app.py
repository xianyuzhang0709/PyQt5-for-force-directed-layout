import sys
import matplotlib
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QSizePolicy

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation

matplotlib.use("Qt5Agg")

from poker_utils import load_poker, poker_distance, annotate_poker
from complex import Ui_MainWindow
import forcelayout as fl


fl.utils.signals = {}


class PlotCanvas(FigureCanvas):

    progress_signal = QtCore.pyqtSignal(str, int)  # stage, progress

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        FigureCanvas.__init__(self,
                              figure=Figure(
                                  figsize=(width, height),
                                  dpi=dpi,
                                  # tight_layout=True
                                    )
                              )
        self.ax = self.figure.add_subplot(111)

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

        self.ani = fl.draw_spring_layout_animated(
            dataset=dataset,
            algorithm=algorithm,
            distance=distance,
            size=5,
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
        self.draw()

    def stop_plot(self):
        if isinstance(self.ani, FuncAnimation):
            self.ani.event_source.stop()


class MainApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)

        self.frame_chalmer_layout = QtWidgets.QGridLayout(self.frame_chalmer)
        self.canvas_chalmer = PlotCanvas(self.frame_chalmer)
        self.frame_chalmer_layout.addWidget(self.canvas_chalmer, 0, 0, 1, 1)

        self.frame_hybird_layout = QtWidgets.QGridLayout(self.frame_hybird)
        self.canvas_hybird = PlotCanvas(self.frame_hybird)
        self.frame_hybird_layout.addWidget(self.canvas_hybird, 0, 0, 1, 1)
        fl.utils.signals['hybrid'] = self.canvas_hybird.progress_signal

        #
        self.frame_pivot_layout = QtWidgets.QGridLayout(self.frame_pivot)
        self.canvas_pivot = PlotCanvas(self.frame_pivot)
        self.frame_pivot_layout.addWidget(self.canvas_pivot, 0, 0, 1, 1)
        fl.utils.signals['pivot'] = self.canvas_pivot.progress_signal

        self.btn_chalmer.clicked.connect(self.plot_chalmer)
        self.btn_hybird.clicked.connect(self.plot_hybird)
        self.btn_pivot.clicked.connect(self.plot_pivot)
        fl.utils.signals['chalmer'] = self.canvas_chalmer.progress_signal

        self.canvas_hybird.progress_signal.connect(self.handle_hybird_progress)
        self.canvas_chalmer.progress_signal.connect(self.handle_chalmer_progress)
        self.canvas_pivot.progress_signal.connect(self.handle_pivot_progress)

    def handle_pivot_progress(self, stage, percent):
        print(stage, percent)
        if (percent==100):
            self.canvas_pivot.stop_plot
            print("stopped")


    def handle_chalmer_progress(self, stage, percent):
        print(stage, percent)
        if (percent==100):
            self.canvas_pivot.stop_plot
            print("stopped")

    def handle_hybird_progress(self, stage, percent):
        print(stage, percent)
        if (percent==100):
            self.canvas_pivot.stop_plot
            print("stopped")



    def plot_chalmer(self):
        dataset = load_poker(500)
        self.canvas_chalmer.plot(
            dataset=dataset,
            algorithm=fl.NeighbourSampling,
            distance=poker_distance)

    def plot_hybird(self):
        dataset = load_poker(500)
        self.canvas_hybird.plot(
            dataset=dataset,
            algorithm=fl.Hybrid,
            distance=poker_distance)

    def plot_pivot(self):
        dataset = load_poker(500)
        self.canvas_pivot.plot(
            dataset=dataset,
            algorithm=fl.Pivot,
            distance=poker_distance)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    center = QtWidgets.QDesktopWidget().availableGeometry().center()
    m = MainApp()
    m.show()
    sys.exit(app.exec_())


