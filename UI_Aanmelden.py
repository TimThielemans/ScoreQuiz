from PyQt5 import QtCore, QtGui, QtWidgets, uic
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
        from inschrijving_handler import Class_Inschrijvingen
        self.PH = Class_Inschrijvingen()
        for ploegnaam in self.PH.getPloegNamen():
            self.ploegnaamTxt.addItem(ploegnaam)
        self.ploegnaamTxt.setCurrentIndex(-1)
        self.ploegnaamTxt.setFocus()
        self.updateLabel()
       

    def keyPressEvent(self, event):
        if type(event)==QtGui.QKeyEvent:
           # print ("type(event) = ",type(event), 'Event Key=', event.key())
            if event.key()==QtCore.Qt.Key_Return or event.key()==QtCore.Qt.Key_Enter:
                self.aanmelding()
            elif event.key()==QtCore.Qt.Key_Escape:
                self.close()
            elif event.key()==QtCore.Qt.Key_Control:
                self.afwezigOverzicht()
            event.accept()
        else:
            event.ignore()
    
    def aanmelding(self):
        ploegnaam = self.ploegnaamTxt.currentText()
        index = self.ploegnaamTxt.currentIndex()
        if not ploegnaam == ' ' and index>-1:
            aanmeldResult = self.PH.aanmelden(ploegnaam)
            if len(aanmeldResult)>1:
                
                tekst = "<p align='center'>Ploeg: {}</p>".format(aanmeldResult['Ploegnaam'])
                tekst = tekst + "<p align='center'>Tafelnummer: {}</p>".format(aanmeldResult['TN'])
                if aanmeldResult['Aanwezig']:
                    tekst = tekst +  "<p align='left'> Vorige aanmelding: {}<br>" .format(aanmeldResult['Uur'])
                    tekst = tekst + 'Terug afmelden?</p>'                    
                    qm = QtWidgets.QMessageBox()
                    answer = qm.question(QtWidgets.QDialog(), 'Terug afmelden?', tekst, qm.Yes | qm.No)
                    if answer == qm.Yes:
                        self.PH.resetAanmelding(ploegnaam)
                else:
                    if bool(aanmeldResult['Betaald']):
                        tekst = tekst + "<p align='left'> Betaling in orde: €{}<br>".format(aanmeldResult['Bedrag']) + "Drankkaarten: {}<br>".format(aanmeldResult['Drankkaarten'])
                    else:
                        tekst = tekst + "<p align='left'> NOG NIET BETAALD!!!<br>"

                    if not aanmeldResult['Email']:
                        tekst = tekst + "EMAILADRES TOEVOEGEN!!!</p>"
                        self.msgBoxAanmelden(tekst, 'Aanmelding')
                        email, ok = QtWidgets.QInputDialog.getText(self, 'Emailadres', 'Emailadres voor ploeg {}'.format(ploegnaam));
                        if '@' in email and ok:
                            self.PH.veranderEmail(ploegnaam, email)
                    else:
                        self.msgBoxAanmelden(tekst + '</p>', 'Aanmelding')
                self.updateLabel()
            else:
                self.msgBox('Ploeg niet gevonden', 'Ongeldig')
                    
        self.ploegnaamTxt.setCurrentIndex(-1)
        self.ploegnaamTxt.setFocus()

    def afwezigOverzicht(self):
        aanwezig, afwezig = self.PH.aanwezigePloegen()
        tekst= ''
        for ploeg in afwezig:
            tekst = tekst + '{}.\t{}\n'.format(ploeg[0], ploeg[1])
        if len(tekst)>0:
            self.msgBox(tekst, 'Afwezige ploegen')
        else:
            self.msgBox('Iedereen is aanwezig, je kan starten!', 'Afwezige ploegen')


        
    def updateLabel(self):
        numbers = self.PH.aantalPloegen()
        self.aangemeldTxt.setText('{}/{}'.format(numbers[0], numbers[1]))
        if numbers[0]==numbers[1]:
            self.msgBox('Alle {} ploegen zijn aanwezig, de quiz kan starten!'.format(numbers[1]), 'Joepie!')
            self.close()

    def msgBox(self, text, titel):
        msg = QtWidgets.QMessageBox()
        #msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(titel)
        msg.exec()

    def msgBoxAanmelden(self, text, titel):
        msg = QtWidgets.QMessageBox()
        #msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(titel)
        msg.setStyleSheet("QLabel{min-width: 300px;}");
        msg.exec()

    def questionBox(self, text, titel):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Question)
        msg.setText(text)
        msg.setWindowTitle(titel)
        msg.exec()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Aanmelden()
    sys.exit(app.exec_())

