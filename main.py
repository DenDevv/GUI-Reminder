import sys
import time
import db

from datetime import datetime
from PyQt5 import QtCore, QtWidgets
from win10toast import ToastNotifier

from themes.new_remind_window import Ui_newDialog
from themes.home_window import Ui_MainWindow


class Monitor(QtCore.QThread):
    signal = QtCore.pyqtSignal(str)
    
    def __init__(self, title, year, month, day, hour, minute, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.title = title
        self.day = day
        self.month = month
        self.year = year
        self.hour = hour
        self.minute = minute

    def run(self):
        toaster = ToastNotifier()
        delay_time = datetime(self.year, self.month, self.day, hour=self.hour, minute=self.minute)

        while True:
            try:
                for i in db.check_data(self.title):
                    message = i

                if delay_time <= datetime.today():
                    self.signal.emit(self.title)
                    toaster.show_toast(self.title, message, duration=10, icon_path='themes/icon.ico')
                    break

                time.sleep(5)
            except:
                break


class ReminderGUI(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self, db.row_count(), db.select_data())
        self.connect_btns()

    def connect_btns(self):
        self.ui.newR.clicked.connect(self.n_window)
        self.ui.refR.clicked.connect(self.refresh_reminds)
        self.ui.tableWidget.cellClicked.connect(self.delete)

    def delete(self):
        row = self.ui.tableWidget.currentRow()
        column = self.ui.tableWidget.currentColumn()
        cell_text = self.ui.tableWidget.item(row, column).text()
        self.ui.delR.clicked.connect(lambda: self.delete_remind(cell_text))

    def n_window(self):
        self.newDialog = QtWidgets.QDialog()
        self.new = Ui_newDialog()
        self.new.setupUi(self.newDialog)
        self.new.Save.clicked.connect(self.new_remind)
        self.new.Date.setDate(QtCore.QDate.currentDate())
        self.new.Date.setTime(QtCore.QTime.currentTime())
        
        self.newDialog.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.newDialog.show()
        self.newDialog.exec()
    
    def new_remind(self):
        dt = self.new.Date.dateTime()
        date = dt.toString(self.new.Date.displayFormat())
        some_date = date.split(".")
        today = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M")

        title = self.new.Title.text()
        text = self.new.Text.text()

        self.day = int(some_date[0])
        self.month = int(some_date[1])
        self.year = int(some_date[2][:4])
        self.hour = int(some_date[2][5:].split(":")[0])
        self.minute = int(some_date[2][5:].split(":")[1])
        db_date = datetime.strftime(
                datetime(
                    self.year, 
                    self.month, 
                    self.day, 
                    hour=self.hour, 
                    minute=self.minute
                    ), 
                    "%Y-%m-%d %H:%M")
        
        if title != "" and text != "" and not (db_date == today):
            db.insert_data(date, title, text)
            self.newDialog.close()
            self.refresh_reminds()
            self.reminder(title, self.year, self.month, self.day, self.hour, self.minute)
    
    def reminder(self, title, year, month, day, hour, minute):
        self.monitor = Monitor(title, year, month, day, hour, minute)
        self.monitor.signal.connect(self.refresh_reminds)
        self.monitor.start()

    def delete_remind(self, data):
        if db.check_data(data):
            db.delete_data(data)
            self.refresh_reminds()

    def refresh_reminds(self, title=None):
        if title:
            db.delete_data(title)
            self.ui.setupUi(self, db.row_count(), db.select_data())
            self.connect_btns()
        else:
            self.ui.setupUi(self, db.row_count(), db.select_data())
            self.connect_btns()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ReminderGUI()
    window.setWindowTitle("Reminder")
    window.show()
    app.exec_()