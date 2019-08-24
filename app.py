from PyQt5 import QtCore, QtGui, QtWidgets
from ui.ui import Ui_Form
import sys
import widgets
import os
from poker_utils import read_dataset, poker_distance, annotate_poker, base_dir
import time
import psutil


widgets.fl.utils.signals = {}


class Worker(QtCore.QThread):
    # 创建信号，发送系统监控数据
    status_signal = QtCore.pyqtSignal(float, float, str, float, float, float, float)
    # my_cpu, my_ram, cpu load, ram, cpu_freq_current, cpu_freq_min, cpu_freq_max

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.flag = True
        self.process = psutil.Process(pid=os.getpid())

    def __del__(self):
        self.flag = False
        if self.isRunning():
            self.wait()

    def run(self) -> None:
        while self.flag:
            time.sleep(0.1)

            my_ram = self.process.memory_info()[0] / 2 ** 20
            my_cpu = self.process.cpu_percent(interval=None)

            sys_ram = psutil.virtual_memory()[2]  # ram
            sys_cpu_cores = psutil.cpu_percent(interval=None, percpu=True)  # cpu
            current_freq, min_freq, max_freq = psutil.cpu_freq()  # freq

            _ = []
            for i, c in enumerate(sys_cpu_cores):
                _.append('Core_{}: {:0>6.2f}%'.format(i, c))
            sys_cpu_cores = '<br>'.join(_)
            self.status_signal.emit(my_cpu, my_ram, sys_cpu_cores, sys_ram, current_freq, min_freq, max_freq)


class App(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.move_to_center()
        self.setWindowTitle('Animation Plot')
        self.setMinimumWidth(1024)
        self.setMinimumHeight(600)

        self._timer = QtCore.QTimer()
        self._time = QtCore.QTime(0, 0, 0)
        self._timer.timeout.connect(self.time_event)
        self.label_time.setText('00:00:00')
        
        self.layout_canvas = QtWidgets.QGridLayout(self.group_box_firgure)

        self.canvas_chalmer = widgets.PlotCanvas(self.group_box_firgure, title='Chalmer Animation')
        self.layout_canvas.addWidget(self.canvas_chalmer, 0, 0, 1, 1)
        widgets.fl.utils.signals['chalmer'] = self.canvas_chalmer.progress_signal

        self.canvas_hybrid = widgets.PlotCanvas(self.group_box_firgure, title='Hybrid Animation')
        self.layout_canvas.addWidget(self.canvas_hybrid, 0, 0, 1, 1)
        widgets.fl.utils.signals['hybrid'] = self.canvas_hybrid.progress_signal

        self.canvas_pivot = widgets.PlotCanvas(self.group_box_firgure, title='Pivot Animation')
        self.layout_canvas.addWidget(self.canvas_pivot, 0, 0, 1, 1)
        widgets.fl.utils.signals['pivot'] = self.canvas_pivot.progress_signal

        self.canvas_ls = [self.canvas_pivot, self.canvas_hybrid, self.canvas_chalmer]
        self.algorithm_ls = [widgets.fl.Pivot, widgets.fl.Hybrid, widgets.fl.NeighbourSampling]
        self.current_canvas = None
        self.current_algorithm = None

        self.comb_algorithm.clear()
        self.comb_algorithm.currentIndexChanged.connect(self.chane_canvas)
        self.comb_algorithm.addItems(['Pivot', 'Hybrid', 'Chalmer'])
        self.comb_algorithm.setCurrentIndex(0)

        self.canvas_hybrid.progress_signal.connect(self.handle_hybrid_progress)
        self.canvas_chalmer.progress_signal.connect(self.handle_chalmer_progress)
        self.canvas_pivot.progress_signal.connect(self.handle_pivot_progress)

        # self.btn_load.clicked.connect(self.ask_dataset)

        self.csv_fp = None

        self.btn_start.clicked.connect(self.canvas_plot_start)
        self.btn_stop.clicked.connect(self.canvas_plot_stop)
        self.btn_clrear.clicked.connect(self.canvas_plot_clear)
        self.label_dataset_name.setText('<span style="color: red;"><b>Please Chose proper DataSet</b></span>')

        self.worker = Worker(self)
        self.worker.status_signal.connect(self.update_status)  # 接受信号
        self.worker.start()

        dataset_size_ls = []
        self.poker_dir = os.path.join(base_dir, 'datasets', 'poker')
        for fn in os.listdir(self.poker_dir):
            _, ext = os.path.splitext(fn)
            if not ext.lower() == '.csv':
                continue
            if _.startswith('poker') and len(_) > 5:
                try:
                    s = int(_[5:])
                    dataset_size_ls.append(s)
                except (TypeError, ValueError):
                    continue
        dataset_size_ls.sort()

        self.comb_size.clear()
        self.comb_size.currentIndexChanged.connect(self.choose_dataset)
        self.comb_size.addItems([str(i) for i in dataset_size_ls])
        self.comb_size.setCurrentIndex(4)

    def update_status(self, my_cpu: float, my_ram: float,
                      sys_cpu_cores: str, sys_ram, current_freq, min_freq, max_freq):
        self.label_cpu_load.setText('{}'.format(sys_cpu_cores))
        self.label_ram.setText('{}%'.format(round(sys_ram, 2)))
        self.label_freq.setText('''
<table>
    <tbody>
    <tr>
        <td>Current:</td>
        <td> {:0>7.2f}Mhz</td>
    </tr>
    <tr>
        <td>Min:</td>
        <td> {:0>7.2f}Mhz</td>
    </tr>
    <tr>
        <td>Max:</td>
        <td> {:0>7.2f}Mhz</td>
    </tr>
    </tbody>
</table>'''.format(
            round(current_freq, 2), round(min_freq, 2), round(max_freq, 2)
        ))

        self.label_my_cpu.setText('{}%'.format(my_cpu))
        self.label_my_ram.setText('{:.2f}MB'.format(my_ram))

    def time_event(self):
        self._time = self._time.addSecs(1)
        # print(self._time)
        self.label_time.setText(self._time.toString('hh:mm:ss'))
        
    def handle_pivot_progress(self, stage, percent):
        print('Pivot: {}, {}'.format(stage, percent))
        self.progress_bar.setValue(percent)
        if isinstance(stage, str) and stage:
            self.progress_bar.setFormat('{} %p%'.format(stage))
        else:
            self.progress_bar.setFormat('%p%')

    def handle_chalmer_progress(self, stage, percent):
        print('Chalmer: {}, {}'.format(stage, percent))
        self.progress_bar.setValue(percent)
        if isinstance(stage, str) and stage:
            self.progress_bar.setFormat('{} %p%'.format(stage))
        else:
            self.progress_bar.setFormat('%p%')

    def handle_hybrid_progress(self, stage, percent):
        print('Hybrid: {}, {}'.format(stage, percent))

        self.progress_bar.setValue(percent)
        if isinstance(stage, str) and stage:
            self.progress_bar.setFormat('{} %p%'.format(stage))
        else:
            self.progress_bar.setFormat('%p%')

    def chane_canvas(self):
        index = self.comb_algorithm.currentIndex()
        if 0 <= index < len(self.canvas_ls):
            self.current_canvas = self.canvas_ls[index]
            self.current_algorithm = self.algorithm_ls[index]
        else:
            return

        for canvas in self.canvas_ls:
            canvas.hide()
            canvas.stop_plot()

        self.current_canvas.show()
        self.progress_bar.setValue(0)
        self.progress_bar.hide()

        self.canvas_plot_clear()

        # self.csv_fp = None
        # self.label_dataset_name.setText('')

    def canvas_plot_start(self):
        if self.csv_fp is None \
                or (isinstance(self.csv_fp, str) and not os.path.exists(self.csv_fp)):
            return self.show_warning(message='Please load proper dataset!')
        self.progress_bar.show()
        dataset = read_dataset(fp=self.csv_fp)

        self._time = QtCore.QTime(0, 0, 0)
        self.label_time.setText('00:00:00')
        self._timer.start(1000)

        self.current_canvas.plot(
            dataset=dataset,
            algorithm=self.current_algorithm,
            distance=poker_distance)

    def canvas_plot_stop(self):
        if not isinstance(self.current_canvas, widgets.PlotCanvas):
            return self.show_warning(message='Animation not started yet.')
        self.current_canvas.stop_plot()
        self.mute_progress_bar()
        self._timer.stop()

    def canvas_plot_clear(self):
        if not isinstance(self.current_canvas, widgets.PlotCanvas):
            return self.show_warning(message='Please chose a plot type')
        self.canvas_plot_stop()

        self.current_canvas.clear()
        self.label_time.setText('00:00:00')

    def mute_progress_bar(self):
        self.progress_bar.setValue(0)
        self.progress_bar.hide()

    def choose_dataset(self):
        '''choose size of dataset'''
        index = self.comb_size.currentIndex()

        if index < 0:
            return
        fn = 'poker{}.csv'.format(self.comb_size.currentText())

        self.csv_fp = os.path.join(self.poker_dir, fn)
        print(index, fn, self.csv_fp)

        self.label_dataset_name.setText(fn)
        self.update()

    def ask_dataset(self):
        file_path, file_type = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Chose DataSet', '.', "CSV Files (*.csv)"
        )
        if file_path and os.path.exists(file_path):
            self.csv_fp = file_path
            dir_name, fn = os.path.split(file_path)
            self.label_dataset_name.setText(fn)

        else:
            pass

    def move_to_center(self):
        ''''''
        qtRectangle = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def show_warning(self, message, title='Warning'):
        reply = QtWidgets.QMessageBox.warning(
            self, title, message, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            return True
        else:
            return False


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    m = App()
    m.show()
    sys.exit(app.exec_())
