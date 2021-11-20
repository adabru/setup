#!/usr/bin/python

# minimal imports for faster startup
import os
import errno


def run():
    import subprocess
    import urllib.request
    import re
    from datetime import datetime
    import time
    import sys
    from threading import Condition
    import signal

    from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout
    from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, Qt
    from PyQt5.QtGui import QFont

    class Pipe(QThread):
        toggle_signal = pyqtSignal()

        def __init__(self, path):
            super().__init__()
            self.path = path
            self._quit = False

        def run(self):
            while not self._quit:
                # wait for someone to write to the exit pipe
                with open(self.path, 'r') as f:
                    command = f.read()
                    self.toggle_signal.emit()

        def quit(self):
            self._quit = True
            # release pipe
            try:
                fd = os.open(self.path, os.O_WRONLY | os.O_NONBLOCK)
                os.close(fd)
            except:
                pass

    class Status(QThread):
        update_signal = pyqtSignal(str)

        def __init__(self, condition, is_visible):
            super().__init__()
            self.condition = condition
            self.is_visible = is_visible
            self.lastCpu = None
            self._quit = False
            self.s_cpu = '…'
            self.s_mem = '…'
            self.s_bat = '…'
            self.s_dat = '…'
            self.s_net = '…'
            self.s_srv = '…'

        def run(self):
            network = None
            serverstatus = None
            while not self._quit:
                with self.condition:
                    self.condition.wait_for(self.is_visible)
                self.s_dat = self._time()
                self._update()
                self.s_cpu = self._cpuload()
                self.s_mem = self._memory()
                self.s_bat = self._battery()
                self.s_dat = self._time()
                self._update()
                self.s_srv = self._serverstatus()
                self.s_net = self._network()
                self.s_dat = self._time()
                self._update()
                time.sleep(.5)

        def _update(self):
            # for supported html elements, see https://doc.qt.io/qt-5/richtext-html-subset.html
            message = '<div><p>%s</p><p>%s %s</p><p>%s</p><p>%s</p><p>%s</p></div>' % (
                self.s_cpu, self.s_net, self.s_srv, self.s_mem, self.s_bat, self.s_dat)
            self.update_signal.emit(message)

        def quit(self):
            self._quit = True
            with condition:
                condition.notify()

        def cat(self, file):
            with open(file, "r") as f:
                return f.read()

        def _network(self):
            network = subprocess.run('nmcli -t -f general.connection device show wlp2s0'.split(),
                                     encoding='UTF-8', capture_output=True).stdout.strip()
            network = network.removeprefix('GENERAL.CONNECTION:')
            network = '<font color=#8888ff>%s</font>' % network
            return network

        def _serverstatus(self):
            t0 = time.time()
            try:
                request = urllib.request.Request(
                    'https://adabru.de', method='HEAD')
                with urllib.request.urlopen(request) as response:
                    if response.status == 200:
                        status = '%dms' % ((time.time() - t0) * 1000)
                    else:
                        status = '🕱'
            except urllib.error.URLError:
                status = '🕱'
            return status

        def _memory(self):
            regex = re.compile(
                'MemAvailable: *([0-9]+).*SwapFree: *([0-9]+)', re.S)
            m = regex.search(self.cat('/proc/meminfo'))
            mem, swap = int(m.group(1))/1e6, int(m.group(2))/1e6
            color = '#ff4444' if mem < 1 else '#aaaaaa'
            return '<font color=%s>%.1f %.1f</font>' % (
                color, mem, swap)

        def _battery(self):
            battery = None
            try:
                battery = (float(self.cat('/sys/class/power_supply/BAT1/energy_now'))
                           / float(self.cat('/sys/class/power_supply/BAT1/energy_full')))
            except FileNotFoundError:
                pass
            try:
                battery = (float(self.cat('/sys/class/power_supply/BAT1/charge_now'))
                           / float(self.cat('/sys/class/power_supply/BAT1/charge_full')))
            except FileNotFoundError:
                pass
            mode = '🔌' if int(
                self.cat('/sys/class/power_supply/ACAD/online')) else '🔋'
            if not battery:
                battery = 0
            if battery > .3:
                color = '#aaaaaa'
            elif battery > .15:
                color = '#aaaa22'
            else:
                color = '#ff4444'
            return '<font color=%s>%.1f</font>%s' % (
                color, 100*battery, mode)

        def _time(self):
            return datetime.now().strftime("<font color=#aaaaaa>%Y-%m-%d W%V</font>    %H:%M:%S")

        def _cpuload(self):
            def cpu():
                def sum(line):
                    x = line.split()
                    return (int(x[1]) + int(x[2]) + int(x[3]) + int(x[6]) + int(x[7]) + int(x[8]) + int(x[9]) + int(x[10]),
                            int(x[4]) + int(x[5]))
                return [sum(line) for line in self.cat('/proc/stat').split('\n')[1:5]]

            def cpuload(curr, last):
                return '{:3.0%}'.format(float(curr[0]-last[0]) / (curr[0]-last[0]+curr[1]-last[1]+1))
            currCpu = cpu()
            if self.lastCpu == None:
                self.lastCpu = currCpu
            result = '<font color=#aaaaaa>%s</font>' % ' '.join([cpuload(curr, last)
                                                                 for curr, last in zip(currCpu, self.lastCpu)])
            self.lastCpu = currCpu
            return result

    class App(QObject):
        def __init__(self, condition):
            super().__init__()
            self.condition = condition
            self.widget = QWidget()
            self.label = QLabel()
            self.label.setStyleSheet('QLabel { font-size: 12pt; }')
            layout = QHBoxLayout()
            self.widget.setLayout(layout)
            layout.addWidget(self.label)
            self.widget.setGeometry(100, 100, 100, 200)
            self.label.move(50, 20)
            self.widget.setWindowTitle("statuswindow")
            self.widget.show()

        def visible(self):
            return self.widget != None and self.widget.isVisible()

        def toggle(self):
            if self.widget.isVisible():
                self.widget.hide()
            else:
                self.widget.show()
                with self.condition:
                    self.condition.notify()

        @pyqtSlot(str)
        def update(self, text):
            self.label.setText(text)

    condition = Condition()
    qapp = QApplication(sys.argv)
    app = App(condition)
    statusthread = Status(condition, app.visible)
    pipethread = Pipe(pipepath)
    # thread safe communication, QtGui requires all gui related code to be called from the same thread
    statusthread.update_signal.connect(app.update, Qt.QueuedConnection)
    # design flaw, see https://stackoverflow.com/q/4938723/6040478
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    pipethread.toggle_signal.connect(app.toggle)
    statusthread.start()
    pipethread.start()
    qapp.exec_()
    print('Quit, collecting threads.')
    statusthread.quit()
    pipethread.quit()
    statusthread.wait()
    pipethread.wait()
    # signal.pause()


# nonblocking pipe communication, see https://stackoverflow.com/a/34754523/6040478
pipepath = '/tmp/statuswindow_toggle'
try:
    os.mkfifo(pipepath)
except FileExistsError:
    pass
try:
    fd = os.open(pipepath, os.O_WRONLY | os.O_NONBLOCK)
    # someone listens, the program is already running
    os.close(fd)
except OSError as ex:
    if ex.errno == errno.ENXIO:
        # no one listening on the pipe yet, start the main program
        run()
    else:
        raise ex
