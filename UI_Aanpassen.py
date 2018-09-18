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
        self.Tafelnummer = 1
        self.ronde = 0
        self.imageDir = self.SH.getImagesDir()
        self.currentRondeSettings = 99
        number = self.PH.aantalPloegen()
        self.AantalPloegen = int(number[1])
        
        self.updateRonde()

        self.rondeBox.currentIndexChanged.connect(self.updateRonde)
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

    def updateRonde(self):
        rondetekst = self.rondeBox.currentText().split('_')
        dictronde = self.RH.getRondeInfoDict(rondetekst[0])
        if dictronde == '':
            self.ronde = 0
            if self.RH.numberBonusRondes()>0:
                self.NOQ = 2
            else:
                self.NOQ = 1
        else:
            self.ronde = int(dictronde['RN'])
            self.NOQ = int(dictronde['Aantal'])
            
        self.goTo(self.ronde, self.Tafelnummer)

    def nextTafel(self, save=True):
        if save:
            self.saveScore()
        self.Tafelnummer = self.Tafelnummer+1
        if not self.updatePloeg(self.ronde, self.Tafelnummer):
            if self.Tafelnummer<self.AantalPloegen:
                self.nextTafel(False)
            else:
                self.msgBox('Dit is de laatste ploeg', 'Laatste ploeg')

    def previousTafel(self, save=True):
        if save:
            self.saveScore()
        if self.Tafelnummer>1:
            self.Tafelnummer = self.Tafelnummer-1
            if not self.updatePloeg(self.ronde, self.Tafelnummer):
                self.previousTafel(False)
        else:
            self.msgBox('Dit is de eerste ploeg', 'Eerste ploeg')

    def goTo(self,ronde, tafel):
        self.saveScore()
        self.updatePloeg(ronde, tafel)
            
    def updatePloeg(self, ronde, tafelnummer):
        if ronde>0:
            self.score = self.SH.getScore(ronde, tafelnummer)
            if len(self.score)>0:
                self.Tafelnummer = tafelnummer
                self.tafelnummerTxt.setText(str(self.Tafelnummer))
                self.ronde = ronde
                self.filename = self.imageDir + '{}_{}.jpg'.format(ronde, tafelnummer)
                self.updateLayout()
                return True
            return False
        else:
            self.score = self.PH.getSchiftingBonus(tafelnummer)
            self.Tafelnummer = tafelnummer
            self.ronde=0
            self.updateLayout()
            if int(self.score[1]) == 999:
                    return False    
            self.tafelnummerTxt.setText(str(self.Tafelnummer))
            self.updateBoxes()
            return True
            
    def saveScore(self):
        print('save Score')

    def qrGo(self):
        try:
            ronde, tafelnummer = map(int, self.qrcodeText.text().split('_'))
            self.rondeBox.setCurrentIndex(self.comborondes.index(ronde))
            self.Tafelnummer = tafelnummer
            self.updateRonde()
        except:
            self.msgBox('Error', 'Geen geldige QR-code of ronde is nog niet ingegeven')
           
        self.qrcodeText.setText('')

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
                for i, box in enumerate(self.checkboxes):
                    if i == int(self.score[1])-1:
                        box.setChecked(1)
                    else:
                        box.setChecked(0)
        
    def updateLayout(self):
        if not self.ronde == self.currentRondeSettings:
            #updatelayout
            self.checkboxes = []
            print('updateLayout')
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

