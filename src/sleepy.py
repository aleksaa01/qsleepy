from PyQt5.QtWidgets import QMainWindow, QWidget, QRadioButton, \
    QHBoxLayout, QVBoxLayout, QApplication, QLineEdit, QLabel, \
    QPushButton, QMessageBox
from PyQt5.QtCore import QTimer

import subprocess
import os


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


class Sleepy(QMainWindow):

    def __init__(self):
        super().__init__(None)

        self.shutdown = lambda: subprocess.call(["shutdown", "/s"])
        self.sleep = lambda: os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        self.countdown_timer = QTimer()
        self.time_passed = 0

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
        self.show()

    def start(self):
        seconds = int(self.seconds.text())
        minutes = int(self.minutes.text())
        hours = int(self.hours.text())
        total_seconds = seconds + 60 * minutes + 60 * 60 * hours

        action = None
        if self.rb_shutdown.isChecked():
            action = self.shutdown
        elif self.rb_sleep.isChecked():
            action = self.sleep

        if action is None:
            msg = QMessageBox()
            msg.setText('Select what action to execute(shutdown/sleep) !')
            msg.exec_()
            return

        print('INFO:', total_seconds, action)
        QTimer.singleShot(total_seconds * 1000, action)


if __name__ == '__main__':
    app = QApplication([])
    w = Sleepy()
    w.show()
    app.exec_()