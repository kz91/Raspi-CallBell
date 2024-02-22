import sys
import subprocess
import PySide6.QtWidgets as Qw
from PySide6.QtWidgets import QApplication, QMessageBox
from datetime import datetime


# PySide6.QtWidgets.MainWindow を継承aした MainWindow クラスの定義
class MainWindow(Qw.QMainWindow):
    # コンストラクタ(初期化)
    def __init__(self):
        super().__init__()

        # 親クラスのコンストラクタの呼び出し
        self.window_position_x = 100
        self.window_position_y = 50
        self.window_width = 640
        self.window_height = 240
        self.log_file_path = 'log.txt'
        self.send_ip_txt = []
        self.a_ip = 'a_ip'
        self.b_ip = 'b_ip'
        self.c_ip = 'c_ip'

        # ウィンドウタイトル設定
        self.setWindowTitle('Call Bell')

        # ウィンドウのサイズ(640x240)と位置(X=100,Y=50)の設定
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

        # テキストボックス
        self.tb_log = Qw.QTextEdit('', self)
        self.tb_log.setReadOnly(True)
        self.tb_log.setGeometry(10, 40, 620, 170)
        self.tb_log.setPlaceholderText('(ここに実行ログを表示します)')

        # ステータスバー
        self.sb_status = Qw.QStatusBar()
        self.setStatusBar(self.sb_status)
        self.sb_status.setSizeGripEnabled(False)
        self.sb_status.showMessage('プログラムを起動しました。')

    def btn_call_a_clicked(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f'[{current_time}] Call A Button Clicked.'
        self.tb_log.append(log_message)
        self.send_ip_txt = [self.a_ip]

    def btn_call_b_clicked(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f'[{current_time}] Call B Button Clicked.'
        self.tb_log.append(log_message)
        self.send_ip_txt = [self.b_ip]

    def btn_call_c_clicked(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f'[{current_time}] Call C Button Clicked.'
        self.tb_log.append(log_message)
        self.send_ip_txt = [self.c_ip]

    def btn_call_all_clicked(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f'[{current_time}] Call All Button Clicked.'
        self.tb_log.append(log_message)
        self.send_ip_txt = [self.a_ip, self.b_ip, self.c_ip]

    def btn_log_clicked(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f'[{current_time}] open "log.txt" Button Clicked.'
        self.tb_log.append(log_message)
        try:
            subprocess.run(['xdg-open', self.log_file_path])

        except Exception as e:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.critical)
            error_dialog.setText("ファイルが読み込めませんでした．")
            # error_dialog.setInformativeText(message)
            error_dialog.setWindowTitle("Call Bell - Error")
            error_dialog.exec()


class SubWindow(Qw.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SubWindow')
        self.setGeometry(100, 50, 640, 240)


# 本体
if __name__ == '__main__':
    app = Qw.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
