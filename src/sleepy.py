from PyQt5.QtWidgets import QMainWindow, QWidget, QRadioButton, \
    QHBoxLayout, QVBoxLayout, QApplication, QLineEdit, QLabel, \
    QPushButton, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont

import subprocess
import weakref
import os
import time


class LabeledLineEdit(QWidget):

    DEFAULT_LINE_EDIT_WIDTH = 30

    def __init__(self, label_text='', line_edit_text='', parent=None):
        super().__init__(parent)

        self.label = QLabel(label_text, self)
        self.line_edit = QLineEdit(self)
        self.line_edit.setFixedWidth(self.DEFAULT_LINE_EDIT_WIDTH)
        self.line_edit.setText(line_edit_text)

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        self.setLayout(layout)

    def text(self):
        return self.line_edit.text()

    def set_text(self, text):
        self.line_edit.setText(text)


class CountdownWidget(QWidget):

    def __init__(self, total_time, started_at, close_action, parent=None):
        super().__init__(parent)

        self.time_left = total_time
        self.started_at = started_at
        self.close_action = close_action

        self.label = QLabel('Time left: {}'.format(total_time))
        font = QFont()
        font.setPixelSize(23)
        self.label.setFont(font)
        self.label.setFixedSize(200, 40)
        self.stop_btn = QPushButton('Stop')
        self.stop_btn.clicked.connect(self.close)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.stop_btn)
        self.setLayout(main_layout)

    def update(self):
        curr_time = time.perf_counter()
        time_passed = int(curr_time - self.started_at)
        self.label.setText('Time left: {}'.format(self.time_left - time_passed))

    def notify(self):
        self.close()

    def close(self):
        self.close_action()
        super().close()


class TimedAction(object):

    def __init__(self, total_time, action):
        """
        :param total_time: total_time in miliseconds
        :param action: function to be called after "total_time"
        :param observers: list of observers
        """
        self.total_time = total_time
        self._command = action
        self._observers = []

    def start(self):
        QTimer.singleShot(self.total_time, self.run)

    def register(self, observer):
        if not hasattr(observer, 'notify'):
            raise NotImplementedError('Observers must implement "notify" method.')
        self._observers.append(weakref.ref(observer))

    def run(self):
        self._notify()
        self._command()

    def _notify(self):
        length = len(self._observers)
        index = 0
        while index < length:
            ref = self._observers[index]
            obs = ref()

            if obs is None:
                self._observers.pop(index)
                length -= 1
                continue

            obs.notify()
            index += 1



class Sleepy(QMainWindow):

    def __init__(self):
        super().__init__(None)

        self.shutdown = lambda: subprocess.call(["shutdown", "/s"])
        self.sleep = lambda: os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        self.action = None

        self.setup_central_widget()
        self.show()

    def setup_central_widget(self):
        self.central_widget = QWidget(self)

        rblayout = QHBoxLayout()
        self.rb_sleep = QRadioButton('Sleep', self.central_widget)
        self.rb_shutdown = QRadioButton('Shutdown', self.central_widget)
        rblayout.addWidget(self.rb_sleep)
        rblayout.addWidget(self.rb_shutdown)

        lelayout = QHBoxLayout()
        self.seconds = LabeledLineEdit('Seconds:', '0', self.central_widget)
        self.minutes = LabeledLineEdit('Minutes:', '0', self.central_widget)
        self.hours = LabeledLineEdit('Hours:', '0', self.central_widget)
        lelayout.addWidget(self.seconds)
        lelayout.addWidget(self.minutes)
        lelayout.addWidget(self.hours)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton('OK')
        self.ok_btn.clicked.connect(self.start)
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(rblayout)
        self.main_layout.addLayout(lelayout)
        self.main_layout.addLayout(btn_layout)
        self.central_widget.setLayout(self.main_layout)

        self.setCentralWidget(self.central_widget)

    def start(self):
        seconds = int(self.seconds.text())
        minutes = int(self.minutes.text())
        hours = int(self.hours.text())
        total_seconds = seconds + 60 * minutes + 60 * 60 * hours

        self.action = None
        if self.rb_shutdown.isChecked():
            self.action = TimedAction(total_seconds * 1000, self.shutdown)
        elif self.rb_sleep.isChecked():
            self.action = TimedAction(total_seconds * 1000, self.sleep)

        if self.action is None:
            msg = QMessageBox()
            msg.setText('Select what action to execute(shutdown/sleep) !')
            msg.exec_()
            return

        self.setup_countdown(total_seconds)
        self.action.start()

    def setup_countdown(self, total_time):
        self.countdown_timer = QTimer()
        started_at = time.perf_counter()

        countdown_widget = CountdownWidget(total_time, started_at, self.reset_layout)
        self.action.register(countdown_widget)
        self.setCentralWidget(countdown_widget)

        self.countdown_timer.timeout.connect(countdown_widget.update)
        self.countdown_timer.start(1000)

    def reset_layout(self):
        self.action = None
        self.setup_central_widget()


if __name__ == '__main__':
    app = QApplication([])
    w = Sleepy()
    w.show()
    app.exec_()