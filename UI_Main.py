from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt
import configparser
import os, parser
import sys

sys.path.append('code/')
import UI_Inschrijvingen
import UI_ScanControl
import UI_Aanmelden
import UI_Admin
import UI_Aanpassen
import decodeSheets
        

class startScherm(QtWidgets.QMainWindow):   
    def __init__(self, parent=None):
        super(startScherm, self).__init__(parent)
        uic.loadUi('code/ui/MainControl.ui', self)
        self.setup()
        self.show()

    def setup(self):
        geldig = self.selectDir()
        if geldig:
            self.nieuwePloegBtn.clicked.connect(lambda: UI_Inschrijvingen.Inschrijving(self))
            self.adminBtn.clicked.connect(self.admin)
            self.aanmeldenBtn.clicked.connect(lambda: UI_Aanmelden.Aanmelden(self))
            self.scansVerwerkenBtn.clicked.connect(self.scansVerwerken)
            self.scansControlerenBtn.clicked.connect(lambda: UI_ScanControl.Control(self))
            self.aanpassingenBtn.clicked.connect(lambda: UI_Aanpassen.Aanpassen(self))
            self.scorebordBtn.clicked.connect(self.scorebord)
        else:
            self.msgBox('Geen geldige directory, opgestart in default mode', 'Niet geldig')

        from score_handler import Class_Scores
        self.SH = Class_Scores()

    def keyPressEvent(self, event):
        if type(event)==QtGui.QKeyEvent:
            if event.key()==QtCore.Qt.Key_Escape:
                self.close()
            elif event.key()==QtCore.Qt.Key_A:
                UI_Aanmelden.Aanmelden(self)
            elif event.key()==QtCore.Qt.Key_D:
                self.admin()
            elif event.key()==QtCore.Qt.Key_O:
                self.scorebord()
            elif event.key()==QtCore.Qt.Key_C:
                UI_ScanControl.Control(self)
            elif event.key()==QtCore.Qt.Key_N:
                UI_Inschrijvingen.Inschrijving(self)
            event.accept()
        else:
            event.ignore() 
        
    def selectDir(self):
        filename = 'settings.ini'
        parser = configparser.ConfigParser()
        parser.read(filename)
        global WACHTWOORD
        WACHTWOORD = parser.get('COMMON', 'wachtwoord')
        
        debug = 1
        default = 'Test/'
        if debug == 1:
            dialog = QtWidgets.QFileDialog()
            dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
            dialog.setViewMode(QtWidgets.QFileDialog.Detail);
            if(dialog.exec()):
                a = dialog.selectedFiles()
                directory = a[0]+'/'
            else:
                directory = default
        else:
            directory = default
        
        try:
            open(directory + parser.get('PATHS', 'SHEETINFO'))
            gelukt= True
        except:
            gelukt = False

        if not gelukt:
            directory = default
            
        parser.set('PATHS', 'QUIZFOLDER', directory)
        with open(filename, 'w') as configfile:
            parser.write(configfile)

        if 'Test' in directory:
            pal = QPalette()
            pal.setColor(QPalette.Background, Qt.red)
            self.setAutoFillBackground(True)
            self.setPalette(pal)
            
        lijstje = directory.split('/')
        titel = lijstje[len(lijstje)-2]
        self.setWindowTitle(self.windowTitle() + ' ' + titel)
        return gelukt
        

    def scansVerwerken(self):
        directory = None
        qm = QtWidgets.QMessageBox()
        answer = qm.question(QtWidgets.QDialog(), 'Default of aangepast?', 'Staan de scanbestanden op de default plaats?', qm.Yes | qm.No)
        if answer == qm.No:
            dialog = QtWidgets.QFileDialog()
            dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
            dialog.setViewMode(QtWidgets.QFileDialog.Detail);
            if(dialog.exec()):
                a = dialog.selectedFiles()
                directory = a[0]+'/'
        self.msgBox("De computer gaat al de beschikbare scans verwerken en dat kan even duren. Druk op Ok en ... let the magic begin!", 'Ready, set, ...')
        aantal, tijd = decodeSheets.main(directory, None,None ,None )
        self.msgBox("Er werden {} scans verwerkt op {}s. Dat is een gemiddelde van {}s per pagina. Geef jij dat sneller in misschien?".format(aantal, round(tijd, 2), round(tijd/aantal, 2)), 'Klaar!')

    def scorebord(self):
        qm = QtWidgets.QMessageBox()
        answer = qm.question(QtWidgets.QDialog(), 'Bonus berekening', 'Bereken ook de optimale bonus? (enkel eenmaal bij de eindstand)', qm.Yes | qm.No)
        geenBonus, geenSchifting, ontbreekt, fout = self.SH.generateScorebord(answer == qm.Yes)
        fouten = False
        info = ''
        if len(geenBonus)>0:
            info = info + '\nGeen BonusThema: {}'.format(geenBonus)
            fouten = True
        if len(geenSchifting)>0:
            info = info + '\nGeen Schifting: {}'.format(geenSchifting)
            fouten = True
        if len(ontbreekt)>0:
            info = info + '\nOntbrekende files: {}'.format(ontbreekt)
            fouten = True
        if len(fout)>0:
            info = info + '\nAfwezig maar ingegeven: {}'.format(fout)
            fouten =True

        if fouten:
            text = 'Het scorebord werd berekend maar er zijn aanpassingen gebeurd bij volgende bestanden. Kijk dit zeker nog eens na!' + info
            titel = 'Klaar maar opgelet!!!'
        else:
            text = 'Het scorebord werd berekend zonder fouten!'
            titel = 'Klaar'
        self.msgBox(text, titel)

    def admin(self):
        wachtwoord, ok = QtWidgets.QInputDialog.getText(self, 'Wachtwoord', 'Wachtwoord voor Admin', QtWidgets.QLineEdit.Password)
        if ok and wachtwoord == WACHTWOORD:
            UI_Admin.AdminUI(self)
        

            
    def msgBox(self, text, titel):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(titel)
        msg.exec()
       

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = startScherm()
    sys.exit(app.exec_())
    
