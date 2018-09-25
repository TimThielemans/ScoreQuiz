from PyQt5 import QtCore, QtGui, QtWidgets, uic
import cv2

class Control(QtWidgets.QMainWindow):   
    def __init__(self, parent=None):
        super(Control, self).__init__(parent)
        uic.loadUi('code/ui/Controleren.ui', self)
        self.setWindowTitle('Scans controleren')
        self.show()
        self.setup()

        self.nextBtn.clicked.connect(self.nextFile)
        self.updateScoreBtn.clicked.connect(self.updateScore)
        self.allesJustBtn.clicked.connect(self.allesOverzetten)

    def closeEvent(self, event):
        self.SH.fromScannerToUser()
        if len(self.SH.getAllScanResults())>0:
            msg = QtWidgets.QMessageBox()
            msg.setText("Nog niet alle scans werden gecontroleerd")
            msg.setWindowTitle("Opgelet")
            msg.exec()
        event.accept()
        
    def setup(self):
        from score_handler import Class_Scores
        from ronde_handler import Class_Rondes
        from inschrijving_handler import Class_Inschrijvingen
        self.SH = Class_Scores()
        self.RH = Class_Rondes()
        self.PH = Class_Inschrijvingen()
        self.AllScanData = self.SH.getAllScanResults()
        
        if len(self.AllScanData)>0:
            self.ScanDataIndex = 0
            self.currentRondeSettings = None
            self.checkboxes = []
            self.checkTafelnummer = False

            self.hideQLayout(self.basicScores)
            self.updateFile()
            self.updateLayout()
            self.setImageLbl()
            
        else:
            msg = QtWidgets.QMessageBox()
            msg.setText("Alle beschikbare scans zijn gecontroleerd dus je kan hier niets mee doen...")
            msg.setWindowTitle("Klaar!")
            msg.exec()

    def allesOverzetten(self):
        #Laatste Aanpassing
        
        bereik = range(self.ScanDataIndex, len(self.AllScanData))

        self.toCheck = []
        for i in bereik:
            row = self.AllScanData[i]
            row = row[0]
            if int(row[2]) == 0:
                self.ScanDataIndex = i
                self.iterateAll()
                if self.checkTafelnummer:
                    self.toCheck.append(row)
            else:
                self.toCheck.append(row)
        if len(self.toCheck) == 0:
            self.allChecked(True)
        else:
            self.SH.fromScannerToUser()
            self.msgBox('Bijna klaar', 'Er zijn nog een paar scans die manueel nagekeken moeten worden.')
            self.setup()

    def iterateAll(self):
        self.updateFile()
        if not self.checkTafelnummer:
            newRow = [self.ronde] + [self.ploeg] + self.score
            self.SH.validateScanResult(newRow)
        
    def nextFile(self):
        if self.updateScore():
            newRow = [self.ronde] + [self.ploeg] + self.score
            self.SH.validateScanResult(newRow)
            self.ScanDataIndex = self.ScanDataIndex+1
            if self.ScanDataIndex<len(self.AllScanData):
                self.updateFile()
                self.setImageLbl()
                self.updateLayout()
            else:
                self.allChecked(True)
            return True
        else:
            if not self.scoresOk:
                text = 'Deze score kan niet kloppen, kijk het nog eens na!'
            elif not self.bonusOk:
                text = 'Er is iets mis met het bonusthema, kijk het nog eens na!'
            elif not self.tafelOk:
                text = 'Dit tafelnummer bestaat niet of is niet aanwezig, kijk het nog eens na!'
                self.ploegTxt.setFocus()
            elif not self.schiftingOk:
                text = 'Geen geldig antwoord voor de schiftingsvraag, kijk het nog eens na!'
                self.schiftingTxt.setFocus()
            else:
                text = 'Geen geldige input, kijk het nog eens na!'
            self.msgBox('Ongeldig', text)
            return False
    
    def updateFile(self):
        data = self.AllScanData[self.ScanDataIndex]
        self.filename = data[1]
        self.row = data[0]
        self.ploeg = int(self.row[1])
        self.ronde = int(self.row[0])
        self.score = self.row[3:]
        
    def setImageLbl(self):
        try:
            pixmap = QtGui.QPixmap(self.filename)
            pixmap = pixmap.scaled(self.imagesLbl.width(), self.imagesLbl.height(), QtCore.Qt.KeepAspectRatio)
            self.imagesLbl.setPixmap(pixmap)
            self.imagesLbl.setAlignment(QtCore.Qt.AlignCenter)
        except:
            msg = QtWidgets.QMessageBox()
            msg.setText("Geen afbeelding gevonden maar wel de data???")
            msg.setWindowTitle("Vreemd")
            msg.exec()

    def updateScore(self):
        score = []
        nieuwescore = []
        checked = False
        update = False
        changed = False
        self.schiftingOk = True
        self.bonusOk = True
        self.tafelOk = True
        self.scoresOk = True
        if self.ronde>0 and self.superronde == 1:
            for box in self.checkboxes:
                score.append(int(box.isChecked()))
            checked = True
            update = True
            for i in range(int(len(score)/3)):
                if sum(score[i*3:i*3+3])>1:
                    update = False
                    self.scoresOk = False
                    break
            if update:
                nieuwescore = score
                changed = not list(map(int, self.score)) == nieuwescore 
        elif self.ronde == 0:
            checked = True
            try:
                schifting = int(self.schiftingTxt.text())
                nieuwescore.append(schifting)
                update = True
                changed = not int(self.score[1])==nieuwescore[0]
            except:
                update = False
                self.schiftingOk = False
                                  
            if len(self.checkboxes)>1 and update:
                bonusThema = 0
                update=False
                for i, box in enumerate(self.checkboxes):
                    if box.isChecked():
                        score.append(1)
                        bonusThema = i+1
                    else:
                        score.append(0)
                if sum(score) == 1:
                    nieuwescore.append(bonusThema)
                    update = True
                    if not changed and not int(self.score[1])==bonusThema:
                        changed = True
                else:
                    self.bonusOk = False
                
        else:
            for i, box in enumerate(self.checkboxes):
                if box.isChecked():
                    nieuwescore.append(1)
                else:
                    nieuwescore.append(0)
            update = True
            checked = False
            changed = not list(map(int, self.score)) == nieuwescore

        if self.checkTafelnummer:
            try:
                self.ploeg = int(self.ploegTxt.text())
                aanwezig = self.PH.isAanwezig(self.ploeg)
                if not aanwezig:
                    #de nieuwe tafel is niet aanwezig dus is sowieso foute ingave
                    checked = True
                    update = False
                    self.tafelOk = False
                else:
                    self.ploeg = int(str('999')+str(self.ploeg))
            except:
                checked = True
                update = False
                self.tafelOk = False   

        if checked and not update:
            return False
        if update and changed:
            self.score = nieuwescore
            filename = self.AllScanData[self.ScanDataIndex][1]
            image = cv2.imread(self.filename)
            heigth, width, channels = image.shape
            cv2.rectangle(image, (int(width*0.1), int(heigth)), (0, int(heigth*0.9)), (0, 166, 255), -1)
            cv2.imwrite(self.filename, image)
            self.setImageLbl()
        return True


    def updateBoxes(self):
        if self.ronde>0:
            for i, box in enumerate(self.checkboxes):
                box.setChecked(int(self.score[i]))
        else:
            self.schiftingTxt.setText(self.score[0])
            if self.NOQ == 2:
                bonusthema = int(self.score[1])
                for i, box in enumerate(self.checkboxes):
                    box.setChecked(i+1==bonusthema)
        
    def updateLayout(self):
        self.checkTafelnummer = False
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
            self.hideQLayout(self.tafelnummer)
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
                    self.schiftingTxt.setText(self.score[0])
                
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
        if '999' in str(self.ploeg):
            self.showQLayout(self.tafelnummer)
            self.checkTafelnummer = True
            self.ploegTxt.setText('')
        self.updateBoxes() #check or unchek
        
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
    def msgBox(self, titel, text):
        msg = QtWidgets.QMessageBox()
        msg.setText(text)
        msg.setWindowTitle(titel)
        msg.exec()
        
    def allChecked(self, doeiets):
        #sluit deze GUI af en verwerk SCANCONTROL

        self.msgBox('Klaar!', "Alle beschikbare scans zijn gecontroleerd!")
        if doeiets:
            self.SH.fromScannerToUser()
        self.close()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Control()
    sys.exit(app.exec_())

