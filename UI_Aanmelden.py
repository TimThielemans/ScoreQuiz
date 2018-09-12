from PyQt5 import QtCore, QtGui, QtWidgets, uic
from inschrijving_handler import Class_Inschrijvingen
import email_sender
import sys

class Aanmelden(QtWidgets.QDialog):   
    def __init__(self, parent=None):
        super(Aanmelden, self).__init__(parent)
        uic.loadUi('code/ui/Aanmelden.ui', self)
        self.setWindowTitle('Aanmelden')
        self.setup()
        self.show()

    def setup(self):
        #fill Combobox
        self.PH = Class_Inschrijvingen()
        for ploegnaam in self.PH.getPloegNamen():
            self.ploegnaamTxt.addItem(ploegnaam)
        self.ploegnaamTxt.setCurrentIndex(-1)
        self.ploegnaamTxt.setFocus()
       

    def keyPressEvent(self, event):
        if type(event)==QtGui.QKeyEvent:
           # print ("type(event) = ",type(event), 'Event Key=', event.key())
            if event.key()==QtCore.Qt.Key_Return or event.key()==QtCore.Qt.Key_Enter:
                self.aanmelding()
            elif event.key()==QtCore.Qt.Key_Escape:
                self.close()
            event.accept()
        else:
            event.ignore()
        
    def aanmelding(self):
        ploegnaam = self.ploegnaamTxt.currentText()
        index = self.ploegnaamTxt.currentIndex()
        if not ploegnaam == ' ' and index>-1:
            aanmeldtekst = self.PH.aanmelden(ploegnaam)
            if 'Er heeft zich al iemand' in aanmeldtekst:
                qm = QtWidgets.QMessageBox()
                answer = qm.question(QtWidgets.QDialog(), 'Terug afmelden?', aanmeldtekst +'\n\nTerug Afmelden?', qm.Yes | qm.No)
                if answer == qm.Yes:
                    self.PH.resetAanmelding(ploegnaam)
            else:
                self.msgBox(aanmeldtekst, 'Aanmelding')
            if 'EMAILADRES' in aanmeldtekst:
                email, ok = QtWidgets.QInputDialog.getText(self, 'Emailadres', 'Emailadres voor ploeg {}'.format(ploegnaam));
                if '@' in email and ok:
                    self.PH.veranderEmail(ploegnaam, email)
        self.ploegnaamTxt.setCurrentIndex(-1)
        self.ploegnaamTxt.setFocus()

    def msgBox(self, text, titel):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(titel)
        msg.exec()

    def questionBox(self, text, titel):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(titel)
        msg.exec()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Aanmelden()
    sys.exit(app.exec_())

