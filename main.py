import sys
import subprocess
import PySide6.QtWidgets as Qw
from PySide6.QtWidgets import QMessageBox
from datetime import datetime


class MainWindow(Qw.QMainWindow):
    def __init__(self, a_ip, b_ip, c_ip):
        super().__init__()

        self.window_position_x = 100
        self.window_position_y = 50
        self.window_width = 640
        self.window_height = 240
        self.log_file_path = 'log.txt'
        self.destination_ip = []
        self.a_ip = a_ip
        self.b_ip = b_ip
        self.c_ip = c_ip

        # window title setting
        self.setWindowTitle('Call Bell')

        # window size and position setting
        self.setFixedSize(self.window_width, self.window_height)

        # 'Call A' button settings
        self.btn_call_a = Qw.QPushButton('Call A', self)
        self.btn_call_a.setGeometry(10, 10, 100, 20)
        self.btn_call_a.clicked.connect(self.btn_call_a_clicked)

        # 'Call B' button settings
        self.btn_call_b = Qw.QPushButton('Call B', self)
        self.btn_call_b.setGeometry(130, 10, 100, 20)
        self.btn_call_b.clicked.connect(self.btn_call_b_clicked)

        # 'Call C' button settings
        self.btn_call_c = Qw.QPushButton('Call C', self)
        self.btn_call_c.setGeometry(260, 10, 100, 20)
        self.btn_call_c.clicked.connect(self.btn_call_c_clicked)

        # 'Call All' button settings
        self.btn_call_all = Qw.QPushButton('Call All', self)
        self.btn_call_all.setGeometry(390, 10, 100, 20)
        self.btn_call_all.clicked.connect(self.btn_call_all_clicked)

        # 'log' button settings
        self.btn_log = Qw.QPushButton('open "log.txt"', self)
        # self.btn_log.setGeometry(window_width - 150, window_height - 20, 140, 20)
        self.btn_log.setGeometry(520, 10, 100, 20)
        self.btn_log.clicked.connect(self.btn_log_clicked)

        # text box
        self.tb_log = Qw.QTextEdit('', self)
        self.tb_log.setReadOnly(True)
        self.tb_log.setGeometry(10, 40, 620, 170)
        self.tb_log.setPlaceholderText('(ここに実行ログを表示します)')
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f'[{current_time}] Program started.'
        self.tb_log.append(log_message)

        # status bar
        self.sb_status = Qw.QStatusBar()
        self.setStatusBar(self.sb_status)
        self.sb_status.setSizeGripEnabled(False)
        self.sb_status.showMessage('Program started.')

    def send_request(self, ips):
        try:
            completed_process = subprocess.run(['python', 'send-request.py'] + ips,
                                               capture_output=True, text=True)
            output = completed_process.stdout.strip()
            self.log_output(output)
            self.log_output('Finishing send-request.py')
        except Exception as e:
            self.log_output('Error:', e)

    def log_output(self, message):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f'[{current_time}] {message}'
        self.tb_log.append(log_message)

    def btn_call_a_clicked(self):
        self.log_output('Call A Button Clicked.')
        self.destination_ip = [self.a_ip]
        self.send_request(self.destination_ip)

    def btn_call_b_clicked(self):
        self.log_output('Call B Button Clicked.')
        self.destination_ip = [self.b_ip]
        self.send_request(self.destination_ip)

    def btn_call_c_clicked(self):
        self.log_output('Call C Button Clicked.')
        self.destination_ip = [self.c_ip]
        self.send_request(self.destination_ip)

    def btn_call_all_clicked(self):
        self.log_output('Call All Button Clicked.')
        self.destination_ip = [self.a_ip, self.b_ip, self.c_ip]
        self.send_request(self.destination_ip)

    def btn_log_clicked(self):
        self.log_output('open "log.txt" Button Clicked.')
        try:
            subprocess.run(['xdg-open', self.log_file_path])
        except Exception as e:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.critical)
            error_dialog.setText('File could not be loaded.')
            error_dialog.setWindowTitle('Call Bell - Error')
            error_dialog.exec_()


class SubWindow(Qw.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SubWindow')
        self.setGeometry(100, 50, 640, 240)


def main():
    #############
    A_IP = 'a_ip'
    B_IP = 'b_ip'
    C_IP = 'c_ip'
    #############
    app = Qw.QApplication(sys.argv)
    main_window = MainWindow(A_IP, B_IP, C_IP)
    main_window.show()
    sys.exit(app.exec())


# 本体
if __name__ == '__main__':
    main()
