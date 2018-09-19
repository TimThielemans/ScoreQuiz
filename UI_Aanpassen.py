from PyQt5 import QtCore, QtGui, QtWidgets, uic
import cv2
import os

class Aanpassen(QtWidgets.QDialog):   
    def __init__(self, parent=None):
        super(Aanpassen, self).__init__(parent)
        uic.loadUi('code/ui/Aanpassen.ui', self)
        self.setWindowTitle('Scores aanpassen')
        self.setup()
        self.show()
            
    def setup(self):
        from score_handler import Class_Scores
        from ronde_handler import Class_Rondes
        from inschrijving_handler import Class_Inschrijvingen
        self.RH = Class_Rondes()
        self.PH = Class_Inschrijvingen()
        self.SH = Class_Scores()
       
        self.fillComboBox()
        
        self.ronde = 0
        self.imageDir = self.SH.getImagesDir()
        self.currentRondeSettings = 99
        number = self.PH.aantalPloegen()
        aanwezigen = self.PH.aanwezigePloegen()
        self.AanwezigePloegen = list(map(int, aanwezigen[0]))
        self.AantalPloegen = int(number[1])
        
        self.TNIndex = 0;
        self.updateRonde()

        self.rondeBox.currentIndexChanged.connect(self.nieuweRondeBox)
        self.NextBtn.clicked.connect(self.nextTafel)
        self.PreviousBtn.clicked.connect(self.previousTafel)
        self.SaveBtn.clicked.connect(self.saveScore)
        self.qrcodeText.returnPressed.connect(self.qrGo)
        self.qrcodeText.setFocus()
            
    def fillComboBox(self):
        self.rondeBox.addItem('0_Schifting&Bonus')
        self.comborondes = []
        self.comborondes.append(0)
        for ronde in self.SH.getUserRondes():
            self.rondeBox.addItem(ronde)
            a = ronde.split('_')
            self.comborondes.append(int(a[0]))
        self.rondeBox.setCurrentIndex(0)
        self.ronde = 0

    def nextTafel(self):
        if self.saveScore():
            if self.TNIndex<len(self.AanwezigePloegen)-1:
                self.TNIndex = self.TNIndex+1
                self.updatePloeg()
            else:
                self.msgBox('Laatste ploeg', 'Dit is de laatste aanwezige ploeg')
        
    def previousTafel(self):
        if self.saveScore():
            if self.TNIndex>0:
                self.TNIndex = self.TNIndex-1
                self.updatePloeg()
            else:
                self.msgBox('Eerste ploeg', 'Dit is de eerste aanwezige ploeg')

    def qrGo(self):
        if self.saveScore():
            try:
                ronde, tafelnummer = map(int, self.qrcodeText.text().split('_'))
                try:
                    self.rondeBox.setCurrentIndex(self.comborondes.index(ronde))
                    self.updateRonde()
                    try:
                        self.TNIndex = self.AanwezigePloegen.index(tafelnummer)
                        self.updatePloeg()
                    except:
                        self.msgBox('Error', 'Deze ploeg is niet aanwezig')
                except:
                    self.msgBox('Error', 'Deze ronde werd nog niet ingegeven')
            except:
                self.msgBox('Error', 'Geen geldige QR-code')
               
            self.qrcodeText.setText('')

    def nieuweRondeBox(self):
        if self.saveScore():
            self.updateRonde()

    def updateRonde(self):
        dictronde = self.RH.getRondeInfoDict(self.comborondes[self.rondeBox.currentIndex()])
        if dictronde == '':
            self.ronde = 0
            if self.RH.numberBonusRondes()>0:
                self.NOQ = 2
            else:
                self.NOQ = 1
        else:
            self.ronde = int(dictronde['RN'])
            self.NOQ = int(dictronde['Aantal'])
        self.updatePloeg()
            
    def updatePloeg(self):
        self.Tafelnummer = self.AanwezigePloegen[self.TNIndex]
        self.tafelnummerTxt.setText(str(self.Tafelnummer))
        if self.ronde>0:
            self.score = self.SH.getScore(self.ronde, self.Tafelnummer)
            self.filename = self.imageDir + '{}_{}.jpg'.format(self.ronde, self.Tafelnummer)
            if not len(self.score)>0:
                self.score = [0]*self.NOQ
        else:
            self.score = self.PH.getSchiftingBonus(self.Tafelnummer)
        self.updateLayout()

    def saveScore(self):
        nieuwescore = []
        if self.ronde>0:
            for box in self.checkboxes:
                nieuwescore.append(int(box.isChecked()))

            if self.RH.isSuperRonde(self.ronde):
                for i in range(int(len(nieuwescore)/3)):
                    if sum(nieuwescore[i*3:i*3+3])>1:
                        self.msgBox('Ongeldige score', 'Geen geldige invoer voor een superronde: vraag {}'.format(i+1))
                        return False
        else:
            nieuwescore.append(self.schiftingTxt.text())
            try:
                float(nieuwescore[0])
            except:
                self.msgBox('Ongeldige score', 'Geen geldige schiftingsvraag!')
                return False
            if len(self.checkboxes)>0:
                aantal = 0
                bonus = 0
                for i, box in enumerate(self.checkboxes):
                    if box.isChecked():
                        aantal = aantal+1
                        bonus = i+1
                if not aantal == 1:
                    self.msgBox('Ongeldige score', 'Geen geldig bonusthema!')
                    return False
                
        if not list(map(str,nieuwescore)) == self.score:
            self.SH.setScore(self.ronde, self.Tafelnummer, nieuwescore)
            
        return True
    
    def setImageLbl(self):
        try:
            pixmap = QtGui.QPixmap(self.filename)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(self.imagesLbl.width(), self.imagesLbl.height(), QtCore.Qt.KeepAspectRatio)
                self.imagesLbl.setPixmap(pixmap)
                self.imagesLbl.setAlignment(QtCore.Qt.AlignCenter)
        except:
            pass

    def updateBoxes(self):
        if self.ronde>0:
            for i, box in enumerate(self.checkboxes):
                box.setChecked(int(self.score[i]))
        else:
            self.schiftingTxt.setText(str(self.score[0]))
            if self.NOQ == 2:
                bonusthema = int(self.score[1])
                for i, box in enumerate(self.checkboxes):
                    box.setChecked(i+1==bonusthema)
        
    def updateLayout(self):
        if not self.ronde == self.currentRondeSettings:
            #updatelayout
            self.checkboxes = []
            self.NOQ = len(self.score)
            try:
                self.superronde = self.RH.isSuperRonde(self.ronde)
            except:
                self.superronde = 0
                pass
            for box in self.checkboxes:
                box.hide()
                box.setChecked(0)
        
            self.hideQLayout(self.schiftingsvraag)
            if self.superronde == 1:
                index = 0
                for i in range(self.basicScores.count()):
                    box1 = self.basicScores.itemAt(i).widget()
                    box2 = self.superronde2.itemAt(i).widget()
                    box3 = self.superronde3.itemAt(i).widget()
                    if i<self.NOQ/3:
                        box1.setText('{}a.'.format(i+1))
                        box2.setText('{}b.'.format(i+1))
                        box3.setText('{}c.'.format(i+1))
                        self.checkboxes.append(box1)
                        self.checkboxes.append(box2)
                        self.checkboxes.append(box3)
                        box1.show()
                        box2.show()
                        box3.show()
                    else:
                        box1.hide()
                        box2.hide()
                        box3.hide()
            else:
                self.hideQLayout(self.superronde2)
                self.hideQLayout(self.superronde3)
                if self.NOQ <3:
                    self.showQLayout(self.schiftingsvraag)
                    if self.NOQ == 2:
                        aantalThemas = 9
                        boxes = (self.basicScores.itemAt(i).widget() for i in range(self.basicScores.count())) 
                        for i, box in enumerate(boxes):
                            if i<aantalThemas:
                                box.setText('{}.'.format(i+1))
                                self.checkboxes.append(box)
                                box.show()
                            else:
                                box.hide()
                    self.schiftingTxt.setText(str(self.score[0]))
                
                else:
                    boxes = (self.basicScores.itemAt(i).widget() for i in range(self.basicScores.count())) 
                    for i, box in enumerate(boxes):
                        if i<self.NOQ:
                            box.setText('{}.'.format(i+1))
                            self.checkboxes.append(box)
                            box.show()
                        else:
                            box.hide()
                            
        self.currentRondeSettings = self.ronde
        self.updateBoxes() #check or uncheck
        self.setImageLbl()
        
    def hideQLayout(self, layout):
        items = (layout.itemAt(i).widget() for i in range(layout.count())) 
        for i, item in enumerate(items):
            try:
                item.hide()
            except:
                pass

    def showQLayout(self, layout):
        items = (layout.itemAt(i).widget() for i in range(layout.count())) 
        for i, item in enumerate(items):
            try:
                item.show()
            except:
                pass

    def msgBox(self, titel, tekst):
        msg = QtWidgets.QMessageBox()
        msg.setText(tekst)
        msg.setWindowTitle(titel)
        msg.exec()
                                
    def allChecked(self, doeiets):
        #sluit deze GUI af en verwerk SCANCONTROL

        msg = QtWidgets.QMessageBox()
        msg.setText("Alle beschikbare scans zijn gecontroleerd!")
        msg.setWindowTitle("Klaar!")
        msg.exec()
        if doeiets:
            self.SH.fromScannerToUser()
        self.close()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Aanpassen()
    sys.exit(app.exec_())

