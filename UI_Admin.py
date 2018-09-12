from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt
import configparser
import os, parser
import sys
sys.path.append('code/')



class Admin(QtWidgets.QDialog):   
    def __init__(self, parent=None):
        super(Admin, self).__init__(parent)
        uic.loadUi('code/ui/Admin.ui', self)
        self.setup()
        self.show()
        

    def setup(self):
        from inschrijving_handler import Class_Inschrijvingen
        import email_sender
        print('setup')
            
        
    def msgBox(self, text, titel):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(titel)
        msg.exec()
       

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Admin()
    sys.exit(app.exec_())

