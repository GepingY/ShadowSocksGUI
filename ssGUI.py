from PyQt6 import QtWidgets, uic
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSize, Qt, QTimer, QProcess
from datetime import datetime
import urllib.parse
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import sys
import requests
import subprocess
import base64
import threading
import time
from requests import get
import json
import ast

def overwrite_line(file_path, line_number, new_text):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    lines[line_number] = str(new_text) + '\n'  # Overwrite the specified line

    with open(file_path, 'w') as file:
        file.writelines(lines)

if hasattr(sys, '_MEIPASS'):
    # When running the PyInstaller-extracted binary
    base_path = sys._MEIPASS
else:
    # When running the script normally
    base_path = os.path.dirname(os.path.abspath(__file__))

ui_path = os.path.join(base_path, 'socksGUI1.ui')
config_path = os.path.join(base_path, 'config.txt')

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.servers = []
        self.radio_buttons = []
        self.data = []

        #init stored config data
        file = open(config_path, "r+", encoding='utf-8')
        files = file.readlines()
        c = 0
        for i in files:
            if c >= 2:
                self.data.append(ast.literal_eval(i.rstrip('\n')))
            elif c < 2:
                self.data.append(i.rstrip('\n'))
            c += 1
        file.close()

        for i in range(2, len(self.data)):
            self.servers.append(self.data[i])
        #init over

        #UI init
        loadUi(ui_path, self)
        self.lineEdit.setText(self.data[1].rstrip('\n'))
        self.lineEdit_2.setText(self.data[0].rstrip('\n'))
        self.pushButton.clicked.connect(self.Download)
        self.pushButton_2.clicked.connect(self.UpdateLocalConfig)
        self.pushButton_3.clicked.connect(self.connect)
        self.pushButton_5.clicked.connect(self.Extract)
        self.pushButton_6.clicked.connect(self.RegenerateConfig)
        self.pushButton_7.clicked.connect(self.ss_kill)
        self.pushButton_8.clicked.connect(self.Manual)
        self.pushButton_9.clicked.connect(self.DecodeB64)

        self.scrollArea_layout = QVBoxLayout()
        self.scrollAreaWidget = QWidget()  # Widget to hold the scroll area content
        self.scrollAreaWidget.setLayout(self.scrollArea_layout)
        self.scrollArea.setWidget(self.scrollAreaWidget)  # Set the widget in the scroll area
        self.scrollArea.setWidgetResizable(True)  # Allow resizing

        self.RegenerateConfig()

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.readyReadStandardError.connect(self.read_output)
        self.output_timer = QTimer(self)
        self.output_timer.timeout.connect(self.update_timer_label)

    def Manual(self):
        config = []
        try:
            config.append(self.lineEdit_5.text())
        except:
            self.error("Failed to set password ")
            return

        try:
            config.append(self.lineEdit_3.text())
        except:
            self.error("Failed to set server address")
            return

        try:
            config.append(self.spinBox.value())
        except:
            self.error("Failed to set server port")
            return

        try:
            config.append(self.lineEdit_6.text())
        except:
            self.error("Failed to set name of the connection")
            return
        if config not in self.servers:
            self.servers.append(config)
        self.RegenerateConfig()        

    def Extract(self):
        self.data = []
        file = open(config_path, "r+", encoding='utf-8')
        files = file.readlines()
        c = 0
        for i in files:
            if c >= 2:
                if i not in self.data:
                    self.data.append(ast.literal_eval(i.rstrip('\n')))
                else:
                    pass
            elif c < 2:
                if i not in self.data:
                    self.data.append(i.rstrip('\n'))
                else:
                    pass
            c += 1
        file.close()

        for i in range(2, len(self.data)):
            if self.data[i] not in self.servers:
                self.servers.append(self.data[i])
        self.RegenerateConfig()

    def UpdateLocalConfig(self):
        try:
            self.lineEdit_2.setText(self.lineEdit_2.text().rstrip('\n'))
        except:
            pass
        try:
            self.lineEdit.setText(self.lineEdit.text().rstrip('\n'))
        except:
            pass
        first_line = self.lineEdit_2.text()
        second_line = self.lineEdit.text()
        with open(config_path, 'w') as file:
            file.write(first_line + '\n')  # Write the first line
            file.write(second_line + '\n')
            for server in self.servers:
                file.write(str(server) + '\n')  # Add one server per line

    def update_timer_label(self):
        # Implement your logic for updating the timer label here
        seconds = time.time() - self.start_time
        days = int(seconds // 86400)
        hours = int(seconds // 3600)
        minutes = int(seconds // 60)
        seconds = int(seconds - minutes * 60)
        minutes = int(minutes - hours * 60)
        hours = int(hours - days * 24)
        self.label_30.setText(f"{days} D, {hours} H, {minutes} Min, {seconds} Sec")

    def read_output(self):
        """Read output without blocking and update UI."""
        while self.process.canReadLine():
            output = self.process.readLine().data().decode().strip()
            if output:
                self.textEdit.append(output)

    def ss_kill(self):
        self.process.terminate()  # Gracefully terminate the process
        self.output_timer.stop()  # Stop the timer
        self.label_13.setText("• Stopped")
        self.label_13.setStyleSheet("color: rgb(193, 0, 3);")
        self.label_11.setStyleSheet("color: rgb(193, 0, 3);")
        self.label_9.setStyleSheet("color: rgb(193, 0, 3);")
        self.label_30.setStyleSheet("color: rgb(193, 0, 3);")
        self.label_30.setText("Not Running")
        self.label_15.setStyleSheet("color: rgb(193, 0, 3);")

    def connect(self):
        self.ss(self.servers[self.get_selected_server()])

    def error(self, msg):
        QMessageBox.critical(
            self,
            'Error',
            msg
        )

    def info(self, info):
         QMessageBox.information(
            self,
            'Information',
            info
        )

    def kill(self):
        command = ["kill", str(pid)]
        try:
            subprocess.run(command, check=True)
            self.info("Process terminated successfully.")
        except subprocess.CalledProcessError as e:
            self.info(f"Error terminating process: {e}")

    def confirm(self, title, msg):
        answer = QMessageBox.question(
            self,
            title,
            msg,
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )
        if answer == QMessageBox.StandardButton.Yes:
            return True
        else:
            return False
            

    def ss(self, data):
        self.server_password = data[0]  # This would be your password
        self.server_host = data[1]       # Server hostname or IP
        self.server_port = data[2]       # Server port
        if str(self.spinBox_2.value()) == "0":
            local_port = 1080
        else:
            local_port = self.spinBox_2.value()                         # Local port to bind

        if self.lineEdit_4.text() == "":
            local_addr = "127.0.0.1"
        else:
            local_addr = str(self.lineEdit_4.text())
        encrypt_method = str(self.comboBox.currentText()) # Encryption method

        # Command to run ss-local
        command = [
            'ss-local',
            '-s', self.server_host,
            '-p', self.server_port,
            '-l', str(local_port),
            '-k', self.server_password,
            '-b', local_addr,
            '-m', encrypt_method,
        ]
        if self.checkBox.isChecked():
            command.append('-u')
        if self.checkBox_2.isChecked():
            command.append('--fast-open')
        if self.checkBox_3.isChecked():
            command.append('--no-delay')
        if self.checkBox_4.isChecked():
            command.append('-v')
        

        self.process.start(command[0], command[1:])
        if self.process.state() != QProcess.ProcessState.NotRunning:  # We don't rely on state anymore
            self.start_time = time.time()
            self.output_timer.start(1000)  # Update every second
            self.label_13.setText("• Running")
            self.label_13.setStyleSheet("color: rgb(36, 134, 29);")
            self.label_15.setText(str(datetime.now()))
            self.label_15.setStyleSheet("color: rgb(36, 134, 29);")
            self.label_30.setStyleSheet("color: rgb(36, 134, 29);")
            self.label_9.setStyleSheet("color: rgb(255, 255, 255);")
            self.label_11.setStyleSheet("color: rgb(255, 255, 255);")
            self.proxies = {
                'https': 'socks5://127.0.0.1:1080',
                'http': 'socks5://127.0.0.1:1080',
            }
            time.sleep(0.5)
            try:
                response = requests.get("http://ipinfo.io/json", proxies=self.proxies)
                self.ipinfo = response.json()
                self.IP = self.ipinfo['ip']
                self.org = self.ipinfo['org']
                self.city = self.ipinfo['city']
                self.country = self.ipinfo['country']
                self.region = self.ipinfo['region']
                self.label_32.setText(self.server_host)
                self.label_34.setText(self.server_port)
                self.label_9.setText(self.IP)
                self.label_36.setText(self.org)
                self.label_11.setText(self.country + " " + self.region + " " + self.city)
            except:
                try:
                    time.sleep(1)
                    response = requests.get("http://ipinfo.io/json", proxies=self.proxies)
                    self.ipinfo = response.json()
                    self.IP = self.ipinfo['ip']
                    self.org = self.ipinfo['org']
                    self.city = self.ipinfo['city']
                    self.country = self.ipinfo['country']
                    self.region = self.ipinfo['region']
                    self.label_32.setText(self.server_host)
                    self.label_34.setText(self.server_port)
                    self.label_9.setText(self.IP)
                    self.label_36.setText(self.org)
                    self.label_11.setText(self.country + " " + self.region + " " + self.city)
                except:
                    if self.confirm("Failed", "Unable to request current IP through proxy, might be a connection error. Do you want to retry in 10sec?") == True:
                        time.sleep(10)
                        response = requests.get("http://ipinfo.io/json", proxies=self.proxies)
                        self.ipinfo = response.json()
                        self.IP = self.ipinfo['ip']
                        self.org = self.ipinfo['org']
                        self.city = self.ipinfo['city']
                        self.country = self.ipinfo['country']
                        self.region = self.ipinfo['region']
                        self.label_32.setText(self.server_host)
                        self.label_34.setText(self.server_port)
                        self.label_9.setText(self.IP)
                        self.label_36.setText(self.org)
                        self.label_11.setText(self.country + " " + self.region + " " + self.city)
                    else:
                        pass

        else:
            self.error("Error: Unable to start connection")



    def get_selected_server(self):
        for i, button in enumerate(self.radio_buttons):
            if button.isChecked():
                return i
        self.error("Please select server")
        return None  # Optional: Return None if no selection is made

    def ss_to_config(self, line):
        # Split the line into its components
        parts = line.split('@')

        # Decode the password
        #encoded_info = parts[0].split('://')[1]
        encoded_info = parts[0].replace("ss://", "")
        password = base64.b64decode(encoded_info + "==").decode('utf-8').replace("chacha20-ietf-poly1305:", "")

        # Extract server location and port
        server_info = parts[1].split('#')[0]
        server_location = server_info.split(':')[0]
        server_port = server_info.split(':')[1]

        # Decode additional info
        additional_info = urllib.parse.unquote(parts[1].split('#')[1])

        # Append the results to the 2D array
        return [password, server_location, server_port, additional_info]

    def server_extract(self, data):
        return base64.b64decode(data).decode('utf-8').splitlines()

    def DecodeB64(self):
        servers = self.server_extract(self.lineEdit_2.text())
        for line in servers:
            config = self.ss_to_config(line)
            if config not in self.servers:  # Check if config already exists in self.servers
                self.servers.append(config)
        self.RegenerateConfig()

    def RegenerateConfig(self):
        self.remove_radio_buttons()
        for i in range (0, len(self.servers)):
            radio_button = QRadioButton(self.servers[i][3])  # Using additional info as the label
            self.scrollArea_layout.addWidget(radio_button)
            self.radio_buttons.append(radio_button)

    def remove_radio_buttons(self):
        # Loop through each radio button in the list
        for radio_button in self.radio_buttons:
            # Remove the radio button from the layout
            self.scrollArea_layout.removeWidget(radio_button)

            # Hide the widget (optional but good practice)
            radio_button.hide()

            # Delete the widget from memory
            radio_button.deleteLater()

        # Clear the list after removing all radio buttons
        self.radio_buttons.clear()


    def Download(self):
        url = self.lineEdit.text()
        #in version 2, here needs to be a try: to recieve http error code to preven error, not bothered to do it in version 1
        raw = requests.get(url).text.strip()
        self.data[0] = raw
        self.lineEdit_2.setText(raw)
        overwrite_line(config_path, 0, raw)


    def get_public_ip(self):
        response = requests.get('https://httpbin.org/ip')
        if response.status_code == 200:
            ip = response.json()['origin']
            return ip
        else:
            return 'Unable to retrieve public IP.'

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    mainwindow = MainWindow()
#    window2 = window2()
    widget.addWidget(mainwindow)
#    widget.addWidget(window2)
    widget.setFixedHeight(890)
    widget.setFixedWidth(1112)
    widget.setWindowTitle("ShadowSocks GUI")
    widget.show()
    sys.exit(app.exec())
