import sys
from PySide6 import QtCore, QtWidgets, QtGui
from datetime import date, timedelta
import os

class Diary(QtWidgets.QWidget):
    def __init__(self, mainWindow: QtWidgets.QMainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        self.currentDate = date.today()

        if not os.path.exists("diary"):
            os.mkdir("diary")

        # Main Panel

        self.textedit = QtWidgets.QTextEdit(self)
        self.isBold = False
        self.isItalics = False
        self.isUnderline = False
        self.justDidAction = False
        self.textedit.textChanged.connect(self.selectionChanged)
        self.textedit.setAutoFormatting(QtWidgets.QTextEdit.AutoFormattingFlag.AutoAll)
        self.textedit.setMarkdown(self.loadDiary())
        self.textedit.zoomIn(2)
        self.dirty_editor = 0

        self.prevButton = QtWidgets.QPushButton("<<")
        self.nextButton = QtWidgets.QPushButton(">>")
        self.todayButton = QtWidgets.QPushButton("Today")
        self.prevButton.setMaximumWidth(32)
        self.nextButton.setMaximumWidth(32)
        self.todayButton.setMaximumWidth(64)

        self.prevButton.clicked.connect(self.previousDate)
        self.nextButton.clicked.connect(self.nextDate)
        self.todayButton.clicked.connect(self.today)

        self.dateLabel = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter)

        self.dateEdit = QtWidgets.QDateEdit(calendarPopup=True)
        self.dateEdit.setDate(self.currentDate)
        self.dateEdit.dateChanged.connect(self.datePickerChanged)
        self.dateEdit.setMaximumWidth(92)

        self.datebar = QtWidgets.QHBoxLayout()
        self.datebar.addWidget(self.todayButton)
        self.datebar.addWidget(self.dateLabel)
        self.datebar.addWidget(self.prevButton)
        self.datebar.addWidget(self.dateEdit)
        self.datebar.addWidget(self.nextButton)

        self.mainPanel = QtWidgets.QVBoxLayout(self)

        self.mainPanel.addLayout(self.datebar)
        self.mainPanel.addWidget(self.textedit)

        self.mainWindow.setWindowTitle("PyQTDiary")

        self.autosave = QtCore.QTimer()
        self.autosave.setInterval(1000)
        self.autosave.timeout.connect(self.doAutosave)
        self.autosave.start()

        # Menubar

        menuBar = self.mainWindow.menuBar()

        menus = [
            ["File", [
                    ["Save", self.save, QtGui.QKeySequence.Save],
                    ["Quit", self.quit, QtGui.QKeySequence.Quit]
                ]
            ],
            ["Edit", [
                    ["Undo", self.textedit.undo, QtGui.QKeySequence.Undo],
                    ["Redo", self.textedit.redo, QtGui.QKeySequence.Redo],
                    ["Bold", self.toggleBold, QtGui.QKeySequence.Bold],
                    ["Italics", self.toggleItalics, QtGui.QKeySequence.Italic],
                    ["Underline", self.toggleUnderline, QtGui.QKeySequence.Underline]
                ]
            ],
            ["Go", [
                    ["Yesterday", self.previousDate, "Ctrl+,"],
                    ["Tomorrow", self.nextDate, "Ctrl+."],
                    ["Today", self.today, "Ctrl+T"],
                ]
            ]
        ]

        for menu_config in menus:
            menu = menuBar.addMenu("&" + menu_config[0])
            for action in menu_config[1]:
                qaction = QtGui.QAction(action[0], self.mainWindow)
                qaction.triggered.connect(action[1])
                if action[2] is not None:
                    qaction.setShortcut(QtGui.QKeySequence(action[2]))
                menu.addAction(qaction)

        self.updateLabel()
        self.mainWindow.setCentralWidget(self)

    @QtCore.Slot()
    def doAutosave(self):
        if self.dirty_editor == 1:
            self.save()
        elif self.dirty_editor > 0:
            self.dirty_editor -= 1

    @QtCore.Slot()
    def toggleBold(self):
        self.isBold = not self.isBold
        self.textedit.setFontWeight(QtGui.QFont.Weight.Bold if self.isBold else QtGui.QFont.Weight.Normal)
        self.justDidAction = True

    @QtCore.Slot()
    def toggleItalics(self):
        self.isItalics = not self.isItalics
        self.textedit.setFontItalic(self.isItalics)
        self.justDidAction = True

    @QtCore.Slot()
    def toggleUnderline(self):
        self.isUnderline = not self.isUnderline
        self.textedit.setFontUnderline(self.isUnderline)
        self.justDidAction = True

    @QtCore.Slot()
    def selectionChanged(self):
        self.dirty_editor = 5
        if self.justDidAction:
            self.justDidAction = False
            return
        
        self.isBold = False
        self.isItalics = False
        self.isUnderline = False

    @QtCore.Slot()
    def quit(self):
        self.save()
        self.mainWindow.close()

    @QtCore.Slot()
    def save(self):
        self.saveDiary(self.textedit.toMarkdown())
        self.dirty_editor = 0

    @QtCore.Slot()
    def previousDate(self):
        self.changeDateDelta(-1)

    @QtCore.Slot()
    def nextDate(self):
        self.changeDateDelta(1)

    @QtCore.Slot()
    def today(self):
        self.changeDate(date.today())

    @QtCore.Slot()
    def datePickerChanged(self):
        self.changeDate(self.dateEdit.date().toPython())

    def filename(self, date: date) -> str:
        return f"diary/diary-{date.isoformat()}.md"

    def saveDiary(self, content: str):
        filename = self.filename(self.currentDate)
        print(f"Saving {filename}")
        if content.strip() == "":
            print(f"No content!")
            if os.path.exists(filename):
                print(f"Cleaning up!")
                os.remove(filename)
            return

        with open(filename, "w") as file:
            file.write(content.strip())

    def loadDiary(self) -> str:
        filename = self.filename(self.currentDate)
        print(f"Loading {filename}")
        if not os.path.exists(filename):
            print("No diary!")
            return ""
        else:
            with open(filename, "r") as file:
                data = file.read()
            print("Loaded!")
            return data

    def updateLabel(self):
        self.dateLabel.setText(self.currentDate.strftime("%A %d, %B %Y"))

    def changeDateDelta(self, days: int):
        self.changeDate(self.currentDate + timedelta(days=days))

    def changeDate(self, newDate):
        print("changeDate")

        if self.dateEdit.date().toPython() != newDate:
            self.dateEdit.setDate(newDate)
            self.saveDiary(self.textedit.toMarkdown())
            self.textedit.setMarkdown("")

        self.currentDate = newDate
        self.updateLabel()
        self.textedit.setMarkdown(self.loadDiary())

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    mainWindow = QtWidgets.QMainWindow()

    window = Diary(mainWindow)

    mainWindow.resize(640, 480)
    mainWindow.show()

    sys.exit(app.exec())
