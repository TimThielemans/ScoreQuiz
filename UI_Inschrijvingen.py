from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys

class Inschrijving(QtWidgets.QDialog):   
    def __init__(self, parent=None):
        super(Inschrijving, self).__init__(parent)
        uic.loadUi('code/ui/NieuwePloeg.ui', self)
        self.setWindowTitle('Nieuwe Ploeg')
        self.show()
      
        from inschrijving_handler import Class_Inschrijvingen
        from email_handler import Class_Emails
        
        self.EH = Class_Emails()
        self.PH = Class_Inschrijvingen()
        
        self.InschrijvenBtn.clicked.connect(self.inschrijving)
            
    def keyPressEvent(self, event):
        if type(event)==QtGui.QKeyEvent:
           # print ("type(event) = ",type(event), 'Event Key=', event.key())
            if event.key()==QtCore.Qt.Key_Return or event.key()==QtCore.Qt.Key_Enter:
                self.inschrijving()
            elif event.key()==QtCore.Qt.Key_Escape:
                self.close()
            event.accept()
        else:
            event.ignore()
            
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
                    self.EH.bevestigingInschrijving(subscription)
            self.PloegnaamTxt.setText('')
            self.VoornaamTxt.setText('')
            self.AchternaamTxt.setText('')
            self.EmailTxt.setText('')
            

        except NameError:
            qm = QtWidgets.QMessageBox()
            answer = qm.question(QtWidgets.QDialog(), 'Email verzenden?', 'De quiz is momenteel volzet en de ploeg werd toevoegd aan de wachtlijst. Standaard wachtlijst email sturen naar {}'.format(email), qm.Yes | qm.No)
            if answer == qm.Yes:
                self.EH.wachtlijst(subscription)
            self.PloegnaamTxt.setText('')
            self.VoornaamTxt.setText('')
            self.AchternaamTxt.setText('')
            self.EmailTxt.setText('')

        except ValueError:
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

