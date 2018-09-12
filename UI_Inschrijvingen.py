from PyQt5 import QtCore, QtGui, QtWidgets, uic
from inschrijving_handler import Class_Inschrijvingen
import email_sender
import sys

class Inschrijving(QtWidgets.QDialog):   
    def __init__(self, parent=None):
        super(Inschrijving, self).__init__(parent)
        uic.loadUi('code/ui/NieuwePloeg.ui', self)
        self.setWindowTitle('Nieuwe Ploeg')
        self.show()

        self.PH = Class_Inschrijvingen()
        self.InschrijvenBtn.clicked.connect(self.inschrijving)
            
    def inschrijving(self):
        ploegnaam = self.PloegnaamTxt.toPlainText()
        voornaam = self.VoornaamTxt.toPlainText()
        achternaam = self.AchternaamTxt.toPlainText()
        email = self.EmailTxt.toPlainText()
        subscription = [ploegnaam, voornaam, achternaam, email]
        try:
            self.PH.nieuwePloeg(subscription)
            if '@' in email:
                qm = QtWidgets.QMessageBox()
                answer = qm.question(QtWidgets.QDialog(), 'Email verzenden?', 'Bevestigingsmail verzenden naar {}'.format(email), qm.Yes | qm.No)
                if answer == qm.Yes:
                    email_sender.bevestigingInschrijving(subscription)
            self.PloegnaamTxt.setText('')
            self.VoornaamTxt.setText('')
            self.AchternaamTxt.setText('')
            self.EmailTxt.setText('')
            
        except NameError:
            raise
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("Deze ploegnaam is al ingebruikt, inschrijving dus niet verwerkt!")
            msg.setWindowTitle("Geen geldige ploegnaam!")
            msg.exec()
        
        self.PloegnaamTxt.setFocus()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Inschrijving()
    sys.exit(app.exec_())

